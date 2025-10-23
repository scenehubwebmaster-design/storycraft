"""update tts_provider to nullable

Revision ID: 0004_update_tts_provider_nullable
Revises: 44c77dbc6730
Create Date: 2025-10-23 14:30:00.000000
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0004_update_tts_provider_nullable'
down_revision = '44c77dbc6730'
branch_labels = None
depends_on = None


def upgrade():
    """
    Update user_settings table to:
    1. Make tts_provider nullable (no hardcoded default)
    2. Change default voice from 'tara' to 'alloy' (OpenAI default)
    """
    # Check if user_settings table exists
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    
    if 'user_settings' in inspector.get_table_names():
        # Alter tts_provider to be nullable
        with op.batch_alter_table('user_settings', schema=None) as batch_op:
            batch_op.alter_column('tts_provider',
                                  existing_type=sa.String(length=50),
                                  nullable=True,
                                  server_default=None)
            
            # Update default voice to 'alloy' (OpenAI default)
            batch_op.alter_column('tts_voice',
                                  existing_type=sa.String(length=50),
                                  server_default='alloy')
        
        print("[Migration] Updated user_settings: tts_provider is now nullable, default voice changed to 'alloy'")
    else:
        # Table doesn't exist yet, create it
        op.create_table(
            'user_settings',
            sa.Column('id', sa.Integer(), primary_key=True),
            sa.Column('user_id', sa.Integer(), nullable=True, index=True),
            
            # TTS Settings (no hardcoded defaults)
            sa.Column('tts_provider', sa.String(50), nullable=True),
            sa.Column('tts_voice', sa.String(50), server_default='alloy'),
            sa.Column('tts_enabled', sa.Boolean(), server_default='1'),
            sa.Column('tts_auto_play', sa.Boolean(), server_default='0'),
            sa.Column('tts_speed', sa.Float(), server_default='1.0'),
            sa.Column('tts_model', sa.String(50), server_default='standard'),
            
            # UI Preferences
            sa.Column('theme', sa.String(20), server_default='dark'),
            sa.Column('compact_mode', sa.Boolean(), server_default='0'),
            sa.Column('show_dice_rolls', sa.Boolean(), server_default='1'),
            
            # RAG Settings
            sa.Column('rag_enabled', sa.Boolean(), server_default='1'),
            sa.Column('rag_top_k', sa.Integer(), server_default='5'),
            
            # LLM Settings
            sa.Column('preferred_provider', sa.String(50), server_default='groq'),
            sa.Column('preferred_model', sa.String(100), nullable=True),
            sa.Column('temperature', sa.Float(), server_default='0.7'),
            sa.Column('max_tokens', sa.Integer(), server_default='2000'),
        )
        
        op.create_index('ix_user_settings_user_id', 'user_settings', ['user_id'])
        
        print("[Migration] Created user_settings table with nullable tts_provider")


def downgrade():
    """
    Revert changes:
    1. Make tts_provider non-nullable with 'kitten' default
    2. Change default voice back to 'tara'
    """
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    
    if 'user_settings' in inspector.get_table_names():
        with op.batch_alter_table('user_settings', schema=None) as batch_op:
            # Restore old defaults
            batch_op.alter_column('tts_provider',
                                  existing_type=sa.String(length=50),
                                  nullable=False,
                                  server_default='kitten')
            
            batch_op.alter_column('tts_voice',
                                  existing_type=sa.String(length=50),
                                  server_default='tara')
        
        print("[Migration] Reverted user_settings: tts_provider has 'kitten' default, voice is 'tara'")
