import React, { useState, useEffect } from "react";
import axios from "axios";
import {
  Box,
  Chip,
  Typography,
  Card,
  CardContent,
  Grid,
  Button,
  CircularProgress,
  Snackbar,
  Alert,
} from "@mui/material";
import AutoAwesomeIcon from "@mui/icons-material/AutoAwesome";
import { API_URL } from "../config/api";

export default function NamePicker({
  nameOptions = [],
  onSelect = () => {},
  selectedName = "",
  provider = "groq",
  model = null,
  species = null,
  background = null,
  className = null,
}) {
  const [options, setOptions] = useState(
    Array.isArray(nameOptions) ? nameOptions : []
  );
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [snackOpen, setSnackOpen] = useState(false);
  const [retryCount, setRetryCount] = useState(0);

  const MAX_RETRIES = 3;

  useEffect(() => {
    if (Array.isArray(nameOptions)) setOptions(nameOptions);
  }, [nameOptions]);

  const renderDisplay = (opt) => {
    const parts = [opt.first_name || "", opt.surname || ""].filter(Boolean);
    const name = parts.join(" ");
    const subtitle = opt.title
      ? `${opt.title}`
      : opt.origin
      ? `${opt.origin}`
      : "";
    return { name, subtitle, meaning: opt.meaning };
  };

  const regenerate = async () => {
    setLoading(true);
    setError(null);
    try {
      const resp = await axios.post(`${API_URL}/api/generate/names/`, {
        provider,
        model,
        species,
        background,
        class_name: className,
      });
      const names = resp.data?.names ?? resp.data ?? [];
      const parsed = Array.isArray(names) ? names : [];
      if (parsed.length === 0) {
        setError("No names returned from generator");
        setSnackOpen(true);
      } else {
        setOptions(parsed);
        setSnackOpen(false);
      }
    } catch (e) {
      const msg = e?.response?.data?.detail || e?.message || String(e);
      setError(msg);
      setSnackOpen(true);
    } finally {
      setLoading(false);
    }
  };

  // Auto-trigger regenerate once on mount when no options were provided
  useEffect(() => {
    let mounted = true;
    (async () => {
      if (
        mounted &&
        (!Array.isArray(nameOptions) || nameOptions.length === 0)
      ) {
        if (retryCount < MAX_RETRIES) {
          setRetryCount((c) => c + 1);
          await regenerate();
        }
      }
    })();
    return () => {
      mounted = false;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <>
      <Card sx={{ mb: 2 }}>
        <CardContent>
          <Box
            sx={{
              mb: 1,
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
            }}
          >
            <Box>
              <Typography variant="subtitle1">
                Choose a Generated Name
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Select one of the AI-generated name options below
              </Typography>
            </Box>
            <Box>
              <Button
                size="small"
                onClick={regenerate}
                startIcon={loading ? <CircularProgress size={14} /> : null}
              >
                {loading ? "Generating..." : "Regenerate"}
              </Button>
            </Box>
          </Box>

          {error && (
            <Typography
              variant="caption"
              color="error"
              sx={{ display: "block", mb: 1 }}
            >
              {error}
            </Typography>
          )}

          <Grid container spacing={1}>
            {Array.isArray(options) && options.length > 0 ? (
              options.map((opt, idx) => {
                const d = renderDisplay(opt);
                const isSelected = selectedName === d.name;
                return (
                  <Grid item xs={12} sm={6} key={idx}>
                    <Box sx={{ display: "flex", gap: 1, alignItems: "center" }}>
                      <Chip
                        label={d.name}
                        color={isSelected ? "primary" : "default"}
                        onClick={() => onSelect(d.name)}
                        sx={{ fontWeight: isSelected ? 700 : 500 }}
                        icon={
                          opt._ai ? <AutoAwesomeIcon fontSize="small" /> : null
                        }
                      />
                      <Box sx={{ display: "flex", flexDirection: "column" }}>
                        <Typography variant="caption">{d.subtitle}</Typography>
                        {d.meaning && (
                          <Typography variant="caption" color="text.secondary">
                            {d.meaning}
                          </Typography>
                        )}
                      </Box>
                      {/* Small AI badge for accessibility and clarity */}
                      {opt._ai && (
                        <Box
                          sx={{
                            ml: 0.5,
                            display: "flex",
                            alignItems: "center",
                            gap: 0.5,
                          }}
                        >
                          <AutoAwesomeIcon fontSize="small" color="primary" />
                          <Typography
                            variant="caption"
                            sx={{ fontWeight: 600 }}
                          >
                            AI
                          </Typography>
                        </Box>
                      )}
                    </Box>
                  </Grid>
                );
              })
            ) : (
              <Grid item xs={12}>
                <Typography variant="body2" color="text.secondary">
                  No generated names yet. Click "Regenerate" to request new
                  options.
                </Typography>
              </Grid>
            )}
          </Grid>

          <Box sx={{ mt: 2, display: "flex", gap: 1 }}>
            <Button size="small" onClick={() => onSelect("")}>
              Clear
            </Button>
            <Button size="small" onClick={regenerate} disabled={loading}>
              {loading ? "Generating..." : "Regenerate"}
            </Button>
          </Box>
        </CardContent>
      </Card>

      <Snackbar
        open={snackOpen}
        autoHideDuration={6000}
        onClose={() => setSnackOpen(false)}
        anchorOrigin={{ vertical: "bottom", horizontal: "center" }}
      >
        <Alert
          onClose={() => setSnackOpen(false)}
          severity="error"
          action={
            <Button
              color="inherit"
              size="small"
              onClick={async () => {
                if (retryCount >= MAX_RETRIES) return setSnackOpen(false);
                setRetryCount((c) => c + 1);
                await regenerate();
              }}
            >
              Retry
            </Button>
          }
        >
          {error || "An error occurred while generating names"}
        </Alert>
      </Snackbar>
    </>
  );
}
