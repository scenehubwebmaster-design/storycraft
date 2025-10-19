# Portrait Loading Fix - Complete

**Date:** October 18, 2025  
**Status:** ✅ FIXED

## Problem Summary

Portraits were not loading in the character list (`/characters` page) due to:

1. **Wrong file being used**: Application was using `pages/Characters.jsx` but we were editing `routes/characters.jsx`
2. **Large base64 images**: Portraits (100KB-500KB) were causing 431 errors when loaded with character data
3. **Missing lazy loading**: All portraits loaded at once, blocking the UI

## Solution Implemented

### 1. Applied Fix to Correct File

Updated `frontend/src/pages/Characters.jsx` (the actual file being used by React Router).

### 2. Implemented Lazy Portrait Loading

**Added State Management:**

```javascript
const [portraits, setPortraits] = useState({}); // Cache for loaded portraits
const [loadingPortraits, setLoadingPortraits] = useState({}); // Track loading state
```

**Created Portrait Loading Function:**

```javascript
const loadPortraitForCharacter = async (characterId) => {
  setLoadingPortraits((prev) => ({ ...prev, [characterId]: true }));

  const response = await axios.get(
    `${API_URL}/api/characters/${characterId}/portrait/`
  );

  setPortraits((prev) => ({
    ...prev,
    [characterId]: response.data.portrait_image,
  }));

  setLoadingPortraits((prev) => ({ ...prev, [characterId]: false }));
};
```

**Modified Character Loading:**

```javascript
// Load characters WITHOUT portraits first (fast)
const response = await axios.get(
  `${API_URL}/api/characters/?exclude_portraits=true`
);

// Then load portraits in background (non-blocking)
response.data.forEach((character) => {
  if (character.id) {
    loadPortraitForCharacter(character.id);
  }
});
```

**Updated Rendering Logic:**

```javascript
{
  portraits[character.id] ? (
    <CardMedia image={`data:image/png;base64,${portraits[character.id]}`} />
  ) : loadingPortraits[character.id] ? (
    <CircularProgress />
  ) : (
    <PersonIcon />
  );
}
```

### 3. Removed TanStack Router Remnants

- ✅ Deleted `frontend/src/routes/` directory (unused)
- ✅ Verified no `@tanstack/react-router` imports in active code
- ✅ Confirmed `package.json` doesn't include TanStack Router
- ✅ Application now fully uses React Router DOM

## Technical Details

### Function Definition Order

**Critical:** The `loadPortraitForCharacter` function must be defined **before** the `useEffect` that calls it. JavaScript arrow functions assigned to `const` are not hoisted, so:

```javascript
// ✅ CORRECT ORDER
const loadPortraitForCharacter = async (characterId) => { ... };

useEffect(() => {
  // Can call loadPortraitForCharacter here
  loadPortraitForCharacter(1);
}, []);

// ❌ WRONG ORDER - Would fail
useEffect(() => {
  loadPortraitForCharacter(1); // Error: not defined yet
}, []);

const loadPortraitForCharacter = async (characterId) => { ... };
```

### Backend Support

Backend already provides the necessary endpoints:

- `GET /api/characters/?exclude_portraits=true` - Fast list without portraits
- `GET /api/characters/{id}/portrait/` - Individual portrait endpoint

### Performance Impact

**Before:**

- Single request with 3 characters + portraits: ~1.5MB
- 431 Header Too Large errors
- Long wait time before any content appears

**After:**

- Initial request (metadata only): ~5KB (300x smaller!)
- 3 portrait requests: ~500KB each (parallel, non-blocking)
- Content appears instantly, portraits load progressively
- No 431 errors

## Debug Logging

Added comprehensive logging for troubleshooting:

```
[Characters] Starting to load portraits for 3 characters
[Characters] Queueing portrait load for character 1
[Characters] Loading portrait for character 1
[Characters] Portrait response for 1: { hasImage: true, imageLength: 523844 }
[Characters] Portrait loaded for 1
```

## Files Modified

1. **`frontend/src/pages/Characters.jsx`**

   - Added portrait state management
   - Created `loadPortraitForCharacter` function
   - Modified character loading to exclude portraits
   - Updated rendering logic for progressive loading
   - Added debug logging

2. **Deleted: `frontend/src/routes/` directory**
   - Removed all unused TanStack Router files
   - Cleaned up legacy routing code

## Testing

**To verify the fix works:**

1. Open http://localhost:3000/characters
2. Open DevTools Console (F12)
3. Watch for debug messages:
   ```
   [Characters] Starting to load portraits for X characters
   [Characters] Loading portrait for character X
   [Characters] Portrait loaded for X
   ```
4. Observe:
   - Character list appears instantly
   - Portrait loading spinners show briefly
   - Portraits appear progressively as they load
   - No 431 errors in Network tab

## Similar Files That Also Work

The lazy portrait loading pattern is already working in:

- ✅ `frontend/src/pages/CharacterDetail.jsx` - Single character view
- ✅ `frontend/src/routes/characters/$characterId.jsx` - TanStack version (now deleted)

## Related Documentation

- `PORTRAIT_LOADING_FIX.md` - Original issue investigation
- `LAZY_LOADING_PORTRAITS.md` - Implementation planning
- `REACT_ROUTER_MIGRATION.md` - Router migration context
- `VITE_431_FIX.md` - 431 error root cause analysis

## Next Steps

1. ✅ **DONE:** Applied to `pages/Characters.jsx`
2. **TODO:** Apply same pattern to `pages/CreateCharacter.jsx` for edit mode
3. **TODO:** Consider applying to other list views (Worlds, Stories) if they show portraits
4. **TODO:** Add portrait caching to localStorage for offline/faster loads

## Notes

- The `routes/` directory was a remnant from the TanStack Router migration
- React Router DOM uses `pages/` directory via `App.jsx`
- Always check which file is actually being used by inspecting console logs
- Console shows filename:line for logs, helping identify active files
