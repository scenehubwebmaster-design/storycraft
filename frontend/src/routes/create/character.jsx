import {
  createFileRoute,
  useNavigate,
  useSearch,
} from "@tanstack/react-router";
import { useState, useEffect } from "react";
import axios from "axios";
import {
  Container,
  Typography,
  Box,
  Button,
  Grid,
  Paper,
  Alert,
  CircularProgress,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  Stepper,
  Step,
  StepLabel,
  Divider,
  Switch,
  FormControlLabel,
  Chip,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Tooltip,
  IconButton,
  Card,
  CardContent,
} from "@mui/material";
import AutoAwesomeIcon from "@mui/icons-material/AutoAwesome";
import NavigateNextIcon from "@mui/icons-material/NavigateNext";
import NavigateBeforeIcon from "@mui/icons-material/NavigateBefore";
import PhotoCameraIcon from "@mui/icons-material/PhotoCamera";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import PublicIcon from "@mui/icons-material/Public";
import InfoOutlinedIcon from "@mui/icons-material/InfoOutlined";
import ShuffleIcon from "@mui/icons-material/Shuffle";
import SettingsIcon from "@mui/icons-material/Settings";
import PromptSelector from "../../components/PromptSelector";
import GenerationResult from "../../components/GenerationResult";
import ModelSelector from "../../components/ModelSelector";
import StructuredCharacterDisplay from "../../components/StructuredCharacterDisplay";
import DnDCharacterCreator from "../../components/DnDCharacterCreator";
import DnDCharacterSheet from "../../components/DnDCharacterSheet";
import { API_URL } from "../../config/api";

export const Route = createFileRoute("/create/character")({
  component: CreateCharacterComponent,
});

const steps = ["Select Traits", "Generate", "Review & Save"];

function CreateCharacterComponent() {
  console.log("CreateCharacterComponent mounted!");

  const navigate = useNavigate();
  const searchParams = useSearch({ from: "/create/character" });
  const editId = searchParams?.edit;
  const isEditMode = !!editId;

  // State for prompt options
  const [options, setOptions] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  // State for character generation
  const [activeStep, setActiveStep] = useState(0);
  const [selectedThemes, setSelectedThemes] = useState([]);
  const [selectedPersonalityTraits, setSelectedPersonalityTraits] = useState(
    []
  );
  const [selectedPhysicalTraits, setSelectedPhysicalTraits] = useState([]);
  const [selectedEmotionalTraits, setSelectedEmotionalTraits] = useState([]);
  const [selectedArchetype, setSelectedArchetype] = useState("");
  const [customDetails, setCustomDetails] = useState("");
  const [provider, setProvider] = useState("groq");
  const [model, setModel] = useState("");

  // Phase 1 & 2: Genre variations and cultural origins
  const [selectedGenre, setSelectedGenre] = useState("");
  const [selectedVariation, setSelectedVariation] = useState("");
  const [selectedCulturalOrigin, setSelectedCulturalOrigin] = useState("");
  const [variations, setVariations] = useState(null);
  const [culturalOrigins, setCulturalOrigins] = useState(null);

  // Structured generation toggle
  const [useStructured, setUseStructured] = useState(true);

  // D&D Mode toggle
  const [isDnDMode, setIsDnDMode] = useState(false);
  const [dndCharacter, setDndCharacter] = useState(null);
  const [dndRegenerationKey, setDndRegenerationKey] = useState(0); // Key to force DnDCharacterCreator remount

  // Generation results
  const [generatedContent, setGeneratedContent] = useState(null);
  const [generating, setGenerating] = useState(false);
  const [saving, setSaving] = useState(false);

  // Character name for saving
  const [characterName, setCharacterName] = useState("");

  // Portrait generation state
  const [portraitImage, setPortraitImage] = useState(null);
  const [imagePrompt, setImagePrompt] = useState(null);
  const [generatingPortrait, setGeneratingPortrait] = useState(false);
  const [portraitError, setPortraitError] = useState(null);
  const [imageProvider, setImageProvider] = useState("openai"); // Default to OpenAI
  const [imageModel, setImageModel] = useState("dall-e-3"); // Default DALL-E 3 (more widely available)
  const [imageStyle, setImageStyle] = useState("realistic"); // Style preset
  const [imageQuality, setImageQuality] = useState("standard"); // Quality setting
  const [showPortraitSettings, setShowPortraitSettings] = useState(false); // Toggle for portrait settings

  // Load prompt options on mount
  useEffect(() => {
    console.log("useEffect running - loading options");
    loadOptions();
    loadVariations();
    loadCulturalOrigins();

    // Load existing character data if in edit mode
    if (isEditMode && editId) {
      loadCharacterData(editId);
    }
  }, [editId, isEditMode]);

  const loadOptions = async () => {
    console.log(
      "loadOptions called, fetching from:",
      `${API_URL}/api/generate/options`
    );
    try {
      const response = await axios.get(`${API_URL}/api/generate/options`);
      setOptions(response.data);
    } catch (err) {
      setError("Failed to load prompt options");
      console.error(err);
    }
  };

  const loadVariations = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/generate/variations`);
      setVariations(response.data);
    } catch (err) {
      console.error("Failed to load variations:", err);
    }
  };

  const loadCulturalOrigins = async () => {
    try {
      const response = await axios.get(
        `${API_URL}/api/generate/cultural-origins`
      );
      setCulturalOrigins(response.data);
    } catch (err) {
      console.error("Failed to load cultural origins:", err);
    }
  };

  const loadCharacterData = async (characterId) => {
    setLoading(true);
    try {
      const response = await axios.get(
        `${API_URL}/api/characters/${characterId}`
      );
      const character = response.data;

      // Pre-populate form with existing data
      setCharacterName(character.name || "");

      // Check if character has structured data (from structured generation)
      if (character.structured_data) {
        // Parse structured data if it's a JSON string
        let structuredData = character.structured_data;
        if (typeof structuredData === "string") {
          try {
            structuredData = JSON.parse(structuredData);
          } catch (e) {
            console.error("Failed to parse structured_data:", e);
          }
        }

        // Use structured data for editing
        if (typeof structuredData === "object") {
          setGeneratedContent(structuredData);
          setUseStructured(true);
        } else {
          // Fallback to description
          setGeneratedContent(character.description || "");
          setUseStructured(false);
        }
      } else {
        // Legacy character without structured data
        setGeneratedContent(character.description || "");
        setUseStructured(false);
      }

      setPortraitImage(character.portrait_image || null);
      setImagePrompt(character.image_prompt || null);

      // Skip to review step if we have generated content
      if (character.structured_data || character.description) {
        setActiveStep(2);
      }

      setSuccess("Character data loaded for editing");
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to load character");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerate = async () => {
    setGenerating(true);
    setError(null);

    try {
      const endpoint = useStructured
        ? `${API_URL}/api/generate/character/structured`
        : `${API_URL}/api/generate/character`;

      const response = await axios.post(endpoint, {
        themes: selectedThemes.length > 0 ? selectedThemes : null,
        personality_traits:
          selectedPersonalityTraits.length > 0
            ? selectedPersonalityTraits
            : null,
        physical_traits:
          selectedPhysicalTraits.length > 0 ? selectedPhysicalTraits : null,
        emotional_traits:
          selectedEmotionalTraits.length > 0 ? selectedEmotionalTraits : null,
        archetype: selectedArchetype || null,
        custom_details: customDetails || null,
        provider,
        model: model || null,
        // Phase 1 & 2: Genre variation and cultural origin
        genre: selectedGenre || null,
        variation: selectedVariation || null,
        cultural_origin: selectedCulturalOrigin || null,
      });

      setGeneratedContent(
        useStructured ? response.data : response.data.content
      );
      setActiveStep(2);
      setSuccess(
        `Character generated successfully using ${useStructured ? "structured" : "free-form"} generation!`
      );
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to generate character");
      console.error(err);
    } finally {
      setGenerating(false);
    }
  };

  const handleRefine = async (refinementInstructions) => {
    setGenerating(true);
    setError(null);

    try {
      // For structured generation, we'll regenerate with refinement instructions
      // For free-form, use the existing refinement endpoint
      const endpoint = useStructured
        ? `${API_URL}/api/generate/character/structured`
        : `${API_URL}/api/generate/character`;

      const requestData = useStructured
        ? {
            themes: selectedThemes.length > 0 ? selectedThemes : null,
            personality_traits:
              selectedPersonalityTraits.length > 0
                ? selectedPersonalityTraits
                : null,
            physical_traits:
              selectedPhysicalTraits.length > 0 ? selectedPhysicalTraits : null,
            emotional_traits:
              selectedEmotionalTraits.length > 0
                ? selectedEmotionalTraits
                : null,
            archetype: selectedArchetype || null,
            custom_details: `${customDetails}\n\nRefinement: ${refinementInstructions}`,
            provider,
            model: model || null,
            // Phase 1 & 2: Genre variation and cultural origin
            genre: selectedGenre || null,
            variation: selectedVariation || null,
            cultural_origin: selectedCulturalOrigin || null,
          }
        : {
            base_content: generatedContent,
            refinement_instructions: refinementInstructions,
            provider,
            model: model || null,
          };

      const response = await axios.post(endpoint, requestData);

      setGeneratedContent(
        useStructured ? response.data : response.data.content
      );
      setSuccess("Character refined successfully!");
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to refine character");
      console.error(err);
    } finally {
      setGenerating(false);
    }
  };

  const handleSave = async (finalContent) => {
    if (!characterName.trim()) {
      setError("Please enter a character name");
      return;
    }

    setSaving(true);
    setError(null);

    try {
      if (isEditMode && editId) {
        // Update existing character
        const updateData = {
          name: characterName,
          portrait_image: portraitImage,
          image_prompt: imagePrompt,
        };

        // Add structured data or plain description based on mode
        // Only include if we have content to update (user regenerated or modified)
        if (useStructured) {
          const contentToSave = finalContent || generatedContent;
          if (contentToSave) {
            updateData.structured_data = JSON.stringify(contentToSave);
            // Also update description field with the character's name for backwards compatibility
            updateData.description = characterName;
          }
        } else {
          const contentToSave = finalContent || generatedContent;
          if (contentToSave) {
            updateData.description = contentToSave;
          }
        }

        console.log("Updating character with data:", updateData);
        await axios.put(`${API_URL}/api/characters/${editId}`, updateData);
        setSuccess("Character updated successfully!");

        // Navigate back to detail view after 1.5 seconds
        setTimeout(() => {
          navigate({ to: `/characters/${editId}` });
        }, 1500);
      } else {
        // Create new character

        // Check if this is a D&D character that was already saved during generation
        const isDndAlreadySaved =
          dndCharacter && dndCharacter.id && dndCharacter.is_dnd;

        if (isDndAlreadySaved) {
          // D&D character was already saved when generated, just show success
          setSuccess("D&D character already saved!");

          // Navigate to the character detail page after 1.5 seconds
          setTimeout(() => {
            navigate({ to: `/characters/${dndCharacter.id}` });
          }, 1500);
          return;
        }

        if (useStructured) {
          // Use structured save endpoint
          await axios.post(
            `${API_URL}/api/generate/character/structured/save`,
            {
              character_profile: finalContent || generatedContent,
              portrait_image: portraitImage || null,
              image_prompt: imagePrompt || null,
            }
          );
        } else {
          // Use legacy save endpoint
          await axios.post(`${API_URL}/api/generate/character/save`, null, {
            params: {
              name: characterName,
              content: finalContent || generatedContent,
              portrait_image: portraitImage || null,
              image_prompt: imagePrompt || null,
            },
          });
        }
        setSuccess("Character saved successfully!");

        // Reset form after 2 seconds
        setTimeout(() => {
          setActiveStep(0);
          setGeneratedContent(null);
          setCharacterName("");
          setPortraitImage(null);
          setImagePrompt(null);
          setSuccess(null);
        }, 2000);
      }
    } catch (err) {
      console.error("Save error:", err);

      // Handle validation errors (422) specially
      if (err.response?.status === 422 && err.response?.data?.detail) {
        const detail = err.response.data.detail;

        // If detail is an array of validation errors, format them nicely
        if (Array.isArray(detail)) {
          const errorMessages = detail
            .map((e) => {
              const field = e.loc ? e.loc.join(".") : "unknown";
              return `${field}: ${e.msg}`;
            })
            .join("; ");
          setError(`Validation error: ${errorMessages}`);
        } else if (typeof detail === "string") {
          setError(detail);
        } else {
          setError(JSON.stringify(detail));
        }
      } else {
        setError(
          err.response?.data?.detail ||
            err.response?.data?.message ||
            `Failed to ${isEditMode ? "update" : "save"} character`
        );
      }
    } finally {
      setSaving(false);
    }
  };

  const handleGeneratePortrait = async () => {
    if (!characterName.trim()) {
      setPortraitError("Please enter a character name first");
      return;
    }

    setGeneratingPortrait(true);
    setPortraitError(null);

    try {
      // Extract appearance from generated content
      // For structured content, extract physical description
      const appearanceText = useStructured
        ? generatedContent.physical_description ||
          `${generatedContent.height}, ${generatedContent.build} build, ${generatedContent.hair} hair, ${generatedContent.eyes} eyes`
        : generatedContent;

      const response = await axios.post(
        `${API_URL}/api/generate/character/generate-portrait`,
        {
          character_name: characterName,
          appearance_text: appearanceText,
          provider: imageProvider,
          model: imageModel || null,
          aspect_ratio: "3:4",
          custom_prompt: null,
          style_preset: imageStyle,
          quality: imageQuality,
        }
      );

      setPortraitImage(response.data.image_base64);
      setImagePrompt(response.data.prompt_used || null);
      setSuccess(
        `Portrait generated successfully with ${response.data.provider}!`
      );
    } catch (err) {
      setPortraitError(
        err.response?.data?.detail ||
          "Failed to generate portrait. Make sure API key is configured."
      );
      console.error(err);
    } finally {
      setGeneratingPortrait(false);
    }
  };

  const handleNext = () => {
    if (activeStep === 0) {
      setActiveStep(1);
    } else if (activeStep === 1) {
      handleGenerate();
    }
  };

  const handleBack = () => {
    setActiveStep((prevStep) => prevStep - 1);
  };

  if (!options) {
    return (
      <Container>
        <Box sx={{ display: "flex", justifyContent: "center", py: 10 }}>
          <CircularProgress />
        </Box>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg">
      <Box sx={{ mb: 4 }}>
        <Typography variant="h3" gutterBottom sx={{ fontWeight: 700 }}>
          {isEditMode ? "Edit Character" : "Create a Character"}
        </Typography>
        <Typography variant="body1" color="text.secondary">
          {isEditMode
            ? "Update your character's details and portrait"
            : "Use AI to generate detailed, compelling characters for your stories"}
        </Typography>
      </Box>

      <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
        {steps.map((label) => (
          <Step key={label}>
            <StepLabel>{label}</StepLabel>
          </Step>
        ))}
      </Stepper>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {success && (
        <Alert
          severity="success"
          sx={{ mb: 3 }}
          onClose={() => setSuccess(null)}
        >
          {success}
        </Alert>
      )}

      {/* Step 0: Select Traits */}
      {activeStep === 0 && (
        <Paper sx={{ p: 4 }}>
          {/* Generation Mode Toggle */}
          <Box
            sx={{
              mb: 4,
              p: 2,
              bgcolor: "background.default",
              borderRadius: 2,
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
            }}
          >
            <Box>
              <Typography variant="h6" gutterBottom>
                Generation Mode
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {useStructured
                  ? "Organized sections with complete details."
                  : "Narrative style with creative flexibility."}
              </Typography>
            </Box>
            <FormControlLabel
              control={
                <Switch
                  checked={useStructured}
                  onChange={(e) => setUseStructured(e.target.checked)}
                  color="primary"
                />
              }
              label={
                <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                  <Typography variant="body2" fontWeight="bold">
                    Structured
                  </Typography>
                  {useStructured && (
                    <Chip
                      label="Recommended"
                      size="small"
                      color="primary"
                      sx={{ fontSize: "0.7rem" }}
                    />
                  )}
                </Box>
              }
              labelPlacement="start"
            />
          </Box>

          {/* D&D Mode Toggle */}
          <Box
            sx={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              p: 2,
              bgcolor: "background.paper",
              borderRadius: 1,
              border: "1px solid",
              borderColor: isDnDMode ? "primary.main" : "divider",
            }}
          >
            <Box>
              <Typography
                variant="h6"
                gutterBottom
                sx={{ display: "flex", alignItems: "center", gap: 1 }}
              >
                🎲 D&D 5E Mode
                {isDnDMode && (
                  <Chip
                    label="Active"
                    size="small"
                    color="primary"
                    sx={{ fontSize: "0.7rem" }}
                  />
                )}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {isDnDMode
                  ? "Create a complete D&D 5th Edition character with stats, equipment, and AI-generated narrative."
                  : "Enable D&D mode to generate characters with full D&D 5E stats, abilities, and equipment."}
              </Typography>
            </Box>
            <FormControlLabel
              control={
                <Switch
                  checked={isDnDMode}
                  onChange={(e) => setIsDnDMode(e.target.checked)}
                  color="primary"
                />
              }
              label={
                <Typography variant="body2" fontWeight="bold">
                  D&D Mode
                </Typography>
              }
              labelPlacement="start"
            />
          </Box>

          {/* Show D&D Creator when D&D mode is active */}
          {isDnDMode ? (
            <DnDCharacterCreator
              key={dndRegenerationKey} // Force remount when key changes
              onCharacterGenerated={(character) => {
                setDndCharacter(character);
                setGeneratedContent(character);
                setCharacterName(character.name || "");
                setActiveStep(2); // Move to review step
                setSuccess("D&D character generated successfully!");
              }}
              onError={(errorMsg) => {
                setError(errorMsg);
              }}
            />
          ) : (
            // Original character creation form
            <div>
              <Grid container spacing={3}>
                <Grid size={{ xs: 12 }}>
                  <PromptSelector
                    label="Themes/Genre"
                    options={options.themes}
                    selectedValues={selectedThemes}
                    onChange={setSelectedThemes}
                    helperText="Select themes that fit your story's genre"
                  />
                </Grid>

                <Grid size={{ xs: 12 }}>
                  <FormControl fullWidth>
                    <InputLabel>Character Archetype</InputLabel>
                    <Select
                      value={selectedArchetype}
                      onChange={(e) => setSelectedArchetype(e.target.value)}
                      label="Character Archetype"
                    >
                      <MenuItem value="">
                        <em>None</em>
                      </MenuItem>
                      {options.character_archetypes.map((archetype) => (
                        <MenuItem key={archetype} value={archetype}>
                          {archetype}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Grid>

                {/* Phase 1 & 2: Genre Variations and Cultural Origins */}
                {variations && (
                  <Grid size={{ xs: 12 }}>
                    <Accordion>
                      <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                        <Box
                          sx={{ display: "flex", alignItems: "center", gap: 1 }}
                        >
                          <AutoAwesomeIcon color="primary" />
                          <Typography variant="subtitle1">
                            Genre Variation (Optional)
                          </Typography>
                          <Chip
                            label="Enhanced"
                            size="small"
                            color="primary"
                            sx={{ fontSize: "0.7rem" }}
                          />
                        </Box>
                      </AccordionSummary>
                      <AccordionDetails>
                        <Typography
                          variant="body2"
                          color="text.secondary"
                          paragraph
                        >
                          Select a genre and variation to add specific
                          world-building, character archetypes, and thematic
                          elements to your character.
                        </Typography>

                        <FormControl fullWidth sx={{ mb: 2 }}>
                          <InputLabel>Genre</InputLabel>
                          <Select
                            value={selectedGenre}
                            onChange={(e) => {
                              setSelectedGenre(e.target.value);
                              setSelectedVariation(""); // Reset variation when genre changes
                            }}
                            label="Genre"
                          >
                            <MenuItem value="">
                              <em>None</em>
                            </MenuItem>
                            <MenuItem value="fantasy">🧙‍♂️ Fantasy</MenuItem>
                            <MenuItem value="sci_fi">🚀 Sci-Fi</MenuItem>
                            <MenuItem value="historical">
                              📜 Historical
                            </MenuItem>
                            <MenuItem value="horror">👻 Horror</MenuItem>
                            <MenuItem value="mystery_thriller">
                              🔍 Mystery/Thriller
                            </MenuItem>
                            <MenuItem value="romance">💕 Romance</MenuItem>
                            <MenuItem value="adventure">🗺️ Adventure</MenuItem>
                            <MenuItem value="western">🤠 Western</MenuItem>
                            <MenuItem value="dystopian">🏚️ Dystopian</MenuItem>
                            <MenuItem value="superhero">🦸 Superhero</MenuItem>
                          </Select>
                        </FormControl>

                        {selectedGenre && variations[selectedGenre] && (
                          <FormControl fullWidth>
                            <InputLabel>Variation</InputLabel>
                            <Select
                              value={selectedVariation}
                              onChange={(e) =>
                                setSelectedVariation(e.target.value)
                              }
                              label="Variation"
                            >
                              <MenuItem value="">
                                <em>None</em>
                              </MenuItem>
                              {variations[selectedGenre].map((variation) => (
                                <MenuItem
                                  key={variation.key}
                                  value={variation.key}
                                >
                                  <Box>
                                    <Typography variant="body2">
                                      {variation.name}
                                    </Typography>
                                    <Typography
                                      variant="caption"
                                      color="text.secondary"
                                    >
                                      {variation.description}
                                    </Typography>
                                  </Box>
                                </MenuItem>
                              ))}
                            </Select>
                          </FormControl>
                        )}

                        {selectedGenre && selectedVariation && (
                          <Button
                            size="small"
                            startIcon={<ShuffleIcon />}
                            onClick={() => {
                              const variationsList = variations[selectedGenre];
                              const randomVariation =
                                variationsList[
                                  Math.floor(
                                    Math.random() * variationsList.length
                                  )
                                ];
                              setSelectedVariation(randomVariation.key);
                            }}
                            sx={{ mt: 1 }}
                          >
                            Random Variation
                          </Button>
                        )}
                      </AccordionDetails>
                    </Accordion>
                  </Grid>
                )}

                {culturalOrigins && (
                  <Grid size={{ xs: 12 }}>
                    <Accordion>
                      <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                        <Box
                          sx={{ display: "flex", alignItems: "center", gap: 1 }}
                        >
                          <PublicIcon color="secondary" />
                          <Typography variant="subtitle1">
                            Cultural Origin (Optional)
                          </Typography>
                          <Chip
                            label="Authentic"
                            size="small"
                            color="secondary"
                            sx={{ fontSize: "0.7rem" }}
                          />
                        </Box>
                      </AccordionSummary>
                      <AccordionDetails>
                        <Typography
                          variant="body2"
                          color="text.secondary"
                          paragraph
                        >
                          Choose a cultural background to add authentic
                          traditions, values, and cultural context to your
                          character.
                        </Typography>

                        <FormControl fullWidth>
                          <InputLabel>Cultural Origin</InputLabel>
                          <Select
                            value={selectedCulturalOrigin}
                            onChange={(e) =>
                              setSelectedCulturalOrigin(e.target.value)
                            }
                            label="Cultural Origin"
                            renderValue={(selected) => {
                              const origin = culturalOrigins.find(
                                (o) => o.key === selected
                              );
                              return origin ? origin.name : "";
                            }}
                          >
                            <MenuItem value="">
                              <em>None</em>
                            </MenuItem>

                            {/* Group origins by region */}
                            <MenuItem disabled>
                              <Typography
                                variant="caption"
                                fontWeight="bold"
                                color="primary"
                              >
                                AFRICAN CULTURES
                              </Typography>
                            </MenuItem>
                            {culturalOrigins
                              .filter((o) =>
                                [
                                  "north_african",
                                  "west_african",
                                  "east_african",
                                  "southern_african",
                                  "central_african",
                                ].includes(o.key)
                              )
                              .map((origin) => (
                                <MenuItem key={origin.key} value={origin.key}>
                                  <Box sx={{ pl: 2 }}>
                                    <Typography variant="body2">
                                      {origin.name}
                                    </Typography>
                                    <Typography
                                      variant="caption"
                                      color="text.secondary"
                                    >
                                      {origin.regions.slice(0, 3).join(", ")}
                                    </Typography>
                                  </Box>
                                </MenuItem>
                              ))}

                            <MenuItem disabled>
                              <Typography
                                variant="caption"
                                fontWeight="bold"
                                color="primary"
                              >
                                ASIAN CULTURES
                              </Typography>
                            </MenuItem>
                            {culturalOrigins
                              .filter(
                                (o) =>
                                  o.key.startsWith("east_asian") ||
                                  o.key.startsWith("southeast_asian") ||
                                  o.key.startsWith("south_asian") ||
                                  [
                                    "central_asian",
                                    "himalayan",
                                    "mongolian",
                                  ].includes(o.key)
                              )
                              .map((origin) => (
                                <MenuItem key={origin.key} value={origin.key}>
                                  <Box sx={{ pl: 2 }}>
                                    <Typography variant="body2">
                                      {origin.name}
                                    </Typography>
                                    <Typography
                                      variant="caption"
                                      color="text.secondary"
                                    >
                                      {origin.regions.slice(0, 3).join(", ")}
                                    </Typography>
                                  </Box>
                                </MenuItem>
                              ))}

                            <MenuItem disabled>
                              <Typography
                                variant="caption"
                                fontWeight="bold"
                                color="primary"
                              >
                                MIDDLE EASTERN CULTURES
                              </Typography>
                            </MenuItem>
                            {culturalOrigins
                              .filter((o) => o.key.startsWith("middle_eastern"))
                              .map((origin) => (
                                <MenuItem key={origin.key} value={origin.key}>
                                  <Box sx={{ pl: 2 }}>
                                    <Typography variant="body2">
                                      {origin.name}
                                    </Typography>
                                    <Typography
                                      variant="caption"
                                      color="text.secondary"
                                    >
                                      {origin.regions.slice(0, 3).join(", ")}
                                    </Typography>
                                  </Box>
                                </MenuItem>
                              ))}

                            <MenuItem disabled>
                              <Typography
                                variant="caption"
                                fontWeight="bold"
                                color="primary"
                              >
                                EUROPEAN CULTURES
                              </Typography>
                            </MenuItem>
                            {culturalOrigins
                              .filter(
                                (o) =>
                                  o.key.startsWith("western_european") ||
                                  o.key.startsWith("southern_european") ||
                                  o.key.startsWith("eastern_european") ||
                                  o.key === "nordic"
                              )
                              .map((origin) => (
                                <MenuItem key={origin.key} value={origin.key}>
                                  <Box sx={{ pl: 2 }}>
                                    <Typography variant="body2">
                                      {origin.name}
                                    </Typography>
                                    <Typography
                                      variant="caption"
                                      color="text.secondary"
                                    >
                                      {origin.regions.slice(0, 3).join(", ")}
                                    </Typography>
                                  </Box>
                                </MenuItem>
                              ))}

                            <MenuItem disabled>
                              <Typography
                                variant="caption"
                                fontWeight="bold"
                                color="primary"
                              >
                                AMERICAS CULTURES
                              </Typography>
                            </MenuItem>
                            {culturalOrigins
                              .filter(
                                (o) =>
                                  o.key.startsWith("north_american") ||
                                  o.key.startsWith("latin_american") ||
                                  o.key.startsWith("indigenous")
                              )
                              .map((origin) => (
                                <MenuItem key={origin.key} value={origin.key}>
                                  <Box sx={{ pl: 2 }}>
                                    <Typography variant="body2">
                                      {origin.name}
                                    </Typography>
                                    <Typography
                                      variant="caption"
                                      color="text.secondary"
                                    >
                                      {origin.regions.slice(0, 3).join(", ")}
                                    </Typography>
                                  </Box>
                                </MenuItem>
                              ))}

                            <MenuItem disabled>
                              <Typography
                                variant="caption"
                                fontWeight="bold"
                                color="primary"
                              >
                                PACIFIC CULTURES
                              </Typography>
                            </MenuItem>
                            {culturalOrigins
                              .filter((o) =>
                                [
                                  "polynesian",
                                  "australian_aboriginal",
                                  "melanesian_micronesian",
                                ].includes(o.key)
                              )
                              .map((origin) => (
                                <MenuItem key={origin.key} value={origin.key}>
                                  <Box sx={{ pl: 2 }}>
                                    <Typography variant="body2">
                                      {origin.name}
                                    </Typography>
                                    <Typography
                                      variant="caption"
                                      color="text.secondary"
                                    >
                                      {origin.regions.slice(0, 3).join(", ")}
                                    </Typography>
                                  </Box>
                                </MenuItem>
                              ))}
                          </Select>
                        </FormControl>

                        {selectedCulturalOrigin && (
                          <Box sx={{ mt: 2 }}>
                            <Button
                              size="small"
                              startIcon={<ShuffleIcon />}
                              onClick={() => {
                                const randomOrigin =
                                  culturalOrigins[
                                    Math.floor(
                                      Math.random() * culturalOrigins.length
                                    )
                                  ];
                                setSelectedCulturalOrigin(randomOrigin.key);
                              }}
                            >
                              Random Culture
                            </Button>
                            <Tooltip title="All content is in English while maintaining cultural authenticity">
                              <IconButton size="small" sx={{ ml: 1 }}>
                                <InfoOutlinedIcon fontSize="small" />
                              </IconButton>
                            </Tooltip>
                          </Box>
                        )}
                      </AccordionDetails>
                    </Accordion>
                  </Grid>
                )}

                <Grid size={{ xs: 12 }}>
                  <PromptSelector
                    label="Personality Traits"
                    options={options.personality_traits}
                    selectedValues={selectedPersonalityTraits}
                    onChange={setSelectedPersonalityTraits}
                    helperText="Choose personality characteristics"
                  />
                </Grid>

                <Grid size={{ xs: 12 }}>
                  <PromptSelector
                    label="Physical Traits"
                    options={options.physical_traits}
                    selectedValues={selectedPhysicalTraits}
                    onChange={setSelectedPhysicalTraits}
                    helperText="Select physical characteristics"
                  />
                </Grid>

                <Grid size={{ xs: 12 }}>
                  <PromptSelector
                    label="Emotional Traits"
                    options={options.emotional_traits}
                    selectedValues={selectedEmotionalTraits}
                    onChange={setSelectedEmotionalTraits}
                    helperText="Choose emotional characteristics"
                  />
                </Grid>

                <Grid size={{ xs: 12 }}>
                  <Divider sx={{ my: 2 }}>
                    <Typography variant="caption" color="text.secondary">
                      CUSTOM DETAILS
                    </Typography>
                  </Divider>
                  <TextField
                    fullWidth
                    multiline
                    rows={4}
                    label="Additional Custom Details"
                    value={customDetails}
                    onChange={(e) => setCustomDetails(e.target.value)}
                    placeholder="Add any specific requirements, backstory elements, or unique characteristics you want the AI to include..."
                    helperText="Optional: Provide specific instructions for the AI"
                  />
                </Grid>

                <Grid size={{ xs: 12 }}>
                  <ModelSelector
                    provider={provider}
                    model={model}
                    onProviderChange={setProvider}
                    onModelChange={setModel}
                    contentType="character"
                  />
                </Grid>
              </Grid>
            </div>
          )}
        </Paper>
      )}

      {/* Step 1: Generate Preview */}
      {activeStep === 1 && (
        <Paper sx={{ p: 4 }}>
          <Typography variant="h5" gutterBottom>
            Ready to Generate
          </Typography>
          <Typography variant="body2" color="text.secondary" paragraph>
            Review your selections and click Generate to create your character
          </Typography>

          <Box sx={{ my: 3 }}>
            {selectedThemes.length > 0 && (
              <Box sx={{ mb: 2 }}>
                <Typography variant="subtitle2">Themes:</Typography>
                <Typography variant="body2">
                  {selectedThemes.join(", ")}
                </Typography>
              </Box>
            )}
            {selectedArchetype && (
              <Box sx={{ mb: 2 }}>
                <Typography variant="subtitle2">Archetype:</Typography>
                <Typography variant="body2">{selectedArchetype}</Typography>
              </Box>
            )}
            {selectedGenre && selectedVariation && (
              <Box sx={{ mb: 2 }}>
                <Typography variant="subtitle2">Genre Variation:</Typography>
                <Typography variant="body2">
                  {selectedGenre === "sci_fi"
                    ? "Sci-Fi"
                    : selectedGenre === "mystery_thriller"
                      ? "Mystery/Thriller"
                      : selectedGenre.charAt(0).toUpperCase() +
                        selectedGenre.slice(1)}{" "}
                  -{" "}
                  {variations[selectedGenre]?.find(
                    (v) => v.key === selectedVariation
                  )?.name || selectedVariation}
                </Typography>
              </Box>
            )}
            {selectedCulturalOrigin && (
              <Box sx={{ mb: 2 }}>
                <Typography variant="subtitle2">Cultural Origin:</Typography>
                <Typography variant="body2">
                  {culturalOrigins?.find(
                    (o) => o.key === selectedCulturalOrigin
                  )?.name || selectedCulturalOrigin}
                </Typography>
              </Box>
            )}
            {selectedPersonalityTraits.length > 0 && (
              <Box sx={{ mb: 2 }}>
                <Typography variant="subtitle2">Personality:</Typography>
                <Typography variant="body2">
                  {selectedPersonalityTraits.join(", ")}
                </Typography>
              </Box>
            )}
            {selectedPhysicalTraits.length > 0 && (
              <Box sx={{ mb: 2 }}>
                <Typography variant="subtitle2">Physical:</Typography>
                <Typography variant="body2">
                  {selectedPhysicalTraits.join(", ")}
                </Typography>
              </Box>
            )}
            {customDetails && (
              <Box sx={{ mb: 2 }}>
                <Typography variant="subtitle2">Custom Details:</Typography>
                <Typography variant="body2">{customDetails}</Typography>
              </Box>
            )}
          </Box>
        </Paper>
      )}

      {/* Step 2: Review & Save */}
      {activeStep === 2 && (
        <Box>
          {/* Character Name Input */}
          <TextField
            fullWidth
            label="Character Name"
            value={characterName}
            onChange={(e) => setCharacterName(e.target.value)}
            placeholder="Enter a name for this character"
            sx={{ mb: 3 }}
            required
          />

          {/* Grid Layout: Portrait on Left, Details on Right */}
          <Grid container spacing={3}>
            {/* Left Column - Portrait (sticky/fixed) */}
            <Grid item xs={12} md={4}>
              <Box
                sx={{
                  position: { md: "sticky" },
                  top: { md: 24 },
                }}
              >
                {/* Portrait Generation Section */}
                <Paper
                  sx={{
                    p: 3,
                    backgroundColor: "background.default",
                  }}
                >
                  {/* Header with Settings Toggle */}
                  <Box
                    sx={{
                      mb: 2,
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "center",
                    }}
                  >
                    <Box>
                      <Typography variant="h6" gutterBottom>
                        Character Portrait
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Generate an AI portrait
                      </Typography>
                    </Box>
                    <Tooltip title="Portrait Settings">
                      <IconButton
                        onClick={() =>
                          setShowPortraitSettings(!showPortraitSettings)
                        }
                        color={showPortraitSettings ? "primary" : "default"}
                      >
                        <SettingsIcon />
                      </IconButton>
                    </Tooltip>
                  </Box>

                  {/* Portrait Image Display */}
                  {portraitImage && (
                    <Box sx={{ mb: 2, textAlign: "center" }}>
                      <img
                        src={`data:image/png;base64,${portraitImage}`}
                        alt={`${characterName} portrait`}
                        style={{
                          width: "100%",
                          borderRadius: "8px",
                          boxShadow: "0 4px 6px rgba(0,0,0,0.3)",
                        }}
                      />
                    </Box>
                  )}

                  {/* Collapsible Settings */}
                  {showPortraitSettings && (
                    <Box
                      sx={{
                        mb: 2,
                        display: "flex",
                        flexDirection: "column",
                        gap: 2,
                        p: 2,
                        backgroundColor: "action.hover",
                        borderRadius: 1,
                      }}
                    >
                      <FormControl fullWidth size="small">
                        <InputLabel>Provider</InputLabel>
                        <Select
                          value={imageProvider}
                          onChange={(e) => {
                            const newProvider = e.target.value;
                            setImageProvider(newProvider);
                            if (newProvider === "google") {
                              setImageModel("imagen-4.0-fast-generate-001");
                            } else if (newProvider === "openai") {
                              setImageModel("dall-e-3");
                            }
                          }}
                          label="Provider"
                        >
                          <MenuItem value="google">Google Imagen</MenuItem>
                          <MenuItem value="openai">OpenAI</MenuItem>
                        </Select>
                      </FormControl>

                      <FormControl fullWidth size="small">
                        <InputLabel>Model</InputLabel>
                        <Select
                          value={imageModel}
                          onChange={(e) => setImageModel(e.target.value)}
                          label="Model"
                        >
                          {/* Google Models */}
                          <MenuItem
                            value="imagen-4.0-fast-generate-001"
                            sx={{
                              display:
                                imageProvider === "google" ? "block" : "none",
                            }}
                          >
                            Imagen Fast
                          </MenuItem>
                          <MenuItem
                            value="imagen-4.0-generate-001"
                            sx={{
                              display:
                                imageProvider === "google" ? "block" : "none",
                            }}
                          >
                            Imagen Standard
                          </MenuItem>
                          <MenuItem
                            value="imagen-4.0-ultra-generate-001"
                            sx={{
                              display:
                                imageProvider === "google" ? "block" : "none",
                            }}
                          >
                            Imagen Ultra
                          </MenuItem>
                          {/* OpenAI Models */}
                          <MenuItem
                            value="dall-e-3"
                            sx={{
                              display:
                                imageProvider === "openai" ? "block" : "none",
                            }}
                          >
                            DALL-E 3
                          </MenuItem>
                          <MenuItem
                            value="dall-e-2"
                            sx={{
                              display:
                                imageProvider === "openai" ? "block" : "none",
                            }}
                          >
                            DALL-E 2
                          </MenuItem>
                        </Select>
                      </FormControl>

                      <FormControl fullWidth size="small">
                        <InputLabel>Art Style</InputLabel>
                        <Select
                          value={imageStyle}
                          onChange={(e) => setImageStyle(e.target.value)}
                          label="Art Style"
                        >
                          <MenuItem value="realistic">Realistic</MenuItem>
                          <MenuItem value="fantasy_art">Fantasy Art</MenuItem>
                          <MenuItem value="anime">Anime</MenuItem>
                          <MenuItem value="watercolor">Watercolor</MenuItem>
                          <MenuItem value="digital_art">Digital Art</MenuItem>
                        </Select>
                      </FormControl>

                      {imageProvider === "openai" &&
                        imageModel === "dall-e-3" && (
                          <FormControl fullWidth size="small">
                            <InputLabel>Quality</InputLabel>
                            <Select
                              value={imageQuality}
                              onChange={(e) => setImageQuality(e.target.value)}
                              label="Quality"
                            >
                              <MenuItem value="standard">Standard</MenuItem>
                              <MenuItem value="hd">HD</MenuItem>
                            </Select>
                          </FormControl>
                        )}
                    </Box>
                  )}

                  {/* Generate Button */}
                  <Button
                    fullWidth
                    variant="outlined"
                    startIcon={
                      generatingPortrait ? (
                        <CircularProgress size={20} />
                      ) : (
                        <PhotoCameraIcon />
                      )
                    }
                    onClick={handleGeneratePortrait}
                    disabled={
                      generatingPortrait ||
                      !characterName.trim() ||
                      !generatedContent
                    }
                  >
                    {generatingPortrait ? "Generating..." : "Generate"}
                  </Button>

                  {portraitError && (
                    <Alert
                      severity="error"
                      sx={{ mt: 2 }}
                      onClose={() => setPortraitError(null)}
                    >
                      {portraitError}
                    </Alert>
                  )}
                </Paper>
              </Box>
            </Grid>

            {/* Right Column - Character Details (scrollable) */}
            <Grid item xs={12} md={8}>
              {/* Display Component - Conditional based on generation mode */}
              {console.log(
                "Display logic - dndCharacter:",
                dndCharacter,
                "is_dnd:",
                dndCharacter?.is_dnd,
                "typeof is_dnd:",
                typeof dndCharacter?.is_dnd,
                "useStructured:",
                useStructured
              )}
              {dndCharacter && dndCharacter.is_dnd === true ? (
                // D&D Character Sheet - Modern scrollable layout
                <Grid container spacing={3}>
                  {/* Left Column: Portrait (sticky) */}
                  <Grid size={{ xs: 12, md: 4 }}>
                    <Box
                      sx={{
                        position: { md: "sticky" },
                        top: 24,
                        display: "flex",
                        flexDirection: "column",
                        gap: 2,
                      }}
                    >
                      {/* Character Portrait */}
                      {dndCharacter.portrait_image && (
                        <Card
                          sx={{
                            background:
                              "linear-gradient(135deg, #2c1810 0%, #3d2817 100%)",
                            border: "2px solid #8b6f47",
                          }}
                        >
                          <CardContent sx={{ p: 2 }}>
                            <img
                              src={dndCharacter.portrait_image}
                              alt={dndCharacter.name}
                              style={{
                                width: "100%",
                                height: "auto",
                                borderRadius: "8px",
                                border: "2px solid #8b6f47",
                              }}
                            />
                          </CardContent>
                        </Card>
                      )}

                      {/* Character Name & Basic Info Card */}
                      <Card
                        sx={{
                          background:
                            "linear-gradient(135deg, #2c1810 0%, #3d2817 100%)",
                          border: "2px solid #8b6f47",
                          color: "#f4e4c1",
                        }}
                      >
                        <CardContent>
                          <Typography
                            variant="h4"
                            sx={{
                              fontFamily: '"Cinzel", "Times New Roman", serif',
                              fontWeight: 700,
                              mb: 1,
                            }}
                          >
                            {dndCharacter.name}
                          </Typography>
                          <Typography
                            variant="subtitle1"
                            sx={{
                              fontFamily: '"Crimson Text", serif',
                              opacity: 0.9,
                              mb: 2,
                            }}
                          >
                            Level {dndCharacter.dnd_level}{" "}
                            {dndCharacter.dnd_species} {dndCharacter.dnd_class}
                          </Typography>
                          <Divider sx={{ bgcolor: "#8b6f47", my: 2 }} />
                          <Box
                            sx={{
                              display: "grid",
                              gridTemplateColumns: "1fr 1fr",
                              gap: 1,
                            }}
                          >
                            <Box>
                              <Typography
                                variant="caption"
                                sx={{ opacity: 0.7 }}
                              >
                                Alignment
                              </Typography>
                              <Typography variant="body2">
                                {dndCharacter.dnd_alignment}
                              </Typography>
                            </Box>
                            <Box>
                              <Typography
                                variant="caption"
                                sx={{ opacity: 0.7 }}
                              >
                                Background
                              </Typography>
                              <Typography variant="body2">
                                {dndCharacter.dnd_background}
                              </Typography>
                            </Box>
                          </Box>
                        </CardContent>
                      </Card>

                      {/* Action Buttons */}
                      <Box
                        sx={{
                          display: "flex",
                          flexDirection: "column",
                          gap: 1,
                        }}
                      >
                        <Button
                          variant="contained"
                          onClick={() => handleSave(dndCharacter)}
                          disabled={
                            saving || generating || !characterName.trim()
                          }
                          startIcon={
                            saving ? <CircularProgress size={20} /> : null
                          }
                          sx={{
                            bgcolor: "#8b6f47",
                            "&:hover": { bgcolor: "#6d5839" },
                          }}
                        >
                          {saving
                            ? "Saving..."
                            : isEditMode
                              ? "Update"
                              : "Save Character"}
                        </Button>
                        <Button
                          variant="outlined"
                          onClick={() => {
                            // Regenerate D&D character - reset to D&D generation form (step 0)
                            setDndCharacter(null);
                            setGeneratedContent(null);
                            setActiveStep(0); // Go back to step 0 where DnDCharacterCreator is shown
                            setDndRegenerationKey((prev) => prev + 1); // Force DnDCharacterCreator to remount
                            setSuccess(null);
                            setError(null);
                          }}
                          disabled={saving || generating}
                          sx={{
                            borderColor: "#8b6f47",
                            color: "#8b6f47",
                            "&:hover": {
                              borderColor: "#6d5839",
                              bgcolor: "rgba(139, 111, 71, 0.1)",
                            },
                          }}
                        >
                          Regenerate
                        </Button>
                      </Box>
                    </Box>
                  </Grid>

                  {/* Right Column: Scrollable Stats */}
                  <Grid size={{ xs: 12, md: 8 }}>
                    <Box
                      sx={{
                        maxHeight: { md: "calc(100vh - 200px)" },
                        overflowY: "auto",
                        pr: 2,
                        "&::-webkit-scrollbar": {
                          width: "8px",
                        },
                        "&::-webkit-scrollbar-track": {
                          background: "#f1f1f1",
                          borderRadius: "4px",
                        },
                        "&::-webkit-scrollbar-thumb": {
                          background: "#8b6f47",
                          borderRadius: "4px",
                        },
                        "&::-webkit-scrollbar-thumb:hover": {
                          background: "#6d5839",
                        },
                      }}
                    >
                      <DnDCharacterSheet character={dndCharacter} />
                    </Box>
                  </Grid>
                </Grid>
              ) : useStructured ? (
                <Box>
                  <StructuredCharacterDisplay
                    characterProfile={generatedContent}
                  />
                  <Box
                    sx={{
                      display: "flex",
                      justifyContent: "flex-end",
                      gap: 2,
                      mt: 3,
                    }}
                  >
                    <Button
                      variant="outlined"
                      onClick={() =>
                        handleRefine(
                          "Please regenerate with different details while keeping the same structure"
                        )
                      }
                      disabled={saving || generating}
                    >
                      Regenerate
                    </Button>
                    <Button
                      variant="contained"
                      onClick={() => handleSave(generatedContent)}
                      disabled={saving || generating || !characterName.trim()}
                      startIcon={saving ? <CircularProgress size={20} /> : null}
                    >
                      {saving
                        ? "Saving..."
                        : isEditMode
                          ? "Update"
                          : "Save Character"}
                    </Button>
                  </Box>
                </Box>
              ) : (
                <GenerationResult
                  content={generatedContent}
                  onSave={handleSave}
                  onRefine={handleRefine}
                  saving={saving || generating}
                  entity="Character"
                  isEditMode={isEditMode}
                />
              )}
            </Grid>
          </Grid>
        </Box>
      )}

      {/* Navigation Buttons */}
      <Box sx={{ display: "flex", justifyContent: "space-between", mt: 4 }}>
        <Button
          onClick={handleBack}
          disabled={activeStep === 0}
          startIcon={<NavigateBeforeIcon />}
        >
          Back
        </Button>
        {/* Hide Next button for D&D characters on review step (they have inline Save button) */}
        {!(isDnDMode && activeStep === 2) && (
          <Button
            variant="contained"
            onClick={handleNext}
            disabled={generating || activeStep === 2}
            endIcon={
              activeStep === 1 ? <AutoAwesomeIcon /> : <NavigateNextIcon />
            }
          >
            {generating ? (
              <CircularProgress size={24} />
            ) : activeStep === steps.length - 2 ? (
              "Generate with AI"
            ) : (
              "Next"
            )}
          </Button>
        )}
      </Box>
    </Container>
  );
}
