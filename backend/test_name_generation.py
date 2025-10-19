import requests
import json
from dnd_narrative_prompts import DnDNarrativePromptBuilder, NarrativeAspect, NarrativeStyle

# Build example character data
character_data = {
    "name": "",
    "dnd_class": "wizard",
    "dnd_species": "elf",
    "dnd_background": "sage",
    "dnd_alignment": "Neutral Good",
    "dnd_level": 3,
    "dnd_ability_scores": {
        "strength": 8,
        "dexterity": 14,
        "constitution": 12,
        "intelligence": 18,
        "wisdom": 13,
        "charisma": 10
    }
}

builder = DnDNarrativePromptBuilder(character_data)
prompt = builder.build_prompt(aspect=NarrativeAspect.NAME, style=NarrativeStyle.DETAILED, length="short")

print("--- PROMPT (trimmed) ---")
print(prompt[:1200])
print("--- END PROMPT ---\n")

# Send to local backend generate endpoint
url = "http://localhost:8000/generate"
payload = {
    "provider": "groq",
    "prompt": prompt,
    "model": None,
    "max_tokens": 400,
    "temperature": 0.7
}

try:
    resp = requests.post(url, json=payload, timeout=60)
    print("Status:", resp.status_code)
    print(resp.text[:2000])
    # Try to extract content field as JSON
    try:
        data = resp.json()
        content = data.get('content') or data.get('text') or data.get('message') or ''
        print('\n--- RAW CONTENT ---')
        print(content[:2000])
        # Try parse JSON array from content
        try:
            parsed = json.loads(content)
            print('\n--- Parsed JSON ---')
            print(json.dumps(parsed, indent=2)[:2000])
        except Exception as e:
            print('\nCould not parse JSON from content:', e)
    except Exception as e:
        print('\nResponse not JSON:', e)
except Exception as e:
    print('Request failed:', e)
    
