import { useNavigate, useSearchParams } from "react-router-dom";
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
  Switch,
  FormControlLabel,
  Chip,
} from "@mui/material";
import AutoAwesomeIcon from "@mui/icons-material/AutoAwesome";
import NavigateNextIcon from "@mui/icons-material/NavigateNext";
import NavigateBeforeIcon from "@mui/icons-material/NavigateBefore";
import PromptSelector from "../components/PromptSelector";
import GenerationResult from "../components/GenerationResult";
import ModelSelector from "../components/ModelSelector";
import StructuredWorldDisplay from "../components/StructuredWorldDisplay";
import { API_URL } from "../config/api";

const steps = ["Select Parameters", "Generate", "Review & Save"];

export default function CreateWorldPage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const editId = searchParams.get("edit");
  const isEditMode = !!editId;

  const [options, setOptions] = useState(null);
  const [activeStep, setActiveStep] = useState(0);

  // World parameters
  const [selectedThemes, setSelectedThemes] = useState([]);
  const [selectedSettings, setSelectedSettings] = useState([]);
  const [selectedElements, setSelectedElements] = useState([]);
  const [customDetails, setCustomDetails] = useState("");
  const [provider, setProvider] = useState("groq");
  const [model, setModel] = useState("");

  // Structured generation toggle
  const [useStructured, setUseStructured] = useState(true);

  // Results
  const [generatedContent, setGeneratedContent] = useState(null);
  const [generating, setGenerating] = useState(false);
  const [saving, setSaving] = useState(false);
  const [worldName, setWorldName] = useState("");
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadOptions();

    if (isEditMode && editId) {
      loadWorldData(editId);
    }
  }, [editId, isEditMode]);

  const loadWorldData = async (worldId) => {
    setLoading(true);
    try {
      const response = await axios.get(`${API_URL}/api/worlds/${worldId}`);
      setWorldName(response.data.name);
      setGeneratedContent(response.data.description);
      setActiveStep(2); // Skip to review step
    } catch (error) {
      console.error("Failed to load world:", error);
      setError("Failed to load world data");
    } finally {
      setLoading(false);
    }
  };

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
      const endpoint = useStructured
        ? `${API_URL}/api/generate/world/structured`
        : `${API_URL}/api/generate/world`;

      const response = await axios.post(endpoint, {
        themes: selectedThemes.length > 0 ? selectedThemes : null,
        setting: selectedSettings.length > 0 ? selectedSettings : null,
        elements: selectedElements.length > 0 ? selectedElements : null,
        custom_details: customDetails || null,
        provider,
        model: model || null,
      });

      setGeneratedContent(
        useStructured ? response.data : response.data.content
      );
      setActiveStep(2);
      setSuccess(
        `World generated successfully using ${useStructured ? "structured" : "free-form"} generation!`
      );
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
      const endpoint = useStructured
        ? `${API_URL}/api/generate/world/structured`
        : `${API_URL}/api/generate/world`;

      const requestData = useStructured
        ? {
            themes: selectedThemes.length > 0 ? selectedThemes : null,
            setting: selectedSettings.length > 0 ? selectedSettings : null,
            elements: selectedElements.length > 0 ? selectedElements : null,
            custom_details: `${customDetails}\n\nRefinement: ${refinementInstructions}`,
            provider,
            model: model || null,
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
      if (isEditMode && editId) {
        // Update existing world
        await axios.put(`${API_URL}/api/worlds/${editId}`, {
          name: worldName,
          description: useStructured
            ? JSON.stringify(finalContent || generatedContent)
            : finalContent || generatedContent,
          history: finalContent || generatedContent,
          geography: finalContent || generatedContent,
          culture: finalContent || generatedContent,
          lore: finalContent || generatedContent,
        });

        setSuccess("World updated successfully!");
        setTimeout(() => {
          navigate({ to: `/worlds/${editId}` });
        }, 1500);
      } else {
        // Create new world
        if (useStructured) {
          // Use structured save endpoint
          await axios.post(`${API_URL}/api/generate/world/structured/save`, {
            world_profile: finalContent || generatedContent,
          });
        } else {
          // Use legacy save endpoint
          await axios.post(`${API_URL}/api/generate/world/save`, null, {
            params: {
              name: worldName,
              content: finalContent || generatedContent,
            },
          });
        }

        setSuccess("World saved successfully!");
        setTimeout(() => {
          setActiveStep(0);
          setGeneratedContent(null);
          setWorldName("");
          setSuccess(null);
        }, 2000);
      }
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          `Failed to ${isEditMode ? "update" : "save"} world`
      );
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
          {isEditMode ? "Edit World" : "Build a World"}
        </Typography>
        <Typography variant="body1" color="text.secondary">
          {isEditMode
            ? "Update your world's details and lore"
            : "Create immersive worlds with rich lore and detail"}
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
                  ? "Structured generation creates comprehensive world profiles with organized sections, detailed history, geography, culture, and more."
                  : "Free-form generation creates narrative-style world descriptions with more creative flexibility."}
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
              <ModelSelector
                provider={provider}
                model={model}
                onProviderChange={setProvider}
                onModelChange={setModel}
                contentType="world"
              />
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

          {/* Display Component - Conditional based on generation mode */}
          {useStructured ? (
            <Box sx={{ mb: 3 }}>
              <StructuredWorldDisplay worldProfile={generatedContent} />
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
                  disabled={saving || generating || !worldName.trim()}
                  startIcon={saving ? <CircularProgress size={20} /> : null}
                >
                  {saving ? "Saving..." : isEditMode ? "Update" : "Save World"}
                </Button>
              </Box>
            </Box>
          ) : (
            <GenerationResult
              content={generatedContent}
              onSave={handleSave}
              onRefine={handleRefine}
              saving={saving || generating}
              entity="World"
              isEditMode={isEditMode}
            />
          )}
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
