"""Check the actual format of Reference.content in the database."""
import sys
sys.path.insert(0, 'e:/storycraft')

from backend.database import SessionLocal
from backend.models import Reference

session = SessionLocal()

# Get total count
total = session.query(Reference).count()
print(f'Total references in database: {total}\n')

# Check what ref_types exist
ref_types = session.query(Reference.ref_type).distinct().all()
print('All ref_types in database:')
for rt in ref_types:
    count = session.query(Reference).filter(Reference.ref_type == rt[0]).count()
    print(f'  {rt[0]}: {count} references')

print('\n' + '='*70 + '\n')

# Look for anything with "module" in the tags
module_refs = session.query(Reference).filter(
    Reference.tags.like('%module%')
).limit(5).all()

print(f'Found {len(module_refs)} references with "module" in tags\n')
for i, ref in enumerate(module_refs):
    print(f'{i+1}. {ref.title}')
    print(f'   Key: {ref.key}')
    print(f'   Type: {ref.ref_type}')
    print(f'   Tags: {ref.tags[:100]}...' if len(str(ref.tags)) > 100 else f'   Tags: {ref.tags}')
    print()

session.close()
