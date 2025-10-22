"""create chat tables

Revision ID: 0003_create_chat_tables
Revises: 0002_create_references_table
Create Date: 2025-10-22 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0003_create_chat_tables'
down_revision = '0002_create_references_table'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    dialect = conn.dialect.name

    # For sqlite we apply idempotent CREATE TABLE IF NOT EXISTS like behavior
    if dialect == 'sqlite':
        # Create chat_sessions if missing
        res = conn.execute(sa.text("SELECT name FROM sqlite_master WHERE type='table' AND name='chat_sessions';")).fetchall()
        if not res:
            conn.execute(sa.text(
                """
                CREATE TABLE chat_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title VARCHAR(255),
                    user_id INTEGER,
                    provider VARCHAR(100),
                    model VARCHAR(255),
                    include_context BOOLEAN DEFAULT 1,
                    top_k INTEGER DEFAULT 5,
                    meta JSON,
                    is_active BOOLEAN DEFAULT 1,
                    created_at DATETIME,
                    updated_at DATETIME
                );
                """
            ))
        # Create chat_messages if missing
        res2 = conn.execute(sa.text("SELECT name FROM sqlite_master WHERE type='table' AND name='chat_messages';")).fetchall()
        if not res2:
            conn.execute(sa.text(
                """
                CREATE TABLE chat_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER NOT NULL,
                    role VARCHAR(32) NOT NULL,
                    content TEXT NOT NULL,
                    message_index INTEGER NOT NULL DEFAULT 0,
                    tokens INTEGER,
                    meta JSON,
                    is_deleted BOOLEAN DEFAULT 0,
                    created_at DATETIME,
                    FOREIGN KEY(session_id) REFERENCES chat_sessions(id)
                );
                """
            ))
    else:
        # Use SQLAlchemy operations for other DBs and wrap in try/except for idempotency
        try:
            op.create_table(
                'chat_sessions',
                sa.Column('id', sa.Integer, primary_key=True),
                sa.Column('title', sa.String(255), nullable=True),
                sa.Column('user_id', sa.Integer, nullable=True),
                sa.Column('provider', sa.String(100), nullable=True),
                sa.Column('model', sa.String(255), nullable=True),
                sa.Column('include_context', sa.Boolean, nullable=False, server_default=sa.text('1')),
                sa.Column('top_k', sa.Integer, nullable=False, server_default=sa.text('5')),
                sa.Column('meta', sa.JSON, nullable=True),
                sa.Column('is_active', sa.Boolean, nullable=False, server_default=sa.text('1')),
                sa.Column('created_at', sa.DateTime(), nullable=True),
                sa.Column('updated_at', sa.DateTime(), nullable=True),
            )
        except Exception:
            pass
        try:
            op.create_table(
                'chat_messages',
                sa.Column('id', sa.Integer, primary_key=True),
                sa.Column('session_id', sa.Integer, sa.ForeignKey('chat_sessions.id'), nullable=False),
                sa.Column('role', sa.String(32), nullable=False),
                sa.Column('content', sa.Text, nullable=False),
                sa.Column('message_index', sa.Integer, nullable=False, server_default=sa.text('0')),
                sa.Column('tokens', sa.Integer, nullable=True),
                sa.Column('meta', sa.JSON, nullable=True),
                sa.Column('is_deleted', sa.Boolean, nullable=False, server_default=sa.text('0')),
                sa.Column('created_at', sa.DateTime(), nullable=True),
            )
        except Exception:
            pass


def downgrade():
    raise NotImplementedError('Downgrade not supported for chat create migration')
