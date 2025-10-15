import { createFileRoute, Link, useNavigate } from "@tanstack/react-router";
import { useState, useEffect } from "react";
import axios from "axios";
import {
  Typography,
  Box,
  Button,
  Card,
  CardContent,
  CircularProgress,
  Alert,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Divider,
} from "@mui/material";
import EditIcon from "@mui/icons-material/Edit";
import DeleteIcon from "@mui/icons-material/Delete";
import ArrowBackIcon from "@mui/icons-material/ArrowBack";

export const Route = createFileRoute("/worlds/$worldId")({
  component: WorldDetailComponent,
});

const API_URL = "http://localhost:8000";

function WorldDetailComponent() {
  const { worldId } = Route.useParams();
  const navigate = useNavigate();
  const [world, setWorld] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    loadWorld();
  }, [worldId]);

  const loadWorld = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_URL}/api/worlds/${worldId}`);
      setWorld(response.data);
      setError(null);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to load world");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    try {
      setDeleting(true);
      await axios.delete(`${API_URL}/api/worlds/${worldId}`);
      navigate({ to: "/worlds" });
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to delete world");
      setDeleteDialogOpen(false);
      setDeleting(false);
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return "Unknown";
    const date = new Date(dateString);
    return date.toLocaleDateString("en-US", {
      year: "numeric",
      month: "long",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  if (loading) {
    return (
      <Box sx={{ display: "flex", justifyContent: "center", py: 10 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box>
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
        <Button component={Link} to="/worlds" startIcon={<ArrowBackIcon />}>
          Back to Worlds
        </Button>
      </Box>
    );
  }

  if (!world) {
    return (
      <Box>
        <Alert severity="warning" sx={{ mb: 3 }}>
          World not found
        </Alert>
        <Button component={Link} to="/worlds" startIcon={<ArrowBackIcon />}>
          Back to Worlds
        </Button>
      </Box>
    );
  }

  return (
    <Box>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Button
          component={Link}
          to="/worlds"
          startIcon={<ArrowBackIcon />}
          sx={{ mb: 2 }}
        >
          Back to Worlds
        </Button>
        <Box
          sx={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "flex-start",
          }}
        >
          <Box>
            <Typography variant="h3" component="h1" sx={{ fontWeight: 700 }}>
              {world.name}
            </Typography>
            <Box sx={{ display: "flex", gap: 1, mt: 2, flexWrap: "wrap" }}>
              {world.magic_system && (
                <Chip
                  label={`Magic: ${world.magic_system}`}
                  color="secondary"
                />
              )}
              {world.technology_level && (
                <Chip
                  label={`Tech: ${world.technology_level}`}
                  color="primary"
                />
              )}
            </Box>
            <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
              Created: {formatDate(world.created_at)}
            </Typography>
            {world.updated_at && world.updated_at !== world.created_at && (
              <Typography
                variant="body2"
                color="text.secondary"
                sx={{ mt: 0.5 }}
              >
                Updated: {formatDate(world.updated_at)}
              </Typography>
            )}
          </Box>
          <Box sx={{ display: "flex", gap: 2 }}>
            <Button
              variant="outlined"
              startIcon={<EditIcon />}
              component={Link}
              to={`/create/world?edit=${worldId}`}
            >
              Edit
            </Button>
            <Button
              variant="outlined"
              color="error"
              startIcon={<DeleteIcon />}
              onClick={() => setDeleteDialogOpen(true)}
            >
              Delete
            </Button>
          </Box>
        </Box>
      </Box>

      {/* Content Card */}
      <Card>
        <CardContent>
          {/* Description */}
          {world.description && (
            <Box sx={{ mb: 3 }}>
              <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
                Description
              </Typography>
              <Typography variant="body1" sx={{ whiteSpace: "pre-wrap" }}>
                {world.description}
              </Typography>
            </Box>
          )}

          {world.description && world.history && <Divider sx={{ my: 3 }} />}

          {/* History */}
          {world.history && (
            <Box sx={{ mb: 3 }}>
              <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
                History
              </Typography>
              <Typography variant="body1" sx={{ whiteSpace: "pre-wrap" }}>
                {world.history}
              </Typography>
            </Box>
          )}

          {world.history && world.geography && <Divider sx={{ my: 3 }} />}

          {/* Geography */}
          {world.geography && (
            <Box sx={{ mb: 3 }}>
              <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
                Geography
              </Typography>
              <Typography variant="body1" sx={{ whiteSpace: "pre-wrap" }}>
                {world.geography}
              </Typography>
            </Box>
          )}

          {world.geography && world.culture && <Divider sx={{ my: 3 }} />}

          {/* Culture */}
          {world.culture && (
            <Box sx={{ mb: 3 }}>
              <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
                Culture
              </Typography>
              <Typography variant="body1" sx={{ whiteSpace: "pre-wrap" }}>
                {world.culture}
              </Typography>
            </Box>
          )}

          {world.culture && world.lore && <Divider sx={{ my: 3 }} />}

          {/* Lore */}
          {world.lore && (
            <Box>
              <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
                Lore
              </Typography>
              <Typography variant="body1" sx={{ whiteSpace: "pre-wrap" }}>
                {world.lore}
              </Typography>
            </Box>
          )}

          {!world.description &&
            !world.history &&
            !world.geography &&
            !world.culture &&
            !world.lore && (
              <Typography variant="body2" color="text.secondary">
                No content available for this world yet.
              </Typography>
            )}
        </CardContent>
      </Card>

      {/* Delete Confirmation Dialog */}
      <Dialog
        open={deleteDialogOpen}
        onClose={() => !deleting && setDeleteDialogOpen(false)}
      >
        <DialogTitle>Delete World?</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to delete <strong>{world.name}</strong>? This
            action cannot be undone and will also delete all associated
            locations.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button
            onClick={() => setDeleteDialogOpen(false)}
            disabled={deleting}
          >
            Cancel
          </Button>
          <Button
            onClick={handleDelete}
            color="error"
            variant="contained"
            disabled={deleting}
          >
            {deleting ? "Deleting..." : "Delete"}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
