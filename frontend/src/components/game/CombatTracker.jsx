/**
 * CombatTracker - Initiative Tracker and Combat Management
 * 
 * Features:
 * - Initiative order display
 * - Current turn indicator
 * - HP bars for all combatants
 * - Attack buttons
 * - Next turn / End combat controls
 * - Round counter
 */

import React, { useState } from 'react';
import {
  Paper,
  Box,
  Typography,
  LinearProgress,
  IconButton,
  Button,
  List,
  ListItem,
  ListItemText,
  Chip,
  Divider,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Select,
  MenuItem,
  FormControl,
  InputLabel
} from '@mui/material';
import {
  SportsKabaddi as CombatIcon,
  NavigateNext as NextIcon,
  Close as CloseIcon,
  FitnessCenter as AttackIcon,
  Favorite as HPIcon
} from '@mui/icons-material';

function CombatTracker({ 
  combatState, 
  currentTurnCombatant,
  onAttack,
  onNextTurn,
  onEndCombat
}) {
  const [attackDialogOpen, setAttackDialogOpen] = useState(false);
  const [selectedTarget, setSelectedTarget] = useState('');

  if (!combatState || !combatState.active) {
    return null;
  }

  const { combatants = [], current_turn = 0, round = 1 } = combatState;

  const handleOpenAttackDialog = () => {
    // Pre-select first enemy if current combatant is a party member
    const firstEnemy = combatants.find((c, idx) => 
      idx !== current_turn && c.name !== currentTurnCombatant?.name
    );
    if (firstEnemy) {
      setSelectedTarget(firstEnemy.name);
    }
    setAttackDialogOpen(true);
  };

  const handleAttack = () => {
    if (selectedTarget) {
      onAttack(selectedTarget);
      setAttackDialogOpen(false);
      setSelectedTarget('');
    }
  };

  const getHPPercentage = (currentHP, maxHP) => {
    return Math.max(0, Math.min(100, (currentHP / maxHP) * 100));
  };

  const getHPColor = (percentage) => {
    if (percentage > 60) return 'success';
    if (percentage > 30) return 'warning';
    return 'error';
  };

  return (
    <>
      <Paper elevation={3} sx={{ overflow: 'hidden' }}>
        {/* Combat Header */}
        <Box sx={{ 
          p: 2, 
          background: 'linear-gradient(135deg, #f03e3e 0%, #c92a2a 100%)',
          color: 'white',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          <Box>
            <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <CombatIcon /> Combat Tracker
            </Typography>
            <Typography variant="caption">
              Round {round}
            </Typography>
          </Box>
          <IconButton 
            size="small" 
            onClick={onEndCombat}
            sx={{ color: 'white' }}
          >
            <CloseIcon />
          </IconButton>
        </Box>

        {/* Initiative List */}
        <List sx={{ maxHeight: 400, overflowY: 'auto', p: 0 }}>
          {combatants.map((combatant, index) => {
            const isCurrentTurn = index === current_turn;
            const isDead = combatant.current_hp <= 0;
            const hpPercentage = getHPPercentage(combatant.current_hp, combatant.max_hp);

            return (
              <React.Fragment key={index}>
                <ListItem
                  sx={{
                    backgroundColor: isCurrentTurn ? 'rgba(255, 193, 7, 0.1)' : 'transparent',
                    borderLeft: isCurrentTurn ? '4px solid #ffc107' : '4px solid transparent',
                    opacity: isDead ? 0.5 : 1,
                    transition: 'all 0.3s ease'
                  }}
                >
                  <Box sx={{ width: '100%' }}>
                    {/* Combatant Name and Initiative */}
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Typography variant="subtitle1" sx={{ fontWeight: isCurrentTurn ? 'bold' : 'normal' }}>
                          {combatant.name}
                        </Typography>
                        {isCurrentTurn && (
                          <Chip 
                            label="TURN" 
                            size="small" 
                            color="warning"
                            sx={{ fontWeight: 'bold' }}
                          />
                        )}
                        {isDead && (
                          <Chip 
                            label="DEAD" 
                            size="small" 
                            color="error"
                            sx={{ fontWeight: 'bold' }}
                          />
                        )}
                      </Box>
                      <Chip 
                        label={`Initiative: ${combatant.initiative}`}
                        size="small"
                        variant="outlined"
                      />
                    </Box>

                    {/* HP Bar */}
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <HPIcon fontSize="small" color={isDead ? 'error' : 'action'} />
                      <Box sx={{ flex: 1 }}>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                          <Typography variant="caption" color="text.secondary">
                            HP
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {combatant.current_hp} / {combatant.max_hp}
                          </Typography>
                        </Box>
                        <LinearProgress 
                          variant="determinate" 
                          value={hpPercentage}
                          color={getHPColor(hpPercentage)}
                          sx={{ height: 8, borderRadius: 4 }}
                        />
                      </Box>
                    </Box>

                    {/* Attack Button (for current turn) */}
                    {isCurrentTurn && !isDead && (
                      <Box sx={{ mt: 1, display: 'flex', gap: 1 }}>
                        <Button
                          size="small"
                          variant="contained"
                          color="error"
                          startIcon={<AttackIcon />}
                          onClick={handleOpenAttackDialog}
                          fullWidth
                        >
                          Attack
                        </Button>
                      </Box>
                    )}
                  </Box>
                </ListItem>
                {index < combatants.length - 1 && <Divider />}
              </React.Fragment>
            );
          })}
        </List>

        {/* Combat Controls */}
        <Box sx={{ p: 2, backgroundColor: '#f5f5f5' }}>
          <Button
            fullWidth
            variant="contained"
            color="warning"
            startIcon={<NextIcon />}
            onClick={onNextTurn}
          >
            Next Turn
          </Button>
          <Button
            fullWidth
            variant="outlined"
            color="error"
            onClick={onEndCombat}
            sx={{ mt: 1 }}
          >
            End Combat
          </Button>
        </Box>
      </Paper>

      {/* Attack Target Selection Dialog */}
      <Dialog open={attackDialogOpen} onClose={() => setAttackDialogOpen(false)}>
        <DialogTitle>
          Select Attack Target
        </DialogTitle>
        <DialogContent sx={{ minWidth: 300 }}>
          <FormControl fullWidth sx={{ mt: 2 }}>
            <InputLabel>Target</InputLabel>
            <Select
              value={selectedTarget}
              label="Target"
              onChange={(e) => setSelectedTarget(e.target.value)}
            >
              {combatants
                .filter((c, idx) => idx !== current_turn && c.current_hp > 0)
                .map((c) => (
                  <MenuItem key={c.name} value={c.name}>
                    {c.name} ({c.current_hp}/{c.max_hp} HP)
                  </MenuItem>
                ))}
            </Select>
          </FormControl>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setAttackDialogOpen(false)}>Cancel</Button>
          <Button 
            onClick={handleAttack} 
            variant="contained" 
            color="error"
            disabled={!selectedTarget}
          >
            Attack
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
}

export default CombatTracker;
