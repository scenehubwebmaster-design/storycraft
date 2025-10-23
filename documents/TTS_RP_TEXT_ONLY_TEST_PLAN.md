# Manual Test Plan: RP Text Only Feature

## Test Environment

- **Frontend:** React dev server (http://localhost:3000)
- **Backend:** FastAPI server (http://localhost:8000)
- **Browser:** Any modern browser (Chrome, Firefox, Edge)

## Pre-Test Setup

1. Start backend server:

   ```bash
   cd e:\storycraft\backend
   python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

2. Start frontend server:

   ```bash
   cd e:\storycraft\frontend
   npm run dev
   ```

3. Open browser to http://localhost:3000
4. Navigate to a chat session with TTS enabled

## Test Cases

### Test 1: Toggle Visibility

**Steps:**

1. Open a chat session
2. Enable TTS (Voice Narration checkbox)
3. Look for voice selector dropdown

**Expected Result:**

- Voice selector dropdown is visible
- Below it, there's a checkbox labeled "RP Text Only (skip mechanics)"

**Pass Criteria:** ✓ Checkbox is visible and properly labeled

---

### Test 2: Default State

**Steps:**

1. Observe the initial state of the RP Text Only checkbox

**Expected Result:**

- Checkbox is unchecked by default

**Pass Criteria:** ✓ Checkbox starts unchecked

---

### Test 3: Generate Audio Without Filter

**Steps:**

1. Ensure RP Text Only checkbox is **unchecked**
2. Send a message that triggers a DM response with a spell (e.g., "tell me about Lightning Bolt spell")
3. Wait for TTS to generate
4. Listen to the audio

**Expected Result:**

- Audio narrates the complete spell description
- Includes: Level & School, Casting Time, Range, Components, Duration, AND flavor text

**Pass Criteria:** ✓ Complete text is narrated (verify by checking audio length ~30-40 seconds for Lightning Bolt)

---

### Test 4: Generate Audio With Filter

**Steps:**

1. **Check** the RP Text Only checkbox
2. Send the same message again (or click to regenerate audio)
3. Wait for TTS to generate
4. Listen to the audio

**Expected Result:**

- Audio only narrates the descriptive paragraph
- Skips: Level & School, Casting Time, Range, Components, Duration
- Narrates: "A stroke of lightning forming a line 100 feet long..."

**Pass Criteria:** ✓ Audio is significantly shorter (~10-15 seconds) and only contains flavor text

---

### Test 5: Toggle Changes Audio

**Steps:**

1. Generate audio with filter **OFF** (full text)
2. Note the audio player shows audio is loaded
3. **Check** the RP Text Only checkbox (turn filter ON)
4. Observe behavior

**Expected Result:**

- Audio player should automatically regenerate
- Progress bar resets to 0
- New audio loads with filtered text
- Audio is shorter than previous version

**Pass Criteria:** ✓ Toggling the checkbox triggers automatic regeneration

---

### Test 6: Voice + Filter Combination

**Steps:**

1. Select voice "leo" (deep male voice)
2. Check RP Text Only checkbox
3. Generate audio for Lightning Bolt
4. Uncheck RP Text Only
5. Generate audio again
6. Compare audio

**Expected Result:**

- Both audio files use "leo" voice
- First (filtered) is shorter and skips mechanics
- Second (unfiltered) is longer and includes all text

**Pass Criteria:** ✓ Voice selection and filter work independently

---

### Test 7: API Parameter Check

**Steps:**

1. Open browser DevTools (F12)
2. Go to Network tab
3. Generate audio with filter **OFF**
4. Check the network request

**Expected Result:**

- Request URL includes `flavor_text_only=false`
- Example: `/api/chat/sessions/{id}/messages/{id}/tts?voice=tara&flavor_text_only=false`

**Pass Criteria:** ✓ API parameter is correctly set to false

**Steps (continued):** 5. Check RP Text Only checkbox 6. Generate audio again 7. Check the new network request

**Expected Result:**

- Request URL includes `flavor_text_only=true`

**Pass Criteria:** ✓ API parameter is correctly set to true

---

### Test 8: Different Content Types

**Steps:**

1. Test with different message types:
   - Spell description (Lightning Bolt)
   - Monster description (Adult Red Dragon)
   - Pure narrative (DM describing a scene)
2. For each, generate audio with filter ON and OFF

**Expected Result:**

- **Spells:** Filter removes stats, keeps description
- **Monsters:** Filter removes stat blocks, keeps narrative
- **Pure narrative:** Filter changes nothing (all text is kept)

**Pass Criteria:** ✓ Filter works correctly for all content types

---

### Test 9: Compact Mode

**Steps:**

1. Find a message with compact TTS player (smaller controls)
2. Check if RP Text Only toggle is present

**Expected Result:**

- Toggle should NOT be visible in compact mode
- Only visible when `showVoiceSelector={true}` (full mode)

**Pass Criteria:** ✓ Toggle is only visible in full mode

---

### Test 10: Error Handling

**Steps:**

1. Stop the backend server
2. Try to generate audio with filter ON
3. Observe error message

**Expected Result:**

- Error message displays (same as before)
- No JavaScript errors in console
- Feature doesn't break when backend is unavailable

**Pass Criteria:** ✓ Graceful error handling

---

## Quick Verification Checklist

Use this checklist for rapid verification:

- [ ] RP Text Only checkbox visible below voice selector
- [ ] Checkbox unchecked by default
- [ ] Checking checkbox generates filtered audio
- [ ] Unchecking checkbox generates full audio
- [ ] Toggle works with all 8 voices
- [ ] API receives correct `flavor_text_only` parameter
- [ ] Lightning Bolt filtered: ~10-15 seconds, unfiltered: ~30-40 seconds
- [ ] Pure narrative unchanged with filter ON
- [ ] No console errors when toggling

## Expected Test Duration

- Full test suite: ~15 minutes
- Quick verification: ~5 minutes

## Reporting Issues

If any test fails, report:

1. Which test case failed
2. Browser and version
3. Console errors (if any)
4. Network request details (from DevTools)
5. Audio behavior (length, content)

## Success Criteria

**All tests must pass for feature to be considered complete.**

Minimum requirements:

- Checkbox renders correctly
- API parameter sent correctly
- Audio changes based on toggle state
- No JavaScript errors

---

**Test Plan Version:** 1.0

**Created:** 2025-01-23

**Last Updated:** 2025-01-23
