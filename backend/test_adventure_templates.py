"""
Test the adventure templates API endpoint.
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_get_templates():
    """Test fetching adventure templates."""
    print("Testing /api/adventures/templates endpoint...")
    print()
    
    # Test without filters
    print("1. Fetching all templates...")
    response = requests.get(f"{BASE_URL}/api/adventures/templates")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Success! Found {data['total']} total templates")
        print(f"   By type: {json.dumps(data['by_type'], indent=2)}")
        print()
        
        # Show a few examples
        if data['templates']:
            print("Sample templates:")
            for template in data['templates'][:5]:
                print(f"   - {template['title']} ({template['source']})")
                print(f"     Levels: {template['level_range']}, Type: {template['campaign_type']}")
                print(f"     Themes: {', '.join(template['themes'][:3])}")
                print()
    else:
        print(f"✗ Error: {response.status_code}")
        print(f"   {response.text}")
    
    # Test filtered by campaign type
    print("\n2. Fetching one-shot adventures...")
    response = requests.get(f"{BASE_URL}/api/adventures/templates?campaign_type=one_shot")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Found {data['total']} one-shot templates")
        for template in data['templates'][:3]:
            print(f"   - {template['title']}")
    else:
        print(f"✗ Error: {response.status_code}")
    
    # Test filtered by source
    print("\n3. Fetching homebrew adventures...")
    response = requests.get(f"{BASE_URL}/api/adventures/templates?source=homebrew")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Found {data['total']} homebrew templates")
        for template in data['templates'][:3]:
            print(f"   - {template['title']}")
    else:
        print(f"✗ Error: {response.status_code}")
    
    print("\n" + "="*70)
    print("Test complete!")


if __name__ == "__main__":
    test_get_templates()
