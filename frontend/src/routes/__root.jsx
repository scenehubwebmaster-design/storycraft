import { createRootRoute, Outlet, Link } from "@tanstack/react-router";
import { TanStackRouterDevtools } from "@tanstack/react-router-devtools";
import {
  AppBar,
  Toolbar,
  Typography,
  Container,
  Box,
  Button,
  IconButton,
  Paper,
} from "@mui/material";
import MenuBookIcon from "@mui/icons-material/MenuBook";
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
  return (
    <Box sx={{ display: "flex", flexDirection: "column", minHeight: "100vh" }}>
      <AppBar position="static" elevation={0}>
        <Toolbar>
          <IconButton
            size="large"
            edge="start"
            color="inherit"
            aria-label="menu"
            sx={{ mr: 2 }}
          >
            <MenuBookIcon />
          </IconButton>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            StoryCraft
          </Typography>
          <Button color="inherit" component={Link} to="/" sx={{ mx: 1 }}>
            Home
          </Button>
          <Button
            color="inherit"
            component={Link}
            to="/create"
            sx={{
              mx: 1,
              background: "linear-gradient(45deg, #9c27b0 30%, #00bcd4 90%)",
              "&:hover": {
                background: "linear-gradient(45deg, #7b1fa2 30%, #0097a7 90%)",
              },
            }}
          >
            Create
          </Button>
          <Button color="inherit" component={Link} to="/stories" sx={{ mx: 1 }}>
            Stories
          </Button>
          <Button
            color="inherit"
            component={Link}
            to="/characters"
            sx={{ mx: 1 }}
          >
            Characters
          </Button>
          <Button color="inherit" component={Link} to="/worlds" sx={{ mx: 1 }}>
            Worlds
          </Button>
          <Button
            color="inherit"
            component={Link}
            to="/settings"
            sx={{ mx: 1 }}
          >
            Settings
          </Button>
        </Toolbar>
      </AppBar>

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
