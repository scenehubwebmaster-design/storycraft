import {
  createFileRoute,
  Link,
  Outlet,
  useMatches,
} from "@tanstack/react-router";
import {
  Container,
  Typography,
  Grid,
  Card,
  CardContent,
  CardActions,
  Button,
  Box,
} from "@mui/material";
import PeopleIcon from "@mui/icons-material/People";
import AutoStoriesIcon from "@mui/icons-material/AutoStories";
import PublicIcon from "@mui/icons-material/Public";
import LocationOnIcon from "@mui/icons-material/LocationOn";
import TheaterComedyIcon from "@mui/icons-material/TheaterComedy";

export const Route = createFileRoute("/create")({
  component: CreateComponent,
});

function CreateComponent() {
  const matches = useMatches();

  // Check if we're at exactly /create (no child route active)
  const isCreateIndex =
    matches.length === 2 && matches[matches.length - 1].id === "/create";

  const creationTypes = [
    {
      title: "Character",
      description:
        "Design rich, complex characters with AI-generated backstories, motivations, and personality traits.",
      icon: <PeopleIcon sx={{ fontSize: 60, color: "primary.main" }} />,
      link: "/create/character",
      color: "primary.main",
    },
    {
      title: "Story",
      description:
        "Create compelling story outlines with plot structures, themes, and narrative arcs.",
      icon: <AutoStoriesIcon sx={{ fontSize: 60, color: "secondary.main" }} />,
      link: "/create/story",
      color: "secondary.main",
    },
    {
      title: "World",
      description:
        "Build immersive worlds with detailed lore, geography, cultures, and magic systems.",
      icon: <PublicIcon sx={{ fontSize: 60, color: "info.main" }} />,
      link: "/create/world",
      color: "info.main",
    },
    {
      title: "Scene",
      description:
        "Write vivid, engaging scenes with rich sensory details and character interactions.",
      icon: <TheaterComedyIcon sx={{ fontSize: 60, color: "success.main" }} />,
      link: "/create/scene",
      color: "success.main",
    },
    {
      title: "Location",
      description:
        "Design atmospheric locations with history, description, and story potential.",
      icon: <LocationOnIcon sx={{ fontSize: 60, color: "warning.main" }} />,
      link: "/create/location",
      color: "warning.main",
    },
  ];

  // If we're at a child route, render the child component via Outlet
  if (!isCreateIndex) {
    return <Outlet />;
  }

  // Otherwise, show the creation type selector
  return (
    <Container maxWidth="lg">
      <Box sx={{ textAlign: "center", mb: 6 }}>
        <Typography
          variant="h3"
          component="h1"
          gutterBottom
          sx={{
            fontWeight: 700,
            background: "linear-gradient(45deg, #9c27b0 30%, #00bcd4 90%)",
            backgroundClip: "text",
            WebkitBackgroundClip: "text",
            WebkitTextFillColor: "transparent",
          }}
        >
          Create with AI
        </Typography>
        <Typography variant="h6" color="text.secondary" paragraph>
          Choose what you'd like to create and let AI assist you
        </Typography>
      </Box>

      <Grid container spacing={4}>
        {creationTypes.map((type) => (
          <Grid size={{ xs: 12, md: 6 }} key={type.title}>
            <Card
              sx={{
                height: "100%",
                display: "flex",
                flexDirection: "column",
                transition: "transform 0.2s, box-shadow 0.2s",
                "&:hover": {
                  transform: "translateY(-8px)",
                  boxShadow: 6,
                },
              }}
            >
              <CardContent sx={{ flexGrow: 1 }}>
                <Box
                  sx={{
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    mb: 2,
                  }}
                >
                  {type.icon}
                </Box>
                <Typography
                  variant="h5"
                  component="h2"
                  gutterBottom
                  align="center"
                >
                  {type.title}
                </Typography>
                <Typography
                  variant="body1"
                  color="text.secondary"
                  align="center"
                >
                  {type.description}
                </Typography>
              </CardContent>
              <CardActions sx={{ justifyContent: "center", pb: 3 }}>
                <Link
                  to={type.link}
                  from="/create"
                  style={{ textDecoration: "none" }}
                >
                  <Button
                    variant="contained"
                    size="large"
                    sx={{
                      background: `linear-gradient(45deg, ${type.color} 30%, ${type.color}dd 90%)`,
                    }}
                  >
                    Create {type.title}
                  </Button>
                </Link>
              </CardActions>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Container>
  );
}
