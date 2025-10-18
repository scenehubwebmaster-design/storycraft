"""
Test actual image generation with endpoint 124
"""
import requests
import json
import base64

# Endpoint 124 parameters based on analysis:
# 0. parameter_47 (Label) - Unknown, might be empty
# 1. Prompt (Textbox)
# 2. Negative prompt (Textbox)
# 3. Styles (Dropdown)
# 4. Batch count (Slider)
# 5. Batch size (Slider)
# 6. CFG Scale (Slider)
# 7. Height (Slider)
# 8. Width (Slider)
# ... and many more

print("🧪 Testing Stable Diffusion endpoint 124...")

# Build minimal data array (fill positions we don't know with None/defaults)
data = []
data.append("")  # 0. parameter_47 (Label)
data.append("a portrait of a beautiful elf warrior")  # 1. Prompt
data.append("low quality, blurry")  # 2. Negative prompt
data.append([])  # 3. Styles (empty list)
data.append(1)  # 4. Batch count
data.append(1)  # 5. Batch size
data.append(7.0)  # 6. CFG Scale
data.append(512)  # 7. Height
data.append(512)  # 8. Width

# Fill rest with None for now
# Based on the analysis, we need 71 total parameters
while len(data) < 71:
    data.append(None)

payload = {
    "fn_index": 124,
    "data": data
}

print(f"Sending request with {len(data)} parameters...")
print(f"Prompt: {data[1]}")
print(f"Size: {data[8]}x{data[7]}")

try:
    response = requests.post(
        "http://192.168.250.14:7861/api/predict",
        json=payload,
        timeout=120
    )
    
    print(f"\n✅ Response status: {response.status_code}")
    result = response.json()
    
    # Print response structure
    print(f"\nResponse keys: {list(result.keys())}")
    
    if "data" in result:
        print(f"Data array length: {len(result['data'])}")
        print(f"\nFirst return (Gallery/Output):")
        if result['data'] and len(result['data']) > 0:
            output_data = result['data'][0]
            print(f"  Type: {type(output_data)}")
            
            if isinstance(output_data, list):
                print(f"  Length: {len(output_data)}")
                if len(output_data) > 0:
                    first_image = output_data[0]
                    print(f"  First image type: {type(first_image)}")
                    
                    if isinstance(first_image, dict):
                        print(f"  Keys: {list(first_image.keys())}")
                        
                        # Try to extract and save image
                        if 'name' in first_image:
                            print(f"  Image name: {first_image['name']}")
                        
                        # Check for base64 data
                        if 'data' in first_image:
                            img_data = first_image['data']
                            # Check if it's a data URI
                            if img_data.startswith('data:'):
                                # Extract base64 part
                                base64_data = img_data.split(',', 1)[1] if ',' in img_data else img_data
                            else:
                                base64_data = img_data
                            
                            try:
                                # Decode and save
                                img_bytes = base64.b64decode(base64_data)
                                with open('test_generated.png', 'wb') as f:
                                    f.write(img_bytes)
                                print(f"\n🎨 ✅ Image saved to test_generated.png ({len(img_bytes)} bytes)")
                            except Exception as e:
                                print(f"\n❌ Failed to decode image: {e}")
                                print(f"   Data preview: {img_data[:100]}...")
                        
                        # Check for URL/path
                        if 'url' in first_image:
                            print(f"  Image URL: {first_image['url']}")
                    elif isinstance(first_image, str):
                        print(f"  String value: {first_image[:100]}...")
        
        print(f"\nSecond return (Generation info): {result['data'][1][:200] if len(result['data']) > 1 and result['data'][1] else 'N/A'}...")
    
    print(f"\nFull response:")
    print(json.dumps(result, indent=2)[:1000])
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
