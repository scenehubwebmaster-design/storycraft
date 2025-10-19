from backend.dnd_narrative_prompts import build_dnd_narrative_prompt

kaelin = {
    "name": "Kaelin Valtor",
    "dnd_class": "Barbarian",
    "dnd_species": "Goliath",
    "dnd_background": "outlander",
    "dnd_alignment": "Neutral Good",
    "dnd_level": 1,
    "character_appearance": "Kaelin stands with a relaxed, athletic posture, worn leather armor, and a silver hammer earring.",
}

p = build_dnd_narrative_prompt(kaelin, style='detailed')
print('\n'.join(p.splitlines()[:200]))
