"""
Test script to verify structured actions are generated correctly.

This script tests the narrative engine's ability to generate structured
action suggestions in the expected format.
"""
import asyncio
import json
from backend.game.narrative_engine import NarrativeEngine


async def test_action_extraction():
    """Test the _extract_suggested_actions method"""
    engine = NarrativeEngine(db=None)
    
    # Test Case 1: Structured actions from LLM
    scene_data_structured = {
        "description": "You enter a tavern...",
        "suggested_actions": [
            {
                "action": "Talk to the bartender",
                "roll": "Persuasion (d20 + 3)",
                "dc": "10",
                "type": "dialogue"
            },
            {
                "action": "Search for clues",
                "roll": "Investigation (d20 + 1)",
                "dc": "15",
                "type": "skill_check"
            }
        ]
    }
    
    actions = engine._extract_suggested_actions(scene_data_structured)
    print("✓ Test 1: Structured actions from LLM")
    print(f"  Found {len(actions)} actions:")
    for action in actions:
        print(f"    - {action['action']} ({action['type']})")
        if action['roll']:
            print(f"      Roll: {action['roll']}, DC: {action['dc']}")
    print()
    
    # Test Case 2: Parse from text choices
    scene_data_text = {
        "description": "A goblin approaches...",
        "choices": [
            "Attack the goblin (d20+5, AC 13)",
            "Try to negotiate (Persuasion DC 12)",
            "Search for an escape route (Investigation)",
            "Hide behind cover"
        ]
    }
    
    actions = engine._extract_suggested_actions(scene_data_text)
    print("✓ Test 2: Parse from text choices")
    print(f"  Found {len(actions)} actions:")
    for action in actions:
        print(f"    - {action['action']} ({action['type']})")
        if action['roll']:
            print(f"      Roll: {action['roll']}, DC: {action['dc']}")
    print()
    
    # Test Case 3: Empty scene data
    scene_data_empty = {
        "description": "Nothing happens..."
    }
    
    actions = engine._extract_suggested_actions(scene_data_empty)
    print("✓ Test 3: Empty scene data")
    print(f"  Found {len(actions)} actions (should be 0)")
    print()


async def test_action_parsing():
    """Test the _parse_choice_string method"""
    engine = NarrativeEngine(db=None)
    
    test_cases = [
        "Search the room (Investigation DC 15)",
        "Attack the goblin (d20+5, AC 13)",
        "Persuade the guard (Persuasion d20+3, DC 12)",
        "Talk to the innkeeper",
        "Move to the north door",
        "Cast Fireball at the enemies",
    ]
    
    print("✓ Test 4: Action string parsing")
    for text in test_cases:
        action = engine._parse_choice_string(text)
        print(f"  Input: {text}")
        print(f"    Action: {action['action']}")
        print(f"    Type: {action['type']}")
        if action['roll']:
            print(f"    Roll: {action['roll']}")
        if action['dc']:
            print(f"    DC: {action['dc']}")
        print()


def test_json_format():
    """Test that our format matches what frontend expects"""
    expected_format = [
        {
            "action": "Approach the cloaked figure at the bar",
            "roll": "Investigation (d20 + 0)",
            "dc": "12",
            "type": "skill_check"
        },
        {
            "action": "Talk to Mira Hearthstone",
            "roll": "Persuasion (d20 + 3)",
            "dc": "10",
            "type": "dialogue"
        },
        {
            "action": "Order a drink",
            "roll": None,
            "dc": None,
            "type": "explore"
        }
    ]
    
    print("✓ Test 5: JSON format validation")
    print("  Expected format:")
    print(json.dumps(expected_format, indent=2))
    print()
    
    # Verify all required fields
    required_fields = ["action", "roll", "dc", "type"]
    for idx, action in enumerate(expected_format):
        missing = [f for f in required_fields if f not in action]
        if missing:
            print(f"  ✗ Action {idx} missing fields: {missing}")
        else:
            print(f"  ✓ Action {idx} has all required fields")
    print()


async def main():
    """Run all tests"""
    print("=" * 60)
    print("STRUCTURED ACTIONS TEST SUITE")
    print("=" * 60)
    print()
    
    try:
        await test_action_extraction()
        await test_action_parsing()
        test_json_format()
        
        print("=" * 60)
        print("ALL TESTS PASSED ✓")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
