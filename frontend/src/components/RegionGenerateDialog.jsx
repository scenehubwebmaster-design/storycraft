import React, { useState } from "react";
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  FormControlLabel,
  Checkbox,
  Select,
  MenuItem,
  Typography,
} from "@mui/material";

export default function RegionGenerateDialog({
  open,
  onClose,
  regionBounds,
  onGenerate,
}) {
  const [prompt, setPrompt] = useState("");
  const [useCropAndGenerate, setUseCropAndGenerate] = useState(true);
  const [provider, setProvider] = useState("stablediffusion");
  const [saving, setSaving] = useState(false);

  React.useEffect(() => {
    if (!regionBounds) return;
    const sw = regionBounds._southWest || regionBounds.getSouthWest();
    const ne = regionBounds._northEast || regionBounds.getNorthEast();
    setPrompt(
      `Generate high-res view for region between ${sw.lat.toFixed(
        2
      )},${sw.lng.toFixed(2)} and ${ne.lat.toFixed(2)},${ne.lng.toFixed(2)}.`
    );
  }, [regionBounds]);

  const handleGenerate = async () => {
    setSaving(true);
    try {
      await onGenerate({ prompt, regionBounds, useCropAndGenerate, provider });
      onClose();
    } finally {
      setSaving(false);
    }
  };

  return (
    <Dialog
      open={!!open}
      onClose={() => onClose && onClose()}
      fullWidth
      maxWidth="sm"
    >
      <DialogTitle>Generate Region Image</DialogTitle>
      <DialogContent>
        <Typography variant="body2">
          Selected region bounds: {regionBounds ? "see prompt" : "none"}
        </Typography>
        <TextField
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          fullWidth
          multiline
          minRows={3}
          sx={{ mt: 2 }}
        />
        <FormControlLabel
          control={
            <Checkbox
              checked={useCropAndGenerate}
              onChange={(e) => setUseCropAndGenerate(e.target.checked)}
            />
          }
          label="Crop + Generate (use cropped area as context)"
          sx={{ mt: 2 }}
        />
        <div style={{ marginTop: 8 }}>
          <Typography variant="caption">Provider</Typography>
          <Select
            value={provider}
            onChange={(e) => setProvider(e.target.value)}
            fullWidth
            size="small"
          >
            <MenuItem value="stablediffusion">
              Stable Diffusion (local)
            </MenuItem>
            <MenuItem value="google">Google Imagen</MenuItem>
          </Select>
        </div>
      </DialogContent>
      <DialogActions>
        <Button onClick={() => onClose && onClose()} disabled={saving}>
          Cancel
        </Button>
        <Button onClick={handleGenerate} variant="contained" disabled={saving}>
          {saving ? "Generating..." : "Generate"}
        </Button>
      </DialogActions>
    </Dialog>
  );
}
