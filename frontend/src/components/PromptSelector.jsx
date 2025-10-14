import { useState, useEffect } from "react";
import {
  Box,
  Typography,
  Chip,
  TextField,
  FormControl,
  FormLabel,
  Stack,
  Paper,
  Divider,
} from "@mui/material";

/**
 * PromptSelector - Reusable component for selecting prompt options
 * Displays chips for multiple selection and custom text input
 */
export default function PromptSelector({
  label,
  options = [],
  selectedValues = [],
  onChange,
  customValue = "",
  onCustomChange,
  multiSelect = true,
  placeholder = "Add custom details...",
  helperText = "",
}) {
  const handleChipClick = (value) => {
    if (!multiSelect) {
      onChange([value]);
      return;
    }

    if (selectedValues.includes(value)) {
      onChange(selectedValues.filter((v) => v !== value));
    } else {
      onChange([...selectedValues, value]);
    }
  };

  return (
    <FormControl fullWidth sx={{ mb: 3 }}>
      <FormLabel sx={{ mb: 1, fontWeight: 600, color: "text.primary" }}>
        {label}
      </FormLabel>

      {options.length > 0 && (
        <Paper
          variant="outlined"
          sx={{
            p: 2,
            mb: 2,
            maxHeight: 300,
            overflowY: "auto",
            backgroundColor: "background.default",
          }}
        >
          <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
            {options.map((option) => (
              <Chip
                key={option}
                label={option}
                onClick={() => handleChipClick(option)}
                color={selectedValues.includes(option) ? "primary" : "default"}
                variant={
                  selectedValues.includes(option) ? "filled" : "outlined"
                }
                sx={{
                  mb: 1,
                  cursor: "pointer",
                  transition: "all 0.2s",
                  "&:hover": {
                    transform: "scale(1.05)",
                  },
                }}
              />
            ))}
          </Stack>
        </Paper>
      )}

      {onCustomChange && (
        <>
          <Divider sx={{ mb: 2 }}>
            <Typography variant="caption" color="text.secondary">
              OR
            </Typography>
          </Divider>
          <TextField
            fullWidth
            multiline
            rows={3}
            value={customValue}
            onChange={(e) => onCustomChange(e.target.value)}
            placeholder={placeholder}
            helperText={helperText}
            variant="outlined"
          />
        </>
      )}
    </FormControl>
  );
}
