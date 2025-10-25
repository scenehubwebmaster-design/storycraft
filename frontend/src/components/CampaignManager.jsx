import React, { useState, useEffect } from "react";
import {
  Box,
  Paper,
  Typography,
  Button,
  LinearProgress,
  Chip,
  IconButton,
  Tooltip,
  Stack,
  Divider,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Card,
  CardContent,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  FormControlLabel,
  Checkbox,
  Radio,
  RadioGroup,
  FormLabel,
} from "@mui/material";
import {
  Campaign as CampaignIcon,
  TrendingUp as XpIcon,
  Star as LevelUpIcon,
  Settings as SettingsIcon,
  Info as InfoIcon,
  Edit as EditIcon,
  History as HistoryIcon,
  VolumeUp as VoiceIcon,
  RecordVoiceOver as TTSIcon,
} from "@mui/icons-material";
import CheckpointManager from "./CheckpointManager";
import { API_URL } from "../config/api";

/**
 * CampaignManager - Display and manage active campaign
 * Shows: Campaign info, party XP, level progression, scene type
 */
const CampaignManager = ({ campaignId, onCampaignUpdate }) => {
  const [campaign, setCampaign] = useState(null);
  const [loading, setLoading] = useState(true);
  const [xpDialogOpen, setXpDialogOpen] = useState(false);
  const [xpAmount, setXpAmount] = useState("");
  const [xpReason, setXpReason] = useState("");
  const [metadataOpen, setMetadataOpen] = useState(false);

  // TTS Settings (loaded from database)
  const [ttsSettingsOpen, setTtsSettingsOpen] = useState(false);
  const [ttsProvider, setTtsProvider] = useState("kitten");
  const [ttsVoice, setTtsVoice] = useState("tara");
  const [ttsEnabled, setTtsEnabled] = useState(true);
  const [ttsAutoPlay, setTtsAutoPlay] = useState(false);
  const [settingsLoaded, setSettingsLoaded] = useState(false);

  // XP thresholds for each level (D&D 5e)
  const XP_THRESHOLDS = {
    1: 0,
    2: 300,
    3: 900,
    4: 2700,
    5: 6500,
    6: 14000,
    7: 23000,
    8: 34000,
    9: 48000,
    10: 64000,
    11: 85000,
    12: 100000,
    13: 120000,
    14: 140000,
    15: 165000,
    16: 195000,
    17: 225000,
    18: 265000,
    19: 305000,
    20: 355000,
  };

  // Load campaign
  useEffect(() => {
    loadCampaign();

    // Poll every 10 seconds for updates
    const interval = setInterval(loadCampaign, 10000);
    return () => clearInterval(interval);
  }, [campaignId]);

  // Load user settings from database
  useEffect(() => {
    loadUserSettings();
  }, []);

  const loadUserSettings = async () => {
    try {
      const response = await fetch(`${API_URL}/api/settings/`);
      if (response.ok) {
        const settings = await response.json();
        setTtsProvider(settings.tts_provider || "kitten");
        setTtsVoice(settings.tts_voice || "tara");
        setTtsEnabled(settings.tts_enabled ?? true);
        setTtsAutoPlay(settings.tts_auto_play ?? false);
        setSettingsLoaded(true);
      }
    } catch (error) {
      console.error("Error loading settings:", error);
      // Use defaults on error
      setSettingsLoaded(true);
    }
  };

  const loadCampaign = async () => {
    if (!campaignId) return;

    try {
      const response = await fetch(`${API_URL}/api/campaigns/${campaignId}`);
      if (response.ok) {
        const data = await response.json();
        setCampaign(data);
      }
    } catch (error) {
      console.error("Error loading campaign:", error);
    } finally {
      setLoading(false);
    }
  };

  // Award XP to party
  const awardXP = async () => {
    if (!xpAmount || isNaN(xpAmount)) return;

    const xp = parseInt(xpAmount);
    const currentNotes = campaign.session_notes || [];

    // Add XP entry to session notes
    const newNote = {
      type: "xp_award",
      amount: xp,
      reason: xpReason || "XP awarded",
      timestamp: new Date().toISOString(),
    };

    const updatedNotes = [...currentNotes, newNote];

    try {
      // Calculate new total XP
      const totalXpAwarded = updatedNotes
        .filter((n) => n.type === "xp_award")
        .reduce((sum, n) => sum + (n.amount || 0), 0);

      // Determine if level up occurs
      const currentLevel = campaign.current_level;
      let newLevel = currentLevel;

      // Check if XP threshold reached
      for (let level = currentLevel; level < 20; level++) {
        if (totalXpAwarded >= XP_THRESHOLDS[level + 1]) {
          newLevel = level + 1;
        } else {
          break;
        }
      }

      // Update campaign
      const response = await fetch(`${API_URL}/api/campaigns/${campaignId}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          session_notes: updatedNotes,
          current_level: newLevel,
        }),
      });

      if (response.ok) {
        const updated = await response.json();
        setCampaign(updated);
        setXpDialogOpen(false);
        setXpAmount("");
        setXpReason("");

        // Notify parent
        onCampaignUpdate && onCampaignUpdate(updated);
      }
    } catch (error) {
      console.error("Error awarding XP:", error);
    }
  };

  // Get XP progress for current level
  const getXpProgress = () => {
    if (!campaign) return { current: 0, needed: 300, percentage: 0 };

    const currentLevel = campaign.current_level;
    const notes = campaign.session_notes || [];

    const totalXp = notes
      .filter((n) => n.type === "xp_award")
      .reduce((sum, n) => sum + (n.amount || 0), 0);

    const currentThreshold = XP_THRESHOLDS[currentLevel];
    const nextThreshold = XP_THRESHOLDS[currentLevel + 1] || XP_THRESHOLDS[20];

    const xpIntoLevel = totalXp - currentThreshold;
    const xpNeeded = nextThreshold - currentThreshold;
    const percentage = (xpIntoLevel / xpNeeded) * 100;

    return {
      current: xpIntoLevel,
      needed: xpNeeded,
      total: totalXp,
      percentage: Math.min(100, Math.max(0, percentage)),
    };
  };

  // Helpers for metadata parsing + copy
  const copyMetadataToClipboard = async (text) => {
    if (!text) return;
    if (navigator.clipboard && navigator.clipboard.writeText) {
      try {
        await navigator.clipboard.writeText(text);
        return true;
      } catch (e) {
        // fallthrough to textarea fallback
      }
    }

    // Fallback: create a temporary textarea
    try {
      const ta = document.createElement("textarea");
      ta.value = text;
      document.body.appendChild(ta);
      ta.select();
      document.execCommand("copy");
      document.body.removeChild(ta);
      return true;
    } catch (e) {
      console.error("Copy to clipboard failed", e);
      return false;
    }
  };

  // Get scene type badge color
  const getSceneColor = (sceneType) => {
    switch (sceneType) {
      case "combat":
        return "error";
      case "exploration":
        return "info";
      case "roleplay":
        return "success";
      case "rest":
        return "default";
      case "shop":
        return "warning";
      default:
        return "default";
    }
  };

  // Get scene type icon
  const getSceneIcon = (sceneType) => {
    switch (sceneType) {
      case "combat":
        return "⚔️";
      case "exploration":
        return "🗺️";
      case "roleplay":
        return "💬";
      case "rest":
        return "🔥";
      case "shop":
        return "💰";
      default:
        return "📖";
    }
  };

  // Save TTS settings to database
  const saveTtsSettings = async () => {
    try {
      const response = await fetch(`${API_URL}/api/settings/`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          tts_provider: ttsProvider,
          tts_voice: ttsVoice,
          tts_enabled: ttsEnabled,
          tts_auto_play: ttsAutoPlay,
        }),
      });

      if (response.ok) {
        setTtsSettingsOpen(false);
        // Settings saved successfully
      } else {
        console.error("Failed to save settings");
      }
    } catch (error) {
      console.error("Error saving settings:", error);
    }
  };

  // Get voice options based on provider
  const getVoiceOptions = () => {
    if (ttsProvider === "openai") {
      return [
        { value: "alloy", label: "Alloy (Neutral, Balanced)" },
        { value: "echo", label: "Echo (Male, Clear)" },
        { value: "fable", label: "Fable (British, Expressive)" },
        { value: "onyx", label: "Onyx (Deep Male, Authoritative)" },
        { value: "nova", label: "Nova (Female, Warm)" },
        { value: "shimmer", label: "Shimmer (Female, Bright)" },
      ];
    } else {
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
    }
  };

  // Handle provider change - reset to default voice for that provider
  const handleProviderChange = (newProvider) => {
    setTtsProvider(newProvider);
    // Set default voice for the provider
    if (newProvider === "openai") {
      setTtsVoice("alloy");
    } else {
      setTtsVoice("tara");
    }
  };

  if (loading) {
    return (
      <Paper sx={{ p: 2 }}>
        <Typography>Loading campaign...</Typography>
      </Paper>
    );
  }

  if (!campaign) {
    return (
      <Paper sx={{ p: 2 }}>
        <Alert severity="info">
          No active campaign. Create a campaign to start your adventure!
        </Alert>
      </Paper>
    );
  }

  const xpProgress = getXpProgress();

  return (
    <Paper sx={{ p: 2 }}>
      <Box
        sx={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "flex-start",
          mb: 2,
        }}
      >
        <Box>
          <Typography
            variant="h6"
            sx={{ display: "flex", alignItems: "center", gap: 1 }}
          >
            <CampaignIcon />
            {campaign.title}
          </Typography>
          {campaign.description && (
            <Box sx={{ mt: 0.5 }}>
              <Typography
                variant="body2"
                color="text.secondary"
                sx={{
                  // Show a short summary paragraph by default
                  wordBreak: "break-word",
                  overflowWrap: "anywhere",
                  whiteSpace: "pre-wrap",
                }}
              >
                {campaign.description.split(/\n\n|\r\n\r\n/)[0]}
              </Typography>

              {/* Extract AI_DM_METADATA JSON if present and show collapsed */}
              {(() => {
                const m = campaign.description.match(
                  /\[AI_DM_METADATA:\s*(\{[\s\S]*?\})\]/
                );
                if (!m) return null;

                let parsed = null;
                let metadataString = m[1];
                try {
                  parsed = JSON.parse(metadataString);
                  metadataString = JSON.stringify(parsed, null, 2);
                } catch (e) {
                  // keep raw string
                }

                return (
                  <Box sx={{ mt: 1 }}>
                    <Stack direction="row" spacing={1} alignItems="center">
                      <Button
                        size="small"
                        variant="outlined"
                        startIcon={<InfoIcon />}
                        onClick={() => setMetadataOpen((s) => !s)}
                      >
                        {metadataOpen ? "Hide Metadata" : "Show Metadata"}
                      </Button>
                      <Button
                        size="small"
                        onClick={() => copyMetadataToClipboard(metadataString)}
                      >
                        Copy Metadata
                      </Button>
                    </Stack>

                    {metadataOpen && (
                      <Paper
                        sx={{
                          p: 1,
                          mt: 1,
                          bgcolor: "rgba(0,0,0,0.04)",
                          fontFamily: "monospace",
                          fontSize: "0.85rem",
                          whiteSpace: "pre-wrap",
                          wordBreak: "break-all",
                        }}
                      >
                        <Box component="pre" sx={{ m: 0 }}>
                          {metadataString}
                        </Box>
                      </Paper>
                    )}
                  </Box>
                );
              })()}
            </Box>
          )}
        </Box>
        <IconButton size="small">
          <SettingsIcon fontSize="small" />
        </IconButton>
      </Box>

      <Stack spacing={2}>
        {/* Campaign Info */}
        <Box sx={{ display: "flex", gap: 1, flexWrap: "wrap" }}>
          <Chip
            label={`Level ${campaign.current_level}`}
            icon={<LevelUpIcon />}
            color="primary"
            size="small"
          />
          <Chip
            label={`${getSceneIcon(campaign.current_scene_type)} ${
              campaign.current_scene_type?.toUpperCase() || "ROLEPLAY"
            }`}
            color={getSceneColor(campaign.current_scene_type)}
            size="small"
          />
          {campaign.setting && (
            <Chip label={campaign.setting} size="small" variant="outlined" />
          )}
          {campaign.difficulty && (
            <Chip label={campaign.difficulty} size="small" variant="outlined" />
          )}
        </Box>

        <Divider />

        {/* XP Progress */}
        <Box>
          <Box
            sx={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              mb: 1,
            }}
          >
            <Typography
              variant="subtitle2"
              sx={{ display: "flex", alignItems: "center", gap: 0.5 }}
            >
              <XpIcon fontSize="small" />
              Experience Points
            </Typography>
            <Button
              size="small"
              variant="outlined"
              onClick={() => setXpDialogOpen(true)}
            >
              Award XP
            </Button>
          </Box>

          <Box sx={{ mb: 0.5 }}>
            <Typography variant="body2" color="text.secondary">
              {xpProgress.current.toLocaleString()} /{" "}
              {xpProgress.needed.toLocaleString()} XP
              {campaign.current_level < 20
                ? ` to Level ${campaign.current_level + 1}`
                : " (Max Level)"}
            </Typography>
          </Box>

          <LinearProgress
            variant="determinate"
            value={xpProgress.percentage}
            color="primary"
            sx={{ height: 8, borderRadius: 1 }}
          />

          <Typography
            variant="caption"
            color="text.secondary"
            sx={{ mt: 0.5, display: "block" }}
          >
            Total XP: {xpProgress.total.toLocaleString()}
          </Typography>
        </Box>

        <Divider />

        {/* Party Status */}
        <Box>
          <Typography variant="subtitle2" gutterBottom>
            Party ({campaign.party?.length || 0})
          </Typography>
          {campaign.party && campaign.party.length > 0 ? (
            <Stack spacing={0.5}>
              {campaign.party.map((member) => (
                <Box
                  key={member.character_id}
                  sx={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                    p: 1,
                    bgcolor: "action.hover",
                    borderRadius: 1,
                  }}
                >
                  <Typography variant="body2">{member.name}</Typography>
                  <Box sx={{ display: "flex", gap: 1 }}>
                    <Chip
                      label={`${member.current_hp}/${member.max_hp} HP`}
                      size="small"
                      color={
                        member.current_hp > member.max_hp * 0.5
                          ? "success"
                          : "error"
                      }
                    />
                  </Box>
                </Box>
              ))}
            </Stack>
          ) : (
            <Typography variant="body2" color="text.secondary">
              No party members
            </Typography>
          )}
        </Box>

        {/* Current Location */}
        {campaign.current_location && (
          <>
            <Divider />
            <Box>
              <Typography variant="subtitle2" gutterBottom>
                Current Location
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {campaign.current_location}
              </Typography>
            </Box>
          </>
        )}

        {/* Campaign Checkpoints */}
        <Divider />
        <Box>
          <Box
            sx={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              mb: 1,
            }}
          >
            <Typography
              variant="subtitle2"
              sx={{ display: "flex", alignItems: "center", gap: 0.5 }}
            >
              <HistoryIcon fontSize="small" />
              Save Progress
            </Typography>
          </Box>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Create checkpoints to save your campaign progress and restore later
          </Typography>
          <CheckpointManager
            campaignId={campaign.id}
            onRestoreComplete={(restoredCampaign) => {
              setCampaign(restoredCampaign);
              onCampaignUpdate && onCampaignUpdate(restoredCampaign);
            }}
          />
        </Box>

        {/* Voice Narration Settings */}
        <Divider />
        <Box>
          <Box
            sx={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              mb: 1,
            }}
          >
            <Typography
              variant="subtitle2"
              sx={{ display: "flex", alignItems: "center", gap: 0.5 }}
            >
              <VoiceIcon fontSize="small" />
              Voice Narration (TTS)
            </Typography>
            <Button
              size="small"
              variant="outlined"
              startIcon={<SettingsIcon />}
              onClick={() => setTtsSettingsOpen(true)}
            >
              Configure
            </Button>
          </Box>
          <Stack spacing={1}>
            <Box sx={{ display: "flex", gap: 1, flexWrap: "wrap" }}>
              <Chip
                icon={<TTSIcon />}
                label={`Provider: ${
                  ttsProvider === "openai" ? "OpenAI Whisper" : "KittenTTS"
                }`}
                size="small"
                color={ttsEnabled ? "primary" : "default"}
                variant={ttsEnabled ? "filled" : "outlined"}
              />
              <Chip
                label={`Voice: ${ttsVoice}`}
                size="small"
                variant="outlined"
              />
              <Chip
                label={ttsEnabled ? "Enabled" : "Disabled"}
                size="small"
                color={ttsEnabled ? "success" : "default"}
              />
              <Chip
                label={ttsAutoPlay ? "Auto-play" : "Manual"}
                size="small"
                variant="outlined"
              />
            </Box>
            <Typography variant="caption" color="text.secondary">
              Choose between KittenTTS (local, free) or OpenAI Whisper (cloud,
              high-quality)
            </Typography>
          </Stack>
        </Box>
      </Stack>

      {/* TTS Settings Dialog */}
      <Dialog
        open={ttsSettingsOpen}
        onClose={() => setTtsSettingsOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>
          <Stack direction="row" spacing={1} alignItems="center">
            <VoiceIcon />
            <Typography variant="h6">Voice Narration Settings</Typography>
          </Stack>
        </DialogTitle>
        <DialogContent>
          <Stack spacing={3} sx={{ mt: 1 }}>
            {/* Enable TTS */}
            <FormControlLabel
              control={
                <Checkbox
                  checked={ttsEnabled}
                  onChange={(e) => setTtsEnabled(e.target.checked)}
                />
              }
              label="Enable Voice Narration"
            />

            {/* Auto-play */}
            <FormControlLabel
              control={
                <Checkbox
                  checked={ttsAutoPlay}
                  onChange={(e) => setTtsAutoPlay(e.target.checked)}
                  disabled={!ttsEnabled}
                />
              }
              label="Auto-play DM Responses"
            />

            <Divider />

            {/* Provider Selection */}
            <FormControl component="fieldset" disabled={!ttsEnabled}>
              <FormLabel component="legend">TTS Provider</FormLabel>
              <RadioGroup
                value={ttsProvider}
                onChange={(e) => handleProviderChange(e.target.value)}
              >
                <FormControlLabel
                  value="kitten"
                  control={<Radio />}
                  label={
                    <Stack>
                      <Typography variant="body2" fontWeight={600}>
                        KittenTTS (Local)
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        Free • CPU-optimized • No API key required • 8 voices
                      </Typography>
                    </Stack>
                  }
                />
                <FormControlLabel
                  value="openai"
                  control={<Radio />}
                  label={
                    <Stack>
                      <Typography variant="body2" fontWeight={600}>
                        OpenAI Whisper (Cloud)
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        Premium quality • Requires API key • 6 professional
                        voices • $15/1M characters
                      </Typography>
                    </Stack>
                  }
                />
              </RadioGroup>
            </FormControl>

            <Divider />

            {/* Voice Selection */}
            <FormControl fullWidth disabled={!ttsEnabled}>
              <InputLabel>Voice Character</InputLabel>
              <Select
                value={ttsVoice}
                label="Voice Character"
                onChange={(e) => setTtsVoice(e.target.value)}
              >
                {getVoiceOptions().map((voice) => (
                  <MenuItem key={voice.value} value={voice.value}>
                    {voice.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            {/* Info Alert */}
            <Alert severity="info" icon={<InfoIcon />}>
              {ttsProvider === "openai" ? (
                <>
                  <Typography variant="body2" fontWeight={600} gutterBottom>
                    OpenAI Whisper TTS
                  </Typography>
                  <Typography variant="caption">
                    Uses OpenAI's professional text-to-speech API. Requires an
                    OpenAI API key configured in your backend .env file. Offers
                    high-quality neural voices with natural intonation and
                    emotion.
                  </Typography>
                </>
              ) : (
                <>
                  <Typography variant="body2" fontWeight={600} gutterBottom>
                    KittenTTS
                  </Typography>
                  <Typography variant="caption">
                    Ultra-lightweight local TTS (under 25MB). Runs on CPU with
                    no GPU required. Perfect for offline use and
                    privacy-conscious users. No external API calls.
                  </Typography>
                </>
              )}
            </Alert>
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setTtsSettingsOpen(false)}>Cancel</Button>
          <Button onClick={saveTtsSettings} variant="contained">
            Save Settings
          </Button>
        </DialogActions>
      </Dialog>

      {/* XP Award Dialog */}
      <Dialog
        open={xpDialogOpen}
        onClose={() => setXpDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Award Experience Points</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            <TextField
              label="XP Amount"
              type="number"
              value={xpAmount}
              onChange={(e) => setXpAmount(e.target.value)}
              fullWidth
              placeholder="e.g., 200"
              inputProps={{ min: 0 }}
            />

            <TextField
              label="Reason (optional)"
              value={xpReason}
              onChange={(e) => setXpReason(e.target.value)}
              fullWidth
              placeholder="e.g., Defeated goblin ambush"
            />

            <Alert severity="info" icon={<InfoIcon />}>
              XP will be tracked for the entire party. Level ups occur
              automatically when thresholds are reached.
            </Alert>

            {/* Quick XP Buttons */}
            <Box>
              <Typography variant="caption" color="text.secondary" gutterBottom>
                Quick Awards
              </Typography>
              <Stack direction="row" spacing={1} sx={{ mt: 1 }}>
                <Button
                  size="small"
                  variant="outlined"
                  onClick={() => setXpAmount("50")}
                >
                  Easy (50)
                </Button>
                <Button
                  size="small"
                  variant="outlined"
                  onClick={() => setXpAmount("100")}
                >
                  Medium (100)
                </Button>
                <Button
                  size="small"
                  variant="outlined"
                  onClick={() => setXpAmount("200")}
                >
                  Hard (200)
                </Button>
                <Button
                  size="small"
                  variant="outlined"
                  onClick={() => setXpAmount("400")}
                >
                  Deadly (400)
                </Button>
              </Stack>
            </Box>
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setXpDialogOpen(false)}>Cancel</Button>
          <Button onClick={awardXP} variant="contained" disabled={!xpAmount}>
            Award XP
          </Button>
        </DialogActions>
      </Dialog>
    </Paper>
  );
};

export default CampaignManager;
