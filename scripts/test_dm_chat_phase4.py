#!/usr/bin/env python3
"""
Test script for Phase 4: DM Chat Handler Enhancement with D&D MCP Integration

Tests the new D&D content commands and intelligent spell/monster detection:
- /spell <name> command
- /monster <name> command  
- /item <name> command
- Auto-detection of spell casts
- Auto-detection of monster mentions

Usage:
    python scripts/test_dm_chat_phase4.py
"""

import asyncio
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from game.dm_chat_handler import DMChatHandler
from database import SessionLocal
from models import GameSession


def print_section(title: str):
    """Print formatted section header."""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


def print_response(response):
    """Print DM response formatted."""
    print(f"DM: {response.message}\n")
    if response.events:
        print(f"Events: {len(response.events)}")
        for event in response.events:
            print(f"  - {event.get('type', 'unknown')}")
    print(f"State changed: {response.game_state_changed}")
    print(f"Scene changed: {response.scene_changed}")
    print(f"Combat: started={response.combat_started}, ended={response.combat_ended}")


async def test_spell_command():
    """Test /spell command."""
    print_section("TEST 1: /spell Command")
    
    db = SessionLocal()
    handler = DMChatHandler(db)
    
    # Create test game session
    game_session = GameSession(
        session_name="Phase 4 Test Session",
        game_state={"party_status": {}}
    )
    db.add(game_session)
    db.commit()
    
    try:
        # Test Fireball
        print("Player: /spell Fireball")
        response = await handler.process_game_message(
            game_session=game_session,
            user_message="/spell Fireball"
        )
        print_response(response)
        
        # Test unknown spell
        print("\n--- Unknown Spell ---")
        print("Player: /spell Super Mega Blast")
        response = await handler.process_game_message(
            game_session=game_session,
            user_message="/spell Super Mega Blast"
        )
        print_response(response)
        
    finally:
        db.close()


async def test_monster_command():
    """Test /monster command."""
    print_section("TEST 2: /monster Command")
    
    db = SessionLocal()
    handler = DMChatHandler(db)
    
    # Create test game session
    game_session = GameSession(
        session_name="Phase 4 Test Session",
        game_state={"party_status": {}}
    )
    db.add(game_session)
    db.commit()
    
    try:
        # Test Goblin
        print("Player: /monster Goblin")
        response = await handler.process_game_message(
            game_session=game_session,
            user_message="/monster Goblin"
        )
        print_response(response)
        
        # Test Dragon
        print("\n--- Ancient Red Dragon ---")
        print("Player: /monster Ancient Red Dragon")
        response = await handler.process_game_message(
            game_session=game_session,
            user_message="/monster Ancient Red Dragon"
        )
        print_response(response)
        
    finally:
        db.close()


async def test_item_command():
    """Test /item command."""
    print_section("TEST 3: /item Command")
    
    db = SessionLocal()
    handler = DMChatHandler(db)
    
    # Create test game session
    game_session = GameSession(
        session_name="Phase 4 Test Session",
        game_state={"party_status": {}}
    )
    db.add(game_session)
    db.commit()
    
    try:
        print("Player: /item Bag of Holding")
        response = await handler.process_game_message(
            game_session=game_session,
            user_message="/item Bag of Holding"
        )
        print_response(response)
        
    finally:
        db.close()


async def test_spell_detection():
    """Test automatic spell casting detection."""
    print_section("TEST 4: Automatic Spell Detection")
    
    db = SessionLocal()
    handler = DMChatHandler(db)
    
    # Create test game session
    game_session = GameSession(
        session_name="Phase 4 Test Session",
        game_state={"party_status": {}}
    )
    db.add(game_session)
    db.commit()
    
    try:
        # Test spell cast detection
        print("Player: I cast Fireball at the goblins!")
        print("(Should auto-detect and look up Fireball)\n")
        
        response = await handler.process_game_message(
            game_session=game_session,
            user_message="I cast Fireball at the goblins!"
        )
        print_response(response)
        
        # Test another pattern
        print("\n--- Another Pattern ---")
        print("Player: I use Cure Wounds on the fighter")
        
        response = await handler.process_game_message(
            game_session=game_session,
            user_message="I use Cure Wounds on the fighter"
        )
        print_response(response)
        
    finally:
        db.close()


async def test_monster_detection():
    """Test automatic monster mention detection."""
    print_section("TEST 5: Automatic Monster Detection")
    
    db = SessionLocal()
    handler = DMChatHandler(db)
    
    # Create test game session
    game_session = GameSession(
        session_name="Phase 4 Test Session",
        game_state={"party_status": {}}
    )
    db.add(game_session)
    db.commit()
    
    try:
        # Test monster spawn detection
        print("Player: Suddenly, a goblin appears from the shadows!")
        print("(Should auto-detect and look up Goblin)\n")
        
        response = await handler.process_game_message(
            game_session=game_session,
            user_message="Suddenly, a goblin appears from the shadows!"
        )
        print_response(response)
        
        # Test another pattern
        print("\n--- Another Pattern ---")
        print("Player: An orc charges toward the party")
        
        response = await handler.process_game_message(
            game_session=game_session,
            user_message="An orc charges toward the party"
        )
        print_response(response)
        
    finally:
        db.close()


async def test_help_command():
    """Test updated help/status commands."""
    print_section("TEST 6: Help & Status Commands")
    
    db = SessionLocal()
    handler = DMChatHandler(db)
    
    # Create test game session
    game_session = GameSession(
        session_name="Phase 4 Test Session",
        game_state={"party_status": {}}
    )
    db.add(game_session)
    db.commit()
    
    try:
        # Test unknown command (should show available commands)
        print("Player: /help")
        response = await handler.process_game_message(
            game_session=game_session,
            user_message="/help"
        )
        print_response(response)
        
        # Test status
        print("\n--- Status Command ---")
        print("Player: /status")
        response = await handler.process_game_message(
            game_session=game_session,
            user_message="/status"
        )
        print_response(response)
        
    finally:
        db.close()


async def main():
    """Run all Phase 4 tests."""
    print("\n" + "="*70)
    print("  PHASE 4 TEST SUITE: DM CHAT HANDLER + D&D MCP INTEGRATION")
    print("="*70)
    print("\nTesting new features:")
    print("  - /spell, /monster, /item commands")
    print("  - Auto-detection of spell casts")
    print("  - Auto-detection of monster mentions")
    print("\nNOTE: MCP proxy server must be running on port 3001")
    print("      Start with: node scripts/mcp_proxy_server.js")
    
    # Run tests
    await test_spell_command()
    await test_monster_command()
    await test_item_command()
    await test_spell_detection()
    await test_monster_detection()
    await test_help_command()
    
    # Summary
    print_section("TEST SUMMARY")
    print("All Phase 4 tests completed. Check results above.")
    print("\n✅ = Success")
    print("❌ = Failed/Error")
    print("\nIf all tests passed, Phase 4 integration is working correctly!")
    print("\nNew commands available:")
    print("  /spell <name>   - Look up D&D spell details")
    print("  /monster <name> - Look up D&D monster stats")
    print("  /item <name>    - Search for magic items")
    print("\nAuto-detection:")
    print("  • 'I cast Fireball' → Auto-looks up Fireball")
    print("  • 'A goblin appears' → Auto-looks up Goblin stats")


if __name__ == "__main__":
    asyncio.run(main())
