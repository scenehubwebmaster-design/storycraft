import React, { useState } from "react";
import {
  Box,
  Paper,
  Typography,
  Button,
  TextField,
  Stack,
  Chip,
  IconButton,
  Tooltip,
  Autocomplete,
  Divider,
  Alert,
} from "@mui/material";
import {
  LocalFireDepartment as FireballIcon,
  Bolt as AttackIcon,
  Healing as HealIcon,
  Shield as ShieldIcon,
  Psychology as SpellIcon,
  Accessibility as ActionIcon,
  DirectionsRun as DashIcon,
  Visibility as SearchIcon,
  Casino as RollIcon,
} from "@mui/icons-material";

/**
 * CombatActionPanel - Quick combat action buttons and damage/healing tracking
 * Provides one-click actions for common D&D combat activities
 */
const CombatActionPanel = ({
  campaignId,
  party = [],
  onDamage,
  onHeal,
  onAction,
  onDiceRoll,
}) => {
  const [selectedCharacter, setSelectedCharacter] = useState(null);
  const [damageAmount, setDamageAmount] = useState("");
  const [healAmount, setHealAmount] = useState("");
  const [feedback, setFeedback] = useState(null);

  // Apply damage to selected character
  const handleDamage = async () => {
    if (!selectedCharacter || !damageAmount) return;

    try {
      const response = await fetch(
        `http://localhost:8000/api/campaigns/${campaignId}/combat/damage`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            character_id: selectedCharacter.character_id,
            damage: parseInt(damageAmount),
            damage_type: "normal",
          }),
        }
      );

      if (response.ok) {
        const result = await response.json();
        setFeedback({
          type: "damage",
          message: `${result.character_name} takes ${result.damage_taken} damage! (${result.current_hp}/${result.max_hp} HP)`,
          severity: result.status === "unconscious" ? "error" : "warning",
        });
        setDamageAmount("");
        onDamage && onDamage(result);
      }
    } catch (error) {
      console.error("Error applying damage:", error);
      setFeedback({
        type: "error",
        message: "Failed to apply damage",
        severity: "error",
      });
    }
  };

  // Apply healing to selected character
  const handleHeal = async () => {
    if (!selectedCharacter || !healAmount) return;

    try {
      const response = await fetch(
        `http://localhost:8000/api/campaigns/${campaignId}/combat/heal`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            character_id: selectedCharacter.character_id,
            healing: parseInt(healAmount),
          }),
        }
      );

      if (response.ok) {
        const result = await response.json();
        setFeedback({
          type: "heal",
          message: `${result.character_name} regains ${result.healing_received} HP! (${result.current_hp}/${result.max_hp} HP)`,
          severity: "success",
        });
        setHealAmount("");
        onHeal && onHeal(result);
      }
    } catch (error) {
      console.error("Error applying healing:", error);
      setFeedback({
        type: "error",
        message: "Failed to apply healing",
        severity: "error",
      });
    }
  };

  // Quick action buttons
  const quickActions = [
    { label: "Attack", icon: <AttackIcon />, action: "attack", color: "error" },
    {
      label: "Cast Spell",
      icon: <SpellIcon />,
      action: "spell",
      color: "secondary",
    },
    { label: "Dash", icon: <DashIcon />, action: "dash", color: "info" },
    { label: "Dodge", icon: <ShieldIcon />, action: "dodge", color: "warning" },
    { label: "Help", icon: <ActionIcon />, action: "help", color: "success" },
    {
      label: "Search",
      icon: <SearchIcon />,
      action: "search",
      color: "default",
    },
  ];

  // Handle quick action click
  const handleQuickAction = (action) => {
    if (!selectedCharacter) {
      setFeedback({
        type: "warning",
        message: "Please select a character first",
        severity: "warning",
      });
      return;
    }

    onAction &&
      onAction({
        character: selectedCharacter,
        action,
      });
  };

  return (
    <Paper sx={{ p: 2, height: "100%" }}>
      <Typography
        variant="h6"
        gutterBottom
        sx={{ display: "flex", alignItems: "center", gap: 1 }}
      >
        ⚔️ Combat Actions
      </Typography>

      <Stack spacing={2}>
        {/* Character Selection */}
        <Autocomplete
          options={party}
          getOptionLabel={(option) => option.name}
          value={selectedCharacter}
          onChange={(e, value) => {
            setSelectedCharacter(value);
            setFeedback(null);
          }}
          renderInput={(params) => (
            <TextField {...params} label="Select Character" size="small" />
          )}
          renderOption={(props, option) => (
            <li {...props}>
              <Box
                sx={{
                  display: "flex",
                  alignItems: "center",
                  gap: 1,
                  width: "100%",
                }}
              >
                <Typography variant="body2">{option.name}</Typography>
                <Chip
                  label={`${option.current_hp}/${option.max_hp}`}
                  size="small"
                  color={
                    option.current_hp > option.max_hp * 0.5
                      ? "success"
                      : "error"
                  }
                />
              </Box>
            </li>
          )}
        />

        {/* Selected Character Info */}
        {selectedCharacter && (
          <Paper sx={{ p: 1.5, bgcolor: "action.hover" }}>
            <Typography variant="subtitle2">
              {selectedCharacter.name}
            </Typography>
            <Box sx={{ display: "flex", gap: 2, mt: 0.5 }}>
              <Typography variant="caption">
                HP: {selectedCharacter.current_hp}/{selectedCharacter.max_hp}
              </Typography>
              <Typography variant="caption">
                AC: {selectedCharacter.armor_class}
              </Typography>
            </Box>
          </Paper>
        )}

        {/* Feedback Alert */}
        {feedback && (
          <Alert severity={feedback.severity} onClose={() => setFeedback(null)}>
            {feedback.message}
          </Alert>
        )}

        <Divider />

        {/* Damage Input */}
        <Box>
          <Typography variant="subtitle2" gutterBottom>
            Apply Damage
          </Typography>
          <Box sx={{ display: "flex", gap: 1 }}>
            <TextField
              type="number"
              value={damageAmount}
              onChange={(e) => setDamageAmount(e.target.value)}
              placeholder="Damage"
              size="small"
              sx={{ flex: 1 }}
              inputProps={{ min: 0 }}
            />
            <Button
              variant="contained"
              color="error"
              onClick={handleDamage}
              disabled={!selectedCharacter || !damageAmount}
            >
              Damage
            </Button>
            <IconButton
              color="primary"
              onClick={() => onDiceRoll && onDiceRoll("damage")}
              size="small"
            >
              <RollIcon />
            </IconButton>
          </Box>
        </Box>

        {/* Healing Input */}
        <Box>
          <Typography variant="subtitle2" gutterBottom>
            Apply Healing
          </Typography>
          <Box sx={{ display: "flex", gap: 1 }}>
            <TextField
              type="number"
              value={healAmount}
              onChange={(e) => setHealAmount(e.target.value)}
              placeholder="Healing"
              size="small"
              sx={{ flex: 1 }}
              inputProps={{ min: 0 }}
            />
            <Button
              variant="contained"
              color="success"
              onClick={handleHeal}
              disabled={!selectedCharacter || !healAmount}
            >
              Heal
            </Button>
            <IconButton
              color="primary"
              onClick={() => onDiceRoll && onDiceRoll("healing")}
              size="small"
            >
              <RollIcon />
            </IconButton>
          </Box>
        </Box>

        <Divider />

        {/* Quick Actions */}
        <Box>
          <Typography variant="subtitle2" gutterBottom>
            Quick Actions
          </Typography>
          <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
            {quickActions.map((action) => (
              <Tooltip key={action.action} title={action.label}>
                <Button
                  variant="outlined"
                  size="small"
                  color={action.color}
                  startIcon={action.icon}
                  onClick={() => handleQuickAction(action.action)}
                  disabled={!selectedCharacter}
                  sx={{ mb: 1 }}
                >
                  {action.label}
                </Button>
              </Tooltip>
            ))}
          </Stack>
        </Box>

        {/* Common Spell Quick Rolls */}
        <Box>
          <Typography variant="subtitle2" gutterBottom>
            Common Spells
          </Typography>
          <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
            <Button
              variant="outlined"
              size="small"
              startIcon={<FireballIcon />}
              onClick={() => {
                setDamageAmount("28"); // 8d6 average
                onDiceRoll && onDiceRoll("fireball");
              }}
              sx={{ mb: 1 }}
            >
              Fireball
            </Button>
            <Button
              variant="outlined"
              size="small"
              color="success"
              startIcon={<HealIcon />}
              onClick={() => {
                setHealAmount("7"); // 1d8+3 average
                onDiceRoll && onDiceRoll("cure_wounds");
              }}
              sx={{ mb: 1 }}
            >
              Cure Wounds
            </Button>
          </Stack>
        </Box>
      </Stack>
    </Paper>
  );
};

export default CombatActionPanel;
