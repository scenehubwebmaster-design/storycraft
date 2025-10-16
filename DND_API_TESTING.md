# D&D 5E API Testing Guide

## Quick Start

Start the backend server:

```bash
cd backend
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

Interactive API docs: `http://localhost:8000/docs`

## Test Endpoints

### 1. Get Available Classes

```bash
curl http://localhost:8000/api/characters/dnd/classes
```

**Expected Response:**
```json
{
  "classes": [
    {
      "id": "wizard",
      "name": "Wizard",
      "description": "A scholarly magic-user...",
      "hit_die": 6,
      "primary_ability": ["Intelligence"],
      "saving_throws": ["Intelligence", "Wisdom"],
      "spellcaster": true
    }
    // ... 12 more classes
  ],
  "count": 13
}
```

### 2. Get Available Species

```bash
curl http://localhost:8000/api/characters/dnd/species
```

**Expected Response:**
```json
{
  "species": [
    {
      "id": "elf",
      "name": "Elf",
      "description": "Elves are a magical people of otherworldly grace...",
      "size": "Medium",
      "speed": 30,
      "traits": ["Darkvision", "Elven Lineage", "Fey Ancestry"]
    }
    // ... 11+ more species
  ],
  "count": 12
}
```

### 3. Get Available Backgrounds

```bash
curl http://localhost:8000/api/characters/dnd/backgrounds
```

**Expected Response:**
```json
{
  "backgrounds": [
    {
      "id": "sage",
      "name": "Sage",
      "description": "You spent years learning the lore of the multiverse...",
      "skill_proficiencies": ["Arcana", "History"],
      "feature": "Researcher",
      "feature_description": "When you attempt to learn or recall..."
    }
    // ... 11 more backgrounds
  ],
  "count": 12
}
```

### 4. Get Alignments

```bash
curl http://localhost:8000/api/characters/dnd/alignments
```

**Expected Response:**
```json
{
  "alignments": [
    "Lawful Good", "Neutral Good", "Chaotic Good",
    "Lawful Neutral", "True Neutral", "Chaotic Neutral",
    "Lawful Evil", "Neutral Evil", "Chaotic Evil"
  ],
  "count": 9
}
```

### 5. Generate D&D Character (Standard Array)

```bash
curl -X POST http://localhost:8000/api/characters/dnd/generate \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Eldrin Starweaver",
    "dnd_class": "wizard",
    "dnd_species": "elf",
    "dnd_background": "sage",
    "dnd_alignment": "Neutral Good",
    "dnd_level": 1,
    "ability_score_method": "standard_array"
  }'
```

**Expected Response:**
```json
{
  "id": 1,
  "name": "Eldrin Starweaver",
  "description": "A scholarly magic-user...",
  "is_dnd": true,
  "dnd_class": "wizard",
  "dnd_level": 1,
  "dnd_species": "elf",
  "dnd_background": "sage",
  "dnd_alignment": "Neutral Good",
  "dnd_ability_scores": {
    "strength": 8,
    "dexterity": 14,
    "constitution": 12,
    "intelligence": 15,
    "wisdom": 13,
    "charisma": 10
  },
  "dnd_hit_points": 8,
  "dnd_armor_class": 11,
  "dnd_initiative": "+2",
  "dnd_speed": 30,
  "dnd_proficiency_bonus": "+2",
  "dnd_skills": ["Arcana", "History", "Insight", "Investigation"],
  "dnd_proficiencies": {
    "saves": ["Intelligence", "Wisdom"],
    "armor": ["None"],
    "weapons": ["Dagger", "Dart", "Light crossbow", "Quarterstaff", "Sling"],
    "tools": []
  },
  "dnd_features": {
    "racial": ["Darkvision", "Elven Lineage", "Fey Ancestry", "Keen Senses", "Trance"],
    "class": ["Arcane Recovery", "Ritual Casting", "Spellcasting"],
    "background": {
      "feature": "Researcher",
      "description": "When you attempt to learn or recall..."
    }
  },
  "dnd_equipment": {
    "weapons": [
      {"name": "Quarterstaff", "damage": "1d6 bludgeoning"}
    ],
    "armor": [],
    "gear": ["Component pouch", "Scholar's pack", "Spellbook"],
    "gold": 10
  },
  "dnd_spellcasting": {
    "ability": "Intelligence",
    "spell_save_dc": 12,
    "spell_attack_bonus": 4,
    "cantrips_known": 3,
    "spells_known": 6,
    "spell_slots": {"1st": 2}
  },
  "dnd_languages": ["Common", "Elvish"],
  "created_at": "2025-01-20T12:00:00",
  "updated_at": "2025-01-20T12:00:00"
}
```

### 6. Generate Random Character

```bash
curl -X POST http://localhost:8000/api/characters/dnd/generate \
  -H "Content-Type: application/json" \
  -d '{
    "dnd_class": "fighter",
    "dnd_species": "dwarf",
    "dnd_background": "soldier",
    "dnd_level": 1,
    "ability_score_method": "random"
  }'
```

**Note:** Random method uses 4d6 drop lowest for ability scores, so values will vary.

### 7. Get Character Sheet

```bash
curl http://localhost:8000/api/characters/1/dnd-sheet
```

**Expected Response:**
```json
{
  "character_id": 1,
  "character_data": { /* complete character dict */ },
  "formatted_sheet": "
╔═══════════════════════════════════════════════════════════════════════════════╗
║                        D&D 5E CHARACTER SHEET                                 ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║  Name: Eldrin Starweaver                    Level: 1                          ║
║  Class: Wizard                              Species: Elf                      ║
║  Background: Sage                           Alignment: Neutral Good           ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║  ABILITY SCORES                                                               ║
║  ─────────────────────────────────────────────────────────────────────────── ║
║  STR: 8  (-1)    DEX: 14 (+2)    CON: 12 (+1)                               ║
║  INT: 15 (+2)    WIS: 13 (+1)    CHA: 10 (+0)                               ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║  COMBAT STATS                                                                 ║
║  ─────────────────────────────────────────────────────────────────────────── ║
║  HP: 8           AC: 11          Initiative: +2      Speed: 30 ft            ║
║  Proficiency Bonus: +2           Hit Dice: 1d6                               ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║  PROFICIENCIES & SKILLS                                                       ║
║  ─────────────────────────────────────────────────────────────────────────── ║
║  Saving Throws: Intelligence, Wisdom                                         ║
║  Skills: Arcana, History, Insight, Investigation                             ║
║  Languages: Common, Elvish                                                   ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║  FEATURES & TRAITS                                                            ║
║  ─────────────────────────────────────────────────────────────────────────── ║
║  Racial: Darkvision, Elven Lineage, Fey Ancestry, Keen Senses, Trance       ║
║  Class: Arcane Recovery, Ritual Casting, Spellcasting                        ║
║  Background: Researcher                                                       ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║  SPELLCASTING                                                                 ║
║  ─────────────────────────────────────────────────────────────────────────── ║
║  Spellcasting Ability: Intelligence                                          ║
║  Spell Save DC: 12               Spell Attack: +4                            ║
║  Cantrips Known: 3               Spells in Spellbook: 6                      ║
║  Spell Slots: 1st Level: 2                                                   ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║  EQUIPMENT                                                                    ║
║  ─────────────────────────────────────────────────────────────────────────── ║
║  Weapons: Quarterstaff (1d6 bludgeoning)                                     ║
║  Gear: Component pouch, Scholar's pack, Spellbook                            ║
║  Gold: 10 gp                                                                 ║
╚═══════════════════════════════════════════════════════════════════════════════╝
  ",
  "created_at": "2025-01-20T12:00:00",
  "updated_at": "2025-01-20T12:00:00"
}
```

### 8. Update Character Stats (Level Up)

```bash
curl -X PUT http://localhost:8000/api/characters/1/dnd-stats \
  -H "Content-Type: application/json" \
  -d '{
    "dnd_level": 2,
    "dnd_hit_points": 14,
    "dnd_spellcasting": {
      "ability": "Intelligence",
      "spell_save_dc": 12,
      "spell_attack_bonus": 4,
      "cantrips_known": 3,
      "spells_known": 8,
      "spell_slots": {"1st": 3}
    }
  }'
```

**Expected Response:**
```json
{
  "message": "D&D stats updated successfully",
  "character_id": 1,
  "updated_fields": ["dnd_level", "dnd_hit_points", "dnd_spellcasting"]
}
```

## Testing with Python

```python
import requests

BASE_URL = "http://localhost:8000/api/characters"

# 1. Get available classes
response = requests.get(f"{BASE_URL}/dnd/classes")
classes = response.json()
print(f"Available classes: {classes['count']}")

# 2. Generate a character
character_data = {
    "name": "Thorin Ironforge",
    "dnd_class": "fighter",
    "dnd_species": "dwarf",
    "dnd_background": "soldier",
    "dnd_alignment": "Lawful Good",
    "dnd_level": 1,
    "ability_score_method": "standard_array"
}

response = requests.post(f"{BASE_URL}/dnd/generate", json=character_data)
character = response.json()
print(f"Generated character: {character['name']} (ID: {character['id']})")

# 3. Get character sheet
response = requests.get(f"{BASE_URL}/{character['id']}/dnd-sheet")
sheet = response.json()
print("\nCharacter Sheet:")
print(sheet['formatted_sheet'])

# 4. Update stats (level up)
updates = {
    "dnd_level": 2,
    "dnd_hit_points": character['dnd_hit_points'] + 8  # +1d10 for fighter
}

response = requests.put(f"{BASE_URL}/{character['id']}/dnd-stats", json=updates)
result = response.json()
print(f"\n{result['message']}")
```

## Frontend Integration Examples

### Fetch Classes for Dropdown

```javascript
// In your React component
const [classes, setClasses] = useState([]);

useEffect(() => {
  fetch('/api/characters/dnd/classes')
    .then(res => res.json())
    .then(data => setClasses(data.classes));
}, []);

// Render dropdown
<select>
  {classes.map(cls => (
    <option key={cls.id} value={cls.id}>
      {cls.name} ({cls.hit_die}d hit die)
    </option>
  ))}
</select>
```

### Generate Character

```javascript
const generateCharacter = async (formData) => {
  const response = await fetch('/api/characters/dnd/generate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      name: formData.name,
      dnd_class: formData.selectedClass,
      dnd_species: formData.selectedSpecies,
      dnd_background: formData.selectedBackground,
      dnd_alignment: formData.selectedAlignment,
      dnd_level: 1,
      ability_score_method: formData.scoreMethod
    })
  });
  
  const character = await response.json();
  console.log('Character generated:', character);
  return character;
};
```

### Display Character Sheet

```javascript
const [characterSheet, setCharacterSheet] = useState(null);

const loadCharacterSheet = async (characterId) => {
  const response = await fetch(`/api/characters/${characterId}/dnd-sheet`);
  const data = await response.json();
  setCharacterSheet(data);
};

// Render
{characterSheet && (
  <div>
    <h2>{characterSheet.character_data.name}</h2>
    <pre>{characterSheet.formatted_sheet}</pre>
  </div>
)}
```

## Common Issues & Solutions

### Issue: 404 Not Found
**Solution:** Ensure the backend server is running and the endpoint path is correct.

### Issue: 422 Unprocessable Entity
**Solution:** Check that all required fields are included in the request body and have valid values.

### Issue: Character generation fails
**Solution:** Verify that `dnd_class`, `dnd_species`, and `dnd_background` values match the IDs from the reference endpoints (lowercase, e.g., "wizard" not "Wizard").

### Issue: CORS errors in frontend
**Solution:** Ensure CORS is configured in `backend/main.py`:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Next Steps

1. ✅ Backend API fully functional
2. 🔄 Build frontend D&D character creator component (Step 5)
3. 🔄 Build frontend character sheet display (Step 6)
4. 🔄 Integrate with existing character creation workflow (Step 7)

---

**API Version:** 1.0  
**Last Updated:** January 20, 2025  
**Backend Status:** FULLY FUNCTIONAL ✅
