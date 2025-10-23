import React from "react";
import { Box, Chip, Stack, Typography } from "@mui/material";
import {
  QuestionAnswer as QuestionIcon,
  Visibility as LookIcon,
  TouchApp as ActionIcon,
  Chat as TalkIcon,
} from "@mui/icons-material";

/**
 * ResponseSuggestionChips - Context-aware suggestion chips
 * Analyzes the last DM message and suggests relevant player actions
 */
const ResponseSuggestionChips = ({ lastMessage, onSuggestionClick }) => {
  if (!lastMessage || !lastMessage.content) return null;

  const content = lastMessage.content.toLowerCase();
  const suggestions = [];

  // Parse content for NPCs (look for "I'm [Name]" or "I am [Name]" patterns)
  // Match patterns like "I'm Harbin Wester" or "My name is John Smith"
  const npcPatterns = [
    /I'm\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)/,
    /I am\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)/,
    /My name is\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)/,
    /call me\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)/i,
  ];

  let npcName = null;
  for (const pattern of npcPatterns) {
    const match = lastMessage.content.match(pattern);
    if (match && match[1]) {
      npcName = match[1].trim();
      // Validate it looks like a name (not a sentence)
      if (npcName.split(" ").length <= 3 && npcName.length < 30) {
        break;
      } else {
        npcName = null;
      }
    }
  }

  if (npcName) {
    suggestions.push({
      label: `Ask ${npcName} more`,
      icon: <QuestionIcon fontSize="small" />,
      action: `I ask ${npcName} to tell me more about what's happening here.`,
    });
  }

  // Detect locations/places
  const locationMatches = lastMessage.content.match(
    /\b(tavern|inn|temple|castle|dungeon|cave|forest|town|city|village|shop|guild|manor|tower)\b/gi
  );
  if (locationMatches && locationMatches.length > 0) {
    const location = locationMatches[0];
    suggestions.push({
      label: `Look around the ${location}`,
      icon: <LookIcon fontSize="small" />,
      action: `I take a moment to look around the ${location}, observing the people and details.`,
    });
  }

  // Detect questions directed at player
  if (
    content.includes("what would you like") ||
    content.includes("what do you") ||
    content.includes("?")
  ) {
    suggestions.push({
      label: "Introduce myself",
      icon: <TalkIcon fontSize="small" />,
      action: "I introduce myself and explain why I've come here.",
    });
  }

  // Detect items or objects mentioned
  const itemMatches = lastMessage.content.match(
    /\b(ale|drink|food|weapon|sword|shield|potion|map|scroll|book|coin|gold)\b/gi
  );
  if (itemMatches && itemMatches.length > 0) {
    const item = itemMatches[0];
    suggestions.push({
      label: `Ask about ${item}`,
      icon: <QuestionIcon fontSize="small" />,
      action: `I ask about the ${item}.`,
    });
  }

  // Detect potential combat or danger
  if (
    content.includes("threat") ||
    content.includes("danger") ||
    content.includes("hostile") ||
    content.includes("attack") ||
    content.includes("monster") ||
    content.includes("enemy")
  ) {
    suggestions.push({
      label: "Ready my weapon",
      icon: <ActionIcon fontSize="small" />,
      action: "I ready my weapon and prepare for potential conflict.",
    });
  }

  // Detect social/exploration context
  if (
    content.includes("crowd") ||
    content.includes("patrons") ||
    content.includes("people")
  ) {
    suggestions.push({
      label: "Mingle with locals",
      icon: <TalkIcon fontSize="small" />,
      action:
        "I approach some of the locals and try to strike up a conversation.",
    });
  }

  // Detect information gathering opportunities
  if (
    content.includes("rumor") ||
    content.includes("news") ||
    content.includes("information") ||
    content.includes("story")
  ) {
    suggestions.push({
      label: "Listen for rumors",
      icon: <QuestionIcon fontSize="small" />,
      action:
        "I listen carefully to the conversations around me, trying to pick up any useful rumors or information.",
    });
  }

  // Generic fallback suggestions if nothing specific detected
  if (suggestions.length === 0) {
    suggestions.push(
      {
        label: "Investigate further",
        icon: <LookIcon fontSize="small" />,
        action: "I investigate the area more carefully.",
      },
      {
        label: "Ask a question",
        icon: <QuestionIcon fontSize="small" />,
        action: "Can you tell me more about what's happening here?",
      }
    );
  }

  // Limit to 4 suggestions maximum
  const displaySuggestions = suggestions.slice(0, 4);

  return (
    <Box sx={{ mb: 2 }}>
      <Typography
        variant="caption"
        color="text.secondary"
        sx={{ mb: 1, display: "block" }}
      >
        💡 Suggested Actions:
      </Typography>
      <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
        {displaySuggestions.map((suggestion, index) => (
          <Chip
            key={index}
            icon={suggestion.icon}
            label={suggestion.label}
            onClick={() => onSuggestionClick(suggestion.action)}
            sx={{
              mb: 1,
              bgcolor: "primary.light",
              color: "white",
              border: "1px solid",
              borderColor: "primary.main",
              "&:hover": {
                bgcolor: "primary.main",
                transform: "translateY(-2px)",
                boxShadow: 2,
              },
              transition: "all 0.2s",
            }}
          />
        ))}
      </Stack>
    </Box>
  );
};

export default ResponseSuggestionChips;
