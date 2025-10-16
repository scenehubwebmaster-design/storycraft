import {
  createFileRoute,
  Link,
  Outlet,
  useMatches,
} from "@tanstack/react-router";
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
} from "@mui/material";
import AddIcon from "@mui/icons-material/Add";
import PersonIcon from "@mui/icons-material/Person";
import SearchIcon from "@mui/icons-material/Search";
import DeleteIcon from "@mui/icons-material/Delete";
import ClearIcon from "@mui/icons-material/Clear";

export const Route = createFileRoute("/characters")({
  component: CharactersComponent,
});

const API_URL = "http://localhost:8000";

function CharactersComponent() {
  const matches = useMatches();
  const isChildRouteActive = matches.length > 2; // Root + /characters + child route

  const [characters, setCharacters] = useState([]);
  const [filteredCharacters, setFilteredCharacters] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [characterToDelete, setCharacterToDelete] = useState(null);
  const [deleting, setDeleting] = useState(false);

  // Load characters when returning to the list view
  useEffect(() => {
    if (!isChildRouteActive) {
      const loadCharacters = async () => {
        try {
          setLoading(true);
          const response = await axios.get(`${API_URL}/api/characters`);
          setCharacters(response.data);
          setError(null);
        } catch (err) {
          setError(err.response?.data?.detail || "Failed to load characters");
          console.error(err);
        } finally {
          setLoading(false);
        }
      };
      loadCharacters();
    }
  }, [isChildRouteActive]);

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

  // If a child route is active (like character detail), render the outlet
  if (isChildRouteActive) {
    return <Outlet />;
  }

  const handleDeleteClick = (character) => {
    setCharacterToDelete(character);
    setDeleteDialogOpen(true);
  };

  const handleDeleteConfirm = async () => {
    if (!characterToDelete) return;

    try {
      setDeleting(true);
      await axios.delete(`${API_URL}/api/characters/${characterToDelete.id}`);
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
          {error}
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
                {character.portrait_image ? (
                  <CardMedia
                    component="img"
                    height="240"
                    image={`data:image/png;base64,${character.portrait_image}`}
                    alt={character.name}
                    sx={{ objectFit: "cover" }}
                  />
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
                  <Typography variant="h6" gutterBottom>
                    {character.name}
                  </Typography>
                  <Typography
                    variant="body2"
                    color="text.secondary"
                    sx={{ mb: 2 }}
                  >
                    {(() => {
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
                  <Box sx={{ display: "flex", gap: 1, flexWrap: "wrap" }}>
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
    </Box>
  );
}
