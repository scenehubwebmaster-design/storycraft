"""add soft-delete columns to characters

Revision ID: 0001_add_soft_delete_columns
Revises: 
Create Date: 2025-10-19 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0001_add_soft_delete_columns'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # SQLite has limited ALTER TABLE support; use raw SQL to add columns
    conn = op.get_bind()
    dialect = conn.dialect.name
    if dialect == 'sqlite':
        conn.execute(sa.text("ALTER TABLE characters ADD COLUMN is_deleted BOOLEAN DEFAULT 0 NOT NULL;"))
        conn.execute(sa.text("ALTER TABLE characters ADD COLUMN deleted_at DATETIME NULL;"))
    else:
        op.add_column('characters', sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default=sa.text('0')))
        op.add_column('characters', sa.Column('deleted_at', sa.DateTime(), nullable=True))


def downgrade():
    # Dropping columns in sqlite is non-trivial; raise for safety
    raise NotImplementedError("Downgrade not supported for sqlite in this migration")
