"""
Get all parameter details for endpoint 124
"""
import requests

url = "http://192.168.250.14:7861/info?serialize=false"
response = requests.get(url)
data = response.json()

endpoint = data['unnamed_endpoints']['124']

print("=" * 80)
print("ALL 71 PARAMETERS FOR ENDPOINT 124")
print("=" * 80)

for i, param in enumerate(endpoint['parameters']):
    label = param.get('label', 'N/A')
    component = param.get('component', 'N/A')
    python_type = param.get('python_type', {})
    type_desc = python_type.get('type', 'N/A')
    
    # Get default or example value
    default_val = "?"
    if 'example_input' in param and param['example_input']:
        default_val = param['example_input']
    elif component == 'Checkbox':
        default_val = False
    elif component == 'Slider':
        type_info = param.get('type', {})
        if 'description' in type_info:
            default_val = type_info['description']
    elif component == 'Dropdown':
        type_info = param.get('type', {})
        if 'description' in type_info and 'Option from:' in type_info['description']:
            default_val = "[]  # or first option"
    elif component == 'Textbox':
        default_val = '""'
    
    print(f"{i:2d}. {label:35s} | {component:12s} | {type_desc:20s} | {default_val}")

print("\n" + "=" * 80)
