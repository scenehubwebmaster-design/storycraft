import { Link } from "react-router-dom";
import { useState, useEffect } from "react";
import axios from "axios";
import {
  Typography,
  Box,
  Checkbox,
  Button,
  Grid,
  Card,
  CardContent,
  CardActions,
  CardMedia,
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
  Snackbar,
  Alert as MuiAlert,
} from "@mui/material";
import AddIcon from "@mui/icons-material/Add";
import PersonIcon from "@mui/icons-material/Person";
import SearchIcon from "@mui/icons-material/Search";
import DeleteIcon from "@mui/icons-material/Delete";
import ClearIcon from "@mui/icons-material/Clear";
import { API_URL } from "../config/api";

// Note: Removed global axios timeout that was causing issues with portrait loading
// Individual requests can set timeout via { timeout: 10000 } config if needed

export default function CharactersPage() {
  const [characters, setCharacters] = useState([]);
  const [filteredCharacters, setFilteredCharacters] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [characterToDelete, setCharacterToDelete] = useState(null);
  const [deleting, setDeleting] = useState(false);
  const [selectedIds, setSelectedIds] = useState(new Set());
  const [bulkDeleteDialogOpen, setBulkDeleteDialogOpen] = useState(false);
  const [lastDeletedIds, setLastDeletedIds] = useState([]);
  const [undoSnackbarOpen, setUndoSnackbarOpen] = useState(false);
  const [apiHealthy, setApiHealthy] = useState(null);
  const [portraits, setPortraits] = useState({}); // Cache for loaded portraits
  const [loadingPortraits, setLoadingPortraits] = useState({}); // Track which portraits are loading

  // Load portrait for a specific character - DEFINED FIRST so useEffect can call it
  const loadPortraitForCharacter = async (characterId) => {
    console.log(`[Characters] Loading portrait for character ${characterId}`);
    try {
      // Mark as loading
      setLoadingPortraits((prev) => ({ ...prev, [characterId]: true }));

      const response = await axios.get(
        `${API_URL}/api/characters/${characterId}/portrait/`
      );
      console.log(`[Characters] Portrait response for ${characterId}:`, {
        hasImage: !!response.data.portrait_image,
        imageLength: response.data.portrait_image?.length || 0,
      });

      if (response.data.portrait_image) {
        setPortraits((prev) => ({
          ...prev,
          [characterId]: response.data.portrait_image,
        }));
        console.log(`[Characters] Portrait loaded for ${characterId}`);
      } else {
        console.warn(
          `[Characters] No portrait_image in response for ${characterId}`
        );
      }
    } catch (err) {
      // Non-fatal - character card will show placeholder icon
      console.error(
        `[Characters] Failed to load portrait for character ${characterId}:`,
        err.message
      );
    } finally {
      // Mark as done loading
      setLoadingPortraits((prev) => ({ ...prev, [characterId]: false }));
    }
  };

  useEffect(() => {
    const checkApiAndLoadCharacters = async () => {
      try {
        setLoading(true);

        // First, check if the API is reachable
        console.log(
          "[Characters] Checking API health at:",
          `${API_URL}/health`
        );
        try {
          const healthResponse = await axios.get(`${API_URL}/health`, {
            timeout: 5000,
          });
          console.log("[Characters] API health check:", healthResponse.data);
          setApiHealthy(true);
        } catch (healthErr) {
          console.error(
            "[Characters] API health check failed:",
            healthErr.message
          );
          setApiHealthy(false);
          throw new Error(
            `Cannot reach backend API at ${API_URL}. Is the backend server running?`
          );
        }

        // Now load characters WITHOUT portraits for fast list display
        console.log("[Characters] Loading from API URL:", API_URL);
        const response = await axios.get(
          `${API_URL}/api/characters/?exclude_portrait=true`
        );
        console.log("[Characters] Loaded", response.data.length, "characters");
        setCharacters(response.data);
        setError(null);

        // Load portraits in the background for characters that have them
        console.log(
          `[Characters] Starting to load portraits for ${response.data.length} characters`
        );
        response.data.forEach((character) => {
          if (character.id) {
            console.log(
              `[Characters] Queueing portrait load for character ${character.id}`
            );
            loadPortraitForCharacter(character.id);
          }
        });
      } catch (err) {
        const errorMsg =
          err.response?.data?.detail ||
          err.message ||
          "Failed to load characters";
        console.error("[Characters] Error loading:", errorMsg);
        console.error("[Characters] Full error:", err);
        setError(`${errorMsg} (API: ${API_URL})`);
      } finally {
        setLoading(false);
      }
    };
    checkApiAndLoadCharacters();
  }, []);

  // Filter characters based on search query
  useEffect(() => {
    if (!searchQuery.trim()) {
      setFilteredCharacters(characters);
      return;
    }

    const query = searchQuery.toLowerCase();
    const filtered = characters.filter(
      (char) =>
        char.name?.toLowerCase().includes(query) ||
        char.description?.toLowerCase().includes(query) ||
        char.personality?.toLowerCase().includes(query) ||
        char.background?.toLowerCase().includes(query)
    );
    setFilteredCharacters(filtered);
  }, [searchQuery, characters]);

  const handleDeleteClick = (character) => {
    setCharacterToDelete(character);
    setDeleteDialogOpen(true);
  };

  const toggleSelect = (id) => {
    setSelectedIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  const selectAll = () => {
    if (selectedIds.size === filteredCharacters.length) {
      setSelectedIds(new Set());
    } else {
      setSelectedIds(new Set(filteredCharacters.map((c) => c.id)));
    }
  };

  const handleBulkDeleteConfirm = async () => {
    if (selectedIds.size === 0) return;
    try {
      setDeleting(true);
      // Use batch delete endpoint for efficiency
      const ids = Array.from(selectedIds);
      const resp = await axios.post(`${API_URL}/api/characters/bulk-delete/`, {
        ids,
      });
      const deleted = resp.data.deleted || [];
      setCharacters((prev) => prev.filter((c) => !deleted.includes(c.id)));
      setSelectedIds(new Set());
      setBulkDeleteDialogOpen(false);
      // Store deleted ids for possible undo
      setLastDeletedIds(deleted);
      setUndoSnackbarOpen(true);
    } catch (err) {
      setError(
        err.response?.data?.detail || "Failed to delete selected characters"
      );
    } finally {
      setDeleting(false);
    }
  };

  const handleUndo = async () => {
    if (!lastDeletedIds || lastDeletedIds.length === 0) return;
    try {
      // Call restore endpoint
      const resp = await axios.post(`${API_URL}/api/characters/restore/`, {
        ids: lastDeletedIds,
      });
      const restored = resp.data.restored || [];
      if (restored.length) {
        // Fetch restored characters and append to list (simple approach: refetch page)
        const fetchResp = await axios.get(
          `${API_URL}/api/characters/?exclude_portraits=true`
        );
        setCharacters(fetchResp.data);
      }
    } catch (err) {
      // Show error in snackbar area
      setError(err.response?.data?.detail || "Failed to restore characters");
    } finally {
      setLastDeletedIds([]);
      setUndoSnackbarOpen(false);
    }
  };

  const handleDeleteConfirm = async () => {
    if (!characterToDelete) return;

    try {
      setDeleting(true);
      // Ensure trailing slash to match FastAPI route (avoids 405 Method Not Allowed)
      await axios.delete(`${API_URL}/api/characters/${characterToDelete.id}/`);
      setCharacters(characters.filter((c) => c.id !== characterToDelete.id));
      setDeleteDialogOpen(false);
      setCharacterToDelete(null);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to delete character");
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
            Characters
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ mt: 1 }}>
            {filteredCharacters.length} character
            {filteredCharacters.length !== 1 ? "s" : ""}
            {searchQuery && ` (filtered from ${characters.length})`}
          </Typography>
        </Box>
        <Button
          component={Link}
          to="/create/character"
          variant="contained"
          startIcon={<AddIcon />}
        >
          New Character
        </Button>
      </Box>

      {/* Selection toolbar for bulk actions */}
      <Box sx={{ display: "flex", gap: 2, alignItems: "center", mb: 2 }}>
        <Button variant="outlined" size="small" onClick={selectAll}>
          {selectedIds.size === filteredCharacters.length &&
          filteredCharacters.length > 0
            ? "Clear selection"
            : "Select all"}
        </Button>
        <Button
          variant="contained"
          color="error"
          size="small"
          disabled={selectedIds.size === 0}
          onClick={() => setBulkDeleteDialogOpen(true)}
        >
          Delete selected ({selectedIds.size})
        </Button>
      </Box>

      {/* Search Bar */}
      <TextField
        fullWidth
        variant="outlined"
        placeholder="Search characters by name, description, personality, or background..."
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
          <Typography variant="body2" sx={{ fontWeight: 600, mb: 1 }}>
            {error}
          </Typography>
          {apiHealthy === false && (
            <Typography variant="body2" sx={{ mt: 1 }}>
              <strong>Troubleshooting:</strong>
              <br />
              1. Make sure the backend server is running on port 8000
              <br />
              2. Check if you can access:{" "}
              <a
                href={`${API_URL}/health`}
                target="_blank"
                rel="noopener noreferrer"
              >
                {API_URL}/health
              </a>
              <br />
              3. Verify both frontend and mobile device are on the same WiFi
              network
            </Typography>
          )}
        </Alert>
      )}

      {filteredCharacters.length === 0 ? (
        <Card
          sx={{
            p: 4,
            textAlign: "center",
            backgroundColor: "background.default",
          }}
        >
          <PersonIcon sx={{ fontSize: 80, color: "text.secondary", mb: 2 }} />
          <Typography variant="h5" gutterBottom>
            {searchQuery ? "No Characters Found" : "No Characters Yet"}
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
            {searchQuery
              ? "Try a different search term"
              : "Create your first character to get started"}
          </Typography>
          {!searchQuery && (
            <Button
              component={Link}
              to="/create/character"
              variant="contained"
              startIcon={<AddIcon />}
            >
              Create Character
            </Button>
          )}
        </Card>
      ) : (
        <Grid container spacing={3}>
          {filteredCharacters.map((character) => (
            <Grid key={character.id} size={{ xs: 12, sm: 6, md: 4 }}>
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
                {/* Checkbox moved into card header for consistent layout */}
                {portraits[character.id] ? (
                  <CardMedia
                    component="img"
                    height="240"
                    image={`data:image/png;base64,${portraits[character.id]}`}
                    alt={character.name}
                    sx={{ objectFit: "contain" }}
                  />
                ) : loadingPortraits[character.id] ? (
                  <Box
                    sx={{
                      height: 240,
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      backgroundColor: "background.default",
                    }}
                  >
                    <CircularProgress />
                  </Box>
                ) : (
                  <Box
                    sx={{
                      height: 240,
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      backgroundColor: "background.default",
                    }}
                  >
                    <PersonIcon
                      sx={{ fontSize: 80, color: "text.secondary" }}
                    />
                  </Box>
                )}
                <CardContent sx={{ flexGrow: 1 }}>
                  <Box
                    sx={{
                      display: "flex",
                      alignItems: "center",
                      gap: 1,
                      mb: 1,
                    }}
                  >
                    <Checkbox
                      checked={selectedIds.has(character.id)}
                      onChange={() => toggleSelect(character.id)}
                      onClick={(e) => e.stopPropagation()}
                      size="small"
                    />
                    <Typography variant="h6">{character.name}</Typography>
                    {character.is_dnd && (
                      <Chip
                        label="D&D"
                        size="small"
                        color="error"
                        sx={{ fontWeight: 600 }}
                      />
                    )}
                  </Box>
                  <Typography
                    variant="body2"
                    color="text.secondary"
                    sx={{ mb: 2 }}
                  >
                    {(() => {
                      // For D&D characters, show class and level
                      if (character.is_dnd) {
                        const parts = [];
                        if (character.dnd_level)
                          parts.push(`Level ${character.dnd_level}`);
                        if (character.dnd_class)
                          parts.push(character.dnd_class);
                        if (character.dnd_species)
                          parts.push(character.dnd_species);
                        return parts.join(" • ") || "D&D Character";
                      }
                      // For structured characters, show a summary from structured_data
                      if (character.structured_data) {
                        try {
                          const data =
                            typeof character.structured_data === "string"
                              ? JSON.parse(character.structured_data)
                              : character.structured_data;

                          // Build a summary from key fields
                          const parts = [];
                          if (data.age) parts.push(`Age: ${data.age}`);

                          // Add personality traits (first 3 for brevity)
                          if (data.personality_traits?.length) {
                            const traits = Array.isArray(
                              data.personality_traits
                            )
                              ? data.personality_traits.slice(0, 3).join(", ")
                              : data.personality_traits;
                            parts.push(traits);
                          } else if (data.personality_description) {
                            // Use personality description if no traits array
                            parts.push(data.personality_description);
                          }

                          // Add brief backstory if space permits
                          if (
                            data.backstory &&
                            parts.join(" • ").length < 120
                          ) {
                            parts.push(data.backstory);
                          } else if (
                            data.upbringing &&
                            parts.join(" • ").length < 120
                          ) {
                            parts.push(data.upbringing);
                          }

                          return truncateText(
                            parts.join(" • ") ||
                              character.description ||
                              "No description",
                            180
                          );
                        } catch (e) {
                          return truncateText(
                            character.description || "No description"
                          );
                        }
                      }
                      // For legacy characters, show description
                      return truncateText(
                        character.description || "No description"
                      );
                    })()}
                  </Typography>
                  <Box
                    sx={{
                      display: "flex",
                      gap: 1,
                      flexWrap: "wrap",
                      alignItems: "center",
                    }}
                  >
                    {character.is_dnd && (
                      <Chip
                        label="D&D 5E"
                        size="small"
                        color="error"
                        variant="filled"
                      />
                    )}
                    {character.structured_data && !character.is_dnd && (
                      <Chip
                        label="Structured"
                        size="small"
                        color="primary"
                        variant="outlined"
                      />
                    )}
                    <Chip
                      label={formatDate(character.created_at)}
                      size="small"
                      variant="outlined"
                    />
                  </Box>
                </CardContent>
                <CardActions>
                  <Button
                    size="small"
                    component={Link}
                    to={`/characters/${character.id}`}
                  >
                    View Details
                  </Button>
                  <Button
                    size="small"
                    color="secondary"
                    component={Link}
                    to={`/create/character?edit=${character.id}`}
                  >
                    Edit
                  </Button>
                  <IconButton
                    size="small"
                    color="error"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleDeleteClick(character);
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
        <DialogTitle>Delete Character?</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to delete{" "}
            <strong>{characterToDelete?.name}</strong>? This action cannot be
            undone.
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

      {/* Bulk Delete Confirmation Dialog */}
      <Dialog
        open={bulkDeleteDialogOpen}
        onClose={() => !deleting && setBulkDeleteDialogOpen(false)}
      >
        <DialogTitle>Delete Selected Characters?</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to delete <strong>{selectedIds.size}</strong>{" "}
            selected character{selectedIds.size !== 1 ? "s" : ""}? This action
            cannot be undone.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button
            onClick={() => setBulkDeleteDialogOpen(false)}
            disabled={deleting}
          >
            Cancel
          </Button>
          <Button
            onClick={handleBulkDeleteConfirm}
            color="error"
            variant="contained"
            disabled={deleting || selectedIds.size === 0}
          >
            {deleting ? "Deleting..." : `Delete (${selectedIds.size})`}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Undo snackbar after bulk delete */}
      <Snackbar
        open={undoSnackbarOpen}
        autoHideDuration={8000}
        onClose={() => setUndoSnackbarOpen(false)}
        anchorOrigin={{ vertical: "bottom", horizontal: "left" }}
      >
        <MuiAlert
          elevation={6}
          variant="filled"
          severity="info"
          action={
            <Button color="inherit" size="small" onClick={handleUndo}>
              UNDO
            </Button>
          }
        >
          Deleted {lastDeletedIds.length} character
          {lastDeletedIds.length !== 1 ? "s" : ""}.
        </MuiAlert>
      </Snackbar>
    </Box>
  );
}
