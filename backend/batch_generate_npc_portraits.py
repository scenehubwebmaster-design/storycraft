"""
Batch generate portraits for NPCs in the database.

This script:
1. Finds all NPCs without portraits
2. Generates portraits using Stable Diffusion
3. Saves images to backend/static/npc_portraits/
4. Updates NPC records with file paths instead of base64

Usage:
    python batch_generate_npc_portraits.py [--limit N] [--campaign-id ID] [--force]
    
Options:
    --limit N         Generate portraits for at most N NPCs (default: all)
    --campaign-id ID  Only generate for NPCs in specific campaign
    --force          Regenerate even if portrait already exists
    --dry-run        Show what would be generated without actually generating
"""

import asyncio
import argparse
import base64
import sys
from pathlib import Path
from datetime import datetime
from sqlalchemy.orm import Session

# Add backend to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from .database import SessionLocal
from .models import NPC, Campaign, GameSession
from .stablediffusion_client import StableDiffusionClient
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

# Portrait storage directory
PORTRAIT_DIR = Path(__file__).parent / "static" / "npc_portraits"
PORTRAIT_DIR.mkdir(parents=True, exist_ok=True)

# Default portrait generation settings
DEFAULT_SETTINGS = {
    "width": 512,
    "height": 768,  # Portrait orientation
    "steps": 30,
    "cfg_scale": 7.0,
    "negative_prompt": (
        "nsfw, nude, blurry, low quality, distorted, deformed, "
        "multiple heads, extra limbs, bad anatomy, watermark, signature"
    )
}


def sanitize_filename(name: str) -> str:
    """Convert NPC name to safe filename."""
    # Remove special characters, lowercase, replace spaces with underscores
    safe = "".join(c for c in name.lower() if c.isalnum() or c in (' ', '-', '_'))
    return safe.replace(' ', '_')


def generate_portrait_prompt(npc: NPC) -> str:
    """
    Generate SD prompt from NPC description.
    
    Extracts physical appearance details and adds fantasy RPG styling.
    """
    base_prompt = "fantasy RPG character portrait, "
    
    # Add role/occupation
    if npc.role:
        base_prompt += f"{npc.role}, "
    
    # Add description (focus on appearance)
    if npc.description:
        # Add appearance details (truncate to keep prompt reasonable)
        base_prompt += f"{npc.description[:200]}, "
    
    # Add personality hints for expression
    if npc.personality:
        personality_lower = npc.personality.lower()
        if any(word in personality_lower for word in ["kind", "gentle", "warm"]):
            base_prompt += "warm expression, friendly, "
        elif any(word in personality_lower for word in ["stern", "serious", "gruff"]):
            base_prompt += "stern expression, serious, "
        elif any(word in personality_lower for word in ["cunning", "sly", "clever"]):
            base_prompt += "sly smile, intelligent eyes, "
    
    # Add quality tags
    base_prompt += (
        "highly detailed, professional digital art, "
        "trending on artstation, fantasy character design, "
        "detailed face, expressive eyes, cinematic lighting"
    )
    
    return base_prompt


async def generate_portrait(
    npc: NPC,
    sd_client: StableDiffusionClient,
    force: bool = False
) -> bool:
    """
    Generate portrait for a single NPC.
    
    Returns True if portrait was generated, False if skipped.
    """
    # Skip if portrait already exists (unless force)
    if npc.portrait_path and not force:
        portrait_file = PORTRAIT_DIR / npc.portrait_path.split('/')[-1]
        if portrait_file.exists():
            logger.info(f"⏭️  Skipping {npc.name} - portrait already exists")
            return False
    
    logger.info(f"🎨 Generating portrait for: {npc.name}")
    
    # Generate prompt
    prompt = generate_portrait_prompt(npc)
    logger.info(f"   Prompt: {prompt[:100]}...")
    
    try:
        # Generate image
        image_base64 = await sd_client.generate_image(
            prompt=prompt,
            negative_prompt=DEFAULT_SETTINGS["negative_prompt"],
            width=DEFAULT_SETTINGS["width"],
            height=DEFAULT_SETTINGS["height"],
            steps=DEFAULT_SETTINGS["steps"],
            cfg_scale=DEFAULT_SETTINGS["cfg_scale"]
        )
        
        # Save to file
        filename = f"{sanitize_filename(npc.name)}_{npc.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        filepath = PORTRAIT_DIR / filename
        
        # Decode base64 and save
        image_data = base64.b64decode(image_base64)
        with open(filepath, 'wb') as f:
            f.write(image_data)
        
        # Update NPC record with relative path
        relative_path = f"npc_portraits/{filename}"
        
        logger.info(f"✅ Saved portrait to: {relative_path}")
        
        return True, relative_path, prompt
        
    except Exception as e:
        logger.error(f"❌ Failed to generate portrait for {npc.name}: {e}")
        return False, None, None


async def batch_generate(
    campaign_id: int = None,
    limit: int = None,
    force: bool = False,
    dry_run: bool = False
):
    """
    Main batch generation function.
    """
    db: Session = SessionLocal()
    
    try:
        # Build query
        query = db.query(NPC)
        
        if campaign_id:
            # Filter by campaign (join through game_session)
            query = query.join(GameSession).join(Campaign).filter(Campaign.id == campaign_id)
            logger.info(f"🎯 Filtering to campaign ID: {campaign_id}")
        
        if not force:
            # Only NPCs without portraits
            query = query.filter(NPC.portrait_path.is_(None))
        
        npcs = query.limit(limit).all() if limit else query.all()
        
        logger.info(f"📋 Found {len(npcs)} NPCs to process")
        
        if not npcs:
            logger.info("✨ No NPCs need portraits!")
            return
        
        if dry_run:
            logger.info("\n🔍 DRY RUN - NPCs that would be processed:")
            for npc in npcs:
                logger.info(f"   - {npc.name} (ID: {npc.id}, Role: {npc.role})")
            return
        
        # Initialize SD client
        logger.info("🚀 Initializing Stable Diffusion client...")
        sd_client = StableDiffusionClient()
        
        # Generate portraits
        success_count = 0
        skip_count = 0
        fail_count = 0
        
        for i, npc in enumerate(npcs, 1):
            logger.info(f"\n[{i}/{len(npcs)}] Processing: {npc.name}")
            
            result = await generate_portrait(npc, sd_client, force)
            
            if result:
                success, relative_path, prompt = result
                if success:
                    # Update database
                    npc.portrait_path = relative_path
                    npc.portrait_prompt = prompt
                    db.commit()
                    success_count += 1
                    logger.info("   ✅ Updated database record")
                else:
                    fail_count += 1
            else:
                skip_count += 1
            
            # Small delay to avoid overwhelming SD server
            await asyncio.sleep(1)
        
        logger.info("\n🎉 Batch generation complete!")
        logger.info(f"   ✅ Generated: {success_count}")
        logger.info(f"   ⏭️  Skipped: {skip_count}")
        logger.info(f"   ❌ Failed: {fail_count}")
        
    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser(description="Batch generate NPC portraits")
    parser.add_argument("--limit", type=int, help="Maximum number of portraits to generate")
    parser.add_argument("--campaign-id", type=int, help="Only generate for specific campaign")
    parser.add_argument("--force", action="store_true", help="Regenerate existing portraits")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be generated")
    
    args = parser.parse_args()
    
    logger.info("🎨 NPC Portrait Batch Generator")
    logger.info("=" * 50)
    
    asyncio.run(batch_generate(
        campaign_id=args.campaign_id,
        limit=args.limit,
        force=args.force,
        dry_run=args.dry_run
    ))


if __name__ == "__main__":
    main()
