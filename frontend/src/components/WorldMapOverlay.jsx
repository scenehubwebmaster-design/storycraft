import React, { useState, useRef } from "react";
import { Box, IconButton, Tooltip } from "@mui/material";
import RoomIcon from "@mui/icons-material/Room";

// A lightweight map overlay: displays the map image and optional markers
// markers: [{id, name, coordinates ("x,y"), location_image}]
export default function WorldMapOverlay({
  mapSrc,
  markers = [],
  onMarkerClick,
}) {
  const [zoom, setZoom] = useState(1);
  const [offset, setOffset] = useState({ x: 0, y: 0 });
  const dragging = useRef(false);
  const lastPos = useRef({ x: 0, y: 0 });
  // Coordinates are expected as normalized percentages 'x%,y%'
  const parseCoordinates = (coord) => {
    if (!coord) return null;
    // Accept formats like "12,34" or "12% , 34%" or "12% 34%"
    const cleaned = coord.replace("%", "").replace(/\s+/g, "");
    const parts = cleaned.split(/[, ]/).filter(Boolean);
    if (parts.length < 2) return null;
    const x = parseFloat(parts[0]);
    const y = parseFloat(parts[1]);
    if (isNaN(x) || isNaN(y)) return null;
    // If coordinates look like lat/long, we can't map them here. Expect percentages.
    return { x, y };
  };

  const onWheel = (e) => {
    e.preventDefault();
    const delta = e.deltaY > 0 ? -0.1 : 0.1;
    setZoom((z) => Math.min(3, Math.max(0.5, +(z + delta).toFixed(2))));
  };

  const onMouseDown = (e) => {
    dragging.current = true;
    lastPos.current = { x: e.clientX, y: e.clientY };
  };

  const onMouseMove = (e) => {
    if (!dragging.current) return;
    const dx = e.clientX - lastPos.current.x;
    const dy = e.clientY - lastPos.current.y;
    lastPos.current = { x: e.clientX, y: e.clientY };
    setOffset((o) => ({ x: o.x + dx, y: o.y + dy }));
  };

  const onMouseUp = () => {
    dragging.current = false;
  };

  return (
    <Box
      sx={{
        position: "relative",
        width: "100%",
        textAlign: "center",
        overflow: "hidden",
        borderRadius: 1,
      }}
      onWheel={onWheel}
      onMouseDown={onMouseDown}
      onMouseMove={onMouseMove}
      onMouseUp={onMouseUp}
      onMouseLeave={onMouseUp}
    >
      <Box
        sx={{
          position: "relative",
          transform: `translate(${offset.x}px, ${offset.y}px) scale(${zoom})`,
          transformOrigin: "center top",
        }}
      >
        <img
          src={mapSrc}
          alt="world map"
          style={{ width: "100%", height: "auto", display: "block" }}
        />

        {markers.map((m) => {
          const coords = parseCoordinates(m.coordinates);
          if (!coords) return null;
          return (
            <Tooltip title={m.name} key={m.id}>
              <IconButton
                size="small"
                onClick={() => onMarkerClick && onMarkerClick(m)}
                sx={{
                  position: "absolute",
                  left: `calc(${coords.x}% - 14px)`,
                  top: `calc(${coords.y}% - 14px)`,
                  color: "white",
                  background:
                    "linear-gradient(180deg, rgba(255,69,58,0.95), rgba(220,20,60,0.95))",
                  boxShadow: 3,
                  borderRadius: "50%",
                  transform: "translate(-50%, -50%)",
                  width: 28,
                  height: 28,
                  "&:hover": { transform: "translate(-50%, -50%) scale(1.05)" },
                }}
              >
                <RoomIcon sx={{ fontSize: 18 }} />
              </IconButton>
            </Tooltip>
          );
        })}
      </Box>
    </Box>
  );
}
