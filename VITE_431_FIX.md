# Fix for 431 Request Header Fields Too Large

## Problem

Vite dev server returns **431 Request Header Fields Too Large** errors. This happens when:

- **Base64-encoded portrait images** in character data (MOST COMMON - see CHARACTER_PORTRAIT_431_FIX.md)
- **Browser cookies are too large** (auth tokens, session data)
- Request headers exceed Node.js default limit (16KB)
- Common after repeated dev sessions with auth tokens/cookies

**→ For portrait-related 431 errors, see `CHARACTER_PORTRAIT_431_FIX.md`**

## Quick Solution 1: Clear Browser Cookies (Fastest)

1. Open DevTools (F12)
2. Go to **Application** tab
3. Click **Storage** → **Clear site data**
4. Or manually delete cookies for `localhost:3000`

## Quick Solution 2: Use Incognito/Private Window

- Opens fresh browser session without cached cookies
- Good for testing

## Permanent Solution: Increased Header Limit (Already Applied)

We've increased Node.js header size limit from 16KB to 32KB:

```json
// frontend/package.json
"scripts": {
  "dev": "cross-env NODE_OPTIONS=--max-http-header-size=32768 vite --host"
}
```

**What this does:**

- `NODE_OPTIONS=--max-http-header-size=32768` increases limit to 32KB
- `cross-env` makes it work on Windows/Mac/Linux
- Already installed via `npm install --save-dev cross-env`

## If Problem Persists

### Option 1: Increase limit further

```json
"dev": "cross-env NODE_OPTIONS=--max-http-header-size=65536 vite --host"
```

(64KB limit)

### Option 2: Check cookie sizes

```javascript
// Run in browser console
console.log(
  document.cookie.split(";").map((c) => [c.split("=")[0].trim(), c.length])
);
```

### Option 3: Clear all application data

1. DevTools → Application tab
2. Storage → Clear site data
3. Check: Cookies, Local Storage, Session Storage, Cache Storage

## Technical Details

- Node.js default header limit: 16KB (16384 bytes)
- Security measure to prevent CVE-2018-12121 attacks
- Browsers can send 4KB+ cookies easily with auth tokens
- Vite runs on Node.js, inherits this limitation

## Character Portrait Specific Fix

If you're getting 431 errors when editing characters or viewing character lists:

**See `CHARACTER_PORTRAIT_431_FIX.md`** for the complete solution involving:

- Separate portrait loading endpoint
- Optional portrait exclusion parameters
- Two-step loading pattern in CreateCharacter.jsx

## References

- Character portrait fix: `CHARACTER_PORTRAIT_431_FIX.md`
- Vite docs: https://vite.dev/guide/troubleshooting.html#_431-request-header-fields-too-large
- Node.js CLI: https://nodejs.org/api/cli.html#--max-http-header-sizesize
