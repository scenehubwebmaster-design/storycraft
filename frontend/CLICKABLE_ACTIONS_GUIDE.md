# Clickable Actions Guide

## Overview

The DM Chat interface now supports **clickable action buttons** that automatically populate the player's input field. This makes it easier for players to respond to DM prompts without typing everything manually.

## How to Format Actions

### Method 1: Bold Text Actions (Simple)

For narrative-style actions, use **double asterisks** to mark action text:

```markdown
**Approach Rorik** – Introduce yourself and ask about the map.
**Inspect the parchment** – Take a closer look at the map.
**Talk to Mira** – Order a drink and gather rumors.
```

**Result:** Each bold action becomes a clickable chip with an amber/gold styling.

**Player Experience:** Clicking "Approach Rorik" populates the input with:

```
I approach Rorik
```

---

### Method 2: Skill Check Tables (Advanced)

For actions that require ability checks or skill rolls, use a markdown table:

```markdown
| Action                                   | Suggested Roll   | DC (if applicable) |
| ---------------------------------------- | ---------------- | ------------------ |
| Perception check to spot hidden details  | d20 + Perception | 12 (to notice)     |
| Insight check to read Rorik's intentions | d20 + Insight    | 14 (to discern)    |
| Persuasion to convince the barkeep       | d20 + Persuasion | 13 (to succeed)    |
```

**Result:** Each row becomes a clickable chip with blue styling, showing the roll and DC info.

**Player Experience:** Clicking opens the ability check panel (if characters are available) or populates the input with:

```
I want to make a Perception check to spot hidden details

Suggested roll: d20 + Perception
DC: 12
```

---

## Best Practices for DMs

### ✅ Do:

- Use bold text for **narrative actions** (exploring, talking, moving)
- Use tables for **skill checks** (Perception, Insight, Investigation, etc.)
- Keep action text concise (under 50 characters is ideal)
- Include descriptive context after the dash (–) in bold actions
- Group related actions together

### ❌ Don't:

- Use bold for **stats** (AC, HP, DC) – these won't be clickable
- Use bold for **section headings** (they're filtered out)
- Mix bold and table formats for the same actions (pick one style)

---

## Example: Opening Tavern Scene

```markdown
The night air in Breezewood carries the scent of pine and distant campfires. Inside the Gilded Griffon tavern, a weathered half-elf named Rorik "Stone-hand" Thorne sits beneath a banner, watching the room with keen eyes.

A cloaked figure drops a crumpled parchment onto Rorik's table—it looks like a map of the Ruins of Amber, marked with a red X.

**Possible actions:**

**Approach Rorik** – Introduce yourself and ask about the map or the cloaked figure.
**Inspect the parchment** – Take a closer look at the map (requires Perception).
**Talk to Mira** – Order a drink from the halfling barkeep and gather rumors.
**Listen to conversations** – Eavesdrop on tavern patrons (Perception or Insight).
**Take a short rest** – Recover hit points if needed.

| Action                             | Suggested Roll   | DC  |
| ---------------------------------- | ---------------- | --- |
| Perception to read the map details | d20 + Perception | 12  |
| Insight to gauge Rorik's mood      | d20 + Insight    | 14  |
```

---

## Technical Details

### Parsing Logic

- **Bold actions:** Matches `**Text**` patterns, excludes stats/headings
- **Table actions:** Matches markdown tables with "Action" header
- **Duplicate prevention:** Same action text won't appear twice
- **Icon detection:** Automatically assigns icons based on keywords (Perception 👁️, Insight 🧠, etc.)

### Styling

- **Bold actions:** Amber/gold chips with warm hover effects
- **Table actions:** Blue chips with detailed roll/DC info
- Both types show tooltips and animate on hover

### Integration

- Located in: `frontend/src/components/game/ActionChipsParser.jsx`
- Used in: `frontend/src/pages/DMChat.jsx`
- Handles click events to populate chat input or open ability check panels

---

## Testing

To test the feature:

1. Start dev servers: `npm run dev:all`
2. Create a new DM chat session
3. Send a DM message with bold action text or a skill check table
4. Verify that clickable chips appear below the message
5. Click a chip to populate the input field
6. Confirm the text is correctly formatted in first-person

---

## Future Enhancements

Potential improvements:

- [ ] Add action history/favorites
- [ ] Support inline roll buttons (click to auto-roll)
- [ ] Parse more complex action formats (e.g., nested lists)
- [ ] Add action icons for combat actions (Attack, Dash, Dodge, etc.)
- [ ] Support action templates/macros
