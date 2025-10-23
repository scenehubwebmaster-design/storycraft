import React, { useState, useRef, useEffect } from "react";
import {
  Paper,
  TextField,
  IconButton,
  Stack,
  Chip,
  Box,
  Collapse,
  Tooltip,
  CircularProgress,
} from "@mui/material";
import SendIcon from "@mui/icons-material/Send";
import CloseIcon from "@mui/icons-material/Close";
import DragIndicatorIcon from "@mui/icons-material/DragIndicator";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import ExpandLessIcon from "@mui/icons-material/ExpandLess";

/**
 * Compact, draggable floating input panel for DM chat
 * Features: draggable, collapsible, character selection, streamlined design
 * React 19 compatible (no react-draggable dependency)
 */
export default function FloatingChatInput({
  message,
  setMessage,
  onSend,
  sending,
  loading,
  onCancel,
  availableCharacters = [],
  activeCharacters = [],
  onToggleCharacter,
  showCharacterSelect = false,
}) {
  const [expanded, setExpanded] = useState(true);
  const [position, setPosition] = useState({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState(false);
  const dragRef = useRef({ startX: 0, startY: 0, initialX: 0, initialY: 0 });

  const handleSend = () => {
    if (message.trim() && !sending && !loading) {
      onSend();
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleMouseDown = (e) => {
    if (e.target.closest(".drag-handle")) {
      setIsDragging(true);
      dragRef.current = {
        startX: e.clientX,
        startY: e.clientY,
        initialX: position.x,
        initialY: position.y,
      };
      e.preventDefault();
    }
  };

  const handleMouseMove = (e) => {
    if (isDragging) {
      const deltaX = e.clientX - dragRef.current.startX;
      const deltaY = e.clientY - dragRef.current.startY;
      setPosition({
        x: dragRef.current.initialX + deltaX,
        y: dragRef.current.initialY + deltaY,
      });
    }
  };

  const handleMouseUp = () => {
    setIsDragging(false);
  };

  useEffect(() => {
    if (isDragging) {
      window.addEventListener("mousemove", handleMouseMove);
      window.addEventListener("mouseup", handleMouseUp);
      return () => {
        window.removeEventListener("mousemove", handleMouseMove);
        window.removeEventListener("mouseup", handleMouseUp);
      };
    }
  }, [isDragging, position.x, position.y]);

  return (
    <Paper
      elevation={12}
      onMouseDown={handleMouseDown}
      sx={{
        position: "fixed",
        bottom: 24,
        right: 24,
        width: expanded ? "420px" : "280px",
        maxWidth: "calc(100vw - 48px)",
        bgcolor: "rgba(28, 20, 16, 0.98)",
        backdropFilter: "blur(12px)",
        borderRadius: 2,
        border: "2px solid",
        borderColor: "primary.main",
        boxShadow: "0 8px 32px rgba(212, 175, 55, 0.4)",
        transition: "width 0.3s ease-in-out",
        transform: `translate(${position.x}px, ${position.y}px)`,
        zIndex: 1300,
        overflow: "hidden",
        cursor: isDragging ? "grabbing" : "default",
        userSelect: isDragging ? "none" : "auto",
        "&:hover": {
          boxShadow: "0 12px 40px rgba(212, 175, 55, 0.5)",
          borderColor: "primary.light",
        },
      }}
    >
      {/* Header - Drag Handle */}
      <Stack
        direction="row"
        alignItems="center"
        spacing={0.5}
        className="drag-handle"
        sx={{
          bgcolor: "rgba(185, 167, 0, 0.15)",
          px: 1,
          py: 0.5,
          cursor: "move",
          borderBottom: "1px solid",
          borderColor: "primary.dark",
          "&:hover": {
            bgcolor: "rgba(185, 167, 0, 0.25)",
          },
        }}
      >
        <DragIndicatorIcon sx={{ fontSize: 16, color: "primary.main" }} />
        <Box
          sx={{
            flex: 1,
            fontSize: "0.75rem",
            color: "text.secondary",
            fontWeight: 600,
          }}
        >
          💬 DM Chat
        </Box>
        <Tooltip title={expanded ? "Collapse" : "Expand"}>
          <IconButton
            size="small"
            onClick={() => setExpanded(!expanded)}
            sx={{ p: 0.25, color: "primary.main" }}
          >
            {expanded ? (
              <ExpandLessIcon fontSize="small" />
            ) : (
              <ExpandMoreIcon fontSize="small" />
            )}
          </IconButton>
        </Tooltip>
      </Stack>

      <Collapse in={expanded}>
        <Box sx={{ p: 1.5 }}>
          <Stack spacing={1}>
            {/* Character Selection - Compact */}
            {showCharacterSelect && availableCharacters.length > 0 && (
              <Stack
                direction="row"
                spacing={0.5}
                alignItems="center"
                flexWrap="wrap"
                useFlexGap
              >
                <Box sx={{ fontSize: "0.7rem", color: "text.secondary" }}>
                  🎭
                </Box>
                {availableCharacters.map((char) => {
                  const isActive = activeCharacters.includes(char.id);
                  return (
                    <Chip
                      key={char.id}
                      label={char.name}
                      size="small"
                      onClick={() => onToggleCharacter(char.id)}
                      color={isActive ? "primary" : "default"}
                      variant={isActive ? "filled" : "outlined"}
                      sx={{
                        height: 22,
                        fontSize: "0.7rem",
                        cursor: "pointer",
                        "& .MuiChip-label": { px: 0.75 },
                      }}
                    />
                  );
                })}
              </Stack>
            )}

            {/* Input Row */}
            <Stack direction="row" spacing={0.75} alignItems="flex-end">
              <TextField
                fullWidth
                multiline
                maxRows={2}
                placeholder="Ask the DM..."
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                disabled={sending || loading}
                size="small"
                sx={{
                  "& .MuiOutlinedInput-root": {
                    bgcolor: "rgba(13, 13, 13, 0.6)",
                    fontSize: "0.85rem",
                    py: 0.5,
                    "& fieldset": {
                      borderColor: "rgba(185, 167, 0, 0.3)",
                    },
                    "&:hover fieldset": {
                      borderColor: "primary.main",
                    },
                    "&.Mui-focused fieldset": {
                      borderColor: "primary.main",
                    },
                  },
                }}
              />
              <Tooltip title={sending || loading ? "Cancel" : "Send message"}>
                <span>
                  <IconButton
                    onClick={sending || loading ? onCancel : handleSend}
                    disabled={!message.trim() && !sending && !loading}
                    color={sending || loading ? "error" : "primary"}
                    sx={{
                      bgcolor:
                        sending || loading ? "error.dark" : "primary.main",
                      color: "primary.contrastText",
                      width: 36,
                      height: 36,
                      "&:hover": {
                        bgcolor:
                          sending || loading ? "error.main" : "primary.light",
                      },
                      "&.Mui-disabled": {
                        bgcolor: "action.disabledBackground",
                        color: "action.disabled",
                      },
                    }}
                  >
                    {sending || loading ? (
                      <CircularProgress size={16} sx={{ color: "white" }} />
                    ) : (
                      <SendIcon fontSize="small" />
                    )}
                  </IconButton>
                </span>
              </Tooltip>
            </Stack>
          </Stack>
        </Box>
      </Collapse>
    </Paper>
  );
}
