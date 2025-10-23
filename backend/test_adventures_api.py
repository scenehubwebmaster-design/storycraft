"""Test the adventures API endpoint to see if it returns templates."""
import sys
sys.path.insert(0, 'e:/storycraft')

from backend.database import SessionLocal
from backend.models import Reference
from backend.routers.adventures import extract_metadata_from_reference

session = SessionLocal()

print('='*70)
print('TESTING ADVENTURE TEMPLATE EXTRACTION')
print('='*70)

# Get references that might be adventure overviews
overview_refs = session.query(Reference).filter(
    Reference.key.like('%/overview/%')
).limit(10).all()

print(f'\nFound {len(overview_refs)} references with /overview/ in key\n')

templates = []
for i, ref in enumerate(overview_refs):
    print(f'\n{i+1}. Testing {ref.key}')
    print(f'   Type: {ref.ref_type}')
    print(f'   Tags: {ref.tags[:80]}...' if len(str(ref.tags)) > 80 else f'   Tags: {ref.tags}')
    
    template = extract_metadata_from_reference(ref)
    if template:
        print('   ✅ EXTRACTED TEMPLATE!')
        print(f'      Title: {template.title}')
        print(f'      Campaign Type: {template.campaign_type}')
        print(f'      Level Range: {template.level_range}')
        print(f'      Source: {template.source}')
        print(f'      Themes: {template.themes}')
        templates.append(template)
    else:
        print('   ❌ No template extracted')

print('\n' + '='*70)
print(f'RESULTS: Extracted {len(templates)} templates from {len(overview_refs)} overview references')
print('='*70)

for i, template in enumerate(templates):
    print(f'\n{i+1}. {template.title}')
    print(f'   ID: {template.id}')
    print(f'   Type: {template.campaign_type} | Levels: {template.level_range}')
    print(f'   Source: {template.source}')
    print(f'   Themes: {", ".join(template.themes)}')

session.close()
