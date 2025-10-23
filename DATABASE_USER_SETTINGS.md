# Database-Backed User Settings Implementation

## Overview

Migrated from localStorage-based settings to database-backed persistence using PostgreSQL/SQLite. All user preferences (TTS, UI, RAG, LLM, accessibility) are now stored in the `user_settings` table and accessed via REST API.

## Database Schema

### user_settings Table

```sql
CREATE TABLE user_settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,  -- For future multi-user support

    -- TTS Settings
    tts_provider VARCHAR(50) DEFAULT 'kitten',       -- 'kitten' or 'openai'
    tts_voice VARCHAR(50) DEFAULT 'tara',           -- Voice ID
    tts_enabled BOOLEAN DEFAULT 1,                   -- Enable TTS
    tts_auto_play BOOLEAN DEFAULT 0,                 -- Auto-play responses
    tts_speed REAL DEFAULT 1.0,                      -- Speech speed (0.25-4.0)
    tts_model VARCHAR(50) DEFAULT 'standard',        -- 'standard' or 'hd'

    -- UI Preferences
    theme VARCHAR(20) DEFAULT 'dark',                -- 'light' or 'dark'
    compact_mode BOOLEAN DEFAULT 0,
    show_dice_rolls BOOLEAN DEFAULT 1,

    -- RAG Settings
    rag_enabled BOOLEAN DEFAULT 1,
    rag_top_k INTEGER DEFAULT 5,

    -- LLM Settings
    preferred_provider VARCHAR(50) DEFAULT 'groq',
    preferred_model VARCHAR(100),
    temperature REAL DEFAULT 0.7,
    max_tokens INTEGER DEFAULT 2000,

    -- Accessibility
    font_size VARCHAR(20) DEFAULT 'medium',
    high_contrast BOOLEAN DEFAULT 0,
    reduce_animations BOOLEAN DEFAULT 0,

    -- Notifications
    sound_enabled BOOLEAN DEFAULT 1,
    dice_sound_enabled BOOLEAN DEFAULT 1,
    combat_alerts BOOLEAN DEFAULT 1,

    -- Metadata
    settings_version INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## API Endpoints

### Base URL: `/api/settings/`

#### 1. GET /api/settings/

**Get user settings** (or create defaults if none exist)

**Query Parameters:**

- `user_id` (optional): User ID for multi-user mode

**Response:**

```json
{
  "id": 1,
  "user_id": null,
  "tts_provider": "kitten",
  "tts_voice": "tara",
  "tts_enabled": true,
  "tts_auto_play": false,
  "tts_speed": 1.0,
  "tts_model": "standard",
  "theme": "dark",
  "compact_mode": false,
  "show_dice_rolls": true,
  "rag_enabled": true,
  "rag_top_k": 5,
  "preferred_provider": "groq",
  "preferred_model": null,
  "temperature": 0.7,
  "max_tokens": 2000,
  "font_size": "medium",
  "high_contrast": false,
  "reduce_animations": false,
  "sound_enabled": true,
  "dice_sound_enabled": true,
  "combat_alerts": true,
  "settings_version": 1,
  "created_at": "2025-10-23T12:00:00",
  "updated_at": "2025-10-23T12:00:00"
}
```

#### 2. POST /api/settings/

**Create new user settings**

**Body:**

```json
{
  "user_id": null,
  "tts_provider": "openai",
  "tts_voice": "alloy",
  "tts_enabled": true
}
```

**Response:** `201 Created` + settings object

#### 3. PATCH /api/settings/

**Update user settings** (partial update)

**Query Parameters:**

- `user_id` (optional): User ID filter

**Body:**

```json
{
  "tts_provider": "openai",
  "tts_voice": "nova",
  "tts_enabled": true,
  "tts_auto_play": true
}
```

**Response:** `200 OK` + updated settings object

#### 4. PATCH /api/settings/{settings_id}

**Update specific settings by ID**

**Path Parameters:**

- `settings_id`: Settings record ID

**Body:** Same as PATCH /api/settings/

#### 5. DELETE /api/settings/{settings_id}

**Delete settings record**

**Response:** `204 No Content`

### Convenience Endpoints

#### GET /api/settings/tts

**Get only TTS settings**

**Response:**

```json
{
  "tts_provider": "kitten",
  "tts_voice": "tara",
  "tts_enabled": true,
  "tts_auto_play": false,
  "tts_speed": 1.0,
  "tts_model": "standard"
}
```

#### PATCH /api/settings/tts

**Update only TTS settings**

**Query Parameters:**

- `tts_provider` (optional)
- `tts_voice` (optional)
- `tts_enabled` (optional)
- `tts_auto_play` (optional)
- `tts_speed` (optional)
- `tts_model` (optional)

**Response:** Updated TTS settings object

## Frontend Integration

### CampaignManager.jsx

**Load Settings on Mount:**

```javascript
useEffect(() => {
  loadUserSettings();
}, []);

const loadUserSettings = async () => {
  try {
    const response = await fetch("http://localhost:8000/api/settings/");
    if (response.ok) {
      const settings = await response.json();
      setTtsProvider(settings.tts_provider || "kitten");
      setTtsVoice(settings.tts_voice || "tara");
      setTtsEnabled(settings.tts_enabled ?? true);
      setTtsAutoPlay(settings.tts_auto_play ?? false);
    }
  } catch (error) {
    console.error("Error loading settings:", error);
  }
};
```

**Save Settings on Update:**

```javascript
const saveTtsSettings = async () => {
  try {
    const response = await fetch("http://localhost:8000/api/settings/", {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        tts_provider: ttsProvider,
        tts_voice: ttsVoice,
        tts_enabled: ttsEnabled,
        tts_auto_play: ttsAutoPlay,
      }),
    });

    if (response.ok) {
      setTtsSettingsOpen(false);
    }
  } catch (error) {
    console.error("Error saving settings:", error);
  }
};
```

### TTSAudioPlayer.jsx Integration

**Load TTS Provider on Mount:**

```javascript
const [ttsProvider, setTtsProvider] = useState("kitten");
const [ttsVoice, setTtsVoice] = useState("tara");

useEffect(() => {
  fetch("http://localhost:8000/api/settings/tts")
    .then((res) => res.json())
    .then((settings) => {
      setTtsProvider(settings.tts_provider);
      setTtsVoice(settings.tts_voice);
    });
}, []);
```

**Route to Correct TTS Endpoint:**

```javascript
const fetchAudio = async () => {
  if (ttsProvider === "openai") {
    // OpenAI TTS endpoint
    const response = await axios.post("/api/audio/speak", {
      text: messageText,
      voice: ttsVoice,
      model: "standard",
      speed: 1.0,
      format: "mp3",
    });
  } else {
    // KittenTTS endpoint
    const response = await axios.post(
      `/api/chat/sessions/${sessionId}/messages/${messageId}/tts?voice=${ttsVoice}`
    );
  }
};
```

## Migration

**Run Migration:**

```bash
python backend/migrations/add_user_settings.py
```

**Rollback (if needed):**

```bash
python backend/migrations/add_user_settings.py --rollback
```

## File Changes

### New Files

1. **`backend/models.py`** - Added `UserSettings` model
2. **`backend/schemas.py`** - Added schemas:
   - `UserSettingsBase`
   - `UserSettingsCreate`
   - `UserSettingsUpdate`
   - `UserSettingsResponse`
3. **`backend/routers/user_settings.py`** - New router with 7 endpoints
4. **`backend/migrations/add_user_settings.py`** - Database migration script

### Modified Files

1. **`backend/main.py`**

   - Added `user_settings` import
   - Registered `/api/settings/` router

2. **`frontend/src/components/CampaignManager.jsx`**
   - Removed `localStorage` usage
   - Added `loadUserSettings()` function
   - Updated `saveTtsSettings()` to use API
   - Added `settingsLoaded` state for loading indicator

## Benefits

### ✅ Advantages Over localStorage

| Feature            | localStorage     | Database            |
| ------------------ | ---------------- | ------------------- |
| **Persistence**    | Browser-only     | Cross-device        |
| **Backup**         | Manual export    | Automatic           |
| **Multi-user**     | Not supported    | Ready for auth      |
| **API Access**     | Client-side only | Server + Client     |
| **Data Migration** | Complex          | Built-in versioning |
| **Analytics**      | Not available    | Can track usage     |
| **Defaults**       | Hard-coded       | Database-backed     |

### 🔒 Security

- Settings stored server-side (not exposed in client code)
- User-specific settings when auth is added
- Settings versioning for migrations

### 🚀 Future Extensions

1. **User Authentication**:

   - Link settings to authenticated users
   - Per-user customization

2. **Settings Profiles**:

   - Save multiple configurations
   - Quick-switch between profiles

3. **Admin Defaults**:

   - Set organization-wide defaults
   - Enforce policies (e.g., disable certain providers)

4. **Settings Export/Import**:

   - Backup user preferences
   - Share configurations

5. **Usage Analytics**:
   - Track which TTS providers are popular
   - Optimize defaults based on usage

## Testing

### Manual Testing

1. **Start backend**:

   ```bash
   python -m uvicorn backend.main:app --reload
   ```

2. **Test API in browser**:

   - Open http://localhost:8000/docs
   - Try GET `/api/settings/`
   - Try PATCH `/api/settings/` with TTS changes

3. **Test frontend**:
   - Open CampaignManager
   - Click "Configure" under Voice Narration
   - Change provider and voice
   - Click "Save Settings"
   - Refresh page - settings should persist

### API Testing

```bash
# Get settings
curl http://localhost:8000/api/settings/

# Update TTS settings
curl -X PATCH http://localhost:8000/api/settings/ \
  -H "Content-Type: application/json" \
  -d '{"tts_provider": "openai", "tts_voice": "nova"}'

# Get only TTS settings
curl http://localhost:8000/api/settings/tts
```

## Troubleshooting

### Settings Not Persisting

**Problem:** Settings reset after page refresh

**Solution:**

- Check browser console for API errors
- Verify backend is running
- Check database has `user_settings` table:
  ```bash
  sqlite3 storycraft.db "SELECT * FROM user_settings;"
  ```

### Cannot Save Settings

**Problem:** PATCH request returns 404

**Solution:**

- Ensure migration ran successfully
- Check at least one settings record exists:
  ```sql
  SELECT COUNT(*) FROM user_settings;
  ```
- If zero, run GET `/api/settings/` to create default record

### Multiple Settings Records

**Problem:** Multiple settings rows in single-user mode

**Solution:**

- Use settings_id to update specific record
- Or delete extra records and keep one

## Next Steps

1. **Update TTSAudioPlayer**: Read provider from API instead of localStorage
2. **Update SettingsDrawer**: Sync with database settings
3. **Create unified TTS endpoint**: `/api/tts/speak` that auto-routes based on user settings
4. **Add settings export/import**: Backup and restore user preferences
5. **Implement user authentication**: Link settings to user accounts

## Summary

✅ **Completed**:

- Created `user_settings` table
- Implemented full CRUD API
- Updated CampaignManager to use database
- Ran migration successfully

⏳ **Pending**:

- TTSAudioPlayer integration
- SettingsDrawer synchronization
- Unified TTS endpoint (optional)

🎉 **Result**: User preferences now persist in database, enabling cross-device sync, better backup, and future multi-user support!

---

**Implementation Date**: October 23, 2025
**Database**: SQLite (production-ready for PostgreSQL)
**API Version**: v1
