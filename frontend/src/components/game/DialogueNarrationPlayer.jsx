/**
 * DialogueNarrationPlayer - Sequential dialogue playback with voice assignment
 *
 * Extracts dialogue from DM responses and plays them sequentially with
 * appropriate male/female voices for immersive storytelling.
 *
 * Features:
 * - Automatic dialogue extraction
 * - Gender detection for voice assignment
 * - Sequential playback
 * - Pre-loading with manual trigger
 */

import React, { useState, useEffect, useRef } from "react";
import {
  Box,
  Button,
  IconButton,
  LinearProgress,
  Typography,
  Chip,
  Stack,
  Tooltip,
  Paper,
} from "@mui/material";
import {
  PlayArrow as PlayIcon,
  Pause as PauseIcon,
  Stop as StopIcon,
  SkipNext as SkipIcon,
  RecordVoiceOver as VoiceIcon,
} from "@mui/icons-material";
import axios from "axios";
import { API_URL } from "../../config/api";

const API_BASE = `${API_URL}/api`;

/**
 * Extract dialogue from text with speaker detection
 * Returns array of: { text, speaker, gender }
 */
function extractDialogue(content) {
  const dialogues = [];

  // Pattern for quoted dialogue with optional speaker attribution
  // Matches: "dialogue text" or "dialogue text," said John
  const dialoguePattern =
    /"([^"]+)"(?:\s*,?\s*(?:said|says|asks|asked|replies|replied|shouts|shouted|whispers|whispered|mutters|muttered)\s+([^.!?]+))?/gi;

  let match;
  while ((match = dialoguePattern.exec(content)) !== null) {
    const text = match[1].trim();
    const speaker = match[2] ? match[2].trim() : "Unknown Speaker";

    // Detect gender from speaker name or context
    const gender = detectGender(speaker, text);

    dialogues.push({
      text,
      speaker,
      gender,
      voice: gender === "male" ? "leo" : "leah", // Default voices
    });
  }

  return dialogues;
}

/**
 * Detect gender from speaker name and context
 */
function detectGender(speaker, text) {
  const speakerLower = speaker.toLowerCase();

  // Male indicators
  const maleNames = [
    "he",
    "him",
    "his",
    "man",
    "boy",
    "king",
    "prince",
    "lord",
    "sir",
    "baron",
    "duke",
  ];
  const femaleNames = [
    "she",
    "her",
    "woman",
    "girl",
    "queen",
    "princess",
    "lady",
    "dame",
    "baroness",
    "duchess",
  ];

  // Check speaker name
  if (maleNames.some((name) => speakerLower.includes(name))) {
    return "male";
  }
  if (femaleNames.some((name) => speakerLower.includes(name))) {
    return "female";
  }

  // Check context around dialogue
  const contextBefore = text.substring(Math.max(0, text.length - 100));
  if (maleNames.some((name) => contextBefore.toLowerCase().includes(name))) {
    return "male";
  }
  if (femaleNames.some((name) => contextBefore.toLowerCase().includes(name))) {
    return "female";
  }

  // Default to female (DM narrator voice)
  return "female";
}

function DialogueNarrationPlayer({
  sessionId,
  messageId,
  messageContent,
  enabled = true,
  onComplete,
}) {
  const [dialogues, setDialogues] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [loading, setLoading] = useState(false);
  const [audioCache, setAudioCache] = useState({});
  const [preloading, setPreloading] = useState(false);

  const audioRef = useRef(null);

  // Extract dialogues on mount
  useEffect(() => {
    if (enabled && messageContent) {
      const extracted = extractDialogue(messageContent);
      console.log(`[Dialogue] Extracted ${extracted.length} dialogue snippets`);
      setDialogues(extracted);
    }
  }, [messageContent, enabled]);

  // Preload all dialogue audio
  const preloadAllDialogues = async () => {
    if (dialogues.length === 0) return;

    setPreloading(true);
    const newCache = {};

    for (let i = 0; i < dialogues.length; i++) {
      const dialogue = dialogues[i];
      const cacheKey = `${i}_${dialogue.voice}`;

      try {
        console.log(
          `[Dialogue] Preloading ${i + 1}/${
            dialogues.length
          }: "${dialogue.text.substring(0, 30)}..."`
        );

        const response = await axios.post(
          `${API_BASE}/tts/dialogue`,
          {
            text: dialogue.text,
            voice: dialogue.voice,
          },
          {
            responseType: "blob",
          }
        );

        const url = URL.createObjectURL(response.data);
        newCache[cacheKey] = url;
      } catch (err) {
        console.error(`[Dialogue] Failed to preload dialogue ${i}:`, err);
      }
    }

    setAudioCache(newCache);
    setPreloading(false);
    console.log(
      `[Dialogue] Preloaded ${Object.keys(newCache).length} dialogue clips`
    );
  };

  // Play current dialogue
  const playDialogue = (index) => {
    if (!dialogues[index]) return;

    const dialogue = dialogues[index];
    const cacheKey = `${index}_${dialogue.voice}`;
    const audioUrl = audioCache[cacheKey];

    if (!audioUrl) {
      console.error(`[Dialogue] No cached audio for index ${index}`);
      return;
    }

    if (audioRef.current) {
      audioRef.current.src = audioUrl;
      audioRef.current.play();
      setIsPlaying(true);
    }
  };

  // Handle audio ended - move to next dialogue
  const handleAudioEnded = () => {
    if (currentIndex < dialogues.length - 1) {
      const nextIndex = currentIndex + 1;
      setCurrentIndex(nextIndex);
      playDialogue(nextIndex);
    } else {
      setIsPlaying(false);
      setCurrentIndex(0);
      if (onComplete) {
        onComplete();
      }
    }
  };

  // Start sequential playback
  const handlePlay = () => {
    if (Object.keys(audioCache).length === 0) {
      console.log("[Dialogue] No cached audio, preloading first...");
      preloadAllDialogues().then(() => {
        playDialogue(0);
      });
    } else {
      playDialogue(currentIndex);
    }
  };

  const handlePause = () => {
    if (audioRef.current) {
      audioRef.current.pause();
      setIsPlaying(false);
    }
  };

  const handleStop = () => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
    }
    setIsPlaying(false);
    setCurrentIndex(0);
  };

  const handleSkip = () => {
    if (currentIndex < dialogues.length - 1) {
      const nextIndex = currentIndex + 1;
      setCurrentIndex(nextIndex);
      if (isPlaying) {
        playDialogue(nextIndex);
      }
    }
  };

  // Don't render if no dialogues found
  if (!enabled || dialogues.length === 0) {
    return null;
  }

  const currentDialogue = dialogues[currentIndex];
  const hasPreloaded = Object.keys(audioCache).length > 0;

  return (
    <Paper
      elevation={2}
      sx={{
        p: 1.5,
        bgcolor: "rgba(61, 47, 31, 0.6)",
        border: "1px solid rgba(185, 167, 0, 0.3)",
        borderRadius: 2,
        mt: 1,
      }}
    >
      <audio
        ref={audioRef}
        onEnded={handleAudioEnded}
        style={{ display: "none" }}
      />

      <Stack spacing={1.5}>
        {/* Header */}
        <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
          <VoiceIcon sx={{ color: "primary.main", fontSize: 20 }} />
          <Typography variant="body2" sx={{ flex: 1, fontWeight: 600 }}>
            Scene Dialogue ({dialogues.length} clips)
          </Typography>
          {!hasPreloaded && (
            <Button
              size="small"
              variant="outlined"
              startIcon={<VoiceIcon />}
              onClick={preloadAllDialogues}
              disabled={preloading}
              sx={{ textTransform: "none" }}
            >
              {preloading ? "Loading..." : "Load Dialogue"}
            </Button>
          )}
        </Box>

        {/* Preloading progress */}
        {preloading && <LinearProgress sx={{ borderRadius: 1 }} />}

        {/* Current dialogue info */}
        {hasPreloaded && currentDialogue && (
          <Box>
            <Stack direction="row" spacing={1} sx={{ mb: 0.5 }}>
              <Chip
                label={`${currentIndex + 1}/${dialogues.length}`}
                size="small"
                color="primary"
              />
              <Chip
                label={currentDialogue.speaker}
                size="small"
                variant="outlined"
              />
              <Chip
                label={currentDialogue.gender}
                size="small"
                color={currentDialogue.gender === "male" ? "info" : "secondary"}
              />
            </Stack>
            <Typography
              variant="body2"
              sx={{
                fontStyle: "italic",
                color: "text.secondary",
                fontSize: "0.85rem",
              }}
            >
              "{currentDialogue.text.substring(0, 80)}
              {currentDialogue.text.length > 80 ? "..." : ""}"
            </Typography>
          </Box>
        )}

        {/* Playback controls */}
        {hasPreloaded && (
          <Box sx={{ display: "flex", gap: 0.5, justifyContent: "center" }}>
            {!isPlaying ? (
              <Tooltip title="Play Dialogue">
                <IconButton onClick={handlePlay} color="primary" size="small">
                  <PlayIcon />
                </IconButton>
              </Tooltip>
            ) : (
              <Tooltip title="Pause">
                <IconButton onClick={handlePause} color="warning" size="small">
                  <PauseIcon />
                </IconButton>
              </Tooltip>
            )}

            <Tooltip title="Stop">
              <IconButton
                onClick={handleStop}
                color="error"
                size="small"
                disabled={!isPlaying}
              >
                <StopIcon />
              </IconButton>
            </Tooltip>

            <Tooltip title="Skip to Next">
              <IconButton
                onClick={handleSkip}
                size="small"
                disabled={currentIndex >= dialogues.length - 1}
              >
                <SkipIcon />
              </IconButton>
            </Tooltip>
          </Box>
        )}
      </Stack>
    </Paper>
  );
}

export default React.memo(DialogueNarrationPlayer);
