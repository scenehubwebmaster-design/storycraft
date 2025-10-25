"""
Interactive NPC Portrait Review and Regeneration Tool

Browse all generated portraits, compare with NPC descriptions,
and selectively regenerate portraits that didn't turn out well.

Usage:
    python review_npc_portraits.py [--campaign-id ID]
"""

import asyncio
import argparse
import sys
from pathlib import Path
from datetime import datetime
from sqlalchemy.orm import Session
import base64

# Add backend to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from .database import SessionLocal
from .models import NPC, Campaign, GameSession
from .stablediffusion_client import StableDiffusionClient

# Portrait storage directory
PORTRAIT_DIR = Path(__file__).parent / "static" / "npc_portraits"


def print_header(text):
    """Print formatted section header."""
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80)


def print_npc_card(npc: NPC, index: int, total: int):
    """Display NPC information card."""
    print(f"\n[{index}/{total}] NPC: {npc.name}")
    print("-" * 80)
    
    if npc.role:
        print(f"  Role: {npc.role}")
    
    if npc.description:
        # Truncate long descriptions
        desc = npc.description
        if len(desc) > 300:
            desc = desc[:300] + "..."
        print(f"  Description: {desc}")
    
    if npc.personality:
        pers = npc.personality
        if len(pers) > 200:
            pers = pers[:200] + "..."
        print(f"  Personality: {pers}")
    
    if npc.location:
        print(f"  Location: {npc.location}")
    
    if npc.first_met_location:
        print(f"  First Met: {npc.first_met_location}")
    
    print(f"  Importance: {'⭐' * (npc.importance or 3)}")
    
    if npc.relationship_to_party is not None:
        rel = npc.relationship_to_party
        rel_label = "Hostile" if rel < -50 else "Unfriendly" if rel < 0 else "Neutral" if rel < 50 else "Friendly"
        print(f"  Relationship: {rel_label} ({rel:+d})")
    
    if npc.tags:
        print(f"  Tags: {', '.join(npc.tags)}")
    
    if npc.portrait_path:
        portrait_file = PORTRAIT_DIR / npc.portrait_path.split('/')[-1]
        if portrait_file.exists():
            file_size = portrait_file.stat().st_size / 1024  # KB
            print(f"  Portrait: {npc.portrait_path} ({file_size:.1f} KB)")
            if npc.portrait_prompt:
                prompt_preview = npc.portrait_prompt[:150]
                if len(npc.portrait_prompt) > 150:
                    prompt_preview += "..."
                print(f"  Prompt: {prompt_preview}")
        else:
            print(f"  Portrait: {npc.portrait_path} [FILE NOT FOUND]")
    else:
        print("  Portrait: [NONE]")
    
    print("-" * 80)


async def review_portraits(campaign_id: int = None):
    """
    Interactive portrait review workflow.
    """
    db: Session = SessionLocal()
    
    try:
        # Build query
        query = db.query(NPC)
        
        if campaign_id:
            # Filter by campaign
            query = query.join(GameSession).join(Campaign).filter(Campaign.id == campaign_id)
            campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
            print_header(f"Reviewing Portraits for Campaign: {campaign.name if campaign else 'Unknown'}")
        else:
            print_header("Reviewing All NPC Portraits")
        
        # Only NPCs with portraits
        query = query.filter(NPC.portrait_path.isnot(None))
        npcs = query.all()
        
        if not npcs:
            print("\n❌ No NPCs with portraits found!")
            return
        
        print(f"\nFound {len(npcs)} NPCs with portraits\n")
        
        # Initialize SD client (for regeneration)
        sd_client = StableDiffusionClient()
        
        # Review each NPC
        to_regenerate = []
        
        for i, npc in enumerate(npcs, 1):
            print_npc_card(npc, i, len(npcs))
            
            # Ask user for action
            while True:
                choice = input(
                    "\nActions: [K]eep, [R]egenerate, [D]elete portrait, [S]kip to end, [Q]uit\n"
                    "Your choice: "
                ).strip().lower()
                
                if choice == 'k':
                    print("✓ Keeping portrait")
                    break
                elif choice == 'r':
                    to_regenerate.append(npc)
                    print("⚡ Marked for regeneration")
                    break
                elif choice == 'd':
                    # Delete portrait file and clear DB reference
                    if npc.portrait_path:
                        portrait_file = PORTRAIT_DIR / npc.portrait_path.split('/')[-1]
                        if portrait_file.exists():
                            portrait_file.unlink()
                            print(f"🗑️  Deleted file: {portrait_file}")
                        npc.portrait_path = None
                        npc.portrait_prompt = None
                        db.commit()
                    print("✓ Portrait deleted")
                    break
                elif choice == 's':
                    print(f"⏭️  Skipping remaining {len(npcs) - i} NPCs")
                    to_regenerate.extend(npcs[i:])
                    break
                elif choice == 'q':
                    print("👋 Exiting review")
                    return
                else:
                    print("❌ Invalid choice. Try again.")
            
            if choice == 's' or choice == 'q':
                break
        
        # Regeneration phase
        if to_regenerate:
            print_header(f"Regenerating {len(to_regenerate)} Portraits")
            
            for i, npc in enumerate(to_regenerate, 1):
                print(f"\n[{i}/{len(to_regenerate)}] Regenerating: {npc.name}")
                
                # Option to edit prompt
                current_prompt = generate_portrait_prompt(npc)
                print(f"\nCurrent prompt:\n{current_prompt}\n")
                
                edit_prompt = input("Edit prompt? [y/N]: ").strip().lower()
                if edit_prompt == 'y':
                    print("Enter new prompt (or press Enter to keep current):")
                    new_prompt = input("> ").strip()
                    if new_prompt:
                        current_prompt = new_prompt
                
                # Generate new portrait
                try:
                    print("🎨 Generating portrait...")
                    image_base64 = await sd_client.generate_image(
                        prompt=current_prompt,
                        negative_prompt=(
                            "nsfw, nude, blurry, low quality, distorted, deformed, "
                            "multiple heads, extra limbs, bad anatomy, watermark, signature"
                        ),
                        width=512,
                        height=768,
                        steps=30,
                        cfg_scale=7.0
                    )
                    
                    # Delete old portrait if exists
                    if npc.portrait_path:
                        old_file = PORTRAIT_DIR / npc.portrait_path.split('/')[-1]
                        if old_file.exists():
                            old_file.unlink()
                    
                    # Save new portrait
                    filename = f"{sanitize_filename(npc.name)}_{npc.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                    filepath = PORTRAIT_DIR / filename
                    
                    image_data = base64.b64decode(image_base64)
                    with open(filepath, 'wb') as f:
                        f.write(image_data)
                    
                    # Update database
                    npc.portrait_path = f"npc_portraits/{filename}"
                    npc.portrait_prompt = current_prompt
                    db.commit()
                    
                    print(f"✅ Saved new portrait: {filename}")
                    
                except Exception as e:
                    print(f"❌ Generation failed: {e}")
                    continue
                
                # Small delay between generations
                await asyncio.sleep(1)
            
            print_header("Regeneration Complete!")
        else:
            print("\n✨ No portraits marked for regeneration")
    
    finally:
        db.close()


def sanitize_filename(name: str) -> str:
    """Convert NPC name to safe filename."""
    safe = "".join(c for c in name.lower() if c.isalnum() or c in (' ', '-', '_'))
    return safe.replace(' ', '_')


def generate_portrait_prompt(npc: NPC) -> str:
    """
    Generate SD prompt from NPC description.
    """
    base_prompt = "fantasy RPG character portrait, "
    
    if npc.role:
        base_prompt += f"{npc.role}, "
    
    if npc.description:
        base_prompt += f"{npc.description[:200]}, "
    
    if npc.personality:
        personality_lower = npc.personality.lower()
        if any(word in personality_lower for word in ["kind", "gentle", "warm"]):
            base_prompt += "warm expression, friendly, "
        elif any(word in personality_lower for word in ["stern", "serious", "gruff"]):
            base_prompt += "stern expression, serious, "
        elif any(word in personality_lower for word in ["cunning", "sly", "clever"]):
            base_prompt += "sly smile, intelligent eyes, "
    
    base_prompt += (
        "highly detailed, professional digital art, "
        "trending on artstation, fantasy character design, "
        "detailed face, expressive eyes, cinematic lighting"
    )
    
    return base_prompt


def main():
    parser = argparse.ArgumentParser(description="Review and regenerate NPC portraits")
    parser.add_argument("--campaign-id", type=int, help="Only review NPCs from specific campaign")
    
    args = parser.parse_args()
    
    print("\n" + "=" * 80)
    print("  🖼️  NPC PORTRAIT REVIEW & REGENERATION TOOL")
    print("=" * 80)
    print("\nThis tool lets you:")
    print("  • Review all generated NPC portraits")
    print("  • Compare portraits with NPC descriptions")
    print("  • Selectively regenerate portraits that didn't turn out well")
    print("  • Edit prompts before regenerating")
    print("  • Delete unwanted portraits")
    
    asyncio.run(review_portraits(campaign_id=args.campaign_id))


if __name__ == "__main__":
    main()
