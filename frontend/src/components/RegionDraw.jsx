import React, { useEffect } from "react";
import "leaflet-draw/dist/leaflet.draw.css";
import L from "leaflet";

// Attach draw controls to an existing Leaflet map instance and call onCreated when a rectangle is drawn
export default function RegionDraw({ map, onCreated }) {
  useEffect(() => {
    if (!map) return;

    // Ensure draw plugin is available
    const drawControl = new L.Control.Draw({
      draw: {
        polyline: false,
        polygon: false,
        circle: false,
        marker: false,
        circlemarker: false,
        rectangle: {
          shapeOptions: { color: "#ff7800", weight: 2 },
        },
      },
      edit: false,
    });

    map.addControl(drawControl);

    function createdHandler(e) {
      const layer = e.layer;
      if (layer && layer.getBounds) {
        const bounds = layer.getBounds();
        // bounds: { _southWest: {lat,lng}, _northEast: {lat,lng} }
        onCreated && onCreated(bounds, layer);
      }
      // remove the drawn rectangle layer immediately to keep map clean
      map.removeLayer(layer);
    }

    map.on(L.Draw.Event.CREATED, createdHandler);

    return () => {
      map.off(L.Draw.Event.CREATED, createdHandler);
      try {
        map.removeControl(drawControl);
      } catch (err) {}
    };
  }, [map, onCreated]);

  return null;
}
