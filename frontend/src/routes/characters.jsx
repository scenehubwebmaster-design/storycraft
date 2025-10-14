import { createFileRoute, Link } from "@tanstack/react-router";
import { Typography, Box, Button } from "@mui/material";
import AddIcon from "@mui/icons-material/Add";

export const Route = createFileRoute("/characters")({
  component: CharactersComponent,
});

function CharactersComponent() {
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
          Characters
        </Typography>
        <Button
          component={Link}
          to="/create/character"
          variant="contained"
          startIcon={<AddIcon />}
        >
          New Character
        </Button>
      </Box>
      <Typography variant="body1" color="text.secondary">
        Create rich, detailed characters for your stories with AI assistance.
      </Typography>
    </Box>
  );
}
