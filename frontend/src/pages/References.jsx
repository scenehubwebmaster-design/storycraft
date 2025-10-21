import React from "react";
import ReferenceViewer from "../components/ReferenceViewer";
import { Container, Typography } from "@mui/material";

export default function ReferencesPage() {
  return (
    <Container maxWidth="lg">
      <Typography variant="h4" sx={{ mb: 2 }}>
        References
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 2 }}>
        Browse official class, species and equipment documentation.
      </Typography>
      <ReferenceViewer refType="class" />
    </Container>
  );
}
