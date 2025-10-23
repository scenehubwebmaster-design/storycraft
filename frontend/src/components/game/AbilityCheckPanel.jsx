import React, { useState } from "react";
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
  IconButton,
  Avatar,
  Divider,
  Tooltip,
  Grid,
  Card,
  CardContent,
  Fade,
  TextField,
  ToggleButtonGroup,
  ToggleButton,
  List,
  ListItem,
  ListItemText,
  Badge,
  Tabs,
  Tab,
} from "@mui/material";
import {
  Close as CloseIcon,
  FitnessCenter as StrengthIcon,
  DirectionsRun as DexterityIcon,
  Favorite as ConstitutionIcon,
  Psychology as IntelligenceIcon,
  Lightbulb as WisdomIcon,
  RecordVoiceOver as CharismaIcon,
  Casino as DiceIcon,
  TrendingUp as AdvantageIcon,
  TrendingDown as DisadvantageIcon,
  Shield as ShieldIcon,
  Group as GroupIcon,
  History as HistoryIcon,
  Add as AddIcon,
  Remove as RemoveIcon,
} from "@mui/icons-material";

/**
 * AbilityCheckPanel - Character-aware ability check roller
 *
 * Features:
 * - Multi-character selection
 * - Automatic modifier calculation from character stats
 * - Skill proficiency bonuses
 * - Visual feedback for critical success/failure
 * - Formatted output for LLM to auto-calculate pass/fail
 */

const ABILITIES = [
  { key: "strength", label: "Strength", icon: StrengthIcon, color: "#f44336" },
  {
    key: "dexterity",
    label: "Dexterity",
    icon: DexterityIcon,
    color: "#4caf50",
  },
  {
    key: "constitution",
    label: "Constitution",
    icon: ConstitutionIcon,
    color: "#ff9800",
  },
  {
    key: "intelligence",
    label: "Intelligence",
    icon: IntelligenceIcon,
    color: "#2196f3",
  },
  { key: "wisdom", label: "Wisdom", icon: WisdomIcon, color: "#9c27b0" },
  { key: "charisma", label: "Charisma", icon: CharismaIcon, color: "#e91e63" },
];

const SKILLS = {
  strength: [{ key: "athletics", label: "Athletics" }],
  dexterity: [
    { key: "acrobatics", label: "Acrobatics" },
    { key: "sleight_of_hand", label: "Sleight of Hand" },
    { key: "stealth", label: "Stealth" },
  ],
  intelligence: [
    { key: "arcana", label: "Arcana" },
    { key: "history", label: "History" },
    { key: "investigation", label: "Investigation" },
    { key: "nature", label: "Nature" },
    { key: "religion", label: "Religion" },
  ],
  wisdom: [
    { key: "animal_handling", label: "Animal Handling" },
    { key: "insight", label: "Insight" },
    { key: "medicine", label: "Medicine" },
    { key: "perception", label: "Perception" },
    { key: "survival", label: "Survival" },
  ],
  charisma: [
    { key: "deception", label: "Deception" },
    { key: "intimidation", label: "Intimidation" },
    { key: "performance", label: "Performance" },
    { key: "persuasion", label: "Persuasion" },
  ],
};

const AbilityCheckPanel = ({
  open,
  onClose,
  characters = [],
  onCheckComplete,
}) => {
  // Selection state
  const [selectedCharacters, setSelectedCharacters] = useState([]); // Multi-select for group checks
  const [selectedAbility, setSelectedAbility] = useState(null);
  const [selectedSkill, setSelectedSkill] = useState(null);

  // Roll modifiers
  const [rollMode, setRollMode] = useState("normal"); // 'normal', 'advantage', 'disadvantage'
  const [customModifier, setCustomModifier] = useState(0);
  const [isSavingThrow, setIsSavingThrow] = useState(false);

  // Roll state
  const [isRolling, setIsRolling] = useState(false);
  const [lastResults, setLastResults] = useState([]); // Array for group checks
  const [rollHistory, setRollHistory] = useState([]); // Session history

  // UI state
  const [tabValue, setTabValue] = useState(0); // 0: Check, 1: Save, 2: History
  const [dcHint, setDcHint] = useState("");

  // Get character's ability modifier
  const getAbilityModifier = (character, ability) => {
    if (!character || !character.dnd_ability_modifiers) return 0;
    return character.dnd_ability_modifiers[ability] || 0;
  };

  // Get proficiency bonus for character
  const getProficiencyBonus = (character) => {
    if (!character || !character.dnd_proficiency_bonus) return 2;
    // Extract number from "+2" format
    const match = character.dnd_proficiency_bonus.match(/[+-]?\d+/);
    return match ? parseInt(match[0]) : 2;
  };

  // Check if character is proficient in a skill
  const isProficient = (character, skillKey) => {
    if (!character || !character.dnd_skills) return false;

    // dnd_skills is an array of skill names
    const normalizedSkillKey = skillKey.replace(/_/g, " ").toLowerCase();

    return character.dnd_skills.some(
      (skill) =>
        skill.toLowerCase() === normalizedSkillKey ||
        skill.toLowerCase() === skillKey.toLowerCase()
    );
  };

  // Calculate total modifier for a check
  const calculateModifier = (
    character,
    ability,
    skill = null,
    isSave = false
  ) => {
    const abilityMod = getAbilityModifier(character, ability);

    if (isSave) {
      // Saving throws may have proficiency
      const profBonus = getProficiencyBonus(character);
      // Check if character has proficiency in this save (stored in dnd_proficiencies.saves)
      const hasSaveProficiency =
        character.dnd_proficiencies?.saves?.includes(ability);
      return abilityMod + (hasSaveProficiency ? profBonus : 0) + customModifier;
    }

    if (skill && isProficient(character, skill)) {
      const profBonus = getProficiencyBonus(character);
      return abilityMod + profBonus + customModifier;
    }

    return abilityMod + customModifier;
  };

  // Get DC difficulty hints
  const getDCHints = () => {
    return {
      5: "Very Easy",
      10: "Easy",
      15: "Medium",
      20: "Hard",
      25: "Very Hard",
      30: "Nearly Impossible",
    };
  };

  // Roll a single d20 (with advantage/disadvantage)
  const rollD20 = () => {
    if (rollMode === "advantage") {
      const roll1 = Math.floor(Math.random() * 20) + 1;
      const roll2 = Math.floor(Math.random() * 20) + 1;
      return {
        value: Math.max(roll1, roll2),
        rolls: [roll1, roll2],
        mode: "advantage",
      };
    } else if (rollMode === "disadvantage") {
      const roll1 = Math.floor(Math.random() * 20) + 1;
      const roll2 = Math.floor(Math.random() * 20) + 1;
      return {
        value: Math.min(roll1, roll2),
        rolls: [roll1, roll2],
        mode: "disadvantage",
      };
    } else {
      const roll = Math.floor(Math.random() * 20) + 1;
      return { value: roll, rolls: [roll], mode: "normal" };
    }
  };

  // Roll ability check (single or group)
  const rollCheck = async () => {
    if (selectedCharacters.length === 0 || !selectedAbility) return;

    setIsRolling(true);

    const results = [];

    // Roll for each selected character
    for (const character of selectedCharacters) {
      const rollData = rollD20();
      const modifier = calculateModifier(
        character,
        selectedAbility.key,
        selectedSkill?.key,
        isSavingThrow
      );
      const total = rollData.value + modifier;

      const result = {
        character,
        ability: selectedAbility,
        skill: selectedSkill,
        roll: rollData.value,
        rolls: rollData.rolls,
        rollMode: rollData.mode,
        modifier,
        customModifier,
        total,
        isCriticalSuccess: rollData.value === 20,
        isCriticalFailure: rollData.value === 1,
        isSavingThrow,
        timestamp: new Date(),
      };

      results.push(result);
    }

    // Animate
    setTimeout(() => {
      setLastResults(results);
      setRollHistory((prev) => [...results, ...prev].slice(0, 50)); // Keep last 50 rolls
      setIsRolling(false);

      // Send formatted result to chat
      if (onCheckComplete) {
        const checkType = isSavingThrow
          ? `${selectedAbility.label} Save`
          : selectedSkill
          ? `${selectedSkill.label} (${selectedAbility.label})`
          : selectedAbility.label;

        const formattedMessage = formatCheckResults(results, checkType);
        onCheckComplete(formattedMessage, results);
      }
    }, 500);
  };

  // Format check results for LLM (handles single or group checks)
  const formatCheckResults = (results, checkType) => {
    if (results.length === 1) {
      return formatSingleResult(results[0], checkType);
    }

    // Group check formatting
    let message = `**Group ${checkType} Check:**\n\n`;

    results.forEach((result, index) => {
      const {
        character,
        roll,
        rolls,
        rollMode,
        modifier,
        customModifier,
        total,
        isCriticalSuccess,
        isCriticalFailure,
      } = result;

      message += `**${character.name}**:\n`;

      // Show roll details
      if (rollMode === "advantage") {
        message += `🎲 Rolls: ${rolls[0]}, ${rolls[1]} (Advantage: **${roll}**)\n`;
      } else if (rollMode === "disadvantage") {
        message += `🎲 Rolls: ${rolls[0]}, ${rolls[1]} (Disadvantage: **${roll}**)\n`;
      } else {
        message += `🎲 Roll: ${roll}`;
        if (isCriticalSuccess) message += ` 🌟 CRITICAL SUCCESS!`;
        if (isCriticalFailure) message += ` 💀 CRITICAL FAILURE!`;
        message += `\n`;
      }

      message += `➕ Modifier: ${modifier >= 0 ? "+" : ""}${modifier}`;
      if (customModifier !== 0) {
        message += ` (includes ${
          customModifier >= 0 ? "+" : ""
        }${customModifier} situational)`;
      }
      message += `\n`;
      message += `🎯 Total: **${total}**\n`;

      if (index < results.length - 1) message += `\n`;
    });

    message += `\n*(DM: Please compare these results to the appropriate DC and describe the outcomes)*`;

    return message;
  };

  const formatSingleResult = (result, checkType) => {
    const {
      character,
      roll,
      rolls,
      rollMode,
      modifier,
      customModifier,
      total,
      isCriticalSuccess,
      isCriticalFailure,
      isSavingThrow,
    } = result;

    let message = `**${character.name}** rolled a ${checkType}${
      isSavingThrow ? "" : " check"
    }:\n`;

    // Show roll details with advantage/disadvantage
    if (rollMode === "advantage") {
      message += `🎲 Rolls: ${rolls[0]}, ${rolls[1]} (Advantage: **${roll}**)\n`;
    } else if (rollMode === "disadvantage") {
      message += `🎲 Rolls: ${rolls[0]}, ${rolls[1]} (Disadvantage: **${roll}**)\n`;
    } else {
      message += `🎲 Roll: ${roll}`;
      if (isCriticalSuccess) message += ` 🌟 CRITICAL SUCCESS!`;
      if (isCriticalFailure) message += ` 💀 CRITICAL FAILURE!`;
      message += `\n`;
    }

    message += `➕ Modifier: ${modifier >= 0 ? "+" : ""}${modifier}`;
    if (customModifier !== 0) {
      message += ` (includes ${
        customModifier >= 0 ? "+" : ""
      }${customModifier} situational)`;
    }
    message += `\n`;
    message += `🎯 Total: **${total}**\n`;

    // Add context for DM
    message += `\n*(DM: Please compare this result to the appropriate DC and describe the outcome)*`;

    return message;
  };

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="lg"
      fullWidth
      maxHeight="90vh"
    >
      <DialogTitle>
        <Box
          sx={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
          }}
        >
          <Stack direction="row" spacing={2} alignItems="center">
            <Typography variant="h6">
              {isSavingThrow ? "Saving Throw" : "Ability Check"}
            </Typography>
            <Chip
              icon={<GroupIcon />}
              label={`${selectedCharacters.length} selected`}
              color={selectedCharacters.length > 0 ? "primary" : "default"}
              size="small"
            />
          </Stack>
          <IconButton onClick={onClose} size="small">
            <CloseIcon />
          </IconButton>
        </Box>

        {/* Tabs for Check / Save / History */}
        <Tabs
          value={tabValue}
          onChange={(e, newValue) => setTabValue(newValue)}
          sx={{ mt: 1 }}
        >
          <Tab label="Ability Check" />
          <Tab
            label="Saving Throw"
            icon={<ShieldIcon />}
            iconPosition="start"
          />
          <Tab label="History" icon={<HistoryIcon />} iconPosition="start" />
        </Tabs>
      </DialogTitle>

      <DialogContent>
        {tabValue === 2 ? (
          // History Tab
          <Box>
            <Typography variant="h6" sx={{ mb: 2 }}>
              Roll History
            </Typography>
            {rollHistory.length === 0 ? (
              <Typography variant="body2" color="text.secondary">
                No rolls yet in this session
              </Typography>
            ) : (
              <List>
                {rollHistory.map((result, index) => (
                  <ListItem key={index} divider>
                    <ListItemText
                      primary={`${result.character.name} - ${
                        result.skill?.label || result.ability.label
                      } ${result.isSavingThrow ? "Save" : "Check"}`}
                      secondary={`Roll: ${result.roll} | Modifier: ${
                        result.modifier >= 0 ? "+" : ""
                      }${result.modifier} | Total: ${result.total}`}
                    />
                    <Chip
                      label={result.total}
                      color={
                        result.isCriticalSuccess
                          ? "success"
                          : result.isCriticalFailure
                          ? "error"
                          : "default"
                      }
                      size="small"
                    />
                  </ListItem>
                ))}
              </List>
            )}
          </Box>
        ) : (
          <Stack spacing={3}>
            {/* Character Selection */}
            <Box>
              <Stack
                direction="row"
                spacing={1}
                alignItems="center"
                sx={{ mb: 1 }}
              >
                <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                  Select Character(s)
                </Typography>
                {selectedCharacters.length > 1 && (
                  <Chip
                    icon={<GroupIcon />}
                    label="Group Check"
                    size="small"
                    color="primary"
                    variant="outlined"
                  />
                )}
              </Stack>
              <Grid container spacing={1}>
                {characters.map((char) => {
                  const isSelected = selectedCharacters.some(
                    (c) => c.id === char.id
                  );
                  return (
                    <Grid item xs={6} sm={4} md={3} key={char.id}>
                      <Card
                        sx={{
                          cursor: "pointer",
                          border: isSelected ? 2 : 1,
                          borderColor: isSelected ? "primary.main" : "divider",
                          bgcolor: isSelected
                            ? "rgba(25, 118, 210, 0.08)"
                            : "background.paper",
                          transition: "all 0.2s",
                          "&:hover": {
                            borderColor: "primary.main",
                            transform: "translateY(-2px)",
                          },
                        }}
                        onClick={() => {
                          setSelectedCharacters((prev) =>
                            isSelected
                              ? prev.filter((c) => c.id !== char.id)
                              : [...prev, char]
                          );
                        }}
                      >
                        <CardContent
                          sx={{ p: 1.5, "&:last-child": { pb: 1.5 } }}
                        >
                          <Stack
                            direction="row"
                            spacing={1}
                            alignItems="center"
                          >
                            <Badge
                              badgeContent={isSelected ? "✓" : null}
                              color="primary"
                            >
                              <Avatar
                                src={char.portrait_image}
                                sx={{ width: 32, height: 32 }}
                              >
                                {char.name[0]}
                              </Avatar>
                            </Badge>
                            <Box>
                              <Typography
                                variant="body2"
                                sx={{ fontWeight: 600 }}
                              >
                                {char.name}
                              </Typography>
                              {char.dnd_class && (
                                <Typography
                                  variant="caption"
                                  color="text.secondary"
                                >
                                  Lvl {char.dnd_level || 1} {char.dnd_class}
                                </Typography>
                              )}
                            </Box>
                          </Stack>
                        </CardContent>
                      </Card>
                    </Grid>
                  );
                })}
              </Grid>
            </Box>

            {selectedCharacters.length > 0 && (
              <>
                <Divider />

                {/* Roll Mode Selection (Advantage/Disadvantage) */}
                <Box>
                  <Typography
                    variant="subtitle2"
                    sx={{ mb: 1, fontWeight: 600 }}
                  >
                    Roll Mode
                  </Typography>
                  <ToggleButtonGroup
                    value={rollMode}
                    exclusive
                    onChange={(e, newMode) => newMode && setRollMode(newMode)}
                    size="small"
                    fullWidth
                  >
                    <ToggleButton value="disadvantage">
                      <TrendingDown sx={{ mr: 0.5 }} fontSize="small" />
                      Disadvantage
                    </ToggleButton>
                    <ToggleButton value="normal">Normal</ToggleButton>
                    <ToggleButton value="advantage">
                      <TrendingUp sx={{ mr: 0.5 }} fontSize="small" />
                      Advantage
                    </ToggleButton>
                  </ToggleButtonGroup>
                </Box>

                {/* Custom Modifier */}
                <Box>
                  <Typography
                    variant="subtitle2"
                    sx={{ mb: 1, fontWeight: 600 }}
                  >
                    Situational Modifier
                  </Typography>
                  <Stack direction="row" spacing={1} alignItems="center">
                    <IconButton
                      size="small"
                      onClick={() =>
                        setCustomModifier((prev) => Math.max(prev - 1, -10))
                      }
                    >
                      <RemoveIcon />
                    </IconButton>
                    <TextField
                      type="number"
                      value={customModifier}
                      onChange={(e) =>
                        setCustomModifier(parseInt(e.target.value) || 0)
                      }
                      inputProps={{ min: -10, max: 10 }}
                      sx={{ width: 80, textAlign: "center" }}
                      size="small"
                    />
                    <IconButton
                      size="small"
                      onClick={() =>
                        setCustomModifier((prev) => Math.min(prev + 1, 10))
                      }
                    >
                      <AddIcon />
                    </IconButton>
                    <Typography
                      variant="caption"
                      color="text.secondary"
                      sx={{ flex: 1 }}
                    >
                      (cover, terrain, help action, etc.)
                    </Typography>
                  </Stack>
                </Box>

                {/* DC Hints */}
                <Box>
                  <Typography
                    variant="subtitle2"
                    sx={{ mb: 1, fontWeight: 600 }}
                  >
                    DC Reference
                  </Typography>
                  <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
                    {Object.entries(getDCHints()).map(([dc, label]) => (
                      <Chip
                        key={dc}
                        label={`DC ${dc}: ${label}`}
                        size="small"
                        onClick={() => setDcHint(dc)}
                        variant={dcHint === dc ? "filled" : "outlined"}
                        color={dcHint === dc ? "primary" : "default"}
                      />
                    ))}
                  </Stack>
                </Box>

                <Divider />

                {/* Ability Selection */}
                <Box>
                  <Typography
                    variant="subtitle2"
                    sx={{ mb: 1, fontWeight: 600 }}
                  >
                    Select Ability
                  </Typography>
                  <Grid container spacing={1}>
                    {ABILITIES.map((ability) => {
                      const AbilityIcon = ability.icon;
                      // Show modifier for first selected character
                      const modifier =
                        selectedCharacters.length > 0
                          ? getAbilityModifier(
                              selectedCharacters[0],
                              ability.key
                            )
                          : 0;

                      return (
                        <Grid item xs={6} sm={4} key={ability.key}>
                          <Tooltip
                            title={`${
                              modifier >= 0 ? "+" : ""
                            }${modifier} modifier (${
                              selectedCharacters[0]?.name || "first character"
                            })`}
                          >
                            <Button
                              fullWidth
                              variant={
                                selectedAbility?.key === ability.key
                                  ? "contained"
                                  : "outlined"
                              }
                              startIcon={<AbilityIcon />}
                              onClick={() => {
                                setSelectedAbility(ability);
                                if (tabValue === 1) {
                                  // For saving throws, clear skill selection
                                  setSelectedSkill(null);
                                }
                              }}
                              sx={{
                                justifyContent: "flex-start",
                                borderColor: ability.color,
                                color:
                                  selectedAbility?.key === ability.key
                                    ? "#fff"
                                    : ability.color,
                                bgcolor:
                                  selectedAbility?.key === ability.key
                                    ? ability.color
                                    : "transparent",
                                "&:hover": {
                                  borderColor: ability.color,
                                  bgcolor:
                                    selectedAbility?.key === ability.key
                                      ? ability.color
                                      : `${ability.color}22`,
                                },
                              }}
                            >
                              <Box sx={{ flex: 1, textAlign: "left" }}>
                                <Typography variant="body2">
                                  {ability.label}
                                </Typography>
                                <Typography variant="caption">
                                  {modifier >= 0 ? "+" : ""}
                                  {modifier}
                                </Typography>
                              </Box>
                            </Button>
                          </Tooltip>
                        </Grid>
                      );
                    })}
                  </Grid>
                </Box>

                {/* Skill Selection (Only for Ability Checks, not Saves) */}
                {selectedAbility &&
                  SKILLS[selectedAbility.key] &&
                  tabValue === 0 && (
                    <>
                      <Divider />
                      <Box>
                        <Typography
                          variant="subtitle2"
                          sx={{ mb: 1, fontWeight: 600 }}
                        >
                          Or Select a Skill
                          <Typography
                            variant="caption"
                            color="text.secondary"
                            sx={{ ml: 1 }}
                          >
                            (Optional - adds proficiency bonus if trained)
                          </Typography>
                        </Typography>
                        <Stack
                          direction="row"
                          spacing={1}
                          flexWrap="wrap"
                          useFlexGap
                        >
                          <Chip
                            label="None (Pure Ability Check)"
                            onClick={() => setSelectedSkill(null)}
                            variant={!selectedSkill ? "filled" : "outlined"}
                            color={!selectedSkill ? "primary" : "default"}
                            sx={{ mb: 1 }}
                          />
                          {SKILLS[selectedAbility.key].map((skill) => {
                            const proficient =
                              selectedCharacters.length > 0
                                ? isProficient(selectedCharacters[0], skill.key)
                                : false;
                            const modifier =
                              selectedCharacters.length > 0
                                ? calculateModifier(
                                    selectedCharacters[0],
                                    selectedAbility.key,
                                    skill.key,
                                    false
                                  )
                                : 0;

                            return (
                              <Chip
                                key={skill.key}
                                label={
                                  <Box>
                                    {skill.label}
                                    {proficient && " ★"}
                                    <Typography
                                      variant="caption"
                                      sx={{ ml: 0.5 }}
                                    >
                                      ({modifier >= 0 ? "+" : ""}
                                      {modifier})
                                    </Typography>
                                  </Box>
                                }
                                onClick={() => setSelectedSkill(skill)}
                                variant={
                                  selectedSkill?.key === skill.key
                                    ? "filled"
                                    : "outlined"
                                }
                                color={
                                  selectedSkill?.key === skill.key
                                    ? "primary"
                                    : "default"
                                }
                                sx={{ mb: 1 }}
                              />
                            );
                          })}
                        </Stack>
                      </Box>
                    </>
                  )}

                <Divider />

                {/* Roll Button */}
                <Box sx={{ textAlign: "center" }}>
                  <Button
                    variant="contained"
                    size="large"
                    startIcon={<DiceIcon />}
                    onClick={rollCheck}
                    disabled={isRolling || !selectedAbility}
                    sx={{
                      minWidth: 200,
                      py: 1.5,
                      fontSize: "1.1rem",
                      fontWeight: 600,
                    }}
                  >
                    {isRolling
                      ? "Rolling..."
                      : selectedCharacters.length > 1
                      ? "Roll Group Check"
                      : "Roll Check"}
                  </Button>
                </Box>

                {/* Last Results */}
                {lastResults.length > 0 && (
                  <Fade in={true}>
                    <Stack spacing={1}>
                      {lastResults.map((result, index) => (
                        <Paper
                          key={index}
                          elevation={3}
                          sx={{
                            p: 2,
                            bgcolor: result.isCriticalSuccess
                              ? "rgba(76, 175, 80, 0.1)"
                              : result.isCriticalFailure
                              ? "rgba(244, 67, 54, 0.1)"
                              : "background.paper",
                            border: 2,
                            borderColor: result.isCriticalSuccess
                              ? "success.main"
                              : result.isCriticalFailure
                              ? "error.main"
                              : "primary.main",
                          }}
                        >
                          <Typography variant="h6" sx={{ mb: 1 }}>
                            {result.character.name}'s{" "}
                            {result.skill?.label || result.ability.label}{" "}
                            {result.isSavingThrow ? "Save" : "Check"}
                          </Typography>
                          <Stack
                            direction="row"
                            spacing={2}
                            alignItems="center"
                            justifyContent="center"
                            flexWrap="wrap"
                          >
                            {result.rollMode !== "normal" && (
                              <Box sx={{ textAlign: "center" }}>
                                <Typography
                                  variant="caption"
                                  color="text.secondary"
                                >
                                  {result.rollMode === "advantage"
                                    ? "Advantage"
                                    : "Disadvantage"}
                                </Typography>
                                <Typography variant="body2">
                                  {result.rolls.join(", ")}
                                </Typography>
                              </Box>
                            )}
                            <Box sx={{ textAlign: "center" }}>
                              <Typography
                                variant="caption"
                                color="text.secondary"
                              >
                                Roll
                              </Typography>
                              <Typography variant="h4" sx={{ fontWeight: 700 }}>
                                {result.roll}
                              </Typography>
                            </Box>
                            <Typography variant="h5">+</Typography>
                            <Box sx={{ textAlign: "center" }}>
                              <Typography
                                variant="caption"
                                color="text.secondary"
                              >
                                Modifier
                              </Typography>
                              <Typography variant="h4" sx={{ fontWeight: 700 }}>
                                {result.modifier >= 0 ? "+" : ""}
                                {result.modifier}
                              </Typography>
                            </Box>
                            <Typography variant="h5">=</Typography>
                            <Box sx={{ textAlign: "center" }}>
                              <Typography
                                variant="caption"
                                color="text.secondary"
                              >
                                Total
                              </Typography>
                              <Typography
                                variant="h3"
                                sx={{
                                  fontWeight: 700,
                                  color: result.isCriticalSuccess
                                    ? "success.main"
                                    : result.isCriticalFailure
                                    ? "error.main"
                                    : "primary.main",
                                }}
                              >
                                {result.total}
                              </Typography>
                            </Box>
                          </Stack>
                          {(result.isCriticalSuccess ||
                            result.isCriticalFailure) && (
                            <Typography
                              variant="subtitle1"
                              sx={{
                                mt: 1,
                                textAlign: "center",
                                fontWeight: 600,
                                color: result.isCriticalSuccess
                                  ? "success.main"
                                  : "error.main",
                              }}
                            >
                              {result.isCriticalSuccess
                                ? "🌟 CRITICAL SUCCESS!"
                                : "💀 CRITICAL FAILURE!"}
                            </Typography>
                          )}
                        </Paper>
                      ))}
                    </Stack>
                  </Fade>
                )}
              </>
            )}
          </Stack>
        )}
      </DialogContent>
    </Dialog>
  );
};

export default AbilityCheckPanel;
