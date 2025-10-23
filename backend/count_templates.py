"""Count total adventure templates available."""
import sys
sys.path.insert(0, 'e:/storycraft')

from backend.database import SessionLocal
from backend.models import Reference
from backend.routers.adventures import extract_metadata_from_reference
from sqlalchemy import or_

session = SessionLocal()

# Get all index/overview references (main adventure pages)
# Look for /overview/index, /overview/README, and 2-level /README and /index patterns
all_refs = session.query(Reference).filter(
    or_(
        Reference.key.like('%/overview/index'),
        Reference.key.like('%/overview/README'),
        Reference.key.like('%/index'),
        Reference.key.like('%/README')
    )
).all()

print('='*70)
print('ADVENTURE TEMPLATE STATISTICS')
print('='*70)
print(f'\nTotal index/overview/README references: {len(all_refs)}')

templates = []
sources = {'guild_modules': 0, 'generated': 0, 'homebrew': 0}
campaign_types = {'one_shot': 0, 'short_adventure': 0, 'medium_campaign': 0, 'epic_campaign': 0}

for ref in all_refs:
    template = extract_metadata_from_reference(ref)
    if template:
        templates.append(template)
        sources[template.source] = sources.get(template.source, 0) + 1
        campaign_types[template.campaign_type] = campaign_types.get(template.campaign_type, 0) + 1

print(f'Successfully extracted: {len(templates)} templates\n')

print('By Source:')
for source, count in sources.items():
    print(f'  {source}: {count}')

print('\nBy Campaign Type:')
for ctype, count in campaign_types.items():
    print(f'  {ctype}: {count}')

print('\n' + '='*70)
print('SAMPLE TEMPLATES (First 10)')
print('='*70)

for i, template in enumerate(templates[:10]):
    print(f'\n{i+1}. {template.title}')
    print(f'   Source: {template.source} | Type: {template.campaign_type}')
    print(f'   Levels: {template.level_range} | Tier: {template.tier}')
    print(f'   Themes: {", ".join(template.themes)}')

session.close()
