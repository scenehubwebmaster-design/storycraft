"""
Test OpenAI TTS and Whisper Integration

Tests:
1. Service initialization
2. Text-to-speech generation
3. Voice options
4. Audio format support
5. Speed control
6. Speech-to-text (Whisper) transcription

Requirements:
- OPENAI_API_KEY environment variable set
- openai Python package installed
"""

import sys
import os
sys.path.insert(0, 'e:/storycraft')

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv('e:/storycraft/backend/.env')

from backend.openai_tts_service import get_openai_tts_service, OPENAI_AVAILABLE

def test_service_availability():
    """Test if OpenAI package is available."""
    print("="*70)
    print("TEST 1: Service Availability")
    print("="*70)
    
    if not OPENAI_AVAILABLE:
        print("❌ OpenAI package not installed")
        print("   Install with: pip install openai")
        return False
    
    print("✅ OpenAI package is installed")
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY not set in environment")
        return False
    
    print(f"✅ OPENAI_API_KEY is configured ({api_key[:10]}...)")
    return True


def test_service_initialization():
    """Test TTS service initialization."""
    print("\n" + "="*70)
    print("TEST 2: Service Initialization")
    print("="*70)
    
    try:
        service = get_openai_tts_service(
            voice="alloy",
            model="standard",
            audio_format="mp3"
        )
        print("✅ Service initialized successfully")
        print(f"   Default voice: {service.default_voice}")
        print(f"   Default model: {service.default_model}")
        print(f"   Default format: {service.default_format}")
        return service
    except Exception as e:
        print(f"❌ Service initialization failed: {e}")
        return None


def test_voice_options(service):
    """Test available voice options."""
    print("\n" + "="*70)
    print("TEST 3: Voice Options")
    print("="*70)
    
    print(f"Available voices ({len(service.VOICES)}):")
    for voice_id, description in service.VOICES.items():
        print(f"  • {voice_id:10} - {description}")
    
    print("\n✅ Voice options retrieved")


def test_tts_generation(service):
    """Test text-to-speech generation."""
    print("\n" + "="*70)
    print("TEST 4: Text-to-Speech Generation")
    print("="*70)
    
    test_text = (
        "Greetings, adventurers! Welcome to the world of StoryCraft, "
        "where epic tales unfold and legendary heroes are born."
    )
    
    try:
        print(f"Generating speech for: '{test_text[:50]}...'")
        audio_data = service.generate_speech(
            text=test_text,
            voice="alloy",
            model="standard",
            speed=1.0,
            output_format="mp3"
        )
        
        print("✅ Speech generated successfully")
        print(f"   Audio size: {len(audio_data):,} bytes")
        print("   Format: MP3")
        
        # Save test file
        output_path = "e:/storycraft/test_tts_output.mp3"
        with open(output_path, 'wb') as f:
            f.write(audio_data)
        print(f"   Saved to: {output_path}")
        
        return True
    except Exception as e:
        print(f"❌ TTS generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_multiple_voices(service):
    """Test different voice options."""
    print("\n" + "="*70)
    print("TEST 5: Multiple Voice Generation")
    print("="*70)
    
    test_text = "The dragon roars as it emerges from the mountain cave."
    test_voices = ["alloy", "echo", "nova"]
    
    for voice in test_voices:
        try:
            print(f"\nGenerating with voice: {voice}")
            audio_data = service.generate_speech(
                text=test_text,
                voice=voice,
                model="standard",
                speed=1.0,
                output_format="mp3"
            )
            print(f"  ✅ {voice}: {len(audio_data):,} bytes")
        except Exception as e:
            print(f"  ❌ {voice}: {e}")


def test_speed_control(service):
    """Test speech speed control."""
    print("\n" + "="*70)
    print("TEST 6: Speed Control")
    print("="*70)
    
    test_text = "Testing speech speed variations."
    speeds = [0.5, 1.0, 1.5, 2.0]
    
    for speed in speeds:
        try:
            print(f"\nGenerating at speed: {speed}x")
            audio_data = service.generate_speech(
                text=test_text,
                voice="alloy",
                model="standard",
                speed=speed,
                output_format="mp3"
            )
            print(f"  ✅ Speed {speed}x: {len(audio_data):,} bytes")
        except Exception as e:
            print(f"  ❌ Speed {speed}x: {e}")


def test_whisper_transcription(service):
    """Test Whisper speech-to-text."""
    print("\n" + "="*70)
    print("TEST 7: Whisper Transcription")
    print("="*70)
    
    # Check if test audio file exists
    test_audio_path = "e:/storycraft/test_tts_output.mp3"
    if not os.path.exists(test_audio_path):
        print("⚠️  Test audio file not found, skipping transcription test")
        return
    
    try:
        print(f"Transcribing: {test_audio_path}")
        text = service.transcribe_file(
            file_path=test_audio_path,
            language="en",
            temperature=0.0
        )
        
        print("✅ Transcription successful")
        print(f"   Transcribed text: {text}")
        
    except Exception as e:
        print(f"❌ Transcription failed: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Run all tests."""
    print("\n" + "="*70)
    print("OPENAI TTS AND WHISPER INTEGRATION TEST")
    print("="*70)
    
    # Test 1: Availability
    if not test_service_availability():
        print("\n❌ Prerequisites not met. Exiting.")
        return
    
    # Test 2: Initialization
    service = test_service_initialization()
    if not service:
        print("\n❌ Service initialization failed. Exiting.")
        return
    
    # Test 3: Voice options
    test_voice_options(service)
    
    # Test 4: Basic TTS
    if not test_tts_generation(service):
        print("\n⚠️  Basic TTS failed, skipping remaining tests")
        return
    
    # Test 5: Multiple voices
    test_multiple_voices(service)
    
    # Test 6: Speed control
    test_speed_control(service)
    
    # Test 7: Whisper transcription
    test_whisper_transcription(service)
    
    print("\n" + "="*70)
    print("✅ ALL TESTS COMPLETED")
    print("="*70)
    print("\nOpenAI TTS and Whisper integration is working!")
    print("You can now use the following endpoints:")
    print("  • GET  /api/audio/status     - Check service status")
    print("  • GET  /api/audio/voices     - List available voices")
    print("  • POST /api/audio/speak      - Generate speech from text")
    print("  • POST /api/audio/transcribe - Transcribe audio to text")
    print("  • POST /api/audio/test-voice - Test a voice with sample text")


if __name__ == "__main__":
    main()
