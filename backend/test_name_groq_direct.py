import asyncio
from routers.llm import LLMProvider
from dnd_narrative_prompts import DnDNarrativePromptBuilder, NarrativeAspect, NarrativeStyle

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

async def run():
    try:
        res = await LLMProvider.generate_groq(prompt, model="llama-3.3-70b-versatile", max_tokens=400, temperature=0.7)
        print('GROQ RESPONSE:\n', res[:2000])
    except Exception as e:
        print('GROQ call failed:', e)

asyncio.run(run())
