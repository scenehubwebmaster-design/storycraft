#!/usr/bin/env python3
"""
Test script for NarrativeEngine + MCP integration.

Tests the new D&D content lookup methods:
- process_spell_cast()
- spawn_monster()
- enhance_scene_with_dnd_content()

Usage:
    python scripts/test_narrative_mcp.py
"""

import asyncio
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from game.narrative_engine import NarrativeEngine
from database import SessionLocal


def print_section(title: str):
    """Print formatted section header."""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


async def test_spell_cast():
    """Test spell lookup via MCP."""
    print_section("TEST 1: Spell Casting (Fireball)")
    
    db = SessionLocal()
    engine = NarrativeEngine(db)
    
    try:
        result = await engine.process_spell_cast(
            spell_name="Fireball",
            caster_name="Gandalf the Grey",
            target="goblin horde"
        )
        
        if result["success"]:
            print("✅ SUCCESS - Spell found!")
            print(f"\nSpell: {result['spell_name']}")
            print(f"Level: {result['level']}")
            print(f"School: {result['school']}")
            print(f"Damage: {result['damage']}")
            print(f"Save: {result['save_dc']}")
            print(f"\nNarrative:\n{result['narrative']}")
        else:
            print(f"❌ FAILED - {result.get('error', 'Unknown error')}")
            print(f"Narrative: {result.get('narrative', 'N/A')}")
    
    except Exception as e:
        print(f"❌ EXCEPTION - {str(e)}")
    finally:
        db.close()


async def test_monster_spawn():
    """Test monster lookup via MCP."""
    print_section("TEST 2: Monster Spawn (Goblin x3)")
    
    db = SessionLocal()
    engine = NarrativeEngine(db)
    
    try:
        result = await engine.spawn_monster(
            monster_name="Goblin",
            count=3,
            location="the dark cave entrance"
        )
        
        if result["success"]:
            print("✅ SUCCESS - Monster found!")
            print(f"\nMonster: {result['monster_name']}")
            print(f"Count: {result['count']}")
            print(f"CR: {result['cr']}")
            print(f"AC: {result['ac']}")
            print(f"HP: {result['hp']}")
            print(f"Type: {result['size']} {result['type']}")
            print(f"\nCombatants created: {len(result['combatants'])}")
            for combatant in result['combatants']:
                print(f"  - {combatant.name}: HP {combatant.current_hp}/{combatant.max_hp}, AC {combatant.ac}")
            print(f"\nNarrative:\n{result['narrative']}")
        else:
            print(f"❌ FAILED - {result.get('error', 'Unknown error')}")
            print(f"Narrative: {result.get('narrative', 'N/A')}")
    
    except Exception as e:
        print(f"❌ EXCEPTION - {str(e)}")
    finally:
        db.close()


async def test_multiple_spells():
    """Test multiple spell lookups."""
    print_section("TEST 3: Multiple Spells (Cure Wounds, Magic Missile)")
    
    db = SessionLocal()
    engine = NarrativeEngine(db)
    
    spells = [
        ("Cure Wounds", "Cleric"),
        ("Magic Missile", "Wizard")
    ]
    
    try:
        for spell_name, caster in spells:
            print(f"\n--- {spell_name} ---")
            result = await engine.process_spell_cast(
                spell_name=spell_name,
                caster_name=caster
            )
            
            if result["success"]:
                print(f"✅ {result['spell_name']} ({result['level']}, {result['school']})")
                print(f"   Damage: {result['damage']}")
                print(f"   Range: {result.get('range', 'N/A')}")
            else:
                print(f"❌ {spell_name} - {result.get('error', 'Unknown')}")
    
    except Exception as e:
        print(f"❌ EXCEPTION - {str(e)}")
    finally:
        db.close()


async def test_multiple_monsters():
    """Test multiple monster lookups."""
    print_section("TEST 4: Multiple Monsters (Dragon, Orc)")
    
    db = SessionLocal()
    engine = NarrativeEngine(db)
    
    monsters = [
        ("Ancient Red Dragon", 1),
        ("Orc", 5)
    ]
    
    try:
        for monster_name, count in monsters:
            print(f"\n--- {monster_name} x{count} ---")
            result = await engine.spawn_monster(
                monster_name=monster_name,
                count=count
            )
            
            if result["success"]:
                print(f"✅ {result['monster_name']} (CR {result['cr']})")
                print(f"   AC: {result['ac']}, HP: {result['hp']}")
                print(f"   Type: {result['size']} {result['type']}")
                print(f"   Combatants: {len(result['combatants'])}")
            else:
                print(f"❌ {monster_name} - {result.get('error', 'Unknown')}")
    
    except Exception as e:
        print(f"❌ EXCEPTION - {str(e)}")
    finally:
        db.close()


async def test_unknown_content():
    """Test error handling for unknown spells/monsters."""
    print_section("TEST 5: Error Handling (Unknown Content)")
    
    db = SessionLocal()
    engine = NarrativeEngine(db)
    
    try:
        # Test unknown spell
        print("\n--- Unknown Spell: 'Super Mega Blast' ---")
        result = await engine.process_spell_cast(
            spell_name="Super Mega Blast",
            caster_name="Test Wizard"
        )
        
        if not result["success"]:
            print(f"✅ Correctly handled unknown spell")
            print(f"   Error: {result['error']}")
            print(f"   Narrative: {result['narrative']}")
        else:
            print(f"❌ Should have failed for unknown spell")
        
        # Test unknown monster
        print("\n--- Unknown Monster: 'Super Mega Dragon' ---")
        result = await engine.spawn_monster(
            monster_name="Super Mega Dragon"
        )
        
        if not result["success"]:
            print(f"✅ Correctly handled unknown monster")
            print(f"   Error: {result['error']}")
            print(f"   Narrative: {result['narrative']}")
        else:
            print(f"❌ Should have failed for unknown monster")
    
    except Exception as e:
        print(f"❌ EXCEPTION - {str(e)}")
    finally:
        db.close()


async def main():
    """Run all tests."""
    print("\n" + "="*70)
    print("  NARRATIVE ENGINE + MCP INTEGRATION TEST SUITE")
    print("="*70)
    print("\nTesting D&D content lookup methods:")
    print("  - process_spell_cast()")
    print("  - spawn_monster()")
    print("\nNOTE: MCP proxy server must be running on port 3001")
    print("      Start with: node scripts/mcp_proxy_server.js")
    
    # Run tests
    await test_spell_cast()
    await test_monster_spawn()
    await test_multiple_spells()
    await test_multiple_monsters()
    await test_unknown_content()
    
    # Summary
    print_section("TEST SUMMARY")
    print("All tests completed. Check results above.")
    print("\n✅ = Success")
    print("❌ = Failed/Error")
    print("\nIf all tests passed, Phase 3 integration is working correctly!")


if __name__ == "__main__":
    asyncio.run(main())
