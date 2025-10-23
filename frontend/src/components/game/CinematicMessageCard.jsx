import React, { useState } from "react";
import {
  Box,
  Card,
  CardMedia,
  Typography,
  IconButton,
  Collapse,
  Stack,
  Chip,
  Avatar,
  Paper,
  Fade,
} from "@mui/material";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import ExpandLessIcon from "@mui/icons-material/ExpandLess";
import AutoStoriesIcon from "@mui/icons-material/AutoStories";
import ImageIcon from "@mui/icons-material/Image";
import SmartToyIcon from "@mui/icons-material/SmartToy";
import PersonIcon from "@mui/icons-material/Person";
import ReactMarkdown from "react-markdown";

/**
 * Messenger-style Message Card
 * Features: Preview lines with expansion, hero images, clean bubble design
 */
export default function CinematicMessageCard({
  message,
  isUser = false,
  sceneImage = null,
  onImageGenerate,
  children, // For TTS, action chips, etc.
}) {
  const [textExpanded, setTextExpanded] = useState(false);

  // Extract first line for preview (up to first newline or 80 chars)
  const getFirstLine = (content) => {
    const plainText = content.replace(/[#*_`\[\]]/g, "").trim();
    const firstLineBreak = plainText.indexOf("\n");
    const firstLine =
      firstLineBreak > 0 ? plainText.substring(0, firstLineBreak) : plainText;
    return firstLine.length > 80 ? firstLine.substring(0, 80) + "..." : firstLine;
  };

  // User messages - messenger bubble on right
  if (isUser) {
    return (
      <Fade in timeout={300}>
        <Box
          sx={{
            display: "flex",
            justifyContent: "flex-end",
            mb: 1.5,
            width: "100%",
          }}
        >
          <Paper
            elevation={2}
            sx={{
              maxWidth: "75%",
              bgcolor: "rgba(61, 47, 31, 0.85)",
              border: "1px solid rgba(185, 167, 0, 0.3)",
              borderRadius: 2,
              overflow: "hidden",
              transition: "all 0.2s ease-in-out",
              "&:hover": {
                borderColor: "primary.main",
                boxShadow: "0 4px 12px rgba(185, 167, 0, 0.2)",
              },
            }}
          >
            {/* Preview/Header */}
            <Box
              onClick={() => setTextExpanded(!textExpanded)}
              sx={{
                p: 1.5,
                cursor: "pointer",
                display: "flex",
                alignItems: "center",
                gap: 1,
                bgcolor: "rgba(0, 0, 0, 0.2)",
              }}
            >
              <Avatar sx={{ bgcolor: "primary.main", width: 28, height: 28 }}>
                <PersonIcon sx={{ fontSize: 16 }} />
              </Avatar>
              <Typography
                variant="body2"
                sx={{
                  flex: 1,
                  fontSize: "0.9rem",
                  color: "text.primary",
                  fontWeight: 500,
                }}
              >
                {getFirstLine(message.content)}
              </Typography>
              <IconButton
                size="small"
                sx={{
                  color: "primary.main",
                  transform: textExpanded ? "rotate(180deg)" : "rotate(0deg)",
                  transition: "transform 0.3s",
                }}
              >
                <ExpandMoreIcon fontSize="small" />
              </IconButton>
            </Box>

            {/* Expanded Content */}
            <Collapse in={textExpanded}>
              <Box
                sx={{
                  p: 2,
                  pt: 1.5,
                  maxHeight: "300px",
                  overflow: "auto",
                  borderTop: "1px solid rgba(185, 167, 0, 0.2)",
                  "&::-webkit-scrollbar": { width: "6px" },
                  "&::-webkit-scrollbar-track": {
                    bgcolor: "rgba(0, 0, 0, 0.2)",
                  },
                  "&::-webkit-scrollbar-thumb": {
                    bgcolor: "rgba(185, 167, 0, 0.5)",
                    borderRadius: "3px",
                    "&:hover": { bgcolor: "primary.main" },
                  },
                }}
              >
                <Typography
                  variant="body2"
                  sx={{
                    fontSize: "0.9rem",
                    color: "text.primary",
                    lineHeight: 1.6,
                    whiteSpace: "pre-wrap",
                    wordBreak: "break-word",
                  }}
                >
                  {message.content}
                </Typography>
              </Box>
            </Collapse>
          </Paper>
        </Box>
      </Fade>
    );
  }

  // DM messages - Messenger bubble on left with optional hero image
  const hasImage = sceneImage?.image_url;

  return (
    <Fade in timeout={500}>
      <Box sx={{ display: "flex", justifyContent: "flex-start", mb: 2, width: "100%" }}>
        <Paper
          elevation={6}
          sx={{
            maxWidth: "85%",
            bgcolor: "rgba(28, 20, 16, 0.95)",
            border: "2px solid",
            borderColor: "primary.main",
            borderRadius: 3,
            overflow: "hidden",
            transition: "all 0.3s ease-in-out",
            "&:hover": {
              boxShadow: "0 8px 32px rgba(185, 167, 0, 0.4)",
              borderColor: "primary.light",
            },
          }}
        >
          {/* Hero Image Section (Optional) */}
          {hasImage && (
            <Box sx={{ position: "relative" }}>
              <CardMedia
                component="img"
                image={sceneImage.image_url}
                alt="Scene"
                sx={{
                  height: "300px",
                  objectFit: "cover",
                  filter: "brightness(0.9)",
                }}
              />
              {/* Gradient Overlay */}
              <Box
                sx={{
                  position: "absolute",
                  bottom: 0,
                  left: 0,
                  right: 0,
                  height: "80px",
                  background:
                    "linear-gradient(to top, rgba(28, 20, 16, 0.95), transparent)",
                }}
              />
              {/* DM Badge on Image */}
              <Chip
                icon={<SmartToyIcon sx={{ fontSize: 14 }} />}
                label="DM"
                size="small"
                sx={{
                  position: "absolute",
                  top: 12,
                  left: 12,
                  bgcolor: "rgba(139, 0, 0, 0.9)",
                  color: "white",
                  fontWeight: 700,
                  backdropFilter: "blur(8px)",
                  border: "2px solid",
                  borderColor: "primary.main",
                  height: 24,
                  fontSize: "0.7rem",
                }}
              />
            </Box>
          )}

          {/* Message Preview/Header */}
          <Box
            onClick={() => setTextExpanded(!textExpanded)}
            sx={{
              p: 1.5,
              cursor: "pointer",
              display: "flex",
              alignItems: "center",
              gap: 1,
              bgcolor: "rgba(0, 0, 0, 0.3)",
              borderTop: hasImage ? "1px solid rgba(185, 167, 0, 0.2)" : "none",
              "&:hover": {
                bgcolor: "rgba(185, 167, 0, 0.15)",
              },
            }}
          >
            <Avatar
              sx={{
                bgcolor: "secondary.main",
                width: 28,
                height: 28,
                border: "2px solid",
                borderColor: "primary.main",
              }}
            >
              <SmartToyIcon sx={{ fontSize: 16 }} />
            </Avatar>
            <Box sx={{ flex: 1, minWidth: 0 }}>
              <Typography
                variant="body2"
                sx={{
                  fontSize: "0.9rem",
                  color: "text.primary",
                  fontWeight: 500,
                  overflow: "hidden",
                  textOverflow: "ellipsis",
                  display: "-webkit-box",
                  WebkitLineClamp: textExpanded ? "unset" : 1,
                  WebkitBoxOrient: "vertical",
                  lineHeight: 1.4,
                }}
              >
                {getFirstLine(message.content)}
              </Typography>
            </Box>
            <IconButton
              size="small"
              sx={{
                color: "primary.main",
                transform: textExpanded ? "rotate(180deg)" : "rotate(0deg)",
                transition: "transform 0.3s",
              }}
            >
              <ExpandMoreIcon fontSize="small" />
            </IconButton>
          </Box>

          {/* Expanded Text Content */}
          <Collapse in={textExpanded}>
            <Box
              sx={{
                p: 2,
                pt: 1,
                maxHeight: "300px",
                overflow: "auto",
                borderTop: "1px solid rgba(185, 167, 0, 0.2)",
                "&::-webkit-scrollbar": {
                  width: "8px",
                },
                "&::-webkit-scrollbar-track": {
                  bgcolor: "rgba(0, 0, 0, 0.2)",
                  borderRadius: "4px",
                },
                "&::-webkit-scrollbar-thumb": {
                  bgcolor: "rgba(185, 167, 0, 0.5)",
                  borderRadius: "4px",
                  "&:hover": {
                    bgcolor: "primary.main",
                  },
                },
              }}
            >
              <Box
                sx={{
                  fontSize: "0.9rem",
                  lineHeight: 1.6,
                  color: "text.primary",
                  "& p": { mb: 1 },
                  "& p:last-child": { mb: 0 },
                  "& h1, & h2, & h3, & h4, & h5, & h6": {
                    color: "primary.main",
                    fontSize: "1em",
                    fontWeight: 700,
                    mt: 1.5,
                    mb: 0.75,
                    borderBottom: "1px solid rgba(185, 167, 0, 0.3)",
                    pb: 0.5,
                  },
                  "& strong": { color: "primary.light", fontWeight: 700 },
                  "& em": { color: "text.secondary" },
                  "& ul, & ol": { pl: 2.5, my: 0.75 },
                  "& li": { mb: 0.25 },
                  "& code": {
                    bgcolor: "rgba(0,0,0,0.5)",
                    color: "primary.light",
                    px: 0.5,
                    py: 0.25,
                    borderRadius: 0.5,
                    fontSize: "0.85em",
                    fontFamily: "monospace",
                  },
                  "& pre": {
                    bgcolor: "rgba(0,0,0,0.6)",
                    p: 1.5,
                    borderRadius: 1,
                    overflow: "auto",
                    border: "1px solid rgba(185, 167, 0, 0.2)",
                  },
                  "& blockquote": {
                    borderLeft: "3px solid",
                    borderColor: "primary.main",
                    pl: 1.5,
                    py: 0.5,
                    my: 1,
                    fontStyle: "italic",
                    bgcolor: "rgba(185, 167, 0, 0.05)",
                  },
                }}
              >
                <ReactMarkdown>{message.content}</ReactMarkdown>
              </Box>
            </Box>
          </Collapse>

          {/* Additional Content (TTS, Action Chips, etc.) */}
          {children && (
            <Box
              sx={{
                p: 2,
                pt: 1,
                borderTop: "1px solid rgba(185, 167, 0, 0.1)",
              }}
            >
              {children}
            </Box>
          )}
        </Paper>
      </Box>
    </Fade>
  );
}
