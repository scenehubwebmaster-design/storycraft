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
    # Make the migration idempotent: check whether columns already exist
    conn = op.get_bind()
    dialect = conn.dialect.name
    if dialect == 'sqlite':
        # Inspect table columns
        res = conn.execute(sa.text("PRAGMA table_info('characters');")).fetchall()
        cols = {r[1] for r in res}
        if 'is_deleted' not in cols:
            conn.execute(sa.text("ALTER TABLE characters ADD COLUMN is_deleted BOOLEAN DEFAULT 0 NOT NULL;"))
        if 'deleted_at' not in cols:
            conn.execute(sa.text("ALTER TABLE characters ADD COLUMN deleted_at DATETIME NULL;"))
    else:
        # For other DBs, guard with try/except to avoid failure if column exists
        try:
            op.add_column('characters', sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default=sa.text('0')))
        except Exception:
            pass
        try:
            op.add_column('characters', sa.Column('deleted_at', sa.DateTime(), nullable=True))
        except Exception:
            pass


def downgrade():
    # Dropping columns in sqlite is non-trivial; raise for safety
    raise NotImplementedError("Downgrade not supported for sqlite in this migration")
