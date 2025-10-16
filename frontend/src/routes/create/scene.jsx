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
} from "@mui/material";
import AutoAwesomeIcon from "@mui/icons-material/AutoAwesome";
import NavigateNextIcon from "@mui/icons-material/NavigateNext";
import NavigateBeforeIcon from "@mui/icons-material/NavigateBefore";
import PromptSelector from "../../components/PromptSelector";
import GenerationResult from "../../components/GenerationResult";
import ModelSelector from "../../components/ModelSelector";
import { API_URL } from "../../config/api";

export const Route = createFileRoute("/create/scene")({
  component: CreateSceneComponent,
});

const steps = ["Scene Setup", "Generate", "Review & Save"];

function CreateSceneComponent() {
  const [options, setOptions] = useState(null);
  const [activeStep, setActiveStep] = useState(0);

  // Scene parameters
  const [storyContext, setStoryContext] = useState("");
  const [characters, setCharacters] = useState("");
  const [setting, setSetting] = useState("");
  const [purpose, setPurpose] = useState("");
  const [selectedTones, setSelectedTones] = useState([]);
  const [customDetails, setCustomDetails] = useState("");
  const [provider, setProvider] = useState("groq");
  const [model, setModel] = useState("");

  // Results
  const [generatedContent, setGeneratedContent] = useState(null);
  const [generating, setGenerating] = useState(false);
  const [saving, setSaving] = useState(false);
  const [sceneTitle, setSceneTitle] = useState("");
  const [chapterId, setChapterId] = useState("");
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  useEffect(() => {
    loadOptions();
  }, []);

  const loadOptions = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/generate/options`);
      setOptions(response.data);
    } catch (err) {
      setError("Failed to load options");
    }
  };

  const handleGenerate = async () => {
    setGenerating(true);
    setError(null);

    try {
      const charactersArray = characters
        .split(",")
        .map((c) => c.trim())
        .filter((c) => c);

      const response = await axios.post(`${API_URL}/api/generate/scene`, {
        story_context: storyContext || null,
        characters: charactersArray.length > 0 ? charactersArray : null,
        setting: setting || null,
        purpose: purpose || null,
        tone: selectedTones.length > 0 ? selectedTones : null,
        custom_details: customDetails || null,
        provider,
        model: model || null,
      });

      setGeneratedContent(response.data.content);
      setActiveStep(2);
      setSuccess("Scene generated successfully!");
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to generate scene");
    } finally {
      setGenerating(false);
    }
  };

  const handleRefine = async (refinementInstructions) => {
    setGenerating(true);
    setError(null);

    try {
      const response = await axios.post(`${API_URL}/api/generate/scene`, {
        base_content: generatedContent,
        refinement_instructions: refinementInstructions,
        provider,
        model: model || null,
      });

      setGeneratedContent(response.data.content);
      setSuccess("Scene refined successfully!");
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to refine scene");
    } finally {
      setGenerating(false);
    }
  };

  const handleSave = async (finalContent) => {
    if (!sceneTitle.trim()) {
      setError("Please enter a scene title");
      return;
    }
    if (!chapterId) {
      setError("Please enter a chapter ID");
      return;
    }

    setSaving(true);
    setError(null);

    try {
      await axios.post(`${API_URL}/api/generate/scene/save`, null, {
        params: {
          title: sceneTitle,
          content: finalContent || generatedContent,
          chapter_id: parseInt(chapterId),
          order: 0,
        },
      });

      setSuccess("Scene saved successfully!");
      setTimeout(() => {
        setActiveStep(0);
        setGeneratedContent(null);
        setSceneTitle("");
        setSuccess(null);
      }, 2000);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to save scene");
    } finally {
      setSaving(false);
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
    setActiveStep((prev) => prev - 1);
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
          Create a Scene
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Write vivid, engaging scenes with rich details and character
          interactions
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

      {activeStep === 0 && (
        <Paper sx={{ p: 4 }}>
          <Grid container spacing={3}>
            <Grid size={{ xs: 12 }}>
              <TextField
                fullWidth
                multiline
                rows={3}
                label="Story Context"
                value={storyContext}
                onChange={(e) => setStoryContext(e.target.value)}
                placeholder="Brief context about what's happening in your story at this point..."
                helperText="Optional: Provide context to help the AI understand where this scene fits"
              />
            </Grid>

            <Grid size={{ xs: 12, md: 6 }}>
              <TextField
                fullWidth
                label="Characters in Scene"
                value={characters}
                onChange={(e) => setCharacters(e.target.value)}
                placeholder="e.g., John, Sarah, Detective Morgan"
                helperText="Comma-separated list of character names"
              />
            </Grid>

            <Grid size={{ xs: 12, md: 6 }}>
              <TextField
                fullWidth
                label="Setting"
                value={setting}
                onChange={(e) => setSetting(e.target.value)}
                placeholder="e.g., A dark alley at midnight, The king's throne room"
                helperText="Where does this scene take place?"
              />
            </Grid>

            <Grid size={{ xs: 12 }}>
              <TextField
                fullWidth
                label="Scene Purpose"
                value={purpose}
                onChange={(e) => setPurpose(e.target.value)}
                placeholder="e.g., Reveal the villain's plan, First meeting between protagonists, Climactic confrontation"
                helperText="What should this scene accomplish?"
              />
            </Grid>

            <Grid size={{ xs: 12 }}>
              <PromptSelector
                label="Tone"
                options={options.tones}
                selectedValues={selectedTones}
                onChange={setSelectedTones}
                helperText="Choose the emotional tone for this scene"
              />
            </Grid>

            <Grid size={{ xs: 12 }}>
              <TextField
                fullWidth
                multiline
                rows={4}
                label="Custom Scene Details"
                value={customDetails}
                onChange={(e) => setCustomDetails(e.target.value)}
                placeholder="Any specific details, dialogue snippets, actions, or atmosphere you want included..."
              />
            </Grid>

            <Grid size={{ xs: 12 }}>
              <ModelSelector
                provider={provider}
                model={model}
                onProviderChange={setProvider}
                onModelChange={setModel}
                contentType="scene"
              />
            </Grid>
          </Grid>
        </Paper>
      )}

      {activeStep === 1 && (
        <Paper sx={{ p: 4 }}>
          <Typography variant="h5" gutterBottom>
            Ready to Generate Scene
          </Typography>
          <Typography variant="body2" color="text.secondary" paragraph>
            Click Generate to create your scene with vivid details and character
            interactions
          </Typography>
        </Paper>
      )}

      {activeStep === 2 && (
        <Box>
          <Grid container spacing={2} sx={{ mb: 3 }}>
            <Grid size={{ xs: 12, md: 6 }}>
              <TextField
                fullWidth
                label="Scene Title"
                value={sceneTitle}
                onChange={(e) => setSceneTitle(e.target.value)}
                placeholder="Enter a title for this scene"
                required
              />
            </Grid>
            <Grid size={{ xs: 12, md: 6 }}>
              <TextField
                fullWidth
                label="Chapter ID"
                type="number"
                value={chapterId}
                onChange={(e) => setChapterId(e.target.value)}
                placeholder="Enter chapter ID to attach this scene"
                required
                helperText="The ID of the chapter this scene belongs to"
              />
            </Grid>
          </Grid>
          <GenerationResult
            content={generatedContent}
            onSave={handleSave}
            onRefine={handleRefine}
            saving={saving || generating}
            entity="Scene"
          />
        </Box>
      )}

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
          ) : activeStep === 1 ? (
            "Generate with AI"
          ) : (
            "Next"
          )}
        </Button>
      </Box>
    </Container>
  );
}
