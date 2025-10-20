import React, { useState } from "react";
import { MapContainer, TileLayer, Marker, Popup, useMap } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import iconRetinaUrl from "leaflet/dist/images/marker-icon-2x.png";
import iconUrl from "leaflet/dist/images/marker-icon.png";
import shadowUrl from "leaflet/dist/images/marker-shadow.png";
import RegionDraw from "./RegionDraw";
import L from "leaflet";
import MapClusterGroup from "./MapClusterGroup";

// Fix default icon path issues with bundlers (Vite)
try {
  // remove any existing _getIconUrl to avoid conflicts
  delete L.Icon.Default.prototype._getIconUrl;
} catch (e) {}
L.Icon.Default.mergeOptions({
  iconRetinaUrl,
  iconUrl,
  shadowUrl,
});

// markers: [{id, name, lat, lng, coordinates (optional string), location_image}]
export default function MapLeafletOverlay({
  markers = [],
  center = [0, 0],
  zoom = 2,
  tileUrl = "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
  attribution = "&copy; OpenStreetMap contributors",
  enableCluster = true,
  enableRegionDraw = false,
  onRegionCreated = null,
  // If rendering an image-overlay map, pass its intrinsic natural size here
  imageNaturalSize = null,
}) {
  // Compute center if markers present
  const computedCenter =
    markers && markers.length
      ? [markers[0].lat || center[0], markers[0].lng || center[1]]
      : center;
  const [clusterEnabled, setClusterEnabled] = useState(enableCluster);

  return (
    <div style={{ position: "relative" }}>
      <MapContainer
        center={computedCenter}
        zoom={zoom}
        style={{ height: "480px", width: "100%" }}
      >
        <TileLayer attribution={attribution} url={tileUrl} />
        {enableRegionDraw && (
          <RegionDrawBridge
            onCreated={onRegionCreated}
            imageNaturalSize={imageNaturalSize}
          />
        )}

        {clusterEnabled ? (
          <MapClusterGroup markers={markers} />
        ) : (
          markers.map((m) =>
            m.lat && m.lng ? (
              <Marker key={m.id} position={[m.lat, m.lng]}>
                <Popup>
                  <div style={{ maxWidth: 240 }}>
                    <strong>{m.name}</strong>
                    {m.location_image && (
                      <div style={{ marginTop: 8 }}>
                        <img
                          src={`data:image/png;base64,${m.location_image}`}
                          alt={m.name}
                          style={{ width: "100%", borderRadius: 6 }}
                        />
                      </div>
                    )}
                  </div>
                </Popup>
              </Marker>
            ) : null
          )
        )}

        {/* Recenter control */}
        <RecenterControl position={computedCenter} />
      </MapContainer>

      {/* Cluster toggle */}
      <div style={{ position: "absolute", top: 10, left: 10, zIndex: 1000 }}>
        <button
          onClick={() => setClusterEnabled(!clusterEnabled)}
          style={{
            padding: "6px 8px",
            borderRadius: 6,
            background: "white",
            border: "1px solid #ccc",
          }}
        >
          {clusterEnabled ? "Disable Clustering" : "Enable Clustering"}
        </button>
      </div>
    </div>
  );
}
function RecenterControl({ position }) {
  const map = useMap();
  return (
    <div style={{ position: "absolute", top: 10, right: 10, zIndex: 1000 }}>
      <button
        onClick={() => map.setView(position, Math.max(map.getZoom(), 3))}
        style={{
          padding: "6px 8px",
          borderRadius: 6,
          background: "white",
          border: "1px solid #ccc",
        }}
      >
        Recenter
      </button>
    </div>
  );
}

function RegionDrawBridge({ onCreated, imageNaturalSize }) {
  const map = useMap();
  // wrap created handler to indicate this is a geospatial map
  const wrapped = (bounds, layer) => {
    onCreated &&
      onCreated(bounds, {
        isImage: false,
        imageSize: imageNaturalSize || null,
        layer,
      });
  };
  return <RegionDraw map={map} onCreated={wrapped} />;
}
