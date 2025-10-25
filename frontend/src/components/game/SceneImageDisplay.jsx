import React, { useState } from "react";
import {
  Box,
  Button,
  CircularProgress,
  Alert,
  IconButton,
  Tooltip,
  Card,
  CardMedia,
  CardActions,
  Typography,
  Collapse,
} from "@mui/material";
import {
  Image as ImageIcon,
  ExpandMore as ExpandMoreIcon,
  Download as DownloadIcon,
  Refresh as RefreshIcon,
} from "@mui/icons-material";

/**
 * SceneImageDisplay - Generate and display scene images for DM messages
 *
 * Uses Stable Diffusion to create contextual fantasy artwork based on
 * the DM's narrative description.
 */
const SceneImageDisplay = ({
  sessionId,
  messageId,
  messageContent,
  compact = false,
  autoGenerate = false,
  messageMetadata = null, // Pass message.metadata to check for cached images
}) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [image, setImage] = useState(null);
  const [prompt, setPrompt] = useState(null);
  const [showDetails, setShowDetails] = useState(false);
  const [hasAttemptedGeneration, setHasAttemptedGeneration] = useState(false);
  const [isCached, setIsCached] = useState(false);

  // Check for cached scene image on mount
  React.useEffect(() => {
    if (messageMetadata && messageMetadata.scene_image) {
      console.log(
        `[Scene Image] Loading cached image for message ${messageId}`
      );
      const cached = messageMetadata.scene_image;
      setImage(cached.image);
      setPrompt(cached.prompt);
      setIsCached(true);
      setHasAttemptedGeneration(true); // Don't auto-generate if we have cached data
      return;
    }

    // Auto-generate on mount if enabled (only once per component lifecycle)
    if (autoGenerate && !hasAttemptedGeneration && !image) {
      setHasAttemptedGeneration(true);
      generateImage(false);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); // Only run on mount - empty dependency array

  const generateImage = async (forceGenerate = false) => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(
        `/api/chat/sessions/${sessionId}/messages/${messageId}/scene-image`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            force_generate: forceGenerate,
          }),
        }
      );

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));

        // If this is a 400 error during auto-generation, fail silently
        // (message doesn't contain suitable scene description)
        if (response.status === 400 && autoGenerate && !forceGenerate) {
          console.log(
            `[Scene Image] Message ${messageId} not suitable for scene generation (auto-generate)`
          );
          setLoading(false);
          return; // Exit silently without setting error
        }

        throw new Error(
          errorData.detail || `Failed to generate image: ${response.status}`
        );
      }

      const data = await response.json();
      setImage(data.image);
      setPrompt(data.prompt);
      setIsCached(data.cached || false);

      if (data.cached) {
        console.log(
          `[Scene Image] Loaded cached image for message ${messageId}`
        );
      } else {
        console.log(
          `[Scene Image] Generated new image for message ${messageId}`
        );
      }
    } catch (err) {
      console.error("Scene image generation error:", err);
      setError(err.message || "Failed to generate scene image");
    } finally {
      setLoading(false);
    }
  };

  const downloadImage = () => {
    if (!image) return;

    const link = document.createElement("a");
    link.href = `data:image/png;base64,${image}`;
    link.download = `scene_${messageId}_${Date.now()}.png`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  if (!image && !loading && !error) {
    // Initial state - show generate button
    return (
      <Box sx={{ mt: 1.5 }}>
        <Button
          size="small"
          startIcon={loading ? <CircularProgress size={16} /> : <ImageIcon />}
          onClick={() => generateImage(false)}
          disabled={loading}
          sx={{
            color: "inherit",
            borderColor: "rgba(255,255,255,0.3)",
            "&:hover": {
              borderColor: "rgba(255,255,255,0.5)",
              bgcolor: "rgba(255,255,255,0.1)",
            },
          }}
          variant="outlined"
        >
          Generate Scene Image
        </Button>
      </Box>
    );
  }

  return (
    <Box sx={{ mt: 1.5 }}>
      {loading && (
        <Box sx={{ display: "flex", alignItems: "center", gap: 1, p: 2 }}>
          <CircularProgress size={20} sx={{ color: "inherit" }} />
          <Typography variant="body2">Generating scene image...</Typography>
        </Box>
      )}

      {error && (
        <Alert
          severity="warning"
          sx={{
            bgcolor: "rgba(255, 152, 0, 0.1)",
            color: "inherit",
            "& .MuiAlert-icon": { color: "inherit" },
          }}
          action={
            <Button
              size="small"
              onClick={() => generateImage(true)}
              sx={{ color: "inherit" }}
            >
              Retry
            </Button>
          }
        >
          {error}
        </Alert>
      )}

      {image && !loading && (
        <Card sx={{ bgcolor: "rgba(0,0,0,0.2)", maxWidth: 600 }}>
          <CardMedia
            component="img"
            image={`data:image/png;base64,${image}`}
            alt="Scene visualization"
            sx={{
              objectFit: "contain",
              maxHeight: 400,
              cursor: "pointer",
            }}
            onClick={() =>
              window.open(`data:image/png;base64,${image}`, "_blank")
            }
          />

          <CardActions sx={{ justifyContent: "space-between", px: 2, py: 1 }}>
            <Box sx={{ display: "flex", gap: 0.5 }}>
              <Tooltip title="Download image">
                <IconButton
                  size="small"
                  onClick={downloadImage}
                  sx={{ color: "inherit" }}
                >
                  <DownloadIcon fontSize="small" />
                </IconButton>
              </Tooltip>

              <Tooltip title="Generate new image">
                <IconButton
                  size="small"
                  onClick={() => generateImage(true)}
                  sx={{ color: "inherit" }}
                >
                  <RefreshIcon fontSize="small" />
                </IconButton>
              </Tooltip>
            </Box>

            <Tooltip title={showDetails ? "Hide prompt" : "Show prompt"}>
              <IconButton
                size="small"
                onClick={() => setShowDetails(!showDetails)}
                sx={{
                  color: "inherit",
                  transform: showDetails ? "rotate(180deg)" : "rotate(0deg)",
                  transition: "transform 0.3s",
                }}
              >
                <ExpandMoreIcon fontSize="small" />
              </IconButton>
            </Tooltip>
          </CardActions>

          <Collapse in={showDetails}>
            <Box
              sx={{ p: 2, pt: 0, borderTop: "1px solid rgba(255,255,255,0.1)" }}
            >
              <Typography
                variant="caption"
                sx={{ display: "block", mb: 0.5, fontWeight: 600 }}
              >
                Image Prompt:
              </Typography>
              <Typography
                variant="caption"
                sx={{
                  display: "block",
                  fontFamily: "monospace",
                  fontSize: "0.7rem",
                  opacity: 0.8,
                  wordBreak: "break-word",
                }}
              >
                {prompt}
              </Typography>
            </Box>
          </Collapse>
        </Card>
      )}
    </Box>
  );
};

// Memoize to prevent re-renders when parent state changes
export default React.memo(SceneImageDisplay);
