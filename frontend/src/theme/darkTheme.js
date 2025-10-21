import { createTheme } from "@mui/material/styles";

export const darkTheme = createTheme({
  // Define custom breakpoints if needed (optional - using defaults)
  breakpoints: {
    values: {
      xs: 0,
      sm: 600,
      md: 900,
      lg: 1200,
      xl: 1536,
    },
  },
  palette: {
    mode: "dark",
    primary: {
      main: "#9c27b0", // Deep purple
      light: "#ba68c8",
      dark: "#7b1fa2",
      contrastText: "#ffffff",
    },
    secondary: {
      main: "#00bcd4", // Cyan
      light: "#4dd0e1",
      dark: "#0097a7",
      contrastText: "#000000",
    },
    background: {
      default: "#0a0a0a",
      paper: "#1a1a1a",
    },
    text: {
      primary: "#ffffff",
      secondary: "#b0b0b0",
    },
    error: {
      main: "#f44336",
    },
    warning: {
      main: "#ff9800",
    },
    info: {
      main: "#2196f3",
    },
    success: {
      main: "#4caf50",
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
    // Card spacing adjustments
    MuiCard: {
      styleOverrides: {
        root: {
          backgroundImage: "none",
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
    // Paper component
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundImage: "none",
          "@media (max-width:600px)": {
            borderRadius: "4px",
          },
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
