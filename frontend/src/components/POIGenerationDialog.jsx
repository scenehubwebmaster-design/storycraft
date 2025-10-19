import React, { useState } from "react";
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Typography,
} from "@mui/material";

export default function POIGenerationDialog({
  open,
  onClose,
  poi,
  onGenerate,
  onSave,
}) {
  const [prompt, setPrompt] = useState(
    poi?.name ? `Portrait of ${poi.name}, ${poi.description || ""}` : ""
  );
  const [saving, setSaving] = useState(false);

  React.useEffect(() => {
    setPrompt(
      poi?.name ? `Portrait of ${poi.name}, ${poi.description || ""}` : ""
    );
  }, [poi]);

  const handleGenerate = async () => {
    if (!onGenerate) return;
    await onGenerate({ ...poi, prompt });
  };

  const handleSave = async (imageBase64) => {
    setSaving(true);
    try {
      if (onSave) await onSave({ ...poi, imageBase64 });
      onClose();
    } finally {
      setSaving(false);
    }
  };

  return (
    <Dialog
      open={!!open}
      onClose={() => onClose && onClose()}
      maxWidth="sm"
      fullWidth
    >
      <DialogTitle>{poi?.name || "Generate POI Portrait"}</DialogTitle>
      <DialogContent>
        <Typography variant="body2" color="textSecondary">
          Coordinates: {poi?.coordinates}
        </Typography>
        <TextField
          label="Prompt"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          fullWidth
          multiline
          minRows={3}
          style={{ marginTop: 12 }}
        />
      </DialogContent>
      <DialogActions>
        <Button onClick={() => onClose && onClose()} disabled={saving}>
          Cancel
        </Button>
        <Button onClick={handleGenerate} variant="outlined">
          Generate
        </Button>
        <Button
          onClick={() => handleSave(null)}
          color="primary"
          variant="contained"
          disabled={saving}
        >
          Save (after generate)
        </Button>
      </DialogActions>
    </Dialog>
  );
}
