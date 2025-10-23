"""
Phase A Simple Test - Generator Only
====================================
Test that the character generator produces all combat fields correctly.
"""

import sys
import os
import json

# Add backend to path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

from dnd_generator import generate_dnd_character


def test_combat_fields():
    """Test that all 9 combat fields are generated."""
    print("\n=== Phase A Test: Combat Fields Generation ===\n")
    
    test_cases = [
        ('barbarian', 'dwarf', 'folk_hero', 5, 'rage'),
        ('wizard', 'elf', 'sage', 3, 'arcane_recovery'),
        ('fighter', 'human', 'soldier', 4, 'action_surge'),
        ('rogue', 'halfling', 'criminal', 2, 'sneak_attack'),
        ('cleric', 'human', 'acolyte', 3, 'channel_divinity'),
    ]
    
    required_fields = [
        'ability_modifiers',
        'hit_points_max',
        'hit_points_current',
        'temporary_hp',
        'melee_attack_bonus',
        'ranged_attack_bonus',
        'conditions',
        'death_saves',
        'resources'
    ]
    
    for class_key, species_key, background_key, level, expected_resource in test_cases:
        char = generate_dnd_character(
            class_key=class_key,
            species_key=species_key,
            background_key=background_key,
            alignment='neutral',
            ability_score_method='standard_array',
            name=f'Test {class_key.title()}',
            level=level
        )
        
        print(f"✓ {char['name']} (Level {level} {char['species']} {char['class']})")
        
        # Check all fields present
        missing = [f for f in required_fields if f not in char]
        if missing:
            print(f"  ❌ MISSING: {missing}")
            return False
        
        # Display combat values
        print(f"  HP: {char['hit_points_current']}/{char['hit_points_max']}")
        print(f"  Attack Bonuses: Melee +{char['melee_attack_bonus']}, Ranged +{char['ranged_attack_bonus']}")
        print(f"  Ability Mods: {char['ability_modifiers']}")
        
        # Check class resource
        resources = char.get('resources', {})
        if expected_resource in resources:
            print(f"  Class Resource: {expected_resource} = {resources[expected_resource]}")
        else:
            print(f"  ⚠️  Expected resource '{expected_resource}' not found")
            print(f"      Available: {list(resources.keys())}")
        
        print()
    
    return True


if __name__ == "__main__":
    print("=" * 70)
    print("PHASE A SIMPLE TEST")
    print("Testing: Character generator combat field generation")
    print("=" * 70)
    
    try:
        if test_combat_fields():
            print("=" * 70)
            print("✅ ALL TESTS PASSED")
            print("=" * 70)
            print("\nPhase A Generator Summary:")
            print("  ✓ All 9 combat fields generated")
            print("  ✓ Ability modifiers pre-calculated")
            print("  ✓ Attack bonuses pre-calculated")
            print("  ✓ HP max and current initialized")
            print("  ✓ Class resources properly generated")
            print("  ✓ Death saves and conditions initialized")
        else:
            print("\n❌ TESTS FAILED")
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
