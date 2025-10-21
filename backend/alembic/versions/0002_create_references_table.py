"""create references table

Revision ID: 0002_create_references_table
Revises: 0001_add_soft_delete_columns
Create Date: 2025-10-21 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0002_create_references_table'
down_revision = '0001_add_soft_delete_columns'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    dialect = conn.dialect.name
    if dialect == 'sqlite':
        # Create table if not exists. Quote the table name because `references` is a SQL keyword.
        conn.execute(sa.text('''
        CREATE TABLE IF NOT EXISTS "references" (
            id INTEGER PRIMARY KEY,
            ref_type VARCHAR(100) NOT NULL,
            key VARCHAR(255) NOT NULL,
            title VARCHAR(255) NOT NULL,
            content TEXT,
            source_url VARCHAR(1024),
            created_at DATETIME DEFAULT (CURRENT_TIMESTAMP),
            updated_at DATETIME DEFAULT (CURRENT_TIMESTAMP)
        );
        '''))
        # Create simple indexes if sqlite supports them
        try:
            conn.execute(sa.text('CREATE INDEX IF NOT EXISTS ix_references_ref_type ON "references"(ref_type);'))
            conn.execute(sa.text('CREATE INDEX IF NOT EXISTS ix_references_key ON "references"(key);'))
        except Exception:
            pass
    else:
        op.create_table(
            'references',
            sa.Column('id', sa.Integer(), primary_key=True),
            sa.Column('ref_type', sa.String(length=100), nullable=False),
            sa.Column('key', sa.String(length=255), nullable=False),
            sa.Column('title', sa.String(length=255), nullable=False),
            sa.Column('content', sa.Text(), nullable=True),
            sa.Column('source_url', sa.String(length=1024), nullable=True),
            sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=True),
            sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), nullable=True),
        )
        try:
            op.create_index('ix_references_ref_type', 'references', ['ref_type'])
        except Exception:
            pass
        try:
            op.create_index('ix_references_key', 'references', ['key'])
        except Exception:
            pass


def downgrade():
    # safe drop for non-sqlite DBs
    conn = op.get_bind()
    dialect = conn.dialect.name
    if dialect == 'sqlite':
        raise NotImplementedError("Downgrade not supported for sqlite in this migration")
    else:
        try:
            op.drop_index('ix_references_key', table_name='references')
        except Exception:
            pass
        try:
            op.drop_index('ix_references_ref_type', table_name='references')
        except Exception:
            pass
        op.drop_table('references')
