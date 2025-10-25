import React, { useState, useEffect } from "react";
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Stepper,
  Step,
  StepLabel,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Box,
  Typography,
  Card,
  CardContent,
  CardMedia,
  Avatar,
  Chip,
  Checkbox,
  FormControlLabel,
  Alert,
  AlertTitle,
  Stack,
  Grid,
  CircularProgress,
  Pagination,
  Collapse,
} from "@mui/material";
import {
  Campaign as CampaignIcon,
  AutoAwesome,
  Groups as PartyIcon,
  Settings as SettingsIcon,
  Check as CheckIcon,
} from "@mui/icons-material";
import { API_URL } from "../config/api";

/**
 * CampaignSetupWizard - 4-step wizard to create a D&D campaign
 * Step 1: Campaign Details (title, description, setting, difficulty, type)
 * Step 2: Choose Adventure Template & Opening Scene
 * Step 3: Select Party Members (multi-select D&D characters)
 * Step 4: Review & Create
 */
const CampaignSetupWizard = ({
  open,
  onClose,
  onCampaignCreated,
  chatSessionId,
}) => {
  const [activeStep, setActiveStep] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Campaign mode: "premade" or "custom"
  const [campaignMode, setCampaignMode] = useState(null);
  const [premadeCampaigns, setPremadeCampaigns] = useState([]);
  const [loadingPremade, setLoadingPremade] = useState(false);
  const [premadePage, setPremadePage] = useState(0);
  const [showAllPremade, setShowAllPremade] = useState(false);
  const CAMPAIGNS_PER_PAGE = 6;

  // Campaign details
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [setting, setSetting] = useState("Forgotten Realms");
  const [difficulty, setDifficulty] = useState("Normal");
  const [campaignType, setCampaignType] = useState("short_adventure");
  const [startingLevel, setStartingLevel] = useState(1);

  // Adventure template & opening
  const [selectedTemplate, setSelectedTemplate] = useState(null);
  const [selectedOpening, setSelectedOpening] = useState("tavern_meeting");
  const [campaignTone, setCampaignTone] = useState("heroic_fantasy");
  const [loadingTemplates, setLoadingTemplates] = useState(false);
  const [availableTemplates, setAvailableTemplates] = useState([]);

  // Party selection
  const [availableCharacters, setAvailableCharacters] = useState([]);
  const [selectedCharacterIds, setSelectedCharacterIds] = useState([]);
  const [loadingCharacters, setLoadingCharacters] = useState(false);

  const steps = [
    "Campaign Details",
    "Adventure Template",
    "Select Party",
    "Review & Create",
  ];

  const campaignTypes = [
    {
      value: "one_shot",
      label: "One-Shot",
      description: "Single session adventure (2-4 hours)",
    },
    {
      value: "short_adventure",
      label: "Short Adventure",
      description: "Multi-session story (3-6 sessions)",
    },
    {
      value: "epic_campaign",
      label: "Epic Campaign",
      description: "Long-running campaign (20+ sessions)",
    },
  ];

  const settings = [
    "Forgotten Realms",
    "Eberron",
    "Greyhawk",
    "Ravenloft",
    "Dragonlance",
    "Homebrew",
    "Other",
  ];

  const difficulties = ["Easy", "Normal", "Hard", "Deadly"];

  // Adventure Templates
  const adventureTemplates = {
    one_shot: [
      {
        id: "haunted_manor",
        title: "The Haunted Manor",
        description: "Investigate a cursed nobleman's estate plagued by undead",
        level: "1-3",
        type: "Mystery/Horror",
        icon: "🏚️",
      },
      {
        id: "goblin_raiders",
        title: "The Goblin Raiders",
        description: "Track and defeat goblins who kidnapped villagers",
        level: "1-2",
        type: "Combat/Rescue",
        icon: "⚔️",
      },
      {
        id: "custom",
        title: "Custom One-Shot",
        description:
          "AI DM will create a unique adventure based on your preferences",
        level: "Any",
        type: "Custom",
        icon: "✨",
      },
    ],
    short_adventure: [
      {
        id: "cult_crimson_eye",
        title: "The Cult of the Crimson Eye",
        description: "Uncover and stop a sinister cult's blood moon ritual",
        level: "3-5",
        type: "Investigation/Mystery",
        icon: "👁️",
      },
      {
        id: "lost_mine",
        title: "The Lost Mine",
        description: "Classic adventure to find a legendary lost mine",
        level: "1-5",
        type: "Classic D&D",
        icon: "⛏️",
      },
      {
        id: "custom",
        title: "Custom Short Adventure",
        description: "AI DM will create a multi-session adventure",
        level: "Any",
        type: "Custom",
        icon: "✨",
      },
    ],
    epic_campaign: [
      {
        id: "tyranny_dragons",
        title: "Tyranny of Dragons",
        description: "Epic dragon-themed campaign to stop Tiamat's summoning",
        level: "1-15",
        type: "World-Threat",
        icon: "🐉",
      },
      {
        id: "custom",
        title: "Custom Epic Campaign",
        description: "AI DM will craft a long-running epic adventure",
        level: "Any",
        type: "Custom",
        icon: "✨",
      },
    ],
  };

  // Opening Scenes
  const openingScenes = [
    {
      id: "tavern_meeting",
      title: "The Tavern Meeting",
      description: "Strangers meet in a cozy tavern as adventure calls",
      icon: "🍺",
      preview:
        "The warm glow of the hearth illuminates worn wooden tables as travelers from distant lands find themselves sharing space...",
    },
    {
      id: "caravan_guards",
      title: "The Caravan Guards",
      description: "Hired as guards, bonds form during travel",
      icon: "🐴",
      preview:
        "The morning sun rises over the dusty trade road as your caravan prepares for another day's journey...",
    },
    {
      id: "prison_break",
      title: "Prison Break",
      description: "Imprisoned heroes must escape and clear their names",
      icon: "⛓️",
      preview:
        "Cold stone. The drip of water. The rattle of chains. You awaken in darkness...",
    },
    {
      id: "festival_disaster",
      title: "The Festival Disaster",
      description: "Celebration turns to chaos requiring heroes",
      icon: "🎪",
      preview:
        "The festival fills the town square with music and laughter. Then, the screaming begins...",
    },
    {
      id: "mysterious_summons",
      title: "The Summons",
      description: "Each character receives a mysterious message",
      icon: "✉️",
      preview:
        "The letter arrived three days ago, sealed with an unfamiliar sigil. It knew your name...",
    },
  ];

  // Campaign Tones
  const campaignTones = [
    {
      id: "heroic_fantasy",
      title: "Heroic High Fantasy",
      description: "Clear good vs evil, epic quests",
      icon: "🦸",
    },
    {
      id: "dark_fantasy",
      title: "Gritty Dark Fantasy",
      description: "Morally grey, survival-focused",
      icon: "🌑",
    },
    {
      id: "political",
      title: "Political Intrigue",
      description: "Court politics and diplomacy",
      icon: "👑",
    },
    {
      id: "mystery",
      title: "Mystery & Investigation",
      description: "Solve crimes and uncover secrets",
      icon: "🔍",
    },
    {
      id: "horror",
      title: "Horror & Dread",
      description: "Atmosphere of fear and cosmic horror",
      icon: "👻",
    },
    {
      id: "comedy",
      title: "Lighthearted Comedy",
      description: "Fun and silly adventures",
      icon: "😄",
    },
  ];

  // Load available D&D characters
  useEffect(() => {
    if (open && activeStep === 2) {
      loadCharacters();
    }
  }, [open, activeStep]);

  // Load premade campaigns when wizard opens
  useEffect(() => {
    if (open && activeStep === 0 && !campaignMode) {
      loadPremadeCampaigns();
    }
  }, [open, activeStep, campaignMode]);

  // Load adventure templates when wizard opens or campaign type changes
  useEffect(() => {
    if (open && activeStep === 1) {
      loadAdventureTemplates();
    }
  }, [open, activeStep, campaignType]);

  const loadPremadeCampaigns = async () => {
    setLoadingPremade(true);
    try {
      const response = await fetch(`${API_URL}/api/adventures/templates`);
      if (response.ok) {
        const data = await response.json();

        // Deduplicate campaigns by id
        const uniqueCampaigns = [];
        const seenIds = new Set();

        for (const campaign of data.templates || []) {
          if (!seenIds.has(campaign.id)) {
            seenIds.add(campaign.id);
            uniqueCampaigns.push(campaign);
          }
        }

        setPremadeCampaigns(uniqueCampaigns);
      }
    } catch (err) {
      console.error("Error loading premade campaigns:", err);
    } finally {
      setLoadingPremade(false);
    }
  };

  const loadAdventureTemplates = async () => {
    setLoadingTemplates(true);
    try {
      const response = await fetch(
        `${API_URL}/api/adventures/templates?campaign_type=${campaignType}`
      );
      if (response.ok) {
        const data = await response.json();
        setAvailableTemplates(data.templates || []);
      }
    } catch (err) {
      console.error("Error loading adventure templates:", err);
      setError("Failed to load adventure templates");
    } finally {
      setLoadingTemplates(false);
    }
  };

  const loadCharacters = async () => {
    setLoadingCharacters(true);
    try {
      const response = await fetch(
        `${API_URL}/api/characters/?exclude_portraits=false`
      );
      if (response.ok) {
        const data = await response.json();
        // Filter for D&D characters only
        const dndCharacters = data.filter((char) => char.is_dnd);
        setAvailableCharacters(dndCharacters);
      }
    } catch (err) {
      console.error("Error loading characters:", err);
      setError("Failed to load characters");
    } finally {
      setLoadingCharacters(false);
    }
  };

  const handleNext = () => {
    if (activeStep === 0 && !campaignMode) {
      setError(
        "Please choose to create a custom campaign or select a premade adventure"
      );
      return;
    }
    if (activeStep === 0 && !title.trim()) {
      setError("Campaign title is required");
      return;
    }
    if (activeStep === 1 && !selectedTemplate) {
      setError("Please select an adventure template");
      return;
    }
    if (activeStep === 2 && selectedCharacterIds.length === 0) {
      setError("Please select at least one character for your party");
      return;
    }
    setError(null);
    setActiveStep((prev) => prev + 1);
  };

  const handleBack = () => {
    setError(null);
    if (activeStep === 1 && campaignMode === "premade") {
      // If going back from step 1 on a premade, reset mode selection
      setCampaignMode(null);
      setActiveStep(0);
    } else if (activeStep === 0 && campaignMode) {
      // If on step 0 with mode selected, go back to mode selection
      setCampaignMode(null);
    } else {
      setActiveStep((prev) => prev - 1);
    }
  };

  const toggleCharacter = (characterId) => {
    setSelectedCharacterIds((prev) => {
      if (prev.includes(characterId)) {
        return prev.filter((id) => id !== characterId);
      } else {
        return [...prev, characterId];
      }
    });
  };

  const handleSelectPremade = (template) => {
    setTitle(template.title);
    setDescription(template.description);

    // Parse level range to set starting level
    if (template.level_range && template.level_range.includes("-")) {
      const startLevel = parseInt(template.level_range.split("-")[0]);
      setStartingLevel(startLevel);
    }

    // Set campaign type
    setCampaignType(template.campaign_type);

    // Set setting if available
    if (template.setting) {
      setSetting(template.setting);
    }

    // Set selected template for step 1
    setSelectedTemplate(template.id);

    // Set mode and move to next step
    setCampaignMode("premade");
    setActiveStep(1);
  };

  const handleCreateCustom = () => {
    setCampaignMode("custom");
  };

  const handleCreate = async () => {
    setLoading(true);
    setError(null);

    try {
      // Prepare enhanced description with template metadata
      const templateMetadata = {
        template_id: selectedTemplate,
        opening_scene: selectedOpening,
        campaign_tone: campaignTone,
        user_description: description,
      };

      const enhancedDescription = description
        ? `${description}\n\n[AI_DM_METADATA: ${JSON.stringify(
            templateMetadata
          )}]`
        : `[AI_DM_METADATA: ${JSON.stringify(templateMetadata)}]`;

      // Create campaign
      const campaignResponse = await fetch(`${API_URL}/api/campaigns/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          title,
          description: enhancedDescription,
          setting,
          difficulty,
          campaign_type: campaignType,
          starting_level: startingLevel,
          chat_session_id: chatSessionId,
        }),
      });

      if (!campaignResponse.ok) {
        throw new Error("Failed to create campaign");
      }

      const campaign = await campaignResponse.json();

      // Add characters to party
      for (const characterId of selectedCharacterIds) {
        await fetch(`${API_URL}/api/campaigns/${campaign.id}/party/add`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ character_id: characterId }),
        });
      }

      // Success!
      onCampaignCreated && onCampaignCreated(campaign);
      handleClose();
    } catch (err) {
      console.error("Error creating campaign:", err);
      setError(err.message || "Failed to create campaign");
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    if (!loading) {
      setActiveStep(0);
      setCampaignMode(null);
      setPremadePage(0);
      setShowAllPremade(false);
      setTitle("");
      setDescription("");
      setSelectedCharacterIds([]);
      setSelectedTemplate(null);
      setError(null);
      onClose();
    }
  };

  const renderStepContent = () => {
    switch (activeStep) {
      case 0:
        // If no mode selected yet, show choice screen
        if (!campaignMode) {
          return (
            <Stack spacing={3}>
              <Alert severity="info" icon={<AutoAwesome />}>
                <AlertTitle>
                  <strong>Choose Your Path</strong>
                </AlertTitle>
                <Typography variant="body2">
                  Start with a curated adventure from our library, or create
                  your own custom campaign from scratch.
                </Typography>
              </Alert>

              {/* Premade Campaigns Section */}
              <Box>
                <Typography variant="h6" gutterBottom>
                  📚 Premade Campaigns ({premadeCampaigns.length})
                </Typography>
                <Typography
                  variant="body2"
                  color="text.secondary"
                  sx={{ mb: 2 }}
                >
                  Choose from professionally crafted adventures, official D&D
                  modules, and AI-generated content
                </Typography>

                {loadingPremade ? (
                  <Box
                    sx={{ display: "flex", justifyContent: "center", py: 4 }}
                  >
                    <CircularProgress />
                  </Box>
                ) : premadeCampaigns.length === 0 ? (
                  <Alert severity="info">
                    No premade campaigns found. Try creating a custom campaign!
                  </Alert>
                ) : (
                  <>
                    <Grid container spacing={2}>
                      {premadeCampaigns
                        .slice(
                          premadePage * CAMPAIGNS_PER_PAGE,
                          (premadePage + 1) * CAMPAIGNS_PER_PAGE
                        )
                        .map((campaign) => {
                          const sourceIcons = {
                            guild_modules: "📚",
                            generated: "✨",
                            homebrew: "🎨",
                          };
                          const sourceLabels = {
                            guild_modules: "Official Module",
                            generated: "AI Generated",
                            homebrew: "Homebrew",
                          };

                          return (
                            <Grid key={campaign.id} size={{ xs: 12, sm: 6 }}>
                              <Card
                                sx={{
                                  cursor: "pointer",
                                  transition: "all 0.2s",
                                  height: "100%",
                                  "&:hover": {
                                    transform: "translateY(-4px)",
                                    boxShadow: 6,
                                  },
                                }}
                                onClick={() => handleSelectPremade(campaign)}
                              >
                                <CardContent>
                                  <Box
                                    sx={{
                                      display: "flex",
                                      alignItems: "center",
                                      mb: 1,
                                    }}
                                  >
                                    <Typography variant="h3" sx={{ mr: 1 }}>
                                      {sourceIcons[campaign.source] || "🎲"}
                                    </Typography>
                                    <Box sx={{ flex: 1 }}>
                                      <Typography
                                        variant="h6"
                                        component="div"
                                        sx={{ fontSize: "1rem" }}
                                      >
                                        {campaign.title}
                                      </Typography>
                                      <Typography
                                        variant="caption"
                                        color="text.secondary"
                                      >
                                        {sourceLabels[campaign.source]} • Levels{" "}
                                        {campaign.level_range}
                                      </Typography>
                                    </Box>
                                  </Box>
                                  <Typography
                                    variant="body2"
                                    color="text.secondary"
                                    sx={{
                                      mb: 1,
                                      overflow: "hidden",
                                      textOverflow: "ellipsis",
                                      display: "-webkit-box",
                                      WebkitLineClamp: 3,
                                      WebkitBoxOrient: "vertical",
                                    }}
                                  >
                                    {campaign.description}
                                  </Typography>
                                  {campaign.themes &&
                                    campaign.themes.length > 0 && (
                                      <Box
                                        sx={{
                                          display: "flex",
                                          gap: 0.5,
                                          flexWrap: "wrap",
                                          mt: 1,
                                        }}
                                      >
                                        {campaign.themes
                                          .slice(0, 3)
                                          .map((theme, idx) => (
                                            <Chip
                                              key={idx}
                                              label={theme}
                                              size="small"
                                              sx={{
                                                fontSize: "0.7rem",
                                                height: "20px",
                                              }}
                                            />
                                          ))}
                                      </Box>
                                    )}
                                </CardContent>
                              </Card>
                            </Grid>
                          );
                        })}
                    </Grid>

                    {/* Pagination Controls */}
                    {premadeCampaigns.length > CAMPAIGNS_PER_PAGE && (
                      <Box
                        sx={{
                          display: "flex",
                          justifyContent: "center",
                          alignItems: "center",
                          mt: 3,
                          gap: 2,
                        }}
                      >
                        <Pagination
                          count={Math.ceil(
                            premadeCampaigns.length / CAMPAIGNS_PER_PAGE
                          )}
                          page={premadePage + 1}
                          onChange={(e, page) => setPremadePage(page - 1)}
                          color="primary"
                          showFirstButton
                          showLastButton
                        />
                        <Typography variant="caption" color="text.secondary">
                          Showing {premadePage * CAMPAIGNS_PER_PAGE + 1}-
                          {Math.min(
                            (premadePage + 1) * CAMPAIGNS_PER_PAGE,
                            premadeCampaigns.length
                          )}{" "}
                          of {premadeCampaigns.length} campaigns
                        </Typography>
                      </Box>
                    )}
                  </>
                )}
              </Box>

              {/* Divider */}
              <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
                <Box sx={{ flex: 1, height: "1px", bgcolor: "divider" }} />
                <Typography variant="body2" color="text.secondary">
                  OR
                </Typography>
                <Box sx={{ flex: 1, height: "1px", bgcolor: "divider" }} />
              </Box>

              {/* Custom Campaign Option */}
              <Card
                sx={{
                  cursor: "pointer",
                  border: 2,
                  borderColor: "primary.main",
                  transition: "all 0.2s",
                  "&:hover": {
                    transform: "translateY(-2px)",
                    boxShadow: 4,
                  },
                }}
                onClick={handleCreateCustom}
              >
                <CardContent>
                  <Box sx={{ display: "flex", alignItems: "center", mb: 1 }}>
                    <Typography variant="h3" sx={{ mr: 2 }}>
                      ✨
                    </Typography>
                    <Box>
                      <Typography variant="h6">
                        Create Custom Campaign
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Build your own adventure from scratch with full
                        customization
                      </Typography>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Stack>
          );
        }

        // If mode is selected, show campaign details form
        return (
          <Stack spacing={3}>
            <Alert severity="info">
              <Typography variant="body2">
                {campaignMode === "premade"
                  ? "Review and customize your selected campaign"
                  : "Fill in the details for your custom campaign"}
              </Typography>
            </Alert>

            <TextField
              label="Campaign Title"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              fullWidth
              required
              placeholder="e.g., The Lost Mines of Phandelver"
            />

            <TextField
              label="Description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              fullWidth
              multiline
              rows={3}
              placeholder="Describe your campaign's story, setting, and themes..."
            />

            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <FormControl fullWidth>
                  <InputLabel>Campaign Type</InputLabel>
                  <Select
                    value={campaignType}
                    label="Campaign Type"
                    onChange={(e) => setCampaignType(e.target.value)}
                  >
                    {campaignTypes.map((type) => (
                      <MenuItem key={type.value} value={type.value}>
                        <Box>
                          <Typography variant="body2">{type.label}</Typography>
                          <Typography variant="caption" color="text.secondary">
                            {type.description}
                          </Typography>
                        </Box>
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>

              <Grid item xs={12} md={6}>
                <FormControl fullWidth>
                  <InputLabel>Setting</InputLabel>
                  <Select
                    value={setting}
                    label="Setting"
                    onChange={(e) => setSetting(e.target.value)}
                  >
                    {settings.map((s) => (
                      <MenuItem key={s} value={s}>
                        {s}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>

              <Grid item xs={12} md={6}>
                <FormControl fullWidth>
                  <InputLabel>Difficulty</InputLabel>
                  <Select
                    value={difficulty}
                    label="Difficulty"
                    onChange={(e) => setDifficulty(e.target.value)}
                  >
                    {difficulties.map((d) => (
                      <MenuItem key={d} value={d}>
                        {d}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>

              <Grid item xs={12} md={6}>
                <TextField
                  label="Starting Level"
                  type="number"
                  value={startingLevel}
                  onChange={(e) =>
                    setStartingLevel(parseInt(e.target.value) || 1)
                  }
                  fullWidth
                  inputProps={{ min: 1, max: 20 }}
                />
              </Grid>
            </Grid>
          </Stack>
        );

      case 1:
        // Adventure Template & Opening Scene Selection
        const selectedOpeningObj = openingScenes.find(
          (s) => s.id === selectedOpening
        );

        // Helper to get icon for template
        const getTemplateIcon = (template) => {
          const sourceIcons = {
            guild_modules: "📚",
            generated: "✨",
            homebrew: "🎨",
          };
          return sourceIcons[template.source] || "🎲";
        };

        // Helper to get source label
        const getSourceLabel = (source) => {
          const labels = {
            guild_modules: "Official Module",
            generated: "AI Generated",
            homebrew: "Homebrew",
          };
          return labels[source] || source;
        };

        return (
          <Stack spacing={4}>
            {/* AI DM Confirmation Box */}
            <Alert severity="info" icon={<AutoAwesome />}>
              <AlertTitle>
                <strong>Your AI Dungeon Master Awaits</strong>
              </AlertTitle>
              <Typography variant="body2">
                Choose from {availableTemplates.length} curated adventures! Your
                AI Dungeon Master will use your selection to craft an epic
                campaign tailored to your party.
              </Typography>
            </Alert>

            {/* Adventure Template Selection */}
            <Box>
              <Typography variant="h6" gutterBottom>
                Choose Your Adventure
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                {loadingTemplates
                  ? "Loading adventures from the library..."
                  : `${
                      availableTemplates.length
                    } adventures available for ${campaignType.replace(
                      "_",
                      " "
                    )}`}
              </Typography>

              {loadingTemplates ? (
                <Box sx={{ display: "flex", justifyContent: "center", py: 4 }}>
                  <CircularProgress />
                </Box>
              ) : availableTemplates.length === 0 ? (
                <Alert severity="info">
                  No adventures found. The AI DM will create a custom adventure
                  for you!
                </Alert>
              ) : (
                <Grid container spacing={2}>
                  {availableTemplates.map((template) => (
                    <Grid key={template.id} size={{ xs: 12, sm: 6, md: 4 }}>
                      <Card
                        sx={{
                          cursor: "pointer",
                          border: 2,
                          borderColor:
                            selectedTemplate === template.id
                              ? "primary.main"
                              : "transparent",
                          transition: "all 0.2s",
                          height: "100%",
                          "&:hover": {
                            transform: "translateY(-2px)",
                            boxShadow: 4,
                          },
                        }}
                        onClick={() => setSelectedTemplate(template.id)}
                      >
                        <CardContent>
                          <Box
                            sx={{
                              display: "flex",
                              alignItems: "center",
                              mb: 1,
                            }}
                          >
                            <Typography variant="h3" sx={{ mr: 1 }}>
                              {getTemplateIcon(template)}
                            </Typography>
                            <Box sx={{ flex: 1 }}>
                              <Typography
                                variant="h6"
                                component="div"
                                sx={{ fontSize: "0.95rem" }}
                              >
                                {template.title}
                              </Typography>
                              <Typography
                                variant="caption"
                                color="text.secondary"
                              >
                                {getSourceLabel(template.source)} • Levels{" "}
                                {template.level_range}
                              </Typography>
                            </Box>
                          </Box>
                          <Typography
                            variant="body2"
                            color="text.secondary"
                            sx={{ mb: 1 }}
                          >
                            {template.description}
                          </Typography>
                          {template.themes && template.themes.length > 0 && (
                            <Box
                              sx={{
                                display: "flex",
                                gap: 0.5,
                                flexWrap: "wrap",
                                mt: 1,
                              }}
                            >
                              {template.themes.slice(0, 3).map((theme, idx) => (
                                <Chip
                                  key={idx}
                                  label={theme}
                                  size="small"
                                  sx={{ fontSize: "0.7rem", height: "20px" }}
                                />
                              ))}
                            </Box>
                          )}
                        </CardContent>
                      </Card>
                    </Grid>
                  ))}
                </Grid>
              )}
            </Box>

            {/* Opening Scene Selection */}
            <Box>
              <Typography variant="h6" gutterBottom>
                Choose Your Opening Scene
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                How will your party first come together?
              </Typography>

              <Grid container spacing={2}>
                {openingScenes.map((scene) => (
                  <Grid key={scene.id} size={{ xs: 12, sm: 6 }}>
                    <Card
                      sx={{
                        cursor: "pointer",
                        border: 2,
                        borderColor:
                          selectedOpening === scene.id
                            ? "primary.main"
                            : "transparent",
                        transition: "all 0.2s",
                        "&:hover": {
                          transform: "translateY(-2px)",
                          boxShadow: 4,
                        },
                      }}
                      onClick={() => setSelectedOpening(scene.id)}
                    >
                      <CardContent>
                        <Box
                          sx={{ display: "flex", alignItems: "center", mb: 1 }}
                        >
                          <Typography variant="h4" sx={{ mr: 1 }}>
                            {scene.icon}
                          </Typography>
                          <Typography variant="h6">{scene.title}</Typography>
                        </Box>
                        <Typography
                          variant="body2"
                          color="text.secondary"
                          sx={{ mb: 1 }}
                        >
                          {scene.description}
                        </Typography>
                        {selectedOpening === scene.id && (
                          <Typography
                            variant="body2"
                            sx={{
                              fontStyle: "italic",
                              color: "text.secondary",
                              mt: 1,
                              p: 1,
                              bgcolor: "action.hover",
                              borderRadius: 1,
                            }}
                          >
                            "{scene.preview}"
                          </Typography>
                        )}
                      </CardContent>
                    </Card>
                  </Grid>
                ))}
              </Grid>
            </Box>

            {/* Campaign Tone Selection */}
            <Box>
              <Typography variant="h6" gutterBottom>
                Set the Campaign Tone
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                What atmosphere should your adventure have?
              </Typography>

              <Grid container spacing={2}>
                {campaignTones.map((tone) => (
                  <Grid key={tone.id} size={{ xs: 12, sm: 6, md: 4 }}>
                    <Card
                      sx={{
                        cursor: "pointer",
                        border: 2,
                        borderColor:
                          campaignTone === tone.id
                            ? "primary.main"
                            : "transparent",
                        transition: "all 0.2s",
                        "&:hover": {
                          transform: "translateY(-2px)",
                          boxShadow: 4,
                        },
                      }}
                      onClick={() => setCampaignTone(tone.id)}
                    >
                      <CardContent>
                        <Box
                          sx={{ display: "flex", alignItems: "center", mb: 1 }}
                        >
                          <Typography variant="h4" sx={{ mr: 1 }}>
                            {tone.icon}
                          </Typography>
                          <Typography variant="subtitle1">
                            {tone.title}
                          </Typography>
                        </Box>
                        <Typography variant="body2" color="text.secondary">
                          {tone.description}
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                ))}
              </Grid>
            </Box>
          </Stack>
        );

      case 2:
        return (
          <Box>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              Select the characters who will join this adventure. Only D&D
              characters can be added to campaigns.
            </Typography>

            {loadingCharacters ? (
              <Box sx={{ display: "flex", justifyContent: "center", py: 4 }}>
                <CircularProgress />
              </Box>
            ) : availableCharacters.length === 0 ? (
              <Alert severity="info" sx={{ mt: 2 }}>
                No D&D characters found. Please create D&D characters first.
              </Alert>
            ) : (
              <Grid container spacing={2} sx={{ mt: 1 }}>
                {availableCharacters.map((character) => {
                  const isSelected = selectedCharacterIds.includes(
                    character.id
                  );

                  return (
                    <Grid key={character.id} size={{ xs: 12, sm: 6, md: 4 }}>
                      <Card
                        sx={{
                          cursor: "pointer",
                          border: 2,
                          borderColor: isSelected
                            ? "primary.main"
                            : "transparent",
                          transition: "all 0.2s",
                          "&:hover": {
                            transform: "translateY(-2px)",
                            boxShadow: 4,
                          },
                        }}
                        onClick={() => toggleCharacter(character.id)}
                      >
                        {character.portrait_image ? (
                          <CardMedia
                            component="img"
                            height="160"
                            image={`data:image/png;base64,${character.portrait_image}`}
                            alt={character.name}
                            sx={{ objectFit: "contain" }}
                          />
                        ) : (
                          <Box
                            sx={{
                              height: 160,
                              display: "flex",
                              alignItems: "center",
                              justifyContent: "center",
                              bgcolor: "action.hover",
                            }}
                          >
                            <Avatar sx={{ width: 80, height: 80 }}>
                              {character.name.charAt(0)}
                            </Avatar>
                          </Box>
                        )}

                        <CardContent>
                          <Box
                            sx={{
                              display: "flex",
                              alignItems: "center",
                              gap: 1,
                              mb: 1,
                            }}
                          >
                            <Checkbox
                              checked={isSelected}
                              onChange={() => toggleCharacter(character.id)}
                              onClick={(e) => e.stopPropagation()}
                            />
                            <Typography variant="subtitle2" noWrap>
                              {character.name}
                            </Typography>
                          </Box>

                          <Typography variant="body2" color="text.secondary">
                            {character.dnd_species} {character.dnd_class}{" "}
                            {character.dnd_level}
                          </Typography>

                          <Box
                            sx={{
                              display: "flex",
                              gap: 0.5,
                              mt: 1,
                              flexWrap: "wrap",
                            }}
                          >
                            <Chip
                              label={`HP ${
                                character.dnd_hit_points_max ||
                                character.dnd_hit_points ||
                                0
                              }`}
                              size="small"
                            />
                            <Chip
                              label={`AC ${character.dnd_armor_class || 10}`}
                              size="small"
                            />
                          </Box>
                        </CardContent>
                      </Card>
                    </Grid>
                  );
                })}
              </Grid>
            )}
          </Box>
        );

      case 3:
        const selectedChars = availableCharacters.filter((c) =>
          selectedCharacterIds.includes(c.id)
        );
        const currentTemplatesReview =
          adventureTemplates[campaignType] || adventureTemplates.one_shot;
        const selectedTemplateReview = currentTemplatesReview.find(
          (t) => t.id === selectedTemplate
        );
        const selectedOpeningReview = openingScenes.find(
          (s) => s.id === selectedOpening
        );
        const selectedToneReview = campaignTones.find(
          (t) => t.id === campaignTone
        );

        return (
          <Stack spacing={3}>
            <Alert severity="success" icon={<CheckIcon />}>
              Review your campaign details before creating
            </Alert>

            {/* AI DM Confirmation */}
            <Alert severity="info" icon={<AutoAwesome />}>
              <AlertTitle>
                <strong>Your AI Dungeon Master is Ready!</strong>
              </AlertTitle>
              <Typography variant="body2">
                Based on your selections, the AI DM will create a custom
                campaign experience. Your adventure will begin with the{" "}
                <strong>{selectedOpeningReview?.title}</strong> and follow the{" "}
                <strong>{selectedTemplateReview?.title}</strong> template in a{" "}
                <strong>{selectedToneReview?.title}</strong> style.
              </Typography>
            </Alert>

            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  {title}
                </Typography>
                <Typography variant="body2" color="text.secondary" paragraph>
                  {description || "No description"}
                </Typography>

                <Grid container spacing={2}>
                  <Grid item xs={6}>
                    <Typography variant="caption" color="text.secondary">
                      Type
                    </Typography>
                    <Typography variant="body2">
                      {
                        campaignTypes.find((t) => t.value === campaignType)
                          ?.label
                      }
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="caption" color="text.secondary">
                      Setting
                    </Typography>
                    <Typography variant="body2">{setting}</Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="caption" color="text.secondary">
                      Difficulty
                    </Typography>
                    <Typography variant="body2">{difficulty}</Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="caption" color="text.secondary">
                      Starting Level
                    </Typography>
                    <Typography variant="body2">
                      Level {startingLevel}
                    </Typography>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>

            {/* Adventure Template Info */}
            <Card variant="outlined">
              <CardContent>
                <Typography variant="subtitle2" gutterBottom>
                  Adventure Details
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={12}>
                    <Typography variant="caption" color="text.secondary">
                      Template
                    </Typography>
                    <Box
                      sx={{ display: "flex", alignItems: "center", mt: 0.5 }}
                    >
                      <Typography variant="h5" sx={{ mr: 1 }}>
                        {selectedTemplateReview?.icon}
                      </Typography>
                      <Box>
                        <Typography variant="body2">
                          {selectedTemplateReview?.title}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {selectedTemplateReview?.description}
                        </Typography>
                      </Box>
                    </Box>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="caption" color="text.secondary">
                      Opening Scene
                    </Typography>
                    <Box
                      sx={{ display: "flex", alignItems: "center", mt: 0.5 }}
                    >
                      <Typography variant="h6" sx={{ mr: 1 }}>
                        {selectedOpeningReview?.icon}
                      </Typography>
                      <Typography variant="body2">
                        {selectedOpeningReview?.title}
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="caption" color="text.secondary">
                      Campaign Tone
                    </Typography>
                    <Box
                      sx={{ display: "flex", alignItems: "center", mt: 0.5 }}
                    >
                      <Typography variant="h6" sx={{ mr: 1 }}>
                        {selectedToneReview?.icon}
                      </Typography>
                      <Typography variant="body2">
                        {selectedToneReview?.title}
                      </Typography>
                    </Box>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>

            <Box>
              <Typography variant="subtitle2" gutterBottom>
                Party Members ({selectedChars.length})
              </Typography>
              <Stack spacing={1}>
                {selectedChars.map((char) => (
                  <Card key={char.id} variant="outlined">
                    <CardContent
                      sx={{
                        display: "flex",
                        alignItems: "center",
                        gap: 2,
                        p: 2,
                        "&:last-child": { pb: 2 },
                      }}
                    >
                      <Avatar
                        src={
                          char.portrait_image
                            ? `data:image/png;base64,${char.portrait_image}`
                            : null
                        }
                        sx={{ width: 40, height: 40 }}
                      >
                        {char.name.charAt(0)}
                      </Avatar>
                      <Box sx={{ flex: 1 }}>
                        <Typography variant="subtitle2">{char.name}</Typography>
                        <Typography variant="caption" color="text.secondary">
                          {char.dnd_species} {char.dnd_class} {char.dnd_level}
                        </Typography>
                      </Box>
                      <Chip
                        label={`${
                          char.dnd_hit_points_max || char.dnd_hit_points || 0
                        } HP`}
                        size="small"
                      />
                    </CardContent>
                  </Card>
                ))}
              </Stack>
            </Box>
          </Stack>
        );

      default:
        return null;
    }
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="md" fullWidth>
      <DialogTitle>
        <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
          <CampaignIcon />
          <Typography variant="h6">Create New Campaign</Typography>
        </Box>
      </DialogTitle>

      <DialogContent>
        <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
          {steps.map((label) => (
            <Step key={label}>
              <StepLabel>{label}</StepLabel>
            </Step>
          ))}
        </Stepper>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
            {error}
          </Alert>
        )}

        {renderStepContent()}
      </DialogContent>

      <DialogActions>
        <Button onClick={handleClose} disabled={loading}>
          Cancel
        </Button>
        {(activeStep > 0 || campaignMode) && (
          <Button onClick={handleBack} disabled={loading}>
            Back
          </Button>
        )}
        {activeStep < steps.length - 1 ? (
          <Button onClick={handleNext} variant="contained">
            Next
          </Button>
        ) : (
          <Button onClick={handleCreate} variant="contained" disabled={loading}>
            {loading ? "Creating..." : "Create Campaign"}
          </Button>
        )}
      </DialogActions>
    </Dialog>
  );
};

export default CampaignSetupWizard;
