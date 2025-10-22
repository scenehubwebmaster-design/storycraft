
"""add_game_system_tables

Revision ID: 44c77dbc6730
Revises: 5ae375edd031
Create Date: 2025-10-22 11:43:48.838234
"""

from alembic import op
import sqlalchemy as sa



# revision identifiers, used by Alembic.
revision = '44c77dbc6730'
down_revision = '5ae375edd031'
branch_labels = None
depends_on = None


def upgrade():
    # Game sessions table
    op.create_table(
        'game_sessions',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('chat_session_id', sa.Integer(), sa.ForeignKey('chat_sessions.id'), nullable=True),
        sa.Column('campaign_name', sa.String(), nullable=True),
        sa.Column('current_location', sa.String(), nullable=True),
        sa.Column('current_scene', sa.Text(), nullable=True),
        sa.Column('game_state', sa.Text(), nullable=True),  # JSON
        sa.Column('party_level', sa.Integer(), default=1),
        sa.Column('session_notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now())
    )
    op.create_index('ix_game_sessions_chat_session_id', 'game_sessions', ['chat_session_id'])
    
    # Party members table
    op.create_table(
        'party_members',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('game_session_id', sa.Integer(), sa.ForeignKey('game_sessions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('character_id', sa.Integer(), sa.ForeignKey('characters.id'), nullable=False),
        sa.Column('current_hp', sa.Integer(), nullable=True),
        sa.Column('max_hp', sa.Integer(), nullable=True),
        sa.Column('temp_hp', sa.Integer(), default=0),
        sa.Column('conditions', sa.Text(), nullable=True),  # JSON array
        sa.Column('position', sa.String(), nullable=True),  # JSON: {x, y} or room_id
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('joined_at', sa.DateTime(), server_default=sa.func.now())
    )
    op.create_index('ix_party_members_game_session_id', 'party_members', ['game_session_id'])
    op.create_index('ix_party_members_character_id', 'party_members', ['character_id'])
    
    # Combat encounters table
    op.create_table(
        'combat_encounters',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('game_session_id', sa.Integer(), sa.ForeignKey('game_sessions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('difficulty', sa.String(), nullable=True),  # easy, medium, hard, deadly
        sa.Column('is_active', sa.Boolean(), default=False),
        sa.Column('turn_order', sa.Text(), nullable=True),  # JSON array
        sa.Column('current_turn', sa.Integer(), default=0),
        sa.Column('round_number', sa.Integer(), default=1),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('ended_at', sa.DateTime(), nullable=True)
    )
    op.create_index('ix_combat_encounters_game_session_id', 'combat_encounters', ['game_session_id'])
    op.create_index('ix_combat_encounters_is_active', 'combat_encounters', ['is_active'])
    
    # Combat participants table
    op.create_table(
        'combat_participants',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('encounter_id', sa.Integer(), sa.ForeignKey('combat_encounters.id', ondelete='CASCADE'), nullable=False),
        sa.Column('entity_type', sa.String(), nullable=False),  # 'pc' or 'monster'
        sa.Column('entity_id', sa.Integer(), nullable=True),  # character_id or monster instance
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('initiative', sa.Integer(), nullable=False),
        sa.Column('current_hp', sa.Integer(), nullable=False),
        sa.Column('max_hp', sa.Integer(), nullable=False),
        sa.Column('ac', sa.Integer(), nullable=False),
        sa.Column('conditions', sa.Text(), nullable=True),  # JSON array
        sa.Column('position', sa.String(), nullable=True),  # JSON: {x, y}
        sa.Column('is_alive', sa.Boolean(), default=True)
    )
    op.create_index('ix_combat_participants_encounter_id', 'combat_participants', ['encounter_id'])
    
    # Quests table
    op.create_table(
        'quests',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('game_session_id', sa.Integer(), sa.ForeignKey('game_sessions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('quest_giver', sa.String(), nullable=True),
        sa.Column('objectives', sa.Text(), nullable=True),  # JSON array
        sa.Column('status', sa.String(), default='active'),  # active, completed, failed, abandoned
        sa.Column('reward', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('completed_at', sa.DateTime(), nullable=True)
    )
    op.create_index('ix_quests_game_session_id', 'quests', ['game_session_id'])
    op.create_index('ix_quests_status', 'quests', ['status'])
    
    # NPCs table
    op.create_table(
        'npcs',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('game_session_id', sa.Integer(), sa.ForeignKey('game_sessions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('role', sa.String(), nullable=True),  # quest_giver, merchant, ally, enemy, neutral
        sa.Column('location', sa.String(), nullable=True),
        sa.Column('personality', sa.Text(), nullable=True),
        sa.Column('relationship_to_party', sa.Integer(), default=0),  # -100 to 100
        sa.Column('dialogue_history', sa.Text(), nullable=True),  # JSON array
        sa.Column('is_alive', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now())
    )
    op.create_index('ix_npcs_game_session_id', 'npcs', ['game_session_id'])
    
    # Inventory items table
    op.create_table(
        'inventory_items',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('game_session_id', sa.Integer(), sa.ForeignKey('game_sessions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('character_id', sa.Integer(), sa.ForeignKey('characters.id'), nullable=True),  # NULL = party inventory
        sa.Column('item_reference_id', sa.Integer(), sa.ForeignKey('references.id'), nullable=True),  # link to magic_items_md
        sa.Column('item_name', sa.String(), nullable=False),
        sa.Column('quantity', sa.Integer(), default=1),
        sa.Column('is_equipped', sa.Boolean(), default=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('acquired_at', sa.DateTime(), server_default=sa.func.now())
    )
    op.create_index('ix_inventory_items_game_session_id', 'inventory_items', ['game_session_id'])
    op.create_index('ix_inventory_items_character_id', 'inventory_items', ['character_id'])
    
    # Game events table (audit trail + journal)
    op.create_table(
        'game_events',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('game_session_id', sa.Integer(), sa.ForeignKey('game_sessions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('event_type', sa.String(), nullable=False),  # combat, dialogue, skill_check, item_acquired, etc.
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('game_state_snapshot', sa.Text(), nullable=True),  # JSON snapshot
        sa.Column('turn_number', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now())
    )
    op.create_index('ix_game_events_game_session_id', 'game_events', ['game_session_id'])
    op.create_index('ix_game_events_event_type', 'game_events', ['event_type'])
    op.create_index('ix_game_events_created_at', 'game_events', ['created_at'])
    
    # Game locations table (for dungeon crawling)
    op.create_table(
        'game_locations',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('game_session_id', sa.Integer(), sa.ForeignKey('game_sessions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('location_type', sa.String(), nullable=True),  # dungeon, town, wilderness, etc.
        sa.Column('parent_location_id', sa.Integer(), sa.ForeignKey('game_locations.id'), nullable=True),  # for nested locations
        sa.Column('features', sa.Text(), nullable=True),  # JSON: [traps, hazards, treasure, etc.]
        sa.Column('connections', sa.Text(), nullable=True),  # JSON: {north: location_id, south: location_id, etc.}
        sa.Column('is_explored', sa.Boolean(), default=False),
        sa.Column('discovered_at', sa.DateTime(), nullable=True)
    )
    op.create_index('ix_game_locations_game_session_id', 'game_locations', ['game_session_id'])
    op.create_index('ix_game_locations_parent_location_id', 'game_locations', ['parent_location_id'])


def downgrade():
    # Drop tables in reverse order (respecting foreign keys)
    op.drop_index('ix_game_locations_parent_location_id', 'game_locations')
    op.drop_index('ix_game_locations_game_session_id', 'game_locations')
    op.drop_table('game_locations')
    
    op.drop_index('ix_game_events_created_at', 'game_events')
    op.drop_index('ix_game_events_event_type', 'game_events')
    op.drop_index('ix_game_events_game_session_id', 'game_events')
    op.drop_table('game_events')
    
    op.drop_index('ix_inventory_items_character_id', 'inventory_items')
    op.drop_index('ix_inventory_items_game_session_id', 'inventory_items')
    op.drop_table('inventory_items')
    
    op.drop_index('ix_npcs_game_session_id', 'npcs')
    op.drop_table('npcs')
    
    op.drop_index('ix_quests_status', 'quests')
    op.drop_index('ix_quests_game_session_id', 'quests')
    op.drop_table('quests')
    
    op.drop_index('ix_combat_participants_encounter_id', 'combat_participants')
    op.drop_table('combat_participants')
    
    op.drop_index('ix_combat_encounters_is_active', 'combat_encounters')
    op.drop_index('ix_combat_encounters_game_session_id', 'combat_encounters')
    op.drop_table('combat_encounters')
    
    op.drop_index('ix_party_members_character_id', 'party_members')
    op.drop_index('ix_party_members_game_session_id', 'party_members')
    op.drop_table('party_members')
    
    op.drop_index('ix_game_sessions_chat_session_id', 'game_sessions')
    op.drop_table('game_sessions')
