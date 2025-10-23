"""
Fix UserSettings defaults - populate None values with proper defaults
"""
import sys
import os

# Add parent directory to path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
parent_dir = os.path.dirname(backend_dir)
sys.path.insert(0, parent_dir)

from backend.database import SessionLocal
from backend.models import UserSettings

def fix_settings_defaults():
    """Update existing UserSettings records with proper default values"""
    db = SessionLocal()
    
    try:
        settings = db.query(UserSettings).all()
        
        print(f"Found {len(settings)} settings records to update")
        
        for s in settings:
            updated = False
            
            # TTS Settings
            if s.tts_provider is None:
                s.tts_provider = "kitten"
                updated = True
            if s.tts_voice is None:
                s.tts_voice = "tara" if s.tts_provider == "kitten" else "nova"
                updated = True
            if s.tts_enabled is None:
                s.tts_enabled = True
                updated = True
            if s.tts_auto_play is None:
                s.tts_auto_play = False
                updated = True
            if s.tts_speed is None:
                s.tts_speed = 1.0
                updated = True
            if s.tts_model is None:
                s.tts_model = "standard"
                updated = True
            
            # UI Preferences
            if s.theme is None:
                s.theme = "dark"
                updated = True
            if s.compact_mode is None:
                s.compact_mode = False
                updated = True
            if s.show_dice_rolls is None:
                s.show_dice_rolls = True
                updated = True
            
            # RAG Settings
            if s.rag_enabled is None:
                s.rag_enabled = True
                updated = True
            if s.rag_top_k is None:
                s.rag_top_k = 5
                updated = True
            
            # LLM Settings
            if s.preferred_provider is None:
                s.preferred_provider = "groq"
                updated = True
            if s.temperature is None:
                s.temperature = 0.7
                updated = True
            if s.max_tokens is None:
                s.max_tokens = 2000
                updated = True
            
            # Accessibility
            if s.font_size is None:
                s.font_size = "medium"
                updated = True
            if s.high_contrast is None:
                s.high_contrast = False
                updated = True
            if s.reduce_animations is None:
                s.reduce_animations = False
                updated = True
            
            # Notifications
            if s.sound_enabled is None:
                s.sound_enabled = True
                updated = True
            if s.dice_sound_enabled is None:
                s.dice_sound_enabled = True
                updated = True
            if s.combat_alerts is None:
                s.combat_alerts = True
                updated = True
            
            # Metadata
            if s.settings_version is None:
                s.settings_version = 1
                updated = True
            
            # Fix timestamps if None
            from datetime import datetime
            if s.created_at is None:
                s.created_at = datetime.utcnow()
                updated = True
            if s.updated_at is None:
                s.updated_at = datetime.utcnow()
                updated = True
            
            if updated:
                print(f"  Updated settings ID {s.id}")
        
        db.commit()
        print("\n✅ Settings defaults updated successfully!")
        
        # Verify
        for s in settings:
            db.refresh(s)
            print(f"\nSettings ID {s.id}:")
            print(f"  TTS: {s.tts_provider}/{s.tts_voice} (speed: {s.tts_speed})")
            print(f"  UI: theme={s.theme}, compact={s.compact_mode}")
            print(f"  RAG: enabled={s.rag_enabled}, top_k={s.rag_top_k}")
            print(f"  LLM: provider={s.preferred_provider}, temp={s.temperature}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    fix_settings_defaults()
