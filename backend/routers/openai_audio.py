"""
OpenAI Audio API Router

Provides endpoints for:
- Text-to-Speech (TTS) using OpenAI's neural voices
- Speech-to-Text (STT) using Whisper
- Voice configuration and testing
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import StreamingResponse, Response
from pydantic import BaseModel, Field
from typing import Optional, List
import os

from backend.openai_tts_service import get_openai_tts_service, OpenAITTSService, OPENAI_AVAILABLE

router = APIRouter(prefix="/api/audio", tags=["audio"])


class TTSRequest(BaseModel):
    """Request for text-to-speech generation."""
    text: str = Field(..., description="Text to convert to speech (max 4096 characters)")
    voice: Optional[str] = Field("alloy", description="Voice: alloy, echo, fable, onyx, nova, shimmer")
    model: Optional[str] = Field("standard", description="Model quality: standard or hd")
    speed: Optional[float] = Field(1.0, ge=0.25, le=4.0, description="Speech speed (0.25 to 4.0)")
    format: Optional[str] = Field("mp3", description="Audio format: mp3, opus, aac, flac, wav, pcm")
    streaming: Optional[bool] = Field(False, description="Enable streaming response")


class VoiceInfo(BaseModel):
    """Information about an available voice."""
    id: str
    name: str
    description: str
    gender: Optional[str] = None
    accent: Optional[str] = None


class VoicesResponse(BaseModel):
    """Response containing available voices."""
    voices: List[VoiceInfo]
    default_voice: str


class TranscriptionResponse(BaseModel):
    """Response from speech-to-text transcription."""
    text: str
    duration: Optional[float] = None


class AudioServiceStatus(BaseModel):
    """Status of audio service availability."""
    available: bool
    service: str
    api_key_configured: bool
    voices_count: int
    models: List[str]
    formats: List[str]


@router.get("/status", response_model=AudioServiceStatus)
async def get_audio_status():
    """Get status of OpenAI audio service."""
    try:
        api_key_configured = bool(os.getenv("OPENAI_API_KEY"))
        
        if not OPENAI_AVAILABLE:
            return AudioServiceStatus(
                available=False,
                service="openai",
                api_key_configured=api_key_configured,
                voices_count=0,
                models=[],
                formats=[]
            )
        
        return AudioServiceStatus(
            available=api_key_configured,
            service="openai",
            api_key_configured=api_key_configured,
            voices_count=len(OpenAITTSService.VOICES),
            models=list(OpenAITTSService.MODELS.keys()),
            formats=OpenAITTSService.FORMATS
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/voices", response_model=VoicesResponse)
async def get_voices():
    """Get available TTS voices."""
    try:
        if not OPENAI_AVAILABLE:
            raise HTTPException(
                status_code=503,
                detail="OpenAI package not installed"
            )
        
        if not os.getenv("OPENAI_API_KEY"):
            raise HTTPException(
                status_code=503,
                detail="OpenAI API key not configured"
            )
        
        # Map voices to detailed info
        voices = []
        voice_details = {
            "alloy": {"gender": "neutral", "accent": "american"},
            "echo": {"gender": "male", "accent": "american"},
            "fable": {"gender": "neutral", "accent": "british"},
            "onyx": {"gender": "male", "accent": "american"},
            "nova": {"gender": "female", "accent": "american"},
            "shimmer": {"gender": "female", "accent": "american"}
        }
        
        for voice_id, description in OpenAITTSService.VOICES.items():
            details = voice_details.get(voice_id, {})
            voices.append(VoiceInfo(
                id=voice_id,
                name=voice_id.capitalize(),
                description=description,
                gender=details.get("gender"),
                accent=details.get("accent")
            ))
        
        return VoicesResponse(
            voices=voices,
            default_voice="alloy"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/speak")
async def text_to_speech(request: TTSRequest):
    """
    Convert text to speech using OpenAI TTS.
    
    Returns audio file in requested format.
    """
    try:
        # Get TTS service
        tts_service = get_openai_tts_service()
        
        # Generate speech
        if request.streaming:
            # Return streaming response
            def audio_stream():
                for chunk in tts_service.generate_speech_streaming(
                    text=request.text,
                    voice=request.voice,
                    model=request.model,
                    speed=request.speed
                ):
                    yield chunk
            
            # Determine content type
            content_types = {
                "mp3": "audio/mpeg",
                "opus": "audio/opus",
                "aac": "audio/aac",
                "flac": "audio/flac",
                "wav": "audio/wav",
                "pcm": "audio/pcm"
            }
            content_type = content_types.get(request.format, "audio/mpeg")
            
            return StreamingResponse(
                audio_stream(),
                media_type=content_type,
                headers={
                    "Content-Disposition": f"attachment; filename=speech.{request.format}"
                }
            )
        else:
            # Return complete audio file
            audio_data = tts_service.generate_speech(
                text=request.text,
                voice=request.voice,
                model=request.model,
                speed=request.speed,
                output_format=request.format
            )
            
            # Determine content type
            content_types = {
                "mp3": "audio/mpeg",
                "opus": "audio/opus",
                "aac": "audio/aac",
                "flac": "audio/flac",
                "wav": "audio/wav",
                "pcm": "audio/pcm"
            }
            content_type = content_types.get(request.format, "audio/mpeg")
            
            return Response(
                content=audio_data,
                media_type=content_type,
                headers={
                    "Content-Disposition": f"attachment; filename=speech.{request.format}"
                }
            )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"TTS error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/transcribe", response_model=TranscriptionResponse)
async def speech_to_text(
    file: UploadFile = File(..., description="Audio file to transcribe"),
    language: Optional[str] = Form(None, description="Language code (e.g., 'en', 'es', 'fr')"),
    prompt: Optional[str] = Form(None, description="Optional text to guide transcription style"),
    temperature: float = Form(0.0, ge=0.0, le=1.0, description="Sampling temperature (0-1)")
):
    """
    Transcribe audio to text using Whisper.
    
    Supports: flac, m4a, mp3, mp4, mpeg, mpga, oga, ogg, wav, webm
    """
    try:
        import time
        start_time = time.monotonic()
        
        # Get TTS service (which also provides Whisper)
        tts_service = get_openai_tts_service()
        
        # Read uploaded file
        audio_content = await file.read()
        
        # Create file-like object for transcription
        from io import BytesIO
        audio_file = BytesIO(audio_content)
        audio_file.name = file.filename  # Preserve filename for format detection
        
        # Transcribe
        text = tts_service.transcribe_audio(
            audio_file=audio_file,
            language=language,
            prompt=prompt,
            temperature=temperature
        )
        
        duration = time.monotonic() - start_time
        
        return TranscriptionResponse(
            text=text,
            duration=duration
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Transcription error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/test-voice")
async def test_voice(
    voice: str = Form(..., description="Voice to test"),
    model: str = Form("standard", description="Model quality"),
    speed: float = Form(1.0, description="Speech speed")
):
    """
    Test a voice with sample text.
    
    Returns short audio sample for voice preview.
    """
    try:
        # Sample text for testing
        sample_text = (
            "Greetings, adventurer. "
            "I am your Dungeon Master, ready to guide you through epic quests "
            "and thrilling encounters. Roll for initiative!"
        )
        
        # Get TTS service
        tts_service = get_openai_tts_service()
        
        # Generate sample
        audio_data = tts_service.generate_speech(
            text=sample_text,
            voice=voice,
            model=model,
            speed=speed,
            output_format="mp3"
        )
        
        return Response(
            content=audio_data,
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": f"attachment; filename=voice_test_{voice}.mp3"
            }
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Voice test error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
