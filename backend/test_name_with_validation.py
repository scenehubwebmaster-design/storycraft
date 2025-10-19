import asyncio
from backend.routers.llm import LLMProvider
from backend.dnd_narrative_prompts import DnDNarrativePromptBuilder, NarrativeAspect, NarrativeStyle
from backend.name_generation_utils import needs_retry_from_text, extract_json_array_from_text, sanitize_name_options

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

async def run_once():
    try:
        res = await LLMProvider.generate_groq(prompt, model="llama-3.3-70b-versatile", max_tokens=400, temperature=0.7)
        print('RAW:', res)
        retry, pairs = needs_retry_from_text(res, threshold=0.65)
        print('Retry needed?', retry, 'Pairs:', pairs)
        if not retry:
            options = extract_json_array_from_text(res)
            names = sanitize_name_options(options)
            print('\nNames:')
            for n in names:
                print('-', n)
        else:
            print('Names too similar; consider adjusting prompt or regenerating')
    except Exception as e:
        print('Error calling LLM:', e)

asyncio.run(run_once())
