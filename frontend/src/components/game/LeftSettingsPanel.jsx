/**
 * LeftSettingsPanel - Tabbed settings panel for DM Chat
 * Replaces the settings drawer with an always-visible left panel
 */

import React, { useState, useEffect } from "react";
import {
  Box,
  Tabs,
  Tab,
  Typography,
  Stack,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  Checkbox,
  FormControlLabel,
  Chip,
  Tooltip,
  Divider,
  Paper,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
  Button,
} from "@mui/material";
import {
  SmartToy as AIIcon,
  Storage as RAGIcon,
  VolumeUp as VolumeUpIcon,
  RecordVoiceOver as VoiceIcon,
  Image as ImageIcon,
  Campaign as CampaignIcon,
  ChevronLeft as CollapseIcon,
  ChevronRight as ExpandIcon,
  Delete as DeleteIcon,
} from "@mui/icons-material";
import CampaignManager from "../CampaignManager";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

function TabPanel({ children, value, index, ...other }) {
  return (
    <Box
      role="tabpanel"
      hidden={value !== index}
      id={`settings-tabpanel-${index}`}
      aria-labelledby={`settings-tab-${index}`}
      sx={{ flexGrow: 1, overflow: "auto", p: 2 }}
      {...other}
    >
      {value === index && children}
    </Box>
  );
}

export default function LeftSettingsPanel({
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
  // Campaign Selection
  onCampaignSelect,
  onCreateCampaign,
}) {
  const [activeTab, setActiveTab] = useState(0);
  const [ttsProvider, setTtsProvider] = useState("kitten");
  const [settingsLoaded, setSettingsLoaded] = useState(false);
  const [campaigns, setCampaigns] = useState([]);
  const [loadingCampaigns, setLoadingCampaigns] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [campaignToDelete, setCampaignToDelete] = useState(null);
  const [dmRollForPlayers, setDmRollForPlayers] = useState(false);
  // Bulk delete state
  const [bulkMode, setBulkMode] = useState(false);
  const [selectedBulk, setSelectedBulk] = useState([]);
  const [bulkDeleteDialogOpen, setBulkDeleteDialogOpen] = useState(false);

  // Load settings from database (TTS + DM roll preference)
  useEffect(() => {
    if (!settingsLoaded) {
      loadSettings();
    }
  }, []);

  // Load campaigns when session changes
  useEffect(() => {
    loadCampaigns();
  }, [selectedSession]);

  // Reload campaigns when activeCampaign changes (e.g., after creation)
  useEffect(() => {
    if (activeCampaign) {
      loadCampaigns();
    }
  }, [activeCampaign?.id]);

  const loadCampaigns = async () => {
    console.log(
      "Loading campaigns...",
      selectedSession ? `for session ${selectedSession.id}` : "ALL campaigns"
    );
    setLoadingCampaigns(true);
    try {
      // Always load campaigns - if no session, load all campaigns
      const url = selectedSession
        ? `${API_URL}/api/campaigns/?chat_session_id=${selectedSession.id}`
        : `${API_URL}/api/campaigns/`;
      console.log("Fetching campaigns from:", url);

      const response = await fetch(url);
      console.log("Campaign fetch response status:", response.status);

      if (response.ok) {
        const data = await response.json();
        console.log("Campaigns loaded:", data.length, "campaigns");
        setCampaigns(data || []);
      } else {
        const errorText = await response.text();
        console.error("Failed to load campaigns:", response.status, errorText);
      }
    } catch (error) {
      console.error("Error loading campaigns:", error);
    } finally {
      setLoadingCampaigns(false);
    }
  };

  const loadSettings = async () => {
    try {
      const response = await fetch(`${API_URL}/api/settings/`);
      if (response.ok) {
        const settings = await response.json();
        // TTS related
        setTtsProvider(settings.tts_provider || "kitten");
        setTtsEnabled(settings.tts_enabled ?? true);
        setTtsAutoPlay(settings.tts_auto_play ?? false);
        setTtsVoice(settings.tts_voice || "tara");
        // DM roll preference
        setDmRollForPlayers(Boolean(settings.dm_roll_for_players));
        setSettingsLoaded(true);
      }
    } catch (error) {
      console.error("Error loading settings:", error);
    }
  };

  const handleDeleteCampaign = (campaign, event) => {
    event.stopPropagation(); // Prevent the select from opening
    setCampaignToDelete(campaign);
    setDeleteDialogOpen(true);
  };

  const confirmDeleteCampaign = async () => {
    if (!campaignToDelete) return;

    try {
      const response = await fetch(
        `${API_URL}/api/campaigns/${campaignToDelete.id}`,
        {
          method: "DELETE",
        }
      );

      if (response.ok) {
        console.log("Campaign deleted successfully:", campaignToDelete.title);
        // If the deleted campaign was active, clear it
        if (activeCampaign?.id === campaignToDelete.id && onCampaignSelect) {
          onCampaignSelect(null);
        }
        // Reload campaigns list
        await loadCampaigns();
      } else {
        const errorText = await response.text();
        console.error("Failed to delete campaign:", response.status, errorText);
        alert(`Failed to delete campaign: ${errorText}`);
      }
    } catch (error) {
      console.error("Error deleting campaign:", error);
      alert(`Error deleting campaign: ${error.message}`);
    } finally {
      setDeleteDialogOpen(false);
      setCampaignToDelete(null);
    }
  };

  const confirmBulkDelete = async () => {
    if (!selectedBulk || selectedBulk.length === 0) return;

    try {
      for (const id of selectedBulk) {
        try {
          const response = await fetch(`${API_URL}/api/campaigns/${id}`, {
            method: "DELETE",
          });

          if (!response.ok) {
            const errorText = await response.text();
            console.error(
              `Failed to delete campaign ${id}:`,
              response.status,
              errorText
            );
          }
        } catch (err) {
          console.error(`Error deleting campaign ${id}:`, err);
        }
      }

      // Reload campaigns and clear selection
      await loadCampaigns();
      setSelectedBulk([]);
      setBulkMode(false);
    } catch (error) {
      console.error("Bulk delete failed:", error);
      alert(`Bulk delete failed: ${error?.message || error}`);
    } finally {
      setBulkDeleteDialogOpen(false);
    }
  };

  const saveSettings = async () => {
    try {
      const response = await fetch(`${API_URL}/api/settings/`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          tts_provider: ttsProvider,
          tts_voice: ttsVoice,
          tts_enabled: ttsEnabled,
          tts_auto_play: ttsAutoPlay,
          // DM roll toggle persisted as dm_roll_for_players
          dm_roll_for_players: dmRollForPlayers,
        }),
      });

      if (!response.ok) {
        console.error("Failed to save settings");
      }
    } catch (error) {
      console.error("Error saving settings:", error);
    }
  };

  // Save settings whenever they change
  useEffect(() => {
    if (settingsLoaded) {
      saveSettings();
    }
  }, [ttsProvider, ttsVoice, ttsEnabled, ttsAutoPlay, dmRollForPlayers]);

  // Handle provider change and reset voice to valid default
  const handleProviderChange = (newProvider) => {
    setTtsProvider(newProvider);

    if (newProvider === "openai") {
      const openaiVoices = [
        "alloy",
        "echo",
        "fable",
        "onyx",
        "nova",
        "shimmer",
      ];
      if (!openaiVoices.includes(ttsVoice)) {
        setTtsVoice("nova");
      }
    } else if (newProvider === "kitten") {
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
        setTtsVoice("tara");
      }
    }
  };

  // Voice options based on provider
  const getVoiceOptions = () => {
    if (ttsProvider === "openai") {
      return [
        { value: "alloy", label: "Alloy (Neutral, balanced)" },
        { value: "echo", label: "Echo (Male, clear)" },
        { value: "fable", label: "Fable (British, expressive)" },
        { value: "onyx", label: "Onyx (Deep male, authoritative)" },
        { value: "nova", label: "Nova (Female, warm)" },
        { value: "shimmer", label: "Shimmer (Female, bright)" },
      ];
    }
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

  return (
    <Paper
      elevation={3}
      sx={{
        width: 340,
        height: "100%",
        display: "flex",
        flexDirection: "column",
        bgcolor: "background.paper",
      }}
    >
      {/* Header */}
      <Box
        sx={{
          p: 1.5,
          background: "linear-gradient(135deg, #d4af37 0%, #8b0000 100%)",
          color: "white",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        <Typography variant="subtitle1" fontWeight={600}>
          ⚙️ Settings
        </Typography>
      </Box>

      {/* Tabs */}
      <Tabs
        value={activeTab}
        onChange={(e, newValue) => setActiveTab(newValue)}
        variant="scrollable"
        scrollButtons="auto"
        sx={{
          borderBottom: 1,
          borderColor: "divider",
          minHeight: 48,
          "& .MuiTab-root": { minHeight: 48, fontSize: "0.75rem" },
        }}
      >
        <Tab icon={<AIIcon fontSize="small" />} label="AI" />
        <Tab icon={<RAGIcon fontSize="small" />} label="RAG" />
        <Tab icon={<VolumeUpIcon fontSize="small" />} label="Voice" />
        <Tab icon={<ImageIcon fontSize="small" />} label="Images" />
        <Tab icon={<CampaignIcon fontSize="small" />} label="Campaign" />
      </Tabs>

      {/* AI Settings Tab */}
      <TabPanel value={activeTab} index={0}>
        <Stack spacing={2.5}>
          <Typography variant="h6" color="primary">
            AI Model
          </Typography>

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

          <FormControlLabel
            control={
              <Checkbox
                checked={dmRollForPlayers}
                onChange={(e) => setDmRollForPlayers(e.target.checked)}
                color="primary"
                size="small"
              />
            }
            label={
              <Tooltip title="When enabled, the DM can optionally roll dice on behalf of players; rolls will be shown in chat as performed by the DM">
                <span>Allow DM to roll for players</span>
              </Tooltip>
            }
            sx={{ mt: 1 }}
          />
        </Stack>
      </TabPanel>

      {/* RAG Settings Tab */}
      <TabPanel value={activeTab} index={1}>
        {selectedSession ? (
          <Stack spacing={2.5}>
            <Typography variant="h6" color="secondary">
              RAG Context
            </Typography>

            <FormControlLabel
              control={
                <Checkbox
                  checked={!!selectedSession.include_context}
                  onChange={(e) =>
                    updateSessionSettings({ include_context: e.target.checked })
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
                  updateSessionSettings({ top_k: Number(e.target.value || 1) })
                }
                InputProps={{ inputProps: { min: 1, max: 20 } }}
              />
            </Tooltip>

            <Typography variant="body2" color="text.secondary">
              RAG (Retrieval-Augmented Generation) pulls relevant D&D 5e rules
              and content from the Player's Handbook to enhance DM responses
            </Typography>
          </Stack>
        ) : (
          <Typography variant="body2" color="text.secondary">
            Select a session to configure RAG settings
          </Typography>
        )}
      </TabPanel>

      {/* TTS Settings Tab */}
      <TabPanel value={activeTab} index={2}>
        <Stack spacing={2.5}>
          <Typography variant="h6" color="primary">
            Voice Narration
          </Typography>

          <FormControlLabel
            control={
              <Checkbox
                checked={ttsEnabled}
                onChange={(e) => setTtsEnabled(e.target.checked)}
                color="primary"
              />
            }
            label={
              <Typography variant="body2">Enable Voice Narration</Typography>
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
              <Typography variant="body2">Auto-play DM Responses</Typography>
            }
          />

          {ttsEnabled && (
            <>
              <Box>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  TTS Provider
                </Typography>
                <Stack direction="row" spacing={1}>
                  <Chip
                    label="KittenTTS"
                    color={ttsProvider === "kitten" ? "primary" : "default"}
                    onClick={() => handleProviderChange("kitten")}
                    variant={ttsProvider === "kitten" ? "filled" : "outlined"}
                  />
                  <Chip
                    label="OpenAI"
                    color={ttsProvider === "openai" ? "primary" : "default"}
                    onClick={() => handleProviderChange("openai")}
                    variant={ttsProvider === "openai" ? "filled" : "outlined"}
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
            </>
          )}

          <Typography variant="body2" color="text.secondary">
            Text-to-speech converts DM messages into spoken narration for
            immersive gameplay
          </Typography>
        </Stack>
      </TabPanel>

      {/* Scene Images Tab */}
      <TabPanel value={activeTab} index={3}>
        <Stack spacing={2.5}>
          <Typography variant="h6" color="primary">
            Scene Images
          </Typography>

          <FormControlLabel
            control={
              <Checkbox
                checked={sceneImageAutoGenerate}
                onChange={(e) => setSceneImageAutoGenerate(e.target.checked)}
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
            Automatically generates fantasy artwork for DM messages using Stable
            Diffusion. Creates immersive visual scenes based on the narrative
            description.
          </Typography>
        </Stack>
      </TabPanel>

      {/* Campaign Management Tab */}
      <TabPanel value={activeTab} index={4}>
        <Stack spacing={2.5}>
          <Typography variant="h6" color="primary">
            Campaign Selection
          </Typography>

          {/* Show all campaigns */}
          <Box sx={{ display: "flex", alignItems: "flex-start", gap: 1 }}>
            <FormControl fullWidth size="small">
              <InputLabel>Active Campaign</InputLabel>
              <Select
                value={activeCampaign?.id || ""}
                label="Active Campaign"
                onChange={(e) => {
                  const selectedCampaign = campaigns.find(
                    (c) => c.id === e.target.value
                  );
                  if (selectedCampaign && onCampaignSelect) {
                    onCampaignSelect(selectedCampaign);
                  }
                }}
                disabled={loadingCampaigns}
              >
                <MenuItem value="">
                  <em>None</em>
                </MenuItem>
                {campaigns.map((campaign) => (
                  <MenuItem key={campaign.id} value={campaign.id}>
                    {campaign.title || `Campaign ${campaign.id}`}
                    {!selectedSession && campaign.chat_session_id && (
                      <Typography
                        component="span"
                        variant="caption"
                        color="text.secondary"
                        sx={{ ml: 1 }}
                      >
                        (Session {campaign.chat_session_id})
                      </Typography>
                    )}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            {activeCampaign && (
              <Tooltip title="Delete this campaign">
                <IconButton
                  size="small"
                  color="error"
                  onClick={(e) => handleDeleteCampaign(activeCampaign, e)}
                  sx={{ mt: 0.5 }}
                >
                  <DeleteIcon fontSize="small" />
                </IconButton>
              </Tooltip>
            )}
            {/* Bulk actions toggle */}
            <Tooltip title="Bulk select campaigns for deletion">
              <IconButton
                size="small"
                color={bulkMode ? "primary" : "default"}
                onClick={() => setBulkMode((v) => !v)}
                sx={{ mt: 0.5 }}
              >
                {/* reuse DeleteIcon for simplicity */}
                <DeleteIcon fontSize="small" />
              </IconButton>
            </Tooltip>
          </Box>

          {/* Info box */}
          {!selectedSession && campaigns.length > 0 && (
            <Box
              sx={{
                p: 1.5,
                bgcolor: "info.main",
                color: "info.contrastText",
                borderRadius: 1,
              }}
            >
              <Typography variant="body2" fontWeight={600} gutterBottom>
                💡 Showing all {campaigns.length} campaigns
              </Typography>
              <Typography variant="caption">
                Select a campaign to continue playing. The associated chat
                session will be loaded automatically.
              </Typography>
            </Box>
          )}

          {/* Debug Info */}
          <Box
            sx={{
              p: 1,
              bgcolor: "action.hover",
              borderRadius: 1,
              fontSize: "0.75rem",
            }}
          >
            <Typography variant="caption" display="block">
              {selectedSession
                ? `Session: ${selectedSession.id} (${
                    selectedSession.title || "Untitled"
                  })`
                : "No session selected - showing all campaigns"}
            </Typography>
            <Typography variant="caption" display="block">
              Campaigns loaded: {campaigns.length}
            </Typography>
            <Typography variant="caption" display="block">
              Loading: {loadingCampaigns ? "Yes" : "No"}
            </Typography>
          </Box>

          {/* Create New Campaign Button */}
          <Box>
            <Tooltip
              title={
                selectedSession
                  ? "Create a new campaign for this session"
                  : "Create a session first, then create a campaign"
              }
            >
              <Box
                component="span"
                onClick={() =>
                  selectedSession && onCreateCampaign && onCreateCampaign()
                }
                sx={{
                  display: "inline-flex",
                  alignItems: "center",
                  gap: 1,
                  cursor: selectedSession ? "pointer" : "not-allowed",
                  color: selectedSession ? "primary.main" : "text.disabled",
                  fontSize: "0.875rem",
                  fontWeight: 600,
                  textDecoration: "none",
                  transition: "all 0.2s",
                  "&:hover": selectedSession
                    ? {
                        color: "primary.dark",
                        textDecoration: "underline",
                      }
                    : {},
                }}
              >
                <CampaignIcon fontSize="small" />
                <Typography variant="body2" fontWeight={600}>
                  Create New Campaign
                </Typography>
              </Box>
            </Tooltip>
          </Box>

          {loadingCampaigns && (
            <Typography variant="caption" color="text.secondary">
              Loading campaigns...
            </Typography>
          )}

          {/* Bulk selection list */}
          {bulkMode && campaigns.length > 0 && (
            <Box sx={{ mt: 2 }}>
              <Typography variant="subtitle2">Bulk Select</Typography>
              <Stack
                spacing={1}
                sx={{ maxHeight: 220, overflow: "auto", p: 1 }}
              >
                {campaigns.map((c) => (
                  <Box
                    key={`bulk-${c.id}`}
                    sx={{ display: "flex", alignItems: "center", gap: 1 }}
                  >
                    <Checkbox
                      checked={selectedBulk.includes(c.id)}
                      onChange={(e) => {
                        if (e.target.checked) {
                          setSelectedBulk((prev) => [...prev, c.id]);
                        } else {
                          setSelectedBulk((prev) =>
                            prev.filter((id) => id !== c.id)
                          );
                        }
                      }}
                    />
                    <Typography variant="body2">
                      {c.title || `Campaign ${c.id}`}
                    </Typography>
                    <Typography
                      variant="caption"
                      color="text.secondary"
                      sx={{ ml: 1 }}
                    >
                      {c.chat_session_id
                        ? `(Session ${c.chat_session_id})`
                        : ""}
                    </Typography>
                  </Box>
                ))}
              </Stack>

              <Box sx={{ display: "flex", gap: 1, mt: 1 }}>
                <Button
                  variant="outlined"
                  color="error"
                  onClick={() => setBulkDeleteDialogOpen(true)}
                  disabled={selectedBulk.length === 0}
                >
                  Delete Selected ({selectedBulk.length})
                </Button>
                <Button
                  variant="text"
                  onClick={() => {
                    setSelectedBulk([]);
                    setBulkMode(false);
                  }}
                >
                  Cancel
                </Button>
              </Box>
            </Box>
          )}

          {!loadingCampaigns && campaigns.length === 0 && (
            <Box
              sx={{
                p: 2,
                bgcolor: "warning.light",
                borderRadius: 1,
                textAlign: "center",
              }}
            >
              <Typography variant="body2" color="warning.dark" fontWeight={600}>
                No campaigns found
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Create a session from the welcome screen, then create a campaign
                to start your adventure!
              </Typography>
            </Box>
          )}

          <Divider sx={{ my: 2 }} />

          {/* Active Campaign Details */}
          {activeCampaign && (
            <>
              <Typography variant="h6" color="primary">
                Campaign Management
              </Typography>
              <CampaignManager
                campaignId={activeCampaign.id}
                onCampaignUpdate={handleCampaignUpdate}
              />
            </>
          )}

          {!activeCampaign && selectedSession && (
            <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
              Select or create a campaign to see management options
            </Typography>
          )}
        </Stack>
      </TabPanel>

      {/* Delete Confirmation Dialog */}
      <Dialog
        open={deleteDialogOpen}
        onClose={() => setDeleteDialogOpen(false)}
        aria-labelledby="delete-campaign-dialog-title"
      >
        <DialogTitle id="delete-campaign-dialog-title">
          Delete Campaign?
        </DialogTitle>
        <DialogContent>
          <DialogContentText>
            Are you sure you want to delete the campaign "
            <strong>{campaignToDelete?.title}</strong>"? This action cannot be
            undone and will remove all campaign data, including party members
            and game state.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)} color="primary">
            Cancel
          </Button>
          <Button
            onClick={confirmDeleteCampaign}
            color="error"
            variant="contained"
            autoFocus
          >
            Delete Campaign
          </Button>
        </DialogActions>
      </Dialog>
      {/* Bulk Delete Confirmation Dialog */}
      <Dialog
        open={bulkDeleteDialogOpen}
        onClose={() => setBulkDeleteDialogOpen(false)}
        aria-labelledby="bulk-delete-campaign-dialog-title"
      >
        <DialogTitle id="bulk-delete-campaign-dialog-title">
          Delete Selected Campaigns?
        </DialogTitle>
        <DialogContent>
          <DialogContentText>
            Are you sure you want to delete the {selectedBulk.length} selected
            campaign(s)? This action cannot be undone and will remove all
            campaign data, including party members and game state.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button
            onClick={() => setBulkDeleteDialogOpen(false)}
            color="primary"
          >
            Cancel
          </Button>
          <Button
            onClick={confirmBulkDelete}
            color="error"
            variant="contained"
            autoFocus
          >
            Delete Selected
          </Button>
        </DialogActions>
      </Dialog>
    </Paper>
  );
}
