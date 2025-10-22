/**
 * DiceRoller - Visual Dice Roller Widget
 *
 * Quick dice rolling interface with common D&D dice
 */

import React, { useState } from "react";
import {
  Paper,
  Box,
  Typography,
  Button,
  TextField,
  Grid,
  IconButton,
  Chip,
} from "@mui/material";
import { Casino as DiceIcon, Close as CloseIcon } from "@mui/icons-material";

function DiceRoller({ onRoll, onClose }) {
  const [customNotation, setCustomNotation] = useState("");
  const [lastResult, setLastResult] = useState(null);

  const commonDice = [
    { label: "d4", notation: "1d4" },
    { label: "d6", notation: "1d6" },
    { label: "d8", notation: "1d8" },
    { label: "d10", notation: "1d10" },
    { label: "d12", notation: "1d12" },
    { label: "d20", notation: "1d20" },
    { label: "d100", notation: "1d100" },
  ];

  const handleRoll = async (notation) => {
    try {
      const result = await onRoll(notation);
      setLastResult(result);
    } catch (err) {
      console.error("Roll failed:", err);
    }
  };

  const handleCustomRoll = () => {
    if (customNotation.trim()) {
      handleRoll(customNotation.trim());
      setCustomNotation("");
    }
  };

  return (
    <Paper elevation={3}>
      {/* Header */}
      <Box
        sx={{
          p: 2,
          background: "linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%)",
          color: "white",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
        }}
      >
        <Typography
          variant="h6"
          sx={{ display: "flex", alignItems: "center", gap: 1 }}
        >
          <DiceIcon /> Dice Roller
        </Typography>
        <IconButton size="small" onClick={onClose} sx={{ color: "white" }}>
          <CloseIcon />
        </IconButton>
      </Box>

      {/* Content */}
      <Box sx={{ p: 2 }}>
        {/* Last Result */}
        {lastResult && (
          <Box
            sx={{
              mb: 2,
              p: 2,
              backgroundColor: "#f5f5f5",
              borderRadius: 1,
              textAlign: "center",
            }}
          >
            <Typography variant="caption" color="text.secondary">
              Last Roll: {lastResult.notation}
            </Typography>
            <Typography
              variant="h4"
              color="primary"
              sx={{ fontWeight: "bold" }}
            >
              {lastResult.total}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {lastResult.formatted}
            </Typography>
          </Box>
        )}

        {/* Common Dice */}
        <Typography variant="caption" color="text.secondary" gutterBottom>
          Quick Roll
        </Typography>
        <Grid container spacing={1} sx={{ mb: 2 }}>
          {commonDice.map((dice) => (
            <Grid item xs={4} sm={3} key={dice.notation}>
              <Button
                fullWidth
                variant="outlined"
                onClick={() => handleRoll(dice.notation)}
                size="small"
              >
                {dice.label}
              </Button>
            </Grid>
          ))}
        </Grid>

        {/* Custom Notation */}
        <Typography variant="caption" color="text.secondary" gutterBottom>
          Custom Roll
        </Typography>
        <Box sx={{ display: "flex", gap: 1 }}>
          <TextField
            fullWidth
            size="small"
            placeholder="e.g., 2d6+5, 1d20+3"
            value={customNotation}
            onChange={(e) => setCustomNotation(e.target.value)}
            onKeyPress={(e) => {
              if (e.key === "Enter") {
                handleCustomRoll();
              }
            }}
          />
          <Button
            variant="contained"
            onClick={handleCustomRoll}
            disabled={!customNotation.trim()}
          >
            Roll
          </Button>
        </Box>

        {/* Common Modifiers */}
        <Box sx={{ mt: 2 }}>
          <Typography variant="caption" color="text.secondary" gutterBottom>
            Common Rolls
          </Typography>
          <Box sx={{ display: "flex", gap: 0.5, flexWrap: "wrap", mt: 0.5 }}>
            <Chip
              label="Attack: 1d20+5"
              size="small"
              onClick={() => handleRoll("1d20+5")}
              clickable
            />
            <Chip
              label="Damage: 1d8+3"
              size="small"
              onClick={() => handleRoll("1d8+3")}
              clickable
            />
            <Chip
              label="Save: 1d20+2"
              size="small"
              onClick={() => handleRoll("1d20+2")}
              clickable
            />
          </Box>
        </Box>
      </Box>
    </Paper>
  );
}

export default DiceRoller;
