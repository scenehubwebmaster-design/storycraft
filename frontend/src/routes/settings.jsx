import { createFileRoute } from "@tanstack/react-router";
import { useState, useEffect } from "react";
import axios from "axios";
import {
  Container,
  Typography,
  Box,
  Paper,
  TextField,
  Button,
  Grid,
  Alert,
  CircularProgress,
  IconButton,
  InputAdornment,
  Chip,
  Card,
  CardContent,
  Divider,
} from "@mui/material";
import VisibilityIcon from "@mui/icons-material/Visibility";
import VisibilityOffIcon from "@mui/icons-material/VisibilityOff";
import SaveIcon from "@mui/icons-material/Save";
import DeleteIcon from "@mui/icons-material/Delete";
import CheckCircleIcon from "@mui/icons-material/CheckCircle";
import ErrorIcon from "@mui/icons-material/Error";
import InfoIcon from "@mui/icons-material/Info";

export const Route = createFileRoute("/settings")({
  component: SettingsComponent,
});

const API_URL = "http://localhost:8000";

function SettingsComponent() {
  const [openaiKey, setOpenaiKey] = useState("");
  const [anthropicKey, setAnthropicKey] = useState("");
  const [googleKey, setGoogleKey] = useState("");

  const [showOpenaiKey, setShowOpenaiKey] = useState(false);
  const [showAnthropicKey, setShowAnthropicKey] = useState(false);
  const [showGoogleKey, setShowGoogleKey] = useState(false);

  const [keyStatus, setKeyStatus] = useState(null);
  const [providerStatus, setProviderStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  useEffect(() => {
    loadStatus();
  }, []);

  const loadStatus = async () => {
    setLoading(true);
    try {
      const [keysResponse, providersResponse] = await Promise.all([
        axios.get(`${API_URL}/api/settings/api-keys`),
        axios.get(`${API_URL}/api/settings/providers`),
      ]);

      setKeyStatus(keysResponse.data);
      setProviderStatus(providersResponse.data);
    } catch (err) {
      setError("Failed to load settings");
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    setSaving(true);
    setError(null);
    setSuccess(null);

    const keysToUpdate = {};
    if (openaiKey.trim()) keysToUpdate.openai_api_key = openaiKey.trim();
    if (anthropicKey.trim())
      keysToUpdate.anthropic_api_key = anthropicKey.trim();
    if (googleKey.trim()) keysToUpdate.google_api_key = googleKey.trim();

    if (Object.keys(keysToUpdate).length === 0) {
      setError("Please enter at least one API key");
      setSaving(false);
      return;
    }

    try {
      const response = await axios.post(
        `${API_URL}/api/settings/api-keys`,
        keysToUpdate
      );
      setSuccess(response.data.message);

      // Clear input fields
      setOpenaiKey("");
      setAnthropicKey("");
      setGoogleKey("");

      // Reload status
      await loadStatus();
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to save API keys");
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (provider) => {
    if (!confirm(`Are you sure you want to remove the ${provider} API key?`)) {
      return;
    }

    try {
      await axios.delete(`${API_URL}/api/settings/api-keys/${provider}`);
      setSuccess(`Successfully removed ${provider} API key`);
      await loadStatus();
    } catch (err) {
      setError(
        err.response?.data?.detail || `Failed to remove ${provider} API key`
      );
    }
  };

  const getProviderChip = (provider, providerData) => {
    if (!providerData) return null;

    if (providerData.available) {
      return (
        <Chip
          icon={<CheckCircleIcon />}
          label="Available"
          color="success"
          size="small"
        />
      );
    } else if (providerData.configured && !providerData.installed) {
      return (
        <Chip
          icon={<ErrorIcon />}
          label="Not Installed"
          color="error"
          size="small"
        />
      );
    } else if (providerData.installed && !providerData.configured) {
      return (
        <Chip
          icon={<InfoIcon />}
          label="Not Configured"
          color="warning"
          size="small"
        />
      );
    } else {
      return (
        <Chip
          icon={<ErrorIcon />}
          label="Unavailable"
          color="default"
          size="small"
        />
      );
    }
  };

  if (loading) {
    return (
      <Container>
        <Box sx={{ display: "flex", justifyContent: "center", py: 10 }}>
          <CircularProgress />
        </Box>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg">
      <Box sx={{ mb: 4 }}>
        <Typography variant="h3" gutterBottom sx={{ fontWeight: 700 }}>
          Settings
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Configure your AI provider API keys to enable story generation
        </Typography>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {success && (
        <Alert
          severity="success"
          sx={{ mb: 3 }}
          onClose={() => setSuccess(null)}
        >
          {success}
        </Alert>
      )}

      {/* Provider Status Cards */}
      <Typography variant="h5" gutterBottom sx={{ mb: 2 }}>
        Provider Status
      </Typography>
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid size={{ xs: 12, md: 4 }}>
          <Card>
            <CardContent>
              <Box
                sx={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  mb: 1,
                }}
              >
                <Typography variant="h6">OpenAI</Typography>
                {providerStatus &&
                  getProviderChip("openai", providerStatus.openai)}
              </Box>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                GPT-4, GPT-3.5
              </Typography>
              {keyStatus?.openai_configured && (
                <Box sx={{ mt: 2 }}>
                  <Typography variant="caption" color="text.secondary">
                    Current Key: {keyStatus.openai_api_key_preview}
                  </Typography>
                  <IconButton
                    size="small"
                    color="error"
                    onClick={() => handleDelete("openai")}
                    sx={{ ml: 1 }}
                  >
                    <DeleteIcon fontSize="small" />
                  </IconButton>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>

        <Grid size={{ xs: 12, md: 4 }}>
          <Card>
            <CardContent>
              <Box
                sx={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  mb: 1,
                }}
              >
                <Typography variant="h6">Anthropic</Typography>
                {providerStatus &&
                  getProviderChip("anthropic", providerStatus.anthropic)}
              </Box>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                Claude 3.5 Sonnet
              </Typography>
              {keyStatus?.anthropic_configured && (
                <Box sx={{ mt: 2 }}>
                  <Typography variant="caption" color="text.secondary">
                    Current Key: {keyStatus.anthropic_api_key_preview}
                  </Typography>
                  <IconButton
                    size="small"
                    color="error"
                    onClick={() => handleDelete("anthropic")}
                    sx={{ ml: 1 }}
                  >
                    <DeleteIcon fontSize="small" />
                  </IconButton>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>

        <Grid size={{ xs: 12, md: 4 }}>
          <Card>
            <CardContent>
              <Box
                sx={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  mb: 1,
                }}
              >
                <Typography variant="h6">Google</Typography>
                {providerStatus &&
                  getProviderChip("google", providerStatus.google)}
              </Box>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                Gemini Pro
              </Typography>
              {keyStatus?.google_configured && (
                <Box sx={{ mt: 2 }}>
                  <Typography variant="caption" color="text.secondary">
                    Current Key: {keyStatus.google_api_key_preview}
                  </Typography>
                  <IconButton
                    size="small"
                    color="error"
                    onClick={() => handleDelete("google")}
                    sx={{ ml: 1 }}
                  >
                    <DeleteIcon fontSize="small" />
                  </IconButton>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Divider sx={{ my: 4 }} />

      {/* API Key Configuration */}
      <Typography variant="h5" gutterBottom sx={{ mb: 2 }}>
        Add or Update API Keys
      </Typography>
      <Paper sx={{ p: 4 }}>
        <Grid container spacing={3}>
          <Grid size={{ xs: 12 }}>
            <TextField
              fullWidth
              label="OpenAI API Key"
              type={showOpenaiKey ? "text" : "password"}
              value={openaiKey}
              onChange={(e) => setOpenaiKey(e.target.value)}
              placeholder="sk-..."
              helperText="Get your API key from platform.openai.com"
              InputProps={{
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton
                      onClick={() => setShowOpenaiKey(!showOpenaiKey)}
                      edge="end"
                    >
                      {showOpenaiKey ? (
                        <VisibilityOffIcon />
                      ) : (
                        <VisibilityIcon />
                      )}
                    </IconButton>
                  </InputAdornment>
                ),
              }}
            />
          </Grid>

          <Grid size={{ xs: 12 }}>
            <TextField
              fullWidth
              label="Anthropic API Key"
              type={showAnthropicKey ? "text" : "password"}
              value={anthropicKey}
              onChange={(e) => setAnthropicKey(e.target.value)}
              placeholder="sk-ant-..."
              helperText="Get your API key from console.anthropic.com"
              InputProps={{
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton
                      onClick={() => setShowAnthropicKey(!showAnthropicKey)}
                      edge="end"
                    >
                      {showAnthropicKey ? (
                        <VisibilityOffIcon />
                      ) : (
                        <VisibilityIcon />
                      )}
                    </IconButton>
                  </InputAdornment>
                ),
              }}
            />
          </Grid>

          <Grid size={{ xs: 12 }}>
            <TextField
              fullWidth
              label="Google API Key"
              type={showGoogleKey ? "text" : "password"}
              value={googleKey}
              onChange={(e) => setGoogleKey(e.target.value)}
              placeholder="AIza..."
              helperText="Get your API key from makersuite.google.com/app/apikey"
              InputProps={{
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton
                      onClick={() => setShowGoogleKey(!showGoogleKey)}
                      edge="end"
                    >
                      {showGoogleKey ? (
                        <VisibilityOffIcon />
                      ) : (
                        <VisibilityIcon />
                      )}
                    </IconButton>
                  </InputAdornment>
                ),
              }}
            />
          </Grid>

          <Grid size={{ xs: 12 }}>
            <Button
              variant="contained"
              size="large"
              startIcon={saving ? <CircularProgress size={20} /> : <SaveIcon />}
              onClick={handleSave}
              disabled={saving}
              fullWidth
            >
              {saving ? "Saving..." : "Save API Keys"}
            </Button>
          </Grid>
        </Grid>
      </Paper>

      <Alert severity="info" sx={{ mt: 4 }}>
        <Typography variant="body2">
          <strong>Note:</strong> Your API keys are stored securely in a .env
          file on the server. They are never sent to the frontend or exposed in
          API responses. Each provider requires installing their respective
          Python package (openai, anthropic, google-generativeai).
        </Typography>
      </Alert>
    </Container>
  );
}
