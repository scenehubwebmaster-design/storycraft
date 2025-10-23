import React, { useState, useEffect } from "react";
import {
  Box,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  List,
  ListItem,
  ListItemButton,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Typography,
  Chip,
  CircularProgress,
  Alert,
  Divider,
  Paper,
  Stack,
} from "@mui/material";
import {
  Save as SaveIcon,
  Restore as RestoreIcon,
  Delete as DeleteIcon,
  History as HistoryIcon,
  Close as CloseIcon,
  Info as InfoIcon,
} from "@mui/icons-material";

/**
 * CheckpointManager - Save and restore campaign progress
 *
 * Features:
 * - Create checkpoints with LLM-generated summaries
 * - List all checkpoints for a campaign
 * - Restore campaign state from checkpoints
 * - Delete old checkpoints
 */
const CheckpointManager = ({ campaignId, onRestoreComplete }) => {
  const [open, setOpen] = useState(false);
  const [checkpoints, setCheckpoints] = useState([]);
  const [loading, setLoading] = useState(false);
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState(null);

  // Create checkpoint dialog
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [checkpointTitle, setCheckpointTitle] = useState("");

  // Restore confirmation dialog
  const [restoreDialogOpen, setRestoreDialogOpen] = useState(false);
  const [selectedCheckpoint, setSelectedCheckpoint] = useState(null);

  // Details dialog
  const [detailsDialogOpen, setDetailsDialogOpen] = useState(false);
  const [detailsCheckpoint, setDetailsCheckpoint] = useState(null);

  useEffect(() => {
    if (open && campaignId) {
      loadCheckpoints();
    }
  }, [open, campaignId]);

  const loadCheckpoints = async () => {
    if (!campaignId) return;

    setLoading(true);
    setError(null);
    try {
      const r = await fetch(`/api/checkpoints/campaign/${campaignId}`);
      if (!r.ok) throw new Error(`Failed to load checkpoints: ${r.status}`);
      const data = await r.json();
      setCheckpoints(data.checkpoints || []);
    } catch (e) {
      console.error("Failed to load checkpoints:", e);
      setError(String(e));
    } finally {
      setLoading(false);
    }
  };

  const createCheckpoint = async () => {
    if (!campaignId) return;

    setCreating(true);
    setError(null);
    try {
      const r = await fetch(`/api/checkpoints/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          campaign_id: campaignId,
          title: checkpointTitle || undefined,
          checkpoint_type: "manual",
        }),
      });

      if (!r.ok) throw new Error(`Failed to create checkpoint: ${r.status}`);
      const data = await r.json();

      setCheckpoints((prev) => [data.checkpoint, ...prev]);
      setCreateDialogOpen(false);
      setCheckpointTitle("");
    } catch (e) {
      console.error("Failed to create checkpoint:", e);
      setError(String(e));
    } finally {
      setCreating(false);
    }
  };

  const restoreCheckpoint = async (checkpointId) => {
    setLoading(true);
    setError(null);
    try {
      const r = await fetch(`/api/checkpoints/restore`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          checkpoint_id: checkpointId,
          restore_party_state: true,
          restore_combat_state: false,
        }),
      });

      if (!r.ok) throw new Error(`Failed to restore checkpoint: ${r.status}`);
      const data = await r.json();

      setRestoreDialogOpen(false);
      setSelectedCheckpoint(null);
      setOpen(false);

      if (onRestoreComplete) {
        onRestoreComplete(data.campaign);
      }
    } catch (e) {
      console.error("Failed to restore checkpoint:", e);
      setError(String(e));
    } finally {
      setLoading(false);
    }
  };

  const deleteCheckpoint = async (checkpointId) => {
    if (!confirm("Delete this checkpoint? This cannot be undone.")) return;

    try {
      const r = await fetch(`/api/checkpoints/${checkpointId}`, {
        method: "DELETE",
      });

      if (!r.ok) throw new Error(`Failed to delete checkpoint: ${r.status}`);

      setCheckpoints((prev) => prev.filter((cp) => cp.id !== checkpointId));
    } catch (e) {
      console.error("Failed to delete checkpoint:", e);
      setError(String(e));
    }
  };

  const showDetails = (checkpoint) => {
    setDetailsCheckpoint(checkpoint);
    setDetailsDialogOpen(true);
  };

  const formatDate = (isoString) => {
    if (!isoString) return "Unknown";
    const date = new Date(isoString);
    return date.toLocaleDateString() + " " + date.toLocaleTimeString();
  };

  return (
    <>
      {/* Main Trigger Button */}
      <Button
        variant="outlined"
        startIcon={<HistoryIcon />}
        onClick={() => setOpen(true)}
        disabled={!campaignId}
      >
        Checkpoints
      </Button>

      {/* Checkpoints List Dialog */}
      <Dialog
        open={open}
        onClose={() => setOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          <Box
            sx={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
            }}
          >
            <Typography variant="h6">Campaign Checkpoints</Typography>
            <IconButton onClick={() => setOpen(false)} size="small">
              <CloseIcon />
            </IconButton>
          </Box>
        </DialogTitle>

        <DialogContent dividers>
          <Stack spacing={2}>
            {error && (
              <Alert severity="error" onClose={() => setError(null)}>
                {error}
              </Alert>
            )}

            <Button
              variant="contained"
              startIcon={<SaveIcon />}
              onClick={() => setCreateDialogOpen(true)}
              fullWidth
              sx={{ mb: 2 }}
            >
              Create New Checkpoint
            </Button>

            {loading && (
              <Box sx={{ display: "flex", justifyContent: "center", p: 3 }}>
                <CircularProgress />
              </Box>
            )}

            {!loading && checkpoints.length === 0 && (
              <Paper
                sx={{ p: 3, textAlign: "center", bgcolor: "action.hover" }}
              >
                <Typography variant="body2" color="text.secondary">
                  No checkpoints yet. Create one to save your progress!
                </Typography>
              </Paper>
            )}

            {!loading && checkpoints.length > 0 && (
              <List>
                {checkpoints.map((checkpoint, index) => (
                  <React.Fragment key={checkpoint.id}>
                    {index > 0 && <Divider />}
                    <ListItem
                      sx={{
                        flexDirection: "column",
                        alignItems: "flex-start",
                        py: 2,
                      }}
                    >
                      <Box sx={{ width: "100%", mb: 1 }}>
                        <Typography variant="subtitle1" fontWeight={600}>
                          {checkpoint.title}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {formatDate(checkpoint.created_at)} • Level{" "}
                          {checkpoint.campaign_state?.current_level || "?"}
                        </Typography>
                      </Box>

                      <Typography
                        variant="body2"
                        color="text.secondary"
                        sx={{ mb: 1 }}
                      >
                        {checkpoint.summary}
                      </Typography>

                      <Stack
                        direction="row"
                        spacing={1}
                        flexWrap="wrap"
                        useFlexGap
                        sx={{ mt: 1 }}
                      >
                        <Chip
                          label={`${
                            checkpoint.party_state?.length || 0
                          } party members`}
                          size="small"
                          variant="outlined"
                        />
                        {checkpoint.combat_state && (
                          <Chip
                            label="In Combat"
                            size="small"
                            color="error"
                            variant="outlined"
                          />
                        )}
                        {checkpoint.campaign_state?.current_location && (
                          <Chip
                            label={checkpoint.campaign_state.current_location}
                            size="small"
                            variant="outlined"
                            icon={<InfoIcon fontSize="small" />}
                          />
                        )}
                      </Stack>

                      <ListItemSecondaryAction>
                        <Stack direction="row" spacing={1}>
                          <IconButton
                            size="small"
                            color="primary"
                            onClick={() => showDetails(checkpoint)}
                            title="View Details"
                          >
                            <InfoIcon />
                          </IconButton>
                          <IconButton
                            size="small"
                            color="success"
                            onClick={() => {
                              setSelectedCheckpoint(checkpoint);
                              setRestoreDialogOpen(true);
                            }}
                            title="Restore"
                          >
                            <RestoreIcon />
                          </IconButton>
                          <IconButton
                            size="small"
                            color="error"
                            onClick={() => deleteCheckpoint(checkpoint.id)}
                            title="Delete"
                          >
                            <DeleteIcon />
                          </IconButton>
                        </Stack>
                      </ListItemSecondaryAction>
                    </ListItem>
                  </React.Fragment>
                ))}
              </List>
            )}
          </Stack>
        </DialogContent>

        <DialogActions>
          <Button onClick={() => setOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>

      {/* Create Checkpoint Dialog */}
      <Dialog
        open={createDialogOpen}
        onClose={() => !creating && setCreateDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Create Checkpoint</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            <Alert severity="info" icon={<InfoIcon />}>
              The AI will generate a narrative summary of your current progress.
              This may take a moment.
            </Alert>

            <TextField
              label="Checkpoint Title (optional)"
              fullWidth
              value={checkpointTitle}
              onChange={(e) => setCheckpointTitle(e.target.value)}
              placeholder="e.g., Before entering the dragon's lair"
              disabled={creating}
            />

            {error && <Alert severity="error">{error}</Alert>}
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button
            onClick={() => setCreateDialogOpen(false)}
            disabled={creating}
          >
            Cancel
          </Button>
          <Button
            onClick={createCheckpoint}
            variant="contained"
            disabled={creating}
            startIcon={creating ? <CircularProgress size={16} /> : <SaveIcon />}
          >
            {creating ? "Creating..." : "Save Checkpoint"}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Restore Confirmation Dialog */}
      <Dialog
        open={restoreDialogOpen}
        onClose={() => !loading && setRestoreDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Restore Checkpoint?</DialogTitle>
        <DialogContent>
          {selectedCheckpoint && (
            <Stack spacing={2}>
              <Alert severity="warning">
                This will restore your campaign to this checkpoint. Current
                progress since this checkpoint will not be lost (it stays in
                chat history), but your party states and quest progress will be
                updated.
              </Alert>

              <Paper sx={{ p: 2, bgcolor: "action.hover" }}>
                <Typography variant="subtitle2" gutterBottom>
                  {selectedCheckpoint.title}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {selectedCheckpoint.summary}
                </Typography>
              </Paper>
            </Stack>
          )}
        </DialogContent>
        <DialogActions>
          <Button
            onClick={() => setRestoreDialogOpen(false)}
            disabled={loading}
          >
            Cancel
          </Button>
          <Button
            onClick={() =>
              selectedCheckpoint && restoreCheckpoint(selectedCheckpoint.id)
            }
            variant="contained"
            color="warning"
            disabled={loading}
            startIcon={
              loading ? <CircularProgress size={16} /> : <RestoreIcon />
            }
          >
            {loading ? "Restoring..." : "Restore"}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Details Dialog */}
      <Dialog
        open={detailsDialogOpen}
        onClose={() => setDetailsDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          <Box
            sx={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
            }}
          >
            Checkpoint Details
            <IconButton
              onClick={() => setDetailsDialogOpen(false)}
              size="small"
            >
              <CloseIcon />
            </IconButton>
          </Box>
        </DialogTitle>
        <DialogContent dividers>
          {detailsCheckpoint && (
            <Stack spacing={2}>
              <Box>
                <Typography variant="h6" gutterBottom>
                  {detailsCheckpoint.title}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Created: {formatDate(detailsCheckpoint.created_at)}
                </Typography>
              </Box>

              <Divider />

              <Box>
                <Typography variant="subtitle2" gutterBottom>
                  Summary
                </Typography>
                <Typography variant="body2" sx={{ whiteSpace: "pre-wrap" }}>
                  {detailsCheckpoint.summary}
                </Typography>
              </Box>

              <Divider />

              <Box>
                <Typography variant="subtitle2" gutterBottom>
                  Party Status
                </Typography>
                <List dense>
                  {detailsCheckpoint.party_state?.map((member, i) => (
                    <ListItem key={i}>
                      <ListItemText
                        primary={`${member.name} (Level ${member.level} ${member.class})`}
                        secondary={`HP: ${member.current_hp}/${member.max_hp} • ${member.status}`}
                      />
                    </ListItem>
                  ))}
                </List>
              </Box>

              {detailsCheckpoint.campaign_state?.current_location && (
                <>
                  <Divider />
                  <Box>
                    <Typography variant="subtitle2" gutterBottom>
                      Location
                    </Typography>
                    <Typography variant="body2">
                      {detailsCheckpoint.campaign_state.current_location}
                    </Typography>
                  </Box>
                </>
              )}

              {detailsCheckpoint.combat_state && (
                <>
                  <Divider />
                  <Box>
                    <Typography variant="subtitle2" gutterBottom>
                      Combat Status
                    </Typography>
                    <Alert severity="warning">
                      Active combat encounter:{" "}
                      {detailsCheckpoint.combat_state.name}
                    </Alert>
                  </Box>
                </>
              )}
            </Stack>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDetailsDialogOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </>
  );
};

export default CheckpointManager;
