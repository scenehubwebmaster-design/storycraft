import { createFileRoute, Link } from "@tanstack/react-router";
import { Typography, Box, Button } from "@mui/material";
import AddIcon from "@mui/icons-material/Add";

export const Route = createFileRoute("/worlds")({
  component: WorldsComponent,
});

function WorldsComponent() {
  return (
    <Box>
      <Box
        sx={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          mb: 4,
        }}
      >
        <Typography variant="h3" component="h1">
          Worlds & Lore
        </Typography>
        <Button
          component={Link}
          to="/create/world"
          variant="contained"
          startIcon={<AddIcon />}
        >
          New World
        </Button>
      </Box>
      <Typography variant="body1" color="text.secondary">
        Build immersive worlds with detailed lore, locations, and histories.
      </Typography>
    </Box>
  );
}
