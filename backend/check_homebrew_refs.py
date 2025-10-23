import sys
import os

# Add backend to path
backend_path = os.path.dirname(os.path.abspath(__file__))
parent_path = os.path.dirname(backend_path)
sys.path.insert(0, parent_path)

from backend.database import SessionLocal
from backend.models import Reference

db = SessionLocal()

print("Checking homebrew references...\n")

# Get some homebrew references
homebrew_refs = db.query(Reference).filter(
    Reference.key.like('%Bloodmoon%')
).limit(10).all()

print(f"Found {len(homebrew_refs)} Bloodmoon references\n")

for ref in homebrew_refs:
    print(f"Key: {ref.key}")
    print(f"Title: {ref.title}")
    print(f"Type: {ref.ref_type}")
    print(f"Tags: {ref.tags[:5] if ref.tags else []}")
    print(f"Key parts: {ref.key.split('/')}")
    print(f"Depth: {ref.key.count('/')}")
    print("-" * 80)

print("\n\nChecking for adventure index files...\n")

# Check for adventure overview files
adventure_indices = db.query(Reference).filter(
    Reference.key.like('%/index')
).limit(20).all()

print(f"Found {len(adventure_indices)} index files\n")

for ref in adventure_indices:
    parts = ref.key.split('/')
    print(f"Key: {ref.key}")
    print(f"  Depth: {len(parts)} parts")
    print(f"  Has items: {'items' in parts}")
    print(f"  Has npcs: {'npcs' in parts}")
    print(f"  Has locations: {'locations' in parts}")
    print(f"  Title: {ref.title}")
    print()

db.close()
