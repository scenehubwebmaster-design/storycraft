import React from "react";
import {
  Box,
  Typography,
  Paper,
  Grid,
  Chip,
  Divider,
  List,
  ListItem,
  ListItemText,
  Card,
  CardContent,
} from "@mui/material";
import PersonIcon from "@mui/icons-material/Person";
import FavoriteIcon from "@mui/icons-material/Favorite";
import PsychologyIcon from "@mui/icons-material/Psychology";
import HistoryIcon from "@mui/icons-material/History";
import EmojiObjectsIcon from "@mui/icons-material/EmojiObjects";
import WarningIcon from "@mui/icons-material/Warning";
import FlashOnIcon from "@mui/icons-material/FlashOn";
import PeopleIcon from "@mui/icons-material/People";
import TrendingUpIcon from "@mui/icons-material/TrendingUp";
import StarsIcon from "@mui/icons-material/Stars";

/**
 * StructuredCharacterDisplay Component
 *
 * Displays a CharacterProfile object with organized sections and visual hierarchy.
 * Optimized for readability and comprehensive character information display.
 */
const StructuredCharacterDisplay = ({ characterProfile }) => {
  if (!characterProfile) {
    return null;
  }

  return (
    <Box sx={{ py: 2 }}>
      {/* Header: Name and Age */}
      <Paper
        elevation={3}
        sx={{
          p: 3,
          mb: 3,
          bgcolor: "primary.main",
          color: "white",
          background: "linear-gradient(135deg, #9c27b0 0%, #7b1fa2 100%)",
          borderRadius: 2,
        }}
      >
        <Typography variant="h3" gutterBottom>
          {characterProfile.name}
        </Typography>
        <Typography variant="h6" sx={{ opacity: 0.9 }}>
          Age: {characterProfile.age}
        </Typography>
      </Paper>

      {/* Section 1: Physical Appearance */}
      <Card
        id="physical"
        sx={{
          mb: 3,
          scrollMarginTop: "20px",
          bgcolor: "background.paper",
          borderLeft: "4px solid",
          borderColor: "primary.main",
        }}
      >
        <CardContent>
          <Box display="flex" alignItems="center" mb={2}>
            <PersonIcon sx={{ mr: 1, color: "primary.main", fontSize: 28 }} />
            <Typography variant="h5" sx={{ color: "primary.light", fontWeight: 600 }}>
              Physical Appearance
            </Typography>
          </Box>

          <Grid container spacing={2}>
            <Grid item xs={12} sm={6}>
              <Typography variant="subtitle2" color="text.secondary">
                Height
              </Typography>
              <Typography variant="body1" gutterBottom>
                {characterProfile.height}
              </Typography>
            </Grid>
            <Grid item xs={12} sm={6}>
              <Typography variant="subtitle2" color="text.secondary">
                Build
              </Typography>
              <Typography variant="body1" gutterBottom>
                {characterProfile.build}
              </Typography>
            </Grid>
            <Grid item xs={12} sm={6}>
              <Typography variant="subtitle2" color="text.secondary">
                Hair
              </Typography>
              <Typography variant="body1" gutterBottom>
                {characterProfile.hair}
              </Typography>
            </Grid>
            <Grid item xs={12} sm={6}>
              <Typography variant="subtitle2" color="text.secondary">
                Eyes
              </Typography>
              <Typography variant="body1" gutterBottom>
                {characterProfile.eyes}
              </Typography>
            </Grid>
          </Grid>

          <Box mt={2}>
            <Typography variant="subtitle2" color="text.secondary" gutterBottom>
              Distinctive Features
            </Typography>
            <Box display="flex" flexWrap="wrap" gap={1}>
              {characterProfile.distinctive_features?.map((feature, index) => (
                <Chip key={index} label={feature} size="small" />
              ))}
            </Box>
          </Box>

          <Box mt={2}>
            <Typography variant="subtitle2" color="text.secondary" gutterBottom>
              Overall Description
            </Typography>
            <Typography variant="body1" paragraph>
              {characterProfile.physical_description}
            </Typography>
          </Box>
        </CardContent>
      </Card>

      {/* Section 2: Personality */}
      <Card
        id="personality"
        sx={{
          mb: 3,
          scrollMarginTop: "20px",
          bgcolor: "background.paper",
          borderLeft: "4px solid",
          borderColor: "secondary.main",
        }}
      >
        <CardContent>
          <Box display="flex" alignItems="center" mb={2}>
            <PsychologyIcon sx={{ mr: 1, color: "secondary.main", fontSize: 28 }} />
            <Typography variant="h5" sx={{ color: "secondary.light", fontWeight: 600 }}>
              Personality
            </Typography>
          </Box>

          <Box mb={2}>
            <Typography variant="subtitle2" color="text.secondary" gutterBottom>
              Core Traits
            </Typography>
            <Box display="flex" flexWrap="wrap" gap={1}>
              {characterProfile.personality_traits?.map((trait, index) => (
                <Chip
                  key={index}
                  label={trait}
                  color="secondary"
                  size="small"
                />
              ))}
            </Box>
          </Box>

          <Box mb={2}>
            <Typography variant="subtitle2" color="text.secondary">
              Demeanor
            </Typography>
            <Typography variant="body1" paragraph>
              {characterProfile.demeanor}
            </Typography>
          </Box>

          {characterProfile.sense_of_humor && (
            <Box mb={2}>
              <Typography variant="subtitle2" color="text.secondary">
                Sense of Humor
              </Typography>
              <Typography variant="body1" paragraph>
                {characterProfile.sense_of_humor}
              </Typography>
            </Box>
          )}

          <Box>
            <Typography variant="subtitle2" color="text.secondary">
              Personality Overview
            </Typography>
            <Typography variant="body1" paragraph>
              {characterProfile.personality_description}
            </Typography>
          </Box>
        </CardContent>
      </Card>

      {/* Section 3: Background */}
      <Card
        id="background"
        sx={{
          mb: 3,
          scrollMarginTop: "20px",
          bgcolor: "background.paper",
          borderLeft: "4px solid",
          borderColor: "primary.dark",
        }}
      >
        <CardContent>
          <Box display="flex" alignItems="center" mb={2}>
            <HistoryIcon sx={{ mr: 1, color: "primary.dark", fontSize: 28 }} />
            <Typography variant="h5" sx={{ color: "primary.light", fontWeight: 600 }}>
              Background
            </Typography>
          </Box>

          <Grid container spacing={2}>
            <Grid item xs={12} sm={6}>
              <Typography variant="subtitle2" color="text.secondary">
                Birthplace
              </Typography>
              <Typography variant="body1" gutterBottom>
                {characterProfile.birthplace}
              </Typography>
            </Grid>
            <Grid item xs={12}>
              <Typography variant="subtitle2" color="text.secondary">
                Upbringing
              </Typography>
              <Typography variant="body1" paragraph>
                {characterProfile.upbringing}
              </Typography>
            </Grid>
          </Grid>

          <Box mb={2}>
            <Typography variant="subtitle2" color="text.secondary" gutterBottom>
              Formative Events
            </Typography>
            <List dense>
              {characterProfile.formative_events?.map((event, index) => (
                <ListItem key={index}>
                  <ListItemText primary={`• ${event}`} />
                </ListItem>
              ))}
            </List>
          </Box>

          <Box>
            <Typography variant="subtitle2" color="text.secondary">
              Full Backstory
            </Typography>
            <Typography variant="body1" paragraph>
              {characterProfile.backstory}
            </Typography>
          </Box>
        </CardContent>
      </Card>

      {/* Section 4: Motivations */}
      <Card
        id="motivations"
        sx={{
          mb: 3,
          scrollMarginTop: "20px",
          bgcolor: "background.paper",
          borderLeft: "4px solid",
          borderColor: "error.main",
        }}
      >
        <CardContent>
          <Box display="flex" alignItems="center" mb={2}>
            <FavoriteIcon sx={{ mr: 1, color: "error.main", fontSize: 28 }} />
            <Typography variant="h5" sx={{ color: "error.light", fontWeight: 600 }}>
              Motivations & Values
            </Typography>
          </Box>

          <Box mb={2}>
            <Typography variant="subtitle2" color="text.secondary">
              Primary Motivation
            </Typography>
            <Typography variant="body1" paragraph>
              {characterProfile.primary_motivation}
            </Typography>
          </Box>

          <Box mb={2}>
            <Typography variant="subtitle2" color="text.secondary" gutterBottom>
              Goals
            </Typography>
            <List dense>
              {characterProfile.goals?.map((goal, index) => (
                <ListItem key={index}>
                  <ListItemText primary={`• ${goal}`} />
                </ListItem>
              ))}
            </List>
          </Box>

          <Box>
            <Typography variant="subtitle2" color="text.secondary" gutterBottom>
              Core Values
            </Typography>
            <Box display="flex" flexWrap="wrap" gap={1}>
              {characterProfile.values?.map((value, index) => (
                <Chip
                  key={index}
                  label={value}
                  color="error"
                  variant="outlined"
                  size="small"
                />
              ))}
            </Box>
          </Box>
        </CardContent>
      </Card>

      {/* Section 5: Fears & Weaknesses */}
      <Card
        id="fears"
        sx={{
          mb: 3,
          scrollMarginTop: "20px",
          bgcolor: "background.paper",
          borderLeft: "4px solid",
          borderColor: "warning.main",
        }}
      >
        <CardContent>
          <Box display="flex" alignItems="center" mb={2}>
            <WarningIcon sx={{ mr: 1, color: "warning.main", fontSize: 28 }} />
            <Typography variant="h5" sx={{ color: "warning.light", fontWeight: 600 }}>
              Fears & Weaknesses
            </Typography>
          </Box>

          <Box mb={2}>
            <Typography variant="subtitle2" color="text.secondary">
              Greatest Fear
            </Typography>
            <Typography variant="body1" paragraph>
              {characterProfile.greatest_fear}
            </Typography>
          </Box>

          <Grid container spacing={2}>
            <Grid item xs={12} sm={6}>
              <Typography
                variant="subtitle2"
                color="text.secondary"
                gutterBottom
              >
                Emotional Weaknesses
              </Typography>
              <List dense>
                {characterProfile.emotional_weaknesses?.map(
                  (weakness, index) => (
                    <ListItem key={index}>
                      <ListItemText primary={`• ${weakness}`} />
                    </ListItem>
                  )
                )}
              </List>
            </Grid>
            <Grid item xs={12} sm={6}>
              <Typography
                variant="subtitle2"
                color="text.secondary"
                gutterBottom
              >
                Physical Weaknesses
              </Typography>
              <List dense>
                {characterProfile.physical_weaknesses?.map(
                  (weakness, index) => (
                    <ListItem key={index}>
                      <ListItemText primary={`• ${weakness}`} />
                    </ListItem>
                  )
                )}
              </List>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Section 6: Strengths & Abilities */}
      <Card
        id="strengths"
        sx={{
          mb: 3,
          scrollMarginTop: "20px",
          bgcolor: "background.paper",
          borderLeft: "4px solid",
          borderColor: "success.main",
        }}
      >
        <CardContent>
          <Box display="flex" alignItems="center" mb={2}>
            <FlashOnIcon sx={{ mr: 1, color: "success.main", fontSize: 28 }} />
            <Typography variant="h5" sx={{ color: "success.light", fontWeight: 600 }}>
              Strengths & Abilities
            </Typography>
          </Box>

          <Box mb={2}>
            <Typography variant="subtitle2" color="text.secondary" gutterBottom>
              Skills
            </Typography>
            <Box display="flex" flexWrap="wrap" gap={1}>
              {characterProfile.skills?.map((skill, index) => (
                <Chip key={index} label={skill} color="success" size="small" />
              ))}
            </Box>
          </Box>

          <Box mb={2}>
            <Typography variant="subtitle2" color="text.secondary">
              Special Abilities
            </Typography>
            <Typography variant="body1" paragraph>
              {characterProfile.special_abilities}
            </Typography>
          </Box>

          <Box mb={2}>
            <Typography variant="subtitle2" color="text.secondary">
              Combat Style
            </Typography>
            <Typography variant="body1" paragraph>
              {characterProfile.combat_style}
            </Typography>
          </Box>

          <Box>
            <Typography variant="subtitle2" color="text.secondary">
              Strengths Overview
            </Typography>
            <Typography variant="body1" paragraph>
              {characterProfile.strengths_description}
            </Typography>
          </Box>
        </CardContent>
      </Card>

      {/* Section 7: Relationships */}
      <Card
        id="relationships"
        sx={{
          mb: 3,
          scrollMarginTop: "20px",
          bgcolor: "background.paper",
          borderLeft: "4px solid",
          borderColor: "primary.light",
        }}
      >
        <CardContent>
          <Box display="flex" alignItems="center" mb={2}>
            <PeopleIcon sx={{ mr: 1, color: "primary.light", fontSize: 28 }} />
            <Typography variant="h5" sx={{ color: "primary.light", fontWeight: 600 }}>
              Key Relationships
            </Typography>
          </Box>

          <Grid container spacing={2}>
            {characterProfile.key_relationships?.map((relationship, index) => (
              <Grid item xs={12} sm={6} key={index}>
                <Paper elevation={1} sx={{ p: 2 }}>
                  <Typography variant="subtitle1" fontWeight="bold">
                    {relationship.name}
                  </Typography>
                  <Typography
                    variant="caption"
                    color="text.secondary"
                    display="block"
                    gutterBottom
                  >
                    {relationship.relationship}
                  </Typography>
                  <Typography variant="body2">
                    {relationship.description}
                  </Typography>
                </Paper>
              </Grid>
            ))}
          </Grid>
        </CardContent>
      </Card>

      {/* Section 8: Character Arc */}
      <Card
        id="arc"
        sx={{
          mb: 3,
          scrollMarginTop: "20px",
          bgcolor: "background.paper",
          borderLeft: "4px solid",
          borderColor: "secondary.dark",
        }}
      >
        <CardContent>
          <Box display="flex" alignItems="center" mb={2}>
            <TrendingUpIcon sx={{ mr: 1, color: "secondary.main", fontSize: 28 }} />
            <Typography variant="h5" sx={{ color: "secondary.light", fontWeight: 600 }}>
              Character Arc Potential
            </Typography>
          </Box>
          <Typography variant="body1" paragraph>
            {characterProfile.character_arc_potential}
          </Typography>
        </CardContent>
      </Card>

      {/* Section 9: Unique Qualities */}
      <Card
        id="unique"
        sx={{
          mb: 3,
          scrollMarginTop: "20px",
          bgcolor: "background.paper",
          borderLeft: "4px solid",
          borderColor: "info.main",
        }}
      >
        <CardContent>
          <Box display="flex" alignItems="center" mb={2}>
            <StarsIcon sx={{ mr: 1, color: "info.main", fontSize: 28 }} />
            <Typography variant="h5" sx={{ color: "info.light", fontWeight: 600 }}>
              What Makes Them Unique
            </Typography>
          </Box>

          <Box mb={2}>
            <Typography variant="subtitle2" color="text.secondary">
              Distinctive Qualities
            </Typography>
            <Typography variant="body1" paragraph>
              {characterProfile.unique_qualities}
            </Typography>
          </Box>

          <Box>
            <Typography variant="subtitle2" color="text.secondary" gutterBottom>
              Quirks & Habits
            </Typography>
            <List dense>
              {characterProfile.quirks_and_habits?.map((quirk, index) => (
                <ListItem key={index}>
                  <ListItemText primary={`• ${quirk}`} />
                </ListItem>
              ))}
            </List>
          </Box>
        </CardContent>
      </Card>
    </Box>
  );
};

export default StructuredCharacterDisplay;
