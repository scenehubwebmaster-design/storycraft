import React, { useState, useEffect, useRef } from "react";
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
import PlayArrowIcon from "@mui/icons-material/PlayArrow";
import ReactMarkdown from "react-markdown";

// D&D Emblem URL
const DND_EMBLEM_URL =
  "https://logos-world.net/wp-content/uploads/2021/12/DnD-Emblem.png";

/**
 * Messenger-style Message Card
 * Features: Preview lines with expansion, hero images, ChatGPT-style typing animation
 */
function CinematicMessageCard({
  message,
  isUser = false,
  sceneImage = null,
  onImageGenerate,
  children, // For TTS, action chips, etc.
  ttsPlaying = false, // Whether TTS is currently playing
  ttsAutoPlay = false, // Whether TTS auto-play is enabled
  onTypingProgress, // Callback fired periodically during typing for auto-scroll
}) {
  const [textExpanded, setTextExpanded] = useState(true); // Always expanded for better UX
  const [displayedText, setDisplayedText] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const typingTimeoutRef = useRef(null);
  const charCountRef = useRef(0); // Track chars for throttled scroll callbacks
  const hasAnimatedRef = useRef(false); // Track if this message has already animated
  const messageCardRef = useRef(null); // Ref to message card for scrolling
  const textContentRef = useRef(null); // Ref to scrollable text content area

  // Extract first 1-2 lines for preview (up to 2 newlines or 120 chars)
  const getPreviewLines = (content) => {
    const plainText = content.replace(/[#*_`\[\]]/g, "").trim();
    const lines = plainText.split("\n").filter((line) => line.trim());
    const preview = lines.slice(0, 2).join(" ");
    return preview.length > 120 ? preview.substring(0, 120) + "..." : preview;
  };

  // Simplified: Show text immediately with typing animation (no TTS sync complexity)
  useEffect(() => {
    if (!isUser && message.content && !message._optimistic) {
      // Check if message is "new" (just generated) or "existing" (from database reload)
      // Messages with IDs but that haven't animated yet are existing messages
      const isExistingMessage = message.id && !hasAnimatedRef.current;

      if (isExistingMessage) {
        // Skip animation for existing messages (on page reload/revisit)
        setDisplayedText(message.content);
        setIsTyping(false);
        hasAnimatedRef.current = true;
        return;
      }

      // Mark that we're about to animate this message
      hasAnimatedRef.current = true;

      // Start typing animation immediately when NEW message arrives
      setIsTyping(true);
      setDisplayedText("");
      charCountRef.current = 0;

      const text = message.content;
      let currentIndex = 0;

      // Typing speed: faster for normal text, slower for punctuation
      const typeNextChar = () => {
        if (currentIndex < text.length) {
          setDisplayedText(text.substring(0, currentIndex + 1));
          currentIndex++;
          charCountRef.current++;

          // Trigger scroll callback every 10 characters or on newlines
          const char = text[currentIndex - 1];
          if (charCountRef.current % 10 === 0 || char === "\n") {
            // Scroll the INNER text content area, not the outer message card
            // This keeps the scroll within the message's expanded text box
            if (textContentRef.current) {
              // Scroll to bottom of the text content area
              textContentRef.current.scrollTop =
                textContentRef.current.scrollHeight;
            }
            // Don't call onTypingProgress - that scrolls the outer container
            // We only want to scroll within the message itself
          }

          // Variable speed: slower after punctuation
          const delay = [".", "!", "?", "\n"].includes(char) ? 40 : 15;

          typingTimeoutRef.current = setTimeout(typeNextChar, delay);
        } else {
          setIsTyping(false);
          // Final scroll at end of typing
          if (onTypingProgress) {
            onTypingProgress();
          }
        }
      };

      // Start typing immediately for better UX
      typeNextChar();

      return () => {
        if (typingTimeoutRef.current) {
          clearTimeout(typingTimeoutRef.current);
        }
      };
    }
  }, [message.content, message._optimistic, isUser, onTypingProgress]);

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
            {/* Preview/Header - Shows 1-2 lines */}
            <Box
              onClick={() => setTextExpanded(!textExpanded)}
              sx={{
                p: 1.5,
                cursor: "pointer",
                display: "flex",
                alignItems: "flex-start",
                gap: 1,
                bgcolor: "rgba(0, 0, 0, 0.2)",
                "&:hover": {
                  bgcolor: "rgba(185, 167, 0, 0.1)",
                },
              }}
            >
              <Avatar sx={{ bgcolor: "primary.main", width: 32, height: 32 }}>
                <PersonIcon sx={{ fontSize: 16 }} />
              </Avatar>
              <Typography
                variant="body2"
                sx={{
                  flex: 1,
                  fontSize: "0.9rem",
                  color: "text.primary",
                  fontWeight: 500,
                  lineHeight: 1.5,
                  overflow: "hidden",
                  textOverflow: "ellipsis",
                  display: "-webkit-box",
                  WebkitLineClamp: 2, // Show 2 lines in preview
                  WebkitBoxOrient: "vertical",
                }}
              >
                {getPreviewLines(message.content)}
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
      <Box
        ref={messageCardRef}
        sx={{
          display: "flex",
          justifyContent: "flex-start",
          mb: 2,
          width: "100%",
        }}
      >
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

          {/* Message Preview/Header - Always shows 1-2 lines */}
          <Box
            sx={{
              p: 1.5,
              display: "flex",
              alignItems: "flex-start",
              gap: 1,
              bgcolor: "rgba(0, 0, 0, 0.3)",
              borderTop: hasImage ? "1px solid rgba(185, 167, 0, 0.2)" : "none",
            }}
          >
            <Avatar
              src={DND_EMBLEM_URL}
              sx={{
                bgcolor: "#8b0000",
                width: 32,
                height: 32,
                border: "2px solid",
                borderColor: "primary.main",
                "& img": {
                  objectFit: "contain",
                },
              }}
            >
              <SmartToyIcon sx={{ fontSize: 16 }} />
            </Avatar>
            <Box sx={{ flex: 1, minWidth: 0 }}>
              {/* Preview Text - Always collapsed, shows 1-2 lines */}
              <Box
                onClick={() => setTextExpanded(!textExpanded)}
                sx={{ cursor: "pointer", mb: 0.5 }}
              >
                <Typography
                  variant="body2"
                  sx={{
                    fontSize: "0.9rem",
                    color: "text.primary",
                    lineHeight: 1.5,
                    overflow: "hidden",
                    textOverflow: "ellipsis",
                    display: "-webkit-box",
                    WebkitLineClamp: 2, // Always show 2 lines in preview
                    WebkitBoxOrient: "vertical",
                  }}
                >
                  {textExpanded
                    ? getPreviewLines(message.content)
                    : isTyping
                    ? displayedText
                    : getPreviewLines(message.content)}
                </Typography>
              </Box>

              {/* TTS Bubble Animation */}
              {ttsPlaying && (
                <Box
                  sx={{
                    display: "flex",
                    alignItems: "center",
                    gap: 0.5,
                    mt: 0.5,
                  }}
                >
                  <PlayArrowIcon
                    sx={{
                      fontSize: 14,
                      color: "primary.main",
                      animation: "pulse 1.5s infinite",
                    }}
                  />
                  <Box sx={{ display: "flex", gap: 0.5, alignItems: "center" }}>
                    <Box
                      className="tts-dot"
                      sx={{
                        width: 6,
                        height: 6,
                        borderRadius: "50%",
                        bgcolor: "primary.main",
                        animation: "bounce 1.4s infinite",
                      }}
                    />
                    <Box
                      className="tts-dot"
                      sx={{
                        width: 6,
                        height: 6,
                        borderRadius: "50%",
                        bgcolor: "primary.main",
                        animation: "bounce 1.4s infinite 0.2s",
                      }}
                    />
                    <Box
                      className="tts-dot"
                      sx={{
                        width: 6,
                        height: 6,
                        borderRadius: "50%",
                        bgcolor: "primary.main",
                        animation: "bounce 1.4s infinite 0.4s",
                      }}
                    />
                  </Box>
                  <style>{`
                    @keyframes bounce {
                      0%, 60%, 100% { transform: translateY(0); }
                      30% { transform: translateY(-8px); }
                    }
                    @keyframes pulse {
                      0%, 100% { opacity: 1; }
                      50% { opacity: 0.5; }
                    }
                  `}</style>
                </Box>
              )}
            </Box>
            <IconButton
              size="small"
              onClick={() => setTextExpanded(!textExpanded)}
              sx={{
                color: "primary.main",
                transform: textExpanded ? "rotate(180deg)" : "rotate(0deg)",
                transition: "transform 0.3s",
              }}
            >
              <ExpandMoreIcon fontSize="small" />
            </IconButton>
          </Box>

          {/* Expanded Text Content - Shows full message with typing animation */}
          <Collapse in={textExpanded}>
            <Box
              ref={textContentRef}
              sx={{
                p: 2,
                pt: 1,
                maxHeight: "400px",
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
                <ReactMarkdown>
                  {isTyping ? displayedText : message.content}
                </ReactMarkdown>
                {/* Typing cursor */}
                {isTyping && (
                  <Box
                    component="span"
                    sx={{
                      display: "inline-block",
                      width: "8px",
                      height: "16px",
                      bgcolor: "primary.main",
                      ml: 0.25,
                      animation: "blink 1s infinite",
                      "@keyframes blink": {
                        "0%, 49%": { opacity: 1 },
                        "50%, 100%": { opacity: 0 },
                      },
                    }}
                  />
                )}
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

// Memoize to prevent unnecessary re-renders when parent state changes
export default React.memo(CinematicMessageCard);
