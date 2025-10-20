import React from "react";

// Lightweight shim for react-leaflet-cluster for environments where
// the original package is not installed or incompatible. This shim
// simply renders children directly and provides a compatible API for
// MarkerClusterGroup usage in the codebase. Replace with a proper
// clustering implementation when ready.
export default function MarkerClusterGroup({ children, ...props }) {
  return <>{children}</>;
}
