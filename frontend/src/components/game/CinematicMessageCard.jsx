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
 * Cinematic Message Card - Visual-first design
 * Features: Hero images, collapsible text, compact user messages, modern layout
 */
export default function CinematicMessageCard({
  message,
  isUser = false,
  sceneImage = null,
  onImageGenerate,
  children, // For TTS, action chips, etc.
}) {
  const [textExpanded, setTextExpanded] = useState(!isUser);
  const [showUserMessage, setShowUserMessage] = useState(false);

  // User messages - super compact, hidden by default
  if (isUser) {
    return (
      <Fade in timeout={300}>
        <Box sx={{ display: "flex", justifyContent: "flex-end", mb: 1 }}>
          <Chip
            avatar={
              <Avatar sx={{ bgcolor: "primary.main", width: 24, height: 24 }}>
                <PersonIcon sx={{ fontSize: 14 }} />
              </Avatar>
            }
            label="You asked..."
            onClick={() => setShowUserMessage(!showUserMessage)}
            size="small"
            sx={{
              bgcolor: "rgba(61, 47, 31, 0.6)",
              color: "text.secondary",
              fontSize: "0.75rem",
              height: 24,
              cursor: "pointer",
              border: "1px solid rgba(185, 167, 0, 0.2)",
              "&:hover": {
                bgcolor: "rgba(61, 47, 31, 0.8)",
                borderColor: "primary.main",
              },
            }}
          />
          <Collapse in={showUserMessage} orientation="horizontal">
            <Paper
              elevation={2}
              sx={{
                ml: 1,
                p: 1,
                maxWidth: "400px",
                bgcolor: "rgba(61, 47, 31, 0.8)",
                border: "1px solid rgba(185, 167, 0, 0.3)",
              }}
            >
              <Typography
                variant="body2"
                sx={{ fontSize: "0.85rem", color: "text.primary" }}
              >
                {message.content}
              </Typography>
            </Paper>
          </Collapse>
        </Box>
      </Fade>
    );
  }

  // DM messages - Visual-first with scene hero
  const hasImage = sceneImage?.image_url;

  return (
    <Fade in timeout={500}>
      <Card
        elevation={6}
        sx={{
          position: "relative",
          borderRadius: 3,
          overflow: "hidden",
          border: "2px solid",
          borderColor: "primary.main",
          bgcolor: "rgba(28, 20, 16, 0.95)",
          mb: 2,
          transition: "all 0.3s ease-in-out",
          "&:hover": {
            boxShadow: "0 8px 32px rgba(185, 167, 0, 0.4)",
            borderColor: "primary.light",
          },
        }}
      >
        {/* Hero Image Section */}
        {hasImage ? (
          <Box sx={{ position: "relative" }}>
            <CardMedia
              component="img"
              image={sceneImage.image_url}
              alt="Scene"
              sx={{
                height: "400px",
                objectFit: "cover",
                filter: "brightness(0.9)",
              }}
            />
            {/* Gradient Overlay for text readability */}
            <Box
              sx={{
                position: "absolute",
                bottom: 0,
                left: 0,
                right: 0,
                height: "120px",
                background:
                  "linear-gradient(to top, rgba(28, 20, 16, 0.95), transparent)",
              }}
            />
            {/* DM Badge on Image */}
            <Chip
              icon={<SmartToyIcon />}
              label="Dungeon Master"
              size="small"
              sx={{
                position: "absolute",
                top: 16,
                left: 16,
                bgcolor: "rgba(139, 0, 0, 0.9)",
                color: "white",
                fontWeight: 700,
                backdropFilter: "blur(8px)",
                border: "2px solid",
                borderColor: "primary.main",
              }}
            />
          </Box>
        ) : (
          // No image - show placeholder with generate button
          <Box
            sx={{
              height: "200px",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              bgcolor: "rgba(0, 0, 0, 0.4)",
              borderBottom: "2px solid rgba(185, 167, 0, 0.2)",
              position: "relative",
            }}
          >
            <Stack alignItems="center" spacing={1}>
              <ImageIcon
                sx={{ fontSize: 48, color: "primary.main", opacity: 0.5 }}
              />
              <Typography variant="caption" color="text.secondary">
                Scene illustration
              </Typography>
              {onImageGenerate && (
                <IconButton
                  size="small"
                  onClick={onImageGenerate}
                  sx={{
                    bgcolor: "primary.main",
                    color: "primary.contrastText",
                    "&:hover": { bgcolor: "primary.light" },
                  }}
                >
                  <ImageIcon />
                </IconButton>
              )}
            </Stack>
            {/* DM Badge */}
            <Chip
              icon={<SmartToyIcon />}
              label="DM"
              size="small"
              sx={{
                position: "absolute",
                top: 12,
                left: 12,
                bgcolor: "rgba(139, 0, 0, 0.9)",
                color: "white",
                fontWeight: 700,
                border: "2px solid",
                borderColor: "primary.main",
              }}
            />
          </Box>
        )}

        {/* Text Content Section - Collapsible */}
        <Box>
          {/* Collapsed View - Just a preview bar */}
          <Box
            onClick={() => setTextExpanded(!textExpanded)}
            sx={{
              p: 2,
              cursor: "pointer",
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              bgcolor: textExpanded ? "transparent" : "rgba(0, 0, 0, 0.3)",
              borderTop: textExpanded
                ? "none"
                : "1px solid rgba(185, 167, 0, 0.2)",
              "&:hover": {
                bgcolor: "rgba(185, 167, 0, 0.1)",
              },
            }}
          >
            <Stack
              direction="row"
              spacing={1}
              alignItems="center"
              sx={{ flex: 1 }}
            >
              <AutoStoriesIcon sx={{ fontSize: 20, color: "primary.main" }} />
              <Typography
                variant="body2"
                sx={{
                  fontSize: "0.9rem",
                  color: "text.primary",
                  overflow: "hidden",
                  textOverflow: "ellipsis",
                  whiteSpace: textExpanded ? "normal" : "nowrap",
                  lineHeight: 1.4,
                }}
              >
                {textExpanded
                  ? ""
                  : message.content.slice(0, 120) +
                    (message.content.length > 120 ? "..." : "")}
              </Typography>
            </Stack>
            <IconButton
              size="small"
              sx={{
                color: "primary.main",
                transform: textExpanded ? "rotate(180deg)" : "rotate(0deg)",
                transition: "transform 0.3s",
              }}
            >
              <ExpandMoreIcon />
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
        </Box>
      </Card>
    </Fade>
  );
}
