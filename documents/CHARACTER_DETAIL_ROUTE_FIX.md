# Character Detail Page Route Fix

## Issue

When clicking "View Details" on a character, the URL would change to `/characters/3` but the page would still show the characters list instead of the character detail page.

## Root Cause

The `/characters` route file (`frontend/src/routes/characters.jsx`) was rendering the characters list component directly without an `<Outlet />` component.

In TanStack Router, when a route has child routes (like `/characters/$characterId`), the parent route needs to render an `<Outlet />` component to display the child route's content. Without this, the parent component keeps rendering even when navigating to child routes.

## Solution

Modified `frontend/src/routes/characters.jsx` to:

1. Import `Outlet` and `useMatches` from TanStack Router
2. Check if a child route is active using `useMatches()`
3. Render `<Outlet />` when a child route is active
4. Render the characters list when no child route is active

### Code Changes

```javascript
// Added imports
import {
  createFileRoute,
  Link,
  Outlet,
  useMatches,
} from "@tanstack/react-router";

function CharactersComponent() {
  // Check if child route is active
  const matches = useMatches();
  const isChildRouteActive = matches.length > 2; // Root + /characters + child route

  // ... state declarations ...

  // If a child route is active (like character detail), render the outlet
  if (isChildRouteActive) {
    return <Outlet />;
  }

  // Otherwise render the characters list
  // ... rest of component ...
}
```

## How It Works

- **`useMatches()`** returns an array of all matched routes in the current location
- When at `/characters`, matches contains: `[rootRoute, charactersRoute]` (length = 2)
- When at `/characters/3`, matches contains: `[rootRoute, charactersRoute, characterIdRoute]` (length = 3)
- When length > 2, we know a child route is active and should render `<Outlet />`
- The `<Outlet />` component renders the child route's component (CharacterDetailComponent)

## Testing

1. **Navigate to characters list**:
   - Go to http://localhost:3000/characters
   - ✅ Should show the list of all characters

2. **View character details**:
   - Click "View Details" on any character
   - ✅ URL changes to `/characters/{id}`
   - ✅ Character detail page displays
   - ✅ Shows full character profile, portrait, edit/delete buttons

3. **Navigate back**:
   - Click "Back to Characters" button
   - ✅ Returns to characters list

4. **Direct URL access**:
   - Navigate directly to http://localhost:3000/characters/3
   - ✅ Character detail page loads correctly

## Related Routes Using Same Pattern

The same outlet pattern is used for:

- `/stories` → `/stories/$storyId`
- `/worlds` → `/worlds/$worldId`
- `/create` → `/create/character`, `/create/world`, etc.

If similar issues occur with these routes, apply the same fix.

## Files Modified

- `frontend/src/routes/characters.jsx` - Added outlet logic for child routes
- `frontend/src/routes/characters/$characterId.jsx` - Fixed Edit button path (from `/character` to `/create/character`)
