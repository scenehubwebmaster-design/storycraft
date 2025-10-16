import { Link } from "react-router-dom";
import {
  Box,
  Typography,
  Button,
  Card,
  CardContent,
  Grid,
  Container,
} from "@mui/material";
import CreateIcon from "@mui/icons-material/Create";
import AutoStoriesIcon from "@mui/icons-material/AutoStories";
import PublicIcon from "@mui/icons-material/Public";
import PeopleIcon from "@mui/icons-material/People";

export default function HomePage() {
  return (
    <Container maxWidth="lg">
      <Box sx={{ textAlign: "center", mb: 6 }}>
        <Typography
          variant="h2"
          component="h1"
          gutterBottom
          sx={{
            fontWeight: 600,
            background: "linear-gradient(45deg, #9c27b0 30%, #00bcd4 90%)",
            backgroundClip: "text",
            WebkitBackgroundClip: "text",
            WebkitTextFillColor: "transparent",
          }}
        >
          Welcome to StoryCraft
        </Typography>
        <Typography variant="h5" color="text.secondary" paragraph>
          Create thoughtful and robust stories with AI assistance
        </Typography>
        <Button
          component={Link}
          to="/create"
          variant="contained"
          size="large"
          startIcon={<CreateIcon />}
          sx={{ mt: 2 }}
        >
          Start Creating
        </Button>
      </Box>

      <Grid container spacing={3}>
        <Grid size={{ xs: 12, md: 4 }}>
          <Card sx={{ height: "100%" }}>
            <CardContent>
              <Box sx={{ display: "flex", alignItems: "center", mb: 2 }}>
                <AutoStoriesIcon
                  sx={{ fontSize: 40, color: "primary.main", mr: 2 }}
                />
                <Typography variant="h5" component="h2">
                  Rich Stories
                </Typography>
              </Box>
              <Typography variant="body1" color="text.secondary">
                Draft novels, create campaign narratives, or develop any story
                with AI-powered chapters, plots, and scenes.
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid size={{ xs: 12, md: 4 }}>
          <Card sx={{ height: "100%" }}>
            <CardContent>
              <Box sx={{ display: "flex", alignItems: "center", mb: 2 }}>
                <PeopleIcon
                  sx={{ fontSize: 40, color: "secondary.main", mr: 2 }}
                />
                <Typography variant="h5" component="h2">
                  Deep Characters
                </Typography>
              </Box>
              <Typography variant="body1" color="text.secondary">
                Generate beautiful and rich characters with detailed
                backgrounds, motivations, and personality traits.
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid size={{ xs: 12, md: 4 }}>
          <Card sx={{ height: "100%" }}>
            <CardContent>
              <Box sx={{ display: "flex", alignItems: "center", mb: 2 }}>
                <PublicIcon sx={{ fontSize: 40, color: "info.main", mr: 2 }} />
                <Typography variant="h5" component="h2">
                  Vast Worlds
                </Typography>
              </Box>
              <Typography variant="body1" color="text.secondary">
                Build immersive worlds with detailed lore, locations, and
                histories that bring your stories to life.
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Box
        sx={{
          mt: 6,
          p: 4,
          backgroundColor: "background.paper",
          borderRadius: 2,
        }}
      >
        <Typography variant="h4" gutterBottom align="center">
          Powered by Leading AI Providers
        </Typography>
        <Typography variant="body1" color="text.secondary" align="center">
          Connect to Google, Claude, OpenAI, and more to leverage the power of
          AI in your creative process.
        </Typography>
      </Box>
    </Container>
  );
}
