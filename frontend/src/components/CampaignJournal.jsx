/**
 * CampaignJournal - Visual logger for campaign events, NPCs, decisions, and quests
 *
 * Features:
 * - Timeline view of journal entries
 * - NPC codex with portraits
 * - Quest log with progress
 * - Location tracker
 * - Decision history
 * - Integration with checkpoint system
 */

import React, { useState, useEffect } from "react";
import {
  Box,
  Drawer,
  Typography,
  IconButton,
  Tabs,
  Tab,
  Card,
  CardContent,
  CardMedia,
  Avatar,
  Chip,
  List,
  ListItem,
  ListItemAvatar,
  ListItemText,
  LinearProgress,
  Divider,
  Tooltip,
  Badge,
  Paper,
  ToggleButtonGroup,
  ToggleButton,
} from "@mui/material";
import {
  MenuBook as JournalIcon,
  Close as CloseIcon,
  Person as PersonIcon,
  Place as PlaceIcon,
  Assignment as QuestIcon,
  CompareArrows as DecisionIcon,
  Timeline as TimelineIcon,
  Star as StarIcon,
  StarBorder as StarBorderIcon,
  CheckCircle as CheckCircleIcon,
  AccessTime as InProgressIcon,
} from "@mui/icons-material";

const drawerWidth = 400;

export default function CampaignJournal({ campaignId, open, onClose }) {
  const [activeTab, setActiveTab] = useState(0);
  const [entries, setEntries] = useState([]);
  const [npcs, setNpcs] = useState([]);
  const [quests, setQuests] = useState([]);
  const [locations, setLocations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [importanceFilter, setImportanceFilter] = useState([1, 2, 3, 4, 5]);

  useEffect(() => {
    if (open && campaignId) {
      loadJournalData();
    }
  }, [open, campaignId]);

  const loadJournalData = async () => {
    setLoading(true);
    try {
      // Load all journal-related data
      const [entriesRes, npcsRes, questsRes] = await Promise.all([
        fetch(`/api/campaigns/${campaignId}/journal/entries`),
        fetch(`/api/campaigns/${campaignId}/npcs`),
        fetch(`/api/campaigns/${campaignId}/quests`),
      ]);

      if (entriesRes.ok) setEntries(await entriesRes.json());
      if (npcsRes.ok) setNpcs(await npcsRes.json());
      if (questsRes.ok) setQuests(await questsRes.json());

      // Extract unique locations from entries
      const locationSet = new Set();
      if (entriesRes.ok) {
        const entryData = await entriesRes.json();
        entryData.forEach((entry) => {
          if (entry.location_name) locationSet.add(entry.location_name);
        });
      }
      setLocations(Array.from(locationSet));
    } catch (error) {
      console.error("Failed to load journal data:", error);
    } finally {
      setLoading(false);
    }
  };

  const getImportanceIcon = (importance) => {
    const stars = [];
    for (let i = 0; i < 5; i++) {
      stars.push(
        i < importance ? (
          <StarIcon key={i} sx={{ fontSize: 16, color: "gold" }} />
        ) : (
          <StarBorderIcon key={i} sx={{ fontSize: 16, color: "grey.400" }} />
        )
      );
    }
    return <Box sx={{ display: "flex", gap: 0.25 }}>{stars}</Box>;
  };

  const getEntryIcon = (type) => {
    switch (type) {
      case "npc_met":
        return <PersonIcon />;
      case "location_visited":
        return <PlaceIcon />;
      case "quest_update":
        return <QuestIcon />;
      case "decision":
        return <DecisionIcon />;
      default:
        return <TimelineIcon />;
    }
  };

  const getEntryColor = (type) => {
    switch (type) {
      case "npc_met":
        return "primary";
      case "location_visited":
        return "secondary";
      case "quest_update":
        return "warning";
      case "decision":
        return "error";
      case "combat":
        return "error";
      case "loot":
        return "success";
      default:
        return "info";
    }
  };

  const formatDate = (isoString) => {
    return new Date(isoString).toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  const renderTimeline = () => {
    const filteredEntries = entries.filter((entry) =>
      importanceFilter.includes(entry.importance)
    );

    return (
      <Box sx={{ p: 2 }}>
        <Box sx={{ mb: 2 }}>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
            Filter by Importance:
          </Typography>
          <ToggleButtonGroup
            value={importanceFilter}
            onChange={(e, newFilter) => {
              if (newFilter.length > 0) setImportanceFilter(newFilter);
            }}
            aria-label="importance filter"
            size="small"
          >
            {[1, 2, 3, 4, 5].map((level) => (
              <ToggleButton key={level} value={level}>
                <StarIcon sx={{ fontSize: 16 }} />
                {level}
              </ToggleButton>
            ))}
          </ToggleButtonGroup>
        </Box>

        <List>
          {filteredEntries.map((entry, idx) => (
            <React.Fragment key={entry.id}>
              <ListItem alignItems="flex-start" sx={{ px: 0 }}>
                <ListItemAvatar>
                  <Avatar
                    sx={{
                      bgcolor: `${getEntryColor(entry.entry_type)}.main`,
                    }}
                  >
                    {getEntryIcon(entry.entry_type)}
                  </Avatar>
                </ListItemAvatar>
                <ListItemText
                  primary={
                    <Box
                      sx={{
                        display: "flex",
                        justifyContent: "space-between",
                        alignItems: "center",
                      }}
                    >
                      <Typography variant="subtitle2">{entry.title}</Typography>
                      {getImportanceIcon(entry.importance)}
                    </Box>
                  }
                  secondary={
                    <>
                      <Typography
                        variant="body2"
                        color="text.secondary"
                        sx={{ mb: 0.5 }}
                      >
                        {entry.description}
                      </Typography>
                      {entry.location_name && (
                        <Chip
                          icon={<PlaceIcon />}
                          label={entry.location_name}
                          size="small"
                          sx={{ mr: 0.5, mb: 0.5 }}
                        />
                      )}
                      {entry.tags &&
                        entry.tags.map((tag, i) => (
                          <Chip
                            key={i}
                            label={tag}
                            size="small"
                            variant="outlined"
                            sx={{ mr: 0.5, mb: 0.5 }}
                          />
                        ))}
                      <Typography variant="caption" color="text.disabled">
                        {formatDate(entry.created_at)}
                      </Typography>
                    </>
                  }
                />
              </ListItem>
              {idx < filteredEntries.length - 1 && <Divider variant="inset" />}
            </React.Fragment>
          ))}
        </List>

        {filteredEntries.length === 0 && (
          <Typography color="text.secondary" align="center" sx={{ py: 4 }}>
            No journal entries yet. Adventure awaits!
          </Typography>
        )}
      </Box>
    );
  };

  const renderNPCCodex = () => {
    return (
      <Box sx={{ p: 2 }}>
        <Typography variant="h6" gutterBottom>
          NPCs Encountered ({npcs.length})
        </Typography>

        {npcs.length === 0 ? (
          <Typography color="text.secondary" align="center" sx={{ py: 4 }}>
            No NPCs recorded yet.
          </Typography>
        ) : (
          <Box sx={{ display: "grid", gridTemplateColumns: "1fr", gap: 2 }}>
            {npcs.map((npc) => (
              <Card key={npc.id} variant="outlined">
                <Box sx={{ display: "flex" }}>
                  {npc.portrait_path ? (
                    <CardMedia
                      component="img"
                      sx={{ width: 120, objectFit: "cover" }}
                      image={`/static/${npc.portrait_path}`}
                      alt={npc.name}
                    />
                  ) : (
                    <Box
                      sx={{
                        width: 120,
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        bgcolor: "grey.800",
                      }}
                    >
                      <PersonIcon sx={{ fontSize: 64, color: "grey.600" }} />
                    </Box>
                  )}

                  <CardContent sx={{ flex: 1 }}>
                    <Box
                      sx={{
                        display: "flex",
                        justifyContent: "space-between",
                        alignItems: "flex-start",
                        mb: 1,
                      }}
                    >
                      <Typography variant="h6">{npc.name}</Typography>
                      {getImportanceIcon(npc.importance || 3)}
                    </Box>

                    {npc.role && (
                      <Chip
                        label={npc.role}
                        size="small"
                        color="primary"
                        sx={{ mb: 1 }}
                      />
                    )}

                    <Typography
                      variant="body2"
                      color="text.secondary"
                      sx={{
                        mb: 1,
                        display: "-webkit-box",
                        WebkitLineClamp: 2,
                        WebkitBoxOrient: "vertical",
                        overflow: "hidden",
                      }}
                    >
                      {npc.description}
                    </Typography>

                    {npc.location && (
                      <Typography variant="caption" color="text.disabled">
                        <PlaceIcon sx={{ fontSize: 14, mr: 0.5 }} />
                        {npc.location}
                      </Typography>
                    )}

                    {npc.first_met_location && (
                      <Typography
                        variant="caption"
                        color="text.disabled"
                        sx={{ display: "block", mt: 0.5 }}
                      >
                        First met: {npc.first_met_location}
                      </Typography>
                    )}

                    {npc.tags && npc.tags.length > 0 && (
                      <Box sx={{ mt: 1 }}>
                        {npc.tags.map((tag, i) => (
                          <Chip
                            key={i}
                            label={tag}
                            size="small"
                            variant="outlined"
                            sx={{ mr: 0.5, mt: 0.5 }}
                          />
                        ))}
                      </Box>
                    )}

                    {/* Relationship meter */}
                    {npc.relationship_to_party !== undefined && (
                      <Box sx={{ mt: 1 }}>
                        <Typography variant="caption" color="text.secondary">
                          Relationship:{" "}
                          {npc.relationship_to_party > 0 ? "+" : ""}
                          {npc.relationship_to_party}
                        </Typography>
                        <LinearProgress
                          variant="determinate"
                          value={
                            ((npc.relationship_to_party + 100) / 200) * 100
                          }
                          color={
                            npc.relationship_to_party > 50
                              ? "success"
                              : npc.relationship_to_party < -50
                              ? "error"
                              : "warning"
                          }
                          sx={{ mt: 0.5 }}
                        />
                      </Box>
                    )}
                  </CardContent>
                </Box>
              </Card>
            ))}
          </Box>
        )}
      </Box>
    );
  };

  const renderQuestLog = () => {
    const activeQuests = quests.filter((q) => q.status === "in_progress");
    const completedQuests = quests.filter((q) => q.status === "completed");
    const failedQuests = quests.filter((q) => q.status === "failed");

    return (
      <Box sx={{ p: 2 }}>
        {activeQuests.length > 0 && (
          <>
            <Typography variant="h6" gutterBottom>
              Active Quests ({activeQuests.length})
            </Typography>
            <List>
              {activeQuests.map((quest) => (
                <Card key={quest.id} variant="outlined" sx={{ mb: 2 }}>
                  <CardContent>
                    <Box sx={{ display: "flex", alignItems: "center", mb: 1 }}>
                      <InProgressIcon color="warning" sx={{ mr: 1 }} />
                      <Typography variant="h6">{quest.title}</Typography>
                    </Box>
                    <Typography variant="body2" color="text.secondary">
                      {quest.description}
                    </Typography>
                    {quest.reward && (
                      <Chip
                        label={`Reward: ${quest.reward}`}
                        size="small"
                        color="success"
                        sx={{ mt: 1 }}
                      />
                    )}
                  </CardContent>
                </Card>
              ))}
            </List>
          </>
        )}

        {completedQuests.length > 0 && (
          <>
            <Typography variant="h6" gutterBottom sx={{ mt: 2 }}>
              Completed Quests ({completedQuests.length})
            </Typography>
            <List>
              {completedQuests.map((quest) => (
                <ListItem key={quest.id} sx={{ px: 0 }}>
                  <ListItemAvatar>
                    <Avatar sx={{ bgcolor: "success.main" }}>
                      <CheckCircleIcon />
                    </Avatar>
                  </ListItemAvatar>
                  <ListItemText
                    primary={quest.title}
                    secondary={quest.description}
                  />
                </ListItem>
              ))}
            </List>
          </>
        )}

        {quests.length === 0 && (
          <Typography color="text.secondary" align="center" sx={{ py: 4 }}>
            No quests recorded yet.
          </Typography>
        )}
      </Box>
    );
  };

  const renderLocations = () => {
    return (
      <Box sx={{ p: 2 }}>
        <Typography variant="h6" gutterBottom>
          Locations Visited ({locations.length})
        </Typography>

        {locations.length === 0 ? (
          <Typography color="text.secondary" align="center" sx={{ py: 4 }}>
            No locations recorded yet.
          </Typography>
        ) : (
          <List>
            {locations.map((location, idx) => (
              <ListItem key={idx} sx={{ px: 0 }}>
                <ListItemAvatar>
                  <Avatar sx={{ bgcolor: "secondary.main" }}>
                    <PlaceIcon />
                  </Avatar>
                </ListItemAvatar>
                <ListItemText primary={location} />
              </ListItem>
            ))}
          </List>
        )}
      </Box>
    );
  };

  return (
    <Drawer
      anchor="right"
      open={open}
      onClose={onClose}
      sx={{
        "& .MuiDrawer-paper": {
          width: drawerWidth,
          boxSizing: "border-box",
        },
      }}
    >
      <Box
        sx={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          p: 2,
          borderBottom: 1,
          borderColor: "divider",
        }}
      >
        <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
          <JournalIcon color="primary" />
          <Typography variant="h6">Campaign Journal</Typography>
        </Box>
        <IconButton onClick={onClose} size="small">
          <CloseIcon />
        </IconButton>
      </Box>

      <Tabs
        value={activeTab}
        onChange={(e, v) => setActiveTab(v)}
        variant="fullWidth"
        sx={{ borderBottom: 1, borderColor: "divider" }}
      >
        <Tab icon={<TimelineIcon />} label="Timeline" />
        <Tab
          icon={<PersonIcon />}
          label={
            <Badge badgeContent={npcs.length} color="primary">
              NPCs
            </Badge>
          }
        />
        <Tab
          icon={<QuestIcon />}
          label={
            <Badge
              badgeContent={
                quests.filter((q) => q.status === "in_progress").length
              }
              color="warning"
            >
              Quests
            </Badge>
          }
        />
        <Tab icon={<PlaceIcon />} label="Locations" />
      </Tabs>

      <Box sx={{ overflow: "auto", flex: 1 }}>
        {activeTab === 0 && renderTimeline()}
        {activeTab === 1 && renderNPCCodex()}
        {activeTab === 2 && renderQuestLog()}
        {activeTab === 3 && renderLocations()}
      </Box>
    </Drawer>
  );
}
