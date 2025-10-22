/**
 * TTSAudioPlayer - Text-to-Speech Audio Player Component
 *
 * Features:
 * - Play/pause/stop controls
 * - Volume control
 * - Progress bar
 * - Auto-play option
 * - Loading states
 * - Voice selection
 */

import React, { useState, useRef, useEffect } from "react";
import {
  Box,
  IconButton,
  Slider,
  Typography,
  CircularProgress,
  Tooltip,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
} from "@mui/material";
import {
  PlayArrow as PlayIcon,
  Pause as PauseIcon,
  Stop as StopIcon,
  VolumeUp as VolumeIcon,
  VolumeOff as MuteIcon,
  RecordVoiceOver as VoiceIcon,
} from "@mui/icons-material";
import axios from "axios";

const API_BASE = "http://localhost:8000/api";

function TTSAudioPlayer({
  sessionId,
  messageId,
  autoPlay = false,
  showVoiceSelector = false,
  compact = false,
}) {
  const [isPlaying, setIsPlaying] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolume] = useState(0.8);
  const [isMuted, setIsMuted] = useState(false);
  const [selectedVoice, setSelectedVoice] = useState("tara");
  const [audioUrl, setAudioUrl] = useState(null);
  const [error, setError] = useState(null);

  const audioRef = useRef(null);

  const voices = [
    { value: "tara", label: "Tara (Female, Warm)" },
    { value: "leah", label: "Leah (Female, Clear)" },
    { value: "jess", label: "Jess (Female, Bright)" },
    { value: "leo", label: "Leo (Male, Deep)" },
    { value: "dan", label: "Dan (Male, Smooth)" },
    { value: "mia", label: "Mia (Female, Soft)" },
    { value: "zac", label: "Zac (Male, Strong)" },
    { value: "zoe", label: "Zoe (Female, Energetic)" },
  ];

  // Fetch and setup audio
  useEffect(() => {
    if (autoPlay && !audioUrl) {
      fetchAudio();
    }
  }, [autoPlay]);

  // Update audio element volume
  useEffect(() => {
    if (audioRef.current) {
      audioRef.current.volume = isMuted ? 0 : volume;
    }
  }, [volume, isMuted]);

  // Update progress
  useEffect(() => {
    if (!audioRef.current) return;

    const audio = audioRef.current;

    const updateProgress = () => {
      if (audio.duration) {
        setProgress((audio.currentTime / audio.duration) * 100);
      }
    };

    const handleLoadedMetadata = () => {
      setDuration(audio.duration);
    };

    const handleEnded = () => {
      setIsPlaying(false);
      setProgress(0);
    };

    audio.addEventListener("timeupdate", updateProgress);
    audio.addEventListener("loadedmetadata", handleLoadedMetadata);
    audio.addEventListener("ended", handleEnded);

    return () => {
      audio.removeEventListener("timeupdate", updateProgress);
      audio.removeEventListener("loadedmetadata", handleLoadedMetadata);
      audio.removeEventListener("ended", handleEnded);
    };
  }, [audioUrl]);

  const fetchAudio = async (voice = selectedVoice) => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await axios.post(
        `${API_BASE}/chat/sessions/${sessionId}/messages/${messageId}/tts?voice=${voice}`,
        {},
        {
          responseType: "blob",
        }
      );

      // Create object URL for audio blob
      const url = URL.createObjectURL(response.data);
      setAudioUrl(url);

      // Auto-play if requested
      if (autoPlay) {
        setTimeout(() => {
          audioRef.current?.play();
          setIsPlaying(true);
        }, 100);
      }
    } catch (err) {
      console.error("Failed to fetch TTS audio:", err);
      
      // Check if it's a dependency error
      if (err.response?.status === 500 && err.response?.data?.detail?.includes("TTS service not available")) {
        setError("Voice narration unavailable. Install orpheus-speech on backend.");
      } else {
        setError("Failed to generate audio");
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handlePlayPause = async () => {
    if (!audioRef.current) return;

    if (!audioUrl) {
      await fetchAudio();
      return;
    }

    if (isPlaying) {
      audioRef.current.pause();
      setIsPlaying(false);
    } else {
      audioRef.current.play();
      setIsPlaying(true);
    }
  };

  const handleStop = () => {
    if (!audioRef.current) return;

    audioRef.current.pause();
    audioRef.current.currentTime = 0;
    setIsPlaying(false);
    setProgress(0);
  };

  const handleProgressChange = (event, newValue) => {
    if (!audioRef.current || !duration) return;

    const newTime = (newValue / 100) * duration;
    audioRef.current.currentTime = newTime;
    setProgress(newValue);
  };

  const handleVolumeChange = (event, newValue) => {
    setVolume(newValue / 100);
    if (newValue === 0) {
      setIsMuted(true);
    } else if (isMuted) {
      setIsMuted(false);
    }
  };

  const toggleMute = () => {
    setIsMuted(!isMuted);
  };

  const handleVoiceChange = async (event) => {
    const newVoice = event.target.value;
    setSelectedVoice(newVoice);

    // Re-fetch audio with new voice if already loaded
    if (audioUrl) {
      // Cleanup old URL
      URL.revokeObjectURL(audioUrl);
      setAudioUrl(null);
      setProgress(0);
      setIsPlaying(false);

      await fetchAudio(newVoice);
    }
  };

  const formatTime = (seconds) => {
    if (!seconds || !isFinite(seconds)) return "0:00";
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  };

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (audioUrl) {
        URL.revokeObjectURL(audioUrl);
      }
    };
  }, [audioUrl]);

  if (compact) {
    return (
      <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
        <audio ref={audioRef} src={audioUrl} />

        {isLoading ? (
          <CircularProgress size={24} />
        ) : (
          <Tooltip title={isPlaying ? "Pause" : "Play DM Voice"}>
            <IconButton
              size="small"
              onClick={handlePlayPause}
              disabled={!!error}
              color="primary"
            >
              {isPlaying ? <PauseIcon /> : <PlayIcon />}
            </IconButton>
          </Tooltip>
        )}

        {error && (
          <Typography variant="caption" color="error">
            {error}
          </Typography>
        )}
      </Box>
    );
  }

  return (
    <Box
      sx={{
        p: 2,
        backgroundColor: "#f5f5f5",
        borderRadius: 2,
        border: "1px solid #ddd",
      }}
    >
      <audio ref={audioRef} src={audioUrl} />

      {/* Voice Selector */}
      {showVoiceSelector && (
        <FormControl fullWidth size="small" sx={{ mb: 2 }}>
          <InputLabel>DM Voice</InputLabel>
          <Select
            value={selectedVoice}
            label="DM Voice"
            onChange={handleVoiceChange}
            startAdornment={
              <VoiceIcon fontSize="small" sx={{ mr: 1, ml: 1 }} />
            }
          >
            {voices.map((voice) => (
              <MenuItem key={voice.value} value={voice.value}>
                {voice.label}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
      )}

      {/* Playback Controls */}
      <Box sx={{ display: "flex", alignItems: "center", gap: 1, mb: 1 }}>
        {isLoading ? (
          <CircularProgress size={32} />
        ) : (
          <>
            <IconButton onClick={handlePlayPause} disabled={!!error}>
              {isPlaying ? <PauseIcon /> : <PlayIcon />}
            </IconButton>
            <IconButton onClick={handleStop} disabled={!audioUrl || !!error}>
              <StopIcon />
            </IconButton>
          </>
        )}

        {/* Progress Bar */}
        <Box sx={{ flex: 1, mx: 2 }}>
          <Slider
            value={progress}
            onChange={handleProgressChange}
            disabled={!audioUrl || !!error}
            size="small"
          />
          <Box sx={{ display: "flex", justifyContent: "space-between" }}>
            <Typography variant="caption" color="text.secondary">
              {formatTime(audioRef.current?.currentTime || 0)}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              {formatTime(duration)}
            </Typography>
          </Box>
        </Box>

        {/* Volume Control */}
        <Box
          sx={{ display: "flex", alignItems: "center", gap: 1, minWidth: 120 }}
        >
          <IconButton size="small" onClick={toggleMute}>
            {isMuted || volume === 0 ? <MuteIcon /> : <VolumeIcon />}
          </IconButton>
          <Slider
            value={isMuted ? 0 : volume * 100}
            onChange={handleVolumeChange}
            size="small"
            sx={{ width: 80 }}
          />
        </Box>
      </Box>

      {/* Error Message */}
      {error && (
        <Typography variant="caption" color="error">
          {error}
        </Typography>
      )}
    </Box>
  );
}

export default TTSAudioPlayer;
