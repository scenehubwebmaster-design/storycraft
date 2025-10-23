import { createTheme } from "@mui/material/styles";

export const darkTheme = createTheme({
  // Define custom breakpoints if needed (optional - using defaults)
  breakpoints: {
    values: {
      xs: 0,
      sm: 600,
      md: 1080, // raised md breakpoint so mobile/tabbed views apply below 1080px
      lg: 1200,
      xl: 1536,
    },
  },
  palette: {
    mode: "dark",
    primary: {
      main: "rgba(185, 167, 0, 1)", // Rich gold (coins, treasure, magic)
      light: "#685202ff",
      dark: "#6d550cff",
      contrastText: "#1a0f00",
    },
    secondary: {
      main: "#8b0000", // Deep burgundy/crimson (dragons, epic battles)
      light: "#b71c1c",
      dark: "#5a0000",
      contrastText: "#ffffff",
    },
    background: {
      default: "#0d0d0d", // Deep dungeon black
      paper: "#1c1410", // Aged parchment brown-black
    },
    text: {
      primary: "#f5e6d3", // Warm parchment white
      secondary: "#b89968", // Faded gold text
    },
    error: {
      main: "#d32f2f", // Blood red
    },
    warning: {
      main: "#ff8f00", // Torch orange
    },
    info: {
      main: "#4a90e2", // Arcane blue
    },
    success: {
      main: "#2e7d32", // Forest green (nature, healing)
    },
  },
  typography: {
    fontFamily: '"Poppins", "Helvetica", "Arial", sans-serif',
    // Adjusted typography scales for Poppins: slightly tighter headings, higher weight
    h1: {
      fontSize: "2.25rem",
      fontWeight: 600,
      letterSpacing: "-0.02em",
      "@media (max-width:600px)": {
        fontSize: "1.9rem",
      },
    },
    h2: {
      fontSize: "1.9rem",
      fontWeight: 600,
      letterSpacing: "-0.01em",
      "@media (max-width:600px)": {
        fontSize: "1.6rem",
      },
    },
    h3: {
      fontSize: "1.6rem",
      fontWeight: 600,
      letterSpacing: "0em",
      "@media (max-width:600px)": {
        fontSize: "1.35rem",
      },
    },
    h4: {
      fontSize: "1.35rem",
      fontWeight: 600,
      letterSpacing: "0.005em",
      "@media (max-width:600px)": {
        fontSize: "1.15rem",
      },
    },
    h5: {
      fontSize: "1.15rem",
      fontWeight: 600,
      letterSpacing: "0em",
      "@media (max-width:600px)": {
        fontSize: "1rem",
      },
    },
    h6: {
      fontSize: "1rem",
      fontWeight: 600,
      letterSpacing: "0.01em",
      "@media (max-width:600px)": {
        fontSize: "0.95rem",
      },
    },
    body1: {
      fontSize: "0.98rem",
      letterSpacing: "0.01em",
      "@media (max-width:600px)": {
        fontSize: "0.95rem",
      },
    },
    body2: {
      fontSize: "0.86rem",
      letterSpacing: "0.01em",
    },
  },
  spacing: 8, // Default spacing unit (1 spacing = 8px)
  shape: {
    borderRadius: 8,
  },
  components: {
    // Global responsive container settings
    MuiContainer: {
      styleOverrides: {
        root: {
          paddingLeft: "16px",
          paddingRight: "16px",
          "@media (max-width:600px)": {
            paddingLeft: "12px",
            paddingRight: "12px",
          },
        },
      },
    },
    // Responsive button sizing
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: "none",
          fontWeight: 500,
          minHeight: "44px", // Minimum touch target size (accessibility)
          "@media (max-width:600px)": {
            minHeight: "48px", // Larger on mobile for easier tapping
            fontSize: "0.95rem",
          },
        },
        sizeLarge: {
          "@media (max-width:600px)": {
            padding: "12px 24px",
          },
        },
      },
    },
    // Icon buttons with proper touch targets
    MuiIconButton: {
      styleOverrides: {
        root: {
          "@media (max-width:600px)": {
            padding: "12px", // Larger touch target on mobile
          },
        },
      },
    },
    // Card spacing adjustments with fantasy border
    MuiCard: {
      styleOverrides: {
        root: {
          backgroundImage: "none",
          backgroundColor: "#1c1410",
          borderWidth: "1px",
          borderStyle: "solid",
          borderColor: "#3d2f1f", // Subtle wood/leather border
          transition: "all 0.2s ease-in-out",
          "&:hover": {
            borderColor: "#d4af37", // Gold border on hover
            boxShadow: "0 0 12px rgba(212, 175, 55, 0.3)", // Golden glow
          },
          "@media (max-width:600px)": {
            borderRadius: "4px", // Slightly less rounded on mobile
          },
        },
      },
    },
    MuiCardContent: {
      styleOverrides: {
        root: {
          "@media (max-width:600px)": {
            padding: "12px", // Tighter padding on mobile
            "&:last-child": {
              paddingBottom: "12px",
            },
          },
        },
      },
    },
    // Paper component with enhanced borders for panels
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundImage: "none",
          backgroundColor: "#1c1410",
          borderWidth: "1px",
          borderStyle: "solid",
          borderColor: "#3d2f1f",
          "@media (max-width:600px)": {
            borderRadius: "4px",
          },
        },
        elevation1: {
          boxShadow: "0 2px 4px rgba(0,0,0,0.4)",
        },
        elevation2: {
          borderColor: "#4d3f2f", // Slightly lighter border for elevated panels
          boxShadow: "0 3px 6px rgba(0,0,0,0.5)",
        },
        elevation4: {
          borderColor: "#d4af37", // Gold border for highly elevated elements
          boxShadow: "0 4px 12px rgba(212,175,55,0.2)",
        },
      },
    },
    // TextField optimizations for mobile
    MuiTextField: {
      styleOverrides: {
        root: {
          "@media (max-width:600px)": {
            "& .MuiInputBase-root": {
              fontSize: "16px", // Prevents zoom on iOS
            },
          },
        },
      },
    },
    // Select dropdown optimizations
    MuiSelect: {
      styleOverrides: {
        root: {
          "@media (max-width:600px)": {
            fontSize: "16px", // Prevents zoom on iOS
          },
        },
      },
    },
    // AppBar mobile optimization
    MuiAppBar: {
      styleOverrides: {
        root: {
          "@media (max-width:600px)": {
            "& .MuiToolbar-root": {
              minHeight: "56px",
              paddingLeft: "8px",
              paddingRight: "8px",
            },
          },
        },
      },
    },
    // Toolbar mobile spacing
    MuiToolbar: {
      styleOverrides: {
        root: {
          "@media (max-width:600px)": {
            minHeight: "56px",
            paddingLeft: "8px",
            paddingRight: "8px",
          },
        },
      },
    },
    // Dialog full-screen on mobile
    MuiDialog: {
      styleOverrides: {
        paper: {
          "@media (max-width:600px)": {
            margin: "16px",
            maxHeight: "calc(100% - 32px)",
            borderRadius: "8px",
          },
        },
      },
    },
    // Stepper mobile optimization
    MuiStepper: {
      styleOverrides: {
        root: {
          "@media (max-width:600px)": {
            padding: "12px 4px",
          },
        },
      },
    },
    MuiStepLabel: {
      styleOverrides: {
        label: {
          "@media (max-width:600px)": {
            fontSize: "0.8rem",
          },
        },
      },
    },
    // Chip mobile sizing
    MuiChip: {
      styleOverrides: {
        root: {
          "@media (max-width:600px)": {
            height: "28px",
            fontSize: "0.8rem",
          },
        },
      },
    },
    // Table responsive behavior
    MuiTableCell: {
      styleOverrides: {
        root: {
          "@media (max-width:600px)": {
            padding: "8px",
            fontSize: "0.85rem",
          },
        },
      },
    },
  },
});
