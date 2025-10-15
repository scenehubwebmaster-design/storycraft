import { useState, useEffect } from "react";
import {
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Box,
  Typography,
  Chip,
  Tooltip,
  CircularProgress,
  Alert,
} from "@mui/material";
import InfoIcon from "@mui/icons-material/Info";
import CheckCircleIcon from "@mui/icons-material/CheckCircle";
import SpeedIcon from "@mui/icons-material/Speed";
import MoneyOffIcon from "@mui/icons-material/MoneyOff";
import {
  useProviders,
  useProviderModels,
  getRecommendedModel,
  formatRateLimits,
} from "../hooks/useProviders";

/**
 * Enhanced Model Selector Component
 * Shows provider availability, models with rate limits, and recommendations
 */
export default function ModelSelector({
  provider,
  model,
  onProviderChange,
  onModelChange,
  contentType = "character",
}) {
  const {
    providers,
    loading: providersLoading,
    error: providersError,
  } = useProviders();
  const { models: detailedModels, loading: modelsLoading } =
    useProviderModels(provider);

  const [availableModels, setAvailableModels] = useState([]);
  const [recommendedModel, setRecommendedModel] = useState(null);

  // Get provider display name
  const getProviderName = (providerKey) => {
    const names = {
      openai: "OpenAI",
      anthropic: "Anthropic",
      google: "Google",
      groq: "Groq",
    };
    return names[providerKey] || providerKey;
  };

  // Get provider icon/badge
  const getProviderBadge = (providerKey) => {
    const badges = {
      groq: {
        label: "Fast",
        icon: <SpeedIcon fontSize="small" />,
        color: "success",
      },
      google: {
        label: "Free Tier",
        icon: <MoneyOffIcon fontSize="small" />,
        color: "primary",
      },
      openai: { label: "Premium", icon: null, color: "default" },
      anthropic: { label: "Premium", icon: null, color: "default" },
    };
    return badges[providerKey];
  };

  // Update available models when provider or providers data changes
  useEffect(() => {
    if (providers && provider) {
      const providerData = providers[provider];
      if (providerData?.models) {
        setAvailableModels(providerData.models);
      }
    }
  }, [providers, provider]);

  // Calculate recommended model
  useEffect(() => {
    if (provider && contentType) {
      const complexity = getTaskComplexity(contentType);
      const recommended = getRecommendedModel(provider, complexity);
      setRecommendedModel(recommended);
    }
  }, [provider, contentType]);

  // Auto-select recommended model if no model is selected
  useEffect(() => {
    if (
      !model &&
      recommendedModel &&
      availableModels.includes(recommendedModel)
    ) {
      onModelChange(recommendedModel);
    }
  }, [recommendedModel, availableModels, model, onModelChange]);

  // Get model details from detailed models
  const getModelDetails = (modelId) => {
    return detailedModels.find((m) => m.id === modelId);
  };

  // Get task complexity
  const getTaskComplexity = (type) => {
    const complexityMap = {
      character: "medium",
      story: "complex",
      world: "complex",
      scene: "medium",
      location: "simple",
    };
    return complexityMap[type] || "medium";
  };

  if (providersLoading) {
    return (
      <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
        <CircularProgress size={20} />
        <Typography variant="body2" color="text.secondary">
          Loading providers...
        </Typography>
      </Box>
    );
  }

  if (providersError) {
    return (
      <Alert severity="warning" sx={{ mb: 2 }}>
        Unable to fetch providers. Using defaults.
      </Alert>
    );
  }

  return (
    <Box sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
      {/* Provider Selector */}
      <FormControl fullWidth>
        <InputLabel>AI Provider</InputLabel>
        <Select
          value={provider}
          onChange={(e) => onProviderChange(e.target.value)}
          label="AI Provider"
        >
          {providers &&
            Object.entries(providers).map(([key, data]) => (
              <MenuItem key={key} value={key} disabled={!data.available}>
                <Box
                  sx={{
                    display: "flex",
                    alignItems: "center",
                    gap: 1,
                    width: "100%",
                  }}
                >
                  <Typography sx={{ flexGrow: 1 }}>
                    {getProviderName(key)}
                  </Typography>
                  {data.available ? (
                    <>
                      {getProviderBadge(key) && (
                        <Chip
                          label={getProviderBadge(key).label}
                          icon={getProviderBadge(key).icon}
                          size="small"
                          color={getProviderBadge(key).color}
                          sx={{ height: 20 }}
                        />
                      )}
                      <CheckCircleIcon fontSize="small" color="success" />
                    </>
                  ) : (
                    <Chip
                      label="Not Configured"
                      size="small"
                      color="error"
                      sx={{ height: 20 }}
                    />
                  )}
                </Box>
              </MenuItem>
            ))}
        </Select>
      </FormControl>

      {/* Model Selector */}
      <FormControl fullWidth>
        <InputLabel>Model</InputLabel>
        <Select
          value={model || ""}
          onChange={(e) => onModelChange(e.target.value)}
          label="Model"
          disabled={modelsLoading || availableModels.length === 0}
        >
          {modelsLoading ? (
            <MenuItem disabled>
              <CircularProgress size={16} sx={{ mr: 1 }} />
              Loading models...
            </MenuItem>
          ) : (
            availableModels.map((modelId) => {
              const details = getModelDetails(modelId);
              const isRecommended = modelId === recommendedModel;

              return (
                <MenuItem key={modelId} value={modelId}>
                  <Box
                    sx={{
                      display: "flex",
                      flexDirection: "column",
                      width: "100%",
                    }}
                  >
                    <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                      <Typography sx={{ flexGrow: 1 }}>
                        {details?.name || modelId}
                      </Typography>
                      {isRecommended && (
                        <Chip
                          label="Recommended"
                          size="small"
                          color="primary"
                          sx={{ height: 20 }}
                        />
                      )}
                    </Box>
                    {details?.rate_limits && (
                      <Typography variant="caption" color="text.secondary">
                        {formatRateLimits(details.rate_limits)}
                      </Typography>
                    )}
                  </Box>
                </MenuItem>
              );
            })
          )}
        </Select>
      </FormControl>

      {/* Info Box */}
      {model && (
        <Box
          sx={{
            p: 2,
            bgcolor: "background.paper",
            borderRadius: 1,
            border: "1px solid",
            borderColor: "divider",
          }}
        >
          <Box sx={{ display: "flex", alignItems: "flex-start", gap: 1 }}>
            <InfoIcon fontSize="small" color="primary" sx={{ mt: 0.5 }} />
            <Box sx={{ flexGrow: 1 }}>
              <Typography variant="body2" gutterBottom>
                <strong>Selected Model:</strong> {model}
              </Typography>
              {(() => {
                const details = getModelDetails(model);
                if (details?.rate_limits) {
                  return (
                    <Typography variant="caption" color="text.secondary">
                      Rate Limits: {formatRateLimits(details.rate_limits)}
                    </Typography>
                  );
                }
                return null;
              })()}
              {model === recommendedModel && (
                <Box sx={{ mt: 1 }}>
                  <Chip
                    label={`Recommended for ${contentType} generation`}
                    size="small"
                    color="primary"
                    variant="outlined"
                  />
                </Box>
              )}
            </Box>
          </Box>
        </Box>
      )}
    </Box>
  );
}
