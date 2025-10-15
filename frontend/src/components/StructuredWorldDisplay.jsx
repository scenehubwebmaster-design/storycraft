import React from "react";
import {
  Box,
  Typography,
  Paper,
  Grid,
  Chip,
  List,
  ListItem,
  ListItemText,
  Card,
  CardContent,
  Accordion,
  AccordionSummary,
  AccordionDetails,
} from "@mui/material";
import PublicIcon from "@mui/icons-material/Public";
import HistoryIcon from "@mui/icons-material/History";
import TerrainIcon from "@mui/icons-material/Terrain";
import GroupsIcon from "@mui/icons-material/Groups";
import AutoFixHighIcon from "@mui/icons-material/AutoFixHigh";
import GavelIcon from "@mui/icons-material/Gavel";
import MenuBookIcon from "@mui/icons-material/MenuBook";
import ExploreIcon from "@mui/icons-material/Explore";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";

/**
 * StructuredWorldDisplay Component
 *
 * Displays a WorldProfile object with organized sections using accordions for better space management.
 * Optimized for rich worldbuilding information display.
 */
const StructuredWorldDisplay = ({ worldProfile }) => {
  if (!worldProfile) {
    return null;
  }

  return (
    <Box sx={{ py: 2 }}>
      {/* Header: World Name and Tagline */}
      <Paper
        elevation={3}
        sx={{ p: 3, mb: 3, bgcolor: "primary.main", color: "white" }}
      >
        <Typography variant="h3" gutterBottom>
          {worldProfile.name}
        </Typography>
        <Typography variant="h6" sx={{ opacity: 0.9, fontStyle: "italic" }}>
          "{worldProfile.tagline}"
        </Typography>
        <Chip
          label={worldProfile.world_type}
          sx={{ mt: 2, bgcolor: "rgba(255,255,255,0.2)", color: "white" }}
        />
      </Paper>

      {/* Overview */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box display="flex" alignItems="center" mb={2}>
            <PublicIcon sx={{ mr: 1, color: "primary.main" }} />
            <Typography variant="h5" color="primary">
              World Overview
            </Typography>
          </Box>
          <Typography variant="body1" paragraph>
            {worldProfile.overview}
          </Typography>
        </CardContent>
      </Card>

      {/* History Section - Accordion */}
      <Accordion defaultExpanded sx={{ mb: 2 }}>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Box display="flex" alignItems="center">
            <HistoryIcon sx={{ mr: 1, color: "info.main" }} />
            <Typography variant="h6" color="info.main">
              History
            </Typography>
          </Box>
        </AccordionSummary>
        <AccordionDetails>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6}>
              <Typography variant="subtitle2" color="text.secondary">
                Age
              </Typography>
              <Typography variant="body1" gutterBottom>
                {worldProfile.age}
              </Typography>
            </Grid>
            <Grid item xs={12} sm={6}>
              <Typography variant="subtitle2" color="text.secondary">
                Current Era
              </Typography>
              <Typography variant="body1" gutterBottom>
                {worldProfile.current_era}
              </Typography>
            </Grid>
            <Grid item xs={12}>
              <Typography variant="subtitle2" color="text.secondary">
                Origin Story
              </Typography>
              <Typography variant="body1" paragraph>
                {worldProfile.origin_story}
              </Typography>
            </Grid>
          </Grid>

          <Box mt={2}>
            <Typography variant="subtitle2" color="text.secondary" gutterBottom>
              Major Historical Events
            </Typography>
            <List>
              {worldProfile.major_historical_events?.map((event, index) => (
                <ListItem key={index} alignItems="flex-start">
                  <ListItemText
                    primary={
                      <Typography fontWeight="bold">{event.event}</Typography>
                    }
                    secondary={
                      <>
                        <Typography
                          variant="caption"
                          display="block"
                          color="text.secondary"
                        >
                          {event.era}
                        </Typography>
                        <Typography variant="body2">
                          {event.description}
                        </Typography>
                      </>
                    }
                  />
                </ListItem>
              ))}
            </List>
          </Box>

          <Box mt={2}>
            <Typography variant="subtitle2" color="text.secondary">
              Historical Summary
            </Typography>
            <Typography variant="body1" paragraph>
              {worldProfile.history_summary}
            </Typography>
          </Box>
        </AccordionDetails>
      </Accordion>

      {/* Geography Section - Accordion */}
      <Accordion sx={{ mb: 2 }}>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Box display="flex" alignItems="center">
            <TerrainIcon sx={{ mr: 1, color: "success.main" }} />
            <Typography variant="h6" color="success.main">
              Geography
            </Typography>
          </Box>
        </AccordionSummary>
        <AccordionDetails>
          <Box mb={2}>
            <Typography variant="subtitle2" color="text.secondary">
              Size & Scale
            </Typography>
            <Typography variant="body1" paragraph>
              {worldProfile.size_and_scale}
            </Typography>
          </Box>

          <Box mb={2}>
            <Typography variant="subtitle2" color="text.secondary" gutterBottom>
              Climate Zones
            </Typography>
            <Box display="flex" flexWrap="wrap" gap={1}>
              {worldProfile.climate_zones?.map((zone, index) => (
                <Chip
                  key={index}
                  label={zone}
                  color="success"
                  variant="outlined"
                  size="small"
                />
              ))}
            </Box>
          </Box>

          <Box mb={2}>
            <Typography variant="subtitle2" color="text.secondary" gutterBottom>
              Major Regions
            </Typography>
            <Grid container spacing={2}>
              {worldProfile.major_regions?.map((region, index) => (
                <Grid item xs={12} sm={6} key={index}>
                  <Paper elevation={1} sx={{ p: 2 }}>
                    <Typography variant="subtitle1" fontWeight="bold">
                      {region.name}
                    </Typography>
                    <Typography variant="body2">
                      {region.description}
                    </Typography>
                  </Paper>
                </Grid>
              ))}
            </Grid>
          </Box>

          <Box mb={2}>
            <Typography variant="subtitle2" color="text.secondary" gutterBottom>
              Natural Wonders
            </Typography>
            <List dense>
              {worldProfile.natural_wonders?.map((wonder, index) => (
                <ListItem key={index}>
                  <ListItemText primary={`✨ ${wonder}`} />
                </ListItem>
              ))}
            </List>
          </Box>

          <Box>
            <Typography variant="subtitle2" color="text.secondary">
              Geography Summary
            </Typography>
            <Typography variant="body1" paragraph>
              {worldProfile.geography_summary}
            </Typography>
          </Box>
        </AccordionDetails>
      </Accordion>

      {/* Culture & Society Section - Accordion */}
      <Accordion sx={{ mb: 2 }}>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Box display="flex" alignItems="center">
            <GroupsIcon sx={{ mr: 1, color: "secondary.main" }} />
            <Typography variant="h6" color="secondary.main">
              Culture & Society
            </Typography>
          </Box>
        </AccordionSummary>
        <AccordionDetails>
          <Grid container spacing={2} mb={2}>
            <Grid item xs={12} sm={6}>
              <Typography variant="subtitle2" color="text.secondary">
                Dominant Species
              </Typography>
              <Typography variant="body1">
                {worldProfile.dominant_species}
              </Typography>
            </Grid>
            <Grid item xs={12} sm={6}>
              <Typography variant="subtitle2" color="text.secondary">
                Population
              </Typography>
              <Typography variant="body1">
                {worldProfile.population_estimate}
              </Typography>
            </Grid>
          </Grid>

          <Box mb={2}>
            <Typography variant="subtitle2" color="text.secondary" gutterBottom>
              Major Civilizations
            </Typography>
            <Grid container spacing={2}>
              {worldProfile.major_civilizations?.map((civ, index) => (
                <Grid item xs={12} md={6} key={index}>
                  <Paper elevation={1} sx={{ p: 2 }}>
                    <Typography variant="subtitle1" fontWeight="bold">
                      {civ.name}
                    </Typography>
                    <Typography variant="body2">{civ.description}</Typography>
                  </Paper>
                </Grid>
              ))}
            </Grid>
          </Box>

          <Box mb={2}>
            <Typography variant="subtitle2" color="text.secondary" gutterBottom>
              Languages
            </Typography>
            <Box display="flex" flexWrap="wrap" gap={1}>
              {worldProfile.languages?.map((lang, index) => (
                <Chip key={index} label={lang} size="small" />
              ))}
            </Box>
          </Box>

          <Box mb={2}>
            <Typography variant="subtitle2" color="text.secondary" gutterBottom>
              Religions & Beliefs
            </Typography>
            <List dense>
              {worldProfile.religions_and_beliefs?.map((religion, index) => (
                <ListItem key={index}>
                  <ListItemText primary={`• ${religion}`} />
                </ListItem>
              ))}
            </List>
          </Box>

          <Box mb={2}>
            <Typography variant="subtitle2" color="text.secondary" gutterBottom>
              Cultural Norms
            </Typography>
            <List dense>
              {worldProfile.cultural_norms?.map((norm, index) => (
                <ListItem key={index}>
                  <ListItemText primary={`• ${norm}`} />
                </ListItem>
              ))}
            </List>
          </Box>

          <Box>
            <Typography variant="subtitle2" color="text.secondary">
              Culture Summary
            </Typography>
            <Typography variant="body1" paragraph>
              {worldProfile.culture_summary}
            </Typography>
          </Box>
        </AccordionDetails>
      </Accordion>

      {/* Magic/Technology System - Accordion */}
      <Accordion sx={{ mb: 2 }}>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Box display="flex" alignItems="center">
            <AutoFixHighIcon sx={{ mr: 1, color: "error.main" }} />
            <Typography variant="h6" color="error.main">
              Magic/Technology System
            </Typography>
          </Box>
        </AccordionSummary>
        <AccordionDetails>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6}>
              <Typography variant="subtitle2" color="text.secondary">
                Power System
              </Typography>
              <Typography variant="body1" gutterBottom>
                {worldProfile.power_system}
              </Typography>
            </Grid>
            <Grid item xs={12} sm={6}>
              <Typography variant="subtitle2" color="text.secondary">
                Power Level
              </Typography>
              <Typography variant="body1" gutterBottom>
                {worldProfile.power_level}
              </Typography>
            </Grid>
            <Grid item xs={12}>
              <Typography variant="subtitle2" color="text.secondary">
                Limitations
              </Typography>
              <Typography variant="body1" paragraph>
                {worldProfile.limitations}
              </Typography>
            </Grid>
          </Grid>

          <Box mt={2}>
            <Typography variant="subtitle2" color="text.secondary" gutterBottom>
              Notable Artifacts
            </Typography>
            <List dense>
              {worldProfile.notable_artifacts?.map((artifact, index) => (
                <ListItem key={index}>
                  <ListItemText primary={`⚡ ${artifact}`} />
                </ListItem>
              ))}
            </List>
          </Box>
        </AccordionDetails>
      </Accordion>

      {/* Conflicts & Themes - Accordion */}
      <Accordion sx={{ mb: 2 }}>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Box display="flex" alignItems="center">
            <GavelIcon sx={{ mr: 1, color: "warning.main" }} />
            <Typography variant="h6" color="warning.main">
              Conflicts & Themes
            </Typography>
          </Box>
        </AccordionSummary>
        <AccordionDetails>
          <Box mb={2}>
            <Typography variant="subtitle2" color="text.secondary" gutterBottom>
              Major Conflicts
            </Typography>
            <List>
              {worldProfile.major_conflicts?.map((conflict, index) => (
                <ListItem key={index}>
                  <ListItemText primary={`⚔️ ${conflict}`} />
                </ListItem>
              ))}
            </List>
          </Box>

          <Box mb={2}>
            <Typography variant="subtitle2" color="text.secondary">
              Central Themes
            </Typography>
            <Typography variant="body1" paragraph>
              {worldProfile.central_themes}
            </Typography>
          </Box>

          <Box>
            <Typography variant="subtitle2" color="text.secondary">
              Current Threats
            </Typography>
            <Typography variant="body1" paragraph>
              {worldProfile.current_threats}
            </Typography>
          </Box>
        </AccordionDetails>
      </Accordion>

      {/* Lore & Mysteries - Accordion */}
      <Accordion sx={{ mb: 2 }}>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Box display="flex" alignItems="center">
            <MenuBookIcon sx={{ mr: 1, color: "info.main" }} />
            <Typography variant="h6" color="info.main">
              Lore & Mysteries
            </Typography>
          </Box>
        </AccordionSummary>
        <AccordionDetails>
          <Box mb={2}>
            <Typography variant="subtitle2" color="text.secondary">
              Legends & Myths
            </Typography>
            <Typography variant="body1" paragraph>
              {worldProfile.legends_and_myths}
            </Typography>
          </Box>

          <Box mb={2}>
            <Typography variant="subtitle2" color="text.secondary">
              Unsolved Mysteries
            </Typography>
            <Typography variant="body1" paragraph>
              {worldProfile.unsolved_mysteries}
            </Typography>
          </Box>

          <Box mb={2}>
            <Typography variant="subtitle2" color="text.secondary">
              Prophecies
            </Typography>
            <Typography variant="body1" paragraph>
              {worldProfile.prophecies}
            </Typography>
          </Box>

          <Box>
            <Typography variant="subtitle2" color="text.secondary">
              Lore Summary
            </Typography>
            <Typography variant="body1" paragraph>
              {worldProfile.lore_summary}
            </Typography>
          </Box>
        </AccordionDetails>
      </Accordion>

      {/* Story Potential - Accordion */}
      <Accordion sx={{ mb: 2 }}>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Box display="flex" alignItems="center">
            <ExploreIcon sx={{ mr: 1, color: "primary.main" }} />
            <Typography variant="h6" color="primary">
              Story Potential
            </Typography>
          </Box>
        </AccordionSummary>
        <AccordionDetails>
          <Box mb={2}>
            <Typography variant="subtitle2" color="text.secondary" gutterBottom>
              Adventure Hooks
            </Typography>
            <List>
              {worldProfile.adventure_hooks?.map((hook, index) => (
                <ListItem key={index}>
                  <ListItemText primary={`🎯 ${hook}`} />
                </ListItem>
              ))}
            </List>
          </Box>

          <Box mb={2}>
            <Typography variant="subtitle2" color="text.secondary" gutterBottom>
              Notable Locations
            </Typography>
            <Grid container spacing={2}>
              {worldProfile.notable_locations?.map((location, index) => (
                <Grid item xs={12} sm={6} key={index}>
                  <Paper elevation={1} sx={{ p: 2 }}>
                    <Typography variant="subtitle1" fontWeight="bold">
                      {location.name}
                    </Typography>
                    <Typography
                      variant="caption"
                      color="text.secondary"
                      display="block"
                      gutterBottom
                    >
                      {location.type}
                    </Typography>
                    <Typography variant="body2">
                      {location.description}
                    </Typography>
                  </Paper>
                </Grid>
              ))}
            </Grid>
          </Box>

          <Box>
            <Typography variant="subtitle2" color="text.secondary">
              Unique Aspects
            </Typography>
            <Typography variant="body1" paragraph>
              {worldProfile.unique_aspects}
            </Typography>
          </Box>
        </AccordionDetails>
      </Accordion>
    </Box>
  );
};

export default StructuredWorldDisplay;
