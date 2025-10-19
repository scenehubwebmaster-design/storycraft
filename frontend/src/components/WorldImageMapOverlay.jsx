import React, { useEffect, useState, useRef } from "react";
import {
  MapContainer,
  ImageOverlay,
  Marker,
  Popup,
  useMap,
} from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import RegionDraw from "./RegionDraw";

// Helper component to set view to bounds once image is loaded
function FitBounds({ bounds }) {
  const map = useMap();
  useEffect(() => {
    if (bounds) map.fitBounds(bounds, { padding: [20, 20] });
  }, [map, bounds]);
  return null;
}

// markers: [{id, name, coordinates: 'x,y' percent or 'lat,lng', location_image}]
export default function WorldImageMapOverlay({
  imageBase64,
  markers = [],
  onMarkerClick,
  enableRegionDraw = false,
  onRegionCreated = null,
}) {
  const [imgUrl, setImgUrl] = useState(null);
  const [bounds, setBounds] = useState(null);
  const imgRef = useRef(null);

  useEffect(() => {
    if (!imageBase64) return;
    const url = `data:image/png;base64,${imageBase64}`;
    setImgUrl(url);
    const img = new Image();
    img.onload = () => {
      // Leaflet CRS.Simple uses coords [0,0] top-left; we use bounds [[0,0],[h,w]]
      const w = img.naturalWidth;
      const h = img.naturalHeight;
      setBounds([
        [0, 0],
        [h, w],
      ]);
    };
    img.src = url;
    imgRef.current = img;
  }, [imageBase64]);

  // Map percent coords to image CRS.Simple coordinates
  const mapMarkerToPoint = (coordStr) => {
    if (!coordStr || !imgRef.current) return null;
    const cleaned = coordStr.replace("%", "").trim();
    const parts = cleaned.split(/[, ]+/).filter(Boolean);
    if (parts.length !== 2) return null;
    const px = parseFloat(parts[0]);
    const py = parseFloat(parts[1]);
    if (isNaN(px) || isNaN(py)) return null;
    const w = imgRef.current.naturalWidth;
    const h = imgRef.current.naturalHeight;
    // Percent assumed 0-100
    const x = (px / 100) * w;
    const y = (py / 100) * h;
    // In CRS.Simple, coordinates are [y, x]
    return [y, x];
  };

  if (!imgUrl || !bounds) return <div>Loading map...</div>;

  return (
    <MapContainer
      crs={L.CRS.Simple}
      bounds={bounds}
      style={{ height: "640px", width: "100%" }}
      zoomControl={true}
    >
      <ImageOverlay url={imgUrl} bounds={bounds} />
      <FitBounds bounds={bounds} />
      {enableRegionDraw && (
        <RegionDrawBridge
          onCreated={onRegionCreated}
          imageNaturalSize={
            imgRef.current
              ? {
                  width: imgRef.current.naturalWidth,
                  height: imgRef.current.naturalHeight,
                }
              : null
          }
        />
      )}
      {markers.map((m) => {
        const point = mapMarkerToPoint(m.coordinates || "");
        if (!point) return null;
        return (
          <Marker
            key={m.id}
            position={point}
            eventHandlers={{ click: () => onMarkerClick && onMarkerClick(m) }}
          >
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
        );
      })}
    </MapContainer>
  );
}

function RegionDrawBridge({ onCreated, imageNaturalSize }) {
  const map = useMap();
  const wrapped = (bounds, layer) => {
    try {
      // Map bounds are in CRS.Simple pixel coordinates [y, x] ordering
      // We need to convert the rectangle pixel bounds to percent based on image natural size
      if (!onCreated) return;
      // bounds have _southWest and _northEast with lat/lng in pixel space
      onCreated(bounds, {
        isImage: true,
        // prefer intrinsic image size (naturalWidth/naturalHeight) when available
        imageSize: imageNaturalSize || (map.getSize ? map.getSize() : null),
        layer,
      });
    } catch (err) {
      console.error("RegionDrawBridge image wrap error", err);
      onCreated(bounds, {
        isImage: true,
        imageSize: imageNaturalSize || null,
        layer,
      });
    }
  };
  return <RegionDraw map={map} onCreated={wrapped} />;
}
