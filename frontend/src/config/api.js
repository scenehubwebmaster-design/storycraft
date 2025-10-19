/**
 * API Configuration
 *
 * Handles API base URL for different environments:
 * - Development: Uses backend server on port 8000
 * - Production: Uses same hostname as frontend
 */

const getApiUrl = () => {
  // In development, Vite dev server runs on 3000, backend on 8000
  // In production, both are served from the same origin
  const hostname = window.location.hostname;
  const isDev = import.meta.env.DEV;

  if (isDev) {
    // Development: point to backend server
    return `http://${hostname}:8000`;
  } else {
    // Production: same origin (handled by reverse proxy or same server)
    return `http://${hostname}:8000`;
  }
};

export const API_URL = getApiUrl();

// Log the API URL for debugging
console.log("[API Config] Using API URL:", API_URL);
