"""
Test script for structured output generation endpoints.
Run this to verify that the structured character and world generation works correctly.
"""
import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from schemas import CharacterGenerationRequest, WorldGenerationRequest
from routers.generation import generate_character_structured, generate_world_structured
import json


async def test_character_generation():
    """Test structured character generation"""
    print("\n" + "="*80)
    print("TESTING STRUCTURED CHARACTER GENERATION")
    print("="*80)
    
    # Create a test request
    request = CharacterGenerationRequest(
        themes=["fantasy", "adventure"],
        personality_traits=["brave", "loyal", "sarcastic"],
        physical_traits=["tall", "muscular"],
        archetype="warrior",
        custom_details="A former knight seeking redemption",
        provider="groq",  # Change to your preferred provider
        model="llama-3.3-70b-versatile"
    )
    
    try:
        print(f"\n📝 Request: {request.provider} / {request.model}")
        print(f"   Themes: {request.themes}")
        print(f"   Archetype: {request.archetype}")
        print(f"   Traits: {request.personality_traits}")
        print("\n⏳ Generating character profile...")
        
        character_profile = await generate_character_structured(request)
        
        print("\n✅ SUCCESS! Generated CharacterProfile:")
        print(f"   Name: {character_profile.name}")
        print(f"   Age: {character_profile.age}")
        print(f"   Height: {character_profile.height}")
        print(f"   Build: {character_profile.build}")
        print(f"   Personality Traits: {', '.join(character_profile.personality_traits)}")
        print(f"   Primary Motivation: {character_profile.primary_motivation}")
        print(f"   Greatest Fear: {character_profile.greatest_fear}")
        print(f"   Skills: {', '.join(character_profile.skills)}")
        
        # Check if all required fields are populated
        print("\n🔍 Validation Check:")
        missing_fields = []
        for field_name, field_value in character_profile.model_dump().items():
            if field_value is None or (isinstance(field_value, (list, str)) and not field_value):
                missing_fields.append(field_name)
        
        if missing_fields:
            print(f"   ⚠️  WARNING: {len(missing_fields)} empty fields found: {', '.join(missing_fields)}")
        else:
            print(f"   ✅ All {len(character_profile.model_dump())} fields populated!")
        
        # Export to JSON for inspection
        output_file = "test_character_output.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(character_profile.model_dump(), f, indent=2, ensure_ascii=False)
        print(f"\n💾 Full profile saved to: {output_file}")
        
        return True
    
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_world_generation():
    """Test structured world generation"""
    print("\n" + "="*80)
    print("TESTING STRUCTURED WORLD GENERATION")
    print("="*80)
    
    # Create a test request
    request = WorldGenerationRequest(
        themes=["dark fantasy", "political intrigue"],
        setting=["medieval", "low magic"],
        elements=["kingdoms", "ancient prophecy"],
        custom_details="A dying empire torn by civil war",
        provider="groq",  # Change to your preferred provider
        model="llama-3.3-70b-versatile"
    )
    
    try:
        print(f"\n📝 Request: {request.provider} / {request.model}")
        print(f"   Themes: {request.themes}")
        print(f"   Setting: {request.setting}")
        print(f"   Elements: {request.elements}")
        print("\n⏳ Generating world profile...")
        
        world_profile = await generate_world_structured(request)
        
        print("\n✅ SUCCESS! Generated WorldProfile:")
        print(f"   Name: {world_profile.name}")
        print(f"   World Type: {world_profile.world_type}")
        print(f"   Tagline: {world_profile.tagline}")
        print(f"   Age: {world_profile.age}")
        print(f"   Dominant Species: {world_profile.dominant_species}")
        print(f"   Major Civilizations: {len(world_profile.major_civilizations)}")
        print(f"   Major Regions: {len(world_profile.major_regions)}")
        print(f"   Notable Locations: {len(world_profile.notable_locations)}")
        
        # Check if all required fields are populated
        print("\n🔍 Validation Check:")
        missing_fields = []
        for field_name, field_value in world_profile.model_dump().items():
            if field_value is None or (isinstance(field_value, (list, str)) and not field_value):
                missing_fields.append(field_name)
        
        if missing_fields:
            print(f"   ⚠️  WARNING: {len(missing_fields)} empty fields found: {', '.join(missing_fields)}")
        else:
            print(f"   ✅ All {len(world_profile.model_dump())} fields populated!")
        
        # Export to JSON for inspection
        output_file = "test_world_output.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(world_profile.model_dump(), f, indent=2, ensure_ascii=False)
        print(f"\n💾 Full profile saved to: {output_file}")
        
        return True
    
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests"""
    print("\n" + "🧪 STRUCTURED OUTPUT TESTING SUITE " + "🧪".center(60))
    print("="*80)
    
    # Check API keys
    required_keys = {
        "openai": "OPENAI_API_KEY",
        "anthropic": "ANTHROPIC_API_KEY",
        "google": "GOOGLE_API_KEY",
        "groq": "GROQ_API_KEY"
    }
    
    print("\n🔑 Checking API Keys:")
    available_providers = []
    for provider, key_name in required_keys.items():
        if os.getenv(key_name):
            print(f"   ✅ {provider}: Configured")
            available_providers.append(provider)
        else:
            print(f"   ❌ {provider}: Not configured ({key_name} missing)")
    
    if not available_providers:
        print("\n⚠️  ERROR: No API keys configured. Please set at least one API key.")
        return
    
    print(f"\n✅ Will test with: {', '.join(available_providers)}")
    
    # Run tests
    character_success = await test_character_generation()
    world_success = await test_world_generation()
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"   Character Generation: {'✅ PASSED' if character_success else '❌ FAILED'}")
    print(f"   World Generation:     {'✅ PASSED' if world_success else '❌ FAILED'}")
    
    if character_success and world_success:
        print("\n🎉 All tests passed! Structured output is working correctly.")
    else:
        print("\n⚠️  Some tests failed. Check the error messages above.")


if __name__ == "__main__":
    asyncio.run(main())
