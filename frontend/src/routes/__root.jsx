import { createRootRoute, Outlet, Link } from "@tanstack/react-router";
import { TanStackRouterDevtools } from "@tanstack/react-router-devtools";
import { useState } from "react";
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

function NotFoundComponent() {
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

export const Route = createRootRoute({
  component: RootComponent,
  notFoundComponent: NotFoundComponent,
});

function RootComponent() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down("md"));

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
                  color="inherit"
                  component={Link}
                  to={item.path}
                  sx={{
                    ...(item.highlight && {
                      background:
                        "linear-gradient(45deg, #9c27b0 30%, #00bcd4 90%)",
                      "&:hover": {
                        background:
                          "linear-gradient(45deg, #7b1fa2 30%, #0097a7 90%)",
                      },
                    }),
                  }}
                >
                  {item.label}
                </Button>
              ))}
            </Box>
          )}

          {/* Mobile Menu Button */}
          {isMobile && (
            <IconButton
              color="inherit"
              aria-label="open menu"
              edge="end"
              onClick={handleDrawerToggle}
              sx={{ ml: 1 }}
            >
              <MenuIcon />
            </IconButton>
          )}
        </Toolbar>
      </AppBar>

      {/* Mobile Drawer Menu */}
      <Drawer
        anchor="right"
        open={mobileMenuOpen}
        onClose={handleDrawerClose}
        sx={{
          display: { xs: "block", md: "none" },
          "& .MuiDrawer-paper": {
            width: 280,
            maxWidth: "80vw",
          },
        }}
      >
        <Box sx={{ p: 2, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <Typography variant="h6" sx={{ display: "flex", alignItems: "center", gap: 1 }}>
            <MenuBookIcon />
            StoryCraft
          </Typography>
          <IconButton onClick={handleDrawerClose} aria-label="close menu">
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
                sx={{
                  py: 1.5,
                  ...(item.highlight && {
                    background:
                      "linear-gradient(45deg, #9c27b0 30%, #00bcd4 90%)",
                    "&:hover": {
                      background:
                        "linear-gradient(45deg, #7b1fa2 30%, #0097a7 90%)",
                    },
                  }),
                }}
              >
                <ListItemIcon sx={{ minWidth: 40, color: "inherit" }}>
                  {item.icon}
                </ListItemIcon>
                <ListItemText primary={item.label} />
              </ListItemButton>
            </ListItem>
          ))}
        </List>
      </Drawer>

      <Container component="main" sx={{ flex: 1, py: 4 }}>
        <Outlet />
      </Container>

      <Box
        component="footer"
        sx={{
          py: 3,
          px: 2,
          mt: "auto",
          backgroundColor: (theme) => theme.palette.background.paper,
        }}
      >
        <Container maxWidth="lg">
          <Typography variant="body2" color="text.secondary" align="center">
            {"StoryCraft © "}
            {new Date().getFullYear()}
            {" - AI-Powered Story Creation"}
          </Typography>
        </Container>
      </Box>

      <TanStackRouterDevtools position="bottom-right" />
    </Box>
  );
}
