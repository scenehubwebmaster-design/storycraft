import { useEffect } from "react";
import { useMap } from "react-leaflet";
import L from "leaflet";
import "leaflet.markercluster/dist/MarkerCluster.css";
import "leaflet.markercluster/dist/MarkerCluster.Default.css";

// markers: array of {id, name, lat, lng, location_image}
export default function MapClusterGroup({ markers = [], options = {} }) {
  const map = useMap();

  useEffect(() => {
    if (!map) return;

    // Create the marker cluster group
    const clusterGroup = L.markerClusterGroup(options);

    // Create markers and bind popups
    const created = markers
      .filter((m) => m && m.lat != null && m.lng != null)
      .map((m) => {
        const marker = L.marker([m.lat, m.lng]);
        let popupHtml = `<div style="max-width:240px"><strong>${escapeHtml(
          m.name || ""
        )}</strong>`;
        if (m.location_image) {
          popupHtml += `<div style="margin-top:8px"><img src="data:image/png;base64,${
            m.location_image
          }" alt="${escapeHtml(
            m.name || ""
          )}" style="width:100%;border-radius:6px"/></div>`;
        }
        popupHtml += `</div>`;
        marker.bindPopup(popupHtml);
        clusterGroup.addLayer(marker);
        return marker;
      });

    map.addLayer(clusterGroup);

    return () => {
      // Cleanup markers and cluster group
      created.forEach((m) => clusterGroup.removeLayer(m));
      if (map.hasLayer(clusterGroup)) map.removeLayer(clusterGroup);
    };
  }, [map, JSON.stringify(markers), JSON.stringify(options)]);

  return null;
}

function escapeHtml(str) {
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}
