from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Optional
import os
from ..database import get_db
from ..models import Reference
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
    for p in pathlib.Path(docs_dir).glob("*.md"):
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

            # infer ref_type from frontmatter if it mentions 'class' or from filename
            ref_type = None
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
