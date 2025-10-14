import { useState, useEffect } from 'react';
import axios from 'axios';

const API_URL = 'http://localhost:8000';

/**
 * Custom hook to fetch and manage LLM providers and their available models
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
        const response = await axios.get(`${API_URL}/api/llm/providers`);
        setProviders(response.data);
        setError(null);
      } catch (err) {
        setError(err.message);
        console.error('Failed to fetch providers:', err);
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
 * @param {string} provider - Provider name (google, groq)
 * @returns {Object} Detailed model data
 */
export const useProviderModels = (provider) => {
  const [models, setModels] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!provider || (provider !== 'google' && provider !== 'groq')) {
      return;
    }

    const fetchModels = async () => {
      try {
        setLoading(true);
        const response = await axios.get(`${API_URL}/api/llm/${provider}/models`);
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
  if (!providers) return 'openai';
  
  const providerOrder = ['groq', 'google', 'anthropic', 'openai'];
  for (const provider of providerOrder) {
    if (providers[provider]?.available) {
      return provider;
    }
  }
  
  return 'openai'; // Default fallback
};

/**
 * Get recommended model based on task complexity
 * @param {string} provider - Provider name
 * @param {string} complexity - 'simple', 'medium', 'complex'
 * @returns {string|null} Recommended model ID
 */
export const getRecommendedModel = (provider, complexity = 'medium') => {
  const recommendations = {
    openai: {
      simple: 'gpt-3.5-turbo',
      medium: 'gpt-4',
      complex: 'gpt-4-turbo',
    },
    anthropic: {
      simple: 'claude-3-sonnet-20240229',
      medium: 'claude-3-5-sonnet-20241022',
      complex: 'claude-3-opus-20240229',
    },
    google: {
      simple: 'gemini-2.0-flash',
      medium: 'gemini-2.5-flash',
      complex: 'gemini-2.5-flash',
    },
    groq: {
      simple: 'llama-3.1-8b-instant',
      medium: 'llama-3.3-70b-versatile',
      complex: 'meta-llama/llama-4-scout-17b-16e-instruct',
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
    character: 'medium',
    story: 'complex',
    world: 'complex',
    scene: 'medium',
    location: 'simple',
  };

  return complexityMap[contentType] || 'medium';
};

/**
 * Format rate limit for display
 * @param {Object} rateLimits - Rate limit object
 * @returns {string} Formatted string
 */
export const formatRateLimits = (rateLimits) => {
  if (!rateLimits) return 'N/A';

  const parts = [];
  
  if (rateLimits.requests_per_minute) {
    parts.push(`${rateLimits.requests_per_minute} req/min`);
  }
  
  if (rateLimits.tokens_per_minute) {
    const tpm = rateLimits.tokens_per_minute >= 1000 
      ? `${(rateLimits.tokens_per_minute / 1000).toFixed(0)}K`
      : rateLimits.tokens_per_minute;
    parts.push(`${tpm} tok/min`);
  }
  
  if (rateLimits.requests_per_day) {
    const rpd = rateLimits.requests_per_day >= 1000
      ? `${(rateLimits.requests_per_day / 1000).toFixed(1)}K`
      : rateLimits.requests_per_day;
    parts.push(`${rpd} req/day`);
  }

  return parts.join(' • ') || 'N/A';
};
