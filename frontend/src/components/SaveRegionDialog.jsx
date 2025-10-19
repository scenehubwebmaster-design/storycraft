import React, { useState, useEffect } from "react";
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Box,
  Typography,
  CircularProgress,
  Alert,
} from "@mui/material";

export default function SaveRegionDialog({
  open,
  onClose,
  imageBase64,
  suggestedName,
  suggestedCoords,
  onSave,
  // optional provider status metadata
  isGenerating = false,
  provider = null,
  promptUsed = null,
  generationError = null,
  onAcceptFallback = null,
  imageDimensions = null,
}) {
  const [name, setName] = useState(suggestedName || "");
  const [description, setDescription] = useState("");
  const [saving, setSaving] = useState(false);
  const [acceptedFallback, setAcceptedFallback] = useState(false);

  useEffect(() => {
    setName(suggestedName || "");
    setDescription("");
    setAcceptedFallback(false);
  }, [suggestedName, imageBase64, generationError]);

  const handleSave = async () => {
    setSaving(true);
    try {
      await onSave({ name, description });
    } finally {
      setSaving(false);
      onClose && onClose();
    }
  };

  const handleAcceptFallback = () => {
    setAcceptedFallback(true);
    onAcceptFallback && onAcceptFallback();
  };

  return (
    <Dialog
      open={!!open}
      onClose={() => onClose && onClose()}
      fullWidth
      maxWidth="sm"
    >
      <DialogTitle>Save Generated Region</DialogTitle>
      <DialogContent>
        {isGenerating && (
          <Box sx={{ display: "flex", alignItems: "center", gap: 2, mb: 2 }}>
            <CircularProgress size={20} />
            <Typography variant="body2">Generating image...</Typography>
          </Box>
        )}

        {generationError && (
          <Alert severity="warning" sx={{ mb: 2 }}>
            Provider error: {generationError}
          </Alert>
        )}

        {imageBase64 ? (
          <Box sx={{ display: "flex", gap: 2, alignItems: "flex-start" }}>
            <img
              src={`data:image/png;base64,${imageBase64}`}
              alt={name}
              style={{ width: 200, borderRadius: 6 }}
            />
            <Box sx={{ flex: 1 }}>
              <Typography variant="body2" sx={{ mb: 1 }}>
                Suggested coordinates: {suggestedCoords}
              </Typography>
              {imageDimensions && (
                <Typography variant="caption" sx={{ display: "block", mb: 1 }}>
                  Image size: {imageDimensions.width} x {imageDimensions.height}{" "}
                  px
                </Typography>
              )}
              {provider && (
                <Typography variant="caption" sx={{ display: "block", mb: 1 }}>
                  Provider: {provider}{" "}
                  {promptUsed ? ` — Prompt: ${promptUsed}` : ""}
                </Typography>
              )}
              <TextField
                label="Name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                fullWidth
                sx={{ mb: 2 }}
              />
              <TextField
                label="Description"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                fullWidth
                multiline
                minRows={3}
              />
            </Box>
          </Box>
        ) : (
          <Typography>Waiting for generated image...</Typography>
        )}
        {generationError && !acceptedFallback && (
          <Box sx={{ mt: 2, display: "flex", gap: 1 }}>
            <Button variant="outlined" onClick={handleAcceptFallback}>
              Use Cropped Fallback
            </Button>
            <Button
              variant="text"
              onClick={() => onClose && onClose()}
              color="inherit"
            >
              Cancel
            </Button>
          </Box>
        )}
        {suggestedCoords && (
          <Box sx={{ mt: 2, display: "flex", gap: 1, alignItems: "center" }}>
            <Typography variant="body2">
              Coordinates: {suggestedCoords}
            </Typography>
            <Button
              size="small"
              onClick={() => navigator.clipboard?.writeText(suggestedCoords)}
            >
              Copy
            </Button>
          </Box>
        )}
      </DialogContent>
      <DialogActions>
        <Button
          onClick={() => onClose && onClose()}
          disabled={saving || isGenerating}
        >
          Close
        </Button>
        <Button
          onClick={handleSave}
          variant="contained"
          disabled={saving || (!imageBase64 && !acceptedFallback)}
        >
          {saving ? "Saving..." : "Save"}
        </Button>
      </DialogActions>
    </Dialog>
  );
}
