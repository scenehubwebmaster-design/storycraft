# Hybrid Context Optimization Implementation

## Overview

Implemented a smart hybrid approach for including character stats in DM prompts. The system automatically detects when mechanical information is needed and switches between **FULL** and **COMPACT** context modes.

## How It Works

### 1. Context Detection

The `_should_include_stats()` method scans the last 6 messages (3 user+assistant pairs) for mechanical gameplay keywords:

**Mechanical Keywords:**

- Dice/Checks: `roll`, `check`, `saving throw`, `d20`, `skill check`
- Combat: `attack`, `hit`, `damage`, `strike`, `initiative`
- Spellcasting: `cast`, `spell`, `cantrip`, `spell slot`
- Resources: `hp`, `hit points`, `healing`, `ki point`, `rage`
- Stats: `ac`, `armor class`, `modifier`, `bonus`
- Conditions: `poisoned`, `stunned`, `paralyzed`, `prone`

### 2. Two Modes

#### COMPACT Mode (Names Only)

**When:** Pure roleplay, social interactions, exploration without mechanics
**Includes:** Character names and basic class/level info
**Token Cost:** ~50-100 tokens
**Example:**

```
=== PARTY ===
Elara Moonwhisper (Wizard 3), Thorn Ironforge (Fighter 3)
```

#### FULL Mode (Complete Stats)

**When:** Combat, skill checks, spellcasting, mechanical actions
**Includes:** HP, AC, ability scores, modifiers, spell slots, conditions, skills
**Token Cost:** ~500-600 tokens for 4-character party
**Example:**

```
=== PARTY CHARACTERS (FULL STATS) ===

**Elara Moonwhisper**
  Class: Wizard 3, Species: High Elf
  HP: 18/18 (Temp: 0) | AC: 13
  STR: 8 (-1) | DEX: 14 (+2) | CON: 12 (+1)
  INT: 18 (+4) | WIS: 14 (+2) | CHA: 10 (+0)
  Proficiency: +2 | Initiative: +2 | Speed: 30 ft
  Spellcasting: Intelligence | DC: 14 | Attack: +6
  Spell Slots: 1st: 4/4, 2nd: 2/2
  Skill Proficiencies: Arcana, History, Investigation, Insight, Perception
```

### 3. Combat Override

When in combat (`combat_state.active == True`), FULL mode is always used regardless of conversation content.

## Token Savings

| Scenario           | Mode    | Tokens | Savings    |
| ------------------ | ------- | ------ | ---------- |
| Roleplay dialogue  | COMPACT | ~50    | 500 tokens |
| Social interaction | COMPACT | ~50    | 500 tokens |
| Skill check        | FULL    | ~550   | 0          |
| Combat round       | FULL    | ~550   | 0          |
| Spellcasting       | FULL    | ~550   | 0          |

**Average Session Savings: 30-40% fewer tokens**

For a typical 2-hour session with 50 messages (30 roleplay, 20 mechanical):

- Old approach: 50 × 550 = 27,500 tokens
- New approach: (30 × 50) + (20 × 550) = 12,500 tokens
- **Savings: 15,000 tokens (54%)**

## Benefits

1. **Automatic:** No manual configuration needed
2. **Conservative:** Defaults to FULL mode on first message and when in doubt
3. **Responsive:** Switches modes within 3 message exchanges
4. **Combat-aware:** Always uses FULL mode during combat
5. **Cost-effective:** Significant token savings during roleplay-heavy sessions
6. **No RAG complexity:** Simple keyword matching, no embedding lookups

## Debug Logging

Console output shows mode selection:

```
[DM Context] Including FULL character stats (combat=False, keywords detected)
[DM Context] Using COMPACT mode (names only) - no mechanical keywords detected
```

## Testing

Run `backend/test_context_optimization.py` to see the system in action across different scenarios.

## When NOT To Use This

This optimization is **NOT** appropriate for:

- Static reference data (use RAG instead)
- NPC descriptions (already using RAG)
- Spell/monster lookups (already using MCP)
- World lore (already using RAG with 52K embeddings)

## Future Enhancements

Possible improvements:

- ML-based intent classification (more accurate than keywords)
- Per-character stat inclusion (only include caster's stats for spellcasting)
- Configurable keyword list via settings
- Analytics dashboard showing token savings
