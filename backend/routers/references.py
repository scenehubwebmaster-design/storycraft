from fastapi import APIRouter, HTTPException, Depends, Header
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
def sync_references_from_disk(db: Session = Depends(get_db), x_admin_token: str = Header(None)):
    """
    Scan the repository's `documents/` folder for Markdown files and upsert them into the references table.
    Filenames should be like `ClassName_PHB2024.md` or `Species_PHB2024.md`.
    The ref_type will be inferred from the filename prefix (lowercased).
    """
    # Simple admin protection: require env key to be set and passed in X-Admin-Token header
    required = os.environ.get("REF_SYNC_KEY")
    if not required:
        # If no key configured, disallow the endpoint by default in production setups
        raise HTTPException(status_code=403, detail="Reference sync is disabled on this server")
    if x_admin_token != required:
        raise HTTPException(status_code=403, detail="Invalid admin token for reference sync")

    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    docs_dir = os.path.join(repo_root, "documents")
    if not os.path.isdir(docs_dir):
        raise HTTPException(status_code=404, detail=f"Documents folder not found at {docs_dir}")

    imported = []
    for p in pathlib.Path(docs_dir).glob("*.md"):
        try:
            stem = p.stem
            # Infer type and key: split on underscore or space
            parts = stem.split("_")
            if len(parts) >= 1 and parts[0]:
                inferred = parts[0].lower()
            else:
                inferred = "unknown"

            ref_type = inferred
            key = stem.replace(" ", "_").lower()
            title = parts[0].replace("-", " ")
            content = p.read_text(encoding="utf-8")

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
