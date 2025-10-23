import React from "react";
import { Box, Typography, Paper, Avatar } from "@mui/material";
import ReactMarkdown from "react-markdown";
import { Chat as DialogueIcon } from "@mui/icons-material";

/**
 * DMMessageFormatter - Format DM messages with speaker identification
 *
 * Parses DM narrative to identify dialogue with speakers and formats them
 * like video game dialogues: "NPC Name: 'dialogue text'"
 */
const DMMessageFormatter = ({ content }) => {
  if (!content) return null;

  // Parse dialogue patterns:
  // - "Name says: 'dialogue'" or "Name says, 'dialogue'"
  // - "'Dialogue,' Name says" or "'Dialogue,' says Name"
  // - Direct quotes with speaker attribution before or after
  const dialoguePatterns = [
    // Pattern 1: Name says: "dialogue" or Name says, "dialogue"
    /([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+says[,:]?\s*["']([^"']+)["']/g,
    // Pattern 2: "dialogue," says Name or "dialogue," Name says
    /["']([^"']+)["'],?\s+(?:says\s+)?([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+says/g,
    // Pattern 3: Name: "dialogue" (simple colon format)
    /([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?):\s*["']([^"']+)["']/g,
  ];

  // Split content into segments (narrative and dialogue)
  const segments = [];
  let lastIndex = 0;
  const matches = [];

  // Collect all dialogue matches
  for (const pattern of dialoguePatterns) {
    let match;
    while ((match = pattern.exec(content)) !== null) {
      matches.push({
        index: match.index,
        length: match[0].length,
        speaker: match[1],
        dialogue: match[2] || match[1], // Handle different capture groups
        fullMatch: match[0],
      });
    }
  }

  // Sort matches by index to process in order
  matches.sort((a, b) => a.index - b.index);

  // Remove overlapping matches (keep first occurrence)
  const uniqueMatches = [];
  let lastEndIndex = 0;
  for (const match of matches) {
    if (match.index >= lastEndIndex) {
      uniqueMatches.push(match);
      lastEndIndex = match.index + match.length;
    }
  }

  // Build segments array with narrative and dialogue
  let currentIndex = 0;
  for (const match of uniqueMatches) {
    // Add narrative before dialogue
    if (match.index > currentIndex) {
      segments.push({
        type: "narrative",
        content: content.substring(currentIndex, match.index).trim(),
      });
    }

    // Add dialogue segment
    // Swap speaker/dialogue if the pattern captured them in wrong order
    let speaker = match.speaker;
    let dialogue = match.dialogue;

    // Heuristic: if "speaker" looks like dialogue (lowercase start, long), swap
    if (speaker && dialogue && speaker.length > 50 && dialogue.length < 30) {
      [speaker, dialogue] = [dialogue, speaker];
    }

    segments.push({
      type: "dialogue",
      speaker: speaker,
      content: dialogue,
    });

    currentIndex = match.index + match.length;
  }

  // Add remaining narrative after last dialogue
  if (currentIndex < content.length) {
    segments.push({
      type: "narrative",
      content: content.substring(currentIndex).trim(),
    });
  }

  // If no dialogues detected, treat entire content as narrative
  if (segments.length === 0) {
    segments.push({
      type: "narrative",
      content: content,
    });
  }

  return (
    <Box>
      {segments.map((segment, index) => {
        if (segment.type === "narrative") {
          return <ReactMarkdown key={index}>{segment.content}</ReactMarkdown>;
        } else {
          // Dialogue segment - format like video game dialogue
          return (
            <Paper
              key={index}
              elevation={0}
              sx={{
                my: 1,
                p: 1.5,
                bgcolor: "rgba(212, 175, 55, 0.08)",
                border: "1px solid",
                borderColor: "primary.light",
                borderLeft: "4px solid",
                borderLeftColor: "primary.main",
                display: "flex",
                gap: 1,
                alignItems: "flex-start",
              }}
            >
              <Avatar
                sx={{
                  width: 32,
                  height: 32,
                  bgcolor: "primary.main",
                  fontSize: "0.875rem",
                }}
              >
                {segment.speaker?.charAt(0) || "?"}
              </Avatar>
              <Box sx={{ flex: 1 }}>
                <Typography
                  variant="subtitle2"
                  sx={{
                    color: "primary.main",
                    fontWeight: 600,
                    display: "flex",
                    alignItems: "center",
                    gap: 0.5,
                    mb: 0.5,
                  }}
                >
                  <DialogueIcon fontSize="small" />
                  {segment.speaker}
                </Typography>
                <Typography
                  variant="body2"
                  sx={{
                    fontStyle: "italic",
                    color: "text.primary",
                    pl: 1,
                    borderLeft: "2px solid",
                    borderLeftColor: "primary.light",
                  }}
                >
                  "{segment.content}"
                </Typography>
              </Box>
            </Paper>
          );
        }
      })}
    </Box>
  );
};

export default DMMessageFormatter;
