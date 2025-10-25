import React, { useState, useEffect } from "react";
import {
  Box,
  Paper,
  Typography,
  Avatar,
  Chip,
  LinearProgress,
  IconButton,
  Tooltip,
  Badge,
  Divider,
  Card,
  CardContent,
  Stack,
} from "@mui/material";
import {
  Favorite as HeartIcon,
  Shield as ShieldIcon,
  Speed as SpeedIcon,
  Psychology as MindIcon,
  Close as CloseIcon,
  Warning as WarningIcon,
} from "@mui/icons-material";
import { API_URL } from "../config/api";

/**
 * PartyPanel - Display party members with real-time HP, resources, and status
 * Positioned as a left sidebar in DMChat for quick reference during gameplay
 */
const PartyPanel = ({ campaignId, onCharacterClick, onRemoveCharacter }) => {
  const [party, setParty] = useState([]);
  const [loading, setLoading] = useState(true);

  // Fetch party data
  useEffect(() => {
    const fetchParty = async () => {
      if (!campaignId) return;

      try {
        const response = await fetch(
          `${API_URL}/api/campaigns/${campaignId}/party`
        );
        if (response.ok) {
          const data = await response.json();
          setParty(data);
        }
      } catch (error) {
        console.error("Error fetching party:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchParty();

    // Poll every 5 seconds for updates during gameplay
    const interval = setInterval(fetchParty, 5000);
    return () => clearInterval(interval);
  }, [campaignId]);

  // Calculate HP percentage
  const getHpPercentage = (current, max) => {
    return (current / max) * 100;
  };

  // Get HP color based on percentage
  const getHpColor = (percentage) => {
    if (percentage > 75) return "success";
    if (percentage > 50) return "info";
    if (percentage > 25) return "warning";
    return "error";
  };

  // Get status badge color
  const getStatusColor = (status) => {
    switch (status) {
      case "active":
        return "success";
      case "unconscious":
        return "error";
      case "dead":
        return "default";
      default:
        return "info";
    }
  };

  if (loading) {
    return (
      <Paper sx={{ p: 2, height: "100%" }}>
        <Typography>Loading party...</Typography>
      </Paper>
    );
  }

  if (!party || party.length === 0) {
    return (
      <Paper sx={{ p: 2, height: "100%" }}>
        <Typography variant="h6" gutterBottom>
          ⚔️ Party
        </Typography>
        <Typography variant="body2" color="text.secondary">
          No characters in party yet
        </Typography>
      </Paper>
    );
  }

  return (
    <Paper
      sx={{ height: "100%", overflow: "auto", bgcolor: "background.default" }}
    >
      <Box sx={{ p: 2 }}>
        <Typography
          variant="h6"
          gutterBottom
          sx={{ display: "flex", alignItems: "center", gap: 1 }}
        >
          ⚔️ Party ({party.length})
        </Typography>

        <Stack spacing={2} sx={{ mt: 2 }}>
          {party.map((member) => {
            const hpPercentage = getHpPercentage(
              member.current_hp,
              member.max_hp
            );
            const hasConditions =
              member.conditions && member.conditions.length > 0;

            return (
              <Card
                key={member.character_id}
                sx={{
                  cursor: "pointer",
                  transition: "all 0.2s",
                  "&:hover": {
                    transform: "translateY(-2px)",
                    boxShadow: 4,
                  },
                  border: member.status !== "active" ? "2px solid" : "none",
                  borderColor:
                    member.status === "unconscious" ? "error.main" : "grey.700",
                }}
                onClick={() => onCharacterClick && onCharacterClick(member)}
              >
                <CardContent sx={{ p: 2, "&:last-child": { pb: 2 } }}>
                  <Box
                    sx={{ display: "flex", alignItems: "flex-start", gap: 1.5 }}
                  >
                    {/* Portrait */}
                    <Badge
                      badgeContent={member.position_in_initiative || null}
                      color="primary"
                      invisible={!member.position_in_initiative}
                    >
                      <Avatar
                        src={
                          member.portrait_image
                            ? `data:image/png;base64,${member.portrait_image}`
                            : null
                        }
                        sx={{ width: 56, height: 56 }}
                      >
                        {member.name.charAt(0)}
                      </Avatar>
                    </Badge>

                    {/* Character Info */}
                    <Box sx={{ flex: 1, minWidth: 0 }}>
                      <Box
                        sx={{
                          display: "flex",
                          justifyContent: "space-between",
                          alignItems: "flex-start",
                        }}
                      >
                        <Box>
                          <Typography variant="subtitle2" noWrap>
                            {member.name}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {member.dnd_species} {member.dnd_class}{" "}
                            {member.dnd_level}
                          </Typography>
                        </Box>

                        {onRemoveCharacter && (
                          <IconButton
                            size="small"
                            onClick={(e) => {
                              e.stopPropagation();
                              onRemoveCharacter(member.character_id);
                            }}
                          >
                            <CloseIcon fontSize="small" />
                          </IconButton>
                        )}
                      </Box>

                      {/* Status Badge */}
                      {member.status !== "active" && (
                        <Chip
                          label={member.status.toUpperCase()}
                          size="small"
                          color={getStatusColor(member.status)}
                          icon={<WarningIcon />}
                          sx={{ mt: 0.5 }}
                        />
                      )}

                      {/* HP Bar */}
                      <Box sx={{ mt: 1 }}>
                        <Box
                          sx={{
                            display: "flex",
                            justifyContent: "space-between",
                            mb: 0.5,
                          }}
                        >
                          <Typography
                            variant="caption"
                            sx={{
                              display: "flex",
                              alignItems: "center",
                              gap: 0.5,
                            }}
                          >
                            <HeartIcon sx={{ fontSize: 14 }} />
                            HP
                          </Typography>
                          <Typography variant="caption" fontWeight="bold">
                            {member.current_hp}/{member.max_hp}
                          </Typography>
                        </Box>
                        <LinearProgress
                          variant="determinate"
                          value={hpPercentage}
                          color={getHpColor(hpPercentage)}
                          sx={{ height: 8, borderRadius: 1 }}
                        />
                      </Box>

                      {/* Quick Stats */}
                      <Box
                        sx={{
                          display: "flex",
                          gap: 1,
                          mt: 1,
                          flexWrap: "wrap",
                        }}
                      >
                        <Tooltip title="Armor Class">
                          <Chip
                            size="small"
                            icon={<ShieldIcon />}
                            label={`AC ${member.armor_class || 10}`}
                            variant="outlined"
                          />
                        </Tooltip>

                        <Tooltip title="Initiative Modifier">
                          <Chip
                            size="small"
                            icon={<SpeedIcon />}
                            label={member.initiative || "+0"}
                            variant="outlined"
                          />
                        </Tooltip>

                        {member.spellcasting && (
                          <Tooltip
                            title={`Spell DC ${
                              member.spellcasting.dc || "N/A"
                            }`}
                          >
                            <Chip
                              size="small"
                              icon={<MindIcon />}
                              label={`DC ${member.spellcasting.dc || "?"}`}
                              variant="outlined"
                              color="secondary"
                            />
                          </Tooltip>
                        )}
                      </Box>

                      {/* Active Conditions */}
                      {hasConditions && (
                        <Box sx={{ mt: 1 }}>
                          <Stack direction="row" spacing={0.5} flexWrap="wrap">
                            {member.conditions.map((condition, idx) => (
                              <Chip
                                key={idx}
                                label={condition}
                                size="small"
                                color="warning"
                                sx={{ mb: 0.5 }}
                              />
                            ))}
                          </Stack>
                        </Box>
                      )}
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            );
          })}
        </Stack>
      </Box>
    </Paper>
  );
};

export default PartyPanel;
