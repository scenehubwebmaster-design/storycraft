import React, { useState, useEffect } from "react";
import {
  Drawer,
  Box,
  Typography,
  IconButton,
  Divider,
  Stack,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  Checkbox,
  FormControlLabel,
  Button,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Tooltip,
  Chip,
} from "@mui/material";
import {
  Close as CloseIcon,
  ExpandMore as ExpandMoreIcon,
  Settings as SettingsIcon,
  VolumeUp as VolumeUpIcon,
  SmartToy as AIIcon,
  MenuBook as RAGIcon,
  Campaign as CampaignIcon,
  RecordVoiceOver as VoiceIcon,
  Image as ImageIcon,
} from "@mui/icons-material";
import CampaignManager from "./CampaignManager";

/**
 * SettingsDrawer - Offcanvas settings panel
 * Combines AI settings, TTS settings, RAG settings, and campaign management
 */
const SettingsDrawer = ({
  open,
  onClose,
  // AI Settings
  provider,
  setProvider,
  model,
  setModel,
  availableModels,
  // RAG Settings
  selectedSession,
  updateSessionSettings,
  // TTS Settings
  ttsEnabled,
  setTtsEnabled,
  ttsAutoPlay,
  setTtsAutoPlay,
  ttsVoice,
  setTtsVoice,
  ttsFlavorTextOnly,
  setTtsFlavorTextOnly,
  // Scene Image Settings
  sceneImageAutoGenerate,
  setSceneImageAutoGenerate,
  // Campaign
  activeCampaign,
  handleCampaignUpdate,
}) => {
  const [expandedPanel, setExpandedPanel] = useState("ai");
  const [ttsProvider, setTtsProvider] = useState("kitten");
  const [settingsLoaded, setSettingsLoaded] = useState(false);

  // Load TTS settings from database
  useEffect(() => {
    if (open && !settingsLoaded) {
      loadTtsSettings();
    }
  }, [open]);

  const loadTtsSettings = async () => {
    try {
      const response = await fetch("http://localhost:8000/api/settings/tts");
      if (response.ok) {
        const settings = await response.json();
        setTtsProvider(settings.tts_provider || "kitten");
        setTtsEnabled(settings.tts_enabled ?? true);
        setTtsAutoPlay(settings.tts_auto_play ?? false);
        setTtsVoice(settings.tts_voice || "tara");
        setSettingsLoaded(true);
      }
    } catch (error) {
      console.error("Error loading TTS settings:", error);
    }
  };

  const saveTtsSettings = async () => {
    try {
      const response = await fetch("http://localhost:8000/api/settings/", {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          tts_provider: ttsProvider,
          tts_voice: ttsVoice,
          tts_enabled: ttsEnabled,
          tts_auto_play: ttsAutoPlay,
        }),
      });

      if (!response.ok) {
        console.error("Failed to save TTS settings");
      }
    } catch (error) {
      console.error("Error saving TTS settings:", error);
    }
  };

  // Save settings whenever they change
  useEffect(() => {
    if (settingsLoaded) {
      saveTtsSettings();
    }
  }, [ttsProvider, ttsVoice, ttsEnabled, ttsAutoPlay]);

  // Voice options based on provider
  const getVoiceOptions = () => {
    if (ttsProvider === "openai") {
      return [
        { value: "alloy", label: "Alloy (Neutral)" },
        { value: "echo", label: "Echo (Male)" },
        { value: "fable", label: "Fable (British Male)" },
        { value: "onyx", label: "Onyx (Deep Male)" },
        { value: "nova", label: "Nova (Female)" },
        { value: "shimmer", label: "Shimmer (Soft Female)" },
      ];
    }
    // KittenTTS voices
    return [
      { value: "tara", label: "Tara (Female, Warm)" },
      { value: "leah", label: "Leah (Female, Friendly)" },
      { value: "jess", label: "Jess (Female, Energetic)" },
      { value: "mia", label: "Mia (Female, Mysterious)" },
      { value: "leo", label: "Leo (Male, Deep)" },
      { value: "dan", label: "Dan (Male, Classic)" },
      { value: "zac", label: "Zac (Male, Young)" },
      { value: "zoe", label: "Zoe (Neutral)" },
    ];
  };

  const handleAccordionChange = (panel) => (event, isExpanded) => {
    setExpandedPanel(isExpanded ? panel : false);
  };

  // Handle provider change and reset voice to valid default
  const handleProviderChange = (newProvider) => {
    setTtsProvider(newProvider);

    // Reset voice to valid default for new provider
    if (newProvider === "openai") {
      // Check if current voice is valid for OpenAI, otherwise reset
      const openaiVoices = [
        "alloy",
        "echo",
        "fable",
        "onyx",
        "nova",
        "shimmer",
      ];
      if (!openaiVoices.includes(ttsVoice)) {
        setTtsVoice("nova"); // Default OpenAI voice
      }
    } else if (newProvider === "kitten") {
      // Check if current voice is valid for KittenTTS, otherwise reset
      const kittenVoices = [
        "tara",
        "leah",
        "jess",
        "mia",
        "leo",
        "dan",
        "zac",
        "zoe",
      ];
      if (!kittenVoices.includes(ttsVoice)) {
        setTtsVoice("tara"); // Default Kitten voice
      }
    }
  };

  return (
    <Drawer
      anchor="right"
      open={open}
      onClose={onClose}
      sx={{
        "& .MuiDrawer-paper": {
          width: { xs: "100%", sm: 420 },
          bgcolor: "background.paper",
        },
      }}
    >
      {/* Header */}
      <Box
        sx={{
          p: 2,
          background: "linear-gradient(135deg, #d4af37 0%, #8b0000 100%)",
          color: "white",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
        }}
      >
        <Stack direction="row" spacing={1} alignItems="center">
          <SettingsIcon />
          <Typography variant="h6">Settings & Configuration</Typography>
        </Stack>
        <IconButton onClick={onClose} sx={{ color: "white" }}>
          <CloseIcon />
        </IconButton>
      </Box>

      <Box sx={{ overflow: "auto", flexGrow: 1 }}>
        {/* AI Model Settings */}
        <Accordion
          expanded={expandedPanel === "ai"}
          onChange={handleAccordionChange("ai")}
          sx={{ boxShadow: "none", "&:before": { display: "none" } }}
        >
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Stack direction="row" spacing={1.5} alignItems="center">
              <AIIcon color="primary" />
              <Typography variant="subtitle1" fontWeight={600}>
                AI Model Settings
              </Typography>
            </Stack>
          </AccordionSummary>
          <AccordionDetails>
            <Stack spacing={2.5}>
              <FormControl fullWidth size="small">
                <InputLabel>Provider</InputLabel>
                <Select
                  value={provider}
                  label="Provider"
                  onChange={(e) => setProvider(e.target.value)}
                >
                  <MenuItem value="groq">Groq</MenuItem>
                  <MenuItem value="openai">OpenAI</MenuItem>
                  <MenuItem value="google">Google</MenuItem>
                  <MenuItem value="anthropic">Anthropic</MenuItem>
                  <MenuItem value="http://100.120.44.114:1234/v1">
                    LM Studio (Local)
                  </MenuItem>
                </Select>
              </FormControl>

              {availableModels.length > 0 ? (
                <FormControl fullWidth size="small">
                  <InputLabel>Model</InputLabel>
                  <Select
                    value={model}
                    label="Model"
                    onChange={(e) => setModel(e.target.value)}
                  >
                    <MenuItem value="">(default)</MenuItem>
                    {availableModels.map((m) => (
                      <MenuItem key={m.id} value={m.id}>
                        {m.name}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              ) : (
                <TextField
                  fullWidth
                  size="small"
                  label="Model (optional)"
                  value={model}
                  onChange={(e) => setModel(e.target.value)}
                />
              )}

              <Typography variant="body2" color="text.secondary">
                Choose the AI provider and model for generating DM responses
              </Typography>
            </Stack>
          </AccordionDetails>
        </Accordion>

        <Divider />

        {/* RAG Context Settings */}
        {selectedSession && (
          <>
            <Accordion
              expanded={expandedPanel === "rag"}
              onChange={handleAccordionChange("rag")}
              sx={{ boxShadow: "none", "&:before": { display: "none" } }}
            >
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Stack direction="row" spacing={1.5} alignItems="center">
                  <RAGIcon color="secondary" />
                  <Typography variant="subtitle1" fontWeight={600}>
                    RAG Context
                  </Typography>
                </Stack>
              </AccordionSummary>
              <AccordionDetails>
                <Stack spacing={2.5}>
                  <FormControlLabel
                    control={
                      <Checkbox
                        checked={!!selectedSession.include_context}
                        onChange={(e) =>
                          updateSessionSettings({
                            include_context: e.target.checked,
                          })
                        }
                        color="secondary"
                      />
                    }
                    label={
                      <Typography variant="body2">
                        Enable RAG Context Retrieval
                      </Typography>
                    }
                  />

                  <Tooltip title="Number of D&D references to retrieve from the knowledge base">
                    <TextField
                      size="small"
                      label="Context Chunks (k)"
                      type="number"
                      fullWidth
                      value={selectedSession.top_k || 5}
                      onChange={(e) =>
                        updateSessionSettings({
                          top_k: Number(e.target.value || 1),
                        })
                      }
                      InputProps={{
                        inputProps: { min: 1, max: 20 },
                      }}
                    />
                  </Tooltip>

                  <Typography variant="body2" color="text.secondary">
                    RAG (Retrieval-Augmented Generation) pulls relevant D&D 5e
                    rules and content from the Player's Handbook to enhance DM
                    responses
                  </Typography>
                </Stack>
              </AccordionDetails>
            </Accordion>

            <Divider />
          </>
        )}

        {/* TTS Voice Settings */}
        <Accordion
          expanded={expandedPanel === "tts"}
          onChange={handleAccordionChange("tts")}
          sx={{ boxShadow: "none", "&:before": { display: "none" } }}
        >
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Stack direction="row" spacing={1.5} alignItems="center">
              <VolumeUpIcon color="primary" />
              <Typography variant="subtitle1" fontWeight={600}>
                Voice Narration (TTS)
              </Typography>
            </Stack>
          </AccordionSummary>
          <AccordionDetails>
            <Stack spacing={2.5}>
              <FormControlLabel
                control={
                  <Checkbox
                    checked={ttsEnabled}
                    onChange={(e) => setTtsEnabled(e.target.checked)}
                    color="primary"
                  />
                }
                label={
                  <Typography variant="body2">
                    Enable Voice Narration
                  </Typography>
                }
              />

              <FormControlLabel
                control={
                  <Checkbox
                    checked={ttsAutoPlay}
                    onChange={(e) => setTtsAutoPlay(e.target.checked)}
                    disabled={!ttsEnabled}
                    color="primary"
                  />
                }
                label={
                  <Typography variant="body2">
                    Auto-play DM Responses
                  </Typography>
                }
              />

              {ttsEnabled && (
                <>
                  <Box>
                    <Typography
                      variant="body2"
                      color="text.secondary"
                      gutterBottom
                    >
                      TTS Provider
                    </Typography>
                    <Stack direction="row" spacing={1}>
                      <Chip
                        label="KittenTTS"
                        color={ttsProvider === "kitten" ? "primary" : "default"}
                        onClick={() => handleProviderChange("kitten")}
                        variant={
                          ttsProvider === "kitten" ? "filled" : "outlined"
                        }
                      />
                      <Chip
                        label="OpenAI Whisper"
                        color={ttsProvider === "openai" ? "primary" : "default"}
                        onClick={() => handleProviderChange("openai")}
                        variant={
                          ttsProvider === "openai" ? "filled" : "outlined"
                        }
                      />
                    </Stack>
                    <Typography
                      variant="caption"
                      color="text.secondary"
                      sx={{ mt: 0.5, display: "block" }}
                    >
                      {ttsProvider === "kitten"
                        ? "Local, free TTS (8 voices)"
                        : "Cloud-based, premium quality (6 voices)"}
                    </Typography>
                  </Box>

                  <FormControl size="small" fullWidth>
                    <InputLabel>Voice Character</InputLabel>
                    <Select
                      value={ttsVoice}
                      label="Voice Character"
                      onChange={(e) => setTtsVoice(e.target.value)}
                      startAdornment={
                        <VoiceIcon fontSize="small" sx={{ mr: 1, ml: 1 }} />
                      }
                    >
                      {getVoiceOptions().map((voice) => (
                        <MenuItem key={voice.value} value={voice.value}>
                          {voice.label}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </>
              )}

              {ttsEnabled && (
                <FormControlLabel
                  control={
                    <Checkbox
                      checked={ttsFlavorTextOnly}
                      onChange={(e) => setTtsFlavorTextOnly(e.target.checked)}
                      color="primary"
                      size="small"
                    />
                  }
                  label={
                    <Typography variant="body2">
                      Narrate RP Text Only (skip stats/mechanics)
                    </Typography>
                  }
                />
              )}

              <Typography variant="body2" color="text.secondary">
                Text-to-speech converts DM messages into spoken narration for
                immersive gameplay
              </Typography>
            </Stack>
          </AccordionDetails>
        </Accordion>

        <Divider />

        {/* Scene Image Settings */}
        <Accordion
          expanded={expandedPanel === "sceneimage"}
          onChange={handleAccordionChange("sceneimage")}
          sx={{ boxShadow: "none", "&:before": { display: "none" } }}
        >
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Stack direction="row" spacing={1.5} alignItems="center">
              <ImageIcon color="primary" />
              <Typography variant="subtitle1" fontWeight={600}>
                Scene Images (Stable Diffusion)
              </Typography>
            </Stack>
          </AccordionSummary>
          <AccordionDetails>
            <Stack spacing={2.5}>
              <FormControlLabel
                control={
                  <Checkbox
                    checked={sceneImageAutoGenerate}
                    onChange={(e) =>
                      setSceneImageAutoGenerate(e.target.checked)
                    }
                    color="primary"
                  />
                }
                label={
                  <Typography variant="body2">
                    Auto-generate Scene Images for DM Responses
                  </Typography>
                }
              />

              <Typography variant="body2" color="text.secondary">
                Automatically generates fantasy artwork for DM messages using
                Stable Diffusion. Creates immersive visual scenes based on the
                narrative description.
              </Typography>
            </Stack>
          </AccordionDetails>
        </Accordion>

        <Divider />

        {/* Campaign Management */}
        {activeCampaign && (
          <>
            <Accordion
              expanded={expandedPanel === "campaign"}
              onChange={handleAccordionChange("campaign")}
              sx={{ boxShadow: "none", "&:before": { display: "none" } }}
            >
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Stack direction="row" spacing={1.5} alignItems="center">
                  <CampaignIcon color="secondary" />
                  <Typography variant="subtitle1" fontWeight={600}>
                    Campaign Management
                  </Typography>
                </Stack>
              </AccordionSummary>
              <AccordionDetails>
                <CampaignManager
                  campaignId={activeCampaign.id}
                  onCampaignUpdate={handleCampaignUpdate}
                />
              </AccordionDetails>
            </Accordion>
            <Divider />
          </>
        )}
      </Box>

      {/* Footer */}
      <Box sx={{ p: 2, borderTop: 1, borderColor: "divider" }}>
        <Button fullWidth variant="contained" onClick={onClose}>
          Close Settings
        </Button>
      </Box>
    </Drawer>
  );
};

export default SettingsDrawer;
