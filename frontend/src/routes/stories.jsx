import { createFileRoute, Link } from "@tanstack/react-router";
import { useState, useEffect } from "react";
import axios from "axios";
import {
  Typography,
  Box,
  Button,
  Grid,
  Card,
  CardContent,
  CardActions,
  CircularProgress,
  Alert,
  Chip,
  TextField,
  InputAdornment,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from "@mui/material";
import AddIcon from "@mui/icons-material/Add";
import MenuBookIcon from "@mui/icons-material/MenuBook";
import SearchIcon from "@mui/icons-material/Search";
import DeleteIcon from "@mui/icons-material/Delete";
import ClearIcon from "@mui/icons-material/Clear";

export const Route = createFileRoute("/stories")({
  component: StoriesComponent,
});

const API_URL = "http://localhost:8000";

function StoriesComponent() {
  const [stories, setStories] = useState([]);
  const [filteredStories, setFilteredStories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [storyToDelete, setStoryToDelete] = useState(null);
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    loadStories();
  }, []);

  useEffect(() => {
    filterStories();
  }, [searchQuery, stories]);

  const loadStories = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_URL}/api/stories`);
      setStories(response.data);
      setError(null);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to load stories");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const filterStories = () => {
    if (!searchQuery.trim()) {
      setFilteredStories(stories);
      return;
    }

    const query = searchQuery.toLowerCase();
    const filtered = stories.filter(
      (story) =>
        story.title?.toLowerCase().includes(query) ||
        story.description?.toLowerCase().includes(query) ||
        story.genre?.toLowerCase().includes(query) ||
        story.content?.toLowerCase().includes(query)
    );
    setFilteredStories(filtered);
  };

  const handleDeleteClick = (story) => {
    setStoryToDelete(story);
    setDeleteDialogOpen(true);
  };

  const handleDeleteConfirm = async () => {
    if (!storyToDelete) return;

    try {
      setDeleting(true);
      await axios.delete(`${API_URL}/api/stories/${storyToDelete.id}`);
      setStories(stories.filter((s) => s.id !== storyToDelete.id));
      setDeleteDialogOpen(false);
      setStoryToDelete(null);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to delete story");
    } finally {
      setDeleting(false);
    }
  };

  const truncateText = (text, maxLength = 200) => {
    if (!text) return "";
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + "...";
  };

  const formatDate = (dateString) => {
    if (!dateString) return "Unknown";
    const date = new Date(dateString);
    return date.toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
    });
  };

  if (loading) {
    return (
      <Box sx={{ display: "flex", justifyContent: "center", py: 10 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Box
        sx={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          mb: 4,
        }}
      >
        <Box>
          <Typography variant="h3" component="h1" sx={{ fontWeight: 700 }}>
            My Stories
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ mt: 1 }}>
            {filteredStories.length} stor{filteredStories.length !== 1 ? "ies" : "y"}
            {searchQuery && ` (filtered from ${stories.length})`}
          </Typography>
        </Box>
        <Button
          component={Link}
          to="/create/story"
          variant="contained"
          startIcon={<AddIcon />}
        >
          New Story
        </Button>
      </Box>

      {/* Search Bar */}
      <TextField
        fullWidth
        variant="outlined"
        placeholder="Search stories by title, description, genre, or content..."
        value={searchQuery}
        onChange={(e) => setSearchQuery(e.target.value)}
        sx={{ mb: 3 }}
        InputProps={{
          startAdornment: (
            <InputAdornment position="start">
              <SearchIcon />
            </InputAdornment>
          ),
          endAdornment: searchQuery && (
            <InputAdornment position="end">
              <IconButton
                onClick={() => setSearchQuery("")}
                edge="end"
                size="small"
              >
                <ClearIcon />
              </IconButton>
            </InputAdornment>
          ),
        }}
      />

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {filteredStories.length === 0 ? (
        <Card
          sx={{
            p: 4,
            textAlign: "center",
            backgroundColor: "background.default",
          }}
        >
          <MenuBookIcon sx={{ fontSize: 80, color: "text.secondary", mb: 2 }} />
          <Typography variant="h5" gutterBottom>
            {searchQuery ? "No Stories Found" : "No Stories Yet"}
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
            {searchQuery
              ? "Try a different search term"
              : "Create your first story to get started"}
          </Typography>
          {!searchQuery && (
            <Button
              component={Link}
              to="/create/story"
              variant="contained"
              startIcon={<AddIcon />}
            >
              Create Story
            </Button>
          )}
        </Card>
      ) : (
        <Grid container spacing={3}>
          {filteredStories.map((story) => (
            <Grid key={story.id} size={{ xs: 12, sm: 6, md: 4 }}>
              <Card
                sx={{
                  height: "100%",
                  display: "flex",
                  flexDirection: "column",
                  transition: "transform 0.2s, box-shadow 0.2s",
                  "&:hover": {
                    transform: "translateY(-4px)",
                    boxShadow: 4,
                  },
                }}
              >
                <CardContent sx={{ flexGrow: 1 }}>
                  <Typography variant="h6" gutterBottom>
                    {story.title}
                  </Typography>
                  <Typography
                    variant="body2"
                    color="text.secondary"
                    sx={{ mb: 2 }}
                  >
                    {truncateText(story.description)}
                  </Typography>
                  <Box sx={{ display: "flex", gap: 1, flexWrap: "wrap" }}>
                    {story.genre && (
                      <Chip label={story.genre} size="small" color="primary" />
                    )}
                    <Chip
                      label={formatDate(story.created_at)}
                      size="small"
                      variant="outlined"
                    />
                  </Box>
                </CardContent>
                <CardActions>
                  <Button
                    size="small"
                    component={Link}
                    to={`/stories/${story.id}`}
                  >
                    View Details
                  </Button>
                  <Button
                    size="small"
                    color="secondary"
                    component={Link}
                    to={`/create/story?edit=${story.id}`}
                  >
                    Edit
                  </Button>
                  <IconButton
                    size="small"
                    color="error"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleDeleteClick(story);
                    }}
                    sx={{ ml: "auto" }}
                  >
                    <DeleteIcon fontSize="small" />
                  </IconButton>
                </CardActions>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      {/* Delete Confirmation Dialog */}
      <Dialog
        open={deleteDialogOpen}
        onClose={() => !deleting && setDeleteDialogOpen(false)}
      >
        <DialogTitle>Delete Story?</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to delete{" "}
            <strong>{storyToDelete?.title}</strong>? This action cannot be
            undone and will also delete all associated chapters.
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
            onClick={handleDeleteConfirm}
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
