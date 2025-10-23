"""
API endpoints for adventure template management.

Provides endpoints to fetch adventure modules from the RAG system
for use in campaign creation wizards.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from typing import List, Optional
from pydantic import BaseModel

from backend.database import get_db
from backend.models import Reference

router = APIRouter(prefix="/api/adventures", tags=["adventures"])


class AdventureTemplate(BaseModel):
    """Adventure template for campaign wizard."""
    id: str
    title: str
    description: str
    level_range: str
    campaign_type: str  # one_shot, short_adventure, epic_campaign
    themes: List[str]
    setting: Optional[str] = None
    tier: Optional[int] = None
    source: str  # guild_modules, generated, homebrew


class AdventureListResponse(BaseModel):
    """Response containing list of adventure templates."""
    templates: List[AdventureTemplate]
    total: int
    by_type: dict


def extract_metadata_from_reference(ref: Reference) -> Optional[AdventureTemplate]:
    """
    Extract adventure template metadata from a Reference document.
    
    Since frontmatter is stripped during ingestion, we rely on:
    - ref.tags: Contains metadata like themes, settings, campaign_type
    - ref.ref_type: Indicates source (guild_modules, generated, homebrew)
    - ref.key: Module path (e.g., "module_name/overview/index")
    - ref.content: Markdown content with title and description
    """
    try:
        # Only process true adventure overview/index/README files
        # Patterns:
        # - /overview/index or /overview/README (generated adventures)
        # - /README at 2-level depth (tyranny_of_dragons sub-adventures)
        # - /index at 2-level depth for guild modules OR 3-level for homebrew adventures
        # - EXCLUDE: items/index, npcs/index, locations/index, mechanics/index, etc.
        
        # Skip item/npc/location/mechanic/handout/parts subdirectories
        excluded_subdirs = ['items', 'npcs', 'locations', 'mechanics', 'handouts', 'parts', 'maps']
        key_parts = ref.key.split('/')
        if any(subdir in key_parts for subdir in excluded_subdirs):
            return None
        
        # Also skip if tags indicate this is an item/npc/location list
        if ref.tags:
            excluded_tags = ['items', 'npcs', 'locations', 'mechanics', 'handouts']
            if any(tag in ref.tags for tag in excluded_tags):
                return None
        
        # Skip if title suggests this is an item/treasure list
        if ref.title and any(word in ref.title.lower() for word in ['notable items', 'items & treasure', 'items & lore', 'treasure &', 'items & relics', 'items & clues']):
            return None
        
        is_overview = (
            ref.key.endswith('/overview/index') or 
            ref.key.endswith('/overview/README')
        )
        
        # Module-level README files (tyranny_of_dragons adventures)
        if ref.key.endswith('/README') and ref.key.count('/') == 2:
            is_overview = True
        
        # Module-level index files (2-level depth)
        # Guild modules: tyranny_of_dragons/hoard_of_the_dragon_queen/index
        # Homebrew adventures: Bloodmoon_Epitaph/Epitaph_of_Thorns/index
        if ref.key.endswith('/index') and ref.key.count('/') == 2:
            is_overview = True
        
        if not is_overview:
            return None
        
        # Skip if ref_type doesn't indicate adventure content
        if ref.ref_type not in ['guild_modules', 'generated_modules', 'homebrew_modules']:
            # For backwards compatibility, also accept if tags contain 'adventure'
            if not ref.tags or 'adventure' not in str(ref.tags).lower():
                return None
        
        # Determine source from key structure (most reliable)
        source = "guild_modules"  # default
        
        if 'homebrew_adventures' in ref.key:
            source = "homebrew"
        elif 'generated_content' in ref.key:
            source = "generated"
        elif 'guild_modules' in ref.key or 'tyranny' in ref.key.lower():
            source = "guild_modules"
        
        # Extract themes from tags
        themes = []
        if ref.tags:
            tags = ref.tags if isinstance(ref.tags, list) else []
            # Filter out meta tags, keep descriptive themes
            meta_tags = ['guild_module', 'adventure', 'ddal', 'overview', 'generated', 'homebrew']
            themes = [tag for tag in tags if tag not in meta_tags and not tag.startswith('_')]
            # Limit to first 5 most relevant themes
            themes = themes[:5]
        
        # Extract description from content (first few lines after title)
        description = ""
        lines = ref.content.split('\n')
        found_title = False
        desc_lines = []
        for line in lines:
            line = line.strip()
            if not found_title and line.startswith('#'):
                found_title = True
                continue
            if found_title and line and not line.startswith('#') and not line.startswith('**'):
                desc_lines.append(line)
                if len(' '.join(desc_lines)) > 200:  # Limit description length
                    break
        description = ' '.join(desc_lines)[:300] + ('...' if len(' '.join(desc_lines)) > 300 else '')
        
        # Extract level range from content
        level_range = "1-5"  # default
        import re
        # Look for common level range patterns
        level_patterns = [
            r'levels?\s+(\d+[-–]\d+)',
            r'tier\s+(\d)',
            r'APL\s+(\d+)',
            r'level\s+range:\s*(\d+[-–]\d+)'
        ]
        for pattern in level_patterns:
            match = re.search(pattern, ref.content, re.IGNORECASE)
            if match:
                level_range = match.group(1).replace('–', '-')
                break
        
        # Determine campaign type based on level range and module name
        campaign_type = "short_adventure"  # default
        if '-' in level_range:
            start, end = map(int, level_range.split('-'))
            level_span = end - start
            if level_span >= 10:
                campaign_type = "epic_campaign"
            elif level_span >= 5:
                campaign_type = "medium_campaign"
            elif level_span <= 2:
                campaign_type = "one_shot"
        
        # Check if keywords in title/content suggest campaign type
        title_lower = ref.title.lower()
        if any(word in title_lower for word in ['epic', 'campaign', 'saga', 'tyranny']):
            campaign_type = "epic_campaign"
        elif any(word in title_lower for word in ['one-shot', 'oneshot', 'quick']):
            campaign_type = "one_shot"
        
        # Extract setting from tags
        setting = None
        setting_keywords = ['underdark', 'forgotten_realms', 'phlan', 'waterdeep', 'baldurs_gate', 'faerun']
        for tag in (ref.tags or []):
            if any(keyword in str(tag).lower() for keyword in setting_keywords):
                setting = tag
                break
        
        # Determine tier from level range
        tier = 1  # Tier 1: levels 1-5
        if '-' in level_range:
            start_level = int(level_range.split('-')[0])
            if start_level <= 5:
                tier = 1
            elif start_level <= 10:
                tier = 2
            elif start_level <= 15:
                tier = 3
            else:
                tier = 4
        
        return AdventureTemplate(
            id=ref.key,
            title=ref.title,
            description=description or "No description available.",
            level_range=level_range,
            campaign_type=campaign_type,
            themes=themes if themes else ["adventure"],
            setting=setting,
            tier=tier,
            source=source
        )
    except Exception as e:
        print(f"Error extracting metadata from {ref.key}: {e}")
        return None


@router.get("/templates", response_model=AdventureListResponse)
async def get_adventure_templates(
    campaign_type: Optional[str] = None,
    source: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get adventure templates for campaign creation wizard.
    
    Args:
        campaign_type: Filter by type (one_shot, short_adventure, epic_campaign)
        source: Filter by source (guild_modules, generated, homebrew)
    """
    try:
        # Query for adventure index/overview documents only
        # Patterns:
        # - Generated adventures: */overview/index or */overview/README
        # - Guild modules: */module_name/README or */module_name/index
        # - Homebrew adventures: */collection/adventure/index
        query = db.query(Reference).filter(
            and_(
                Reference.ref_type == 'guild_modules',
                or_(
                    Reference.key.like('%/index'),
                    Reference.key.like('%/README'),
                    Reference.key.like('%/overview/%')
                ),
                # Exclude subdirectories that are not adventure roots
                ~Reference.key.like('%/items/%'),
                ~Reference.key.like('%/npcs/%'),
                ~Reference.key.like('%/locations/%'),
                ~Reference.key.like('%/mechanics/%'),
                ~Reference.key.like('%/handouts/%'),
                ~Reference.key.like('%/parts/%'),
                ~Reference.key.like('%/maps/%')
            )
        )
        
        # Get all references
        references = query.all()
        print(f"[DEBUG] Found {len(references)} potential adventure references")
        
        # Extract adventure templates and deduplicate
        templates = []
        seen_adventures = {}  # Track by adventure module path
        
        for ref in references:
            template = extract_metadata_from_reference(ref)
            if template:
                # Debug: log extracted templates
                print(f"[EXTRACTED] {template.title} ({template.id}) - Source: {template.source}")
                # Extract adventure module path (first 2 parts of key)
                # e.g., "crown_of_the_fire_giants/overview/index" -> "crown_of_the_fire_giants"
                key_parts = template.id.split('/')
                adventure_key = key_parts[0] if key_parts else template.id
                
                # Only keep first occurrence of each adventure
                if adventure_key not in seen_adventures:
                    seen_adventures[adventure_key] = template
                    templates.append(template)
                else:
                    # If we found a better version (e.g., index.md vs README.md), prefer index
                    existing = seen_adventures[adventure_key]
                    if template.id.endswith('/index') and not existing.id.endswith('/index'):
                        # Replace with index version
                        templates.remove(existing)
                        templates.append(template)
                        seen_adventures[adventure_key] = template
        
        # Filter by campaign type
        if campaign_type:
            templates = [t for t in templates if t.campaign_type == campaign_type]
        
        # Filter by source
        if source:
            templates = [t for t in templates if t.source == source]
        
        # Sort by source and title
        templates.sort(key=lambda t: (t.source, t.title))
        
        # Count by type
        by_type = {
            "one_shot": len([t for t in templates if t.campaign_type == "one_shot"]),
            "short_adventure": len([t for t in templates if t.campaign_type == "short_adventure"]),
            "epic_campaign": len([t for t in templates if t.campaign_type == "epic_campaign"])
        }
        
        return AdventureListResponse(
            templates=templates,
            total=len(templates),
            by_type=by_type
        )
    
    except Exception as e:
        print(f"Error fetching adventure templates: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/templates/{template_id}")
async def get_adventure_template(
    template_id: str,
    db: Session = Depends(get_db)
):
    """Get detailed information about a specific adventure template."""
    try:
        # Find the reference with this ID
        ref = db.query(Reference).filter(
            Reference.content.like(f"%{template_id}%")
        ).first()
        
        if not ref:
            raise HTTPException(status_code=404, detail="Adventure template not found")
        
        template = extract_metadata_from_reference(ref)
        if not template:
            raise HTTPException(status_code=404, detail="Could not parse adventure template")
        
        return template
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error fetching adventure template: {e}")
        raise HTTPException(status_code=500, detail=str(e))
