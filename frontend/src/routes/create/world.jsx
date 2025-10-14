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

export const Route = createFileRoute("/create/world")({
  component: CreateWorldComponent,
});

const steps = ["World Elements", "Generate", "Review & Save"];

function CreateWorldComponent() {
  const [options, setOptions] = useState(null);
  const [activeStep, setActiveStep] = useState(0);

  // World parameters
  const [selectedThemes, setSelectedThemes] = useState([]);
  const [selectedSettings, setSelectedSettings] = useState([]);
  const [selectedElements, setSelectedElements] = useState([]);
  const [customDetails, setCustomDetails] = useState("");
  const [provider, setProvider] = useState("openai");

  // Results
  const [generatedContent, setGeneratedContent] = useState(null);
  const [generating, setGenerating] = useState(false);
  const [saving, setSaving] = useState(false);
  const [worldName, setWorldName] = useState("");
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  useEffect(() => {
    loadOptions();
  }, []);

  const loadOptions = async () => {
    try {
      const response = await axios.get(`/api/generate/options`);
      setOptions(response.data);
    } catch (err) {
      setError("Failed to load options");
    }
  };

  const handleGenerate = async () => {
    setGenerating(true);
    setError(null);

    try {
      const response = await axios.post(`/api/generate/world`, {
        themes: selectedThemes.length > 0 ? selectedThemes : null,
        setting: selectedSettings.length > 0 ? selectedSettings : null,
        elements: selectedElements.length > 0 ? selectedElements : null,
        custom_details: customDetails || null,
        provider,
      });

      setGeneratedContent(response.data.content);
      setActiveStep(2);
      setSuccess("World generated successfully!");
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to generate world");
    } finally {
      setGenerating(false);
    }
  };

  const handleRefine = async (refinementInstructions) => {
    setGenerating(true);
    setError(null);

    try {
      const response = await axios.post(`/api/generate/world`, {
        base_content: generatedContent,
        refinement_instructions: refinementInstructions,
        provider,
      });

      setGeneratedContent(response.data.content);
      setSuccess("World refined successfully!");
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to refine world");
    } finally {
      setGenerating(false);
    }
  };

  const handleSave = async (finalContent) => {
    if (!worldName.trim()) {
      setError("Please enter a world name");
      return;
    }

    setSaving(true);
    setError(null);

    try {
      await axios.post(`/api/generate/world/save`, null, {
        params: {
          name: worldName,
          content: finalContent || generatedContent,
        },
      });

      setSuccess("World saved successfully!");
      setTimeout(() => {
        setActiveStep(0);
        setGeneratedContent(null);
        setWorldName("");
        setSuccess(null);
      }, 2000);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to save world");
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
          Build a World
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Create immersive worlds with rich lore and detail
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
              <PromptSelector
                label="Themes/Genre"
                options={options.themes}
                selectedValues={selectedThemes}
                onChange={setSelectedThemes}
                helperText="Select the genre and themes for your world"
              />
            </Grid>

            <Grid size={{ xs: 12 }}>
              <PromptSelector
                label="Setting Type"
                options={options.settings}
                selectedValues={selectedSettings}
                onChange={setSelectedSettings}
                helperText="Choose the setting and environment"
              />
            </Grid>

            <Grid size={{ xs: 12 }}>
              <PromptSelector
                label="World Elements"
                options={options.world_elements}
                selectedValues={selectedElements}
                onChange={setSelectedElements}
                helperText="Select which aspects to focus on"
              />
            </Grid>

            <Grid size={{ xs: 12 }}>
              <TextField
                fullWidth
                multiline
                rows={5}
                label="Custom World Details"
                value={customDetails}
                onChange={(e) => setCustomDetails(e.target.value)}
                placeholder="Describe your world vision: unique features, history, cultures, magic systems, or any specific elements you want included..."
                helperText="Be as detailed as you'd like - the AI will use this to create a richer world"
              />
            </Grid>

            <Grid size={{ xs: 12 }}>
              <FormControl fullWidth>
                <InputLabel>AI Provider</InputLabel>
                <Select
                  value={provider}
                  onChange={(e) => setProvider(e.target.value)}
                  label="AI Provider"
                >
                  <MenuItem value="openai">OpenAI (GPT)</MenuItem>
                  <MenuItem value="anthropic">Anthropic (Claude)</MenuItem>
                  <MenuItem value="google">Google (Gemini)</MenuItem>
                </Select>
              </FormControl>
            </Grid>
          </Grid>
        </Paper>
      )}

      {activeStep === 1 && (
        <Paper sx={{ p: 4 }}>
          <Typography variant="h5" gutterBottom>
            Ready to Generate World
          </Typography>
          <Typography variant="body2" color="text.secondary" paragraph>
            Click Generate to create your world with all its details
          </Typography>
        </Paper>
      )}

      {activeStep === 2 && (
        <Box>
          <TextField
            fullWidth
            label="World Name"
            value={worldName}
            onChange={(e) => setWorldName(e.target.value)}
            placeholder="Enter a name for this world"
            sx={{ mb: 3 }}
            required
          />
          <GenerationResult
            content={generatedContent}
            onSave={handleSave}
            onRefine={handleRefine}
            saving={saving || generating}
            entity="World"
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
