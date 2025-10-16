import { useState, useEffect } from "react";
import {
  Box,
  Paper,
  Typography,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  Button,
  Grid,
  Chip,
  Alert,
  CircularProgress,
  Divider,
  FormControlLabel,
  Switch,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Tooltip,
  IconButton,
  RadioGroup,
  Radio,
} from "@mui/material";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import InfoOutlinedIcon from "@mui/icons-material/InfoOutlined";
import CasinoIcon from "@mui/icons-material/Casino";
import AutoAwesomeIcon from "@mui/icons-material/AutoAwesome";
import ShuffleIcon from "@mui/icons-material/Shuffle";
import axios from "axios";
import ModelSelector from "./ModelSelector";
import { API_URL } from "../config/api";

/**
 * DnDCharacterCreator Component
 *
 * Comprehensive D&D 5E character creation interface with AI assistance
 * for narrative aspects (backstory, personality, appearance, etc.)
 */
export default function DnDCharacterCreator({ onCharacterGenerated, onError }) {
  // D&D Reference Data
  const [classes, setClasses] = useState([]);
  const [species, setSpecies] = useState([]);
  const [backgrounds, setBackgrounds] = useState([]);
  const [alignments, setAlignments] = useState([]);

  // Character Creation Form State
  const [characterName, setCharacterName] = useState("");
  const [selectedClass, setSelectedClass] = useState("");
  const [selectedSpecies, setSelectedSpecies] = useState("");
  const [selectedBackground, setSelectedBackground] = useState("");
  const [selectedAlignment, setSelectedAlignment] = useState("");
  const [characterLevel, setCharacterLevel] = useState(1);
  const [abilityScoreMethod, setAbilityScoreMethod] =
    useState("standard_array");

  // AI-Assisted Narrative Generation
  const [useAINarrative, setUseAINarrative] = useState(true);
  const [narrativePrompt, setNarrativePrompt] = useState("");
  const [narrativeStyle, setNarrativeStyle] = useState("detailed"); // detailed, concise, dramatic
  const [generateAppearance, setGenerateAppearance] = useState(true);
  const [generatePersonality, setGeneratePersonality] = useState(true);
  const [generateBackstory, setGenerateBackstory] = useState(true);
  const [generateMotivations, setGenerateMotivations] = useState(true);
  const [generateQuirks, setGenerateQuirks] = useState(true);

  // LLM Provider Selection for narrative generation
  const [provider, setProvider] = useState("groq");
  const [model, setModel] = useState("");

  // Structured Output Toggle
  const [useStructured, setUseStructured] = useState(true);

  // Portrait Generation
  const [generatePortrait, setGeneratePortrait] = useState(false);
  const [portraitStyle, setPortraitStyle] = useState("fantasy_art");

  // Loading States
  const [loadingData, setLoadingData] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [dataError, setDataError] = useState(null);

  // Selected Data Details (for display)
  const [classDetails, setClassDetails] = useState(null);
  const [speciesDetails, setSpeciesDetails] = useState(null);
  const [backgroundDetails, setBackgroundDetails] = useState(null);

  // Load D&D reference data on mount
  useEffect(() => {
    loadDnDData();
  }, []);

  // Update details when selections change
  useEffect(() => {
    if (selectedClass) {
      const cls = classes.find((c) => c.id === selectedClass);
      setClassDetails(cls);
    }
  }, [selectedClass, classes]);

  useEffect(() => {
    if (selectedSpecies) {
      const spec = species.find((s) => s.id === selectedSpecies);
      setSpeciesDetails(spec);
    }
  }, [selectedSpecies, species]);

  useEffect(() => {
    if (selectedBackground) {
      const bg = backgrounds.find((b) => b.id === selectedBackground);
      setBackgroundDetails(bg);
    }
  }, [selectedBackground, backgrounds]);

  const loadDnDData = async () => {
    setLoadingData(true);
    setDataError(null);

    try {
      // Load all D&D reference data in parallel
      const [classesRes, speciesRes, backgroundsRes, alignmentsRes] =
        await Promise.all([
          axios.get(`${API_URL}/api/characters/dnd/classes`),
          axios.get(`${API_URL}/api/characters/dnd/species`),
          axios.get(`${API_URL}/api/characters/dnd/backgrounds`),
          axios.get(`${API_URL}/api/characters/dnd/alignments`),
        ]);

      setClasses(classesRes.data.classes || []);
      setSpecies(speciesRes.data.species || []);
      setBackgrounds(backgroundsRes.data.backgrounds || []);
      setAlignments(alignmentsRes.data.alignments || []);

      setLoadingData(false);
    } catch (error) {
      console.error("Failed to load D&D data:", error);
      setDataError("Failed to load D&D reference data. Please try again.");
      setLoadingData(false);
      if (onError) {
        onError(error.message || "Failed to load D&D data");
      }
    }
  };

  const handleRandomizeSelection = () => {
    if (classes.length > 0) {
      const randomClass = classes[Math.floor(Math.random() * classes.length)];
      setSelectedClass(randomClass.id);
    }
    if (species.length > 0) {
      const randomSpecies = species[Math.floor(Math.random() * species.length)];
      setSelectedSpecies(randomSpecies.id);
    }
    if (backgrounds.length > 0) {
      const randomBg =
        backgrounds[Math.floor(Math.random() * backgrounds.length)];
      setSelectedBackground(randomBg.id);
    }
    if (alignments.length > 0) {
      const randomAlign =
        alignments[Math.floor(Math.random() * alignments.length)];
      setSelectedAlignment(randomAlign);
    }
  };

  const generateCharacter = async () => {
    // Validation
    if (!selectedClass || !selectedSpecies || !selectedBackground) {
      if (onError) {
        onError("Please select a class, species, and background.");
      }
      return;
    }

    setGenerating(true);

    try {
      // Step 1: Generate D&D stats
      const dndRequest = {
        name: characterName || null,
        dnd_class: selectedClass,
        dnd_species: selectedSpecies,
        dnd_background: selectedBackground,
        dnd_alignment: selectedAlignment || null,
        dnd_level: characterLevel,
        ability_score_method: abilityScoreMethod,

        // AI Narrative Generation (backend handles structured generation)
        generate_narrative: useAINarrative,
        narrative_provider: provider,
        narrative_model: model || null,
        use_structured: useStructured,
        narrative_style: narrativeStyle,
        narrative_context: narrativePrompt || null,
      };

      const dndResponse = await axios.post(
        `${API_URL}/api/characters/dnd/generate`,
        dndRequest
      );

      const character = dndResponse.data;

      // Parse JSON strings from SQLite TEXT columns
      if (
        character.structured_data &&
        typeof character.structured_data === "string"
      ) {
        try {
          character.structured_data = JSON.parse(character.structured_data);
        } catch (e) {
          console.error("Failed to parse structured_data:", e);
        }
      }

      // Debug: Log the structured_data to see what we got
      console.log("Character structured_data:", character.structured_data);
      console.log("Character generation_log:", character.generation_log);
      if (
        character.generation_log &&
        typeof character.generation_log === "string"
      ) {
        try {
          character.generation_log = JSON.parse(character.generation_log);
        } catch (e) {
          console.error("Failed to parse generation_log:", e);
        }
      }

      // Note: AI narrative is now generated by backend using structured output
      // The backend handles narrative generation with DnDCharacterNarrative schema

      // Step 2: Generate portrait if enabled
      if (generatePortrait && character.id) {
        try {
          const portraitResponse = await generateCharacterPortrait(character);
          character.portrait_image = portraitResponse.portrait_image;
          character.image_prompt = portraitResponse.image_prompt;
        } catch (portraitError) {
          console.error("Portrait generation failed:", portraitError);
          // Continue without portrait
        }
      }

      setGenerating(false);

      if (onCharacterGenerated) {
        onCharacterGenerated(character);
      }
    } catch (error) {
      console.error("Character generation failed:", error);
      setGenerating(false);

      if (onError) {
        const errorMsg =
          error.response?.data?.detail ||
          error.message ||
          "Character generation failed";
        onError(errorMsg);
      }
    }
  };

  /**
   * Generate AI-enhanced narrative aspects based on D&D stats
   */
  const generateNarrativeEnhancements = async (character) => {
    const narrativePrompts = buildNarrativePrompts(character);
    const enhancements = {};

    try {
      // Generate all narrative aspects in parallel
      const promises = [];

      if (generateAppearance) {
        promises.push(
          generateNarrativeAspect(narrativePrompts.appearance, "appearance")
        );
      }

      if (generatePersonality) {
        promises.push(
          generateNarrativeAspect(narrativePrompts.personality, "personality")
        );
      }

      if (generateBackstory) {
        promises.push(
          generateNarrativeAspect(narrativePrompts.backstory, "backstory")
        );
      }

      if (generateMotivations) {
        promises.push(
          generateNarrativeAspect(narrativePrompts.motivations, "motivations")
        );
      }

      if (generateQuirks) {
        promises.push(
          generateNarrativeAspect(narrativePrompts.quirks, "quirks")
        );
      }

      const results = await Promise.allSettled(promises);

      results.forEach((result, index) => {
        if (result.status === "fulfilled") {
          const { aspect, content } = result.value;
          enhancements[aspect] = content;
        }
      });

      return enhancements;
    } catch (error) {
      console.error("Narrative generation failed:", error);
      return {};
    }
  };

  /**
   * Build context-aware prompts for narrative generation
   */
  const buildNarrativePrompts = (character) => {
    const classInfo = classes.find((c) => c.id === character.dnd_class);
    const speciesInfo = species.find((s) => s.id === character.dnd_species);
    const backgroundInfo = backgrounds.find(
      (b) => b.id === character.dnd_background
    );

    const baseContext = `
Character: ${character.name || "unnamed"}
Class: ${classInfo?.name || character.dnd_class}
Species: ${speciesInfo?.name || character.dnd_species}
Background: ${backgroundInfo?.name || character.dnd_background}
Alignment: ${character.dnd_alignment || "unaligned"}
Level: ${character.dnd_level}

Ability Scores:
- Strength: ${character.dnd_ability_scores?.strength || 10}
- Dexterity: ${character.dnd_ability_scores?.dexterity || 10}
- Constitution: ${character.dnd_ability_scores?.constitution || 10}
- Intelligence: ${character.dnd_ability_scores?.intelligence || 10}
- Wisdom: ${character.dnd_ability_scores?.wisdom || 10}
- Charisma: ${character.dnd_ability_scores?.charisma || 10}

Additional Context: ${narrativePrompt || "none"}
`;

    return {
      appearance: `${baseContext}

Generate a vivid, detailed physical appearance description for this D&D character.
Consider their species traits, class, and ability scores (especially Strength, Dexterity, Constitution, and Charisma).
Include: body build, facial features, distinctive marks, clothing/armor style, and overall presence.
Style: ${narrativeStyle}
Length: 3-4 sentences.`,

      personality: `${baseContext}

Generate a rich personality profile for this D&D character.
Consider their alignment, background, class philosophy, and mental ability scores (Intelligence, Wisdom, Charisma).
Include: core traits, behavioral patterns, social tendencies, and emotional characteristics.
Style: ${narrativeStyle}
Length: 3-4 sentences.`,

      backstory: `${baseContext}

Generate a compelling backstory for this D&D character.
Consider their background feature, species history, class training origin, and alignment influences.
Include: origins, formative experiences, key relationships, and path to becoming an adventurer.
Style: ${narrativeStyle}
Length: 4-6 sentences.`,

      motivations: `${baseContext}

Generate clear motivations and goals for this D&D character.
Consider their background, alignment, class ideology, and what drives them to adventure.
Include: primary goal, secondary objectives, personal desires, and fears/concerns.
Style: ${narrativeStyle}
Length: 2-3 sentences.`,

      quirks: `${baseContext}

Generate memorable quirks, habits, and mannerisms for this D&D character.
Consider their species traits, background experiences, and personality tendencies.
Include: speech patterns, nervous habits, unique behaviors, and notable preferences.
Style: ${narrativeStyle}
Length: 2-3 distinctive quirks.`,
    };
  };

  /**
   * Generate a single narrative aspect using the LLM API
   */
  const generateNarrativeAspect = async (prompt, aspectName) => {
    try {
      const response = await axios.post(`${API_URL}/api/llm/generate-text`, {
        prompt: prompt,
        provider: provider,
        model: model || undefined, // Let backend choose default if not specified
        max_tokens: 500,
        structured: useStructured,
      });

      return {
        aspect: aspectName,
        content: response.data.text || response.data.content || "",
      };
    } catch (error) {
      console.error(`Failed to generate ${aspectName}:`, error);
      throw error;
    }
  };

  /**
   * Generate character portrait using the image API
   */
  const generateCharacterPortrait = async (character) => {
    const classInfo = classes.find((c) => c.id === character.dnd_class);
    const speciesInfo = species.find((s) => s.id === character.dnd_species);

    // Build D&D-specific portrait prompt with species and class details
    const speciesName = speciesInfo?.name || character.dnd_species;
    const className = classInfo?.name || character.dnd_class;

    // Add appearance details from structured_data if available
    let appearanceDetails = "";
    if (character.structured_data?.character_appearance) {
      appearanceDetails = character.structured_data.character_appearance;
    }

    // Build comprehensive D&D fantasy portrait prompt
    const portraitPrompt = `A ${portraitStyle} fantasy RPG character portrait of ${character.name}, a ${speciesName} ${className}. ${appearanceDetails} Dungeons & Dragons character art style, professional fantasy illustration, detailed armor and equipment, dramatic lighting, heroic pose, high quality digital art, trending on artstation.${narrativePrompt ? ` Additional context: ${narrativePrompt}` : ""}`;

    const response = await axios.post(
      `${API_URL}/api/characters/${character.id}/generate-portrait`,
      {
        style: portraitStyle,
        custom_prompt: portraitPrompt,
      }
    );

    return response.data;
  };

  if (loadingData) {
    return (
      <Box
        display="flex"
        justifyContent="center"
        alignItems="center"
        minHeight="400px"
      >
        <CircularProgress />
        <Typography variant="body1" sx={{ ml: 2 }}>
          Loading D&D data...
        </Typography>
      </Box>
    );
  }

  if (dataError) {
    return (
      <Alert severity="error" sx={{ mb: 2 }}>
        {dataError}
        <Button onClick={loadDnDData} sx={{ ml: 2 }}>
          Retry
        </Button>
      </Alert>
    );
  }

  return (
    <Box>
      <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
        <Typography
          variant="h5"
          gutterBottom
          sx={{ display: "flex", alignItems: "center" }}
        >
          <CasinoIcon sx={{ mr: 1 }} />
          D&D 5E Character Creator
        </Typography>

        <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
          Create a complete D&D 5th Edition character with stats, equipment, and
          AI-generated narrative.
        </Typography>

        <Divider sx={{ my: 2 }} />

        {/* Quick Randomize Button */}
        <Box sx={{ mb: 3 }}>
          <Button
            variant="outlined"
            startIcon={<ShuffleIcon />}
            onClick={handleRandomizeSelection}
            fullWidth
          >
            Randomize All Selections
          </Button>
        </Box>

        <Grid container spacing={3}>
          {/* Character Name */}
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Character Name (Optional)"
              value={characterName}
              onChange={(e) => setCharacterName(e.target.value)}
              placeholder="Leave blank to auto-generate"
              helperText="AI can suggest a name based on your selections"
            />
          </Grid>

          {/* Class Selection */}
          <Grid item xs={12} md={6}>
            <FormControl fullWidth required>
              <InputLabel>Class</InputLabel>
              <Select
                value={selectedClass}
                onChange={(e) => setSelectedClass(e.target.value)}
                label="Class"
              >
                {classes.map((cls) => (
                  <MenuItem key={cls.id} value={cls.id}>
                    {cls.name} (d{cls.hit_die} hit die)
                    {cls.spellcaster && " ✨"}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            {classDetails && (
              <Box
                sx={{ mt: 1, p: 1, bgcolor: "action.hover", borderRadius: 1 }}
              >
                <Typography variant="caption" display="block">
                  <strong>Primary:</strong>{" "}
                  {classDetails.primary_ability.join(", ")}
                </Typography>
                <Typography variant="caption" display="block">
                  <strong>Saves:</strong>{" "}
                  {classDetails.saving_throws.join(", ")}
                </Typography>
                <Typography
                  variant="caption"
                  display="block"
                  color="text.secondary"
                >
                  {classDetails.description}
                </Typography>
              </Box>
            )}
          </Grid>

          {/* Species Selection */}
          <Grid item xs={12} md={6}>
            <FormControl fullWidth required>
              <InputLabel>Species</InputLabel>
              <Select
                value={selectedSpecies}
                onChange={(e) => setSelectedSpecies(e.target.value)}
                label="Species"
              >
                {species.map((spec) => (
                  <MenuItem key={spec.id} value={spec.id}>
                    {spec.name} ({spec.size}, {spec.speed} ft)
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            {speciesDetails && (
              <Box
                sx={{ mt: 1, p: 1, bgcolor: "action.hover", borderRadius: 1 }}
              >
                <Typography variant="caption" display="block">
                  <strong>Traits:</strong> {speciesDetails.traits.join(", ")}
                </Typography>
                <Typography
                  variant="caption"
                  display="block"
                  color="text.secondary"
                >
                  {speciesDetails.description}
                </Typography>
              </Box>
            )}
          </Grid>

          {/* Background Selection */}
          <Grid item xs={12} md={6}>
            <FormControl fullWidth required>
              <InputLabel>Background</InputLabel>
              <Select
                value={selectedBackground}
                onChange={(e) => setSelectedBackground(e.target.value)}
                label="Background"
              >
                {backgrounds.map((bg) => (
                  <MenuItem key={bg.id} value={bg.id}>
                    {bg.name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            {backgroundDetails && (
              <Box
                sx={{ mt: 1, p: 1, bgcolor: "action.hover", borderRadius: 1 }}
              >
                <Typography variant="caption" display="block">
                  <strong>Skills:</strong>{" "}
                  {backgroundDetails.skill_proficiencies.join(", ")}
                </Typography>
                <Typography variant="caption" display="block">
                  <strong>Feature:</strong> {backgroundDetails.feature}
                </Typography>
                <Typography
                  variant="caption"
                  display="block"
                  color="text.secondary"
                >
                  {backgroundDetails.description}
                </Typography>
              </Box>
            )}
          </Grid>

          {/* Alignment Selection */}
          <Grid item xs={12} md={6}>
            <FormControl fullWidth>
              <InputLabel>Alignment (Optional)</InputLabel>
              <Select
                value={selectedAlignment}
                onChange={(e) => setSelectedAlignment(e.target.value)}
                label="Alignment (Optional)"
              >
                <MenuItem value="">
                  <em>None (Random)</em>
                </MenuItem>
                {alignments.map((alignment) => (
                  <MenuItem key={alignment} value={alignment}>
                    {alignment}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>

          {/* Level & Ability Score Method */}
          <Grid item xs={12} md={6}>
            <FormControl fullWidth>
              <InputLabel>Level</InputLabel>
              <Select
                value={characterLevel}
                onChange={(e) => setCharacterLevel(e.target.value)}
                label="Level"
              >
                {[1, 2, 3, 4, 5].map((level) => (
                  <MenuItem key={level} value={level}>
                    Level {level}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12} md={6}>
            <FormControl fullWidth>
              <InputLabel>Ability Score Method</InputLabel>
              <Select
                value={abilityScoreMethod}
                onChange={(e) => setAbilityScoreMethod(e.target.value)}
                label="Ability Score Method"
              >
                <MenuItem value="standard_array">
                  Standard Array [15, 14, 13, 12, 10, 8]
                </MenuItem>
                <MenuItem value="random">Random (4d6 drop lowest)</MenuItem>
              </Select>
            </FormControl>
          </Grid>
        </Grid>

        <Divider sx={{ my: 3 }} />

        {/* AI Narrative Enhancement Section */}
        <Accordion defaultExpanded>
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Typography
              variant="h6"
              sx={{ display: "flex", alignItems: "center" }}
            >
              <AutoAwesomeIcon sx={{ mr: 1 }} />
              AI Narrative Enhancement
            </Typography>
          </AccordionSummary>
          <AccordionDetails>
            <FormControlLabel
              control={
                <Switch
                  checked={useAINarrative}
                  onChange={(e) => setUseAINarrative(e.target.checked)}
                />
              }
              label="Generate AI-enhanced narrative aspects"
            />

            {useAINarrative && (
              <Box sx={{ mt: 2 }}>
                {/* LLM Provider and Model Selection */}
                <Box sx={{ mb: 3 }}>
                  <Typography variant="subtitle2" gutterBottom>
                    LLM Provider for Narrative Generation:
                  </Typography>
                  <ModelSelector
                    provider={provider}
                    model={model}
                    onProviderChange={setProvider}
                    onModelChange={setModel}
                  />
                </Box>

                {/* Structured Output Toggle */}
                <Box sx={{ mb: 2 }}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={useStructured}
                        onChange={(e) => setUseStructured(e.target.checked)}
                        size="small"
                      />
                    }
                    label={
                      <Box
                        sx={{ display: "flex", alignItems: "center", gap: 1 }}
                      >
                        <Typography variant="body2">
                          Use Structured Output
                        </Typography>
                        <Tooltip title="Structured output provides more consistent, formatted responses following a schema">
                          <InfoOutlinedIcon fontSize="small" color="action" />
                        </Tooltip>
                        <Chip
                          label="Recommended"
                          size="small"
                          color="primary"
                          sx={{ fontSize: "0.7rem" }}
                        />
                      </Box>
                    }
                  />
                </Box>

                <Divider sx={{ my: 2 }} />

                <TextField
                  fullWidth
                  multiline
                  rows={3}
                  label="Additional Context (Optional)"
                  value={narrativePrompt}
                  onChange={(e) => setNarrativePrompt(e.target.value)}
                  placeholder="Add any specific details you want included in the narrative..."
                  sx={{ mb: 2 }}
                />

                <FormControl fullWidth sx={{ mb: 2 }}>
                  <InputLabel>Narrative Style</InputLabel>
                  <Select
                    value={narrativeStyle}
                    onChange={(e) => setNarrativeStyle(e.target.value)}
                    label="Narrative Style"
                  >
                    <MenuItem value="concise">
                      Concise (Brief descriptions)
                    </MenuItem>
                    <MenuItem value="detailed">
                      Detailed (Rich descriptions)
                    </MenuItem>
                    <MenuItem value="dramatic">
                      Dramatic (Epic storytelling)
                    </MenuItem>
                  </Select>
                </FormControl>

                <Typography variant="subtitle2" gutterBottom>
                  Generate:
                </Typography>

                <Grid container spacing={1}>
                  <Grid item xs={6} sm={4}>
                    <FormControlLabel
                      control={
                        <Switch
                          checked={generateAppearance}
                          onChange={(e) =>
                            setGenerateAppearance(e.target.checked)
                          }
                          size="small"
                        />
                      }
                      label="Appearance"
                    />
                  </Grid>
                  <Grid item xs={6} sm={4}>
                    <FormControlLabel
                      control={
                        <Switch
                          checked={generatePersonality}
                          onChange={(e) =>
                            setGeneratePersonality(e.target.checked)
                          }
                          size="small"
                        />
                      }
                      label="Personality"
                    />
                  </Grid>
                  <Grid item xs={6} sm={4}>
                    <FormControlLabel
                      control={
                        <Switch
                          checked={generateBackstory}
                          onChange={(e) =>
                            setGenerateBackstory(e.target.checked)
                          }
                          size="small"
                        />
                      }
                      label="Backstory"
                    />
                  </Grid>
                  <Grid item xs={6} sm={4}>
                    <FormControlLabel
                      control={
                        <Switch
                          checked={generateMotivations}
                          onChange={(e) =>
                            setGenerateMotivations(e.target.checked)
                          }
                          size="small"
                        />
                      }
                      label="Motivations"
                    />
                  </Grid>
                  <Grid item xs={6} sm={4}>
                    <FormControlLabel
                      control={
                        <Switch
                          checked={generateQuirks}
                          onChange={(e) => setGenerateQuirks(e.target.checked)}
                          size="small"
                        />
                      }
                      label="Quirks"
                    />
                  </Grid>
                </Grid>
              </Box>
            )}
          </AccordionDetails>
        </Accordion>

        {/* Portrait Generation Section */}
        <Accordion>
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Typography variant="h6">🎨 Character Portrait</Typography>
          </AccordionSummary>
          <AccordionDetails>
            <FormControlLabel
              control={
                <Switch
                  checked={generatePortrait}
                  onChange={(e) => setGeneratePortrait(e.target.checked)}
                />
              }
              label="Generate character portrait"
            />

            {generatePortrait && (
              <FormControl fullWidth sx={{ mt: 2 }}>
                <InputLabel>Portrait Style</InputLabel>
                <Select
                  value={portraitStyle}
                  onChange={(e) => setPortraitStyle(e.target.value)}
                  label="Portrait Style"
                >
                  <MenuItem value="fantasy_art">Fantasy Art</MenuItem>
                  <MenuItem value="realistic">Realistic</MenuItem>
                  <MenuItem value="anime">Anime</MenuItem>
                  <MenuItem value="oil_painting">Oil Painting</MenuItem>
                  <MenuItem value="digital_art">Digital Art</MenuItem>
                </Select>
              </FormControl>
            )}
          </AccordionDetails>
        </Accordion>

        <Divider sx={{ my: 3 }} />

        {/* Generate Button */}
        <Button
          variant="contained"
          size="large"
          fullWidth
          onClick={generateCharacter}
          disabled={
            generating ||
            !selectedClass ||
            !selectedSpecies ||
            !selectedBackground
          }
          startIcon={
            generating ? <CircularProgress size={20} /> : <AutoAwesomeIcon />
          }
          sx={{ mt: 2 }}
        >
          {generating ? "Generating Character..." : "Generate D&D Character"}
        </Button>

        {generating && (
          <Alert severity="info" sx={{ mt: 2 }}>
            <Typography variant="body2">
              Generating your D&D character with stats, equipment, and
              narrative...
              {useAINarrative && " Including AI-enhanced descriptions..."}
            </Typography>
          </Alert>
        )}
      </Paper>
    </Box>
  );
}
