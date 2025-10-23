import sys
sys.path.insert(0, 'e:\\storycraft\\backend')

from backend.database import SessionLocal
from backend.models import Reference

db = SessionLocal()

# Check bloodmoon references
refs = db.query(Reference).filter(Reference.key.like('%bloodmoon%')).all()

print("Bloodmoon references:")
for r in refs[:15]:
    print(f"Key: {r.key}")
    print(f"Title: {r.title}")
    print(f"Type: {r.ref_type}")
    print(f"Tags: {r.tags}")
    print(f"Content preview: {r.content[:100]}")
    print("-" * 80)

# Check actual campaigns
print("\n\nActual campaign references:")
campaign_refs = db.query(Reference).filter(
    Reference.key.like('%tyranny_of_dragons%')
).all()

for r in campaign_refs[:5]:
    print(f"Key: {r.key}")
    print(f"Title: {r.title}")
    print(f"Type: {r.ref_type}")
    print("-" * 80)

db.close()
