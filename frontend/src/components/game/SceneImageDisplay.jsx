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
}) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [image, setImage] = useState(null);
  const [prompt, setPrompt] = useState(null);
  const [showDetails, setShowDetails] = useState(false);
  const [hasAttemptedGeneration, setHasAttemptedGeneration] = useState(false);

  // Auto-generate on mount if enabled
  React.useEffect(() => {
    if (autoGenerate && !hasAttemptedGeneration && !image && !loading) {
      setHasAttemptedGeneration(true);
      generateImage(false);
    }
  }, [autoGenerate, hasAttemptedGeneration, image, loading]);

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
        throw new Error(
          errorData.detail || `Failed to generate image: ${response.status}`
        );
      }

      const data = await response.json();
      setImage(data.image);
      setPrompt(data.prompt);
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

export default SceneImageDisplay;
