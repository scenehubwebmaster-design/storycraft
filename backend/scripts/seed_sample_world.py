"""
Seed script to create a sample world with a generated world_map image.
Run from the repository root: python backend\scripts\seed_sample_world.py
"""
import base64
from io import BytesIO
import os

# Ensure backend package imports work when run from repo root
import sys
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from database import SessionLocal, engine, Base
from models import World

# Create a simple image using Pillow
try:
    from PIL import Image, ImageDraw, ImageFont
except Exception:
    raise SystemExit("Pillow is required to run this script. Install with: pip install pillow")


def make_sample_image(size=(512, 512)):
    img = Image.new('RGBA', size, (40, 40, 80, 255))
    draw = ImageDraw.Draw(img)
    w, h = size
    # draw a simple cross and a circle so crops are visually identifiable
    draw.line((0, 0, w, h), fill=(255, 200, 100, 255), width=6)
    draw.line((0, h, w, 0), fill=(255, 200, 100, 255), width=6)
    r = min(w, h) // 6
    draw.ellipse((w//2 - r, h//2 - r, w//2 + r, h//2 + r), outline=(200, 255, 200, 255), width=8)
    # optional text (skip if font unavailable)
    try:
        fnt = ImageFont.load_default()
        draw.text((10, 10), "Sample World Map", font=fnt, fill=(220, 220, 255, 255))
    except Exception:
        pass
    return img


def image_to_base64(img: Image.Image) -> str:
    buf = BytesIO()
    img.save(buf, format='PNG')
    return base64.b64encode(buf.getvalue()).decode('utf-8')


def main():
    print("Ensuring DB tables...")
    Base.metadata.create_all(engine)

    session = SessionLocal()
    try:
        # Create sample image
        img = make_sample_image((512, 512))
        img_b64 = image_to_base64(img)

        # Insert a sample world
        world = World(
            name="Seeded Sample World",
            description="A small seeded world for development/testing.",
            world_image=img_b64,
            world_map=img_b64,
            image_prompt="seed script generated image",
        )
        session.add(world)
        session.commit()
        session.refresh(world)

        print(f"Inserted world id={world.id} name={world.name}")
        print("You can now call POST /api/generate/region/crop/ with world_id set to this ID.")
    except Exception as e:
        print("Failed to insert sample world:", e)
        session.rollback()
    finally:
        session.close()


if __name__ == '__main__':
    main()
