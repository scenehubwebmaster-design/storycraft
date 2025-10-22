from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Optional
import os
import json
import math
from ..database import get_db
from ..models import Reference, ReferenceEmbedding, DocumentChunk, ChunkEmbedding
from datetime import datetime
import pathlib

router = APIRouter(prefix="/api/references", tags=["references"])


@router.get("/", summary="List references")
def list_references(ref_type: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(Reference)
    if ref_type:
        query = query.filter(Reference.ref_type == ref_type)
    results = query.order_by(Reference.title).all()
    return [r.to_dict() for r in results]


# IMPORTANT: /search route must come BEFORE /{ref_id} to avoid path conflicts
@router.get("/search", summary="Search references with semantic similarity and filters")
def search_references(
    q: Optional[str] = None,
    ref_type: Optional[str] = None,
    k: int = 5,
    level: Optional[int] = None,
    rarity: Optional[str] = None,
    school: Optional[str] = None,
    category: Optional[str] = None,
    tags: Optional[str] = None,  # Comma-separated tags
    use_chunks: bool = False,  # Enable chunk-based search
    chunks_per_doc: int = 2,  # Chunks to return per document
    db: Session = Depends(get_db)
):
    """
    Search references using semantic embeddings with optional metadata filters.
    
    Args:
        q: Query string for semantic search
        ref_type: Filter by ref_type (e.g., 'classes_md', 'spells_md')
        k: Number of results to return
        level: Filter by spell/character level (0-9)
        rarity: Filter by item rarity (Common, Uncommon, Rare, Very Rare, Legendary, Artifact)
        school: Filter by spell school (Abjuration, Conjuration, Divination, Enchantment, Evocation, Illusion, Necromancy, Transmutation)
        category: Filter by item category (Weapon, Armor, Potion, Ring, etc.)
        tags: Comma-separated tags to filter by (e.g., 'fire,damage')
        use_chunks: If True, search document chunks for more granular results (default: False)
        chunks_per_doc: Max chunks to return per document when use_chunks=True (default: 2)
        db: Database session
    
    Returns:
        List of matching references with similarity scores
        When use_chunks=True, results include 'chunks' array with relevant sections
    """
    # Parse tags if provided
    tag_list = [t.strip() for t in tags.split(',')] if tags else None
    
    # Choose search function based on use_chunks parameter
    if use_chunks:
        results = do_chunk_search(
            q=q,
            ref_type=ref_type,
            k=k,
            db=db,
            level=level,
            rarity=rarity,
            school=school,
            category=category,
            tags=tag_list,
            chunks_per_doc=chunks_per_doc
        )
    else:
        results = do_reference_search(
            q=q, 
            ref_type=ref_type, 
            k=k, 
            db=db,
            level=level,
            rarity=rarity,
            school=school,
            category=category,
            tags=tag_list
        )
    return {"results": results}


@router.get("/{ref_id}", summary="Get reference by id")
def get_reference(ref_id: int, db: Session = Depends(get_db)):
    ref = db.query(Reference).filter(Reference.id == ref_id).first()
    if not ref:
        raise HTTPException(status_code=404, detail="Reference not found")
    return ref.to_dict()


@router.post("/sync-from-disk", summary="Sync Markdown reference files from disk into DB")
def sync_references_from_disk(db: Session = Depends(get_db)):
    """
    Scan the repository's `documents/` folder for Markdown files and upsert them into the references table.
    Filenames should be like `ClassName_PHB2024.md` or `Species_PHB2024.md`.
    The ref_type will be inferred from the filename prefix (lowercased).
    """
    # NOTE: For personal/dev use this endpoint is intentionally open and will
    # import Markdown files from the repository `documents/` folder.
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    docs_dir = os.path.join(repo_root, "documents")
    if not os.path.isdir(docs_dir):
        raise HTTPException(status_code=404, detail=f"Documents folder not found at {docs_dir}")

    imported = []
    # scan markdown files recursively so subfolders (eg documents/Species) are respected
    for p in pathlib.Path(docs_dir).rglob("*.md"):
        try:
            stem = p.stem
            content = p.read_text(encoding="utf-8")

            # attempt to read YAML frontmatter (simple split)
            fm = None
            body = content
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    fm = parts[1]
                    body = parts[2]

            # key and title
            key = stem.replace(" ", "_").lower()
            title = stem.replace("-", " ")

            # infer ref_type from frontmatter if it mentions 'class', from parent folder name or from filename
            ref_type = None
            # prefer parent dir name when it's a direct child of documents (e.g., documents/Species)
            try:
                parent = p.parent
                if parent and parent.name:
                    # if parent is the documents dir itself, skip
                    if parent.name.lower() != os.path.basename(docs_dir).lower():
                        # If parent folder is a generic 'reference' folder, prefer the
                        # grandparent (e.g., documents/reference/spells_md -> use spells_md)
                        pname = parent.name.lower()
                        if pname in ("reference", "references") and parent.parent and parent.parent.name:
                            pname = parent.parent.name.lower()
                        # strip common suffix used in this repo (folders named like 'spells_md')
                        if pname.endswith("_md"):
                            pname = pname[: -3]
                        ref_type = pname
            except Exception:
                parent = None
            if fm:
                for line in fm.splitlines():
                    if ':' not in line:
                        continue
                    k, v = line.split(':', 1)
                    k = k.strip().lower()
                    v = v.strip().lower()
                    if k in ('chapter', 'category', 'section') and 'class' in v:
                        ref_type = 'class'
                        break

            if not ref_type:
                parts = stem.split("_")
                candidate = parts[0].lower() if parts and parts[0] else ''
                # common D&D class names -> treat as class
                common_classes = {
                    'barbarian','bard','cleric','druid','fighter','monk','paladin','ranger','rogue','sorcerer','warlock','wizard'
                }
                if candidate in common_classes:
                    ref_type = 'class'
                elif candidate:
                    ref_type = candidate
                else:
                    ref_type = 'unknown'

            # use body (no frontmatter) as stored content
            content = body

            # Upsert
            existing = db.query(Reference).filter(Reference.key == key, Reference.ref_type == ref_type).first()
            if existing:
                existing.title = title
                existing.content = content
                existing.updated_at = datetime.utcnow()
                db.add(existing)
                db.commit()
                db.refresh(existing)
                imported.append(existing.to_dict())
            else:
                new = Reference(
                    ref_type=ref_type,
                    key=key,
                    title=title,
                    content=content,
                    source_url=None
                )
                db.add(new)
                db.commit()
                db.refresh(new)
                imported.append(new.to_dict())
        except Exception:
            # skip problematic files but continue
            continue

    return {"imported": len(imported), "items": imported}


def cosine(a, b):
    """Compute cosine similarity between two vectors."""
    num = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0 or nb == 0:
        return 0.0
    return num / (na * nb)


def do_reference_search(
    q: Optional[str], 
    ref_type: Optional[str], 
    k: int, 
    db: Session,
    level: Optional[int] = None,
    rarity: Optional[str] = None,
    school: Optional[str] = None,
    category: Optional[str] = None,
    tags: Optional[list] = None
):
    """
    Core search logic for references - can be called from routes or other functions.
    Uses real semantic embeddings (384-dim sentence-transformers).
    
    Args:
        q: Query string for semantic search
        ref_type: Filter by ref_type (e.g., 'classes_md', 'spells_md')
        k: Number of results to return
        db: Database session
        level: Filter by spell/character level (e.g., 3 for 3rd-level spells)
        rarity: Filter by item rarity (e.g., 'Uncommon', 'Rare')
        school: Filter by spell school (e.g., 'Evocation', 'Abjuration')
        category: Filter by item category (e.g., 'Weapon', 'Armor')
        tags: Filter by tags (e.g., ['fire', 'damage'])
    
    Returns:
        List of reference dicts with similarity scores
    """
    # Build base query with filters
    query = db.query(Reference)
    
    if ref_type:
        query = query.filter(Reference.ref_type == ref_type)
    
    if level is not None:
        query = query.filter(Reference.level == level)
    
    if rarity:
        query = query.filter(Reference.rarity == rarity)
    
    if school:
        query = query.filter(Reference.school == school)
    
    if category:
        query = query.filter(Reference.category == category)
    
    # If no query string, just return filtered results
    if not q:
        results = query.order_by(Reference.title).limit(k).all()
        # Filter by tags in Python if needed (since tags are JSON)
        if tags:
            filtered = []
            for r in results:
                if r.tags and all(tag in r.tags for tag in tags):
                    filtered.append(r)
            return [r.to_dict() for r in filtered[:k]]
        return [r.to_dict() for r in results]
    
    # Get all matching references (apply filters)
    # Don't limit candidates - we need to score ALL documents for accurate results
    candidates = query.all()
    
    # Filter by tags in Python (since tags are JSON arrays)
    if tags:
        candidates = [c for c in candidates if c.tags and all(tag in c.tags for tag in tags)]
    
    if not candidates:
        return []
    
    # Load sentence transformer model for query encoding
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    # Generate query vector using real semantic embeddings
    qv = model.encode(q).tolist()
    
    # Load embeddings for candidates
    ref_ids = [r.id for r in candidates]
    embeddings = db.query(ReferenceEmbedding).filter(ReferenceEmbedding.reference_id.in_(ref_ids)).all()
    vec_map = {e.reference_id: json.loads(e.vector) for e in embeddings}
    
    # Score candidates - combine embedding similarity with keyword matching
    scored = []
    query_lower = q.lower()
    # Extract meaningful words (filter out common words)
    stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'about', 'tell', 'me'}
    query_tokens = [w for w in query_lower.split() if w not in stopwords]
    
    for ref in candidates:
        # Start with embedding similarity score
        emb_score = 0.0
        if ref.id in vec_map:
            emb_score = cosine(qv, vec_map[ref.id])
        
        # Add keyword matching
        keyword_score = 0.0
        title_lower = (ref.title or '').lower()
        content_lower = (ref.content or '').lower()[:1000]
        
        # Full query match in title is very strong
        if query_lower in title_lower:
            keyword_score += 0.5
        
        # Partial matches in title
        for token in query_tokens:
            if token in title_lower:
                keyword_score += 0.3
        
        # Tokens in content
        for token in query_tokens:
            if token in content_lower:
                keyword_score += 0.1
        
        # Token overlap bonus
        if query_tokens:
            matches = sum(1 for t in query_tokens if t in title_lower or t in content_lower)
            keyword_score += 0.05 * matches / len(query_tokens)
        
        # Combine: with real embeddings, we can trust them more
        # But still keep some keyword signal for exact matches
        final_score = 0.7 * emb_score + 0.3 * keyword_score
        
        result = ref.to_dict()
        result['score'] = final_score
        result['_debug_emb_score'] = emb_score
        result['_debug_keyword_score'] = keyword_score
        scored.append((final_score, result))
    
    # Sort by score and return top k
    scored.sort(key=lambda x: x[0], reverse=True)
    results = [s[1] for s in scored[:k]]
    
    return results


def do_chunk_search(
    q: str,
    ref_type: Optional[str],
    k: int,
    db: Session,
    level: Optional[int] = None,
    rarity: Optional[str] = None,
    school: Optional[str] = None,
    category: Optional[str] = None,
    tags: Optional[list] = None,
    chunks_per_doc: int = 2
):
    """
    Search document chunks using semantic embeddings.
    Returns the most relevant chunks, grouped by parent document.
    
    Args:
        q: Query string for semantic search
        ref_type: Filter by ref_type
        k: Number of documents to return (not chunks)
        db: Database session
        level/rarity/school/category/tags: Metadata filters
        chunks_per_doc: Max chunks to return per document (default: 2)
    
    Returns:
        List of documents with their best-matching chunks
    """
    if not q:
        # Fall back to full document search if no query
        return do_reference_search(q, ref_type, k, db, level, rarity, school, category, tags)
    
    # Build base query with filters on parent documents
    ref_query = db.query(Reference)
    
    if ref_type:
        ref_query = ref_query.filter(Reference.ref_type == ref_type)
    if level is not None:
        ref_query = ref_query.filter(Reference.level == level)
    if rarity:
        ref_query = ref_query.filter(Reference.rarity == rarity)
    if school:
        ref_query = ref_query.filter(Reference.school == school)
    if category:
        ref_query = ref_query.filter(Reference.category == category)
    
    candidate_refs = ref_query.all()
    
    # Filter by tags in Python
    if tags:
        candidate_refs = [r for r in candidate_refs if r.tags and all(tag in r.tags for tag in tags)]
    
    if not candidate_refs:
        return []
    
    # Get all chunks for candidate documents
    ref_ids = [r.id for r in candidate_refs]
    chunks = db.query(DocumentChunk).filter(DocumentChunk.source_id.in_(ref_ids)).all()
    
    if not chunks:
        # Fall back to full document search if no chunks exist
        return do_reference_search(q, ref_type, k, db, level, rarity, school, category, tags)
    
    # Load sentence transformer model
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    # Generate query vector
    qv = model.encode(q).tolist()
    
    # Load chunk embeddings
    chunk_ids = [c.id for c in chunks]
    embeddings = db.query(ChunkEmbedding).filter(ChunkEmbedding.chunk_id.in_(chunk_ids)).all()
    vec_map = {e.chunk_id: json.loads(e.vector) for e in embeddings}
    
    # Score all chunks
    chunk_scores = []
    for chunk in chunks:
        if chunk.id in vec_map:
            score = cosine(qv, vec_map[chunk.id])
            chunk_scores.append((score, chunk))
    
    # Sort chunks by score
    chunk_scores.sort(key=lambda x: x[0], reverse=True)
    
    # Group chunks by parent document and take top chunks_per_doc per document
    doc_chunks = {}  # source_id -> [(score, chunk), ...]
    for score, chunk in chunk_scores:
        if chunk.source_id not in doc_chunks:
            doc_chunks[chunk.source_id] = []
        if len(doc_chunks[chunk.source_id]) < chunks_per_doc:
            doc_chunks[chunk.source_id].append((score, chunk))
    
    # Calculate document scores (average of top chunks)
    doc_scores = []
    ref_map = {r.id: r for r in candidate_refs}
    
    for source_id, chunks_list in doc_chunks.items():
        if source_id not in ref_map:
            continue
        
        avg_score = sum(s for s, _ in chunks_list) / len(chunks_list)
        ref = ref_map[source_id]
        
        # Build result with chunks
        result = ref.to_dict()
        result['score'] = avg_score
        result['chunks'] = [
            {
                'heading': chunk.heading,
                'text': chunk.chunk_text[:500] + ('...' if len(chunk.chunk_text) > 500 else ''),
                'chunk_index': chunk.chunk_index,
                'chunk_score': score
            }
            for score, chunk in chunks_list
        ]
        
        doc_scores.append((avg_score, result))
    
    # Sort documents by average chunk score and return top k
    doc_scores.sort(key=lambda x: x[0], reverse=True)
    results = [doc for _, doc in doc_scores[:k]]
    
    return results
