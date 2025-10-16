# Mobile Styling Guide for StoryCraft

## Overview

This guide documents the mobile-first responsive design implementation for StoryCraft using Material-UI (MUI) best practices.

## Key Implementations

### 1. ✅ Viewport Meta Tag
**Location:** `frontend/index.html`
```html
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
```
- Ensures proper rendering on all devices
- Enables responsive design and touch zooming
- **Mobile-first requirement** ✓

### 2. ✅ CssBaseline Component
**Location:** `frontend/src/main.jsx`
```jsx
import CssBaseline from "@mui/material/CssBaseline";
// Applied in ThemeProvider wrapper
```
- Normalizes cross-browser inconsistencies
- Provides better defaults than normalize.css
- Tailored for Material-UI components
- **MUI best practice** ✓

### 3. ✅ Network Exposure Configuration
**Location:** `frontend/package.json`
```json
"dev": "vite --host"
```
- Exposes dev server on all network interfaces
- Enables testing on mobile devices
- Shows network IP for remote access
- **Mobile testing enabled** ✓

## Enhanced Theme Configuration

### Responsive Breakpoints
**Location:** `frontend/src/theme/darkTheme.js`

Default MUI breakpoints used:
- **xs** (extra-small): 0px - Mobile phones
- **sm** (small): 600px - Tablets (portrait)
- **md** (medium): 900px - Tablets (landscape) / Small laptops
- **lg** (large): 1200px - Desktops
- **xl** (extra-large): 1536px - Large desktops

### Mobile-Optimized Typography

#### Responsive Heading Scales
```javascript
h1: {
  fontSize: "2.5rem",      // Desktop
  "@media (max-width:600px)": {
    fontSize: "2rem",       // Mobile (20% smaller)
  },
}
```

**All headings (h1-h6) scale down on mobile** for:
- Better readability on small screens
- Reduced scrolling
- Improved content density

#### Font Size Optimization
- **body1**: 1rem desktop → 0.95rem mobile
- **TextField/Select**: 16px minimum on mobile (prevents iOS zoom)

### Touch Target Optimization

#### Minimum Touch Targets (WCAG Compliance)
```javascript
MuiButton: {
  minHeight: "44px",  // Desktop
  minHeight: "48px",  // Mobile (easier tapping)
}

MuiIconButton: {
  padding: "12px",    // Larger on mobile
}
```
- **Accessibility:** 44px × 44px minimum (WCAG 2.1 Level AAA)
- **Mobile:** 48px recommended for easier tapping

### Spacing and Layout Adjustments

#### Container Padding
```javascript
MuiContainer: {
  paddingLeft: "16px",   // Desktop
  paddingRight: "16px",
  "@media (max-width:600px)": {
    paddingLeft: "12px",  // Mobile (tighter for more content)
    paddingRight: "12px",
  },
}
```

#### Card Content Padding
```javascript
MuiCardContent: {
  "@media (max-width:600px)": {
    padding: "12px",      // Reduced from 16px
    "&:last-child": {
      paddingBottom: "12px",
    },
  },
}
```

#### Border Radius
- Desktop: 8px
- Mobile: 4px (slightly less rounded)

### Mobile-Specific Component Optimizations

#### AppBar & Toolbar
```javascript
MuiAppBar: {
  "@media (max-width:600px)": {
    "& .MuiToolbar-root": {
      minHeight: "56px",      // Standard mobile height
      paddingLeft: "8px",     // Tighter spacing
      paddingRight: "8px",
    },
  },
}
```

#### Stepper (Wizard UI)
```javascript
MuiStepper: {
  "@media (max-width:600px)": {
    padding: "12px 4px",     // Compact on mobile
  },
}

MuiStepLabel: {
  "@media (max-width:600px)": {
    fontSize: "0.8rem",      // Smaller labels
  },
}
```

#### Dialog Modals
```javascript
MuiDialog: {
  paper: {
    "@media (max-width:600px)": {
      margin: "16px",                  // Screen margins
      maxHeight: "calc(100% - 32px)",  // Prevents overflow
      borderRadius: "8px",
    },
  },
}
```

#### Tables
```javascript
MuiTableCell: {
  "@media (max-width:600px)": {
    padding: "8px",      // Reduced padding
    fontSize: "0.85rem", // Smaller text
  },
}
```

#### Chips
```javascript
MuiChip: {
  "@media (max-width:600px)": {
    height: "28px",      // More compact
    fontSize: "0.8rem",
  },
}
```

## Best Practices Already Implemented

### 1. Grid Layout System
**Used throughout the app:**
```jsx
<Grid container spacing={3}>
  <Grid size={{ xs: 12, md: 6 }}>
    {/* Full width on mobile, half on desktop */}
  </Grid>
</Grid>
```

**Examples:**
- `routes/index.jsx`: Feature cards (xs: 12, md: 4)
- `routes/create/character.jsx`: D&D review (xs: 12, md: 4/8)
- `routes/stories.jsx`: Story cards (xs: 12, sm: 6, md: 4)

### 2. Responsive Utilities (sx prop)
```jsx
sx={{
  display: { xs: "none", md: "block" },  // Hide on mobile
  padding: { xs: 2, md: 3 },             // Responsive spacing
  maxHeight: { md: "calc(100vh - 250px)" }, // Desktop only
}}
```

**Common patterns:**
- **Hide on mobile:** `display: { xs: "none", md: "block" }`
- **Show on mobile:** `display: { xs: "block", md: "none" }`
- **Conditional sticky:** `position: { md: "sticky" }`

### 3. useMediaQuery Hook
**Example usage:**
```jsx
import useMediaQuery from '@mui/material/useMediaQuery';
import { useTheme } from '@mui/material/styles';

function MyComponent() {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  
  return (
    <Box>
      {isMobile ? <MobileView /> : <DesktopView />}
    </Box>
  );
}
```

## Mobile Testing Workflow

### 1. Local Device Testing
```bash
# Start dev server with network access
npm run dev

# Access from mobile device on same network
http://192.168.x.x:3000
```

### 2. Browser DevTools
- **Chrome DevTools:** Device toolbar (Ctrl+Shift+M)
- **Firefox:** Responsive Design Mode (Ctrl+Shift+M)
- Test breakpoints: 320px, 375px, 414px, 768px, 1024px

### 3. Real Device Testing
- iOS Safari (iPhone, iPad)
- Android Chrome (various screen sizes)
- Test touch interactions and scrolling

## Mobile-Responsive Navigation (Implemented)

### Hamburger Menu System
**Location:** `frontend/src/routes/__root.jsx`

#### Features
- **Responsive Breakpoint:** Switches at `md` (900px)
- **Desktop:** Full horizontal navigation bar
- **Mobile:** Hamburger menu (☰) with slide-out drawer
- **Swipeable:** Drawer can be swiped closed (MUI default)

#### Components Used
```jsx
// Responsive detection
const theme = useTheme();
const isMobile = useMediaQuery(theme.breakpoints.down("md"));

// Navigation items with icons
const navigationItems = [
  { label: "Home", path: "/", icon: <HomeIcon /> },
  { label: "Create", path: "/create", icon: <CreateIcon />, highlight: true },
  { label: "Stories", path: "/stories", icon: <AutoStoriesIcon /> },
  { label: "Characters", path: "/characters", icon: <PeopleIcon /> },
  { label: "Worlds", path: "/worlds", icon: <PublicIcon /> },
  { label: "Settings", path: "/settings", icon: <SettingsIcon /> },
];
```

#### Desktop View (≥900px)
- Logo + App title on left
- All 6 navigation buttons displayed horizontally
- Create button highlighted with gradient
- Adequate spacing between buttons

#### Mobile View (<900px)
- Logo + App title (responsive font size)
- Hamburger menu icon (☰) on right
- Drawer slides from right
- Full-height navigation list with icons
- 280px width (max 80vw for small screens)
- Auto-closes on navigation

#### Implementation Details
```jsx
{/* Desktop Navigation - Hidden on mobile */}
{!isMobile && (
  <Box sx={{ display: "flex", gap: 1 }}>
    {/* Buttons */}
  </Box>
)}

{/* Mobile Menu Button - Shown on mobile only */}
{isMobile && (
  <IconButton onClick={handleDrawerToggle}>
    <MenuIcon />
  </IconButton>
)}

{/* Mobile Drawer - Responsive display */}
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
  {/* Navigation List */}
</Drawer>
```

#### Benefits
- ✅ **No horizontal overflow** on mobile devices
- ✅ **Better UX:** Standard mobile pattern (hamburger menu)
- ✅ **Accessible:** Keyboard navigable, screen reader friendly
- ✅ **Performance:** Conditional rendering based on breakpoint
- ✅ **Touch-friendly:** Large touch targets in drawer
- ✅ **Visual feedback:** Icons + text for clarity

### Logo Responsive Sizing
```jsx
<Typography
  variant="h6"
  sx={{
    fontSize: { xs: "1rem", sm: "1.25rem" },
  }}
>
  StoryCraft
</Typography>
```

## Additional Mobile Enhancements

### Recommended Future Improvements

#### 1. Swipeable Components
```jsx
import { SwipeableDrawer } from '@mui/material';

<SwipeableDrawer
  anchor="left"
  open={drawerOpen}
  onClose={() => setDrawerOpen(false)}
  onOpen={() => setDrawerOpen(true)}
>
  {/* Navigation menu */}
</SwipeableDrawer>
```

#### 2. Virtual Scrolling for Long Lists
```jsx
import { FixedSizeList } from 'react-window';

// For character/story lists with 100+ items
<FixedSizeList
  height={400}
  itemCount={items.length}
  itemSize={80}
>
  {Row}
</FixedSizeList>
```

#### 3. Bottom Navigation (Mobile)
```jsx
import { BottomNavigation, BottomNavigationAction } from '@mui/material';

<BottomNavigation
  value={value}
  onChange={(event, newValue) => setValue(newValue)}
  showLabels
  sx={{ display: { xs: 'flex', md: 'none' } }}
>
  <BottomNavigationAction label="Stories" icon={<StoriesIcon />} />
  <BottomNavigationAction label="Characters" icon={<PeopleIcon />} />
</BottomNavigation>
```

#### 4. Pull-to-Refresh
```jsx
// Use react-simple-pull-to-refresh or custom implementation
import PullToRefresh from 'react-simple-pull-to-refresh';

<PullToRefresh onRefresh={handleRefresh}>
  <StoryList stories={stories} />
</PullToRefresh>
```

#### 5. Progressive Web App (PWA)
```json
// public/manifest.json
{
  "name": "StoryCraft",
  "short_name": "StoryCraft",
  "theme_color": "#9c27b0",
  "background_color": "#0a0a0a",
  "display": "standalone",
  "orientation": "portrait",
  "scope": "/",
  "start_url": "/"
}
```

## Performance Considerations

### 1. Image Optimization
```jsx
<img
  src={image}
  alt="Character portrait"
  loading="lazy"  // Lazy loading
  style={{
    width: "100%",
    height: "auto",
    maxWidth: "600px",
  }}
/>
```

### 2. Code Splitting (Already in place via TanStack Router)
```jsx
// Routes are automatically code-split
import { createFileRoute } from '@tanstack/react-router';
```

### 3. Debounced Search
```jsx
import { useDebounce } from 'use-debounce';

const [searchTerm, setSearchTerm] = useState('');
const [debouncedSearch] = useDebounce(searchTerm, 300);
```

## Accessibility Notes

### WCAG 2.1 Compliance
- ✅ Touch targets: 44px minimum
- ✅ Color contrast: MUI dark theme ensures compliance
- ✅ Font sizes: 16px minimum for inputs (no zoom)
- ✅ Keyboard navigation: All components focusable

### Screen Reader Support
- ✅ CssBaseline includes proper ARIA defaults
- ✅ MUI components have built-in ARIA labels
- Consider adding `aria-label` to icon buttons

## Testing Checklist

### Mobile Compatibility
- [ ] Portrait orientation (320px - 414px)
- [ ] Landscape orientation (568px - 896px)
- [ ] Tablet portrait (768px)
- [ ] Tablet landscape (1024px)
- [ ] Touch interactions (tap, swipe, pinch)
- [ ] Scrolling performance
- [ ] Form inputs (no zoom on focus)
- [ ] Navigation menu accessibility
- [ ] Image loading and display
- [ ] Dialog/modal behavior

### Cross-Browser
- [ ] iOS Safari (latest 2 versions)
- [ ] Android Chrome (latest 2 versions)
- [ ] Samsung Internet
- [ ] Firefox Mobile

## Resources

### MUI Documentation
- [Responsive UI Guide](https://mui.com/material-ui/guides/responsive-ui/)
- [Breakpoints](https://mui.com/material-ui/customization/breakpoints/)
- [useMediaQuery Hook](https://mui.com/material-ui/react-use-media-query/)
- [Grid System](https://mui.com/material-ui/react-grid/)

### Testing Tools
- [Chrome DevTools Device Mode](https://developer.chrome.com/docs/devtools/device-mode/)
- [BrowserStack](https://www.browserstack.com/) - Real device testing
- [Lighthouse](https://developers.google.com/web/tools/lighthouse) - Mobile performance

### Best Practices
- [Material Design Guidelines](https://m2.material.io/design/layout/responsive-layout-grid.html)
- [WCAG Touch Target Size](https://www.w3.org/WAI/WCAG21/Understanding/target-size.html)
- [Mobile Web Best Practices](https://web.dev/mobile/)

## Commit History
- ✅ Viewport meta tag (pre-existing)
- ✅ CssBaseline component (pre-existing)
- ✅ Vite --host configuration (commit: ebaac33)
- ✅ Comprehensive theme mobile optimizations (current)
