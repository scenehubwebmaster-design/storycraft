"""
Quick diagnostic script to check if characters are properly linked to campaigns.

Run this to verify:
1. Characters exist in database
2. Game sessions (campaigns) exist
3. Characters are linked to campaigns via party_members table

Usage:
    cd backend
    python verify_party_members.py
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import SQLALCHEMY_DATABASE_URL
from models import Character, GameSession, PartyMember

# Create engine and session
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

try:
    # Check all characters
    characters = db.query(Character).all()
    print(f"\n{'='*60}")
    print(f"CHARACTERS IN DATABASE: {len(characters)}")
    print(f"{'='*60}")
    
    for char in characters:
        print(f"\nID: {char.id}")
        print(f"Name: {char.name}")
        print(f"D&D Class: {char.dnd_class or 'Not set'}")
        print(f"Level: {char.dnd_level or 'Not set'}")
        print(f"Species: {char.dnd_species or 'Not set'}")
        print(f"Has D&D stats: {char.is_dnd}")
        if char.dnd_ability_scores:
            print(f"Ability Scores: {char.dnd_ability_scores}")
        print("-" * 40)
    
    # Check all game sessions (campaigns)
    game_sessions = db.query(GameSession).all()
    print(f"\n{'='*60}")
    print(f"GAME SESSIONS (CAMPAIGNS): {len(game_sessions)}")
    print(f"{'='*60}")
    
    for session in game_sessions:
        print(f"\nSession ID: {session.id}")
        print(f"Campaign ID: {session.campaign_id}")
        print(f"Created: {session.created_at}")
        print(f"Party Members Count: {len(session.party_members)}")
        
        if session.party_members:
            print("  Party Members:")
            for pm in session.party_members:
                char = pm.character
                print(f"    - {char.name} ({char.dnd_class} {char.dnd_level})")
                print(f"      Active: {pm.is_active}")
                print(f"      Current HP: {pm.current_hp}/{pm.max_hp}")
        else:
            print("  ⚠️  NO PARTY MEMBERS LINKED!")
        print("-" * 40)
    
    # Check party_members table directly
    party_members = db.query(PartyMember).all()
    print(f"\n{'='*60}")
    print(f"PARTY MEMBER LINKS: {len(party_members)}")
    print(f"{'='*60}")
    
    for pm in party_members:
        char = pm.character
        session = pm.game_session
        print(f"\nCharacter: {char.name if char else 'ORPHANED'}")
        print(f"Session ID: {pm.session_id}")
        print(f"Campaign ID: {session.campaign_id if session else 'ORPHANED'}")
        print(f"Active: {pm.is_active}")
        print(f"HP: {pm.current_hp}/{pm.max_hp}")
        print("-" * 40)
    
    # Summary and recommendations
    print(f"\n{'='*60}")
    print("SUMMARY & RECOMMENDATIONS")
    print(f"{'='*60}\n")
    
    if len(characters) == 0:
        print("❌ NO CHARACTERS FOUND")
        print("   → Create characters in the frontend character creator")
    else:
        print(f"✅ Found {len(characters)} character(s)")
    
    if len(game_sessions) == 0:
        print("❌ NO GAME SESSIONS FOUND")
        print("   → Create a campaign in the frontend")
    else:
        print(f"✅ Found {len(game_sessions)} game session(s)")
    
    if len(party_members) == 0:
        print("❌ NO PARTY MEMBERS LINKED")
        print("   → Characters need to be added to campaigns!")
        print("   → This is likely why the DM doesn't see character stats")
        print("\n   SOLUTION:")
        print("   1. In frontend, open your campaign")
        print("   2. Look for 'Add Party Member' or similar button")
        print("   3. Select characters to add to the party")
        print("   4. Characters should appear in campaign party list")
    else:
        print(f"✅ Found {len(party_members)} party member link(s)")
        
        # Check for inactive members
        inactive = [pm for pm in party_members if not pm.is_active]
        if inactive:
            print(f"⚠️  {len(inactive)} party member(s) marked as INACTIVE")
            print("   → DM will ignore inactive party members")
    
    # Check for characters with missing D&D stats
    chars_without_stats = [c for c in characters if not c.is_dnd or not c.dnd_ability_scores]
    if chars_without_stats:
        print(f"\n⚠️  {len(chars_without_stats)} character(s) missing D&D stats:")
        for char in chars_without_stats:
            print(f"   - {char.name}")
        print("   → These characters won't have useful mechanical information for the DM")
    
    print("\n" + "="*60)

except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    print(traceback.format_exc())

finally:
    db.close()
    print("\n✅ Database connection closed")
