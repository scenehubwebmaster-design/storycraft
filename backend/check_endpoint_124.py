"""
Get detailed info about endpoint 124 (txt2img generation)
"""
import requests

url = "http://192.168.250.14:7861/info?serialize=false"
response = requests.get(url)
data = response.json()

endpoint = data['unnamed_endpoints']['124']

print("=" * 80)
print("ENDPOINT 124 - TEXT TO IMAGE GENERATION")
print("=" * 80)

print("\n📝 PARAMETERS:")
for i, param in enumerate(endpoint['parameters'][:25]):
    label = param.get('label', 'N/A')
    component = param.get('component', 'N/A')
    print(f"   {i:2d}. {label:30s} ({component})")

if len(endpoint['parameters']) > 25:
    print(f"   ... and {len(endpoint['parameters']) - 25} more parameters")

print(f"\n   Total parameters: {len(endpoint['parameters'])}")

print("\n📤 RETURNS:")
for i, ret in enumerate(endpoint['returns']):
    label = ret.get('label', 'N/A')
    component = ret.get('component', 'N/A')
    print(f"   {i}. {label:30s} ({component})")

print("\n" + "=" * 80)
