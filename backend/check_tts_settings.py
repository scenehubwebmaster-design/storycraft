"""Quick script to check TTS settings"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import from the backend package
import database
import models

SessionLocal = database.SessionLocal
UserSettings = models.UserSettings

db = SessionLocal()
settings = db.query(UserSettings).first()

if settings:
    print(f"TTS Provider: {settings.tts_provider}")
    print(f"TTS Voice: {settings.tts_voice}")
    print(f"TTS Model: {settings.tts_model}")
    print(f"TTS Speed: {settings.tts_speed}")
    print(f"TTS Enabled: {settings.tts_enabled}")
else:
    print("No settings found!")

db.close()
