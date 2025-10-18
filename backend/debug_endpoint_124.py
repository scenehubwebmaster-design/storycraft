"""Debug endpoint 124 response to see actual structure"""
import requests
import json

BASE_URL = "http://192.168.250.14:7861"

# Build minimal parameter array
data = []
data.append({})  # 0. parameter_47 (Label)
data.append("portrait of a beautiful elf warrior, detailed, fantasy art")  # 1. Prompt
data.append("low quality, blurry, distorted")  # 2. Negative prompt
data.append([])  # 3. Styles
data.append(1)  # 4. Batch count
data.append(1)  # 5. Batch size
data.append(7.0)  # 6. CFG Scale
data.append(512)  # 7. Height
data.append(512)  # 8. Width
data.append(False)  # 9. Hires fix
data.append(0.7)  # 10. Denoising strength
data.append(2.0)  # 11. Upscale by
data.append("")  # 12. Upscaler
data.append(0)  # 13. Hires steps
data.append(0)  # 14-15. Resize
data.append(0)
data.append("")  # 16. Checkpoint
data.append("")  # 17-18. Hires sampling
data.append("")
data.append("")  # 19-20. Hires prompts
data.append("")
data.append([])  # 21. Override settings
data.append("None")  # 22. Script
data.append(20)  # 23. Sampling steps (reduced for speed)
data.append("")  # 24-25. Sampling
data.append("")
data.append(False)  # 26-28. Refiner
data.append("")
data.append(0.5)
data.append(-1)  # 29. Seed

# Fill remaining parameters (30-70)
for i in range(30, 71):
    if i in [30, 35, 43, 44, 45, 49, 50, 62, 63, 64, 65, 66, 67, 68, 70]:
        data.append(False)  # Checkboxes
    elif i in [31, 48, 69]:
        data.append(0 if i == 48 or i == 69 else -1)  # Numbers
    elif i in [32, 33, 34, 41]:
        data.append(0 if i != 41 else 1.0)  # Float values
    elif i in [55, 58, 61]:
        data.append([])  # Lists
    else:
        data.append("")  # Strings

print(f"📊 Sending {len(data)} parameters to endpoint 124")

payload = {
    "fn_index": 124,
    "data": data
}

try:
    response = requests.post(f"{BASE_URL}/api/predict", json=payload, timeout=120)
    
    print(f"✅ Response status: {response.status_code}")
    
    result = response.json()
    
    print(f"\n📦 Response keys: {result.keys()}")
    print(f"📊 Data array length: {len(result['data'])}")
    
    for i, item in enumerate(result['data']):
        print(f"\n--- Return {i} ---")
        print(f"Type: {type(item)}")
        if isinstance(item, list):
            print(f"Length: {len(item)}")
            if len(item) > 0:
                print(f"First item type: {type(item[0])}")
                if isinstance(item[0], dict):
                    print(f"First item keys: {item[0].keys()}")
                    for key, value in item[0].items():
                        if isinstance(value, str):
                            print(f"  {key}: {value[:100] if len(value) > 100 else value}")
                        else:
                            print(f"  {key}: {type(value)}")
        elif isinstance(item, str):
            print(f"Content: {item[:200]}")
        else:
            print(f"Value: {item}")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
