# RAG-First Data Architecture for StoryCraft

## Problems with Current Setup

1. **Pseudo-embeddings** - SHA256 hashing doesn't capture semantic similarity
2. **Document-level retrieval** - Retrieving entire markdown files is inefficient
3. **No structured metadata** - Can't filter by spell level, CR, item rarity, etc.
4. **Generic schema** - One `references` table for all content types
5. **No chunking** - Long documents aren't split into retrievable chunks

## Proposed Improvements

### 1. Use Real Embeddings

**Option A: Local Sentence Transformers** (Recommended)

```python
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')  # 384-dim, fast, local
embeddings = model.encode(texts)
```

**Option B: OpenAI Embeddings** (Higher quality, API cost)

```python
import openai
embedding = openai.Embedding.create(
    input="text",
    model="text-embedding-3-small"  # 1536-dim
)
```

**Option C: LM Studio Embeddings** (Local, configurable)

- Use your existing LM Studio setup with an embedding model
- Maintain full control and privacy

### 2. Chunk Documents for Retrieval

Instead of storing entire markdown files, split into retrievable chunks:

```python
# Chunk strategy
- Max chunk size: 512 tokens (~2000 chars)
- Overlap: 50 tokens (for context continuity)
- Semantic boundaries: Split on headers, paragraphs, sections
```

**New Table Structure:**

```python
class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True)
    source_id = Column(Integer, ForeignKey("references.id"))  # Parent document
    chunk_index = Column(Integer)  # Order within document
    chunk_text = Column(Text)  # The actual chunk content
    heading = Column(String(255))  # Section heading if any
    metadata = Column(JSON)  # Flexible metadata
    token_count = Column(Integer)

class ChunkEmbedding(Base):
    __tablename__ = "chunk_embeddings"

    id = Column(Integer, primary_key=True)
    chunk_id = Column(Integer, ForeignKey("document_chunks.id"), unique=True)
    vector = Column(Text)  # JSON-encoded or use pgvector for Postgres
    model = Column(String(100))  # Track which embedding model was used
```

### 3. Add Structured Metadata for Filtering

**Enhanced Reference Model:**

```python
class Reference(Base):
    __tablename__ = "references"

    # Existing fields
    id = Column(Integer, primary_key=True)
    ref_type = Column(String(100), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text)  # Keep full content for display

    # NEW: Structured metadata for filtering
    level = Column(Integer, nullable=True)  # Spell level, character level
    rarity = Column(String(50))  # Common, Uncommon, Rare, etc.
    school = Column(String(100))  # Spell school (Evocation, etc.)
    category = Column(String(100))  # Weapon, Armor, Wondrous Item
    tags = Column(JSON)  # Flexible tagging: ["fire", "area", "damage"]

    # Relationships
    chunks = relationship("DocumentChunk", back_populates="source")
```

### 4. Hybrid Search Architecture

Combine multiple retrieval strategies:

```python
def hybrid_search(query: str, filters: dict, k: int = 5):
    # 1. Semantic search (vector similarity)
    semantic_results = vector_search(query, k=k*2)

    # 2. Keyword search (BM25 or simple keyword)
    keyword_results = keyword_search(query, k=k*2)

    # 3. Apply filters (level, rarity, type, tags)
    filtered_semantic = apply_filters(semantic_results, filters)
    filtered_keyword = apply_filters(keyword_results, filters)

    # 4. Reciprocal Rank Fusion (combine rankings)
    final_results = reciprocal_rank_fusion(
        filtered_semantic,
        filtered_keyword,
        k=k
    )

    return final_results
```

### 5. Specialized Schemas for Content Types

Instead of one generic `references` table, use specialized tables:

```python
class Spell(Base):
    __tablename__ = "spells"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    level = Column(Integer, nullable=False)
    school = Column(String(50))  # Evocation, Conjuration, etc.
    casting_time = Column(String(100))
    range = Column(String(100))
    components = Column(String(255))  # V, S, M
    duration = Column(String(100))
    description = Column(Text)
    higher_levels = Column(Text, nullable=True)
    tags = Column(JSON)  # ["fire", "damage", "area"]
    source = Column(String(100))  # PHB, XGE, etc.

    # For RAG
    embedding_id = Column(Integer, ForeignKey("embeddings.id"))

class MagicItem(Base):
    __tablename__ = "magic_items"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    rarity = Column(String(50))  # Common, Uncommon, Rare, Very Rare, Legendary
    requires_attunement = Column(Boolean, default=False)
    category = Column(String(100))  # Weapon, Armor, Wondrous Item, etc.
    description = Column(Text)
    tags = Column(JSON)
    source = Column(String(100))

    embedding_id = Column(Integer, ForeignKey("embeddings.id"))
```

### 6. Vector Database Options

**Option A: Keep SQLite with JSON vectors** (Current)

- ✅ Simple, no new dependencies
- ❌ Slow for large datasets (>10k vectors)
- ❌ No native vector indexing

**Option B: Add FAISS index** (Already partially implemented)

- ✅ Fast vector search (microseconds)
- ✅ Local, no external service
- ❌ In-memory (high RAM for large datasets)
- ❌ Separate from DB (sync issues)

**Option C: Qdrant** (Recommended for production)

- ✅ Purpose-built vector database
- ✅ Built-in filtering on metadata
- ✅ Fast and scalable
- ✅ Local deployment option
- ❌ Additional service to run

**Option D: pgvector (PostgreSQL extension)**

- ✅ Vectors stored in Postgres
- ✅ Native SQL queries with vector search
- ✅ ACID compliance
- ❌ Requires migrating from SQLite to Postgres

### 7. Recommended Migration Path

**Phase 1: Improve embeddings (Quick Win)**

1. Add sentence-transformers to requirements
2. Create script to regenerate embeddings with real model
3. Update search to use cosine similarity with real vectors
4. Keep existing schema

**Phase 2: Add metadata filtering**

1. Extend Reference model with structured fields
2. Parse existing content to extract metadata
3. Update search to support filters
4. Update UI to show filter options

**Phase 3: Implement chunking**

1. Create DocumentChunk and ChunkEmbedding tables
2. Split existing documents into chunks
3. Generate embeddings per chunk
4. Update search to retrieve chunks, group by source

**Phase 4: Specialized schemas (Optional)**

1. Create Spell, MagicItem, Class tables
2. Migrate data from references
3. Tailored search per content type

## Implementation Example: Phase 1

```python
# scripts/generate_real_embeddings.py
from sentence_transformers import SentenceTransformer
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.models import Reference, ReferenceEmbedding
import json

model = SentenceTransformer('all-MiniLM-L6-v2')

engine = create_engine('sqlite:///storycraft.db')
Session = sessionmaker(bind=engine)
session = Session()

refs = session.query(Reference).all()
print(f'Generating embeddings for {len(refs)} references...')

for ref in refs:
    text = f"{ref.title}\n{ref.content[:1000]}"  # Title + first 1000 chars
    vector = model.encode(text).tolist()

    emb = session.query(ReferenceEmbedding).filter(
        ReferenceEmbedding.reference_id == ref.id
    ).first()

    if emb:
        emb.vector = json.dumps(vector)
        emb.model = 'all-MiniLM-L6-v2'
    else:
        emb = ReferenceEmbedding(
            reference_id=ref.id,
            vector=json.dumps(vector),
            model='all-MiniLM-L6-v2'
        )
        session.add(emb)

    session.commit()

session.close()
print('Done!')
```

## Quick Wins for Better RAG (Today)

1. **Add stopword filtering** ✅ (Already done in chat.py)
2. **Boost keyword matches** ✅ (Already done)
3. **Add metadata fields** - Extract spell level, item rarity from content
4. **Use real embeddings** - Install sentence-transformers
5. **Add result re-ranking** - Re-score by relevance to last user message

## Resources

- Sentence Transformers: https://www.sbert.net/
- FAISS: https://github.com/facebookresearch/faiss
- Qdrant: https://qdrant.tech/
- pgvector: https://github.com/pgvector/pgvector
- RAG best practices: https://www.pinecone.io/learn/retrieval-augmented-generation/
