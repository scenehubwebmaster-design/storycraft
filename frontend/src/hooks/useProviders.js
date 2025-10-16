import { useState, useEffect } from "react";
import axios from "axios";
import { API_URL } from "../config/api";

/**
 * Custom hook to fetch and manage LLM providers and their available models
 * This hook now uses the unified endpoint that checks API key configuration
 * and only returns models for providers with valid API keys.
 * @returns {Object} Provider data and state
 */
export const useProviders = () => {
  const [providers, setProviders] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchProviders = async () => {
      try {
        setLoading(true);
        // Use the new unified endpoint that checks API keys
        const response = await axios.get(`${API_URL}/api/llm/models/available`);

        // Transform the response to match the expected format
        // Response format: { providers: { openai: { models: [...], count: N }, ... }, provider_status: {...} }
        const transformedData = {};

        if (response.data.providers) {
          Object.entries(response.data.providers).forEach(
            ([provider, data]) => {
              transformedData[provider] = {
                available: data.api_key_configured,
                models: data.models.map((m) => m.id), // Extract model IDs for quick selection
                model_details: data.models, // Keep full model data for details
                count: data.count,
              };
            }
          );
        }

        // Add provider status information
        if (response.data.provider_status) {
          Object.entries(response.data.provider_status).forEach(
            ([provider, status]) => {
              if (!transformedData[provider]) {
                transformedData[provider] = {
                  available: false,
                  models: [],
                  model_details: [],
                  count: 0,
                  status: status,
                };
              } else {
                transformedData[provider].status = status;
              }
            }
          );
        }

        setProviders(transformedData);
        setError(null);
      } catch (err) {
        setError(err.message);
        console.error("Failed to fetch providers:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchProviders();
  }, []);

  return { providers, loading, error };
};

/**
 * Custom hook to fetch detailed models for a specific provider
 * Supports all providers: openai, anthropic, google, groq
 * @param {string} provider - Provider name (openai, anthropic, google, groq)
 * @returns {Object} Detailed model data
 */
export const useProviderModels = (provider) => {
  const [models, setModels] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!provider) {
      return;
    }

    const fetchModels = async () => {
      try {
        setLoading(true);
        const response = await axios.get(
          `${API_URL}/api/llm/${provider}/models`
        );
        setModels(response.data.models || []);
        setError(null);
      } catch (err) {
        setError(err.message);
        console.error(`Failed to fetch ${provider} models:`, err);
        setModels([]);
      } finally {
        setLoading(false);
      }
    };

    fetchModels();
  }, [provider]);

  return { models, loading, error };
};

/**
 * Get the first available provider
 * @param {Object} providers - Providers object from useProviders
 * @returns {string} Provider name
 */
export const getFirstAvailableProvider = (providers) => {
  if (!providers) return "openai";

  const providerOrder = ["groq", "google", "anthropic", "openai"];
  for (const provider of providerOrder) {
    if (providers[provider]?.available) {
      return provider;
    }
  }

  return "openai"; // Default fallback
};

/**
 * Get recommended model based on task complexity
 * @param {string} provider - Provider name
 * @param {string} complexity - 'simple', 'medium', 'complex'
 * @returns {string|null} Recommended model ID
 */
export const getRecommendedModel = (provider, complexity = "medium") => {
  const recommendations = {
    openai: {
      simple: "gpt-3.5-turbo",
      medium: "gpt-4",
      complex: "gpt-4-turbo",
    },
    anthropic: {
      simple: "claude-3-sonnet-20240229",
      medium: "claude-3-5-sonnet-20241022",
      complex: "claude-3-opus-20240229",
    },
    google: {
      simple: "gemini-2.0-flash",
      medium: "gemini-2.5-flash",
      complex: "gemini-2.5-flash",
    },
    groq: {
      simple: "llama-3.1-8b-instant",
      // Updated: Use Llama 4 Scout for medium/complex tasks - supports structured outputs
      // Only these models support json_schema: llama-4-scout, llama-4-maverick, gpt-oss, kimi-k2
      // See: https://console.groq.com/docs/structured-outputs#supported-models
      medium: "meta-llama/llama-4-scout-17b-16e-instruct",
      complex: "meta-llama/llama-4-scout-17b-16e-instruct",
    },
  };

  return recommendations[provider]?.[complexity] || null;
};

/**
 * Get task complexity based on content type
 * @param {string} contentType - 'character', 'story', 'world', 'scene', 'location'
 * @returns {string} Complexity level
 */
export const getTaskComplexity = (contentType) => {
  const complexityMap = {
    character: "medium",
    story: "complex",
    world: "complex",
    scene: "medium",
    location: "simple",
  };

  return complexityMap[contentType] || "medium";
};

/**
 * Format rate limit for display
 * @param {Object} rateLimits - Rate limit object
 * @returns {string} Formatted string
 */
export const formatRateLimits = (rateLimits) => {
  if (!rateLimits) return "N/A";

  const parts = [];

  if (rateLimits.requests_per_minute) {
    parts.push(`${rateLimits.requests_per_minute} req/min`);
  }

  if (rateLimits.tokens_per_minute) {
    const tpm =
      rateLimits.tokens_per_minute >= 1000
        ? `${(rateLimits.tokens_per_minute / 1000).toFixed(0)}K`
        : rateLimits.tokens_per_minute;
    parts.push(`${tpm} tok/min`);
  }

  if (rateLimits.requests_per_day) {
    const rpd =
      rateLimits.requests_per_day >= 1000
        ? `${(rateLimits.requests_per_day / 1000).toFixed(1)}K`
        : rateLimits.requests_per_day;
    parts.push(`${rpd} req/day`);
  }

  return parts.join(" • ") || "N/A";
};
