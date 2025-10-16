/**
 * API Configuration
 * 
 * Dynamically determines the API base URL based on the current hostname.
 * This allows the app to work both locally and when accessed from mobile devices
 * on the same network.
 * 
 * Examples:
 * - localhost:3000 → http://localhost:8000
 * - 192.168.1.100:3000 → http://192.168.1.100:8000
 */

const getApiUrl = () => {
  // In development, use the current hostname but port 8000
  if (import.meta.env.DEV) {
    const hostname = window.location.hostname;
    return `http://${hostname}:8000`;
  }
  
  // In production, you might want to use an environment variable
  return import.meta.env.VITE_API_URL || `http://${window.location.hostname}:8000`;
};

export const API_URL = getApiUrl();

// Log the API URL for debugging
console.log('[API Config] Using API URL:', API_URL);
