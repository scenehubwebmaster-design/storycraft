import React, { useEffect, useState, useRef } from "react";
import {
  Box,
  Button,
  TextField,
  Card,
  CardContent,
  CardActions,
  Typography,
  Divider,
  Alert,
  CircularProgress,
  IconButton,
  Checkbox,
  FormControlLabel,
  MenuItem,
  Select,
  InputLabel,
  FormControl,
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemText,
  ListItemAvatar,
  Avatar,
  Chip,
  Collapse,
  Stack,
  Paper,
  Toolbar,
  AppBar,
  InputAdornment,
  Tooltip,
  Badge,
} from "@mui/material";
import {
  Delete as DeleteIcon,
  Add as AddIcon,
  Send as SendIcon,
  AutoAwesome as AutoAwesomeIcon,
  Person as PersonIcon,
  SmartToy as SmartToyIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  Settings as SettingsIcon,
  MenuBook as MenuBookIcon,
  Chat as ChatIcon,
  ChevronLeft as ChevronLeftIcon,
  ChevronRight as ChevronRightIcon,
  VolumeUp as VolumeUpIcon,
  PlayArrow as PlayArrowIcon,
  RecordVoiceOver as VoiceIcon,
  Stop as StopIcon,
  Campaign as CampaignIcon,
} from "@mui/icons-material";
import { darkTheme } from "../theme/darkTheme";
import ReactMarkdown from "react-markdown";
import TTSAudioPlayer from "../components/game/TTSAudioPlayer";
import CampaignSetupWizard from "../components/CampaignSetupWizard";
import CampaignManager from "../components/CampaignManager";
import PartyPanel from "../components/PartyPanel";
import InitiativeTracker from "../components/InitiativeTracker";
import DiceRoller from "../components/DiceRoller";
import CombatActionPanel from "../components/CombatActionPanel";

const drawerWidth = 320;

export default function DMChatPage() {
  const [sessions, setSessions] = useState([]);
  const [selectedSession, setSelectedSession] = useState(null);
  const [loadingSessions, setLoadingSessions] = useState(false);
  const [creating, setCreating] = useState(false);
  const [title, setTitle] = useState("");
  const [message, setMessage] = useState("");
  const [sending, setSending] = useState(false);
  const [messages, setMessages] = useState([]);
  const [provider, setProvider] = useState("groq");
  const [model, setModel] = useState("");
  const [availableModels, setAvailableModels] = useState([]);
  const [k, setK] = useState(5);
  const [loadingGen, setLoadingGen] = useState(false);
  const [error, setError] = useState(null);
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [drawerOpen, setDrawerOpen] = useState(true);
  const [ttsEnabled, setTtsEnabled] = useState(true);
  const [ttsAutoPlay, setTtsAutoPlay] = useState(false);
  const [ttsVoice, setTtsVoice] = useState("tara");
  const [ttsFlavorTextOnly, setTtsFlavorTextOnly] = useState(false);
  const bottomRef = useRef(null);

  // Campaign & Combat State
  const [campaignWizardOpen, setCampaignWizardOpen] = useState(false);
  const [activeCampaign, setActiveCampaign] = useState(null);
  const [combatMode, setCombatMode] = useState(false);
  const [diceRollerOpen, setDiceRollerOpen] = useState(false);
  const [rightPanelView, setRightPanelView] = useState("party"); // 'party', 'initiative', 'combat'

  useEffect(() => {
    fetchSessions();
  }, []);

  // fetch provider models when provider changes
  useEffect(() => {
    let mounted = true;
    setAvailableModels([]);
    setModel("");
    const fetchModels = async () => {
      try {
        const r = await fetch(
          `/api/llm/models?provider=${encodeURIComponent(provider)}`
        );
        if (!r.ok) return;
        const data = await r.json();
        if (!mounted) return;
        const list = Array.isArray(data)
          ? data.map((m) =>
              typeof m === "string"
                ? { id: m, name: m }
                : { id: m.id || m.name, name: m.name || m.id }
            )
          : [];
        setAvailableModels(list);
      } catch (e) {
        console.debug("Failed to fetch models", e);
      }
    };
    fetchModels();
    return () => {
      mounted = false;
    };
  }, [provider]);

  useEffect(() => {
    // scroll to bottom on messages change
    if (bottomRef.current)
      bottomRef.current.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const fetchSessions = async () => {
    setLoadingSessions(true);
    try {
      const r = await fetch(`/api/chat/sessions`);
      if (!r.ok) throw new Error(`Failed to load sessions: ${r.status}`);
      const data = await r.json();
      setSessions(data || []);
    } catch (e) {
      console.error(e);
    } finally {
      setLoadingSessions(false);
    }
  };

  const createSession = async () => {
    setCreating(true);
    setError(null);
    try {
      const body = { title: title || undefined, provider, model, top_k: k };
      const r = await fetch(`/api/chat/sessions`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      if (!r.ok) throw new Error(`Create failed: ${r.status}`);
      const s = await r.json();
      setSessions((s0) => [s, ...s0]);
      setTitle("");
      selectSession(s.id);
    } catch (e) {
      console.error(e);
      setError(String(e));
    } finally {
      setCreating(false);
    }
  };

  const selectSession = async (sessionId) => {
    setSelectedSession(null);
    setMessages([]);
    setActiveCampaign(null);
    try {
      const r = await fetch(`/api/chat/sessions/${sessionId}`);
      if (!r.ok) throw new Error(`Failed to load session: ${r.status}`);
      const s = await r.json();
      setSelectedSession(s);
      setMessages(s.messages || []);

      // Load campaign for this session if it exists
      await loadCampaignForSession(sessionId);
    } catch (e) {
      console.error(e);
    }
  };

  const loadCampaignForSession = async (sessionId) => {
    try {
      // Get all campaigns for this chat session
      const r = await fetch(`/api/campaigns/?chat_session_id=${sessionId}`);
      if (!r.ok) {
        console.debug("No campaign found for session:", sessionId);
        return;
      }
      const campaigns = await r.json();
      if (campaigns && campaigns.length > 0) {
        // Load the most recent campaign for this session
        const campaign = campaigns[0];
        console.log("Loaded campaign for session:", campaign);
        setActiveCampaign(campaign);
      }
    } catch (e) {
      console.debug("Failed to load campaign for session:", e);
    }
  };

  const updateSessionSettings = async (updates) => {
    if (!selectedSession) return;
    try {
      const r = await fetch(`/api/chat/sessions/${selectedSession.id}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(updates),
      });
      if (!r.ok) throw new Error(`Update failed: ${r.status}`);
      const s = await r.json();
      setSelectedSession(s);
      // update in sessions list
      setSessions((list) => list.map((x) => (x.id === s.id ? s : x)));
    } catch (e) {
      console.error(e);
      setError(String(e));
    }
  };

  const abortGeneration = () => {
    // Reset loading states to allow user to try again
    setSending(false);
    setLoadingGen(false);
    setError("Generation cancelled by user");
    // Remove any placeholder messages
    setMessages((m) => m.filter((msg) => !msg._optimistic));
  };

  const sendMessage = async () => {
    if (!selectedSession) return;
    if (!message || message.trim().length === 0) return;
    setSending(true);
    setError(null);
    try {
      // persist user message
      const r = await fetch(
        `/api/chat/sessions/${selectedSession.id}/messages`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ role: "user", content: message }),
        }
      );
      if (!r.ok) throw new Error(`Send failed: ${r.status}`);
      const userMsg = await r.json();
      // append user message
      setMessages((m) => [...m, userMsg]);
      setMessage("");

      // optimistic assistant placeholder while server generates
      const placeholderId = `pending-${Date.now()}`;
      const placeholder = {
        id: placeholderId,
        session_id: selectedSession.id,
        role: "assistant",
        content: "Generating...",
        message_index: null,
        metadata: null,
        is_deleted: false,
        created_at: new Date().toISOString(),
        _optimistic: true,
      };
      setMessages((m) => [...m, placeholder]);
      setLoadingGen(true);

      // Ask server to generate an assistant reply for this session (server will handle RAG)
      const genResp = await fetch(
        `/api/chat/sessions/${selectedSession.id}/generate`,
        {
          method: "POST",
        }
      );
      if (!genResp.ok) {
        const txt = await genResp.text();
        throw new Error(`Generate failed: ${genResp.status} ${txt}`);
      }
      const genPayload = await genResp.json();
      const assistantMsg = genPayload?.assistant_message;
      if (assistantMsg) {
        // replace placeholder with real assistant message
        setMessages((m) =>
          m.map((it) => (it.id === placeholderId ? assistantMsg : it))
        );
      } else {
        // remove placeholder if no assistant message
        setMessages((m) => m.filter((it) => it.id !== placeholderId));
      }
    } catch (e) {
      console.error(e);
      setError(String(e));
      // Remove placeholder on error
      setMessages((m) => m.filter((it) => it.id !== placeholderId));
    } finally {
      setSending(false);
      setLoadingGen(false);
    }
  };

  // Server-side generation endpoint is used; no client-side orchestration needed.

  const deleteSession = async (id) => {
    try {
      const r = await fetch(`/api/chat/sessions/${id}`, { method: "DELETE" });
      if (!r.ok) throw new Error(`Delete failed: ${r.status}`);
      setSessions((s) => s.filter((x) => x.id !== id));
      if (selectedSession && selectedSession.id === id) {
        setSelectedSession(null);
        setMessages([]);
        setActiveCampaign(null);
      }
    } catch (e) {
      console.error(e);
    }
  };

  // Campaign handlers
  const handleCampaignCreated = async (campaign) => {
    setActiveCampaign(campaign);
    console.log("Campaign created:", campaign);

    // Automatically initialize the campaign with AI DM
    if (selectedSession && campaign) {
      await initializeCampaignWithAI(campaign);
    }
  };

  const initializeCampaignWithAI = async (campaign) => {
    try {
      // Extract template metadata from campaign description
      const metadataMatch = campaign.description?.match(
        /\[AI_DM_METADATA: ({.*?})\]/
      );
      const metadata = metadataMatch ? JSON.parse(metadataMatch[1]) : {};

      // Fetch campaign party details
      const partyResponse = await fetch(`/api/campaigns/${campaign.id}/party`);
      const party = partyResponse.ok ? await partyResponse.json() : [];

      // Build campaign initialization prompt
      const partyList = party
        .map(
          (char) =>
            `- ${char.name} (${char.dnd_species} ${char.dnd_class}, Level ${char.dnd_level})`
        )
        .join("\n");

      const initPrompt = `🎲 **Campaign Initialized: ${campaign.title}**

**Campaign Details:**
- **Type:** ${campaign.campaign_type?.replace("_", " ").toUpperCase()}
- **Setting:** ${campaign.setting}
- **Difficulty:** ${campaign.difficulty}
- **Starting Level:** ${campaign.starting_level}
- **Adventure Template:** ${metadata.template_id || "Custom"}
- **Opening Scene:** ${
        metadata.opening_scene?.replace("_", " ") || "Classic Start"
      }
- **Campaign Tone:** ${
        metadata.campaign_tone?.replace("_", " ") || "Heroic Fantasy"
      }

**The Adventuring Party:**
${partyList || "(No characters assigned yet)"}

---

**Dungeon Master Instructions:**

You are now running this D&D 5th Edition campaign. Use the adventure template "${
        metadata.template_id || "custom"
      }" and opening scene "${
        metadata.opening_scene || "tavern_meeting"
      }" from the campaign starters in your knowledge base.

**Your responsibilities:**
1. Begin with the selected opening scene narration
2. Follow the adventure template's story structure
3. Adapt the ${metadata.campaign_tone || "heroic_fantasy"} tone throughout
4. Track party progress, HP, conditions, and resources
5. Provide vivid descriptions and engaging NPC dialogue
6. Adjudicate rules fairly using D&D 5e mechanics
7. Ask for dice rolls when needed (attack rolls, saving throws, skill checks)
8. Reference the PHB and other source material via RAG when needed

**Please begin the adventure with the opening scene narration!**`;

      // Send the initialization message
      setSending(true);
      const msgResponse = await fetch(
        `/api/chat/sessions/${selectedSession.id}/messages`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            role: "user",
            content: initPrompt,
          }),
        }
      );

      if (!msgResponse.ok) {
        throw new Error("Failed to send initialization message");
      }

      const userMsg = await msgResponse.json();
      setMessages((m) => [...m, userMsg]);

      // Generate AI DM's opening narration
      const placeholderId = `pending-${Date.now()}`;
      const placeholder = {
        id: placeholderId,
        session_id: selectedSession.id,
        role: "assistant",
        content: "Preparing your adventure...",
        message_index: null,
        metadata: null,
        is_deleted: false,
        created_at: new Date().toISOString(),
        _optimistic: true,
      };
      setMessages((m) => [...m, placeholder]);
      setLoadingGen(true);

      const genResp = await fetch(
        `/api/chat/sessions/${selectedSession.id}/generate`,
        {
          method: "POST",
        }
      );

      if (!genResp.ok) {
        throw new Error(`Generate failed: ${genResp.status}`);
      }

      const genPayload = await genResp.json();
      const assistantMsg = genPayload?.assistant_message;

      if (assistantMsg) {
        setMessages((m) =>
          m.map((it) => (it.id === placeholderId ? assistantMsg : it))
        );
      } else {
        setMessages((m) => m.filter((it) => it.id !== placeholderId));
      }
    } catch (e) {
      console.error("Failed to initialize campaign:", e);
      setError(
        "Campaign created, but failed to initialize with AI DM. You can start manually."
      );
    } finally {
      setSending(false);
      setLoadingGen(false);
    }
  };

  const handleCampaignUpdate = (campaign) => {
    setActiveCampaign(campaign);
  };

  const handleCombatStart = () => {
    setCombatMode(true);
    setRightPanelView("initiative");
  };

  const handleCombatEnd = () => {
    setCombatMode(false);
    setRightPanelView("party");
  };

  const handleDiceRoll = (result) => {
    console.log("Dice roll:", result);
    // Could add dice roll to chat as system message
  };

  return (
    <Box
      sx={{ display: "flex", height: "100vh", bgcolor: "background.default" }}
    >
      {/* Session Drawer */}
      <Drawer
        variant="persistent"
        open={drawerOpen}
        sx={{
          width: drawerWidth,
          flexShrink: 0,
          "& .MuiDrawer-paper": {
            width: drawerWidth,
            boxSizing: "border-box",
            bgcolor: "background.paper",
          },
        }}
      >
        <Toolbar sx={{ bgcolor: "primary.main", color: "white" }}>
          <MenuBookIcon sx={{ mr: 1.5 }} />
          <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1 }}>
            DM Sessions
          </Typography>
          <Tooltip title="Hide sidebar">
            <IconButton
              onClick={() => setDrawerOpen(false)}
              sx={{ color: "white" }}
            >
              <ChevronLeftIcon />
            </IconButton>
          </Tooltip>
        </Toolbar>

        {/* New Session Card */}
        <Box sx={{ p: 2 }}>
          <Card
            elevation={2}
            sx={{ border: "1px solid", borderColor: "secondary.main" }}
          >
            <CardContent sx={{ pb: 1 }}>
              <Stack direction="row" spacing={1} alignItems="center">
                <AddIcon color="secondary" />
                <Typography variant="subtitle2" color="secondary">
                  New Campaign
                </Typography>
              </Stack>
              <TextField
                fullWidth
                size="small"
                placeholder="Enter session title..."
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                sx={{ mt: 1.5 }}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <ChatIcon fontSize="small" />
                    </InputAdornment>
                  ),
                }}
              />
            </CardContent>
            <CardActions sx={{ pt: 0 }}>
              <Button
                fullWidth
                variant="contained"
                color="secondary"
                onClick={createSession}
                disabled={creating}
                startIcon={
                  creating ? <CircularProgress size={16} /> : <AddIcon />
                }
              >
                {creating ? "Creating..." : "Begin Session"}
              </Button>
            </CardActions>
          </Card>

          {/* Active Campaign Status */}
          {activeCampaign && (
            <Alert severity="success" icon={<CampaignIcon />} sx={{ mt: 2 }}>
              <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                🎲 Campaign Active
              </Typography>
              <Typography variant="caption" display="block">
                {activeCampaign.title}
              </Typography>
              <Typography
                variant="caption"
                color="text.secondary"
                display="block"
              >
                Level {activeCampaign.current_level} •{" "}
                {activeCampaign.campaign_type?.replace("_", " ")}
              </Typography>
            </Alert>
          )}

          {/* Campaign Setup Button */}
          <Button
            fullWidth
            variant={activeCampaign ? "outlined" : "contained"}
            color={activeCampaign ? "secondary" : "primary"}
            onClick={() => setCampaignWizardOpen(true)}
            disabled={!selectedSession}
            startIcon={activeCampaign ? <SettingsIcon /> : <MenuBookIcon />}
            sx={{ mt: 2 }}
          >
            {activeCampaign ? "Campaign Settings" : "Setup D&D Campaign"}
          </Button>
        </Box>

        <Divider sx={{ borderColor: "secondary.light" }} />

        {/* Sessions List */}
        <Box sx={{ flexGrow: 1, overflow: "auto", px: 2, py: 1 }}>
          {loadingSessions ? (
            <Box sx={{ display: "flex", justifyContent: "center", py: 4 }}>
              <CircularProgress />
            </Box>
          ) : sessions.length === 0 ? (
            <Box sx={{ textAlign: "center", py: 4, px: 2 }}>
              <Typography variant="body2" color="text.secondary">
                No sessions yet. Create your first campaign above!
              </Typography>
            </Box>
          ) : (
            <List disablePadding>
              {sessions.map((s) => (
                <Card
                  key={s.id}
                  sx={{
                    mb: 1.5,
                    cursor: "pointer",
                    bgcolor:
                      selectedSession?.id === s.id
                        ? "primary.light"
                        : "background.paper",
                    color:
                      selectedSession?.id === s.id ? "white" : "text.primary",
                    transition: "all 0.2s",
                    "&:hover": {
                      transform: "translateY(-2px)",
                      boxShadow: 3,
                    },
                  }}
                  onClick={() => selectSession(s.id)}
                >
                  <CardContent sx={{ pb: 1, "&:last-child": { pb: 1.5 } }}>
                    <Stack
                      direction="row"
                      justifyContent="space-between"
                      alignItems="flex-start"
                    >
                      <Box sx={{ flex: 1 }}>
                        <Typography
                          variant="subtitle2"
                          sx={{ fontWeight: 600, mb: 0.5 }}
                        >
                          {s.title || `Session ${s.id}`}
                        </Typography>
                        <Stack direction="row" spacing={0.5} flexWrap="wrap">
                          <Chip
                            size="small"
                            label={s.provider || "groq"}
                            sx={{
                              height: 20,
                              fontSize: "0.7rem",
                              bgcolor:
                                selectedSession?.id === s.id
                                  ? "rgba(255,255,255,0.2)"
                                  : "primary.light",
                              color:
                                selectedSession?.id === s.id
                                  ? "white"
                                  : "white",
                            }}
                          />
                          <Chip
                            size="small"
                            label={`k=${s.top_k || 5}`}
                            sx={{
                              height: 20,
                              fontSize: "0.7rem",
                              bgcolor:
                                selectedSession?.id === s.id
                                  ? "rgba(255,255,255,0.2)"
                                  : "secondary.light",
                            }}
                          />
                        </Stack>
                      </Box>
                      <Tooltip title="Delete session">
                        <IconButton
                          size="small"
                          onClick={(e) => {
                            e.stopPropagation();
                            deleteSession(s.id);
                          }}
                          sx={{
                            color:
                              selectedSession?.id === s.id
                                ? "white"
                                : "error.main",
                            "&:hover": { bgcolor: "error.light" },
                          }}
                        >
                          <DeleteIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                    </Stack>
                  </CardContent>
                </Card>
              ))}
            </List>
          )}
        </Box>

        {/* Settings Section */}
        <Divider sx={{ borderColor: "secondary.light" }} />
        <Box sx={{ p: 2 }}>
          <ListItemButton
            onClick={() => setSettingsOpen(!settingsOpen)}
            sx={{
              borderRadius: 1,
              border: "1px solid",
              borderColor: "divider",
              mb: 1,
            }}
          >
            <ListItemAvatar>
              <Avatar sx={{ bgcolor: "secondary.main" }}>
                <SettingsIcon />
              </Avatar>
            </ListItemAvatar>
            <ListItemText
              primary="AI Settings"
              secondary={`${provider} • ${model || "default"}`}
            />
            {settingsOpen ? <ExpandLessIcon /> : <ExpandMoreIcon />}
          </ListItemButton>

          <Collapse in={settingsOpen}>
            <Card sx={{ p: 2 }}>
              <Stack spacing={2}>
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

                <Tooltip title="Number of D&D references to retrieve">
                  <TextField
                    fullWidth
                    size="small"
                    label="Retrieval Count (k)"
                    type="number"
                    value={k}
                    onChange={(e) => setK(Number(e.target.value || 1))}
                    InputProps={{
                      inputProps: { min: 1, max: 20 },
                    }}
                  />
                </Tooltip>

                <Divider sx={{ my: 1 }} />

                <Typography variant="subtitle2" sx={{ mb: 1 }}>
                  Voice Narration (TTS)
                </Typography>

                <FormControlLabel
                  control={
                    <Checkbox
                      checked={ttsEnabled}
                      onChange={(e) => setTtsEnabled(e.target.checked)}
                      color="secondary"
                    />
                  }
                  label="Enable Voice Narration"
                />

                <FormControlLabel
                  control={
                    <Checkbox
                      checked={ttsAutoPlay}
                      onChange={(e) => setTtsAutoPlay(e.target.checked)}
                      disabled={!ttsEnabled}
                      color="secondary"
                    />
                  }
                  label="Auto-play DM responses"
                />
              </Stack>
            </Card>
          </Collapse>
        </Box>
      </Drawer>

      {/* Main Chat Area */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          display: "flex",
          flexDirection: "column",
          height: "100vh",
          overflow: "hidden",
          marginLeft: drawerOpen ? 0 : `-${drawerWidth}px`,
          transition: "margin 0.3s ease-in-out",
        }}
      >
        {/* App Bar */}
        <AppBar
          position="static"
          elevation={0}
          sx={{
            bgcolor: "primary.main",
            borderBottom: "2px solid",
            borderColor: "secondary.main",
            flexShrink: 0,
          }}
        >
          <Toolbar>
            {!drawerOpen && (
              <Tooltip title="Show sidebar">
                <IconButton
                  onClick={() => setDrawerOpen(true)}
                  sx={{ mr: 1, color: "white" }}
                >
                  <ChevronRightIcon />
                </IconButton>
              </Tooltip>
            )}
            <AutoAwesomeIcon sx={{ mr: 1.5 }} />
            <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
              {selectedSession
                ? selectedSession.title || `Session ${selectedSession.id}`
                : "Dungeon Master Chat"}
            </Typography>
            {selectedSession && (
              <Badge
                badgeContent={messages.length}
                color="secondary"
                sx={{ mr: 2 }}
              >
                <ChatIcon />
              </Badge>
            )}
          </Toolbar>
        </AppBar>

        {/* Error Alert */}
        {error && (
          <Alert
            severity="error"
            onClose={() => setError(null)}
            sx={{ m: 2, mb: 0 }}
          >
            {error}
          </Alert>
        )}

        {/* Content Area - Two Column Layout */}
        {selectedSession && (
          <Box sx={{ display: "flex", flexGrow: 1, overflow: "hidden" }}>
            {/* Left Column - Session Controls (25%) */}
            <Paper
              elevation={0}
              sx={{
                width: "25%",
                minWidth: "300px",
                maxWidth: "400px",
                borderRight: "1px solid",
                borderColor: "divider",
                bgcolor: "background.paper",
                overflow: "auto",
                p: 2,
              }}
            >
              <Stack spacing={3} direction="column">
                {/* Campaign Manager Section */}
                {activeCampaign && (
                  <>
                    <CampaignManager
                      campaignId={activeCampaign.id}
                      onCampaignUpdate={handleCampaignUpdate}
                    />
                    <Divider />
                  </>
                )}

                {/* RAG Context Section */}
                <Box>
                  <Typography variant="subtitle2" color="primary" gutterBottom>
                    <MenuBookIcon
                      fontSize="small"
                      sx={{ verticalAlign: "middle", mr: 0.5 }}
                    />
                    RAG Context
                  </Typography>
                  <Stack spacing={1.5}>
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
                          Enable RAG Context
                        </Typography>
                      }
                    />

                    <TextField
                      size="small"
                      label="Context (k)"
                      type="number"
                      fullWidth
                      value={selectedSession.top_k || k}
                      onChange={(e) =>
                        updateSessionSettings({
                          top_k: Number(e.target.value || 1),
                        })
                      }
                      InputProps={{
                        inputProps: { min: 1, max: 20 },
                      }}
                    />

                    {selectedSession.include_context && (
                      <Chip
                        icon={<MenuBookIcon />}
                        label="RAG Enabled"
                        color="secondary"
                        size="small"
                      />
                    )}
                  </Stack>
                </Box>

                <Divider />

                {/* TTS Controls Section */}
                <Box>
                  <Typography variant="subtitle2" color="primary" gutterBottom>
                    <VolumeUpIcon
                      fontSize="small"
                      sx={{ verticalAlign: "middle", mr: 0.5 }}
                    />
                    Voice Narration
                  </Typography>
                  <Stack spacing={1.5}>
                    <FormControlLabel
                      control={
                        <Checkbox
                          checked={ttsEnabled}
                          onChange={(e) => setTtsEnabled(e.target.checked)}
                          color="primary"
                        />
                      }
                      label={
                        <Typography variant="body2">Enable Voice</Typography>
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
                      label={<Typography variant="body2">Auto-play</Typography>}
                    />

                    {/* Voice Selector */}
                    {ttsEnabled && (
                      <FormControl size="small" fullWidth>
                        <Select
                          value={ttsVoice}
                          onChange={(e) => setTtsVoice(e.target.value)}
                          startAdornment={
                            <VoiceIcon fontSize="small" sx={{ mr: 1, ml: 1 }} />
                          }
                        >
                          <MenuItem value="tara">Tara (Female, Warm)</MenuItem>
                          <MenuItem value="leah">
                            Leah (Female, Friendly)
                          </MenuItem>
                          <MenuItem value="jess">
                            Jess (Female, Energetic)
                          </MenuItem>
                          <MenuItem value="mia">
                            Mia (Female, Mysterious)
                          </MenuItem>
                          <MenuItem value="leo">Leo (Male, Deep)</MenuItem>
                          <MenuItem value="dan">Dan (Male, Classic)</MenuItem>
                          <MenuItem value="zac">Zac (Male, Young)</MenuItem>
                          <MenuItem value="zoe">Zoe (Neutral)</MenuItem>
                        </Select>
                      </FormControl>
                    )}

                    {/* RP Text Only Toggle */}
                    {ttsEnabled && (
                      <FormControlLabel
                        control={
                          <Checkbox
                            checked={ttsFlavorTextOnly}
                            onChange={(e) =>
                              setTtsFlavorTextOnly(e.target.checked)
                            }
                            color="primary"
                            size="small"
                          />
                        }
                        label={
                          <Typography variant="body2">RP Text Only</Typography>
                        }
                      />
                    )}
                  </Stack>
                </Box>
              </Stack>
            </Paper>

            {/* Right Column - Chat Area (75%) */}
            <Box
              sx={{
                flexGrow: 1,
                display: "flex",
                flexDirection: "column",
                overflow: "hidden",
              }}
            >
              {/* Message Input - TOP */}
              <Paper
                elevation={4}
                sx={{
                  p: 2,
                  borderBottom: "2px solid",
                  borderColor: "secondary.main",
                  bgcolor: "background.paper",
                  flexShrink: 0,
                }}
              >
                <Stack spacing={1.5}>
                  <TextField
                    fullWidth
                    multiline
                    maxRows={6}
                    placeholder="Ask the Dungeon Master anything about D&D rules, spells, monsters..."
                    value={message}
                    onChange={(e) => setMessage(e.target.value)}
                    onKeyPress={(e) => {
                      if (e.key === "Enter" && !e.shiftKey) {
                        e.preventDefault();
                        sendMessage();
                      }
                    }}
                    disabled={sending || loadingGen}
                    sx={{
                      "& .MuiOutlinedInput-root": {
                        bgcolor: "background.default",
                      },
                    }}
                  />
                  <Stack direction="row" spacing={1}>
                    <Button
                      variant="contained"
                      color="secondary"
                      onClick={sendMessage}
                      disabled={!message.trim() || sending || loadingGen}
                      endIcon={
                        sending || loadingGen ? (
                          <CircularProgress size={16} />
                        ) : (
                          <SendIcon />
                        )
                      }
                      sx={{
                        px: 3,
                        py: 1,
                        fontWeight: 600,
                        textTransform: "none",
                      }}
                    >
                      {sending
                        ? "Sending..."
                        : loadingGen
                        ? "Generating..."
                        : "Send"}
                    </Button>
                    {(sending || loadingGen) && (
                      <Button
                        variant="outlined"
                        onClick={abortGeneration}
                        color="error"
                        startIcon={<StopIcon />}
                      >
                        Cancel
                      </Button>
                    )}
                  </Stack>
                </Stack>
              </Paper>

              {/* Messages Area - BOTTOM (scrollable) */}
              <Box
                sx={{
                  flexGrow: 1,
                  overflow: "auto",
                  p: 3,
                  bgcolor: "background.default",
                  minHeight: 0,
                }}
              >
                {messages.length === 0 ? (
                  <Box
                    sx={{
                      height: "100%",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      textAlign: "center",
                    }}
                  >
                    <Box>
                      <AutoAwesomeIcon
                        sx={{ fontSize: 80, color: "secondary.main", mb: 2 }}
                      />
                      <Typography variant="h5" color="primary" gutterBottom>
                        Welcome, Dungeon Master
                      </Typography>
                      <Typography variant="body1" color="text.secondary">
                        Select an existing session or create a new campaign to
                        begin
                      </Typography>
                    </Box>
                  </Box>
                ) : messages.length === 0 ? (
                  <Box
                    sx={{
                      height: "100%",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      textAlign: "center",
                    }}
                  >
                    <Box>
                      <ChatIcon
                        sx={{ fontSize: 60, color: "text.disabled", mb: 2 }}
                      />
                      <Typography variant="h6" color="text.secondary">
                        No messages yet
                      </Typography>
                      <Typography variant="body2" color="text.disabled">
                        Start the conversation below
                      </Typography>
                    </Box>
                  </Box>
                ) : (
                  <Stack spacing={2}>
                    {messages.map((msg) => (
                      <Card
                        key={msg.id}
                        elevation={2}
                        sx={{
                          bgcolor:
                            msg.role === "assistant"
                              ? "primary.light"
                              : "background.paper",
                          color:
                            msg.role === "assistant" ? "white" : "text.primary",
                          maxWidth: "85%",
                          alignSelf:
                            msg.role === "assistant"
                              ? "flex-start"
                              : "flex-end",
                          opacity: msg._optimistic ? 0.6 : 1,
                        }}
                      >
                        <CardContent>
                          <Stack
                            direction="row"
                            spacing={1.5}
                            alignItems="flex-start"
                          >
                            <Avatar
                              sx={{
                                bgcolor:
                                  msg.role === "assistant"
                                    ? "secondary.main"
                                    : "primary.main",
                                width: 40,
                                height: 40,
                              }}
                            >
                              {msg.role === "assistant" ? (
                                <SmartToyIcon />
                              ) : (
                                <PersonIcon />
                              )}
                            </Avatar>
                            <Box sx={{ flex: 1 }}>
                              <Typography
                                variant="subtitle2"
                                sx={{
                                  fontWeight: 600,
                                  mb: 1,
                                  textTransform: "capitalize",
                                }}
                              >
                                {msg.role === "assistant"
                                  ? "Dungeon Master"
                                  : "Player"}
                              </Typography>

                              {/* Render Markdown for assistant, plain text for user */}
                              {msg.role === "assistant" ? (
                                <Box
                                  sx={{
                                    "& p": { mb: 1, lineHeight: 1.6 },
                                    "& h1, & h2, & h3, & h4, & h5, & h6": {
                                      fontWeight: 600,
                                      mt: 2,
                                      mb: 1,
                                      color: "inherit",
                                    },
                                    "& ul, & ol": { pl: 3, mb: 1 },
                                    "& li": { mb: 0.5 },
                                    "& strong": { fontWeight: 700 },
                                    "& em": { fontStyle: "italic" },
                                    "& code": {
                                      bgcolor: "rgba(0,0,0,0.2)",
                                      px: 0.5,
                                      py: 0.25,
                                      borderRadius: 0.5,
                                      fontFamily: "monospace",
                                      fontSize: "0.9em",
                                    },
                                    "& pre": {
                                      bgcolor: "rgba(0,0,0,0.3)",
                                      p: 1.5,
                                      borderRadius: 1,
                                      overflow: "auto",
                                      "& code": {
                                        bgcolor: "transparent",
                                        px: 0,
                                        py: 0,
                                      },
                                    },
                                    "& hr": {
                                      borderColor: "rgba(255,255,255,0.2)",
                                      my: 2,
                                    },
                                  }}
                                >
                                  <ReactMarkdown>{msg.content}</ReactMarkdown>
                                </Box>
                              ) : (
                                <Typography
                                  variant="body1"
                                  sx={{
                                    whiteSpace: "pre-wrap",
                                    lineHeight: 1.6,
                                  }}
                                >
                                  {msg.content}
                                </Typography>
                              )}

                              {/* TTS Audio Player */}
                              {msg.role === "assistant" &&
                                ttsEnabled &&
                                msg.id &&
                                !msg._optimistic && (
                                  <Box sx={{ mt: 1.5 }}>
                                    <TTSAudioPlayer
                                      sessionId={selectedSession.id}
                                      messageId={msg.id}
                                      autoPlay={ttsAutoPlay}
                                      compact={true}
                                      defaultVoice={ttsVoice}
                                      defaultFlavorTextOnly={ttsFlavorTextOnly}
                                      sx={{
                                        bgcolor: "rgba(255,255,255,0.1)",
                                        borderRadius: 1,
                                        p: 1,
                                      }}
                                    />
                                  </Box>
                                )}

                              {/* Source Citations */}
                              {msg.role === "assistant" &&
                                msg.metadata &&
                                msg.metadata.retrievals &&
                                msg.metadata.retrievals.length > 0 && (
                                  <Box
                                    sx={{
                                      mt: 2,
                                      pt: 2,
                                      borderTop:
                                        "1px solid rgba(255,255,255,0.2)",
                                    }}
                                  >
                                    <Stack
                                      direction="row"
                                      spacing={0.5}
                                      alignItems="center"
                                      sx={{ mb: 1 }}
                                    >
                                      <MenuBookIcon fontSize="small" />
                                      <Typography
                                        variant="caption"
                                        sx={{ fontWeight: 600 }}
                                      >
                                        Sources Referenced:
                                      </Typography>
                                    </Stack>
                                    <Stack spacing={0.5}>
                                      {msg.metadata.retrievals.map((r, idx) => (
                                        <Chip
                                          key={idx}
                                          label={r.name || r.id || "Unknown"}
                                          size="small"
                                          onClick={
                                            r.source_url
                                              ? () =>
                                                  window.open(
                                                    r.source_url,
                                                    "_blank"
                                                  )
                                              : undefined
                                          }
                                          sx={{
                                            bgcolor: "rgba(255,255,255,0.15)",
                                            color: "white",
                                            "&:hover": {
                                              bgcolor: "rgba(255,255,255,0.25)",
                                            },
                                          }}
                                        />
                                      ))}
                                    </Stack>
                                  </Box>
                                )}
                            </Box>
                          </Stack>
                        </CardContent>
                      </Card>
                    ))}
                    <div ref={bottomRef} />
                  </Stack>
                )}
              </Box>
            </Box>

            {/* Right Column - Party/Combat Panel (25%) */}
            {activeCampaign && (
              <Paper
                elevation={0}
                sx={{
                  width: "25%",
                  minWidth: "300px",
                  maxWidth: "400px",
                  borderLeft: "1px solid",
                  borderColor: "divider",
                  bgcolor: "background.paper",
                  display: "flex",
                  flexDirection: "column",
                  overflow: "hidden",
                }}
              >
                {/* Panel Tabs */}
                <Box sx={{ p: 1, borderBottom: 1, borderColor: "divider" }}>
                  <Stack direction="row" spacing={1}>
                    <Button
                      size="small"
                      variant={
                        rightPanelView === "party" ? "contained" : "outlined"
                      }
                      onClick={() => setRightPanelView("party")}
                      fullWidth
                    >
                      Party
                    </Button>
                    <Button
                      size="small"
                      variant={
                        rightPanelView === "initiative"
                          ? "contained"
                          : "outlined"
                      }
                      onClick={() => setRightPanelView("initiative")}
                      fullWidth
                      disabled={!combatMode}
                    >
                      Initiative
                    </Button>
                    <Button
                      size="small"
                      variant={
                        rightPanelView === "combat" ? "contained" : "outlined"
                      }
                      onClick={() => setRightPanelView("combat")}
                      fullWidth
                      disabled={!combatMode}
                    >
                      Combat
                    </Button>
                  </Stack>
                </Box>

                {/* Panel Content */}
                <Box sx={{ flexGrow: 1, overflow: "auto" }}>
                  {rightPanelView === "party" && (
                    <PartyPanel
                      campaignId={activeCampaign.id}
                      onCharacterClick={(char) =>
                        console.log("Character clicked:", char)
                      }
                    />
                  )}

                  {rightPanelView === "initiative" && (
                    <InitiativeTracker
                      campaignId={activeCampaign.id}
                      isActive={combatMode}
                      onCombatStart={handleCombatStart}
                      onCombatEnd={handleCombatEnd}
                    />
                  )}

                  {rightPanelView === "combat" && activeCampaign.party && (
                    <CombatActionPanel
                      campaignId={activeCampaign.id}
                      party={activeCampaign.party}
                      onDiceRoll={() => setDiceRollerOpen(true)}
                    />
                  )}
                </Box>

                {/* Dice Roller Button */}
                <Box sx={{ p: 2, borderTop: 1, borderColor: "divider" }}>
                  <Button
                    fullWidth
                    variant="outlined"
                    onClick={() => setDiceRollerOpen(true)}
                    startIcon={<MenuBookIcon />}
                  >
                    🎲 Roll Dice
                  </Button>
                </Box>
              </Paper>
            )}
          </Box>
        )}

        {/* Campaign Setup Wizard */}
        <CampaignSetupWizard
          open={campaignWizardOpen}
          onClose={() => setCampaignWizardOpen(false)}
          onCampaignCreated={handleCampaignCreated}
          chatSessionId={selectedSession?.id}
        />

        {/* Dice Roller */}
        <DiceRoller
          open={diceRollerOpen}
          onClose={() => setDiceRollerOpen(false)}
          onRollComplete={handleDiceRoll}
        />
      </Box>
    </Box>
  );
}
