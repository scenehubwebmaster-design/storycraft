import React, { useEffect, useState, useRef, useCallback } from "react";
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
  List,
  ListItem,
  ListItemButton,
  ListItemText,
  ListItemAvatar,
  Avatar,
  Chip,
  Collapse,
  Fade,
  Stack,
  Paper,
  Toolbar,
  AppBar,
  InputAdornment,
  Tooltip,
  Badge,
  useMediaQuery,
  useTheme,
  Drawer,
  ListItemIcon,
  Fab,
} from "@mui/material";
import FloatingChatInput from "../components/game/FloatingChatInput";
import CinematicMessageCard from "../components/game/CinematicMessageCard";
import SuggestedActions from "../components/game/SuggestedActions";
import ActionChipsParser, {
  parseActions,
} from "../components/game/ActionChipsParser";
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
  Menu as MenuIcon,
  Home as HomeIcon,
  Create as CreateIcon,
  AutoStories as AutoStoriesIcon,
  People as PeopleIcon,
  Public as PublicIcon,
  History as HistoryIcon,
} from "@mui/icons-material";
import { darkTheme } from "../theme/darkTheme";
import ReactMarkdown from "react-markdown";
import TTSAudioPlayer from "../components/game/TTSAudioPlayer";
import SceneImageDisplay from "../components/game/SceneImageDisplay";
import DialogueNarrationPlayer from "../components/game/DialogueNarrationPlayer";
import CampaignSetupWizard from "../components/CampaignSetupWizard";
import CampaignManager from "../components/CampaignManager";
import CheckpointManager from "../components/CheckpointManager";
import CampaignJournal from "../components/CampaignJournal";
import PartyPanel from "../components/PartyPanel";
import InitiativeTracker from "../components/InitiativeTracker";
import DiceRoller from "../components/DiceRoller";
import CombatActionPanel from "../components/CombatActionPanel";
import LeftSettingsPanel from "../components/game/LeftSettingsPanel";
import ResponseSuggestionChips from "../components/game/ResponseSuggestionChips";
import AbilityCheckPanel from "../components/game/AbilityCheckPanel";
import CharacterQuickSelect from "../components/game/CharacterQuickSelect";
import { Link } from "react-router-dom";

export default function DMChatPage() {
  const theme = useTheme();
  const isLargeScreen = useMediaQuery(theme.breakpoints.up("lg")); // 1200px+
  const isXLScreen = useMediaQuery(theme.breakpoints.up("xl")); // 1536px+

  const [sessions, setSessions] = useState([]);
  const [selectedSession, setSelectedSession] = useState(null);
  const [loadingSessions, setLoadingSessions] = useState(false);
  const [creating, setCreating] = useState(false);
  const [title, setTitle] = useState("");
  const [message, setMessage] = useState("");
  const [sending, setSending] = useState(false);
  const [messages, setMessages] = useState([]);
  const [archivedMessages, setArchivedMessages] = useState([]); // Historical message pairs
  const [showHistory, setShowHistory] = useState(false); // Toggle history view
  const [provider, setProvider] = useState("groq");
  const [model, setModel] = useState("");
  const [availableModels, setAvailableModels] = useState([]);
  const [k, setK] = useState(5);
  const [loadingGen, setLoadingGen] = useState(false);
  const [error, setError] = useState(null);
  const [settingsOpen, setSettingsOpen] = useState(false);
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
  const [journalOpen, setJournalOpen] = useState(false); // Journal drawer state

  // Active character selection state
  const [activeCharacters, setActiveCharacters] = useState([]); // Array of character IDs currently acting
  const [availableCharacters, setAvailableCharacters] = useState([]); // Characters available to select

  // Track which assistant messages have finished their typing animation so we can reveal chips/buttons
  const [readyMessages, setReadyMessages] = useState({});
  // Parsed actions per message (filled when typing completes)
  const [parsedActions, setParsedActions] = useState({});
  // Which messages currently have their actions visible (user toggled)
  const [showActions, setShowActions] = useState({});

  // Navigation drawer state
  const [navDrawerOpen, setNavDrawerOpen] = useState(false);

  useEffect(() => {
    fetchSessions();
  }, []);

  // Auto-manage right panel state based on screen size
  useEffect(() => {
    if (!isLargeScreen) {
      setRightPanelOpen(false);
    } else {
      if (activeCampaign) {
        setRightPanelOpen(true);
      }
    }
  }, [isLargeScreen, activeCampaign]);

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

  // Scroll handler for typing animation progress
  const handleTypingProgress = useCallback(() => {
    if (bottomRef.current) {
      bottomRef.current.scrollIntoView({
        behavior: "smooth",
        block: "nearest",
      });
    }
  }, []);

  // Contextual roll state: used to prefill DiceRoller with a requested skill check
  const [contextualRoll, setContextualRoll] = useState(null);

  // Parse a roll string like "d20 + 3" or "d20+2" into { dice, count, modifier }
  const parseRollString = (rollStr) => {
    if (!rollStr || typeof rollStr !== "string")
      return { dice: "d20", count: 1, modifier: 0 };
    const s = rollStr.trim();
    // Match patterns like '2d6+3', 'd20 + 4', 'd20', '1d20-1'
    const m = s.match(/(\d*)d(\d+)(?:\s*([+-])\s*(\d+))?/i);
    if (m) {
      const count = m[1] ? parseInt(m[1], 10) : 1;
      const sides = m[2];
      const sign = m[3] || null;
      const num = m[4] ? parseInt(m[4], 10) : 0;
      const modifier = sign === "-" ? -num : num;
      return { dice: `d${sides}`, count, modifier };
    }

    // Fallback: look for a plus/minus value
    const plusMatch = s.match(/([+-]\d+)$/);
    const modifier = plusMatch ? parseInt(plusMatch[1], 10) : 0;
    const diceMatch = s.match(/d\d+/i);
    const dice = diceMatch ? diceMatch[0].toLowerCase() : "d20";
    return { dice, count: 1, modifier };
  };

  // Open DiceRoller prefilled and optionally auto-roll (contextual check)
  const openContextualRoll = ({
    rollStr,
    skillName = null,
    characterId = null,
    autoRoll = true,
  }) => {
    const parsed = parseRollString(rollStr);
    const character =
      availableCharacters.find((c) => c.id === characterId) ||
      availableCharacters[0] ||
      null;
    setContextualRoll({
      dice: parsed.dice,
      count: parsed.count,
      modifier: parsed.modifier,
      skillName,
      character,
      autoRoll: !!autoRoll,
    });
    setDiceRollerOpen(true);
  };

  const handleMessageTypingComplete = useCallback((messageId) => {
    if (!messageId) return;
    // Small delay to allow final scroll animation to settle before revealing chips
    setTimeout(() => {
      setReadyMessages((prev) => ({ ...prev, [messageId]: true }));
    }, 200);
  }, []);

  // Enhanced: when typing completes, parse actions from the message and
  // dispatch a global event so other UI (action buttons, global parsers)
  // can react. This provides the "trigger" behavior you requested.
  const handleMessageTypingCompleteEnhanced = useCallback(
    (messageId) => {
      // mark ready for rendering chips (keep small delay for scroll settling)
      setTimeout(() => {
        setReadyMessages((prev) => ({ ...prev, [messageId]: true }));
      }, 120);

      // find the message content and parse actions
      const msg = messages.find((m) => m.id === messageId);
      if (!msg || !msg.content) return;
      try {
        const actions = parseActions(msg.content) || [];
        // cache parsed actions — don't auto-show them; user can reveal
        setParsedActions((prev) => ({ ...prev, [messageId]: actions }));
      } catch (e) {
        console.debug("Failed to parse actions on typing complete:", e);
      }
    },
    [messages]
  );

  useEffect(() => {
    // scroll to bottom on messages change
    if (bottomRef.current)
      bottomRef.current.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Subscribe to server-sent events for metadata updates for the selected session
  useEffect(() => {
    if (!selectedSession || !selectedSession.id) return;

    const es = new EventSource(
      `/api/chat/sessions/${selectedSession.id}/events`
    );

    es.onmessage = (ev) => {
      try {
        const obj = JSON.parse(ev.data);
        console.log("[DMChat] SSE event received:", obj);

        if (obj && obj.type === "message_metadata_updated") {
          const { message_id, metadata } = obj;
          console.log(
            `[DMChat] Updating metadata for message ${message_id}:`,
            metadata
          );

          setMessages((prev) =>
            prev.map((m) => {
              if (m.id === message_id) {
                // merge metadata into existing message metadata
                const newMeta = Object.assign({}, m.metadata || {}, metadata);
                console.log(
                  `[DMChat] Merged metadata for message ${message_id}:`,
                  newMeta
                );
                return { ...m, metadata: newMeta };
              }
              return m;
            })
          );
        }
      } catch (e) {
        console.warn("[DMChat] Failed to parse SSE event:", e);
      }
    };

    es.onerror = (e) => {
      // If connection fails, close and rely on polling fallback in components
      try {
        es.close();
      } catch (e) {}
    };

    return () => {
      try {
        es.close();
      } catch (e) {}
    };
  }, [selectedSession && selectedSession.id]);

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
    setArchivedMessages([]); // Clear archived messages when switching sessions
    setShowHistory(false); // Reset history view
    setActiveCampaign(null);
    try {
      const r = await fetch(`/api/chat/sessions/${sessionId}`);
      if (!r.ok) throw new Error(`Failed to load session: ${r.status}`);
      const s = await r.json();
      setSelectedSession(s);

      // Show all messages - don't archive anything
      setMessages(s.messages || []);
      // Reset typing/completion readiness when switching sessions
      setReadyMessages({});
      // Clear any cached parsed actions or visible action panels from prior session
      setParsedActions({});
      setShowActions({});

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

    // Archive current messages before sending new one (keep only last pair visible)
    if (messages.length >= 2) {
      setArchivedMessages((prev) => [...prev, ...messages]);
      setMessages([]); // Clear active chat for new interaction
    }

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
        // Server will produce scene_image metadata (prompt/descriptors).
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

**CRITICAL FORMATTING RULES:**
1. NEVER include markdown tables (| --- |) in your narrative description
2. NEVER include bullet lists of action options in the narrative
3. Write the narrative as natural flowing prose only
4. After your narrative, provide 3-4 suggested actions in this exact format:

**Suggested Actions:**
- Action 1: [Description] (Skill check: [Skill] DC [Number])
- Action 2: [Description] (Attack roll or other check)
- Action 3: [Description] (No roll required)

Do NOT use markdown tables for actions. Use the bullet list format shown above.

**Please begin the adventure with the opening scene narration!**`;

      // Don't send initialization prompt as user message - it's internal context
      // The backend will handle party context and campaign details directly
      setSending(true);

      // Generate AI DM's opening narration using two-stage narrative pipeline
      // The backend loads party details and campaign metadata automatically
      const placeholderId = `pending-${Date.now()}`;
      const placeholder = {
        id: placeholderId,
        session_id: selectedSession.id,
        role: "assistant",
        content:
          "✨ Consulting the ancient tomes and weaving your adventure...",
        message_index: null,
        metadata: null,
        is_deleted: false,
        created_at: new Date().toISOString(),
        _optimistic: true,
      };
      setMessages((m) => [...m, placeholder]);
      setLoadingGen(true);

      // Use the standard generate endpoint which now includes campaign context
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
        // Server will populate `metadata.scene_image` (prompt/descriptors)
        // and the SceneImageDisplay will read it directly.
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
    // Roll results are now auto-sent to DM via onSendRollToDM
  };

  const handleSendRollToDM = async (rollMessage) => {
    setMessage(rollMessage);
    setDiceRollerOpen(false);
  };

  // Navigation items for the app drawer
  const navigationItems = [
    { label: "Home", path: "/", icon: <HomeIcon /> },
    { label: "Create", path: "/create", icon: <CreateIcon /> },
    { label: "References", path: "/references", icon: <MenuBookIcon /> },
    { label: "Stories", path: "/stories", icon: <AutoStoriesIcon /> },
    { label: "Characters", path: "/characters", icon: <PeopleIcon /> },
    { label: "Worlds", path: "/worlds", icon: <PublicIcon /> },
    { label: "Settings", path: "/settings", icon: <SettingsIcon /> },
  ];

  return (
    <Box
      sx={{
        display: "flex",
        flexDirection: "row",
        width: "100vw",
        height: "100vh",
        overflow: "hidden",
        bgcolor: "background.default",
        position: "fixed",
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
      }}
    >
      {/* Navigation Drawer */}
      <Drawer
        anchor="left"
        open={navDrawerOpen}
        onClose={() => setNavDrawerOpen(false)}
        sx={{
          zIndex: 1300,
          "& .MuiDrawer-paper": {
            width: 280,
            bgcolor: "background.paper",
          },
        }}
      >
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
            <MenuBookIcon />
            <Typography variant="h6">StoryCraft</Typography>
          </Stack>
          <IconButton
            onClick={() => setNavDrawerOpen(false)}
            sx={{ color: "white" }}
          >
            <ChevronLeftIcon />
          </IconButton>
        </Box>
        <Divider />
        <List>
          {navigationItems.map((item) => (
            <ListItem key={item.path} disablePadding>
              <ListItemButton
                component={Link}
                to={item.path}
                onClick={() => setNavDrawerOpen(false)}
              >
                <ListItemIcon>{item.icon}</ListItemIcon>
                <ListItemText primary={item.label} />
              </ListItemButton>
            </ListItem>
          ))}
        </List>
        <Divider sx={{ mt: "auto" }} />
        <Box sx={{ p: 2 }}>
          <Typography variant="caption" color="text.secondary">
            Campaign Mode Active
          </Typography>
          <Typography variant="body2" color="primary" fontWeight={600}>
            {activeCampaign?.title || "No Campaign"}
          </Typography>
        </Box>
      </Drawer>

      {/* History Drawer - Shows archived messages */}
      <Drawer
        anchor="right"
        open={showHistory}
        onClose={() => setShowHistory(false)}
        sx={{
          zIndex: 1250,
          "& .MuiDrawer-paper": {
            width: { xs: "100%", sm: 450, md: 500 },
            bgcolor: "background.paper",
          },
        }}
      >
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
            <HistoryIcon />
            <Typography variant="h6">Message History</Typography>
          </Stack>
          <IconButton
            onClick={() => setShowHistory(false)}
            sx={{ color: "white" }}
          >
            <ChevronRightIcon />
          </IconButton>
        </Box>
        <Divider />

        {archivedMessages.length === 0 ? (
          <Box sx={{ p: 4, textAlign: "center" }}>
            <HistoryIcon
              sx={{
                fontSize: 60,
                color: "text.secondary",
                mb: 2,
                opacity: 0.5,
              }}
            />
            <Typography variant="h6" color="text.secondary" gutterBottom>
              No Message History
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Previous messages will appear here when you send new messages
            </Typography>
          </Box>
        ) : (
          <Box sx={{ overflow: "auto", flexGrow: 1, p: 2 }}>
            <Typography
              variant="caption"
              color="text.secondary"
              sx={{ mb: 2, display: "block" }}
            >
              {archivedMessages.length} archived message
              {archivedMessages.length !== 1 ? "s" : ""}
            </Typography>
            <Stack spacing={1}>
              {archivedMessages.map((msg, idx) => (
                <Paper
                  key={msg.id || idx}
                  elevation={1}
                  sx={{
                    p: 1.5,
                    bgcolor:
                      msg.role === "assistant"
                        ? "rgba(185, 167, 0, 0.08)"
                        : "rgba(0, 0, 0, 0.2)",
                    borderLeft: "3px solid",
                    borderColor:
                      msg.role === "assistant"
                        ? "primary.main"
                        : "text.secondary",
                  }}
                >
                  <Stack direction="row" spacing={1} alignItems="flex-start">
                    <Avatar
                      sx={{
                        width: 24,
                        height: 24,
                        bgcolor:
                          msg.role === "assistant"
                            ? "#8b0000"
                            : "rgba(61, 47, 31, 0.85)",
                      }}
                    >
                      {msg.role === "assistant" ? (
                        <SmartToyIcon sx={{ fontSize: 14 }} />
                      ) : (
                        <PersonIcon sx={{ fontSize: 14 }} />
                      )}
                    </Avatar>
                    <Box sx={{ flexGrow: 1, minWidth: 0 }}>
                      <Typography
                        variant="caption"
                        color="text.secondary"
                        sx={{ display: "block", mb: 0.5 }}
                      >
                        {msg.role === "assistant" ? "DM" : "You"} •{" "}
                        {new Date(msg.created_at).toLocaleTimeString()}
                      </Typography>
                      <Typography
                        variant="body2"
                        sx={{
                          fontSize: "0.85rem",
                          whiteSpace: "pre-wrap",
                          wordBreak: "break-word",
                          overflow: "hidden",
                          textOverflow: "ellipsis",
                          display: "-webkit-box",
                          WebkitLineClamp: 3,
                          WebkitBoxOrient: "vertical",
                        }}
                      >
                        {msg.content}
                      </Typography>
                    </Box>
                  </Stack>
                </Paper>
              ))}
            </Stack>
          </Box>
        )}

        <Divider />
        <Box sx={{ p: 2 }}>
          <Button
            fullWidth
            variant="outlined"
            onClick={() => {
              // Restore all messages
              setMessages([...archivedMessages, ...messages]);
              setArchivedMessages([]);
              setShowHistory(false);
            }}
            disabled={archivedMessages.length === 0}
          >
            Restore All Messages
          </Button>
        </Box>
      </Drawer>

      {/* Floating Navigation Button */}
      <Fab
        color="primary"
        aria-label="navigation menu"
        onClick={() => setNavDrawerOpen(true)}
        sx={{
          position: "fixed",
          top: 16,
          left: 16,
          zIndex: 1200,
          boxShadow: 3,
        }}
      >
        <MenuIcon />
      </Fab>

      {/* LEFT: Settings Panel (Tabbed) - Anchored to left */}
      <Box
        sx={{
          width: 340,
          minWidth: 340,
          maxWidth: 340,
          flexShrink: 0,
          height: "100vh",
          position: "relative",
          zIndex: 1100,
        }}
      >
        <LeftSettingsPanel
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
          onCampaignSelect={(campaign) => setActiveCampaign(campaign)}
          onCreateCampaign={() => setCampaignWizardOpen(true)}
        />
      </Box>

      {/* Main Chat Area - Takes remaining space */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          display: "flex",
          flexDirection: "column",
          height: "100vh",
          overflow: "hidden",
          position: "relative",
          width: "auto",
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
            <AutoAwesomeIcon sx={{ mr: 1.5 }} />
            <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
              {selectedSession
                ? selectedSession.title || `Session ${selectedSession.id}`
                : "Dungeon Master Chat"}
            </Typography>
            {selectedSession && (
              <>
                <Tooltip title="View Message History">
                  <IconButton
                    onClick={() => setShowHistory(!showHistory)}
                    sx={{ color: "white", mr: 1 }}
                  >
                    <Badge
                      badgeContent={archivedMessages.length}
                      color="secondary"
                    >
                      <HistoryIcon />
                    </Badge>
                  </IconButton>
                </Tooltip>
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
                {!activeCampaign ? (
                  <Tooltip title="Create Campaign">
                    <Button
                      variant="contained"
                      color="secondary"
                      size="small"
                      startIcon={<CampaignIcon />}
                      onClick={() => setCampaignWizardOpen(true)}
                      sx={{ mr: 2 }}
                    >
                      Create Campaign
                    </Button>
                  </Tooltip>
                ) : (
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
                    <Tooltip title="Campaign Journal">
                      <IconButton
                        onClick={() => setJournalOpen(true)}
                        sx={{ color: "white", mr: 1, ml: 1 }}
                      >
                        <MenuBookIcon />
                      </IconButton>
                    </Tooltip>
                    <Tooltip
                      title={
                        rightPanelOpen ? "Hide Party Panel" : "Show Party Panel"
                      }
                    >
                      <IconButton
                        onClick={() => setRightPanelOpen(!rightPanelOpen)}
                        sx={{ color: "white", mr: 1 }}
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
            sx={{ mx: 2, mt: 1, flexShrink: 0 }}
          >
            {error}
          </Alert>
        )}

        {/* Content Area - No scrolling, fixed height */}
        {selectedSession ? (
          <Box
            sx={{
              display: "flex",
              flexGrow: 1,
              overflow: "hidden", // No scroll on outer container
              position: "relative",
              minHeight: 0, // Important for flex overflow
            }}
          >
            {messages.length === 0 ? (
              <Box
                sx={{
                  flexGrow: 1,
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
                  <Typography variant="body1" color="text.secondary" paragraph>
                    {activeCampaign
                      ? "Your campaign is ready! Start your adventure by sending a message below."
                      : "Create a campaign to begin your adventure"}
                  </Typography>
                  {!activeCampaign && (
                    <Button
                      variant="contained"
                      color="secondary"
                      size="large"
                      startIcon={<CampaignIcon />}
                      onClick={() => setCampaignWizardOpen(true)}
                      sx={{ mt: 2 }}
                    >
                      Create Campaign
                    </Button>
                  )}
                </Box>
              </Box>
            ) : (
              <Box
                sx={{
                  flexGrow: 1,
                  overflow: "auto",
                  px: { xs: 2, sm: 3, md: 4 }, // Responsive padding
                  pt: 3, // Top padding to prevent overlap with header
                  pb: 2,
                  display: "flex",
                  flexDirection: "column",
                  width: "100%", // Use full available width
                }}
              >
                <Stack spacing={1.5} sx={{ pt: 4, pb: 2 }}>
                  {messages.map((msg) => (
                    <React.Fragment key={msg.id || msg._tempId}>
                      <CinematicMessageCard
                        message={msg}
                        isUser={msg.role !== "assistant"}
                        sceneImage={null} // Will be populated by SceneImageDisplay
                        ttsPlaying={false} // Not needed with simplified UX
                        ttsAutoPlay={ttsAutoPlay}
                        ttsReady={false} // Not needed with simplified UX
                        onTypingProgress={handleTypingProgress} // Auto-scroll during typing
                        onTypingComplete={(id) =>
                          handleMessageTypingCompleteEnhanced(id)
                        }
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
                            // Construct a formatted message for the action
                            let actionMessage = action;

                            // If the action doesn't start with "I", make it first-person
                            if (!action.toLowerCase().startsWith("i ")) {
                              actionMessage = `I ${action
                                .charAt(0)
                                .toLowerCase()}${action.slice(1)}`;
                            }

                            // Add roll and DC info if present
                            if (roll) {
                              actionMessage += `\n\nSuggested roll: ${roll}`;
                            }
                            if (dc) {
                              actionMessage += `\nDC: ${dc}`;
                            }

                            setMessage(actionMessage);
                          }
                        }}
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
                                messageMetadata={msg.metadata}
                                typingReady={!!readyMessages[msg.id]}
                                // Prefer client-side computed hint (scene_image_hint) if available,
                                // otherwise fall back to any prompt cached in message metadata.
                                locationHint={
                                  msg.scene_image_hint ||
                                  (msg.metadata &&
                                    msg.metadata.scene_image &&
                                    msg.metadata.scene_image.prompt) ||
                                  null
                                }
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
                                sx={{
                                  bgcolor: "rgba(255,255,255,0.1)",
                                  borderRadius: 1,
                                  p: 1,
                                }}
                              />
                            </Box>
                          )}

                        {/* Dialogue Narration Player */}
                        {msg.role === "assistant" &&
                          ttsEnabled &&
                          msg.id &&
                          !msg._optimistic && (
                            <DialogueNarrationPlayer
                              sessionId={selectedSession.id}
                              messageId={msg.id}
                              messageContent={msg.content}
                              enabled={true}
                            />
                          )}

                        {/* Source Citations (still shown immediately) */}
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

                      {/* Reveal action chips only after typing animation completes for this message */}
                      {msg.role === "assistant" && msg.content && msg.id && (
                        <Box sx={{ mt: 1 }}>
                          {/* If actions are parsed and message is ready, show a reveal button */}
                          {readyMessages[msg.id] &&
                            parsedActions[msg.id] &&
                            parsedActions[msg.id].length > 0 && (
                              <Box sx={{ display: "flex", gap: 1, mb: 1 }}>
                                {!showActions[msg.id] ? (
                                  <Button
                                    size="small"
                                    variant="outlined"
                                    onClick={() => {
                                      // reveal and dispatch event for other listeners
                                      setShowActions((prev) => ({
                                        ...prev,
                                        [msg.id]: true,
                                      }));
                                      try {
                                        const ev = new CustomEvent(
                                          "storycraft.actionsReady",
                                          {
                                            detail: {
                                              messageId: msg.id,
                                              actions: parsedActions[msg.id],
                                              rawContent: msg.content,
                                            },
                                          }
                                        );
                                        window.dispatchEvent(ev);
                                      } catch (e) {
                                        console.debug(
                                          "Failed dispatching actionsReady:",
                                          e
                                        );
                                      }
                                    }}
                                  >
                                    Show Actions ({parsedActions[msg.id].length}
                                    )
                                  </Button>
                                ) : (
                                  <Button
                                    size="small"
                                    variant="text"
                                    onClick={() =>
                                      setShowActions((prev) => ({
                                        ...prev,
                                        [msg.id]: false,
                                      }))
                                    }
                                  >
                                    Hide Actions
                                  </Button>
                                )}
                              </Box>
                            )}

                          {/* Render the chips only when user has revealed them */}
                          {showActions[msg.id] && (
                            <Fade in timeout={250}>
                              <Box>
                                <ActionChipsParser
                                  content={msg.content}
                                  onActionClick={(action, roll, dc) => {
                                    const hasAbilityCheck =
                                      roll && /d\d+/.test(roll.toLowerCase());

                                    if (
                                      hasAbilityCheck &&
                                      availableCharacters.length > 0
                                    ) {
                                      // Open contextual dice roller and auto-roll using the first available character
                                      openContextualRoll({
                                        rollStr: roll,
                                        skillName: null,
                                        characterId: availableCharacters[0].id,
                                        autoRoll: true,
                                      });
                                    } else {
                                      let actionMessage = action;
                                      if (
                                        !action.toLowerCase().startsWith("i ")
                                      ) {
                                        actionMessage = `I ${action
                                          .charAt(0)
                                          .toLowerCase()}${action.slice(1)}`;
                                      }
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
                            </Fade>
                          )}
                        </Box>
                      )}
                    </React.Fragment>
                  ))}
                  <div ref={bottomRef} />
                </Stack>
              </Box>
            )}

            {/* Right Column - Party/Combat Panel (Anchored to right) */}
            {activeCampaign && (
              <Paper
                elevation={0}
                sx={{
                  width: rightPanelOpen
                    ? { xs: "100%", sm: 360, md: 370, lg: 380 }
                    : 0,
                  minWidth: rightPanelOpen
                    ? { xs: "100%", sm: 360, md: 370, lg: 380 }
                    : 0,
                  maxWidth: rightPanelOpen
                    ? { xs: "100%", sm: 360, md: 370, lg: 380 }
                    : 0,
                  flexShrink: 0,
                  height: "100vh",
                  borderLeft: rightPanelOpen ? "1px solid" : "none",
                  borderColor: "divider",
                  bgcolor: "background.paper",
                  display: "flex",
                  flexDirection: "column",
                  overflow: "hidden",
                  transition:
                    "width 0.3s ease-in-out, min-width 0.3s ease-in-out",
                  position: "relative",
                  zIndex: 1100,
                }}
              >
                {/* Panel Tabs */}
                <Box
                  sx={{
                    p: 1,
                    borderBottom: 1,
                    borderColor: "divider",
                    opacity: rightPanelOpen ? 1 : 0,
                    flexShrink: 0,
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
                <Box sx={{ flexGrow: 1, overflow: "auto", minHeight: 0 }}>
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
                <Box
                  sx={{
                    p: 2,
                    borderTop: 1,
                    borderColor: "divider",
                    flexShrink: 0,
                  }}
                >
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
        ) : (
          // Welcome screen when no session is selected
          <Box
            sx={{
              flexGrow: 1,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              textAlign: "center",
              px: 4,
            }}
          >
            <Box sx={{ maxWidth: 600 }}>
              <AutoAwesomeIcon
                sx={{
                  fontSize: 120,
                  color: "secondary.main",
                  mb: 3,
                  opacity: 0.8,
                }}
              />
              <Typography
                variant="h3"
                color="primary"
                gutterBottom
                fontWeight={600}
              >
                Welcome, Dungeon Master
              </Typography>
              <Typography variant="h6" color="text.secondary" paragraph>
                Your epic adventure awaits!
              </Typography>
              <Typography
                variant="body1"
                color="text.secondary"
                paragraph
                sx={{ mb: 4 }}
              >
                Use the settings panel on the left to configure your AI model,
                voice narration, and other preferences. Once you're ready,
                create a new session to begin your storytelling journey!
              </Typography>

              <Stack direction="row" spacing={2} justifyContent="center">
                <Button
                  variant="contained"
                  color="primary"
                  size="large"
                  startIcon={<AddIcon />}
                  onClick={createSession}
                  disabled={creating}
                >
                  {creating ? "Creating..." : "Create Session"}
                </Button>
                <Button
                  variant="outlined"
                  color="secondary"
                  size="large"
                  startIcon={<CampaignIcon />}
                  onClick={() => {
                    // Create a session first, then open campaign wizard
                    if (!creating) {
                      createSession();
                      // Wait a moment for session to be created, then open wizard
                      setTimeout(() => setCampaignWizardOpen(true), 500);
                    }
                  }}
                  disabled={creating}
                >
                  Create Campaign
                </Button>
              </Stack>
            </Box>
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
          onClose={() => {
            setDiceRollerOpen(false);
            setContextualRoll(null);
          }}
          onRollComplete={handleDiceRoll}
          activeCharacters={availableCharacters.filter((c) =>
            activeCharacters.includes(c.id)
          )}
          onSendRollToDM={handleSendRollToDM}
          initialDice={contextualRoll?.dice}
          initialCount={contextualRoll?.count}
          initialModifier={contextualRoll?.modifier}
          initialCharacter={contextualRoll?.character}
          initialSkillName={contextualRoll?.skillName}
          autoRollOnOpen={!!contextualRoll?.autoRoll}
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

        {/* Campaign Journal */}
        <CampaignJournal
          campaignId={activeCampaign?.id}
          open={journalOpen}
          onClose={() => setJournalOpen(false)}
        />
      </Box>
    </Box>
  );
}
