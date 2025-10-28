import React, { useState, useEffect } from "react";
import {
  Box,
  Paper,
  Typography,
  Button,
  ButtonGroup,
  Chip,
  Stack,
  Dialog,
  DialogTitle,
  DialogContent,
  TextField,
  IconButton,
  Fade,
  Zoom,
  FormControlLabel,
  Checkbox,
} from "@mui/material";
import {
  Casino as DiceIcon,
  Add as AddIcon,
  Remove as RemoveIcon,
  Close as CloseIcon,
} from "@mui/icons-material";

/**
 * DiceRoller - D&D dice rolling panel with animated results
 * Supports standard D&D dice (d4, d6, d8, d10, d12, d20, d100)
 * Shows roll history and allows modifiers
 * Integrates with character stats for skill checks
 * Auto-sends results to DM
 */
const DiceRoller = ({
  open,
  onClose,
  onRollComplete,
  activeCharacters = [],
  onSendRollToDM,
  // Optional: prefill and auto-roll when opened
  initialDice = "d20",
  initialCount = 1,
  initialModifier = 0,
  initialCharacter = null, // object with character details
  initialSkillName = null,
  autoRollOnOpen = false,
}) => {
  const [selectedDice, setSelectedDice] = useState("d20");
  const [diceCount, setDiceCount] = useState(1);
  const [modifier, setModifier] = useState(0);
  const [rollHistory, setRollHistory] = useState([]);
  const [isRolling, setIsRolling] = useState(false);
  const [lastRoll, setLastRoll] = useState(null);
  const [selectedCharacter, setSelectedCharacter] = useState(null);
  const [selectedSkill, setSelectedSkill] = useState(null);
  const [autoSendEnabled, setAutoSendEnabled] = useState(true);

  // D&D 5e skills with their associated ability scores
  const skills = [
    { name: "Acrobatics", ability: "dexterity", icon: "🤸" },
    { name: "Animal Handling", ability: "wisdom", icon: "🐴" },
    { name: "Arcana", ability: "intelligence", icon: "✨" },
    { name: "Athletics", ability: "strength", icon: "💪" },
    { name: "Deception", ability: "charisma", icon: "🎭" },
    { name: "History", ability: "intelligence", icon: "📜" },
    { name: "Insight", ability: "wisdom", icon: "👁️" },
    { name: "Intimidation", ability: "charisma", icon: "😠" },
    { name: "Investigation", ability: "intelligence", icon: "🔍" },
    { name: "Medicine", ability: "wisdom", icon: "🏥" },
    { name: "Nature", ability: "intelligence", icon: "🌿" },
    { name: "Perception", ability: "wisdom", icon: "👀" },
    { name: "Performance", ability: "charisma", icon: "🎪" },
    { name: "Persuasion", ability: "charisma", icon: "🗣️" },
    { name: "Religion", ability: "intelligence", icon: "⛪" },
    { name: "Sleight of Hand", ability: "dexterity", icon: "🃏" },
    { name: "Stealth", ability: "dexterity", icon: "🥷" },
    { name: "Survival", ability: "wisdom", icon: "🏕️" },
  ];

  // Calculate modifier based on character and skill selection
  const calculateModifier = (character, skill) => {
    if (!character || !skill) return 0;

    const abilityModifiers = character.ability_modifiers || {};
    const baseModifier =
      abilityModifiers[skill.ability] ||
      abilityModifiers[
        skill.ability.charAt(0).toUpperCase() + skill.ability.slice(1)
      ] ||
      0;

    // Check if character is proficient in this skill
    const proficiencyBonus = character.proficiency_bonus || 2;
    const skills = character.skills || {};
    const skillKey = skill.name.toLowerCase().replace(/\s+/g, "_");
    const isProficient = skills[skillKey] === true || skills[skillKey] > 0;

    return isProficient ? baseModifier + proficiencyBonus : baseModifier;
  };

  // Update modifier when character or skill changes
  useEffect(() => {
    if (selectedCharacter && selectedSkill) {
      const calculatedMod = calculateModifier(selectedCharacter, selectedSkill);
      setModifier(calculatedMod);
    }
  }, [selectedCharacter, selectedSkill]);

  // If the modal is opened with initial values and autoRollOnOpen is true,
  // prefill the fields and trigger a roll automatically.
  useEffect(() => {
    if (!open) return;

    // Prefill values
    setSelectedDice(initialDice || "d20");
    setDiceCount(initialCount || 1);
    setModifier(initialModifier || 0);

    if (initialCharacter) setSelectedCharacter(initialCharacter);
    if (initialSkillName) {
      const skillObj = skills.find(
        (s) => s.name.toLowerCase() === initialSkillName.toLowerCase()
      );
      if (skillObj) setSelectedSkill(skillObj);
    }

    if (autoRollOnOpen) {
      // Slight delay to allow state to settle and render for animation
      const t = setTimeout(() => {
        rollDice();
      }, 220);
      return () => clearTimeout(t);
    }
  }, [
    open,
    initialDice,
    initialCount,
    initialModifier,
    initialCharacter,
    initialSkillName,
    autoRollOnOpen,
  ]);

  const diceTypes = [
    { type: "d4", sides: 4, color: "#4caf50" },
    { type: "d6", sides: 6, color: "#2196f3" },
    { type: "d8", sides: 8, color: "#9c27b0" },
    { type: "d10", sides: 10, color: "#ff9800" },
    { type: "d12", sides: 12, color: "#f44336" },
    { type: "d20", sides: 20, color: "#e91e63" },
    { type: "d100", sides: 100, color: "#3f51b5" },
  ];

  // Roll dice
  const rollDice = () => {
    setIsRolling(true);

    const dice = diceTypes.find((d) => d.type === selectedDice);
    const rolls = [];

    // Roll each die
    for (let i = 0; i < diceCount; i++) {
      rolls.push(Math.floor(Math.random() * dice.sides) + 1);
    }

    const total = rolls.reduce((sum, roll) => sum + roll, 0);
    const finalTotal = total + modifier;

    const rollResult = {
      dice: selectedDice,
      count: diceCount,
      rolls,
      total,
      modifier,
      finalTotal,
      timestamp: new Date(),
      isCritical: selectedDice === "d20" && rolls[0] === 20,
      isCriticalFail: selectedDice === "d20" && rolls[0] === 1,
      character: selectedCharacter?.name,
      skill: selectedSkill?.name,
    };

    // Animate the roll
    setTimeout(() => {
      setLastRoll(rollResult);
      setRollHistory((prev) => [rollResult, ...prev.slice(0, 9)]); // Keep last 10 rolls
      setIsRolling(false);

      // Callback with result
      onRollComplete && onRollComplete(rollResult);

      // Auto-send to DM if enabled
      if (autoSendEnabled && onSendRollToDM) {
        const rollMessage = formatRollMessage(rollResult);
        onSendRollToDM(rollMessage);
      }
    }, 500);
  };

  // Format roll result as a message for the DM
  const formatRollMessage = (rollResult) => {
    const characterName = rollResult.character || "I";
    const skillText = rollResult.skill ? ` ${rollResult.skill} check` : "";
    const diceText = `${rollResult.count}${rollResult.dice}`;
    const modText =
      rollResult.modifier !== 0
        ? ` ${rollResult.modifier > 0 ? "+" : ""}${rollResult.modifier}`
        : "";

    let message = `${characterName} rolled${skillText}: **${rollResult.finalTotal}**`;
    message += `\n\n🎲 ${diceText}${modText}`;
    message += `\nRolls: ${rollResult.rolls.join(", ")}`;

    if (rollResult.modifier !== 0) {
      message += `\nModifier: ${rollResult.modifier > 0 ? "+" : ""}${
        rollResult.modifier
      }`;
    }

    if (rollResult.isCritical) {
      message += "\n\n🎉 **CRITICAL SUCCESS!**";
    } else if (rollResult.isCriticalFail) {
      message += "\n\n💀 **CRITICAL FAILURE!**";
    }

    return message;
  };

  // Quick roll shortcuts
  const quickRoll = (type, count = 1, mod = 0) => {
    setSelectedDice(type);
    setDiceCount(count);
    setModifier(mod);
    setTimeout(rollDice, 100);
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>
        <Box
          sx={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
          }}
        >
          <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
            <DiceIcon />
            <Typography variant="h6">Dice Roller</Typography>
          </Box>
          <IconButton onClick={onClose}>
            <CloseIcon />
          </IconButton>
        </Box>
      </DialogTitle>

      <DialogContent>
        <Stack spacing={3}>
          {/* Character & Skill Selection */}
          {activeCharacters && activeCharacters.length > 0 && (
            <>
              <Box>
                <Typography variant="subtitle2" gutterBottom>
                  Rolling Character
                </Typography>
                <ButtonGroup fullWidth size="small">
                  {activeCharacters.map((char) => (
                    <Button
                      key={char.id}
                      variant={
                        selectedCharacter?.id === char.id
                          ? "contained"
                          : "outlined"
                      }
                      onClick={() => setSelectedCharacter(char)}
                    >
                      {char.name}
                    </Button>
                  ))}
                </ButtonGroup>
              </Box>

              {selectedCharacter && (
                <Box>
                  <Typography variant="subtitle2" gutterBottom>
                    Skill Check (Auto-calculates modifier)
                  </Typography>
                  <Box
                    sx={{
                      display: "grid",
                      gridTemplateColumns: "repeat(3, 1fr)",
                      gap: 1,
                    }}
                  >
                    {skills.map((skill) => (
                      <Button
                        key={skill.name}
                        variant={
                          selectedSkill?.name === skill.name
                            ? "contained"
                            : "outlined"
                        }
                        size="small"
                        onClick={() => setSelectedSkill(skill)}
                        sx={{
                          fontSize: "0.75rem",
                          textTransform: "none",
                        }}
                      >
                        {skill.icon} {skill.name}
                      </Button>
                    ))}
                  </Box>
                  {selectedSkill && (
                    <Typography
                      variant="caption"
                      color="primary"
                      sx={{ mt: 1, display: "block" }}
                    >
                      Modifier: +
                      {calculateModifier(selectedCharacter, selectedSkill)} (
                      {selectedSkill.ability})
                    </Typography>
                  )}
                </Box>
              )}
            </>
          )}

          {/* Dice Selection */}
          <Box>
            <Typography variant="subtitle2" gutterBottom>
              Select Dice Type
            </Typography>
            <ButtonGroup fullWidth>
              {diceTypes.map((dice) => (
                <Button
                  key={dice.type}
                  variant={
                    selectedDice === dice.type ? "contained" : "outlined"
                  }
                  onClick={() => setSelectedDice(dice.type)}
                  sx={{
                    bgcolor:
                      selectedDice === dice.type ? dice.color : "transparent",
                    borderColor: dice.color,
                    color: selectedDice === dice.type ? "white" : dice.color,
                    "&:hover": {
                      bgcolor:
                        selectedDice === dice.type
                          ? dice.color
                          : `${dice.color}20`,
                    },
                  }}
                >
                  {dice.type}
                </Button>
              ))}
            </ButtonGroup>
          </Box>

          {/* Dice Count */}
          <Box>
            <Typography variant="subtitle2" gutterBottom>
              Number of Dice
            </Typography>
            <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
              <IconButton
                onClick={() => setDiceCount((prev) => Math.max(1, prev - 1))}
                disabled={diceCount <= 1}
              >
                <RemoveIcon />
              </IconButton>
              <TextField
                type="number"
                value={diceCount}
                onChange={(e) =>
                  setDiceCount(
                    Math.max(1, Math.min(20, parseInt(e.target.value) || 1))
                  )
                }
                sx={{ width: 80 }}
                inputProps={{ min: 1, max: 20, style: { textAlign: "center" } }}
              />
              <IconButton
                onClick={() => setDiceCount((prev) => Math.min(20, prev + 1))}
                disabled={diceCount >= 20}
              >
                <AddIcon />
              </IconButton>
              <Typography variant="body2" color="text.secondary" sx={{ ml: 2 }}>
                {diceCount}
                {selectedDice}
              </Typography>
            </Box>
          </Box>

          {/* Modifier */}
          <Box>
            <Typography variant="subtitle2" gutterBottom>
              Modifier
            </Typography>
            <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
              <IconButton onClick={() => setModifier((prev) => prev - 1)}>
                <RemoveIcon />
              </IconButton>
              <TextField
                type="number"
                value={modifier}
                onChange={(e) => setModifier(parseInt(e.target.value) || 0)}
                sx={{ width: 80 }}
                inputProps={{ style: { textAlign: "center" } }}
              />
              <IconButton onClick={() => setModifier((prev) => prev + 1)}>
                <AddIcon />
              </IconButton>
            </Box>
          </Box>

          {/* Roll Button */}
          <Box>
            <Button
              variant="contained"
              size="large"
              fullWidth
              startIcon={<DiceIcon />}
              onClick={rollDice}
              disabled={isRolling}
              sx={{
                py: 2,
                fontSize: 18,
                fontWeight: "bold",
              }}
            >
              {isRolling
                ? "Rolling..."
                : `Roll ${diceCount}${selectedDice}${
                    modifier !== 0
                      ? ` ${modifier > 0 ? "+" : ""}${modifier}`
                      : ""
                  }`}
            </Button>

            {/* Auto-send toggle */}
            <FormControlLabel
              control={
                <Checkbox
                  checked={autoSendEnabled}
                  onChange={(e) => setAutoSendEnabled(e.target.checked)}
                  size="small"
                />
              }
              label={
                <Typography variant="caption">
                  Automatically send roll result to DM
                </Typography>
              }
              sx={{ mt: 1 }}
            />
          </Box>

          {/* Last Roll Result */}
          {lastRoll && (
            <Zoom in>
              <Paper
                sx={{
                  p: 3,
                  textAlign: "center",
                  bgcolor: lastRoll.isCritical
                    ? "success.dark"
                    : lastRoll.isCriticalFail
                    ? "error.dark"
                    : "primary.dark",
                  color: "white",
                }}
              >
                <Typography variant="h2" fontWeight="bold">
                  {lastRoll.finalTotal}
                </Typography>
                <Typography variant="body2" sx={{ mt: 1 }}>
                  {lastRoll.rolls.join(" + ")}
                  {lastRoll.modifier !== 0 &&
                    ` ${lastRoll.modifier > 0 ? "+" : ""}${lastRoll.modifier}`}
                  {" = "}
                  {lastRoll.finalTotal}
                </Typography>
                {lastRoll.isCritical && (
                  <Chip label="CRITICAL HIT!" color="success" sx={{ mt: 1 }} />
                )}
                {lastRoll.isCriticalFail && (
                  <Chip label="CRITICAL FAIL!" color="error" sx={{ mt: 1 }} />
                )}
              </Paper>
            </Zoom>
          )}

          {/* Quick Roll Buttons */}
          <Box>
            <Typography variant="subtitle2" gutterBottom>
              Quick Rolls
            </Typography>
            <Stack direction="row" spacing={1} flexWrap="wrap">
              <Button
                variant="outlined"
                size="small"
                onClick={() => quickRoll("d20", 1, 0)}
              >
                D20
              </Button>
              <Button
                variant="outlined"
                size="small"
                onClick={() => quickRoll("d20", 1, 5)}
              >
                D20 + 5
              </Button>
              <Button
                variant="outlined"
                size="small"
                onClick={() => quickRoll("d6", 2, 0)}
              >
                2D6
              </Button>
              <Button
                variant="outlined"
                size="small"
                onClick={() => quickRoll("d8", 1, 3)}
              >
                1D8 + 3
              </Button>
              <Button
                variant="outlined"
                size="small"
                onClick={() => quickRoll("d6", 8, 0)}
              >
                Fireball (8D6)
              </Button>
            </Stack>
          </Box>

          {/* Roll History */}
          {rollHistory.length > 0 && (
            <Box>
              <Typography variant="subtitle2" gutterBottom>
                Roll History
              </Typography>
              <Stack spacing={1}>
                {rollHistory.map((roll, index) => (
                  <Fade in key={index}>
                    <Paper sx={{ p: 1.5, bgcolor: "action.hover" }}>
                      <Box
                        sx={{
                          display: "flex",
                          justifyContent: "space-between",
                          alignItems: "center",
                        }}
                      >
                        <Typography variant="body2">
                          {roll.count}
                          {roll.dice}
                          {roll.modifier !== 0 &&
                            ` ${roll.modifier > 0 ? "+" : ""}${roll.modifier}`}
                        </Typography>
                        <Chip
                          label={roll.finalTotal}
                          color={
                            roll.isCritical
                              ? "success"
                              : roll.isCriticalFail
                              ? "error"
                              : "default"
                          }
                          size="small"
                        />
                      </Box>
                      <Typography variant="caption" color="text.secondary">
                        {roll.rolls.join(", ")}
                      </Typography>
                    </Paper>
                  </Fade>
                ))}
              </Stack>
            </Box>
          )}
        </Stack>
      </DialogContent>
    </Dialog>
  );
};

export default DiceRoller;
