/**
 * GameSession Page - AI Dungeon Master Game Board
 *
 * Main container for the D&D game session interface with:
 * - DM chat panel for natural language interaction
 * - Combat tracker with initiative and HP
 * - Party status display
 * - Current scene description
 * - Action buttons for common actions
 * - Dice roller widget
 * - Event log
 */

import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import {
  Box,
  Container,
  Grid,
  Paper,
  Typography,
  Button,
  Alert,
  Snackbar,
  CircularProgress,
  Backdrop,
} from "@mui/material";
import {
  Casino as DiceIcon,
  SportsKabaddi as CombatIcon,
  Explore as ExploreIcon,
  People as PartyIcon,
  VolumeUp as VolumeUpIcon,
  VolumeOff as VolumeOffIcon,
} from "@mui/icons-material";

import { useGameSession } from "../hooks/useGameSession";
import DMChatPanel from "../components/game/DMChatPanel";
import CombatTracker from "../components/game/CombatTracker";
import PartyStatus from "../components/game/PartyStatus";
import SceneDisplay from "../components/game/SceneDisplay";
import ActionButtons from "../components/game/ActionButtons";
import DiceRoller from "../components/game/DiceRoller";
import EventLog from "../components/game/EventLog";

function GameSession() {
  const { gameId, chatId } = useParams();
  const navigate = useNavigate();

  const {
    gameSessionId,
    chatSessionId,
    messages,
    currentScene,
    combatState,
    partyStatus,
    eventLog,
    loading,
    error,
    isGenerating,
    isInCombat,
    currentTurnCombatant,
    createGameSession,
    loadGameSession,
    sendMessage,
    rollDice,
    processAttack,
    nextTurn,
    endCombat,
    startScene,
  } = useGameSession(gameId);

  const [showDiceRoller, setShowDiceRoller] = useState(false);
  const [showEventLog, setShowEventLog] = useState(false);
  const [ttsEnabled, setTtsEnabled] = useState(true);
  const [ttsAutoPlay, setTtsAutoPlay] = useState(false);
  const [snackbar, setSnackbar] = useState({
    open: false,
    message: "",
    severity: "info",
  });

  // Load game session on mount
  useEffect(() => {
    if (gameId && chatId) {
      loadGameSession(parseInt(gameId), parseInt(chatId)).catch((err) => {
        console.error("Failed to load game session:", err);
        setSnackbar({
          open: true,
          message: "Failed to load game session. Creating new session...",
          severity: "error",
        });
      });
    } else {
      // Create new game session if IDs not provided
      handleCreateNewSession();
    }
  }, [gameId, chatId]);

  const handleCreateNewSession = async () => {
    try {
      const { gameSessionId: newGameId, chatSessionId: newChatId } =
        await createGameSession(
          "New Adventure",
          [] // Start with empty party - can add members later
        );

      // Redirect to new session URL
      navigate(`/game/${newGameId}/${newChatId}`, { replace: true });

      setSnackbar({
        open: true,
        message: "New game session created! Start your adventure...",
        severity: "success",
      });
    } catch (err) {
      console.error("Failed to create game session:", err);
      setSnackbar({
        open: true,
        message: "Failed to create game session",
        severity: "error",
      });
    }
  };

  const handleSendMessage = async (message) => {
    try {
      await sendMessage(message);
    } catch (err) {
      console.error("Failed to send message:", err);
      setSnackbar({
        open: true,
        message: "Failed to send message to DM",
        severity: "error",
      });
    }
  };

  const handleRollDice = async (notation) => {
    try {
      const result = await rollDice(notation);
      setSnackbar({
        open: true,
        message: `🎲 Rolled ${notation}: ${result.total}`,
        severity: "info",
      });
      return result;
    } catch (err) {
      console.error("Failed to roll dice:", err);
      setSnackbar({
        open: true,
        message: "Failed to roll dice",
        severity: "error",
      });
    }
  };

  const handleAttack = async (targetName) => {
    if (!currentTurnCombatant) {
      setSnackbar({
        open: true,
        message: "No active combatant",
        severity: "warning",
      });
      return;
    }

    try {
      const result = await processAttack(
        currentTurnCombatant.name,
        targetName,
        currentTurnCombatant.attack_bonus || 5,
        currentTurnCombatant.damage_dice || "1d8+3"
      );

      setSnackbar({
        open: true,
        message: result.hit
          ? `💥 Hit! ${result.damage} damage`
          : `Miss! Rolled ${result.attack_roll}`,
        severity: result.hit ? "success" : "warning",
      });
    } catch (err) {
      console.error("Failed to process attack:", err);
      setSnackbar({
        open: true,
        message: "Failed to process attack",
        severity: "error",
      });
    }
  };

  const handleNextTurn = async () => {
    try {
      await nextTurn();
      setSnackbar({
        open: true,
        message: "Next turn",
        severity: "info",
      });
    } catch (err) {
      console.error("Failed to advance turn:", err);
      setSnackbar({
        open: true,
        message: "Failed to advance turn",
        severity: "error",
      });
    }
  };

  const handleEndCombat = async () => {
    try {
      await endCombat();
      setSnackbar({
        open: true,
        message: "Combat ended",
        severity: "success",
      });
    } catch (err) {
      console.error("Failed to end combat:", err);
      setSnackbar({
        open: true,
        message: "Failed to end combat",
        severity: "error",
      });
    }
  };

  const handleQuickAction = (actionType) => {
    switch (actionType) {
      case "explore":
        handleSendMessage("I look around and examine my surroundings");
        break;
      case "search":
        handleSendMessage("I search the area carefully");
        break;
      case "listen":
        handleSendMessage("I listen carefully for any sounds");
        break;
      case "talk":
        handleSendMessage("I try to start a conversation");
        break;
      case "attack":
        if (isInCombat) {
          handleSendMessage("I attack the nearest enemy");
        } else {
          setSnackbar({
            open: true,
            message: "Not in combat",
            severity: "warning",
          });
        }
        break;
      case "help":
        handleSendMessage("/status");
        break;
      default:
        break;
    }
  };

  if (loading && !gameSessionId) {
    return (
      <Backdrop
        open={true}
        sx={{ color: "#fff", zIndex: (theme) => theme.zIndex.drawer + 1 }}
      >
        <CircularProgress color="inherit" />
      </Backdrop>
    );
  }

  return (
    <Container maxWidth="xl" sx={{ py: 3 }}>
      {/* Header */}
      <Box
        sx={{
          mb: 3,
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
        }}
      >
        <Typography
          variant="h4"
          component="h1"
          sx={{ display: "flex", alignItems: "center", gap: 1 }}
        >
          <ExploreIcon /> AI Dungeon Master
        </Typography>
        <Box sx={{ display: "flex", gap: 2 }}>
          <Button
            variant={ttsEnabled ? "contained" : "outlined"}
            color={ttsEnabled ? "secondary" : "default"}
            startIcon={ttsEnabled ? <VolumeUpIcon /> : <VolumeOffIcon />}
            onClick={() => setTtsEnabled(!ttsEnabled)}
            title={ttsEnabled ? "Disable voice narration" : "Enable voice narration"}
          >
            Voice
          </Button>
          <Button
            variant="outlined"
            startIcon={<DiceIcon />}
            onClick={() => setShowDiceRoller(!showDiceRoller)}
          >
            Dice
          </Button>
          <Button
            variant="outlined"
            onClick={() => setShowEventLog(!showEventLog)}
          >
            Event Log
          </Button>
        </Box>
      </Box>

      {/* Error Alert */}
      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => {}}>
          {error}
        </Alert>
      )}

      {/* Main Game Board */}
      <Grid container spacing={2}>
        {/* Left Column - Scene & Actions */}
        <Grid item xs={12} md={8}>
          <Grid container spacing={2}>
            {/* Current Scene */}
            <Grid item xs={12}>
              <SceneDisplay scene={currentScene} isGenerating={isGenerating} />
            </Grid>

            {/* DM Chat Panel */}
            <Grid item xs={12}>
              <DMChatPanel
                messages={messages}
                onSendMessage={handleSendMessage}
                isGenerating={isGenerating}
                sessionId={chatSessionId}
                ttsEnabled={ttsEnabled}
                ttsAutoPlay={ttsAutoPlay}
              />
            </Grid>

            {/* Action Buttons */}
            <Grid item xs={12}>
              <ActionButtons
                onAction={handleQuickAction}
                isInCombat={isInCombat}
                disabled={isGenerating}
              />
            </Grid>
          </Grid>
        </Grid>

        {/* Right Column - Status & Combat */}
        <Grid item xs={12} md={4}>
          <Grid container spacing={2}>
            {/* Party Status */}
            <Grid item xs={12}>
              <PartyStatus partyStatus={partyStatus} isInCombat={isInCombat} />
            </Grid>

            {/* Combat Tracker (when in combat) */}
            {isInCombat && combatState && (
              <Grid item xs={12}>
                <CombatTracker
                  combatState={combatState}
                  currentTurnCombatant={currentTurnCombatant}
                  onAttack={handleAttack}
                  onNextTurn={handleNextTurn}
                  onEndCombat={handleEndCombat}
                />
              </Grid>
            )}

            {/* Dice Roller (collapsible) */}
            {showDiceRoller && (
              <Grid item xs={12}>
                <DiceRoller
                  onRoll={handleRollDice}
                  onClose={() => setShowDiceRoller(false)}
                />
              </Grid>
            )}

            {/* Event Log (collapsible) */}
            {showEventLog && (
              <Grid item xs={12}>
                <EventLog
                  events={eventLog}
                  onClose={() => setShowEventLog(false)}
                />
              </Grid>
            )}
          </Grid>
        </Grid>
      </Grid>

      {/* Snackbar for notifications */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={4000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
        anchorOrigin={{ vertical: "bottom", horizontal: "right" }}
      >
        <Alert
          severity={snackbar.severity}
          variant="filled"
          onClose={() => setSnackbar({ ...snackbar, open: false })}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Container>
  );
}

export default GameSession;
