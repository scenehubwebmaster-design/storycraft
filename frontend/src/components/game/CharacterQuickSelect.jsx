import React from "react";
import {
  Box,
  Chip,
  Stack,
  Avatar,
  Typography,
  Tooltip,
  Paper,
  IconButton,
} from "@mui/material";
import {
  Person as PersonIcon,
  CheckCircle as CheckCircleIcon,
  Circle as CircleIcon,
} from "@mui/icons-material";

/**
 * CharacterQuickSelect - Quick character selection bar for multi-player sessions
 *
 * Displays all available party characters with:
 * - Character avatar and name
 * - Active/inactive state toggle
 * - Visual indication of who's currently acting
 * - Click to toggle character selection
 *
 * Use case: John and Sam want to take actions simultaneously
 * - Both select their characters
 * - Make ability checks or send messages
 * - System tracks who's acting
 */

const CharacterQuickSelect = ({
  characters = [],
  activeCharacterIds = [],
  onToggleCharacter,
  sx = {},
}) => {
  if (!characters || characters.length === 0) {
    return null;
  }

  return (
    <Paper
      elevation={0}
      sx={{
        p: 1.5,
        bgcolor: "rgba(144, 202, 249, 0.05)",
        borderBottom: 1,
        borderColor: "rgba(144, 202, 249, 0.2)",
        ...sx,
      }}
    >
      <Stack
        direction="row"
        spacing={1}
        alignItems="center"
        flexWrap="wrap"
        useFlexGap
      >
        <Typography
          variant="caption"
          color="text.secondary"
          sx={{ fontWeight: 600, mr: 1 }}
        >
          Acting Characters:
        </Typography>

        {characters.map((char) => {
          const isActive = activeCharacterIds.includes(char.id);

          return (
            <Tooltip
              key={char.id}
              title={
                isActive
                  ? `${char.name} is acting (click to deselect)`
                  : `Click to act as ${char.name}`
              }
              arrow
            >
              <Chip
                avatar={
                  <Avatar
                    src={char.portrait_image}
                    sx={{
                      width: 24,
                      height: 24,
                      bgcolor: isActive ? "primary.main" : "action.disabled",
                    }}
                  >
                    {char.name[0]}
                  </Avatar>
                }
                icon={
                  isActive ? (
                    <CheckCircleIcon sx={{ fontSize: 16 }} />
                  ) : (
                    <CircleIcon sx={{ fontSize: 16, opacity: 0.5 }} />
                  )
                }
                label={
                  <Box>
                    <Typography variant="body2" sx={{ fontWeight: 600 }}>
                      {char.name}
                    </Typography>
                    {char.dnd_class && (
                      <Typography variant="caption" color="text.secondary">
                        Lvl {char.dnd_level || 1} {char.dnd_class}
                      </Typography>
                    )}
                  </Box>
                }
                onClick={() => onToggleCharacter(char.id)}
                clickable
                variant={isActive ? "filled" : "outlined"}
                color={isActive ? "primary" : "default"}
                sx={{
                  height: "auto",
                  py: 0.75,
                  px: 1,
                  "& .MuiChip-label": {
                    px: 0.5,
                  },
                  transition: "all 0.2s ease",
                  ...(isActive && {
                    bgcolor: "rgba(25, 118, 210, 0.15)",
                    borderColor: "primary.main",
                    boxShadow: "0 0 8px rgba(25, 118, 210, 0.3)",
                  }),
                  "&:hover": {
                    transform: "translateY(-2px)",
                    boxShadow: isActive
                      ? "0 4px 12px rgba(25, 118, 210, 0.4)"
                      : "0 4px 8px rgba(0,0,0,0.2)",
                  },
                }}
              />
            </Tooltip>
          );
        })}

        {activeCharacterIds.length === 0 && (
          <Typography
            variant="caption"
            color="warning.main"
            sx={{ ml: 1, fontStyle: "italic" }}
          >
            (No character selected - click a character to act)
          </Typography>
        )}
      </Stack>
    </Paper>
  );
};

export default CharacterQuickSelect;
