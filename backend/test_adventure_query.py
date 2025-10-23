import sys
import os

backend_path = os.path.dirname(os.path.abspath(__file__))
parent_path = os.path.dirname(backend_path)
sys.path.insert(0, parent_path)

from backend.database import SessionLocal
from backend.models import Reference
from sqlalchemy import or_, and_

db = SessionLocal()

# Same query as adventures.py
query = db.query(Reference).filter(
    and_(
        Reference.ref_type == 'guild_modules',
        or_(
            Reference.key.like('%/index'),
            Reference.key.like('%/README'),
            Reference.key.like('%/overview/%')
        )
    )
)

references = query.all()

print(f"Found {len(references)} references matching query\n")

# Check for homebrew
homebrew_refs = [r for r in references if 'Bloodmoon' in r.key or 'Bloodsand' in r.key]
print(f"\nHomebrew references found: {len(homebrew_refs)}")
for ref in homebrew_refs[:10]:
    print(f"Key: {ref.key}")
    print(f"  Title: {ref.title}")
    print(f"  Tags: {ref.tags[:5] if ref.tags else []}")
    print()

db.close()
