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
import FloatingChatInput from "../components/game/FloatingChatInput";
import CinematicMessageCard from "../components/game/CinematicMessageCard";
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
  Casino as DiceIcon,
  Stop as StopIcon,
  Campaign as CampaignIcon,
} from "@mui/icons-material";
import { darkTheme } from "../theme/darkTheme";
import ReactMarkdown from "react-markdown";
import TTSAudioPlayer from "../components/game/TTSAudioPlayer";
import SceneImageDisplay from "../components/game/SceneImageDisplay";
import CampaignSetupWizard from "../components/CampaignSetupWizard";
import CampaignManager from "../components/CampaignManager";
import CheckpointManager from "../components/CheckpointManager";
import PartyPanel from "../components/PartyPanel";
import InitiativeTracker from "../components/InitiativeTracker";
import DiceRoller from "../components/DiceRoller";
import CombatActionPanel from "../components/CombatActionPanel";
import SettingsDrawer from "../components/SettingsDrawer";
import ResponseSuggestionChips from "../components/game/ResponseSuggestionChips";
import ActionChipsParser from "../components/game/ActionChipsParser";
import AbilityCheckPanel from "../components/game/AbilityCheckPanel";
import CharacterQuickSelect from "../components/game/CharacterQuickSelect";

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
  const [ttsAutoPlay, setTtsAutoPlay] = useState(true); // Changed default to true for auto-play
  const [ttsVoice, setTtsVoice] = useState("alloy"); // OpenAI-compatible default voice
  const [ttsFlavorTextOnly, setTtsFlavorTextOnly] = useState(false);
  const [sceneImageAutoGenerate, setSceneImageAutoGenerate] = useState(true); // Auto-generate scene images by default
  const bottomRef = useRef(null);

  // Campaign & Combat State
  const [campaignWizardOpen, setCampaignWizardOpen] = useState(false);
  const [activeCampaign, setActiveCampaign] = useState(null);
  const [combatMode, setCombatMode] = useState(false);
  const [diceRollerOpen, setDiceRollerOpen] = useState(false);
  const [abilityCheckOpen, setAbilityCheckOpen] = useState(false);
  const [rightPanelView, setRightPanelView] = useState("party"); // 'party', 'initiative', 'combat'
  const [rightPanelOpen, setRightPanelOpen] = useState(true);

  // Active character selection state
  const [activeCharacters, setActiveCharacters] = useState([]); // Array of character IDs currently acting
  const [availableCharacters, setAvailableCharacters] = useState([]); // Characters available to select

  useEffect(() => {
    fetchSessions();
  }, []);

  // Load available characters when campaign changes
  useEffect(() => {
    const loadPartyCharacters = async () => {
      if (!activeCampaign || !activeCampaign.party) {
        setAvailableCharacters([]);
        setActiveCharacters([]);
        return;
      }

      try {
        // Get full character details for party members
        const characterPromises = activeCampaign.party.map(async (member) => {
          try {
            const r = await fetch(`/api/characters/${member.character_id}`);
            if (r.ok) {
              const char = await r.json();
              return {
                id: char.id,
                name: char.name || member.name,
                ...char,
              };
            }
          } catch (e) {
            console.error(
              `Failed to load character ${member.character_id}:`,
              e
            );
          }
          return null;
        });

        const characters = (await Promise.all(characterPromises)).filter(
          Boolean
        );
        setAvailableCharacters(characters);

        // Auto-select first character if none selected
        if (characters.length > 0 && activeCharacters.length === 0) {
          setActiveCharacters([characters[0].id]);
        }
      } catch (e) {
        console.error("Failed to load party characters:", e);
      }
    };

    loadPartyCharacters();
  }, [activeCampaign]);

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
      // Build message payload with active character context
      const messagePayload = {
        role: "user",
        content: message,
        // Include active character IDs in metadata for DM context
        meta:
          activeCharacters.length > 0
            ? {
                active_character_ids: activeCharacters,
                active_character_names: availableCharacters
                  .filter((c) => activeCharacters.includes(c.id))
                  .map((c) => c.name),
              }
            : undefined,
      };

      // persist user message
      const r = await fetch(
        `/api/chat/sessions/${selectedSession.id}/messages`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(messagePayload),
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

      // Build detailed party list with stats
      const partyList = party
        .map((char) => {
          const abilityScores = char.ability_scores || {};
          const abilityMods = char.ability_modifiers || {};

          return `### ${char.name}
**${char.dnd_species} ${char.dnd_class} ${char.dnd_level}** | Background: ${
            char.dnd_background || "Unknown"
          }

**Combat Stats:**
- AC: ${char.armor_class || 10} | HP: ${char.current_hp}/${
            char.max_hp
          } | Speed: ${char.speed || 30} ft | Initiative: ${
            char.initiative >= 0 ? "+" : ""
          }${char.initiative || 0}

**Ability Scores:**
- STR: ${abilityScores.strength || 10} (${
            abilityMods.strength >= 0 ? "+" : ""
          }${abilityMods.strength || 0}) | DEX: ${
            abilityScores.dexterity || 10
          } (${abilityMods.dexterity >= 0 ? "+" : ""}${
            abilityMods.dexterity || 0
          }) | CON: ${abilityScores.constitution || 10} (${
            abilityMods.constitution >= 0 ? "+" : ""
          }${abilityMods.constitution || 0})
- INT: ${abilityScores.intelligence || 10} (${
            abilityMods.intelligence >= 0 ? "+" : ""
          }${abilityMods.intelligence || 0}) | WIS: ${
            abilityScores.wisdom || 10
          } (${abilityMods.wisdom >= 0 ? "+" : ""}${
            abilityMods.wisdom || 0
          }) | CHA: ${abilityScores.charisma || 10} (${
            abilityMods.charisma >= 0 ? "+" : ""
          }${abilityMods.charisma || 0})

**Skills:** ${
            char.skills
              ? Object.entries(char.skills)
                  .filter(([_, proficient]) => proficient)
                  .map(([skill, _]) => skill.replace("_", " "))
                  .join(", ") || "None"
              : "None"
          }

**Equipment:** ${
            char.equipment && Array.isArray(char.equipment)
              ? char.equipment.slice(0, 5).join(", ")
              : "Standard starting equipment"
          }
${
  char.equipment && char.equipment.length > 5
    ? `... and ${char.equipment.length - 5} more items`
    : ""
}

**Spellcasting:** ${
            char.spellcasting?.spellcasting_ability
              ? `${char.spellcasting.spellcasting_ability} (DC ${
                  char.spellcasting.spell_save_dc || "N/A"
                }, +${char.spellcasting.spell_attack_bonus || 0} to hit)`
              : "None"
          }

**Conditions:** ${
            char.conditions && char.conditions.length > 0
              ? char.conditions.join(", ")
              : "None"
          }
`;
        })
        .join("\n---\n\n");

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

---

## **The Adventuring Party**

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

**The party's full stats are provided above. You have complete information about:**
- Current HP, AC, and combat statistics
- All ability scores and modifiers
- Proficient skills for appropriate DCs
- Equipment and spellcasting abilities
- Any active conditions or status effects

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
              <Typography
                variant="caption"
                display="block"
                sx={{
                  wordBreak: "break-word",
                  overflowWrap: "break-word",
                  whiteSpace: "normal",
                }}
              >
                {activeCampaign.title}
              </Typography>
              <Typography
                variant="caption"
                color="text.secondary"
                display="block"
                sx={{
                  wordBreak: "break-word",
                  overflowWrap: "break-word",
                  whiteSpace: "normal",
                }}
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
            onClick={() => {
              if (activeCampaign) {
                // Open settings drawer to campaign section
                setSettingsOpen(true);
              } else {
                // Open campaign wizard
                setCampaignWizardOpen(true);
              }
            }}
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
          width: drawerOpen ? `calc(100vw - ${drawerWidth}px)` : "100vw",
          marginLeft: drawerOpen ? 0 : `-${drawerWidth}px`,
          transition: "all 0.3s ease-in-out",
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
              <>
                <Tooltip
                  title={settingsOpen ? "Hide Settings" : "Show Settings"}
                >
                  <IconButton
                    onClick={() => setSettingsOpen(!settingsOpen)}
                    sx={{ color: "white", mr: 1 }}
                  >
                    <SettingsIcon />
                  </IconButton>
                </Tooltip>
                {activeCampaign && (
                  <>
                    <CheckpointManager
                      campaignId={activeCampaign.id}
                      onRestoreComplete={(restoredCampaign) => {
                        setActiveCampaign(restoredCampaign);
                        setError(null);
                        // Optionally reload party data
                        fetchSessions();
                      }}
                    />
                    <Tooltip
                      title={
                        rightPanelOpen ? "Hide Party Panel" : "Show Party Panel"
                      }
                    >
                      <IconButton
                        onClick={() => setRightPanelOpen(!rightPanelOpen)}
                        sx={{ color: "white", mr: 1, ml: 1 }}
                      >
                        <PersonIcon />
                      </IconButton>
                    </Tooltip>
                  </>
                )}
                <Badge
                  badgeContent={messages.length}
                  color="secondary"
                  sx={{ mr: 2 }}
                >
                  <ChatIcon />
                </Badge>
              </>
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

        {/* Content Area - Direct scrolling without nested containers */}
        {selectedSession && (
          <Box
            sx={{
              display: "flex",
              flexGrow: 1,
              overflow: "auto", // Single scrollbar for entire page
              position: "relative",
              p: 3,
              bgcolor: "background.default",
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
              <Stack spacing={1.5}>
                {messages.map((msg) => {
                  // Create a stateful wrapper for SceneImageDisplay to extract image data
                  const SceneImageWrapper = ({ onImageData }) => {
                    const [imageData, setImageData] = useState(null);

                    React.useEffect(() => {
                      if (imageData && onImageData) {
                        onImageData(imageData);
                      }
                    }, [imageData]);

                    return msg.role === "assistant" &&
                      msg.id &&
                      !msg._optimistic ? (
                      <SceneImageDisplay
                        sessionId={selectedSession.id}
                        messageId={msg.id}
                        messageContent={msg.content}
                        compact={true}
                        autoGenerate={sceneImageAutoGenerate}
                        onImageGenerated={(data) => setImageData(data)}
                      />
                    ) : null;
                  };

                  // Track TTS playing state for this message
                  const MessageWithTTS = () => {
                    const [ttsPlaying, setTtsPlaying] = React.useState(false);
                    
                    return (
                      <CinematicMessageCard
                        key={msg.id}
                        message={msg}
                        isUser={msg.role !== "assistant"}
                        sceneImage={null} // Will be populated by SceneImageDisplay
                        onImageGenerate={
                          msg.role === "assistant" && msg.id && !msg._optimistic
                            ? async () => {
                                // Trigger image generation via SceneImageDisplay
                                // This will be handled by the SceneImageDisplay component itself
                              }
                            : undefined
                        }
                        ttsPlaying={ttsPlaying}
                        ttsAutoPlay={ttsAutoPlay}
                      >
                      {/* Scene Image Generator - Appears first for visual hierarchy */}
                      {msg.role === "assistant" &&
                        msg.id &&
                        !msg._optimistic && (
                          <Box sx={{ mb: 1.5 }}>
                            <SceneImageDisplay
                              sessionId={selectedSession.id}
                              messageId={msg.id}
                              messageContent={msg.content}
                              compact={true}
                              autoGenerate={sceneImageAutoGenerate}
                            />
                          </Box>
                        )}

                      {/* Action Chips Parser - Parse tables and create interactive chips */}
                      {msg.role === "assistant" && (
                        <Box sx={{ mb: 1 }}>
                          <ActionChipsParser
                            content={msg.content}
                            onActionClick={(action, roll, dc) => {
                              // Open ability check panel if it's an ability/skill check
                              const hasAbilityCheck =
                                roll && roll.toLowerCase().includes("d20");

                              if (
                                hasAbilityCheck &&
                                availableCharacters.length > 0
                              ) {
                                // Open the ability check panel
                                setAbilityCheckOpen(true);
                              } else {
                                // Fallback: construct a formatted message
                                let actionMessage = `I want to ${action}`;
                                if (roll) {
                                  actionMessage += `\n\nSuggested roll: ${roll}`;
                                }
                                if (dc) {
                                  actionMessage += `\nDC: ${dc}`;
                                }
                                setMessage(actionMessage);
                              }
                            }}
                          />
                        </Box>
                      )}

                        {/* TTS Audio Player */}
                        {msg.role === "assistant" &&
                          ttsEnabled &&
                          msg.id &&
                          !msg._optimistic && (
                            <Box sx={{ mb: 1 }}>
                              <TTSAudioPlayer
                                sessionId={selectedSession.id}
                                messageId={msg.id}
                                autoPlay={ttsAutoPlay}
                                compact={true}
                                defaultVoice={ttsVoice}
                                defaultFlavorTextOnly={ttsFlavorTextOnly}
                                onPlayingChange={setTtsPlaying}
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
                      </CinematicMessageCard>
                    );
                  };

                  return <MessageWithTTS key={msg.id} />;
                })}
                <div ref={bottomRef} />
              </Stack>
            )}

            {/* Right Column - Party/Combat Panel (Collapsible) */}
            {activeCampaign && (
              <Paper
                elevation={0}
                sx={{
                  width: rightPanelOpen ? "320px" : "0px",
                  minWidth: rightPanelOpen ? "320px" : "0px",
                  borderLeft: rightPanelOpen ? "1px solid" : "none",
                  borderColor: "divider",
                  bgcolor: "background.paper",
                  display: "flex",
                  flexDirection: "column",
                  overflow: rightPanelOpen ? "hidden" : "hidden",
                  transition: "all 0.3s ease-in-out",
                }}
              >
                {/* Panel Tabs */}
                <Box
                  sx={{
                    p: 1,
                    borderBottom: 1,
                    borderColor: "divider",
                    opacity: rightPanelOpen ? 1 : 0,
                  }}
                >
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
                  <Stack spacing={1}>
                    <Button
                      fullWidth
                      variant="contained"
                      onClick={() => setAbilityCheckOpen(true)}
                      startIcon={<PersonIcon />}
                      disabled={
                        !availableCharacters || availableCharacters.length === 0
                      }
                    >
                      🎯 Ability Check
                    </Button>
                    <Button
                      fullWidth
                      variant="outlined"
                      onClick={() => setDiceRollerOpen(true)}
                      startIcon={<DiceIcon />}
                    >
                      🎲 Roll Dice
                    </Button>
                  </Stack>
                </Box>
              </Paper>
            )}
          </Box>
        )}

        {/* Compact Draggable Floating Chat Input */}
        {selectedSession && (
          <FloatingChatInput
            message={message}
            setMessage={setMessage}
            onSend={sendMessage}
            sending={sending}
            loading={loadingGen}
            onCancel={abortGeneration}
            availableCharacters={availableCharacters}
            activeCharacters={activeCharacters}
            onToggleCharacter={(charId) => {
              setActiveCharacters((prev) => {
                if (prev.includes(charId)) {
                  return prev.length > 1
                    ? prev.filter((id) => id !== charId)
                    : prev;
                } else {
                  return [...prev, charId];
                }
              });
            }}
            showCharacterSelect={
              activeCampaign && availableCharacters.length > 0
            }
          />
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

        {/* Ability Check Panel */}
        <AbilityCheckPanel
          open={abilityCheckOpen}
          onClose={() => setAbilityCheckOpen(false)}
          characters={availableCharacters}
          onCheckComplete={(message, result) => {
            // Send the formatted check result to chat
            setMessage(message);
            setAbilityCheckOpen(false);
          }}
        />

        {/* Settings Drawer (Offcanvas) */}
        <SettingsDrawer
          open={settingsOpen}
          onClose={() => setSettingsOpen(false)}
          provider={provider}
          setProvider={setProvider}
          model={model}
          setModel={setModel}
          availableModels={availableModels}
          selectedSession={selectedSession}
          updateSessionSettings={updateSessionSettings}
          ttsEnabled={ttsEnabled}
          setTtsEnabled={setTtsEnabled}
          ttsAutoPlay={ttsAutoPlay}
          setTtsAutoPlay={setTtsAutoPlay}
          ttsVoice={ttsVoice}
          setTtsVoice={setTtsVoice}
          ttsFlavorTextOnly={ttsFlavorTextOnly}
          setTtsFlavorTextOnly={setTtsFlavorTextOnly}
          sceneImageAutoGenerate={sceneImageAutoGenerate}
          setSceneImageAutoGenerate={setSceneImageAutoGenerate}
          activeCampaign={activeCampaign}
          handleCampaignUpdate={handleCampaignUpdate}
        />
      </Box>
    </Box>
  );
}
