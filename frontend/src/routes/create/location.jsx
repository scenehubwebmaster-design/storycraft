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

export const Route = createFileRoute("/create/location")({
  component: CreateLocationComponent,
});

const steps = ["Location Setup", "Generate", "Review & Save"];

const LOCATION_TYPES = [
  "City",
  "Town",
  "Village",
  "Fortress",
  "Castle",
  "Tavern",
  "Inn",
  "Temple",
  "Ruins",
  "Cave",
  "Forest",
  "Mountain",
  "Desert",
  "Ocean",
  "Dungeon",
  "Laboratory",
  "Mansion",
  "Market",
  "Port",
  "Wilderness",
];

function CreateLocationComponent() {
  const [options, setOptions] = useState(null);
  const [activeStep, setActiveStep] = useState(0);

  // Location parameters
  const [locationName, setLocationName] = useState("");
  const [locationType, setLocationType] = useState("");
  const [worldContext, setWorldContext] = useState("");
  const [selectedSettings, setSelectedSettings] = useState([]);
  const [significance, setSignificance] = useState("");
  const [customDetails, setCustomDetails] = useState("");
  const [provider, setProvider] = useState("groq");
  const [model, setModel] = useState("");

  // Results
  const [generatedContent, setGeneratedContent] = useState(null);
  const [generating, setGenerating] = useState(false);
  const [saving, setSaving] = useState(false);
  const [worldId, setWorldId] = useState("");
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
      const response = await axios.post(`${API_URL}/api/generate/location`, {
        name: locationName || null,
        location_type: locationType || null,
        world_context: worldContext || null,
        setting: selectedSettings.length > 0 ? selectedSettings : null,
        significance: significance || null,
        custom_details: customDetails || null,
        provider,
        model: model || null,
      });

      setGeneratedContent(response.data.content);
      setActiveStep(2);
      setSuccess("Location generated successfully!");
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to generate location");
    } finally {
      setGenerating(false);
    }
  };

  const handleRefine = async (refinementInstructions) => {
    setGenerating(true);
    setError(null);

    try {
      const response = await axios.post(`${API_URL}/api/generate/location`, {
        base_content: generatedContent,
        refinement_instructions: refinementInstructions,
        provider,
        model: model || null,
      });

      setGeneratedContent(response.data.content);
      setSuccess("Location refined successfully!");
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to refine location");
    } finally {
      setGenerating(false);
    }
  };

  const handleSave = async (finalContent) => {
    if (!locationName.trim()) {
      setError("Please enter a location name");
      return;
    }
    if (!worldId) {
      setError("Please enter a world ID");
      return;
    }

    setSaving(true);
    setError(null);

    try {
      await axios.post(`${API_URL}/api/generate/location/save`, null, {
        params: {
          name: locationName,
          description: finalContent || generatedContent,
          world_id: parseInt(worldId),
          location_type: locationType || "Other",
        },
      });

      setSuccess("Location saved successfully!");
      setTimeout(() => {
        setActiveStep(0);
        setGeneratedContent(null);
        setLocationName("");
        setSuccess(null);
      }, 2000);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to save location");
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
          Create a Location
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Design rich, atmospheric locations that bring your world to life
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
            <Grid size={{ xs: 12, md: 6 }}>
              <TextField
                fullWidth
                label="Location Name"
                value={locationName}
                onChange={(e) => setLocationName(e.target.value)}
                placeholder="e.g., The Dragon's Rest Tavern, Crystal Peaks"
                helperText="Give your location a memorable name"
              />
            </Grid>

            <Grid size={{ xs: 12, md: 6 }}>
              <FormControl fullWidth>
                <InputLabel>Location Type</InputLabel>
                <Select
                  value={locationType}
                  onChange={(e) => setLocationType(e.target.value)}
                  label="Location Type"
                >
                  <MenuItem value="">
                    <em>Select a type</em>
                  </MenuItem>
                  {LOCATION_TYPES.map((type) => (
                    <MenuItem key={type} value={type}>
                      {type}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>

            <Grid size={{ xs: 12 }}>
              <TextField
                fullWidth
                multiline
                rows={3}
                label="World Context"
                value={worldContext}
                onChange={(e) => setWorldContext(e.target.value)}
                placeholder="Describe the world this location exists in..."
                helperText="Optional: Help the AI understand what kind of world this location fits into"
              />
            </Grid>

            <Grid size={{ xs: 12 }}>
              <PromptSelector
                label="Setting/Atmosphere"
                options={options.settings}
                selectedValues={selectedSettings}
                onChange={setSelectedSettings}
                helperText="Choose settings that describe the atmosphere"
              />
            </Grid>

            <Grid size={{ xs: 12 }}>
              <TextField
                fullWidth
                label="Significance"
                value={significance}
                onChange={(e) => setSignificance(e.target.value)}
                placeholder="e.g., A gathering place for adventurers, The last safe haven before the dark lands"
                helperText="What makes this location important or interesting?"
              />
            </Grid>

            <Grid size={{ xs: 12 }}>
              <TextField
                fullWidth
                multiline
                rows={4}
                label="Custom Location Details"
                value={customDetails}
                onChange={(e) => setCustomDetails(e.target.value)}
                placeholder="Any specific features, history, inhabitants, secrets, or atmosphere you want to include..."
              />
            </Grid>

            <Grid size={{ xs: 12 }}>
              <ModelSelector
                provider={provider}
                model={model}
                onProviderChange={setProvider}
                onModelChange={setModel}
                contentType="location"
              />
            </Grid>
          </Grid>
        </Paper>
      )}

      {activeStep === 1 && (
        <Paper sx={{ p: 4 }}>
          <Typography variant="h5" gutterBottom>
            Ready to Generate Location
          </Typography>
          <Typography variant="body2" color="text.secondary" paragraph>
            Click Generate to create a rich, detailed location with atmosphere
            and story potential
          </Typography>
        </Paper>
      )}

      {activeStep === 2 && (
        <Box>
          <Grid container spacing={2} sx={{ mb: 3 }}>
            <Grid size={{ xs: 12, md: 6 }}>
              <TextField
                fullWidth
                label="Location Name"
                value={locationName}
                onChange={(e) => setLocationName(e.target.value)}
                placeholder="Enter the name of this location"
                required
              />
            </Grid>
            <Grid size={{ xs: 12, md: 6 }}>
              <TextField
                fullWidth
                label="World ID"
                type="number"
                value={worldId}
                onChange={(e) => setWorldId(e.target.value)}
                placeholder="Enter world ID to attach this location"
                required
                helperText="The ID of the world this location belongs to"
              />
            </Grid>
          </Grid>
          <GenerationResult
            content={generatedContent}
            onSave={handleSave}
            onRefine={handleRefine}
            saving={saving || generating}
            entity="Location"
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
