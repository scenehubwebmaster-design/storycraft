# Campaign Loading Debugging Guide

## Issue Summary

Campaigns exist in the database but are not appearing in the Campaign dropdown selector in DMChat.

## Database Verification ✅

Campaigns **do exist** in the database:

```sql
SELECT id, title, chat_session_id FROM campaigns ORDER BY updated_at DESC LIMIT 5
```

Results:

- Campaign ID 14: "Amber Sundering" → Session 44
- Campaign ID 13: "Amber Sundering" → Session 43
- Campaign ID 12: "Amber Sundering" → Session 42
- Campaign ID 11: "Arcanum of Twilight" → Session 41
- Campaign ID 10: "Amber Sundering" → Session 40

## API Endpoint Verification ✅

The campaigns API is working correctly:

```bash
http://localhost:8000/api/campaigns/?chat_session_id=44
```

Returns:

```json
[{
  "id": 14,
  "title": "Amber Sundering",
  "chat_session_id": 44,
  "current_level": 1,
  ...
}]
```

## Frontend Changes Made

### 1. Enhanced Logging in `LeftSettingsPanel.jsx`

Added console logging to track campaign loading:

- Logs when `selectedSession` is missing
- Logs the session ID being used
- Logs the API URL being called
- Logs response status and data
- Logs any errors

### 2. Added Debug Info Panel

Added a debug info box in the Campaign tab showing:

- Current session ID
- Number of campaigns loaded
- Loading state

## Testing Steps

1. **Start the backend**:

   ```cmd
   cd backend
   python -m uvicorn main:app --reload
   ```

2. **Start the frontend**:

   ```cmd
   cd frontend
   npm run dev
   ```

3. **Open DMChat and check**:
   - Open browser to `http://localhost:5173`
   - Navigate to DM Chat
   - Select or create a session
   - Click on the **Campaign** tab in the left settings panel
   - Check the debug info box (blue background)
   - Open browser DevTools Console (F12)
   - Look for log messages starting with "Loading campaigns for session:"

## Expected Behavior

When you open the Campaign tab, you should see:

1. Debug info showing the session ID
2. Console logs showing the fetch attempt
3. Campaign dropdown populated with available campaigns
4. If session 44 is selected, "Amber Sundering" should appear in the dropdown

## Common Issues to Check

### Issue 1: No Session Selected

- **Symptom**: Message says "Please select or create a session first"
- **Solution**: Select a session from the session list first

### Issue 2: API URL Mismatch

- **Check**: Console should show `http://localhost:8000/api/campaigns/...`
- **Fix**: If URL is different, check `.env` file for `VITE_API_URL`

### Issue 3: Backend Not Running

- **Symptom**: Console shows network error or CORS error
- **Solution**: Make sure backend is running on port 8000

### Issue 4: Wrong Session

- **Symptom**: Debug shows session ID but 0 campaigns loaded
- **Solution**: That session might not have any campaigns yet - try creating one

## Manual API Test

You can test the API directly in browser:

```
http://localhost:8000/api/campaigns/?chat_session_id=44
```

This should return a JSON array with at least one campaign.

## Next Steps After Debugging

Once you see the campaigns loading in console but not appearing in dropdown:

1. Check if `campaigns` state is being set correctly
2. Verify the dropdown is rendering the items
3. Check for any React rendering errors in console

## Files Modified

1. `frontend/src/components/game/LeftSettingsPanel.jsx`:
   - Enhanced `loadCampaigns()` with detailed logging
   - Added debug info panel in Campaign tab

## Rollback Instructions

If you want to remove the debug info panel, remove lines in `LeftSettingsPanel.jsx`:

- The debug info Box component (lines ~527-538)
