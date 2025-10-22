
"""autogenerate_chat_tables_migration

Revision ID: 5ae375edd031
Revises: 0003_create_chat_tables
Create Date: 2025-10-22 00:14:36.162380
"""

from alembic import op
import sqlalchemy as sa

# sqlite dialect import not needed in this migration

# revision identifiers, used by Alembic.
revision = '5ae375edd031'
down_revision = '0003_create_chat_tables'
branch_labels = None
depends_on = None


def upgrade():
    # This migration was auto-generated but included destructive operations.
    # Replace with a safe, idempotent creation of chat tables only so this
    # migration can be applied on dev DBs without dropping unrelated tables.
    conn = op.get_bind()
    dialect = conn.dialect.name

    if dialect == 'sqlite':
        # create chat_sessions if missing
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

        # create chat_messages if missing
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
        # For other DBs, attempt to create the tables (wrapped in try/except to be idempotent)
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
    # Downgrade not implemented for this safe chat-tables-only migration
    raise NotImplementedError('Downgrade not supported for this migration')
