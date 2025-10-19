"""
Alembic migration: add world and location image + metadata columns

Revision ID: 20251018_add_world_location_image_fields
Revises: <previous_revision>
Create Date: 2025-10-18

This migration adds the following columns:
- worlds: world_image (TEXT), world_map (TEXT), image_prompt (TEXT), climate (VARCHAR(100)), population_level (VARCHAR(50)), danger_level (VARCHAR(50))
- locations: location_image (TEXT), image_prompt (TEXT), parent_location_id (INTEGER, FK->locations.id), coordinates (VARCHAR(50)), notable_features (TEXT), inhabitants (TEXT)

Note: If you use Alembic in your project, add this file to your versions folder and run `alembic upgrade head` after configuring alembic.ini to point to your DB.
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20251018_add_world_location_image_fields'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Worlds table additions
    op.add_column('worlds', sa.Column('world_image', sa.Text(), nullable=True))
    op.add_column('worlds', sa.Column('world_map', sa.Text(), nullable=True))
    op.add_column('worlds', sa.Column('image_prompt', sa.Text(), nullable=True))
    op.add_column('worlds', sa.Column('climate', sa.String(length=100), nullable=True))
    op.add_column('worlds', sa.Column('population_level', sa.String(length=50), nullable=True))
    op.add_column('worlds', sa.Column('danger_level', sa.String(length=50), nullable=True))

    # Locations table additions
    op.add_column('locations', sa.Column('location_image', sa.Text(), nullable=True))
    op.add_column('locations', sa.Column('image_prompt', sa.Text(), nullable=True))
    op.add_column('locations', sa.Column('parent_location_id', sa.Integer(), nullable=True))
    op.add_column('locations', sa.Column('coordinates', sa.String(length=50), nullable=True))
    op.add_column('locations', sa.Column('notable_features', sa.Text(), nullable=True))
    op.add_column('locations', sa.Column('inhabitants', sa.Text(), nullable=True))

    # Add foreign key constraint for parent_location_id -> locations.id (self-referential)
    try:
        op.create_foreign_key(
            'fk_locations_parent_location',
            'locations',
            'locations',
            ['parent_location_id'],
            ['id'],
            ondelete='SET NULL'
        )
    except Exception:
        # Some DB backends or older Alembic configs may fail creating FK here; handle gracefully
        pass


def downgrade():
    # Drop foreign key if exists
    try:
        op.drop_constraint('fk_locations_parent_location', 'locations', type_='foreignkey')
    except Exception:
        pass

    # Remove added columns from locations
    op.drop_column('locations', 'inhabitants')
    op.drop_column('locations', 'notable_features')
    op.drop_column('locations', 'coordinates')
    op.drop_column('locations', 'parent_location_id')
    op.drop_column('locations', 'image_prompt')
    op.drop_column('locations', 'location_image')

    # Remove added columns from worlds
    op.drop_column('worlds', 'danger_level')
    op.drop_column('worlds', 'population_level')
    op.drop_column('worlds', 'climate')
    op.drop_column('worlds', 'image_prompt')
    op.drop_column('worlds', 'world_map')
    op.drop_column('worlds', 'world_image')
