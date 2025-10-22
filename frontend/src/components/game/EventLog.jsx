/**
 * EventLog - Game Event History
 * 
 * Shows chronological log of game events
 */

import React from 'react';
import {
  Paper,
  Box,
  Typography,
  List,
  ListItem,
  ListItemText,
  IconButton,
  Chip
} from '@mui/material';
import {
  Close as CloseIcon,
  History as HistoryIcon,
  Casino as DiceIcon,
  SportsKabaddi as CombatIcon,
  Chat as ChatIcon
} from '@mui/icons-material';

function EventLog({ events = [], onClose }) {
  const getEventIcon = (type) => {
    switch (type) {
      case 'dice_roll':
        return <DiceIcon fontSize="small" />;
      case 'combat_action':
      case 'combat':
        return <CombatIcon fontSize="small" />;
      case 'npc_dialogue':
        return <ChatIcon fontSize="small" />;
      default:
        return <HistoryIcon fontSize="small" />;
    }
  };

  const getEventColor = (type) => {
    switch (type) {
      case 'dice_roll':
        return 'primary';
      case 'combat_action':
      case 'combat':
        return 'error';
      case 'npc_dialogue':
        return 'info';
      default:
        return 'default';
    }
  };

  const formatEventDescription = (event) => {
    switch (event.type) {
      case 'dice_roll':
        return `Rolled ${event.notation}: ${event.total}`;
      case 'combat_action':
        return `${event.attacker} attacked ${event.target}`;
      case 'npc_dialogue':
        return `Talked to ${event.npc}`;
      case 'combat':
        return `Combat ${event.status}`;
      default:
        return JSON.stringify(event).substring(0, 100);
    }
  };

  return (
    <Paper elevation={3}>
      {/* Header */}
      <Box sx={{ 
        p: 2, 
        background: 'linear-gradient(135deg, #868e96 0%, #495057 100%)',
        color: 'white',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center'
      }}>
        <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <HistoryIcon /> Event Log
        </Typography>
        <IconButton size="small" onClick={onClose} sx={{ color: 'white' }}>
          <CloseIcon />
        </IconButton>
      </Box>

      {/* Events List */}
      <List sx={{ maxHeight: 400, overflowY: 'auto', p: 0 }}>
        {events.length === 0 && (
          <Box sx={{ textAlign: 'center', py: 4, color: 'text.secondary' }}>
            <Typography variant="body2">
              No events yet
            </Typography>
          </Box>
        )}

        {events.slice().reverse().map((event, index) => (
          <ListItem key={index} divider>
            <Box sx={{ width: '100%' }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                <Chip
                  icon={getEventIcon(event.type)}
                  label={event.type.replace('_', ' ')}
                  size="small"
                  color={getEventColor(event.type)}
                />
                {event.timestamp && (
                  <Typography variant="caption" color="text.secondary">
                    {new Date(event.timestamp).toLocaleTimeString()}
                  </Typography>
                )}
              </Box>
              <Typography variant="body2">
                {formatEventDescription(event)}
              </Typography>
            </Box>
          </ListItem>
        ))}
      </List>
    </Paper>
  );
}

export default EventLog;
