import React, { useEffect } from "react";
import "leaflet-draw/dist/leaflet.draw.css";
import L from "leaflet";

// Attach draw controls to an existing Leaflet map instance and call onCreated when a rectangle is drawn
export default function RegionDraw({ map, onCreated }) {
  useEffect(() => {
    if (!map) return;

    let drawControl = null;
    let warningEl = null;

    const ensureDrawPlugin = async () => {
      if (!L.Control || !L.Control.Draw) {
        // dynamic import ensures the plugin code runs and attaches to L
        await import("leaflet-draw");
      }
    };

    const createdHandler = (e) => {
      const layer = e.layer;
      if (layer && layer.getBounds) {
        const bounds = layer.getBounds();
        if (onCreated) onCreated(bounds, layer);
      }
      try {
        map.removeLayer(layer);
      } catch (err) {}
    };

    const setup = async () => {
      await ensureDrawPlugin();
      drawControl = new L.Control.Draw({
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
      map.on(L.Draw.Event.CREATED, createdHandler);
    };

    setup().catch((err) => {
      // show a visible warning on the map container so devs/users know drawing is disabled
      try {
        const container = map.getContainer && map.getContainer();
        if (container) {
          warningEl = document.createElement("div");
          warningEl.textContent =
            "Drawing disabled: leaflet-draw failed to load";
          Object.assign(warningEl.style, {
            position: "absolute",
            top: "8px",
            left: "8px",
            zIndex: 1000,
            padding: "6px 8px",
            background: "rgba(255,200,0,0.95)",
            color: "#000",
            borderRadius: "4px",
            fontSize: "12px",
            boxShadow: "0 1px 2px rgba(0,0,0,0.2)",
          });
          if (!container.style.position) container.style.position = "relative";
          container.appendChild(warningEl);
        }
      } catch (e) {
        // ignore DOM errors
      }
      // log the original error for diagnostics
      console.error("leaflet-draw failed to load:", err);
    });

    return () => {
      try {
        if (drawControl && map) {
          if (L && L.Draw && L.Draw.Event && L.Draw.Event.CREATED) {
            try {
              map.off(L.Draw.Event.CREATED, createdHandler);
            } catch (e) {}
          }
          try {
            map.removeControl(drawControl);
          } catch (e) {}
        }
      } catch (err) {
        // swallow during unmount
      }
      try {
        if (warningEl && warningEl.parentNode)
          warningEl.parentNode.removeChild(warningEl);
      } catch (e) {}
    };
  }, [map, onCreated]);

  return null;
}
