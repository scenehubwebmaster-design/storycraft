import { Link, useNavigate, useParams } from "react-router-dom";
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
import { API_URL } from "../config/api";

export default function StoryDetailPage() {
  const { storyId } = useParams();
  const navigate = useNavigate();
  const [story, setStory] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    loadStory();
  }, [storyId]);

  const loadStory = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_URL}/api/stories/${storyId}`);
      setStory(response.data);
      setError(null);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to load story");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    try {
      setDeleting(true);
      await axios.delete(`${API_URL}/api/stories/${storyId}/`);
      navigate({ to: "/stories" });
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to delete story");
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
        <Button component={Link} to="/stories" startIcon={<ArrowBackIcon />}>
          Back to Stories
        </Button>
      </Box>
    );
  }

  if (!story) {
    return (
      <Box>
        <Alert severity="warning" sx={{ mb: 3 }}>
          Story not found
        </Alert>
        <Button component={Link} to="/stories" startIcon={<ArrowBackIcon />}>
          Back to Stories
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
          to="/stories"
          startIcon={<ArrowBackIcon />}
          sx={{ mb: 2 }}
        >
          Back to Stories
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
              {story.title}
            </Typography>
            {story.genre && (
              <Chip label={story.genre} color="primary" sx={{ mt: 2 }} />
            )}
            <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
              Created: {formatDate(story.created_at)}
            </Typography>
            {story.updated_at && story.updated_at !== story.created_at && (
              <Typography
                variant="body2"
                color="text.secondary"
                sx={{ mt: 0.5 }}
              >
                Updated: {formatDate(story.updated_at)}
              </Typography>
            )}
          </Box>
          <Box sx={{ display: "flex", gap: 2 }}>
            <Button
              variant="outlined"
              startIcon={<EditIcon />}
              component={Link}
              to={`/create/story?edit=${storyId}`}
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
          {story.description && (
            <Box sx={{ mb: 3 }}>
              <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
                Description
              </Typography>
              <Typography variant="body1" sx={{ whiteSpace: "pre-wrap" }}>
                {story.description}
              </Typography>
            </Box>
          )}

          {story.description && story.content && <Divider sx={{ my: 3 }} />}

          {/* Content */}
          {story.content && (
            <Box>
              <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
                Story Content
              </Typography>
              <Typography variant="body1" sx={{ whiteSpace: "pre-wrap" }}>
                {story.content}
              </Typography>
            </Box>
          )}

          {!story.description && !story.content && (
            <Typography variant="body2" color="text.secondary">
              No content available for this story yet.
            </Typography>
          )}
        </CardContent>
      </Card>

      {/* Delete Confirmation Dialog */}
      <Dialog
        open={deleteDialogOpen}
        onClose={() => !deleting && setDeleteDialogOpen(false)}
      >
        <DialogTitle>Delete Story?</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to delete <strong>{story.title}</strong>? This
            action cannot be undone and will also delete all associated
            chapters.
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
