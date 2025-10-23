import React, { useState } from "react";
import {
  Box,
  Paper,
  Typography,
  Button,
  ButtonGroup,
  Chip,
  Stack,
  Dialog,
  DialogTitle,
  DialogContent,
  TextField,
  IconButton,
  Fade,
  Zoom,
} from "@mui/material";
import {
  Casino as DiceIcon,
  Add as AddIcon,
  Remove as RemoveIcon,
  Close as CloseIcon,
} from "@mui/icons-material";

/**
 * DiceRoller - D&D dice rolling panel with animated results
 * Supports standard D&D dice (d4, d6, d8, d10, d12, d20, d100)
 * Shows roll history and allows modifiers
 */
const DiceRoller = ({ open, onClose, onRollComplete }) => {
  const [selectedDice, setSelectedDice] = useState("d20");
  const [diceCount, setDiceCount] = useState(1);
  const [modifier, setModifier] = useState(0);
  const [rollHistory, setRollHistory] = useState([]);
  const [isRolling, setIsRolling] = useState(false);
  const [lastRoll, setLastRoll] = useState(null);

  const diceTypes = [
    { type: "d4", sides: 4, color: "#4caf50" },
    { type: "d6", sides: 6, color: "#2196f3" },
    { type: "d8", sides: 8, color: "#9c27b0" },
    { type: "d10", sides: 10, color: "#ff9800" },
    { type: "d12", sides: 12, color: "#f44336" },
    { type: "d20", sides: 20, color: "#e91e63" },
    { type: "d100", sides: 100, color: "#3f51b5" },
  ];

  // Roll dice
  const rollDice = () => {
    setIsRolling(true);

    const dice = diceTypes.find((d) => d.type === selectedDice);
    const rolls = [];

    // Roll each die
    for (let i = 0; i < diceCount; i++) {
      rolls.push(Math.floor(Math.random() * dice.sides) + 1);
    }

    const total = rolls.reduce((sum, roll) => sum + roll, 0);
    const finalTotal = total + modifier;

    const rollResult = {
      dice: selectedDice,
      count: diceCount,
      rolls,
      total,
      modifier,
      finalTotal,
      timestamp: new Date(),
      isCritical: selectedDice === "d20" && rolls[0] === 20,
      isCriticalFail: selectedDice === "d20" && rolls[0] === 1,
    };

    // Animate the roll
    setTimeout(() => {
      setLastRoll(rollResult);
      setRollHistory((prev) => [rollResult, ...prev.slice(0, 9)]); // Keep last 10 rolls
      setIsRolling(false);

      // Callback with result
      onRollComplete && onRollComplete(rollResult);
    }, 500);
  };

  // Quick roll shortcuts
  const quickRoll = (type, count = 1, mod = 0) => {
    setSelectedDice(type);
    setDiceCount(count);
    setModifier(mod);
    setTimeout(rollDice, 100);
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>
        <Box
          sx={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
          }}
        >
          <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
            <DiceIcon />
            <Typography variant="h6">Dice Roller</Typography>
          </Box>
          <IconButton onClick={onClose}>
            <CloseIcon />
          </IconButton>
        </Box>
      </DialogTitle>

      <DialogContent>
        <Stack spacing={3}>
          {/* Dice Selection */}
          <Box>
            <Typography variant="subtitle2" gutterBottom>
              Select Dice Type
            </Typography>
            <ButtonGroup fullWidth>
              {diceTypes.map((dice) => (
                <Button
                  key={dice.type}
                  variant={
                    selectedDice === dice.type ? "contained" : "outlined"
                  }
                  onClick={() => setSelectedDice(dice.type)}
                  sx={{
                    bgcolor:
                      selectedDice === dice.type ? dice.color : "transparent",
                    borderColor: dice.color,
                    color: selectedDice === dice.type ? "white" : dice.color,
                    "&:hover": {
                      bgcolor:
                        selectedDice === dice.type
                          ? dice.color
                          : `${dice.color}20`,
                    },
                  }}
                >
                  {dice.type}
                </Button>
              ))}
            </ButtonGroup>
          </Box>

          {/* Dice Count */}
          <Box>
            <Typography variant="subtitle2" gutterBottom>
              Number of Dice
            </Typography>
            <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
              <IconButton
                onClick={() => setDiceCount((prev) => Math.max(1, prev - 1))}
                disabled={diceCount <= 1}
              >
                <RemoveIcon />
              </IconButton>
              <TextField
                type="number"
                value={diceCount}
                onChange={(e) =>
                  setDiceCount(
                    Math.max(1, Math.min(20, parseInt(e.target.value) || 1))
                  )
                }
                sx={{ width: 80 }}
                inputProps={{ min: 1, max: 20, style: { textAlign: "center" } }}
              />
              <IconButton
                onClick={() => setDiceCount((prev) => Math.min(20, prev + 1))}
                disabled={diceCount >= 20}
              >
                <AddIcon />
              </IconButton>
              <Typography variant="body2" color="text.secondary" sx={{ ml: 2 }}>
                {diceCount}
                {selectedDice}
              </Typography>
            </Box>
          </Box>

          {/* Modifier */}
          <Box>
            <Typography variant="subtitle2" gutterBottom>
              Modifier
            </Typography>
            <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
              <IconButton onClick={() => setModifier((prev) => prev - 1)}>
                <RemoveIcon />
              </IconButton>
              <TextField
                type="number"
                value={modifier}
                onChange={(e) => setModifier(parseInt(e.target.value) || 0)}
                sx={{ width: 80 }}
                inputProps={{ style: { textAlign: "center" } }}
              />
              <IconButton onClick={() => setModifier((prev) => prev + 1)}>
                <AddIcon />
              </IconButton>
            </Box>
          </Box>

          {/* Roll Button */}
          <Button
            variant="contained"
            size="large"
            fullWidth
            startIcon={<DiceIcon />}
            onClick={rollDice}
            disabled={isRolling}
            sx={{
              py: 2,
              fontSize: 18,
              fontWeight: "bold",
            }}
          >
            {isRolling
              ? "Rolling..."
              : `Roll ${diceCount}${selectedDice}${
                  modifier !== 0 ? ` ${modifier > 0 ? "+" : ""}${modifier}` : ""
                }`}
          </Button>

          {/* Last Roll Result */}
          {lastRoll && (
            <Zoom in>
              <Paper
                sx={{
                  p: 3,
                  textAlign: "center",
                  bgcolor: lastRoll.isCritical
                    ? "success.dark"
                    : lastRoll.isCriticalFail
                    ? "error.dark"
                    : "primary.dark",
                  color: "white",
                }}
              >
                <Typography variant="h2" fontWeight="bold">
                  {lastRoll.finalTotal}
                </Typography>
                <Typography variant="body2" sx={{ mt: 1 }}>
                  {lastRoll.rolls.join(" + ")}
                  {lastRoll.modifier !== 0 &&
                    ` ${lastRoll.modifier > 0 ? "+" : ""}${lastRoll.modifier}`}
                  {" = "}
                  {lastRoll.finalTotal}
                </Typography>
                {lastRoll.isCritical && (
                  <Chip label="CRITICAL HIT!" color="success" sx={{ mt: 1 }} />
                )}
                {lastRoll.isCriticalFail && (
                  <Chip label="CRITICAL FAIL!" color="error" sx={{ mt: 1 }} />
                )}
              </Paper>
            </Zoom>
          )}

          {/* Quick Roll Buttons */}
          <Box>
            <Typography variant="subtitle2" gutterBottom>
              Quick Rolls
            </Typography>
            <Stack direction="row" spacing={1} flexWrap="wrap">
              <Button
                variant="outlined"
                size="small"
                onClick={() => quickRoll("d20", 1, 0)}
              >
                D20
              </Button>
              <Button
                variant="outlined"
                size="small"
                onClick={() => quickRoll("d20", 1, 5)}
              >
                D20 + 5
              </Button>
              <Button
                variant="outlined"
                size="small"
                onClick={() => quickRoll("d6", 2, 0)}
              >
                2D6
              </Button>
              <Button
                variant="outlined"
                size="small"
                onClick={() => quickRoll("d8", 1, 3)}
              >
                1D8 + 3
              </Button>
              <Button
                variant="outlined"
                size="small"
                onClick={() => quickRoll("d6", 8, 0)}
              >
                Fireball (8D6)
              </Button>
            </Stack>
          </Box>

          {/* Roll History */}
          {rollHistory.length > 0 && (
            <Box>
              <Typography variant="subtitle2" gutterBottom>
                Roll History
              </Typography>
              <Stack spacing={1}>
                {rollHistory.map((roll, index) => (
                  <Fade in key={index}>
                    <Paper sx={{ p: 1.5, bgcolor: "action.hover" }}>
                      <Box
                        sx={{
                          display: "flex",
                          justifyContent: "space-between",
                          alignItems: "center",
                        }}
                      >
                        <Typography variant="body2">
                          {roll.count}
                          {roll.dice}
                          {roll.modifier !== 0 &&
                            ` ${roll.modifier > 0 ? "+" : ""}${roll.modifier}`}
                        </Typography>
                        <Chip
                          label={roll.finalTotal}
                          color={
                            roll.isCritical
                              ? "success"
                              : roll.isCriticalFail
                              ? "error"
                              : "default"
                          }
                          size="small"
                        />
                      </Box>
                      <Typography variant="caption" color="text.secondary">
                        {roll.rolls.join(", ")}
                      </Typography>
                    </Paper>
                  </Fade>
                ))}
              </Stack>
            </Box>
          )}
        </Stack>
      </DialogContent>
    </Dialog>
  );
};

export default DiceRoller;
