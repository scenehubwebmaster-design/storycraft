import { createFileRoute, Link } from "@tanstack/react-router";
import { Typography, Box, Button } from "@mui/material";
import AddIcon from "@mui/icons-material/Add";

export const Route = createFileRoute("/stories")({
  component: StoriesComponent,
});

function StoriesComponent() {
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
          My Stories
        </Typography>
        <Button
          component={Link}
          to="/create/story"
          variant="contained"
          startIcon={<AddIcon />}
        >
          New Story
        </Button>
      </Box>
      <Typography variant="body1" color="text.secondary">
        Your stories will appear here. Start by creating your first story!
      </Typography>
    </Box>
  );
}
