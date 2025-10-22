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
} from "@mui/icons-material";
import { darkTheme } from "../theme/darkTheme";
import ReactMarkdown from "react-markdown";
import TTSAudioPlayer from "../components/game/TTSAudioPlayer";

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
  const bottomRef = useRef(null);

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
    try {
      const r = await fetch(`/api/chat/sessions/${sessionId}`);
      if (!r.ok) throw new Error(`Failed to load session: ${r.status}`);
      const s = await r.json();
      setSelectedSession(s);
      setMessages(s.messages || []);
    } catch (e) {
      console.error(e);
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
      }
    } catch (e) {
      console.error(e);
    }
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

        {/* Session Controls */}
        {selectedSession && (
          <Paper
            elevation={0}
            sx={{
              p: 2,
              borderBottom: "1px solid",
              borderColor: "divider",
              bgcolor: "background.paper",
            }}
          >
            <Stack
              direction="row"
              spacing={2}
              alignItems="center"
              flexWrap="wrap"
            >
              <Tooltip title="Enable to include D&D rules context in responses">
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
                    <Stack direction="row" spacing={0.5} alignItems="center">
                      <MenuBookIcon fontSize="small" />
                      <Typography variant="body2">RAG Context</Typography>
                    </Stack>
                  }
                />
              </Tooltip>

              <Tooltip title="Number of rule references to include">
                <TextField
                  size="small"
                  label="Context (k)"
                  type="number"
                  value={selectedSession.top_k || k}
                  onChange={(e) =>
                    updateSessionSettings({
                      top_k: Number(e.target.value || 1),
                    })
                  }
                  sx={{ width: 120 }}
                  InputProps={{
                    inputProps: { min: 1, max: 20 },
                  }}
                />
              </Tooltip>

              {selectedSession.include_context && (
                <Chip
                  icon={<MenuBookIcon />}
                  label="RAG Enabled"
                  color="secondary"
                  size="small"
                />
              )}

              <Divider orientation="vertical" flexItem />

              {/* TTS Controls */}
              <Tooltip title="Enable voice narration for DM responses">
                <FormControlLabel
                  control={
                    <Checkbox
                      checked={ttsEnabled}
                      onChange={(e) => setTtsEnabled(e.target.checked)}
                      color="primary"
                    />
                  }
                  label={
                    <Stack direction="row" spacing={0.5} alignItems="center">
                      <VolumeUpIcon fontSize="small" />
                      <Typography variant="body2">Voice</Typography>
                    </Stack>
                  }
                />
              </Tooltip>

              <Tooltip title="Automatically play voice narration">
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
                    <Stack direction="row" spacing={0.5} alignItems="center">
                      <PlayArrowIcon fontSize="small" />
                      <Typography variant="body2">Auto-play</Typography>
                    </Stack>
                  }
                />
              </Tooltip>

              {ttsEnabled && (
                <Chip
                  icon={<VolumeUpIcon />}
                  label={ttsAutoPlay ? "Voice: Auto" : "Voice: Manual"}
                  color="primary"
                  size="small"
                />
              )}
            </Stack>
          </Paper>
        )}

        {/* Messages Area */}
        <Box
          sx={{
            flexGrow: 1,
            overflow: "auto",
            p: 3,
            bgcolor: "background.default",
          }}
        >
          {!selectedSession ? (
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
                  Select an existing session or create a new campaign to begin
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
                    color: msg.role === "assistant" ? "white" : "text.primary",
                    maxWidth: "85%",
                    alignSelf:
                      msg.role === "assistant" ? "flex-start" : "flex-end",
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
                            sx={{ whiteSpace: "pre-wrap", lineHeight: 1.6 }}
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
                                compact={false}
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
                                borderTop: "1px solid rgba(255,255,255,0.2)",
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
                                            window.open(r.source_url, "_blank")
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

        {/* Message Input */}
        {selectedSession && (
          <Paper
            elevation={4}
            sx={{
              p: 2,
              borderTop: "2px solid",
              borderColor: "secondary.main",
              bgcolor: "background.paper",
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
              <Stack direction="row" spacing={2} alignItems="center">
                <Button
                  variant="contained"
                  color="secondary"
                  size="large"
                  onClick={sendMessage}
                  disabled={!message.trim() || sending || loadingGen}
                  startIcon={
                    sending || loadingGen ? (
                      <CircularProgress size={20} />
                    ) : (
                      <SendIcon />
                    )
                  }
                  sx={{ minWidth: 140 }}
                >
                  {sending ? "Sending..." : loadingGen ? "Thinking..." : "Send"}
                </Button>

                {loadingGen && (
                  <Stack direction="row" spacing={1} alignItems="center">
                    <CircularProgress size={20} />
                    <Typography variant="body2" color="text.secondary">
                      The Dungeon Master is consulting the ancient tomes...
                    </Typography>
                  </Stack>
                )}

                <Typography
                  variant="caption"
                  color="text.disabled"
                  sx={{ ml: "auto" }}
                >
                  Press Shift+Enter for new line
                </Typography>
              </Stack>
            </Stack>
          </Paper>
        )}
      </Box>
    </Box>
  );
}
