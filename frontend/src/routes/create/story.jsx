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
} from "@mui/material";
import AutoAwesomeIcon from "@mui/icons-material/AutoAwesome";
import NavigateNextIcon from "@mui/icons-material/NavigateNext";
import NavigateBeforeIcon from "@mui/icons-material/NavigateBefore";
import PromptSelector from "../../components/PromptSelector";
import GenerationResult from "../../components/GenerationResult";
import ModelSelector from "../../components/ModelSelector";

export const Route = createFileRoute("/create/story")({
  component: CreateStoryComponent,
});

const API_URL = "http://localhost:8000";
const steps = ["Select Parameters", "Generate", "Review & Save"];

function CreateStoryComponent() {
  const navigate = useNavigate();
  const searchParams = useSearch({ from: "/create/story" });
  const editId = searchParams?.edit;
  const isEditMode = !!editId;

  const [options, setOptions] = useState(null);
  const [activeStep, setActiveStep] = useState(0);
  const [loading, setLoading] = useState(false);

  // Story parameters
  const [selectedThemes, setSelectedThemes] = useState([]);
  const [selectedTones, setSelectedTones] = useState([]);
  const [storyLength, setStoryLength] = useState("");
  const [plotStructure, setPlotStructure] = useState("");
  const [conflictType, setConflictType] = useState("");
  const [customDetails, setCustomDetails] = useState("");
  const [provider, setProvider] = useState("groq");
  const [model, setModel] = useState("");

  // Results
  const [generatedContent, setGeneratedContent] = useState(null);
  const [generating, setGenerating] = useState(false);
  const [saving, setSaving] = useState(false);
  const [storyTitle, setStoryTitle] = useState("");
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  useEffect(() => {
    loadOptions();

    // Load existing story data if in edit mode
    if (isEditMode && editId) {
      loadStoryData(editId);
    }
  }, [editId, isEditMode]);

  const loadOptions = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/generate/options`);
      setOptions(response.data);
    } catch (err) {
      setError("Failed to load options");
    }
  };

  const loadStoryData = async (storyId) => {
    setLoading(true);
    try {
      const response = await axios.get(`${API_URL}/api/stories/${storyId}`);
      const story = response.data;

      // Pre-populate form with existing data
      setStoryTitle(story.title || "");
      setGeneratedContent(story.description || story.content || "");

      // Skip to review step if we have generated content
      if (story.description || story.content) {
        setActiveStep(2);
      }

      setSuccess("Story data loaded for editing");
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to load story");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerate = async () => {
    setGenerating(true);
    setError(null);

    try {
      const response = await axios.post(`${API_URL}/api/generate/story`, {
        themes: selectedThemes.length > 0 ? selectedThemes : null,
        tone: selectedTones.length > 0 ? selectedTones : null,
        length: storyLength || null,
        plot_structure: plotStructure || null,
        conflict_type: conflictType || null,
        custom_details: customDetails || null,
        provider,
        model: model || null,
      });

      setGeneratedContent(response.data.content);
      setActiveStep(2);
      setSuccess("Story outline generated successfully!");
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to generate story");
    } finally {
      setGenerating(false);
    }
  };

  const handleRefine = async (refinementInstructions) => {
    setGenerating(true);
    setError(null);

    try {
      const response = await axios.post(`${API_URL}/api/generate/story`, {
        base_content: generatedContent,
        refinement_instructions: refinementInstructions,
        provider,
        model: model || null,
      });

      setGeneratedContent(response.data.content);
      setSuccess("Story refined successfully!");
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to refine story");
    } finally {
      setGenerating(false);
    }
  };

  const handleSave = async (finalContent) => {
    if (!storyTitle.trim()) {
      setError("Please enter a story title");
      return;
    }

    setSaving(true);
    setError(null);

    try {
      if (isEditMode && editId) {
        // Update existing story
        await axios.put(`${API_URL}/api/stories/${editId}`, {
          title: storyTitle,
          description: finalContent || generatedContent,
          content: finalContent || generatedContent,
        });
        setSuccess("Story updated successfully!");

        // Navigate back to detail view after 1.5 seconds
        setTimeout(() => {
          navigate({ to: `/stories/${editId}` });
        }, 1500);
      } else {
        // Create new story
        await axios.post(`${API_URL}/api/generate/story/save`, null, {
          params: {
            title: storyTitle,
            content: finalContent || generatedContent,
          },
        });
        setSuccess("Story saved successfully!");

        setTimeout(() => {
          setActiveStep(0);
          setGeneratedContent(null);
          setStoryTitle("");
          setSuccess(null);
        }, 2000);
      }
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          `Failed to ${isEditMode ? "update" : "save"} story`
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
          {isEditMode ? "Edit Story" : "Create a Story"}
        </Typography>
        <Typography variant="body1" color="text.secondary">
          {isEditMode
            ? "Update your story details and content"
            : "Generate compelling story outlines with AI assistance"}
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
              />
            </Grid>

            <Grid size={{ xs: 12 }}>
              <PromptSelector
                label="Tone"
                options={options.tones}
                selectedValues={selectedTones}
                onChange={setSelectedTones}
              />
            </Grid>

            <Grid size={{ xs: 12, md: 6 }}>
              <FormControl fullWidth>
                <InputLabel>Story Length</InputLabel>
                <Select
                  value={storyLength}
                  onChange={(e) => setStoryLength(e.target.value)}
                  label="Story Length"
                >
                  <MenuItem value="">
                    <em>None</em>
                  </MenuItem>
                  {Object.entries(options.story_lengths).map(([key, value]) => (
                    <MenuItem key={key} value={value}>
                      {value}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>

            <Grid size={{ xs: 12, md: 6 }}>
              <FormControl fullWidth>
                <InputLabel>Plot Structure</InputLabel>
                <Select
                  value={plotStructure}
                  onChange={(e) => setPlotStructure(e.target.value)}
                  label="Plot Structure"
                >
                  <MenuItem value="">
                    <em>None</em>
                  </MenuItem>
                  {options.plot_structures.map((structure) => (
                    <MenuItem key={structure} value={structure}>
                      {structure}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>

            <Grid size={{ xs: 12 }}>
              <FormControl fullWidth>
                <InputLabel>Main Conflict</InputLabel>
                <Select
                  value={conflictType}
                  onChange={(e) => setConflictType(e.target.value)}
                  label="Main Conflict"
                >
                  <MenuItem value="">
                    <em>None</em>
                  </MenuItem>
                  {options.conflict_types.map((conflict) => (
                    <MenuItem key={conflict} value={conflict}>
                      {conflict}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>

            <Grid size={{ xs: 12 }}>
              <TextField
                fullWidth
                multiline
                rows={4}
                label="Custom Story Details"
                value={customDetails}
                onChange={(e) => setCustomDetails(e.target.value)}
                placeholder="Describe your story idea, specific plot points, character concepts, or any other details..."
              />
            </Grid>

            <Grid size={{ xs: 12 }}>
              <ModelSelector
                provider={provider}
                model={model}
                onProviderChange={setProvider}
                onModelChange={setModel}
                contentType="story"
              />
            </Grid>
          </Grid>
        </Paper>
      )}

      {activeStep === 1 && (
        <Paper sx={{ p: 4 }}>
          <Typography variant="h5" gutterBottom>
            Ready to Generate Story
          </Typography>
          <Typography variant="body2" color="text.secondary" paragraph>
            Click Generate to create your story outline
          </Typography>
        </Paper>
      )}

      {activeStep === 2 && (
        <Box>
          <TextField
            fullWidth
            label="Story Title"
            value={storyTitle}
            onChange={(e) => setStoryTitle(e.target.value)}
            placeholder="Enter a title for this story"
            sx={{ mb: 3 }}
            required
          />
          <GenerationResult
            content={generatedContent}
            onSave={handleSave}
            onRefine={handleRefine}
            saving={saving || generating}
            entity="Story"
            isEditMode={isEditMode}
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
