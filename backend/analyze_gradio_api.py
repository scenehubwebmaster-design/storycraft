"""
Analyze Gradio API endpoints to find image generation
"""
import requests

url = "http://192.168.250.14:7861/info?serialize=false"
response = requests.get(url)
data = response.json()

endpoints = data['unnamed_endpoints']
print(f"Total endpoints: {len(endpoints)}\n")

print("=" * 80)
print("ENDPOINTS THAT RETURN IMAGES:")
print("=" * 80)

for endpoint_id, endpoint_info in endpoints.items():
    if 'returns' not in endpoint_info or len(endpoint_info['returns']) == 0:
        continue
    
    # Check if any return value is an image or gallery
    for return_item in endpoint_info['returns']:
        component = return_item.get('component', '')
        if component in ['Image', 'Gallery']:
            print(f"\n📸 Endpoint {endpoint_id}:")
            print(f"   Component: {component}")
            print(f"   Label: {return_item.get('label', 'N/A')}")
            
            # Print parameters
            if endpoint_info.get('parameters'):
                print(f"   Parameters ({len(endpoint_info['parameters'])}):")
                for i, param in enumerate(endpoint_info['parameters'][:5]):  # Show first 5
                    print(f"      {i}. {param.get('label', 'N/A')} ({param.get('component', 'N/A')})")
                if len(endpoint_info['parameters']) > 5:
                    print(f"      ... and {len(endpoint_info['parameters']) - 5} more")
            
            # Print all returns
            print(f"   Returns ({len(endpoint_info['returns'])}):")
            for i, ret in enumerate(endpoint_info['returns'][:3]):  # Show first 3
                print(f"      {i}. {ret.get('label', 'N/A')} ({ret.get('component', 'N/A')})")
            if len(endpoint_info['returns']) > 3:
                print(f"      ... and {len(endpoint_info['returns']) - 3} more")
            break

print("\n" + "=" * 80)
print("ENDPOINTS WITH 'GENERATE' OR 'OUTPUT' IN LABELS:")
print("=" * 80)

for endpoint_id, endpoint_info in endpoints.items():
    # Check parameters for generation-related terms
    if endpoint_info.get('parameters'):
        for param in endpoint_info['parameters']:
            label = param.get('label', '').lower()
            if 'generate' in label or 'output' in label:
                print(f"\n🔍 Endpoint {endpoint_id}:")
                print(f"   Found param: {param.get('label')}")
                break
