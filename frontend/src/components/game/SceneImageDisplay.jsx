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
  locationHint = null, // optional short descriptor string to pass to generation endpoint
  typingReady = false, // whether the parent marked this message as finished typing
}) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [image, setImage] = useState(null);
  const [prompt, setPrompt] = useState(null);
  const [showDetails, setShowDetails] = useState(false);
  const [hasAttemptedGeneration, setHasAttemptedGeneration] = useState(false);
  const [isCached, setIsCached] = useState(false);

  // Check for cached scene image - runs whenever messageMetadata changes (SSE updates)
  React.useEffect(() => {
    console.log(`[Scene Image] useEffect triggered for message ${messageId}:`, {
      hasMetadata: !!messageMetadata,
      hasSceneImage: !!(messageMetadata && messageMetadata.scene_image),
      metadataKeys: messageMetadata ? Object.keys(messageMetadata) : [],
      sceneImageKeys: messageMetadata?.scene_image
        ? Object.keys(messageMetadata.scene_image)
        : [],
      hasImageData: !!messageMetadata?.scene_image?.image,
      imageLength: messageMetadata?.scene_image?.image?.length || 0,
    });

    if (messageMetadata && messageMetadata.scene_image) {
      const cached = messageMetadata.scene_image;

      // If an image blob/base64 is already present, use it immediately
      if (cached.image) {
        console.log(
          `[Scene Image] ✅ Setting image state for message ${messageId} (${cached.image.length} bytes)`
        );
        setImage(cached.image);
        setPrompt(cached.prompt);
        setIsCached(true);
        setHasAttemptedGeneration(true);
        setLoading(false); // Stop any loading indicators
        return;
      }

      // If we have scene_image metadata but no image yet (just prompt/descriptors),
      // the backend is probably generating it now. The image will arrive via SSE
      // and this useEffect will re-run with the updated metadata.
      console.log(
        `[Scene Image] ⏳ Waiting for image generation for message ${messageId} (have prompt, no image yet)`,
        "Full scene_image object:",
        cached
      );
      setPrompt(cached.prompt);
      setIsCached(false);

      // Mark that we know about this image generation attempt
      if (!hasAttemptedGeneration) {
        setHasAttemptedGeneration(true);
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [messageMetadata]); // Only depend on messageMetadata to avoid dependency array size changes

  // When the parent indicates typing completed, attempt to generate if we
  // have a prompt (messageMetadata.scene_image.prompt) but no image yet.
  React.useEffect(() => {
    if (!typingReady) return;
    if (!autoGenerate) return;
    if (!messageMetadata || !messageMetadata.scene_image) return;
    const si = messageMetadata.scene_image;
    if (si.image) return; // already have image
    if (hasAttemptedGeneration) return; // already triggered

    // Force generate now so the image is ready by the time the DM finishes
    setHasAttemptedGeneration(true);
    generateImage(true);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [typingReady]);

  const generateImage = async (forceGenerate = false) => {
    setLoading(true);
    setError(null);

    try {
      // If caller provided a locationHint, attach it as a query param so the
      // backend can use it as the primary prompt for image generation.
      const hintQuery = locationHint
        ? `?location_hint=${encodeURIComponent(locationHint)}`
        : "";

      const response = await fetch(
        `/api/chat/sessions/${sessionId}/messages/${messageId}/scene-image${hintQuery}`,
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

    // If image is an http(s) URL, fetch it as a blob then download.
    if (/^https?:\/\//i.test(image)) {
      fetch(image)
        .then((res) => {
          if (!res.ok) throw new Error(`Failed to fetch image: ${res.status}`);
          return res.blob();
        })
        .then((blob) => {
          const url = URL.createObjectURL(blob);
          const link = document.createElement("a");
          link.href = url;
          link.download = `scene_${messageId}_${Date.now()}.png`;
          document.body.appendChild(link);
          link.click();
          document.body.removeChild(link);
          URL.revokeObjectURL(url);
        })
        .catch((e) => console.error("Download failed:", e));
      return;
    }

    // If it already looks like a data URL (starts with data:) use it directly
    if (/^data:/i.test(image)) {
      const link = document.createElement("a");
      link.href = image;
      link.download = `scene_${messageId}_${Date.now()}.png`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      return;
    }

    // Otherwise assume raw base64 string and wrap it in a data URL
    const link = document.createElement("a");
    link.href = `data:image/png;base64,${image}`;
    link.download = `scene_${messageId}_${Date.now()}.png`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  if (!image && !loading && !error) {
    // Initial state - automatically generating or waiting for cached image
    // Do not show a button; generation happens automatically via autoGenerate prop
    return null;
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
            image={
              // If image is an http(s) URL, use it directly. If it already
              // is a data: URL (server returned full data URL), use it as-is.
              // Otherwise assume it's a raw base64 string and prefix it.
              /^https?:\/\//i.test(image)
                ? image
                : /^data:/i.test(image)
                ? image
                : `data:image/png;base64,${image}`
            }
            alt="Scene visualization"
            sx={{
              objectFit: "contain",
              maxHeight: 400,
              cursor: "pointer",
            }}
            onClick={() => {
              const href = /^https?:\/\//i.test(image)
                ? image
                : /^data:/i.test(image)
                ? image
                : `data:image/png;base64,${image}`;
              window.open(href, "_blank");
            }}
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
