"""
Test script for D&D MCP Integration

This script tests the full stack:
1. MCP proxy server (Node.js)
2. Python MCP client
3. Data retrieval and parsing

Run this after starting the MCP proxy server with:
    node scripts/mcp_proxy_server.js
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from services.dnd_mcp_client import DndMcpClient


async def test_mcp_integration():
    """Test D&D MCP integration"""
    
    print("=" * 60)
    print("D&D MCP Integration Test")
    print("=" * 60)
    
    async with DndMcpClient() as client:
        # Test 1: Health check
        print("\n📋 Test 1: Health Check")
        print("-" * 60)
        try:
            health = await client.health_check()
            print(f"✅ MCP Proxy Status: {health.get('status')}")
            if health.get('error'):
                print(f"⚠️  Error: {health.get('error')}")
        except Exception as e:
            print(f"❌ Health check failed: {e}")
            return
        
        # Test 2: Search for Fireball
        print("\n📋 Test 2: Search for 'Fireball'")
        print("-" * 60)
        try:
            results = await client.search_all("fireball")
            print(f"✅ Found {results.get('total_count', 0)} total results")
            
            if 'spells' in results:
                print(f"   Spells: {len(results['spells'])}")
                for spell in results['spells'][:3]:
                    print(f"     - {spell.get('name')} (score: {spell.get('score')})")
            
            if 'magic-items' in results:
                print(f"   Magic Items: {len(results['magic-items'])}")
                for item in results['magic-items'][:3]:
                    print(f"     - {item.get('name')} (score: {item.get('score')})")
                    
        except Exception as e:
            print(f"❌ Search failed: {e}")
        
        # Test 3: Get specific spell
        print("\n📋 Test 3: Get Spell Details - 'Fireball'")
        print("-" * 60)
        try:
            spell = await client.get_spell("fireball")
            if spell:
                print(f"✅ Spell: {spell.get('name')}")
                print(f"   Level: {spell.get('level')}")
                print(f"   School: {spell.get('school')}")
                print(f"   Range: {spell.get('range')}")
                print(f"   Duration: {spell.get('duration')}")
            else:
                print("⚠️  Spell not found")
        except Exception as e:
            print(f"❌ Get spell failed: {e}")
        
        # Test 4: Filter spells by level
        print("\n📋 Test 4: Filter Cantrips (Level 0)")
        print("-" * 60)
        try:
            cantrips = await client.filter_spells_by_level(0, 0)
            print(f"✅ Found {len(cantrips)} cantrips")
            for cantrip in cantrips[:5]:
                print(f"   - {cantrip.get('name')}")
        except Exception as e:
            print(f"❌ Filter spells failed: {e}")
        
        # Test 5: Find monsters by CR
        print("\n📋 Test 5: Find Monsters (CR 0-2)")
        print("-" * 60)
        try:
            monsters = await client.find_monsters_by_cr(0, 2)
            print(f"✅ Found {len(monsters)} monsters")
            for monster in monsters[:5]:
                print(f"   - {monster.get('name')} (CR: {monster.get('challenge_rating', 'N/A')})")
        except Exception as e:
            print(f"❌ Find monsters failed: {e}")
        
        # Test 6: Get monster details
        print("\n📋 Test 6: Get Monster Details - 'Goblin'")
        print("-" * 60)
        try:
            monster = await client.get_monster("goblin")
            if monster:
                print(f"✅ Monster: {monster.get('name')}")
                print(f"   Type: {monster.get('type')}")
                print(f"   Size: {monster.get('size')}")
                print(f"   AC: {monster.get('armor_class')}")
                print(f"   HP: {monster.get('hit_points')}")
                print(f"   CR: {monster.get('challenge_rating')}")
            else:
                print("⚠️  Monster not found")
        except Exception as e:
            print(f"❌ Get monster failed: {e}")
        
        # Test 7: Search equipment by cost
        print("\n📋 Test 7: Search Equipment (Max 10 GP)")
        print("-" * 60)
        try:
            equipment = await client.search_equipment_by_cost(10, 'gp')
            print(f"✅ Found {len(equipment)} items")
            for item in equipment[:5]:
                cost = item.get('cost', {})
                print(f"   - {item.get('name')} ({cost.get('quantity', 0)} {cost.get('unit', 'gp')})")
        except Exception as e:
            print(f"❌ Search equipment failed: {e}")
        
        # Test 8: Cache performance
        print("\n📋 Test 8: Cache Performance Test")
        print("-" * 60)
        try:
            import time
            
            # First call (no cache)
            start = time.time()
            await client.search_all("magic missile")
            first_time = time.time() - start
            
            # Second call (cached)
            start = time.time()
            await client.search_all("magic missile")
            cached_time = time.time() - start
            
            print(f"✅ First call: {first_time:.3f}s")
            print(f"✅ Cached call: {cached_time:.3f}s")
            print(f"✅ Speedup: {first_time/cached_time:.1f}x faster")
        except Exception as e:
            print(f"❌ Cache test failed: {e}")
    
    print("\n" + "=" * 60)
    print("✨ All tests completed!")
    print("=" * 60)


if __name__ == "__main__":
    print("\n⚠️  Make sure MCP proxy server is running:")
    print("    cd scripts && node mcp_proxy_server.js\n")
    
    try:
        asyncio.run(test_mcp_integration())
    except KeyboardInterrupt:
        print("\n\n👋 Test interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
