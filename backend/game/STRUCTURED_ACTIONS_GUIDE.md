# Structured Actions Guide

## Overview

The DM chat system now generates **structured action suggestions** that are displayed as interactive chips in the UI, replacing unreliable markdown table parsing.

## Backend Implementation

### Response Format

All DM responses now include a `suggested_actions` array:

```python
DMResponse(
    message="The tavern is bustling with activity...",
    suggested_actions=[
        {
            "action": "Approach the cloaked figure at the bar",
            "roll": "Investigation (d20 + 0)",
            "dc": "12",
            "type": "skill_check"
        },
        {
            "action": "Talk to Mira Hearthstone about rumors",
            "roll": "Persuasion (d20 + 3)",
            "dc": "10",
            "type": "dialogue"
        },
        {
            "action": "Listen to the conversation at Grolk's table",
            "roll": "Perception (d20 - 1)",
            "dc": "13",
            "type": "skill_check"
        },
        {
            "action": "Order a drink and observe the tavern",
            "roll": None,
            "dc": None,
            "type": "explore"
        }
    ]
)
```

### Action Types

- **`skill_check`**: Requires a dice roll against a DC (Investigation, Perception, Stealth, etc.)
- **`attack`**: Combat action (melee, ranged, spell attack)
- **`dialogue`**: Conversation with NPCs (no roll required usually)
- **`explore`**: General exploration (search, examine, move)

### LLM Prompt Format

The narrative engine prompts now explicitly request structured actions:

```python
"""
Format response as JSON:
{
  "description": "...",
  "location": "...",
  "suggested_actions": [
    {
      "action": "Search the ancient altar for hidden switches",
      "roll": "Investigation (d20 + 2)",
      "dc": "15",
      "type": "skill_check"
    },
    {
      "action": "Speak with the mysterious cloaked figure",
      "roll": null,
      "dc": null,
      "type": "dialogue"
    }
  ]
}

IMPORTANT: Always include "suggested_actions" with 3-4 concrete, context-appropriate actions.
"""
```

## Frontend Implementation

### SuggestedActions Component

Located at: `frontend/src/components/game/SuggestedActions.jsx`

Displays actions as color-coded chips:

- 🎲 **Skill Check** (blue/primary) - Shows dice roll and DC
- ⚡ **Attack** (red/error) - Combat actions
- 💬 **Dialogue** (info/blue) - Conversations
- 🗺️ **Explore** (default) - General exploration

### Integration in DMChat

Actions are rendered below each DM message:

```jsx
{
  msg.role === "assistant" &&
    msg.metadata &&
    msg.metadata.suggested_actions &&
    msg.metadata.suggested_actions.length > 0 && (
      <SuggestedActions
        actions={msg.metadata.suggested_actions}
        onActionClick={(action, roll, dc) => {
          // Auto-populate chat input with formatted action
        }}
      />
    );
}
```

## Example Usage

### DM Response

```json
{
  "message": "Caspian Blackwood enters the Moonlit Mug...",
  "suggested_actions": [
    {
      "action": "Approach the cloaked figure – Ask what business brings them to Neverwinter",
      "roll": "Investigation (d20 + 0)",
      "dc": "12",
      "type": "skill_check"
    },
    {
      "action": "Talk to Mira Hearthstone – Inquire about recent rumors or work",
      "roll": "Persuasion (d20 + 3)",
      "dc": "10",
      "type": "dialogue"
    },
    {
      "action": "Listen at Grolk's table – Try to overhear any useful gossip",
      "roll": "Perception (d20 - 1)",
      "dc": "13",
      "type": "skill_check"
    },
    {
      "action": "Order a drink and observe – Gather a feel for the tavern's mood",
      "roll": null,
      "dc": null,
      "type": "explore"
    }
  ]
}
```

### UI Rendering

The frontend displays these as clickable chips:

```
💡 Suggested Actions
┌──────────────────────────────────────────────────────────┐
│ 🎲 Approach the cloaked figure... • Investigation (d20)  │
│ 💬 Talk to Mira Hearthstone... • Persuasion (d20 + 3)   │
│ 🎲 Listen at Grolk's table... • Perception (d20 - 1)     │
│ 🗺️ Order a drink and observe                            │
└──────────────────────────────────────────────────────────┘
```

Click any chip → Action text populates chat input → Player can edit/send

## Benefits

1. **Consistent Format**: No relying on LLM markdown formatting
2. **Better UX**: Interactive, color-coded chips with tooltips
3. **Reliable Parsing**: Structured JSON instead of regex on markdown
4. **Extensible**: Easy to add new action types or properties
5. **Backward Compatible**: Fallback parser handles old text-based choices

## Fallback Behavior

If the LLM doesn't provide `suggested_actions`, the system:

1. Tries to parse from `choices` field
2. Uses `_parse_choice_string()` to extract roll/DC from text
3. Returns empty array if no actions found

This ensures the system works even with older prompts or LLM failures.

## Testing

To test with Caspian Blackwood's scenario:

1. Send a message in DM chat
2. Check backend response for `suggested_actions` field
3. Verify frontend displays action chips
4. Click a chip and confirm input is populated
5. Check that ability check modal opens for skill checks (if enabled)

## Future Enhancements

- **Smart Roll Detection**: Detect character modifiers from party stats
- **Context-Aware Actions**: Filter actions based on character class/abilities
- **Action History**: Track frequently used actions
- **Custom Actions**: Let players define reusable action templates
