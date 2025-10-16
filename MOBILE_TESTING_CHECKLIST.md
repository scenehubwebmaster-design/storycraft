# Mobile Testing Checklist for StoryCraft

## Quick Test on Your Pixel 8 Pro

### How to Access
1. Ensure your Pixel 8 Pro and dev computer are on the same WiFi network
2. Start the dev server: `npm run dev` (in `frontend/` directory)
3. Note the Network URL (e.g., `http://192.168.x.x:3000`)
4. Open Chrome on your Pixel 8 Pro
5. Navigate to the Network URL

### Navigation Bar Test ✅
**Fixed Issue:** Horizontal overflow from 7 buttons

**What to Check:**
- [ ] No horizontal scrolling on navbar
- [ ] Hamburger menu (☰) icon visible in top right
- [ ] Tap hamburger to open drawer menu
- [ ] Drawer slides in from right
- [ ] All 6 menu items visible with icons
- [ ] Create button has gradient highlight
- [ ] Tap any menu item navigates correctly
- [ ] Drawer auto-closes after navigation
- [ ] Swipe drawer closed works
- [ ] Logo and "StoryCraft" text visible

**Expected Behavior:**
- Desktop (≥900px): All buttons horizontal
- Mobile (<900px): Hamburger menu only

### Page-by-Page Mobile Checks

#### 1. Home Page (`/`)
- [ ] Welcome heading readable (not too large)
- [ ] Feature cards stack vertically (full width)
- [ ] "Start Creating" button is large and tappable
- [ ] No horizontal overflow
- [ ] Footer text readable

#### 2. Create Page (`/create`)
- [ ] "Create with AI" heading scales properly
- [ ] 4 creation cards stack vertically
- [ ] Cards are full width on mobile
- [ ] Button icons and text visible
- [ ] No content cut off

#### 3. Character Creator (`/create/character`)
- [ ] Stepper labels readable (may be smaller)
- [ ] Form fields don't trigger zoom (16px font minimum)
- [ ] Dropdowns work properly
- [ ] Portrait settings icon button visible
- [ ] Generate button large enough to tap
- [ ] D&D character creator form scrolls properly
- [ ] Review page: Portrait and stats stack vertically
- [ ] Buttons at bottom (not obscured)

#### 4. Stories List (`/stories`)
- [ ] Search bar full width
- [ ] Story cards stack vertically
- [ ] Cards transition to 2 columns on larger mobile
- [ ] "Create Story" button tappable
- [ ] Card hover effects work on tap

#### 5. Characters List (`/characters`)
- [ ] Character cards stack vertically
- [ ] Portrait images display correctly
- [ ] "Create Character" button accessible
- [ ] Filter/search works

#### 6. Worlds List (`/worlds`)
- [ ] World cards stack vertically
- [ ] Content readable
- [ ] Images scale properly

#### 7. Settings Page (`/settings`)
- [ ] Form inputs don't zoom on focus
- [ ] API key fields full width
- [ ] Save buttons accessible
- [ ] Chips display properly

### Component-Specific Tests

#### Touch Targets
- [ ] All buttons at least 48px tall
- [ ] Icon buttons at least 48px × 48px
- [ ] No accidental taps on adjacent buttons
- [ ] Swipe gestures work (drawer, etc.)

#### Forms
- [ ] Text fields don't trigger zoom
- [ ] Dropdowns open properly
- [ ] Date pickers work
- [ ] Checkboxes/switches easy to tap
- [ ] Error messages visible

#### Dialogs/Modals
- [ ] Dialogs fit screen with margins
- [ ] Close button accessible
- [ ] Content scrolls if needed
- [ ] Backdrop tap closes modal

#### Cards
- [ ] Card content not cramped
- [ ] Images scale properly
- [ ] Action buttons visible
- [ ] Hover effects work on tap

#### Tables (if any)
- [ ] Columns readable
- [ ] Horizontal scroll if needed
- [ ] Cell content not cut off

### Orientation Tests

#### Portrait (Default)
- [ ] All pages display correctly
- [ ] Navigation works
- [ ] Content readable

#### Landscape
- [ ] Navigation switches to desktop view (if >900px)
- [ ] Or remains hamburger menu (if <900px)
- [ ] Content reflows properly
- [ ] Keyboard doesn't obscure inputs

### Performance Tests

#### Load Time
- [ ] Pages load in <3 seconds
- [ ] Images load progressively
- [ ] No layout shift during load

#### Scrolling
- [ ] Smooth scrolling
- [ ] No janky animations
- [ ] Sticky elements work (if any)

#### Interactions
- [ ] Buttons respond immediately
- [ ] No delay on taps
- [ ] Transitions smooth

### Browser-Specific Tests

#### Chrome (Primary)
- [ ] All features work
- [ ] Rendering correct

#### Firefox Mobile
- [ ] Navigation works
- [ ] Forms functional

#### Samsung Internet (if available)
- [ ] Basic functionality works

### Accessibility

#### Screen Reader (TalkBack)
- [ ] Enable TalkBack
- [ ] Navigate with gestures
- [ ] All buttons announced
- [ ] Form labels clear

#### Zoom
- [ ] Pinch to zoom works
- [ ] Text remains readable
- [ ] Layout doesn't break

### Network Conditions

#### 3G Speed
- [ ] Pages load (slower)
- [ ] Images lazy load
- [ ] Functionality works

#### Offline
- [ ] Appropriate error messages
- [ ] Cached content accessible

## Common Issues to Watch For

### ❌ Problems to Avoid
1. **Horizontal Overflow**
   - Content wider than screen
   - Need to scroll horizontally
   - Solution: Check all containers have `maxWidth` or responsive widths

2. **Text Too Small**
   - Body text < 14px
   - Buttons < 16px
   - Solution: Check theme typography settings

3. **Touch Targets Too Small**
   - Buttons < 44px × 44px
   - Icons < 44px × 44px
   - Solution: Check theme button settings

4. **Input Zoom on iOS**
   - Font size < 16px triggers zoom
   - Solution: Ensure TextField/Select use 16px minimum

5. **Layout Shifting**
   - Content jumps during load
   - Images without dimensions
   - Solution: Set explicit image sizes

6. **Modal Overlap**
   - Dialogs cut off by screen edge
   - Content not scrollable
   - Solution: Check Dialog theme settings

### ✅ What's Working
- Responsive navigation (hamburger menu)
- Typography scales down on mobile
- Touch targets optimized (48px)
- Forms don't trigger zoom (16px minimum)
- Containers have proper padding
- Cards stack vertically
- Grid system responsive

## Quick Fixes

### If Navigation Still Overflows
```jsx
// Check __root.jsx has:
const isMobile = useMediaQuery(theme.breakpoints.down("md"));
{!isMobile && <Box>/* Desktop buttons */</Box>}
{isMobile && <IconButton>/* Hamburger */</IconButton>}
```

### If Text Zooms on Input Focus
```jsx
// Check TextField has:
sx={{
  "& .MuiInputBase-root": {
    fontSize: "16px", // Prevents zoom
  },
}}
```

### If Buttons Too Small
```jsx
// Check theme has:
MuiButton: {
  styleOverrides: {
    root: {
      minHeight: "48px", // Mobile
    },
  },
}
```

## Testing Tools

### Browser DevTools
1. Open Chrome DevTools (F12)
2. Toggle device toolbar (Ctrl+Shift+M)
3. Select "Pixel 8 Pro" or custom dimensions
4. Test in portrait and landscape

### Responsive Testing Sizes
- **Pixel 8 Pro**: 393 × 873 (portrait), 873 × 393 (landscape)
- **iPhone 14 Pro**: 393 × 852
- **iPad Air**: 820 × 1180
- **Galaxy S21**: 360 × 800

### Network Throttling
1. DevTools → Network tab
2. Select "Fast 3G" or "Slow 3G"
3. Test page loads and interactions

## Report Issues

### How to Report
1. **Screenshot:** Show the issue
2. **Device:** Pixel 8 Pro, Chrome version
3. **URL:** Which page has the issue
4. **Steps:** How to reproduce
5. **Expected:** What should happen
6. **Actual:** What actually happens

### Example Report
```
Issue: Navigation buttons overflow on Pixel 8 Pro
Device: Pixel 8 Pro, Chrome 120
URL: http://192.168.1.100:3000/
Steps: Open homepage, observe navbar
Expected: Hamburger menu icon
Actual: All 7 buttons showing, need horizontal scroll
```

## Success Criteria

✅ **Navigation**: No horizontal overflow, hamburger menu works
✅ **Typography**: Readable at all sizes, scales properly
✅ **Touch Targets**: All buttons ≥44px, easy to tap
✅ **Forms**: No zoom on focus, proper spacing
✅ **Layout**: Content stacks vertically, no cut-off
✅ **Performance**: Smooth scrolling, fast interactions
✅ **Accessibility**: Screen reader friendly, keyboard navigable

## Next Steps

After testing, consider:
1. **Bottom Navigation**: For quick access to main sections
2. **Pull to Refresh**: For lists (stories, characters)
3. **Offline Support**: PWA capabilities
4. **Swipeable Cards**: For story/character browsing
5. **Virtual Scrolling**: For long lists (100+ items)

## Resources

- [MOBILE_STYLING_GUIDE.md](./MOBILE_STYLING_GUIDE.md) - Comprehensive guide
- [MUI Breakpoints](https://mui.com/material-ui/customization/breakpoints/)
- [WCAG Touch Targets](https://www.w3.org/WAI/WCAG21/Understanding/target-size.html)
- [Chrome DevTools Device Mode](https://developer.chrome.com/docs/devtools/device-mode/)
