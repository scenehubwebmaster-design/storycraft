/**
 * PartyStatus - Party Member Overview
 * 
 * Shows HP, conditions, and status for all party members
 */

import React from 'react';
import {
  Paper,
  Box,
  Typography,
  LinearProgress,
  List,
  ListItem,
  Chip,
  Avatar
} from '@mui/material';
import {
  People as PartyIcon,
  Favorite as HPIcon
} from '@mui/icons-material';

function PartyStatus({ partyStatus = {}, isInCombat = false }) {
  const partyMembers = Object.entries(partyStatus);

  const getHPPercentage = (currentHP, maxHP) => {
    return Math.max(0, Math.min(100, (currentHP / maxHP) * 100));
  };

  const getHPColor = (percentage) => {
    if (percentage > 60) return 'success';
    if (percentage > 30) return 'warning';
    return 'error';
  };

  return (
    <Paper elevation={3}>
      <Box sx={{ 
        p: 2, 
        background: 'linear-gradient(135deg, #228be6 0%, #1864ab 100%)',
        color: 'white'
      }}>
        <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <PartyIcon /> Party Status
        </Typography>
        <Typography variant="caption">
          {partyMembers.length} member{partyMembers.length !== 1 ? 's' : ''}
        </Typography>
      </Box>

      <List sx={{ p: 2 }}>
        {partyMembers.length === 0 && (
          <Box sx={{ textAlign: 'center', py: 4, color: 'text.secondary' }}>
            <Typography variant="body2">
              No party members yet
            </Typography>
          </Box>
        )}

        {partyMembers.map(([name, status]) => {
          const hpPercentage = getHPPercentage(status.current_hp, status.max_hp);
          const isDead = status.current_hp <= 0;

          return (
            <ListItem key={name} sx={{ display: 'block', py: 2 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 1 }}>
                <Avatar sx={{ bgcolor: isDead ? '#c92a2a' : '#228be6' }}>
                  {name[0].toUpperCase()}
                </Avatar>
                <Box sx={{ flex: 1 }}>
                  <Typography variant="subtitle1" sx={{ fontWeight: 'bold' }}>
                    {name}
                  </Typography>
                  {status.conditions && status.conditions.length > 0 && (
                    <Box sx={{ display: 'flex', gap: 0.5, mt: 0.5, flexWrap: 'wrap' }}>
                      {status.conditions.map((condition, idx) => (
                        <Chip key={idx} label={condition} size="small" color="warning" />
                      ))}
                    </Box>
                  )}
                </Box>
                {isDead && (
                  <Chip label="DEAD" size="small" color="error" sx={{ fontWeight: 'bold' }} />
                )}
              </Box>

              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <HPIcon fontSize="small" color={isDead ? 'error' : 'action'} />
                <Box sx={{ flex: 1 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                    <Typography variant="caption" color="text.secondary">
                      HP
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {status.current_hp} / {status.max_hp}
                    </Typography>
                  </Box>
                  <LinearProgress 
                    variant="determinate" 
                    value={hpPercentage}
                    color={getHPColor(hpPercentage)}
                    sx={{ height: 6, borderRadius: 3 }}
                  />
                </Box>
              </Box>
            </ListItem>
          );
        })}
      </List>
    </Paper>
  );
}

export default PartyStatus;
