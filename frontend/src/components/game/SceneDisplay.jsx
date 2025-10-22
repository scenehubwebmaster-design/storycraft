/**
 * SceneDisplay - Current Scene Description
 * 
 * Shows the current scene description, location, and available choices
 */

import React from 'react';
import {
  Paper,
  Box,
  Typography,
  List,
  ListItem,
  ListItemText,
  Skeleton
} from '@mui/material';
import {
  Explore as ExploreIcon,
  LocationOn as LocationIcon
} from '@mui/icons-material';

function SceneDisplay({ scene, isGenerating = false }) {
  if (!scene && !isGenerating) {
    return (
      <Paper elevation={3} sx={{ p: 3, textAlign: 'center', minHeight: 200, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <Box>
          <ExploreIcon sx={{ fontSize: 64, opacity: 0.3, mb: 2 }} />
          <Typography variant="h6" color="text.secondary" gutterBottom>
            No Active Scene
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Start your adventure by sending a message to the DM
          </Typography>
        </Box>
      </Paper>
    );
  }

  return (
    <Paper elevation={3} sx={{ overflow: 'hidden' }}>
      {/* Scene Header */}
      <Box sx={{ 
        p: 2, 
        background: 'linear-gradient(135deg, #38b2ac 0%, #2c7a7b 100%)',
        color: 'white'
      }}>
        <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <ExploreIcon /> Current Scene
        </Typography>
        {scene?.location && (
          <Typography variant="caption" sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mt: 0.5 }}>
            <LocationIcon fontSize="small" /> {scene.location}
          </Typography>
        )}
      </Box>

      {/* Scene Description */}
      <Box sx={{ p: 3 }}>
        {isGenerating && !scene ? (
          <>
            <Skeleton variant="text" height={30} />
            <Skeleton variant="text" height={30} />
            <Skeleton variant="text" height={30} width="80%" />
          </>
        ) : (
          <>
            <Typography 
              variant="body1" 
              sx={{ 
                whiteSpace: 'pre-wrap',
                lineHeight: 1.8,
                fontStyle: 'italic',
                color: 'text.primary'
              }}
            >
              {scene?.description || 'Your adventure begins...'}
            </Typography>

            {/* Available Choices */}
            {scene?.choices && scene.choices.length > 0 && (
              <Box sx={{ mt: 3 }}>
                <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                  What do you do?
                </Typography>
                <List dense>
                  {scene.choices.map((choice, index) => (
                    <ListItem key={index} sx={{ py: 0.5 }}>
                      <ListItemText 
                        primary={`${index + 1}. ${choice}`}
                        primaryTypographyProps={{
                          variant: 'body2',
                          color: 'primary'
                        }}
                      />
                    </ListItem>
                  ))}
                </List>
              </Box>
            )}
          </>
        )}
      </Box>
    </Paper>
  );
}

export default SceneDisplay;
