/**
 * ActionButtons - Quick Action Buttons
 *
 * Provides common action shortcuts
 */

import React from "react";
import { Paper, Box, Button, Grid } from "@mui/material";
import {
  Explore as ExploreIcon,
  Search as SearchIcon,
  Hearing as ListenIcon,
  Chat as TalkIcon,
  SportsKabaddi as AttackIcon,
  Help as HelpIcon,
} from "@mui/icons-material";

function ActionButtons({ onAction, isInCombat = false, disabled = false }) {
  const actions = [
    {
      id: "explore",
      label: "Look Around",
      icon: <ExploreIcon />,
      color: "primary",
    },
    { id: "search", label: "Search", icon: <SearchIcon />, color: "primary" },
    { id: "listen", label: "Listen", icon: <ListenIcon />, color: "primary" },
    { id: "talk", label: "Talk", icon: <TalkIcon />, color: "primary" },
    {
      id: "attack",
      label: "Attack",
      icon: <AttackIcon />,
      color: "error",
      showOnlyInCombat: true,
    },
    { id: "help", label: "Status", icon: <HelpIcon />, color: "info" },
  ];

  return (
    <Paper elevation={1} sx={{ p: 2 }}>
      <Grid container spacing={1}>
        {actions
          .filter((action) => !action.showOnlyInCombat || isInCombat)
          .map((action) => (
            <Grid item xs={6} sm={4} md={2} key={action.id}>
              <Button
                fullWidth
                variant="outlined"
                color={action.color}
                startIcon={action.icon}
                onClick={() => onAction(action.id)}
                disabled={disabled}
                size="small"
              >
                {action.label}
              </Button>
            </Grid>
          ))}
      </Grid>
    </Paper>
  );
}

export default ActionButtons;
