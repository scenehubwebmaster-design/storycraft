import React, { useState } from "react";
import ReferenceViewer from "../components/ReferenceViewer";
import { Container, Typography, Tabs, Tab, Box } from "@mui/material";

export default function ReferencesPage() {
  const [refType, setRefType] = useState("classes_md");

  return (
    <Container maxWidth="xl">
      <Typography variant="h4" sx={{ mb: 2 }}>
        References
      </Typography>

      <Typography variant="body1" color="text.secondary" sx={{ mb: 2 }}>
        Browse official class, species, equipment, spell, and item
        documentation.
      </Typography>

      <Tabs
        value={refType}
        onChange={(_, v) => setRefType(v)}
        aria-label="Reference types"
        sx={{ mb: 2 }}
        variant="scrollable"
        scrollButtons="auto"
      >
        <Tab label="Classes" value="classes_md" />
        <Tab label="Species" value="species_md" />
        <Tab label="Monsters" value="monsters_md" />
        <Tab label="Equipment" value="equipment_md" />
        <Tab label="Magic Items" value="magic_items_md" />
        <Tab label="Spells" value="spells_md" />
        <Tab label="Tools" value="tools_md" />
        <Tab label="Weapons" value="weapons_md" />
      </Tabs>

      <Box sx={{ mt: 1 }}>
        <ReferenceViewer refType={refType} />
      </Box>
    </Container>
  );
}
