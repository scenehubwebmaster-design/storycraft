/**
 * DMChatPanel - Chat Interface for AI Dungeon Master
 * 
 * Features:
 * - Scrollable message history with user/DM styling
 * - Text input with send button
 * - Loading indicator during DM response generation
 * - Auto-scroll to latest message
 * - Support for markdown in DM responses
 */

import React, { useState, useRef, useEffect } from 'react';
import {
  Paper,
  Box,
  TextField,
  IconButton,
  Typography,
  Avatar,
  CircularProgress,
  Divider
} from '@mui/material';
import {
  Send as SendIcon,
  Person as PlayerIcon,
  Castle as DMIcon
} from '@mui/icons-material';

function DMChatPanel({ messages = [], onSendMessage, isGenerating = false }) {
  const [inputValue, setInputValue] = useState('');
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Focus input after DM responds
  useEffect(() => {
    if (!isGenerating && messages.length > 0) {
      inputRef.current?.focus();
    }
  }, [isGenerating, messages.length]);

  const handleSend = () => {
    if (inputValue.trim() && !isGenerating) {
      onSendMessage(inputValue.trim());
      setInputValue('');
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const formatMessage = (content) => {
    // Simple markdown-like formatting
    return content
      .split('\n')
      .map((line, i) => {
        // Bold text with **
        line = line.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
        // Italic text with *
        line = line.replace(/\*(.+?)\*/g, '<em>$1</em>');
        // Dice rolls with 🎲
        line = line.replace(/🎲/g, '<span style="color: #ff6b6b;">🎲</span>');
        // Combat with ⚔️
        line = line.replace(/⚔️/g, '<span style="color: #f03e3e;">⚔️</span>');
        
        return <div key={i} dangerouslySetInnerHTML={{ __html: line }} />;
      });
  };

  return (
    <Paper elevation={3} sx={{ height: '500px', display: 'flex', flexDirection: 'column' }}>
      {/* Chat Header */}
      <Box sx={{ 
        p: 2, 
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        color: 'white'
      }}>
        <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <DMIcon /> Dungeon Master Chat
        </Typography>
        <Typography variant="caption">
          Talk to your AI DM using natural language or commands like /roll, /hp, /status
        </Typography>
      </Box>

      {/* Messages Container */}
      <Box sx={{ 
        flex: 1, 
        overflowY: 'auto', 
        p: 2, 
        display: 'flex', 
        flexDirection: 'column',
        gap: 2,
        backgroundColor: '#f5f5f5'
      }}>
        {messages.length === 0 && !isGenerating && (
          <Box sx={{ 
            textAlign: 'center', 
            color: 'text.secondary', 
            py: 8 
          }}>
            <DMIcon sx={{ fontSize: 64, opacity: 0.3, mb: 2 }} />
            <Typography variant="h6" gutterBottom>
              Welcome, Adventurer!
            </Typography>
            <Typography variant="body2">
              Start your adventure by sending a message to your Dungeon Master.
              <br />
              Try: "I want to explore a mysterious tavern" or "/roll 1d20+5"
            </Typography>
          </Box>
        )}

        {messages.map((msg, index) => {
          const isUser = msg.role === 'user';
          const isDM = msg.role === 'assistant';

          return (
            <Box
              key={index}
              sx={{
                display: 'flex',
                gap: 1,
                alignItems: 'flex-start',
                flexDirection: isUser ? 'row-reverse' : 'row'
              }}
            >
              {/* Avatar */}
              <Avatar 
                sx={{ 
                  bgcolor: isUser ? '#4caf50' : '#764ba2',
                  width: 36,
                  height: 36
                }}
              >
                {isUser ? <PlayerIcon fontSize="small" /> : <DMIcon fontSize="small" />}
              </Avatar>

              {/* Message Bubble */}
              <Paper
                elevation={1}
                sx={{
                  p: 1.5,
                  maxWidth: '75%',
                  backgroundColor: isUser ? '#e8f5e9' : 'white',
                  borderRadius: 2,
                  borderTopLeftRadius: isUser ? 2 : 0,
                  borderTopRightRadius: isUser ? 0 : 2
                }}
              >
                <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 'bold', mb: 0.5, display: 'block' }}>
                  {isUser ? 'You' : 'Dungeon Master'}
                </Typography>
                <Typography 
                  variant="body1" 
                  sx={{ 
                    whiteSpace: 'pre-wrap',
                    wordBreak: 'break-word'
                  }}
                >
                  {formatMessage(msg.content)}
                </Typography>
              </Paper>
            </Box>
          );
        })}

        {/* Loading Indicator */}
        {isGenerating && (
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Avatar sx={{ bgcolor: '#764ba2', width: 36, height: 36 }}>
              <DMIcon fontSize="small" />
            </Avatar>
            <Paper elevation={1} sx={{ p: 1.5, borderRadius: 2 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <CircularProgress size={16} />
                <Typography variant="body2" color="text.secondary">
                  The DM is thinking...
                </Typography>
              </Box>
            </Paper>
          </Box>
        )}

        <div ref={messagesEndRef} />
      </Box>

      <Divider />

      {/* Input Area */}
      <Box sx={{ p: 2, backgroundColor: 'white' }}>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <TextField
            inputRef={inputRef}
            fullWidth
            multiline
            maxRows={3}
            placeholder="Describe your action or use a command (/roll, /hp, /status)..."
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            disabled={isGenerating}
            variant="outlined"
            size="small"
          />
          <IconButton
            color="primary"
            onClick={handleSend}
            disabled={!inputValue.trim() || isGenerating}
            sx={{
              backgroundColor: 'primary.main',
              color: 'white',
              '&:hover': {
                backgroundColor: 'primary.dark'
              },
              '&:disabled': {
                backgroundColor: 'action.disabledBackground'
              }
            }}
          >
            <SendIcon />
          </IconButton>
        </Box>
        <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
          Press Enter to send • Shift+Enter for new line
        </Typography>
      </Box>
    </Paper>
  );
}

export default DMChatPanel;
