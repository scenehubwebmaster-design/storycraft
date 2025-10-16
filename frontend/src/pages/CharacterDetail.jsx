import { Link, useNavigate, useParams } from "react-router-dom";
import { useState, useEffect } from "react";
import axios from "axios";
import {
  Typography,
  Box,
  Button,
  Card,
  CardContent,
  CardMedia,
  CircularProgress,
  Alert,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Grid,
  Divider,
} from "@mui/material";
import EditIcon from "@mui/icons-material/Edit";
import DeleteIcon from "@mui/icons-material/Delete";
import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import PersonIcon from "@mui/icons-material/Person";
import StructuredCharacterDisplay from "../components/StructuredCharacterDisplay";
import { API_URL } from "../config/api";

export default function CharacterDetailPage() {
  const { characterId } = useParams();
  const navigate = useNavigate();
  const [character, setCharacter] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    loadCharacter();
  }, [characterId]);

  const loadCharacter = async () => {
    try {
      setLoading(true);
      const response = await axios.get(
        `${API_URL}/api/characters/${characterId}`
      );
      const characterData = response.data;

      // Parse structured_data if it's a JSON string
      if (
        characterData.structured_data &&
        typeof characterData.structured_data === "string"
      ) {
        try {
          characterData.structured_data = JSON.parse(
            characterData.structured_data
          );
        } catch (e) {
          console.error("Failed to parse structured_data:", e);
          // Leave it as string if parsing fails
        }
      }

      setCharacter(characterData);
      setError(null);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to load character");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    try {
      setDeleting(true);
      await axios.delete(`${API_URL}/api/characters/${characterId}`);
      navigate({ to: "/characters" });
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to delete character");
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
        <Button component={Link} to="/characters" startIcon={<ArrowBackIcon />}>
          Back to Characters
        </Button>
      </Box>
    );
  }

  if (!character) {
    return (
      <Box>
        <Alert severity="warning" sx={{ mb: 3 }}>
          Character not found
        </Alert>
        <Button component={Link} to="/characters" startIcon={<ArrowBackIcon />}>
          Back to Characters
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
          to="/characters"
          startIcon={<ArrowBackIcon />}
          sx={{ mb: 2 }}
        >
          Back to Characters
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
              {character.name}
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
              Created: {formatDate(character.created_at)}
            </Typography>
            {character.updated_at &&
              character.updated_at !== character.created_at && (
                <Typography
                  variant="body2"
                  color="text.secondary"
                  sx={{ mt: 0.5 }}
                >
                  Updated: {formatDate(character.updated_at)}
                </Typography>
              )}
          </Box>
          <Box sx={{ display: "flex", gap: 2 }}>
            <Button
              variant="outlined"
              startIcon={<EditIcon />}
              component={Link}
              to={`/create/character?edit=${characterId}`}
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

      <Grid container spacing={3}>
        {/* Portrait Card */}
        <Grid size={{ xs: 12, md: 3 }}>
          <Card>
            {character.portrait_image ? (
              <CardMedia
                component="img"
                image={`data:image/png;base64,${character.portrait_image}`}
                alt={character.name}
                sx={{ width: "100%", height: "auto" }}
              />
            ) : (
              <Box
                sx={{
                  height: 400,
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  backgroundColor: "background.default",
                }}
              >
                <PersonIcon sx={{ fontSize: 120, color: "text.secondary" }} />
              </Box>
            )}
            {character.image_prompt && (
              <CardContent>
                <Typography variant="caption" color="text.secondary">
                  <strong>Image Prompt:</strong>
                  <br />
                  {character.image_prompt}
                </Typography>
              </CardContent>
            )}
          </Card>
        </Grid>

        {/* Navigation Sidebar - Only show for structured characters */}
        {character.structured_data && (
          <Grid
            size={{ xs: 12, md: 2 }}
            sx={{ display: { xs: "none", md: "block" } }}
          >
            <Card
              sx={{
                position: "sticky",
                top: 16,
                maxHeight: "calc(100vh - 250px)",
                overflowY: "auto",
              }}
            >
              <CardContent sx={{ py: 2, px: 1.5 }}>
                <Typography
                  variant="caption"
                  sx={{
                    fontWeight: 600,
                    textTransform: "uppercase",
                    color: "text.secondary",
                    mb: 1,
                    display: "block",
                  }}
                >
                  Sections
                </Typography>
                <Box
                  component="nav"
                  sx={{
                    display: "flex",
                    flexDirection: "column",
                    gap: 0.5,
                  }}
                >
                  {[
                    { id: "physical", label: "Physical" },
                    { id: "personality", label: "Personality" },
                    { id: "background", label: "Background" },
                    { id: "motivations", label: "Motivations" },
                    { id: "fears", label: "Fears" },
                    { id: "strengths", label: "Strengths" },
                    { id: "relationships", label: "Relationships" },
                    { id: "arc", label: "Character Arc" },
                    { id: "unique", label: "Unique Qualities" },
                  ].map((section) => (
                    <Button
                      key={section.id}
                      size="small"
                      onClick={() => {
                        const element = document.getElementById(section.id);
                        if (element) {
                          element.scrollIntoView({
                            behavior: "smooth",
                            block: "start",
                          });
                        }
                      }}
                      sx={{
                        justifyContent: "flex-start",
                        textAlign: "left",
                        py: 0.75,
                        px: 1.5,
                        fontSize: "0.8rem",
                        color: "text.secondary",
                        textTransform: "none",
                        "&:hover": {
                          backgroundColor: "action.hover",
                          color: "primary.main",
                        },
                      }}
                    >
                      {section.label}
                    </Button>
                  ))}
                </Box>
              </CardContent>
            </Card>
          </Grid>
        )}

        {/* Details Card - Scrollable */}
        <Grid size={{ xs: 12, md: character.structured_data ? 7 : 9 }}>
          <Box
            sx={{
              maxHeight: { md: "calc(100vh - 250px)" },
              overflowY: "auto",
              overflowX: "hidden",
              pr: 1,
              "&::-webkit-scrollbar": {
                width: "8px",
              },
              "&::-webkit-scrollbar-track": {
                backgroundColor: "background.default",
                borderRadius: "4px",
              },
              "&::-webkit-scrollbar-thumb": {
                backgroundColor: "divider",
                borderRadius: "4px",
                "&:hover": {
                  backgroundColor: "text.secondary",
                },
              },
            }}
          >
            {/* Check if character has structured data */}
            {character.structured_data ? (
              // Display structured character profile
              <Box>
                <Box
                  sx={{
                    mb: 2,
                    p: 2,
                    bgcolor: "primary.main",
                    color: "white",
                    borderRadius: 1,
                    display: "flex",
                    alignItems: "center",
                    gap: 1,
                  }}
                >
                  <Chip
                    label="Structured Profile"
                    size="small"
                    sx={{ bgcolor: "rgba(255,255,255,0.2)", color: "white" }}
                  />
                  <Typography variant="body2">
                    This character uses the new structured format with organized
                    sections
                  </Typography>
                </Box>
                <StructuredCharacterDisplay
                  characterProfile={character.structured_data}
                />
              </Box>
            ) : (
              // Display legacy character format
              <Card>
                <CardContent>
                  {/* Description */}
                  {character.description && (
                    <Box sx={{ mb: 3 }}>
                      <Typography
                        variant="h6"
                        gutterBottom
                        sx={{ fontWeight: 600 }}
                      >
                        Description
                      </Typography>
                      <Typography
                        variant="body1"
                        sx={{ whiteSpace: "pre-wrap" }}
                      >
                        {character.description}
                      </Typography>
                    </Box>
                  )}

                  <Divider sx={{ my: 3 }} />

                  {/* Appearance */}
                  {character.appearance && (
                    <Box sx={{ mb: 3 }}>
                      <Typography
                        variant="h6"
                        gutterBottom
                        sx={{ fontWeight: 600 }}
                      >
                        Appearance
                      </Typography>
                      <Typography
                        variant="body1"
                        sx={{ whiteSpace: "pre-wrap" }}
                      >
                        {character.appearance}
                      </Typography>
                    </Box>
                  )}

                  {character.appearance && character.personality && (
                    <Divider sx={{ my: 3 }} />
                  )}

                  {/* Personality */}
                  {character.personality && (
                    <Box sx={{ mb: 3 }}>
                      <Typography
                        variant="h6"
                        gutterBottom
                        sx={{ fontWeight: 600 }}
                      >
                        Personality
                      </Typography>
                      <Typography
                        variant="body1"
                        sx={{ whiteSpace: "pre-wrap" }}
                      >
                        {character.personality}
                      </Typography>
                    </Box>
                  )}

                  {character.personality && character.background && (
                    <Divider sx={{ my: 3 }} />
                  )}

                  {/* Background */}
                  {character.background && (
                    <Box sx={{ mb: 3 }}>
                      <Typography
                        variant="h6"
                        gutterBottom
                        sx={{ fontWeight: 600 }}
                      >
                        Background
                      </Typography>
                      <Typography
                        variant="body1"
                        sx={{ whiteSpace: "pre-wrap" }}
                      >
                        {character.background}
                      </Typography>
                    </Box>
                  )}

                  {character.background && character.motivations && (
                    <Divider sx={{ my: 3 }} />
                  )}

                  {/* Motivations */}
                  {character.motivations && (
                    <Box sx={{ mb: 3 }}>
                      <Typography
                        variant="h6"
                        gutterBottom
                        sx={{ fontWeight: 600 }}
                      >
                        Motivations
                      </Typography>
                      <Typography
                        variant="body1"
                        sx={{ whiteSpace: "pre-wrap" }}
                      >
                        {character.motivations}
                      </Typography>
                    </Box>
                  )}

                  {character.motivations && character.relationships && (
                    <Divider sx={{ my: 3 }} />
                  )}

                  {/* Relationships */}
                  {character.relationships && (
                    <Box>
                      <Typography
                        variant="h6"
                        gutterBottom
                        sx={{ fontWeight: 600 }}
                      >
                        Relationships
                      </Typography>
                      <Typography
                        variant="body1"
                        sx={{ whiteSpace: "pre-wrap" }}
                      >
                        {typeof character.relationships === "string"
                          ? character.relationships
                          : JSON.stringify(character.relationships, null, 2)}
                      </Typography>
                    </Box>
                  )}
                </CardContent>
              </Card>
            )}
          </Box>
        </Grid>
      </Grid>

      {/* Delete Confirmation Dialog */}
      <Dialog
        open={deleteDialogOpen}
        onClose={() => !deleting && setDeleteDialogOpen(false)}
      >
        <DialogTitle>Delete Character?</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to delete <strong>{character.name}</strong>?
            This action cannot be undone.
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
