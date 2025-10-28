import React from "react";
import { Box, Chip, Stack, Typography, Tooltip, Paper } from "@mui/material";
import {
  Casino as DiceIcon,
  Chat as ChatIcon,
  Explore as ExploreIcon,
  FlashOn as AttackIcon,
} from "@mui/icons-material";

/**
 * SuggestedActions - Displays structured action suggestions from the DM
 *
 * Takes suggested_actions array from backend and renders interactive chips.
 * Each action can have:
 * - action: Description text
 * - roll: Dice notation (e.g., "Investigation (d20 + 2)")
 * - dc: Difficulty Class (e.g., "15")
 * - type: Action type (skill_check, attack, dialogue, explore)
 */
export default function SuggestedActions({ actions = [], onActionClick }) {
  if (!actions || actions.length === 0) {
    return null;
  }

  const getActionIcon = (type) => {
    switch (type) {
      case "skill_check":
        return <DiceIcon fontSize="small" />;
      case "attack":
        return <AttackIcon fontSize="small" />;
      case "dialogue":
        return <ChatIcon fontSize="small" />;
      case "explore":
      default:
        return <ExploreIcon fontSize="small" />;
    }
  };

  const getActionColor = (type) => {
    switch (type) {
      case "skill_check":
        return "primary";
      case "attack":
        return "error";
      case "dialogue":
        return "info";
      case "explore":
      default:
        return "default";
    }
  };

  const formatActionLabel = (action) => {
    const parts = [action.action];

    if (action.roll) {
      parts.push(`${action.roll}`);
    }

    if (action.dc) {
      parts.push(`DC ${action.dc}`);
    }

    return parts.join(" • ");
  };

  return (
    <Paper
      elevation={2}
      sx={{
        p: 2,
        mt: 2,
        bgcolor: "rgba(185, 167, 0, 0.08)",
        border: "1px solid rgba(185, 167, 0, 0.3)",
        borderRadius: 2,
      }}
    >
      <Stack spacing={1.5}>
        <Typography
          variant="subtitle2"
          sx={{
            color: "primary.main",
            fontWeight: 700,
            textTransform: "uppercase",
            letterSpacing: "0.5px",
            fontSize: "0.75rem",
          }}
        >
          💡 Suggested Actions
        </Typography>

        <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
          {actions.map((action, index) => (
            <Tooltip
              key={index}
              title={
                <Box>
                  <Typography variant="body2" sx={{ fontWeight: 700, mb: 0.5 }}>
                    {action.action}
                  </Typography>
                  {action.roll && (
                    <Typography variant="caption" display="block">
                      🎲 Roll: {action.roll}
                    </Typography>
                  )}
                  {action.dc && (
                    <Typography variant="caption" display="block">
                      🎯 DC: {action.dc}
                    </Typography>
                  )}
                  <Typography
                    variant="caption"
                    display="block"
                    sx={{ mt: 0.5, opacity: 0.7 }}
                  >
                    Click to use this action
                  </Typography>
                </Box>
              }
              arrow
              placement="top"
            >
              <Chip
                icon={getActionIcon(action.type)}
                label={formatActionLabel(action)}
                onClick={() =>
                  onActionClick &&
                  onActionClick(action.action, action.roll, action.dc)
                }
                color={getActionColor(action.type)}
                variant="outlined"
                sx={{
                  cursor: "pointer",
                  transition: "all 0.2s ease",
                  fontSize: "0.85rem",
                  height: "auto",
                  py: 1,
                  px: 1.5,
                  "& .MuiChip-label": {
                    whiteSpace: "normal",
                    textAlign: "left",
                    lineHeight: 1.4,
                    py: 0.5,
                  },
                  "&:hover": {
                    transform: "translateY(-2px)",
                    boxShadow: 2,
                    bgcolor: "rgba(185, 167, 0, 0.15)",
                    borderColor: "primary.main",
                  },
                }}
              />
            </Tooltip>
          ))}
        </Stack>
      </Stack>
    </Paper>
  );
}
