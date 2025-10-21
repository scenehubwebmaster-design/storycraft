import {
  BrowserRouter,
  Routes,
  Route,
  Link,
  useLocation,
} from "react-router-dom";
import { useState } from "react";
import { createTheme, ThemeProvider } from "@mui/material/styles";
import { darkTheme } from "./theme/darkTheme";
import {
  AppBar,
  Toolbar,
  Typography,
  Container,
  Box,
  Button,
  IconButton,
  Paper,
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Divider,
  useMediaQuery,
  useTheme,
} from "@mui/material";
import MenuBookIcon from "@mui/icons-material/MenuBook";
import MenuIcon from "@mui/icons-material/Menu";
import CloseIcon from "@mui/icons-material/Close";
import HomeIcon from "@mui/icons-material/Home";
import CreateIcon from "@mui/icons-material/Create";
import AutoStoriesIcon from "@mui/icons-material/AutoStories";
import PeopleIcon from "@mui/icons-material/People";
import PublicIcon from "@mui/icons-material/Public";
import SettingsIcon from "@mui/icons-material/Settings";
import ErrorOutlineIcon from "@mui/icons-material/ErrorOutline";

// Route Components
import HomePage from "./pages/Home";
import CreatePage from "./pages/Create";
import CreateCharacterPage from "./pages/CreateCharacter";
import CreateStoryPage from "./pages/CreateStory";
import CreateWorldPage from "./pages/CreateWorld";
import CreateScenePage from "./pages/CreateScene";
import CreateLocationPage from "./pages/CreateLocation";
import StoriesPage from "./pages/Stories";
import StoryDetailPage from "./pages/StoryDetail";
import CharactersPage from "./pages/Characters";
import CharacterDetailPage from "./pages/CharacterDetail";
import WorldsPage from "./pages/Worlds";
import WorldDetailPage from "./pages/WorldDetail";
import SettingsPage from "./pages/Settings";

function NotFound() {
  return (
    <Container maxWidth="md">
      <Paper sx={{ p: 6, textAlign: "center", mt: 8 }}>
        <ErrorOutlineIcon sx={{ fontSize: 80, color: "error.main", mb: 2 }} />
        <Typography variant="h3" gutterBottom>
          404 - Page Not Found
        </Typography>
        <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
          The page you're looking for doesn't exist or has been moved.
        </Typography>
        <Button component={Link} to="/" variant="contained" size="large">
          Return to Home
        </Button>
      </Paper>
    </Container>
  );
}

function Layout({ children }) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down("md"));
  const location = useLocation();

  const navigationItems = [
    { label: "Home", path: "/", icon: <HomeIcon /> },
    { label: "Create", path: "/create", icon: <CreateIcon />, highlight: true },
    { label: "Stories", path: "/stories", icon: <AutoStoriesIcon /> },
    { label: "Characters", path: "/characters", icon: <PeopleIcon /> },
    { label: "Worlds", path: "/worlds", icon: <PublicIcon /> },
    { label: "Settings", path: "/settings", icon: <SettingsIcon /> },
  ];

  const handleDrawerToggle = () => {
    setMobileMenuOpen(!mobileMenuOpen);
  };

  const handleDrawerClose = () => {
    setMobileMenuOpen(false);
  };

  return (
    <Box sx={{ display: "flex", flexDirection: "column", minHeight: "100vh" }}>
      <AppBar position="static" elevation={0}>
        <Toolbar>
          <IconButton
            size="large"
            edge="start"
            color="inherit"
            aria-label="logo"
            sx={{ mr: { xs: 1, sm: 2 } }}
            component={Link}
            to="/"
          >
            <MenuBookIcon />
          </IconButton>
          <Typography
            variant="h6"
            component="div"
            sx={{
              flexGrow: 1,
              fontSize: { xs: "1rem", sm: "1.25rem" },
            }}
          >
            StoryCraft
          </Typography>

          {/* Desktop Navigation */}
          {!isMobile && (
            <Box sx={{ display: "flex", gap: 1 }}>
              {navigationItems.map((item) => (
                <Button
                  key={item.path}
                  component={Link}
                  to={item.path}
                  color="inherit"
                  startIcon={item.icon}
                  sx={{
                    ...(item.highlight && {
                      background:
                        "linear-gradient(45deg, #FF6B6B 30%, #4ECDC4 90%)",
                      "&:hover": {
                        background:
                          "linear-gradient(45deg, #FF8787 30%, #6FE0D8 90%)",
                      },
                    }),
                  }}
                >
                  {item.label}
                </Button>
              ))}
            </Box>
          )}

          {/* Mobile Hamburger Menu */}
          {isMobile && (
            <IconButton
              color="inherit"
              aria-label="open drawer"
              edge="end"
              onClick={handleDrawerToggle}
            >
              <MenuIcon />
            </IconButton>
          )}
        </Toolbar>
      </AppBar>

      {/* Mobile Drawer */}
      <Drawer
        anchor="right"
        open={mobileMenuOpen}
        onClose={handleDrawerClose}
        sx={{
          "& .MuiDrawer-paper": {
            width: 280,
            maxWidth: "80vw",
          },
        }}
      >
        <Box
          sx={{
            p: 2,
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
          }}
        >
          <Typography variant="h6">StoryCraft</Typography>
          <IconButton onClick={handleDrawerClose}>
            <CloseIcon />
          </IconButton>
        </Box>
        <Divider />
        <List>
          {navigationItems.map((item) => (
            <ListItem key={item.path} disablePadding>
              <ListItemButton
                component={Link}
                to={item.path}
                onClick={handleDrawerClose}
                selected={location.pathname === item.path}
                sx={{
                  ...(item.highlight && {
                    background:
                      "linear-gradient(45deg, #FF6B6B 30%, #4ECDC4 90%)",
                    "&:hover": {
                      background:
                        "linear-gradient(45deg, #FF8787 30%, #6FE0D8 90%)",
                    },
                  }),
                }}
              >
                <ListItemIcon
                  sx={{ color: item.highlight ? "white" : "inherit" }}
                >
                  {item.icon}
                </ListItemIcon>
                <ListItemText
                  primary={item.label}
                  sx={{ color: item.highlight ? "white" : "inherit" }}
                />
              </ListItemButton>
            </ListItem>
          ))}
        </List>
      </Drawer>

      {/* Main Content */}
      <Container
        component="main"
        maxWidth="xl"
        sx={{
          flexGrow: 1,
          py: { xs: 2, sm: 3, md: 4 },
          px: { xs: 2, sm: 3 },
        }}
      >
        {children}
      </Container>

      {/* Footer */}
      <Box
        component="footer"
        sx={{
          py: 3,
          px: 2,
          mt: "auto",
          backgroundColor: "background.paper",
          borderTop: 1,
          borderColor: "divider",
        }}
      >
        <Container maxWidth="xl">
          <Typography variant="body2" color="text.secondary" align="center">
            StoryCraft © {new Date().getFullYear()} - AI-Powered Story Creation
          </Typography>
        </Container>
      </Box>
    </Box>
  );
}

export default function App() {
  // Merge darkTheme with Poppins typography so we keep the dark palette
  const theme = createTheme(darkTheme, {
    typography: {
      fontFamily: ['"Poppins", "Helvetica", "Arial", sans-serif'].join(","),
    },
  });

  // Ensure Poppins font is loaded via Google Fonts link in the document head
  // (This is lightweight and safe for client-side apps)
  if (typeof document !== "undefined") {
    const id = "poppins-font-link";
    if (!document.getElementById(id)) {
      const link = document.createElement("link");
      link.id = id;
      link.rel = "stylesheet";
      link.href =
        "https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap";
      document.head.appendChild(link);
    }
  }
  return (
    <ThemeProvider theme={theme}>
      <BrowserRouter>
        <Layout>
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/create" element={<CreatePage />} />
            <Route path="/create/character" element={<CreateCharacterPage />} />
            <Route path="/create/story" element={<CreateStoryPage />} />
            <Route path="/create/world" element={<CreateWorldPage />} />
            <Route path="/create/scene" element={<CreateScenePage />} />
            <Route path="/create/location" element={<CreateLocationPage />} />
            <Route path="/stories" element={<StoriesPage />} />
            <Route path="/stories/:storyId" element={<StoryDetailPage />} />
            <Route path="/characters" element={<CharactersPage />} />
            <Route
              path="/characters/:characterId"
              element={<CharacterDetailPage />}
            />
            <Route path="/worlds" element={<WorldsPage />} />
            <Route path="/worlds/:worldId" element={<WorldDetailPage />} />
            <Route path="/settings" element={<SettingsPage />} />
            <Route path="*" element={<NotFound />} />
          </Routes>
        </Layout>
      </BrowserRouter>
    </ThemeProvider>
  );
}
