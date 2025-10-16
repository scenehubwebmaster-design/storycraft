import { useState } from "react";
import {
  Box,
  Paper,
  Typography,
  Grid,
  Chip,
  Divider,
  Card,
  CardContent,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Button,
  IconButton,
  Tooltip,
  Alert,
} from "@mui/material";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import DownloadIcon from "@mui/icons-material/Download";
import PrintIcon from "@mui/icons-material/Print";
import ShareIcon from "@mui/icons-material/Share";
import ContentCopyIcon from "@mui/icons-material/ContentCopy";

/**
 * DnDCharacterSheet Component
 *
 * Displays a complete D&D 5E character sheet with all stats, abilities,
 * equipment, and narrative information
 */
export default function DnDCharacterSheet({ character }) {
  const [expanded, setExpanded] = useState({
    combat: true,
    abilities: true,
    skills: true,
    features: true,
    equipment: true,
    spellcasting: false,
    narrative: true,
  });

  if (!character || !character.is_dnd) {
    return (
      <Alert severity="warning">
        This is not a D&D character or character data is missing.
      </Alert>
    );
  }

  const handleExpandToggle = (section) => {
    setExpanded((prev) => ({ ...prev, [section]: !prev[section] }));
  };

  const getAbilityModifier = (score) => {
    const modifier = Math.floor((score - 10) / 2);
    return modifier >= 0 ? `+${modifier}` : `${modifier}`;
  };

  const exportToJSON = () => {
    const dataStr = JSON.stringify(character, null, 2);
    const dataUri =
      "data:application/json;charset=utf-8," + encodeURIComponent(dataStr);
    const exportFileDefaultName = `${character.name}_character.json`;

    const linkElement = document.createElement("a");
    linkElement.setAttribute("href", dataUri);
    linkElement.setAttribute("download", exportFileDefaultName);
    linkElement.click();
  };

  const exportToText = () => {
    const textContent = formatCharacterAsText(character);
    const dataUri =
      "data:text/plain;charset=utf-8," + encodeURIComponent(textContent);
    const exportFileDefaultName = `${character.name}_character.txt`;

    const linkElement = document.createElement("a");
    linkElement.setAttribute("href", dataUri);
    linkElement.setAttribute("download", exportFileDefaultName);
    linkElement.click();
  };

  const handlePrint = () => {
    window.print();
  };

  const copyToClipboard = () => {
    const textContent = formatCharacterAsText(character);
    navigator.clipboard.writeText(textContent);
    alert("Character sheet copied to clipboard!");
  };

  const formatCharacterAsText = (char) => {
    return `
═══════════════════════════════════════════════════════════════
                    D&D 5E CHARACTER SHEET
═══════════════════════════════════════════════════════════════

CHARACTER INFO
──────────────────────────────────────────────────────────────
Name: ${char.name}
Class: ${char.dnd_class} (Level ${char.dnd_level})
Species: ${char.dnd_species}
Background: ${char.dnd_background}
Alignment: ${char.dnd_alignment || "Unaligned"}

ABILITY SCORES
──────────────────────────────────────────────────────────────
STR: ${char.dnd_ability_scores?.strength || 10} (${getAbilityModifier(char.dnd_ability_scores?.strength || 10)})
DEX: ${char.dnd_ability_scores?.dexterity || 10} (${getAbilityModifier(char.dnd_ability_scores?.dexterity || 10)})
CON: ${char.dnd_ability_scores?.constitution || 10} (${getAbilityModifier(char.dnd_ability_scores?.constitution || 10)})
INT: ${char.dnd_ability_scores?.intelligence || 10} (${getAbilityModifier(char.dnd_ability_scores?.intelligence || 10)})
WIS: ${char.dnd_ability_scores?.wisdom || 10} (${getAbilityModifier(char.dnd_ability_scores?.wisdom || 10)})
CHA: ${char.dnd_ability_scores?.charisma || 10} (${getAbilityModifier(char.dnd_ability_scores?.charisma || 10)})

COMBAT STATS
──────────────────────────────────────────────────────────────
Hit Points: ${char.dnd_hit_points || 0}
Armor Class: ${char.dnd_armor_class || 10}
Initiative: ${char.dnd_initiative || "+0"}
Speed: ${char.dnd_speed || 30} ft
Proficiency Bonus: ${char.dnd_proficiency_bonus || "+2"}

PROFICIENCIES
──────────────────────────────────────────────────────────────
Skills: ${char.dnd_skills?.join(", ") || "None"}
Saving Throws: ${char.dnd_proficiencies?.saves?.join(", ") || "None"}
Languages: ${char.dnd_languages?.join(", ") || "Common"}

${
  char.dnd_spellcasting
    ? `
SPELLCASTING
──────────────────────────────────────────────────────────────
Spellcasting Ability: ${char.dnd_spellcasting.ability}
Spell Save DC: ${char.dnd_spellcasting.spell_save_dc}
Spell Attack Bonus: +${char.dnd_spellcasting.spell_attack_bonus}
Cantrips Known: ${char.dnd_spellcasting.cantrips_known || 0}
Spells Known: ${char.dnd_spellcasting.spells_known || 0}
`
    : ""
}

EQUIPMENT
──────────────────────────────────────────────────────────────
${char.dnd_equipment ? formatEquipment(char.dnd_equipment) : "None"}

FEATURES & TRAITS
──────────────────────────────────────────────────────────────
${char.dnd_features ? formatFeatures(char.dnd_features) : "None"}

${
  char.ai_narrative
    ? `
NARRATIVE
──────────────────────────────────────────────────────────────
${formatNarrative(char.ai_narrative)}
`
    : ""
}

═══════════════════════════════════════════════════════════════
    `.trim();
  };

  const formatEquipment = (equipment) => {
    let text = "";
    if (equipment.weapons?.length > 0) {
      text +=
        "Weapons:\n" +
        equipment.weapons
          .map((w) => `  - ${w.name} (${w.damage || ""})`)
          .join("\n") +
        "\n\n";
    }
    if (equipment.armor?.length > 0) {
      text +=
        "Armor:\n" + equipment.armor.map((a) => `  - ${a}`).join("\n") + "\n\n";
    }
    if (equipment.gear?.length > 0) {
      text +=
        "Gear:\n" + equipment.gear.map((g) => `  - ${g}`).join("\n") + "\n\n";
    }
    if (equipment.gold) {
      text += `Gold: ${equipment.gold} gp`;
    }
    return text;
  };

  const formatFeatures = (features) => {
    let text = "";
    if (features.racial?.length > 0) {
      text += "Racial: " + features.racial.join(", ") + "\n\n";
    }
    if (features.class?.length > 0) {
      text += "Class: " + features.class.join(", ") + "\n\n";
    }
    if (features.background?.feature) {
      text += `Background: ${features.background.feature}\n`;
      if (features.background.description) {
        text += `  ${features.background.description}`;
      }
    }
    return text;
  };

  const formatNarrative = (narrative) => {
    let text = "";
    if (narrative.appearance)
      text += `Appearance:\n${narrative.appearance}\n\n`;
    if (narrative.personality)
      text += `Personality:\n${narrative.personality}\n\n`;
    if (narrative.backstory) text += `Backstory:\n${narrative.backstory}\n\n`;
    if (narrative.motivations)
      text += `Motivations:\n${narrative.motivations}\n\n`;
    if (narrative.quirks) text += `Quirks:\n${narrative.quirks}`;
    return text;
  };

  return (
    <Box>
      {/* Header with export options - D&D styled */}
      <Paper
        elevation={3}
        sx={{
          p: 3,
          mb: 2,
          background: "linear-gradient(135deg, #2c1810 0%, #3d2817 100%)",
          color: "#f4e4c1",
          borderRadius: 2,
          border: "2px solid #8b6f47",
        }}
      >
        <Box display="flex" justifyContent="space-between" alignItems="center">
          <Box>
            <Typography
              variant="h3"
              component="h1"
              sx={{
                fontFamily: '"Cinzel", "Times New Roman", serif',
                fontWeight: 700,
                letterSpacing: 1,
                mb: 1,
              }}
            >
              {character.name}
            </Typography>
            <Typography
              variant="subtitle1"
              sx={{
                fontFamily: '"Crimson Text", serif',
                fontSize: "1.1rem",
                opacity: 0.9,
              }}
            >
              Level {character.dnd_level} {character.dnd_species}{" "}
              {character.dnd_class}
            </Typography>
          </Box>
          <Box>
            <Tooltip title="Copy to Clipboard">
              <IconButton onClick={copyToClipboard} sx={{ color: "#f4e4c1" }}>
                <ContentCopyIcon />
              </IconButton>
            </Tooltip>
            <Tooltip title="Export as JSON">
              <IconButton onClick={exportToJSON} sx={{ color: "#f4e4c1" }}>
                <DownloadIcon />
              </IconButton>
            </Tooltip>
            <Tooltip title="Export as Text">
              <IconButton onClick={exportToText} sx={{ color: "#f4e4c1" }}>
                <DownloadIcon />
              </IconButton>
            </Tooltip>
            <Tooltip title="Print">
              <IconButton onClick={handlePrint} sx={{ color: "#f4e4c1" }}>
                <PrintIcon />
              </IconButton>
            </Tooltip>
          </Box>
        </Box>

        <Box display="flex" gap={1} mt={2} flexWrap="wrap">
          <Chip
            label={character.dnd_background}
            sx={{
              bgcolor: "#8b6f47",
              color: "#f4e4c1",
              fontWeight: 600,
            }}
          />
          {character.dnd_alignment && (
            <Chip
              label={character.dnd_alignment}
              sx={{
                bgcolor: "rgba(139, 111, 71, 0.3)",
                color: "#f4e4c1",
                borderColor: "#8b6f47",
                borderWidth: 1,
                borderStyle: "solid",
              }}
            />
          )}
        </Box>
      </Paper>

      <Grid container spacing={2}>
        {/* Left Column - Ability Scores & Combat Stats */}
        <Grid item xs={12} md={4}>
          {/* Ability Scores - Classic D&D hexagon style */}
          <Paper
            elevation={2}
            sx={{
              p: 2.5,
              mb: 2,
              background:
                "linear-gradient(to bottom, #f8f4e6 0%, #ebe6d5 100%)",
              border: "2px solid #8b6f47",
              borderRadius: 2,
            }}
          >
            <Typography
              variant="h6"
              gutterBottom
              sx={{
                fontFamily: '"Cinzel", serif',
                color: "#2c1810",
                borderBottom: "2px solid #8b6f47",
                pb: 1,
                mb: 2,
              }}
            >
              Ability Scores
            </Typography>
            <Grid container spacing={1.5}>
              {character.dnd_ability_scores &&
                Object.entries(character.dnd_ability_scores).map(
                  ([ability, score]) => (
                    <Grid item xs={6} key={ability}>
                      <Card
                        variant="outlined"
                        sx={{
                          background:
                            "linear-gradient(135deg, #2c1810 0%, #3d2817 100%)",
                          border: "2px solid #8b6f47",
                          borderRadius: 1.5,
                        }}
                      >
                        <CardContent sx={{ textAlign: "center", p: 1.5 }}>
                          <Typography
                            variant="caption"
                            sx={{
                              textTransform: "uppercase",
                              color: "#d4af37",
                              fontWeight: 700,
                              letterSpacing: 1,
                              fontSize: "0.7rem",
                            }}
                          >
                            {ability.substring(0, 3)}
                          </Typography>
                          <Typography
                            variant="h3"
                            sx={{
                              color: "#f4e4c1",
                              fontFamily: '"Cinzel", serif',
                              fontWeight: 700,
                              my: 0.5,
                            }}
                          >
                            {score}
                          </Typography>
                          <Typography
                            variant="h6"
                            sx={{
                              color: "#d4af37",
                              fontWeight: 700,
                            }}
                          >
                            {getAbilityModifier(score)}
                          </Typography>
                        </CardContent>
                      </Card>
                    </Grid>
                  )
                )}
            </Grid>
          </Paper>

          {/* Combat Stats - Parchment style */}
          <Paper
            elevation={2}
            sx={{
              p: 2.5,
              mb: 2,
              background:
                "linear-gradient(to bottom, #f8f4e6 0%, #ebe6d5 100%)",
              border: "2px solid #8b6f47",
              borderRadius: 2,
            }}
          >
            <Typography
              variant="h6"
              gutterBottom
              sx={{
                fontFamily: '"Cinzel", serif',
                color: "#2c1810",
                borderBottom: "2px solid #8b6f47",
                pb: 1,
                mb: 2,
              }}
            >
              Combat Stats
            </Typography>
            <Box>
              <Box display="flex" justifyContent="space-between" py={1}>
                <Typography
                  variant="body2"
                  sx={{
                    color: "#2c1810",
                    fontWeight: 600,
                  }}
                >
                  Hit Points
                </Typography>
                <Typography
                  variant="body1"
                  sx={{
                    fontWeight: 700,
                    color: "#c41e3a",
                    fontSize: "1.1rem",
                  }}
                >
                  {character.dnd_hit_points}
                </Typography>
              </Box>
              <Divider sx={{ borderColor: "#8b6f47", opacity: 0.3 }} />
              <Box display="flex" justifyContent="space-between" py={1}>
                <Typography
                  variant="body2"
                  sx={{
                    color: "#2c1810",
                    fontWeight: 600,
                  }}
                >
                  Armor Class
                </Typography>
                <Typography
                  variant="body1"
                  sx={{
                    fontWeight: 700,
                    color: "#2c1810",
                    fontSize: "1.1rem",
                  }}
                >
                  {character.dnd_armor_class}
                </Typography>
              </Box>
              <Divider sx={{ borderColor: "#8b6f47", opacity: 0.3 }} />
              <Box display="flex" justifyContent="space-between" py={1}>
                <Typography
                  variant="body2"
                  sx={{
                    color: "#2c1810",
                    fontWeight: 600,
                  }}
                >
                  Initiative
                </Typography>
                <Typography
                  variant="body1"
                  sx={{
                    fontWeight: 700,
                    color: "#2c1810",
                    fontSize: "1.1rem",
                  }}
                >
                  {character.dnd_initiative}
                </Typography>
              </Box>
              <Divider sx={{ borderColor: "#8b6f47", opacity: 0.3 }} />
              <Box display="flex" justifyContent="space-between" py={1}>
                <Typography
                  variant="body2"
                  sx={{
                    color: "#2c1810",
                    fontWeight: 600,
                  }}
                >
                  Speed
                </Typography>
                <Typography
                  variant="body1"
                  sx={{
                    fontWeight: 700,
                    color: "#2c1810",
                    fontSize: "1.1rem",
                  }}
                >
                  {character.dnd_speed} ft
                </Typography>
              </Box>
              <Divider sx={{ borderColor: "#8b6f47", opacity: 0.3 }} />
              <Box display="flex" justifyContent="space-between" py={1}>
                <Typography
                  variant="body2"
                  sx={{
                    color: "#2c1810",
                    fontWeight: 600,
                  }}
                >
                  Proficiency Bonus
                </Typography>
                <Typography
                  variant="body1"
                  sx={{
                    fontWeight: 700,
                    color: "#2c1810",
                    fontSize: "1.1rem",
                  }}
                >
                  {character.dnd_proficiency_bonus}
                </Typography>
              </Box>
            </Box>
          </Paper>
        </Grid>

        {/* Right Column - Detailed Information */}
        <Grid item xs={12} md={8}>
          {/* Skills & Proficiencies */}
          <Accordion
            expanded={expanded.skills}
            onChange={() => handleExpandToggle("skills")}
          >
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography variant="h6">Skills & Proficiencies</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Grid container spacing={2}>
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle2" gutterBottom>
                    Skills
                  </Typography>
                  <Box display="flex" flexWrap="wrap" gap={0.5}>
                    {character.dnd_skills?.map((skill) => (
                      <Chip key={skill} label={skill} size="small" />
                    ))}
                  </Box>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle2" gutterBottom>
                    Saving Throws
                  </Typography>
                  <Box display="flex" flexWrap="wrap" gap={0.5}>
                    {character.dnd_proficiencies?.saves?.map((save) => (
                      <Chip
                        key={save}
                        label={save}
                        size="small"
                        color="primary"
                      />
                    ))}
                  </Box>
                </Grid>
                <Grid item xs={12}>
                  <Typography variant="subtitle2" gutterBottom>
                    Languages
                  </Typography>
                  <Box display="flex" flexWrap="wrap" gap={0.5}>
                    {character.dnd_languages?.map((lang) => (
                      <Chip
                        key={lang}
                        label={lang}
                        size="small"
                        variant="outlined"
                      />
                    ))}
                  </Box>
                </Grid>
              </Grid>
            </AccordionDetails>
          </Accordion>

          {/* Features & Traits */}
          <Accordion
            expanded={expanded.features}
            onChange={() => handleExpandToggle("features")}
          >
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography variant="h6">Features & Traits</Typography>
            </AccordionSummary>
            <AccordionDetails>
              {character.dnd_features && (
                <Box>
                  {character.dnd_features.racial?.length > 0 && (
                    <Box mb={2}>
                      <Typography
                        variant="subtitle2"
                        color="primary"
                        gutterBottom
                      >
                        Racial Traits
                      </Typography>
                      <Box display="flex" flexWrap="wrap" gap={0.5}>
                        {character.dnd_features.racial.map((trait) => (
                          <Chip key={trait} label={trait} size="small" />
                        ))}
                      </Box>
                    </Box>
                  )}

                  {character.dnd_features.class?.length > 0 && (
                    <Box mb={2}>
                      <Typography
                        variant="subtitle2"
                        color="primary"
                        gutterBottom
                      >
                        Class Features
                      </Typography>
                      <Box display="flex" flexWrap="wrap" gap={0.5}>
                        {character.dnd_features.class.map((feat) => (
                          <Chip
                            key={feat}
                            label={feat}
                            size="small"
                            color="secondary"
                          />
                        ))}
                      </Box>
                    </Box>
                  )}

                  {character.dnd_features.background?.feature && (
                    <Box>
                      <Typography
                        variant="subtitle2"
                        color="primary"
                        gutterBottom
                      >
                        Background Feature:{" "}
                        {character.dnd_features.background.feature}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {character.dnd_features.background.description}
                      </Typography>
                    </Box>
                  )}
                </Box>
              )}
            </AccordionDetails>
          </Accordion>

          {/* Equipment */}
          <Accordion
            expanded={expanded.equipment}
            onChange={() => handleExpandToggle("equipment")}
          >
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography variant="h6">Equipment</Typography>
            </AccordionSummary>
            <AccordionDetails>
              {character.dnd_equipment && (
                <Grid container spacing={2}>
                  {character.dnd_equipment.weapons?.length > 0 && (
                    <Grid item xs={12}>
                      <Typography variant="subtitle2" gutterBottom>
                        Weapons
                      </Typography>
                      <TableContainer>
                        <Table size="small">
                          <TableHead>
                            <TableRow>
                              <TableCell>Name</TableCell>
                              <TableCell>Damage</TableCell>
                            </TableRow>
                          </TableHead>
                          <TableBody>
                            {character.dnd_equipment.weapons.map(
                              (weapon, idx) => (
                                <TableRow key={idx}>
                                  <TableCell>{weapon.name}</TableCell>
                                  <TableCell>{weapon.damage || "-"}</TableCell>
                                </TableRow>
                              )
                            )}
                          </TableBody>
                        </Table>
                      </TableContainer>
                    </Grid>
                  )}

                  {character.dnd_equipment.armor?.length > 0 && (
                    <Grid item xs={12}>
                      <Typography variant="subtitle2" gutterBottom>
                        Armor
                      </Typography>
                      <Box display="flex" flexWrap="wrap" gap={0.5}>
                        {character.dnd_equipment.armor.map((armor, idx) => (
                          <Chip key={idx} label={armor} size="small" />
                        ))}
                      </Box>
                    </Grid>
                  )}

                  {character.dnd_equipment.gear?.length > 0 && (
                    <Grid item xs={12}>
                      <Typography variant="subtitle2" gutterBottom>
                        Gear
                      </Typography>
                      <Box display="flex" flexWrap="wrap" gap={0.5}>
                        {character.dnd_equipment.gear.map((item, idx) => (
                          <Chip
                            key={idx}
                            label={item}
                            size="small"
                            variant="outlined"
                          />
                        ))}
                      </Box>
                    </Grid>
                  )}

                  {character.dnd_equipment.gold && (
                    <Grid item xs={12}>
                      <Typography variant="subtitle2">
                        Gold: <strong>{character.dnd_equipment.gold} gp</strong>
                      </Typography>
                    </Grid>
                  )}
                </Grid>
              )}
            </AccordionDetails>
          </Accordion>

          {/* Spellcasting (if applicable) */}
          {character.dnd_spellcasting && (
            <Accordion
              expanded={expanded.spellcasting}
              onChange={() => handleExpandToggle("spellcasting")}
            >
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Typography variant="h6">✨ Spellcasting</Typography>
              </AccordionSummary>
              <AccordionDetails>
                <Grid container spacing={2}>
                  <Grid item xs={6} md={3}>
                    <Typography variant="caption" color="text.secondary">
                      Ability
                    </Typography>
                    <Typography variant="body1">
                      {character.dnd_spellcasting.ability}
                    </Typography>
                  </Grid>
                  <Grid item xs={6} md={3}>
                    <Typography variant="caption" color="text.secondary">
                      Spell Save DC
                    </Typography>
                    <Typography variant="body1">
                      {character.dnd_spellcasting.spell_save_dc}
                    </Typography>
                  </Grid>
                  <Grid item xs={6} md={3}>
                    <Typography variant="caption" color="text.secondary">
                      Spell Attack
                    </Typography>
                    <Typography variant="body1">
                      +{character.dnd_spellcasting.spell_attack_bonus}
                    </Typography>
                  </Grid>
                  <Grid item xs={6} md={3}>
                    <Typography variant="caption" color="text.secondary">
                      Cantrips Known
                    </Typography>
                    <Typography variant="body1">
                      {character.dnd_spellcasting.cantrips_known || 0}
                    </Typography>
                  </Grid>
                  <Grid item xs={12}>
                    <Typography variant="caption" color="text.secondary">
                      Spells Known
                    </Typography>
                    <Typography variant="body1">
                      {character.dnd_spellcasting.spells_known || 0}
                    </Typography>
                  </Grid>
                  {character.dnd_spellcasting.spell_slots && (
                    <Grid item xs={12}>
                      <Typography variant="caption" color="text.secondary">
                        Spell Slots
                      </Typography>
                      <Box display="flex" gap={1} mt={1}>
                        {Object.entries(
                          character.dnd_spellcasting.spell_slots
                        ).map(([level, slots]) => (
                          <Chip
                            key={level}
                            label={`${level}: ${slots}`}
                            size="small"
                          />
                        ))}
                      </Box>
                    </Grid>
                  )}
                </Grid>
              </AccordionDetails>
            </Accordion>
          )}

          {/* AI-Generated Narrative */}
          {(character.structured_data || character.ai_narrative) && (
            <Accordion
              expanded={expanded.narrative}
              onChange={() => handleExpandToggle("narrative")}
            >
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Typography variant="h6">📖 Character Narrative</Typography>
              </AccordionSummary>
              <AccordionDetails>
                <Box>
                  {/* Character Information Section */}
                  {character.structured_data && (
                    <Box mb={3}>
                      <Typography variant="h6" color="primary" gutterBottom>
                        Character Information
                      </Typography>
                      <Grid container spacing={2}>
                        {character.structured_data.age && (
                          <Grid item xs={6} sm={4}>
                            <Typography
                              variant="caption"
                              color="text.secondary"
                            >
                              Age
                            </Typography>
                            <Typography variant="body2">
                              {character.structured_data.age}
                            </Typography>
                          </Grid>
                        )}
                        {character.structured_data.height && (
                          <Grid item xs={6} sm={4}>
                            <Typography
                              variant="caption"
                              color="text.secondary"
                            >
                              Height
                            </Typography>
                            <Typography variant="body2">
                              {character.structured_data.height}
                            </Typography>
                          </Grid>
                        )}
                        {character.structured_data.weight && (
                          <Grid item xs={6} sm={4}>
                            <Typography
                              variant="caption"
                              color="text.secondary"
                            >
                              Weight
                            </Typography>
                            <Typography variant="body2">
                              {character.structured_data.weight}
                            </Typography>
                          </Grid>
                        )}
                        {character.structured_data.eyes && (
                          <Grid item xs={6} sm={4}>
                            <Typography
                              variant="caption"
                              color="text.secondary"
                            >
                              Eyes
                            </Typography>
                            <Typography variant="body2">
                              {character.structured_data.eyes}
                            </Typography>
                          </Grid>
                        )}
                        {character.structured_data.skin && (
                          <Grid item xs={6} sm={4}>
                            <Typography
                              variant="caption"
                              color="text.secondary"
                            >
                              Skin
                            </Typography>
                            <Typography variant="body2">
                              {character.structured_data.skin}
                            </Typography>
                          </Grid>
                        )}
                        {character.structured_data.hair && (
                          <Grid item xs={6} sm={4}>
                            <Typography
                              variant="caption"
                              color="text.secondary"
                            >
                              Hair
                            </Typography>
                            <Typography variant="body2">
                              {character.structured_data.hair}
                            </Typography>
                          </Grid>
                        )}
                      </Grid>
                    </Box>
                  )}

                  {/* Character Appearance */}
                  {character.structured_data?.character_appearance && (
                    <Box mb={2}>
                      <Typography
                        variant="subtitle2"
                        color="primary"
                        gutterBottom
                      >
                        Character Appearance
                      </Typography>
                      <Typography variant="body2" paragraph>
                        {character.structured_data.character_appearance}
                      </Typography>
                    </Box>
                  )}

                  {/* Character Motivations (D&D 5E Standard) */}
                  {(character.structured_data?.personality_traits ||
                    character.structured_data?.ideals ||
                    character.structured_data?.bonds ||
                    character.structured_data?.flaws) && (
                    <Box mb={2}>
                      <Typography
                        variant="subtitle2"
                        color="primary"
                        gutterBottom
                      >
                        Character Motivations
                      </Typography>

                      {character.structured_data.personality_traits && (
                        <Box mb={1.5}>
                          <Typography
                            variant="caption"
                            fontWeight="bold"
                            color="text.secondary"
                          >
                            Personality Traits:
                          </Typography>
                          <Box
                            sx={{
                              display: "flex",
                              flexWrap: "wrap",
                              gap: 0.5,
                              mt: 0.5,
                            }}
                          >
                            {character.structured_data.personality_traits.map(
                              (trait, idx) => (
                                <Chip
                                  key={idx}
                                  label={trait}
                                  size="small"
                                  color="primary"
                                  variant="outlined"
                                />
                              )
                            )}
                          </Box>
                        </Box>
                      )}

                      {character.structured_data.ideals && (
                        <Typography variant="body2" paragraph>
                          <strong>Ideals:</strong>{" "}
                          {character.structured_data.ideals}
                        </Typography>
                      )}

                      {character.structured_data.bonds && (
                        <Typography variant="body2" paragraph>
                          <strong>Bonds:</strong>{" "}
                          {character.structured_data.bonds}
                        </Typography>
                      )}

                      {character.structured_data.flaws && (
                        <Typography variant="body2" paragraph>
                          <strong>Flaws:</strong>{" "}
                          {character.structured_data.flaws}
                        </Typography>
                      )}
                    </Box>
                  )}

                  {/* Character Backstory */}
                  {character.structured_data?.character_backstory && (
                    <Box mb={2}>
                      <Typography
                        variant="subtitle2"
                        color="primary"
                        gutterBottom
                      >
                        Character Backstory
                      </Typography>
                      <Typography variant="body2" paragraph>
                        {character.structured_data.character_backstory}
                      </Typography>
                    </Box>
                  )}

                  {/* Allies & Organizations */}
                  {character.structured_data?.allies_and_organizations && (
                    <Box mb={2}>
                      <Typography
                        variant="subtitle2"
                        color="primary"
                        gutterBottom
                      >
                        Allies & Organizations
                      </Typography>
                      <Typography variant="body2" paragraph>
                        {character.structured_data.allies_and_organizations}
                      </Typography>
                    </Box>
                  )}

                  {/* Additional Features & Traits */}
                  {character.structured_data
                    ?.additional_features_and_traits && (
                    <Box mb={2}>
                      <Typography
                        variant="subtitle2"
                        color="primary"
                        gutterBottom
                      >
                        Additional Features & Traits
                      </Typography>
                      <Typography variant="body2" paragraph>
                        {
                          character.structured_data
                            .additional_features_and_traits
                        }
                      </Typography>
                    </Box>
                  )}

                  {/* Legacy fields for backwards compatibility */}
                  {!character.structured_data && character.ai_narrative && (
                    <>
                      {character.ai_narrative.appearance && (
                        <Box mb={2}>
                          <Typography
                            variant="subtitle2"
                            color="primary"
                            gutterBottom
                          >
                            Appearance
                          </Typography>
                          <Typography variant="body2">
                            {character.ai_narrative.appearance}
                          </Typography>
                        </Box>
                      )}
                      {character.ai_narrative.personality && (
                        <Box mb={2}>
                          <Typography
                            variant="subtitle2"
                            color="primary"
                            gutterBottom
                          >
                            Personality
                          </Typography>
                          <Typography variant="body2">
                            {character.ai_narrative.personality}
                          </Typography>
                        </Box>
                      )}
                      {character.ai_narrative.backstory && (
                        <Box mb={2}>
                          <Typography
                            variant="subtitle2"
                            color="primary"
                            gutterBottom
                          >
                            Backstory
                          </Typography>
                          <Typography variant="body2">
                            {character.ai_narrative.backstory}
                          </Typography>
                        </Box>
                      )}
                    </>
                  )}
                </Box>
              </AccordionDetails>
            </Accordion>
          )}
        </Grid>
      </Grid>
    </Box>
  );
}
