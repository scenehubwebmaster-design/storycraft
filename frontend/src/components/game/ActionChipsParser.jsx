import React from "react";
import { Box, Chip, Stack, Typography, Divider } from "@mui/material";
import {
  Visibility as PerceptionIcon,
  Psychology as InsightIcon,
  RecordVoiceOver as PersuasionIcon,
  Search as InvestigateIcon,
  DirectionsRun as AthleticsIcon,
  PanTool as SleightIcon,
  Security as StealthIcon,
  Healing as MedicineIcon,
  Nature as NatureIcon,
  MenuBook as ArcanaIcon,
  Church as ReligionIcon,
  Public as HistoryIcon,
  Pets as AnimalHandlingIcon,
  EmojiPeople as PerformanceIcon,
  Gavel as IntimidationIcon,
  SentimentVerySatisfied as DeceptionIcon,
} from "@mui/icons-material";

/**
 * Parses D&D action tables from markdown and renders them as clickable chips.
 *
 * Supports tables in the format:
 * | Action | Suggested Roll | DC (if applicable) |
 * |--------|----------------|-------------------|
 * | Perception check to spot... | d20 + ... | 12 (to notice...) |
 *
 * Each action becomes a clickable chip that sends the action text to the chat.
 */

const getIconForAction = (actionText) => {
  const text = actionText.toLowerCase();

  if (text.includes("perception")) return <PerceptionIcon fontSize="small" />;
  if (text.includes("insight")) return <InsightIcon fontSize="small" />;
  if (text.includes("persuasion")) return <PersuasionIcon fontSize="small" />;
  if (text.includes("investigate") || text.includes("investigation"))
    return <InvestigateIcon fontSize="small" />;
  if (text.includes("athletics")) return <AthleticsIcon fontSize="small" />;
  if (text.includes("sleight")) return <SleightIcon fontSize="small" />;
  if (text.includes("stealth")) return <StealthIcon fontSize="small" />;
  if (text.includes("medicine")) return <MedicineIcon fontSize="small" />;
  if (text.includes("nature")) return <NatureIcon fontSize="small" />;
  if (text.includes("arcana")) return <ArcanaIcon fontSize="small" />;
  if (text.includes("religion")) return <ReligionIcon fontSize="small" />;
  if (text.includes("history")) return <HistoryIcon fontSize="small" />;
  if (text.includes("animal")) return <AnimalHandlingIcon fontSize="small" />;
  if (text.includes("performance")) return <PerformanceIcon fontSize="small" />;
  if (text.includes("intimidation"))
    return <IntimidationIcon fontSize="small" />;
  if (text.includes("deception")) return <DeceptionIcon fontSize="small" />;

  return null;
};

const parseBoldActions = (content) => {
  // Match bold text patterns: **Action Text** or **Action Text** – Description
  // Pattern captures: **Action** or **Action** – additional context
  const boldActionRegex = /\*\*([^*]+)\*\*\s*[–—-]?\s*([^\n.]*)/g;
  const matches = [...content.matchAll(boldActionRegex)];

  const actions = [];
  const seenActions = new Set(); // Prevent duplicates

  matches.forEach((match) => {
    const action = match[1].trim();
    const description = match[2].trim();

    // Skip if it's just a heading or title (all caps, or very short)
    if (action.length < 5 || action === action.toUpperCase()) {
      return;
    }

    // Skip if we've already added this action
    if (seenActions.has(action)) {
      return;
    }

    // Skip common non-action bold text patterns
    const skipPatterns = [
      /^(AC|HP|Speed|Initiative|STR|DEX|CON|INT|WIS|CHA|DC|CR):/i,
      /^(Armor Class|Hit Points|Challenge Rating):/i,
      /^Table /i,
      /^Chapter /i,
      /^\d+\./, // Numbered items
    ];

    if (skipPatterns.some((pattern) => pattern.test(action))) {
      return;
    }

    seenActions.add(action);

    actions.push({
      action,
      description: description || "",
      label: action.length > 50 ? action.substring(0, 50) + "..." : action,
      type: "bold",
    });
  });

  return actions.length > 0 ? actions : null;
};

const parseActionTable = (content) => {
  // Match markdown tables for Quick Reference or Suggested Actions
  const tableRegex = /\|\s*Action\s*\|[^\n]*\n\|[-:\s|]+\n((?:\|[^\n]*\n)+)/gi;
  const matches = [...content.matchAll(tableRegex)];

  if (matches.length === 0) return null;

  const actions = [];

  matches.forEach((match) => {
    const rows = match[1].trim().split("\n");

    rows.forEach((row) => {
      // Parse table row: | Action | Suggested Roll | DC |
      const cells = row
        .split("|")
        .map((cell) => cell.trim())
        .filter(Boolean);

      if (cells.length >= 2) {
        const action = cells[0];
        const roll = cells[1];
        const dc = cells[2] || "";

        // Skip empty or separator rows
        if (
          action &&
          !action.match(/^[-:\s]+$/) &&
          action.toLowerCase() !== "action"
        ) {
          actions.push({
            action,
            roll,
            dc,
            label:
              action.length > 40 ? action.substring(0, 40) + "..." : action,
            type: "table",
          });
        }
      }
    });
  });

  return actions.length > 0 ? actions : null;
};

export default function ActionChipsParser({ content, onActionClick }) {
  // Parse both table-based and bold text actions
  const tableActions = parseActionTable(content);
  const boldActions = parseBoldActions(content);

  // Combine actions, prioritizing table actions
  const allActions = [...(tableActions || []), ...(boldActions || [])];

  if (allActions.length === 0) {
    return null;
  }

  return (
    <Box
      sx={{
        mt: 2,
        mb: 1,
        p: 2,
        bgcolor: "rgba(144, 202, 249, 0.08)",
        borderRadius: 2,
        border: "1px solid rgba(144, 202, 249, 0.3)",
      }}
    >
      <Typography
        variant="subtitle2"
        sx={{
          mb: 1.5,
          fontWeight: 600,
          color: "primary.light",
          display: "flex",
          alignItems: "center",
          gap: 1,
        }}
      >
        <MenuBookIcon fontSize="small" />
        {tableActions && tableActions.length > 0
          ? "Quick Reference Actions"
          : "Possible Actions"}
      </Typography>

      <Stack spacing={1}>
        {allActions.map((item, index) => {
          const icon = getIconForAction(item.action);
          const dcText = item.dc
            ? ` (DC ${item.dc.match(/\d+/)?.[0] || item.dc})`
            : "";

          // Different styling for bold vs table actions
          const isBoldAction = item.type === "bold";

          return (
            <Chip
              key={index}
              icon={icon}
              label={
                <Box
                  sx={{
                    display: "flex",
                    flexDirection: "column",
                    alignItems: "flex-start",
                    py: 0.5,
                  }}
                >
                  <Typography variant="body2" sx={{ fontWeight: 500 }}>
                    {item.label}
                  </Typography>
                  {item.roll && (
                    <Typography
                      variant="caption"
                      sx={{ color: "text.secondary", mt: 0.25 }}
                    >
                      {item.roll}
                      {dcText}
                    </Typography>
                  )}
                  {isBoldAction && item.description && (
                    <Typography
                      variant="caption"
                      sx={{ color: "text.secondary", mt: 0.25 }}
                    >
                      {item.description}
                    </Typography>
                  )}
                </Box>
              }
              onClick={() => onActionClick(item.action, item.roll, item.dc)}
              clickable
              sx={{
                height: "auto",
                py: 1,
                px: 1.5,
                justifyContent: "flex-start",
                bgcolor: isBoldAction
                  ? "rgba(255, 193, 7, 0.12)"
                  : "rgba(144, 202, 249, 0.12)",
                border: "1px solid",
                borderColor: isBoldAction
                  ? "rgba(255, 193, 7, 0.4)"
                  : "rgba(144, 202, 249, 0.3)",
                transition: "all 0.2s ease",
                "& .MuiChip-label": {
                  width: "100%",
                  display: "block",
                  whiteSpace: "normal",
                  textAlign: "left",
                },
                "&:hover": {
                  bgcolor: isBoldAction
                    ? "rgba(255, 193, 7, 0.25)"
                    : "rgba(144, 202, 249, 0.2)",
                  borderColor: isBoldAction ? "warning.main" : "primary.main",
                  transform: "translateY(-1px)",
                  boxShadow: "0 4px 8px rgba(0,0,0,0.2)",
                },
                "&:active": {
                  transform: "translateY(0)",
                },
              }}
            />
          );
        })}
      </Stack>

      <Divider sx={{ mt: 2, borderColor: "rgba(144, 202, 249, 0.2)" }} />

      <Typography
        variant="caption"
        sx={{
          mt: 1,
          display: "block",
          color: "text.secondary",
          fontStyle: "italic",
        }}
      >
        Click an action to add it to your message
      </Typography>
    </Box>
  );
}
