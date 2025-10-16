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
import PublicIcon from "@mui/icons-material/Public";
import SearchIcon from "@mui/icons-material/Search";
import DeleteIcon from "@mui/icons-material/Delete";
import ClearIcon from "@mui/icons-material/Clear";
import { API_URL } from "../config/api";

export const Route = createFileRoute("/worlds")({
  component: WorldsComponent,
});

function WorldsComponent() {
  const [worlds, setWorlds] = useState([]);
  const [filteredWorlds, setFilteredWorlds] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [worldToDelete, setWorldToDelete] = useState(null);
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    loadWorlds();
  }, []);

  useEffect(() => {
    filterWorlds();
  }, [searchQuery, worlds]);

  const loadWorlds = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_URL}/api/worlds`);
      setWorlds(response.data);
      setError(null);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to load worlds");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const filterWorlds = () => {
    if (!searchQuery.trim()) {
      setFilteredWorlds(worlds);
      return;
    }

    const query = searchQuery.toLowerCase();
    const filtered = worlds.filter(
      (world) =>
        world.name?.toLowerCase().includes(query) ||
        world.description?.toLowerCase().includes(query) ||
        world.history?.toLowerCase().includes(query) ||
        world.geography?.toLowerCase().includes(query) ||
        world.culture?.toLowerCase().includes(query) ||
        world.magic_system?.toLowerCase().includes(query) ||
        world.technology_level?.toLowerCase().includes(query)
    );
    setFilteredWorlds(filtered);
  };

  const handleDeleteClick = (world) => {
    setWorldToDelete(world);
    setDeleteDialogOpen(true);
  };

  const handleDeleteConfirm = async () => {
    if (!worldToDelete) return;

    try {
      setDeleting(true);
      await axios.delete(`${API_URL}/api/worlds/${worldToDelete.id}`);
      setWorlds(worlds.filter((w) => w.id !== worldToDelete.id));
      setDeleteDialogOpen(false);
      setWorldToDelete(null);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to delete world");
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
            Worlds & Lore
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ mt: 1 }}>
            {filteredWorlds.length} world{filteredWorlds.length !== 1 ? "s" : ""}
            {searchQuery && ` (filtered from ${worlds.length})`}
          </Typography>
        </Box>
        <Button
          component={Link}
          to="/create/world"
          variant="contained"
          startIcon={<AddIcon />}
        >
          New World
        </Button>
      </Box>

      {/* Search Bar */}
      <TextField
        fullWidth
        variant="outlined"
        placeholder="Search worlds by name, description, history, culture, magic system, or technology level..."
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

      {filteredWorlds.length === 0 ? (
        <Card
          sx={{
            p: 4,
            textAlign: "center",
            backgroundColor: "background.default",
          }}
        >
          <PublicIcon sx={{ fontSize: 80, color: "text.secondary", mb: 2 }} />
          <Typography variant="h5" gutterBottom>
            {searchQuery ? "No Worlds Found" : "No Worlds Yet"}
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
            {searchQuery
              ? "Try a different search term"
              : "Build immersive worlds with detailed lore, locations, and histories"}
          </Typography>
          {!searchQuery && (
            <Button
              component={Link}
              to="/create/world"
              variant="contained"
              startIcon={<AddIcon />}
            >
              Create World
            </Button>
          )}
        </Card>
      ) : (
        <Grid container spacing={3}>
          {filteredWorlds.map((world) => (
            <Grid key={world.id} size={{ xs: 12, sm: 6, md: 4 }}>
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
                    {world.name}
                  </Typography>
                  <Typography
                    variant="body2"
                    color="text.secondary"
                    sx={{ mb: 2 }}
                  >
                    {truncateText(world.description)}
                  </Typography>
                  <Box sx={{ display: "flex", gap: 1, flexWrap: "wrap" }}>
                    {world.magic_system && (
                      <Chip
                        label={`Magic: ${world.magic_system}`}
                        size="small"
                        color="secondary"
                      />
                    )}
                    {world.technology_level && (
                      <Chip
                        label={`Tech: ${world.technology_level}`}
                        size="small"
                        color="primary"
                      />
                    )}
                    <Chip
                      label={formatDate(world.created_at)}
                      size="small"
                      variant="outlined"
                    />
                  </Box>
                </CardContent>
                <CardActions>
                  <Button
                    size="small"
                    component={Link}
                    to={`/worlds/${world.id}`}
                  >
                    View Details
                  </Button>
                  <Button
                    size="small"
                    color="secondary"
                    component={Link}
                    to={`/create/world?edit=${world.id}`}
                  >
                    Edit
                  </Button>
                  <IconButton
                    size="small"
                    color="error"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleDeleteClick(world);
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
        <DialogTitle>Delete World?</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to delete{" "}
            <strong>{worldToDelete?.name}</strong>? This action cannot be
            undone and will also delete all associated locations.
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
