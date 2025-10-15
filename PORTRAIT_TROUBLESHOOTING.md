# Portrait Generation Troubleshooting Guide

## "Generate Portrait" Button is Greyed Out

The "Generate Portrait" button will be disabled (greyed out) if any of these conditions are **NOT** met:

### ✅ Requirements Checklist

1. **Character content must be generated**
   - Status: You must be on Step 2 (Review & Save)
   - The character description must be visible
   - If you see this message: *"Character content is required for portrait generation"*
   - **Solution**: Go back to Step 1, select traits, and click "Generate with AI"

2. **Character name must be entered**
   - Status: The "Character Name" text field must have a value
   - If you see this message: *"Enter a character name above to enable portrait generation"*
   - **Solution**: Type a name in the "Character Name" field above the portrait section

3. **Not currently generating**
   - Status: Portrait generation must not be in progress
   - If you see: "Generating..." on the button
   - **Solution**: Wait for the current generation to complete

## Step-by-Step Fix

### If Button is Greyed Out:

1. **Check for info message** below the button:
   - Blue info alert will tell you exactly what's missing

2. **Character Name Missing?**
   ```
   ┌─────────────────────────────────┐
   │ Character Name: [___________] ← Type name here!
   └─────────────────────────────────┘
   ```

3. **Character Content Missing?**
   - You're on Step 2 but no character was generated
   - **Solution**: 
     - Click "Back" button
     - Return to Step 0 or 1
     - Click "Generate with AI" to create character
     - Then return to Step 2

## Visual Guide

### ❌ Button Disabled (Greyed Out)

```
┌──────────────────────────────────────┐
│ Character Portrait                    │
│ ⚪ Generate Portrait (greyed out)    │
│                                       │
│ ℹ️ Enter a character name above to   │
│   enable portrait generation          │
└──────────────────────────────────────┘
```

**Why?** Character name field is empty

### ❌ Button Disabled (Greyed Out)

```
┌──────────────────────────────────────┐
│ Character Portrait                    │
│ ⚪ Generate Portrait (greyed out)    │
│                                       │
│ ℹ️ Character content is required for │
│   portrait generation                 │
└──────────────────────────────────────┘
```

**Why?** No character content was generated (you skipped generation)

### ✅ Button Enabled (Active)

```
┌──────────────────────────────────────┐
│ Character Name: Ragnar Blackwood      │
│                                       │
│ Character Portrait                    │
│ 📷 Generate Portrait (clickable!)    │
│                                       │
│ [Character content displayed below]   │
└──────────────────────────────────────┘
```

**Why?** All requirements met! ✅

## Common Scenarios

### Scenario 1: "I just opened the page"

- **Current State**: Step 0 (Select Traits)
- **Button Status**: Not visible yet (you're on Step 0)
- **Solution**: Follow the normal workflow:
  1. Select traits (Step 0)
  2. Click "Next"
  3. Click "Generate with AI" (Step 1)
  4. Wait for generation
  5. You'll move to Step 2 automatically
  6. Enter character name
  7. Button becomes enabled ✅

### Scenario 2: "I'm on Step 2 but button is greyed out"

- **Current State**: Step 2 (Review & Save)
- **Button Status**: Disabled
- **Check**:
  - Is there character content visible? (text below the portrait section)
  - Is the character name field filled?
- **Solution**:
  - If no content: Click "Back", then "Generate with AI"
  - If no name: Type a name in the field

### Scenario 3: "I entered a name but it's still greyed out"

- **Possible Causes**:
  1. Character content is missing
  2. You only typed spaces (name.trim() is empty)
  3. Portrait is currently generating
- **Solution**:
  - Check for blue info message below button
  - Make sure character content is visible
  - Try typing a real name (not just spaces)

### Scenario 4: "Button was working, now it's not"

- **Possible Causes**:
  1. Character name field was cleared
  2. Page was refreshed (lost generated content)
  3. Navigated away and back (lost state)
- **Solution**:
  - Re-enter character name
  - If content is lost, start over from Step 0
  - Make sure to save your character before navigating away

## Quick Fix Commands

### Check Current State (Browser Console)

Open browser console (F12) and run:

```javascript
// Check if character name is set
console.log("Character Name:", document.querySelector('input[placeholder="Enter a name for this character"]')?.value);

// Check if you're on Step 2
console.log("Current Step:", document.querySelector('.MuiStepLabel-label.Mui-active')?.textContent);

// Check if generated content exists
console.log("Has Content:", !!document.querySelector('[class*="ReactMarkdown"]'));
```

## Backend Checks

If the button is enabled but portrait generation fails:

### 1. Check Backend is Running

```bash
# Terminal 1: Backend should be running
cd backend
python main.py
# Should show: "Uvicorn running on http://0.0.0.0:8000"
```

### 2. Check Google API Key

```bash
# Check .env file
cat backend/.env | grep GOOGLE_API_KEY
# Should show: GOOGLE_API_KEY=your_key_here
```

### 3. Check Dependencies

```bash
cd backend
pip list | grep -E "google-genai|pillow"
# Should show both packages installed
```

### 4. Test API Directly

```bash
curl -X POST http://localhost:8000/api/generate/character/generate-portrait \
  -H "Content-Type: application/json" \
  -d '{
    "character_name": "Test",
    "appearance_text": "A tall warrior with dark hair",
    "model": "imagen-4.0-fast-generate-001",
    "aspect_ratio": "3:4"
  }'
```

## Still Having Issues?

### Debug Steps:

1. **Clear Browser Cache**
   - Ctrl + F5 (force refresh)
   - Or clear cache in browser settings

2. **Check Browser Console**
   - F12 → Console tab
   - Look for JavaScript errors in red

3. **Check Network Tab**
   - F12 → Network tab
   - Try clicking "Generate Portrait"
   - Look for failed requests

4. **Restart Everything**
   ```bash
   # Stop backend (Ctrl+C)
   # Stop frontend (Ctrl+C)
   
   # Start backend
   cd backend && python main.py
   
   # Start frontend (new terminal)
   cd frontend && npm run dev
   ```

5. **Check Logs**
   - Backend terminal: Look for errors
   - Frontend terminal: Look for build errors
   - Browser console: Look for runtime errors

## Error Messages Reference

| Error Message | Meaning | Solution |
|---------------|---------|----------|
| "Enter a character name above..." | Name field is empty | Type a name |
| "Character content is required..." | No generated content | Generate character first |
| "Please enter a character name first" | Tried to generate without name | Enter name in field |
| "Failed to generate portrait..." | Backend/API error | Check backend logs |
| "Make sure Google API key is configured" | Missing/invalid API key | Check .env file |

## Tips for Success

### ✅ Do This:

1. Follow the steps in order (0 → 1 → 2)
2. Wait for character generation to complete
3. Enter a meaningful character name
4. Check for info messages below the button
5. Make sure backend is running

### ❌ Don't Do This:

1. Skip character generation step
2. Leave character name field empty
3. Use only spaces in the name field
4. Click button repeatedly while generating
5. Navigate away before saving

## Need More Help?

- **Full Documentation**: [CHARACTER_PORTRAIT_GENERATION.md](./CHARACTER_PORTRAIT_GENERATION.md)
- **Quick Start Guide**: [PORTRAIT_QUICK_START.md](./PORTRAIT_QUICK_START.md)
- **Backend Setup**: Check "Setup (One-time)" in PORTRAIT_QUICK_START.md
- **API Reference**: See CHARACTER_PORTRAIT_GENERATION.md → API Reference

## Summary

**The button is greyed out for a good reason!** It prevents errors by ensuring:

1. ✅ You have character content to extract appearance from
2. ✅ You have a character name to use in the prompt
3. ✅ The system isn't already generating a portrait

**Always check the blue info message below the button** - it tells you exactly what's needed!
