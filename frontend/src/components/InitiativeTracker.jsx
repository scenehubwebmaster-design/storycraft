import React, { useState, useEffect } from "react";
import {
  Box,
  Paper,
  Typography,
  List,
  ListItem,
  ListItemAvatar,
  ListItemText,
  Avatar,
  IconButton,
  LinearProgress,
  Chip,
  Button,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Stack,
  Divider,
  Tooltip,
} from "@mui/material";
import {
  NavigateNext as NextTurnIcon,
  Casino as DiceIcon,
  Favorite as HeartIcon,
  Shield as ShieldIcon,
  Close as CloseIcon,
  Edit as EditIcon,
  PlayArrow as StartIcon,
  Stop as StopIcon,
} from "@mui/icons-material";
import { API_URL } from "../config/api";

/**
 * InitiativeTracker - D&D combat initiative order display and management
 * Shows turn order, current turn, HP tracking, and quick actions
 */
const InitiativeTracker = ({
  campaignId,
  isActive,
  onCombatStart,
  onCombatEnd,
}) => {
  const [initiative, setInitiative] = useState([]);
  const [currentTurn, setCurrentTurn] = useState(0);
  const [roundNumber, setRoundNumber] = useState(1);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [party, setParty] = useState([]);

  // Fetch party for initiative setup
  useEffect(() => {
    const fetchParty = async () => {
      if (!campaignId) return;

      try {
        const response = await fetch(
          `${API_URL}/api/campaigns/${campaignId}/party`
        );
        if (response.ok) {
          const data = await response.json();
          setParty(data);

          // Auto-populate initiative if not set
          if (initiative.length === 0 && data.length > 0) {
            const tempInitiative = data.map((member) => ({
              character_id: member.character_id,
              character_name: member.name,
              initiative: 10, // Default roll
              current_hp: member.current_hp,
              max_hp: member.max_hp,
              ac: member.armor_class,
              conditions: member.conditions || [],
              portrait_image: member.portrait_image,
            }));
            setInitiative(tempInitiative);
          }
        }
      } catch (error) {
        console.error("Error fetching party:", error);
      }
    };

    fetchParty();
  }, [campaignId]);

  // Roll initiative for a character
  const rollInitiative = (characterId, modifier = 0) => {
    const roll = Math.floor(Math.random() * 20) + 1;
    const total = roll + modifier;

    setInitiative(
      (prev) =>
        prev
          .map((entry) =>
            entry.character_id === characterId
              ? { ...entry, initiative: total }
              : entry
          )
          .sort((a, b) => b.initiative - a.initiative) // Sort by initiative descending
    );

    return total;
  };

  // Start combat and send initiative to server
  const handleStartCombat = async () => {
    try {
      // Start combat mode
      await fetch(`${API_URL}/api/campaigns/${campaignId}/combat/start`, {
        method: "POST",
      });

      // Send initiative order to server
      await fetch(`${API_URL}/api/campaigns/${campaignId}/combat/initiative`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(initiative),
      });

      setCurrentTurn(0);
      setRoundNumber(1);
      onCombatStart && onCombatStart();
    } catch (error) {
      console.error("Error starting combat:", error);
    }
  };

  // End combat
  const handleEndCombat = async () => {
    try {
      await fetch(`${API_URL}/api/campaigns/${campaignId}/combat/end`, {
        method: "POST",
      });

      setCurrentTurn(0);
      setRoundNumber(1);
      onCombatEnd && onCombatEnd();
    } catch (error) {
      console.error("Error ending combat:", error);
    }
  };

  // Next turn
  const handleNextTurn = () => {
    if (currentTurn === initiative.length - 1) {
      setCurrentTurn(0);
      setRoundNumber((prev) => prev + 1);
    } else {
      setCurrentTurn((prev) => prev + 1);
    }
  };

  // Get HP color
  const getHpColor = (current, max) => {
    const percentage = (current / max) * 100;
    if (percentage > 75) return "success";
    if (percentage > 50) return "info";
    if (percentage > 25) return "warning";
    return "error";
  };

  if (!isActive) {
    return (
      <Paper sx={{ p: 3, textAlign: "center" }}>
        <Typography variant="h6" gutterBottom>
          ⚔️ Combat Tracker
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
          Start combat to track initiative and turns
        </Typography>
        <Button
          variant="contained"
          startIcon={<DiceIcon />}
          onClick={() => setEditDialogOpen(true)}
          disabled={party.length === 0}
        >
          Roll Initiative & Start Combat
        </Button>

        {/* Initiative Setup Dialog */}
        <Dialog
          open={editDialogOpen}
          onClose={() => setEditDialogOpen(false)}
          maxWidth="sm"
          fullWidth
        >
          <DialogTitle>Roll Initiative</DialogTitle>
          <DialogContent>
            <List>
              {party.map((member) => {
                const entry = initiative.find(
                  (e) => e.character_id === member.character_id
                );
                const initiativeMod = parseInt(
                  member.initiative?.replace("+", "") || 0
                );

                return (
                  <ListItem key={member.character_id} divider>
                    <ListItemAvatar>
                      <Avatar
                        src={
                          member.portrait_image
                            ? `data:image/png;base64,${member.portrait_image}`
                            : null
                        }
                      >
                        {member.name.charAt(0)}
                      </Avatar>
                    </ListItemAvatar>
                    <ListItemText
                      primary={member.name}
                      secondary={`Initiative modifier: ${
                        member.initiative || "+0"
                      }`}
                    />
                    <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                      <TextField
                        type="number"
                        value={entry?.initiative || 10}
                        onChange={(e) => {
                          setInitiative((prev) =>
                            prev.map((i) =>
                              i.character_id === member.character_id
                                ? {
                                    ...i,
                                    initiative: parseInt(e.target.value) || 0,
                                  }
                                : i
                            )
                          );
                        }}
                        size="small"
                        sx={{ width: 80 }}
                      />
                      <IconButton
                        color="primary"
                        onClick={() =>
                          rollInitiative(member.character_id, initiativeMod)
                        }
                      >
                        <DiceIcon />
                      </IconButton>
                    </Box>
                  </ListItem>
                );
              })}
            </List>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setEditDialogOpen(false)}>Cancel</Button>
            <Button
              variant="contained"
              startIcon={<StartIcon />}
              onClick={() => {
                setEditDialogOpen(false);
                handleStartCombat();
              }}
            >
              Start Combat
            </Button>
          </DialogActions>
        </Dialog>
      </Paper>
    );
  }

  return (
    <Paper sx={{ height: "100%", display: "flex", flexDirection: "column" }}>
      {/* Header */}
      <Box sx={{ p: 2, borderBottom: 1, borderColor: "divider" }}>
        <Box
          sx={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
          }}
        >
          <Typography variant="h6">⚔️ Combat - Round {roundNumber}</Typography>
          <Button
            variant="outlined"
            color="error"
            size="small"
            startIcon={<StopIcon />}
            onClick={handleEndCombat}
          >
            End Combat
          </Button>
        </Box>
      </Box>

      {/* Initiative List */}
      <Box sx={{ flex: 1, overflow: "auto" }}>
        <List sx={{ p: 0 }}>
          {initiative.map((entry, index) => {
            const isCurrentTurn = index === currentTurn;
            const hpPercentage = (entry.current_hp / entry.max_hp) * 100;

            return (
              <React.Fragment key={entry.character_id}>
                <ListItem
                  sx={{
                    bgcolor: isCurrentTurn ? "action.selected" : "transparent",
                    borderLeft: isCurrentTurn ? 4 : 0,
                    borderColor: "primary.main",
                    transition: "all 0.3s",
                  }}
                >
                  <ListItemAvatar>
                    <Box sx={{ position: "relative" }}>
                      <Avatar
                        src={
                          entry.portrait_image
                            ? `data:image/png;base64,${entry.portrait_image}`
                            : null
                        }
                        sx={{
                          width: 48,
                          height: 48,
                          border: isCurrentTurn ? 2 : 0,
                          borderColor: "primary.main",
                        }}
                      >
                        {entry.character_name.charAt(0)}
                      </Avatar>
                      <Chip
                        label={entry.initiative}
                        size="small"
                        color="primary"
                        sx={{
                          position: "absolute",
                          bottom: -4,
                          right: -4,
                          height: 20,
                          fontSize: 10,
                        }}
                      />
                    </Box>
                  </ListItemAvatar>

                  <ListItemText
                    primary={
                      <Box
                        sx={{ display: "flex", alignItems: "center", gap: 1 }}
                      >
                        <Typography variant="subtitle2">
                          {entry.character_name}
                        </Typography>
                        {isCurrentTurn && (
                          <Chip
                            label="CURRENT TURN"
                            size="small"
                            color="primary"
                          />
                        )}
                      </Box>
                    }
                    secondary={
                      <Box sx={{ mt: 0.5 }}>
                        {/* HP Bar */}
                        <Box
                          sx={{
                            display: "flex",
                            alignItems: "center",
                            gap: 1,
                            mb: 0.5,
                          }}
                        >
                          <HeartIcon sx={{ fontSize: 14 }} />
                          <Typography variant="caption">
                            {entry.current_hp}/{entry.max_hp}
                          </Typography>
                          <ShieldIcon sx={{ fontSize: 14, ml: 1 }} />
                          <Typography variant="caption">
                            AC {entry.ac}
                          </Typography>
                        </Box>
                        <LinearProgress
                          variant="determinate"
                          value={hpPercentage}
                          color={getHpColor(entry.current_hp, entry.max_hp)}
                          sx={{ height: 6, borderRadius: 1 }}
                        />

                        {/* Conditions */}
                        {entry.conditions.length > 0 && (
                          <Box
                            sx={{
                              mt: 0.5,
                              display: "flex",
                              gap: 0.5,
                              flexWrap: "wrap",
                            }}
                          >
                            {entry.conditions.map((condition, idx) => (
                              <Chip
                                key={idx}
                                label={condition}
                                size="small"
                                color="warning"
                              />
                            ))}
                          </Box>
                        )}
                      </Box>
                    }
                  />
                </ListItem>
                {index < initiative.length - 1 && <Divider />}
              </React.Fragment>
            );
          })}
        </List>
      </Box>

      {/* Footer - Next Turn Button */}
      <Box sx={{ p: 2, borderTop: 1, borderColor: "divider" }}>
        <Button
          variant="contained"
          fullWidth
          size="large"
          endIcon={<NextTurnIcon />}
          onClick={handleNextTurn}
        >
          Next Turn
          {currentTurn === initiative.length - 1 ? " (New Round)" : ""}
        </Button>
      </Box>
    </Paper>
  );
};

export default InitiativeTracker;
