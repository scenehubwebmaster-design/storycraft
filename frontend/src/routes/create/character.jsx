import { createFileRoute } from "@tanstack/react-router";
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
} from "@mui/material";
import AutoAwesomeIcon from "@mui/icons-material/AutoAwesome";
import NavigateNextIcon from "@mui/icons-material/NavigateNext";
import NavigateBeforeIcon from "@mui/icons-material/NavigateBefore";
import PhotoCameraIcon from "@mui/icons-material/PhotoCamera";
import PromptSelector from "../../components/PromptSelector";
import GenerationResult from "../../components/GenerationResult";
import ModelSelector from "../../components/ModelSelector";

export const Route = createFileRoute("/create/character")({
  component: CreateCharacterComponent,
});

const API_URL = "http://localhost:8000";

const steps = ["Select Traits", "Generate", "Review & Save"];

function CreateCharacterComponent() {
  console.log("CreateCharacterComponent mounted!");

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

  // Generation results
  const [generatedContent, setGeneratedContent] = useState(null);
  const [generating, setGenerating] = useState(false);
  const [saving, setSaving] = useState(false);

  // Character name for saving
  const [characterName, setCharacterName] = useState("");

  // Portrait generation state
  const [portraitImage, setPortraitImage] = useState(null);
  const [generatingPortrait, setGeneratingPortrait] = useState(false);
  const [portraitError, setPortraitError] = useState(null);

  // Load prompt options on mount
  useEffect(() => {
    console.log("useEffect running - loading options");
    loadOptions();
  }, []);

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

  const handleGenerate = async () => {
    setGenerating(true);
    setError(null);

    try {
      const response = await axios.post(`${API_URL}/api/generate/character`, {
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
      });

      setGeneratedContent(response.data.content);
      setActiveStep(2);
      setSuccess("Character generated successfully!");
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
      const response = await axios.post(`${API_URL}/api/generate/character`, {
        base_content: generatedContent,
        refinement_instructions: refinementInstructions,
        provider,
        model: model || null,
      });

      setGeneratedContent(response.data.content);
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
      await axios.post(`${API_URL}/api/generate/character/save`, null, {
        params: {
          name: characterName,
          content: finalContent || generatedContent,
        },
      });

      setSuccess("Character saved successfully!");
      // Reset form after 2 seconds
      setTimeout(() => {
        setActiveStep(0);
        setGeneratedContent(null);
        setCharacterName("");
        setPortraitImage(null);
        setSuccess(null);
      }, 2000);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to save character");
      console.error(err);
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
      const response = await axios.post(
        `${API_URL}/api/generate/character/generate-portrait`,
        {
          character_name: characterName,
          appearance_text: generatedContent,
          model: "imagen-4.0-fast-generate-001",
          aspect_ratio: "3:4",
          custom_prompt: null,
        }
      );

      setPortraitImage(response.data.image_base64);
      setSuccess("Portrait generated successfully!");
    } catch (err) {
      setPortraitError(
        err.response?.data?.detail ||
          "Failed to generate portrait. Make sure Google API key is configured."
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
          Create a Character
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Use AI to generate detailed, compelling characters for your stories
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
          <TextField
            fullWidth
            label="Character Name"
            value={characterName}
            onChange={(e) => setCharacterName(e.target.value)}
            placeholder="Enter a name for this character"
            sx={{ mb: 3 }}
            required
          />

          {/* Portrait Generation Section */}
          <Paper sx={{ p: 3, mb: 3, backgroundColor: "background.default" }}>
            <Box
              sx={{
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                mb: 2,
              }}
            >
              <Box>
                <Typography variant="h6" gutterBottom>
                  Character Portrait
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Generate an AI portrait based on the character's appearance
                </Typography>
              </Box>
              <Button
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
                title={
                  !characterName.trim()
                    ? "Enter a character name first"
                    : !generatedContent
                      ? "Generate character content first"
                      : "Generate AI portrait"
                }
              >
                {generatingPortrait ? "Generating..." : "Generate Portrait"}
              </Button>
            </Box>

            {(!characterName.trim() || !generatedContent) && !generatingPortrait && (
              <Alert severity="info" sx={{ mb: 2 }}>
                {!characterName.trim() 
                  ? "Enter a character name above to enable portrait generation"
                  : "Character content is required for portrait generation"}
              </Alert>
            )}

            {portraitError && (
              <Alert
                severity="error"
                sx={{ mb: 2 }}
                onClose={() => setPortraitError(null)}
              >
                {portraitError}
              </Alert>
            )}

            {portraitImage && (
              <Box sx={{ mt: 2, textAlign: "center" }}>
                <img
                  src={`data:image/png;base64,${portraitImage}`}
                  alt={`${characterName} portrait`}
                  style={{
                    maxWidth: "100%",
                    maxHeight: "500px",
                    borderRadius: "8px",
                    boxShadow: "0 4px 6px rgba(0,0,0,0.3)",
                  }}
                />
                <Typography
                  variant="caption"
                  display="block"
                  sx={{ mt: 1 }}
                  color="text.secondary"
                >
                  Generated with Google Imagen
                </Typography>
              </Box>
            )}
          </Paper>

          <GenerationResult
            content={generatedContent}
            onSave={handleSave}
            onRefine={handleRefine}
            saving={saving || generating}
            entity="Character"
          />
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
      </Box>
    </Container>
  );
}
