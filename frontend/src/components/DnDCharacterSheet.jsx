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
      {/* Header with export options */}
      <Paper elevation={3} sx={{ p: 2, mb: 2 }}>
        <Box display="flex" justifyContent="space-between" alignItems="center">
          <Typography variant="h4" component="h1">
            {character.name}
          </Typography>
          <Box>
            <Tooltip title="Copy to Clipboard">
              <IconButton onClick={copyToClipboard}>
                <ContentCopyIcon />
              </IconButton>
            </Tooltip>
            <Tooltip title="Export as JSON">
              <IconButton onClick={exportToJSON}>
                <DownloadIcon />
              </IconButton>
            </Tooltip>
            <Tooltip title="Export as Text">
              <IconButton onClick={exportToText}>
                <DownloadIcon />
              </IconButton>
            </Tooltip>
            <Tooltip title="Print">
              <IconButton onClick={handlePrint}>
                <PrintIcon />
              </IconButton>
            </Tooltip>
          </Box>
        </Box>

        <Box display="flex" gap={1} mt={1} flexWrap="wrap">
          <Chip
            label={`Level ${character.dnd_level} ${character.dnd_class}`}
            color="primary"
          />
          <Chip label={character.dnd_species} color="secondary" />
          <Chip label={character.dnd_background} />
          {character.dnd_alignment && (
            <Chip label={character.dnd_alignment} variant="outlined" />
          )}
        </Box>
      </Paper>

      <Grid container spacing={2}>
        {/* Left Column - Ability Scores */}
        <Grid item xs={12} md={4}>
          <Paper elevation={2} sx={{ p: 2, mb: 2 }}>
            <Typography variant="h6" gutterBottom>
              Ability Scores
            </Typography>
            <Grid container spacing={1}>
              {character.dnd_ability_scores &&
                Object.entries(character.dnd_ability_scores).map(
                  ([ability, score]) => (
                    <Grid item xs={6} key={ability}>
                      <Card variant="outlined">
                        <CardContent sx={{ textAlign: "center", p: 1 }}>
                          <Typography
                            variant="caption"
                            color="text.secondary"
                            sx={{ textTransform: "uppercase" }}
                          >
                            {ability.substring(0, 3)}
                          </Typography>
                          <Typography variant="h4">{score}</Typography>
                          <Typography variant="body2" color="primary">
                            {getAbilityModifier(score)}
                          </Typography>
                        </CardContent>
                      </Card>
                    </Grid>
                  )
                )}
            </Grid>
          </Paper>

          {/* Combat Stats */}
          <Paper elevation={2} sx={{ p: 2, mb: 2 }}>
            <Typography variant="h6" gutterBottom>
              Combat Stats
            </Typography>
            <Box>
              <Box display="flex" justifyContent="space-between" py={1}>
                <Typography variant="body2" color="text.secondary">
                  Hit Points
                </Typography>
                <Typography variant="body1" fontWeight="bold">
                  {character.dnd_hit_points}
                </Typography>
              </Box>
              <Divider />
              <Box display="flex" justifyContent="space-between" py={1}>
                <Typography variant="body2" color="text.secondary">
                  Armor Class
                </Typography>
                <Typography variant="body1" fontWeight="bold">
                  {character.dnd_armor_class}
                </Typography>
              </Box>
              <Divider />
              <Box display="flex" justifyContent="space-between" py={1}>
                <Typography variant="body2" color="text.secondary">
                  Initiative
                </Typography>
                <Typography variant="body1" fontWeight="bold">
                  {character.dnd_initiative}
                </Typography>
              </Box>
              <Divider />
              <Box display="flex" justifyContent="space-between" py={1}>
                <Typography variant="body2" color="text.secondary">
                  Speed
                </Typography>
                <Typography variant="body1" fontWeight="bold">
                  {character.dnd_speed} ft
                </Typography>
              </Box>
              <Divider />
              <Box display="flex" justifyContent="space-between" py={1}>
                <Typography variant="body2" color="text.secondary">
                  Proficiency Bonus
                </Typography>
                <Typography variant="body1" fontWeight="bold">
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
                  {/* Physical Appearance */}
                  {(character.structured_data?.physical_appearance || character.ai_narrative?.appearance) && (
                    <Box mb={2}>
                      <Typography
                        variant="subtitle2"
                        color="primary"
                        gutterBottom
                      >
                        Physical Appearance
                      </Typography>
                      <Typography variant="body2" paragraph>
                        {character.structured_data?.physical_appearance || character.ai_narrative?.appearance}
                      </Typography>
                      {character.structured_data?.height_and_build && (
                        <Typography variant="body2" color="text.secondary" paragraph>
                          <strong>Build:</strong> {character.structured_data.height_and_build}
                        </Typography>
                      )}
                      {character.structured_data?.distinctive_features && (
                        <Box mt={1}>
                          <Typography variant="caption" color="text.secondary">
                            Distinctive Features:
                          </Typography>
                          <Box component="ul" sx={{ mt: 0.5, pl: 2 }}>
                            {character.structured_data.distinctive_features.map((feature, idx) => (
                              <Typography component="li" variant="body2" key={idx}>
                                {feature}
                              </Typography>
                            ))}
                          </Box>
                        </Box>
                      )}
                    </Box>
                  )}

                  {/* Personality */}
                  {(character.structured_data?.personality_summary || character.ai_narrative?.personality) && (
                    <Box mb={2}>
                      <Typography
                        variant="subtitle2"
                        color="primary"
                        gutterBottom
                      >
                        Personality
                      </Typography>
                      <Typography variant="body2" paragraph>
                        {character.structured_data?.personality_summary || character.ai_narrative?.personality}
                      </Typography>
                      {character.structured_data?.personality_traits && (
                        <Box mt={1}>
                          <Typography variant="caption" color="text.secondary">
                            Core Traits:
                          </Typography>
                          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mt: 0.5 }}>
                            {character.structured_data.personality_traits.map((trait, idx) => (
                              <Chip key={idx} label={trait} size="small" />
                            ))}
                          </Box>
                        </Box>
                      )}
                      {character.structured_data?.ideals && (
                        <Typography variant="body2" color="text.secondary" mt={1}>
                          <strong>Ideals:</strong> {character.structured_data.ideals}
                        </Typography>
                      )}
                      {character.structured_data?.bonds && (
                        <Typography variant="body2" color="text.secondary" mt={1}>
                          <strong>Bonds:</strong> {character.structured_data.bonds}
                        </Typography>
                      )}
                      {character.structured_data?.flaws && (
                        <Typography variant="body2" color="text.secondary" mt={1}>
                          <strong>Flaws:</strong> {character.structured_data.flaws}
                        </Typography>
                      )}
                    </Box>
                  )}

                  {/* Backstory */}
                  {(character.structured_data?.backstory || character.ai_narrative?.backstory) && (
                    <Box mb={2}>
                      <Typography
                        variant="subtitle2"
                        color="primary"
                        gutterBottom
                      >
                        Backstory
                      </Typography>
                      <Typography variant="body2" paragraph>
                        {character.structured_data?.backstory || character.ai_narrative?.backstory}
                      </Typography>
                      {character.structured_data?.formative_events && (
                        <Box mt={1}>
                          <Typography variant="caption" color="text.secondary">
                            Formative Events:
                          </Typography>
                          <Box component="ul" sx={{ mt: 0.5, pl: 2 }}>
                            {character.structured_data.formative_events.map((event, idx) => (
                              <Typography component="li" variant="body2" key={idx}>
                                {event}
                              </Typography>
                            ))}
                          </Box>
                        </Box>
                      )}
                    </Box>
                  )}

                  {/* Motivations */}
                  {(character.structured_data?.primary_motivation || character.ai_narrative?.motivations) && (
                    <Box mb={2}>
                      <Typography
                        variant="subtitle2"
                        color="primary"
                        gutterBottom
                      >
                        Motivations & Goals
                      </Typography>
                      {character.structured_data ? (
                        <>
                          <Typography variant="body2" paragraph>
                            {character.structured_data.primary_motivation}
                          </Typography>
                          {character.structured_data.short_term_goals && (
                            <Box mt={1}>
                              <Typography variant="caption">Short-term Goals:</Typography>
                              <Box component="ul" sx={{ pl: 2 }}>
                                {character.structured_data.short_term_goals.map((goal, idx) => (
                                  <Typography component="li" variant="body2" key={idx}>{goal}</Typography>
                                ))}
                              </Box>
                            </Box>
                          )}
                          {character.structured_data.long_term_goals && (
                            <Box mt={1}>
                              <Typography variant="caption">Long-term Goals:</Typography>
                              <Box component="ul" sx={{ pl: 2 }}>
                                {character.structured_data.long_term_goals.map((goal, idx) => (
                                  <Typography component="li" variant="body2" key={idx}>{goal}</Typography>
                                ))}
                              </Box>
                            </Box>
                          )}
                        </>
                      ) : (
                        <Typography variant="body2" paragraph>
                          {character.ai_narrative?.motivations}
                        </Typography>
                      )}
                    </Box>
                  )}

                  {/* Quirks */}
                  {(character.structured_data?.quirks || character.ai_narrative?.quirks) && (
                    <Box mb={2}>
                      <Typography
                        variant="subtitle2"
                        color="primary"
                        gutterBottom
                      >
                        Quirks & Mannerisms
                      </Typography>
                      {character.structured_data ? (
                        <>
                          {character.structured_data.quirks && character.structured_data.quirks.length > 0 && (
                            <Box component="ul" sx={{ pl: 2, mb: 1 }}>
                              {character.structured_data.quirks.map((quirk, idx) => (
                                <Typography component="li" variant="body2" key={idx}>
                                  {quirk}
                                </Typography>
                              ))}
                            </Box>
                          )}
                          {character.structured_data.speech_pattern && (
                            <Box mt={1}>
                              <Typography variant="caption">Speech Pattern:</Typography>
                              <Typography variant="body2">
                                {character.structured_data.speech_pattern}
                              </Typography>
                            </Box>
                          )}
                        </>
                      ) : (
                        <Typography variant="body2">
                          {character.ai_narrative.quirks}
                        </Typography>
                      )}
                    </Box>
                  )}

                  {/* Combat Style & Abilities */}
                  {(character.structured_data?.combat_style_narrative || character.structured_data?.signature_abilities) && (
                    <Box mb={2}>
                      <Typography
                        variant="subtitle2"
                        color="primary"
                        gutterBottom
                      >
                        Combat Style
                      </Typography>
                      {character.structured_data.combat_style_narrative && (
                        <Typography variant="body2" paragraph>
                          {character.structured_data.combat_style_narrative}
                        </Typography>
                      )}
                      {character.structured_data.signature_abilities && character.structured_data.signature_abilities.length > 0 && (
                        <Box mt={1}>
                          <Typography variant="caption">Signature Abilities:</Typography>
                          <Box component="ul" sx={{ pl: 2 }}>
                            {character.structured_data.signature_abilities.map((ability, idx) => (
                              <Typography component="li" variant="body2" key={idx}>
                                {ability}
                              </Typography>
                            ))}
                          </Box>
                        </Box>
                      )}
                    </Box>
                  )}

                  {/* Social Identity */}
                  {(character.structured_data?.reputation || character.structured_data?.allies_and_enemies) && (
                    <Box mb={2}>
                      <Typography
                        variant="subtitle2"
                        color="primary"
                        gutterBottom
                      >
                        Social Identity
                      </Typography>
                      {character.structured_data.reputation && (
                        <Box mb={1}>
                          <Typography variant="caption">Reputation:</Typography>
                          <Typography variant="body2">
                            {character.structured_data.reputation}
                          </Typography>
                        </Box>
                      )}
                      {character.structured_data.allies_and_enemies && (
                        <Box mt={1}>
                          <Typography variant="caption">Allies & Enemies:</Typography>
                          <Typography variant="body2">
                            {character.structured_data.allies_and_enemies}
                          </Typography>
                        </Box>
                      )}
                    </Box>
                  )}

                  {/* Character Arc Potential */}
                  {character.structured_data?.character_arc_potential && (
                    <Box mb={2}>
                      <Typography
                        variant="subtitle2"
                        color="primary"
                        gutterBottom
                      >
                        Character Arc Potential
                      </Typography>
                      <Typography variant="body2">
                        {character.structured_data.character_arc_potential}
                      </Typography>
                    </Box>
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
