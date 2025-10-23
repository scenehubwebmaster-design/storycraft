"""
OpenAI Text-to-Speech and Speech-to-Text Service

Provides high-quality voice narration using OpenAI's TTS API and
speech recognition using Whisper API.

TTS Models:
- tts-1: Standard quality, faster, lower latency
- tts-1-hd: High definition quality, slower, higher latency

TTS Voices (6 available):
- alloy: Neutral, balanced
- echo: Male, clear
- fable: British accent, expressive
- onyx: Deep male voice
- nova: Female, warm
- shimmer: Female, bright and energetic

Whisper Models:
- whisper-1: General-purpose speech recognition

Audio Formats:
- TTS Output: mp3, opus, aac, flac, wav, pcm
- Whisper Input: flac, m4a, mp3, mp4, mpeg, mpga, oga, ogg, wav, webm

API Reference:
- TTS: https://platform.openai.com/docs/api-reference/audio/createSpeech
- Whisper: https://platform.openai.com/docs/api-reference/audio/createTranscription
"""

import os
import time
from typing import Iterator, Optional, BinaryIO
from pathlib import Path

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    OpenAI = None


class OpenAITTSService:
    """
    OpenAI TTS and Whisper service for voice narration and speech recognition.
    
    Features:
    - High-quality neural TTS with 6 voice options
    - Multiple audio format support (mp3, wav, opus, etc.)
    - Speech-to-text using Whisper
    - Streaming support for TTS
    - Configurable quality levels
    """
    
    # Voice options with descriptions
    VOICES = {
        "alloy": "Neutral and balanced, suitable for general narration",
        "echo": "Male voice, clear and articulate",
        "fable": "British accent, expressive storytelling",
        "onyx": "Deep male voice, authoritative",
        "nova": "Female voice, warm and engaging",
        "shimmer": "Female voice, bright and energetic"
    }
    
    # TTS model options
    MODELS = {
        "standard": "tts-1",      # Faster, lower latency, standard quality
        "hd": "tts-1-hd"          # Slower, higher quality
    }
    
    # Audio format options
    FORMATS = ["mp3", "opus", "aac", "flac", "wav", "pcm"]
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        default_voice: str = "alloy",
        default_model: str = "standard",
        default_format: str = "mp3"
    ):
        """
        Initialize OpenAI TTS/Whisper service.
        
        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
            default_voice: Default voice (alloy, echo, fable, onyx, nova, shimmer)
            default_model: Default model quality (standard or hd)
            default_format: Default audio format (mp3, opus, aac, flac, wav, pcm)
        """
        if not OPENAI_AVAILABLE:
            raise ImportError(
                "OpenAI Python package not available. Install with: "
                "pip install openai"
            )
        
        # Get API key from parameter or environment
        api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "OpenAI API key not found. Set OPENAI_API_KEY environment variable "
                "or pass api_key parameter."
            )
        
        # Validate inputs
        if default_voice not in self.VOICES:
            raise ValueError(
                f"Invalid voice '{default_voice}'. "
                f"Choose from: {', '.join(self.VOICES.keys())}"
            )
        
        if default_model not in self.MODELS:
            raise ValueError(
                f"Invalid model '{default_model}'. "
                f"Choose from: {', '.join(self.MODELS.keys())}"
            )
        
        if default_format not in self.FORMATS:
            raise ValueError(
                f"Invalid format '{default_format}'. "
                f"Choose from: {', '.join(self.FORMATS)}"
            )
        
        self.client = OpenAI(api_key=api_key)
        self.default_voice = default_voice
        self.default_model = default_model
        self.default_format = default_format
        
        print("OpenAI TTS Service initialized")
        print(f"  Default voice: {default_voice} ({self.VOICES[default_voice]})")
        print(f"  Default model: {default_model} ({self.MODELS[default_model]})")
        print(f"  Default format: {default_format}")
    
    def generate_speech_streaming(
        self,
        text: str,
        voice: Optional[str] = None,
        model: Optional[str] = None,
        speed: float = 1.0
    ) -> Iterator[bytes]:
        """
        Generate speech audio from text with streaming.
        
        OpenAI supports true streaming, yielding audio chunks as they're generated.
        
        Args:
            text: Text to convert to speech (max 4096 characters)
            voice: Voice to use (defaults to self.default_voice)
            model: Model quality (standard or hd, defaults to self.default_model)
            speed: Speech speed (0.25 to 4.0, default 1.0)
            
        Yields:
            bytes: Audio data chunks
        """
        voice = voice or self.default_voice
        model = model or self.default_model
        model_id = self.MODELS[model]
        
        # Validate speed
        if not 0.25 <= speed <= 4.0:
            raise ValueError("Speed must be between 0.25 and 4.0")
        
        # Truncate text if too long (OpenAI limit: 4096 chars)
        if len(text) > 4096:
            text = self._truncate_text(text, 4096)
        
        print(f"Streaming speech generation (voice={voice}, model={model}, speed={speed}, length={len(text)} chars)")
        start_time = time.monotonic()
        
        try:
            # Use streaming API
            with self.client.audio.speech.with_streaming_response.create(
                model=model_id,
                voice=voice,
                input=text,
                response_format=self.default_format,
                speed=speed
            ) as response:
                # Stream chunks as they arrive
                for chunk in response.iter_bytes(chunk_size=4096):
                    yield chunk
            
            end_time = time.monotonic()
            print(f"Streaming completed in {end_time - start_time:.2f}s")
            
        except Exception as e:
            print(f"Speech generation failed: {e}")
            raise
    
    def generate_speech(
        self,
        text: str,
        voice: Optional[str] = None,
        model: Optional[str] = None,
        speed: float = 1.0,
        output_format: Optional[str] = None
    ) -> bytes:
        """
        Generate complete speech audio from text.
        
        Returns complete audio file as bytes.
        
        Args:
            text: Text to convert to speech (max 4096 characters)
            voice: Voice to use (defaults to self.default_voice)
            model: Model quality (standard or hd, defaults to self.default_model)
            speed: Speech speed (0.25 to 4.0, default 1.0)
            output_format: Audio format (mp3, opus, aac, flac, wav, pcm)
            
        Returns:
            bytes: Complete audio file data
        """
        voice = voice or self.default_voice
        model = model or self.default_model
        output_format = output_format or self.default_format
        model_id = self.MODELS[model]
        
        # Validate inputs
        if not 0.25 <= speed <= 4.0:
            raise ValueError("Speed must be between 0.25 and 4.0")
        
        if output_format not in self.FORMATS:
            raise ValueError(
                f"Invalid format '{output_format}'. "
                f"Choose from: {', '.join(self.FORMATS)}"
            )
        
        # Truncate text if too long (OpenAI limit: 4096 chars)
        if len(text) > 4096:
            text = self._truncate_text(text, 4096)
        
        print(f"Generating speech (voice={voice}, model={model}, format={output_format}, speed={speed}, length={len(text)} chars)")
        start_time = time.monotonic()
        
        try:
            # Generate audio
            response = self.client.audio.speech.create(
                model=model_id,
                voice=voice,
                input=text,
                response_format=output_format,
                speed=speed
            )
            
            # Read audio data
            audio_data = response.read()
            
            end_time = time.monotonic()
            print(f"Speech generation completed in {end_time - start_time:.2f}s")
            
            return audio_data
            
        except Exception as e:
            print(f"Speech generation failed: {e}")
            raise
    
    def transcribe_audio(
        self,
        audio_file: BinaryIO,
        language: Optional[str] = None,
        prompt: Optional[str] = None,
        temperature: float = 0.0
    ) -> str:
        """
        Transcribe audio to text using Whisper.
        
        Args:
            audio_file: Audio file (flac, m4a, mp3, mp4, mpeg, mpga, oga, ogg, wav, webm)
            language: Language code (ISO-639-1, e.g., 'en', 'es', 'fr')
            prompt: Optional text to guide the model's style
            temperature: Sampling temperature (0 to 1, default 0 for deterministic)
            
        Returns:
            str: Transcribed text
        """
        print(f"Transcribing audio (language={language or 'auto'}, temperature={temperature})")
        start_time = time.monotonic()
        
        try:
            # Transcribe using Whisper
            params = {
                "model": "whisper-1",
                "file": audio_file,
                "temperature": temperature
            }
            
            if language:
                params["language"] = language
            
            if prompt:
                params["prompt"] = prompt
            
            response = self.client.audio.transcriptions.create(**params)
            
            text = response.text
            
            end_time = time.monotonic()
            print(f"Transcription completed in {end_time - start_time:.2f}s")
            print(f"Transcribed text: {text[:100]}{'...' if len(text) > 100 else ''}")
            
            return text
            
        except Exception as e:
            print(f"Transcription failed: {e}")
            raise
    
    def transcribe_file(
        self,
        file_path: str,
        language: Optional[str] = None,
        prompt: Optional[str] = None,
        temperature: float = 0.0
    ) -> str:
        """
        Transcribe audio file to text using Whisper.
        
        Args:
            file_path: Path to audio file
            language: Language code (ISO-639-1, e.g., 'en', 'es', 'fr')
            prompt: Optional text to guide the model's style
            temperature: Sampling temperature (0 to 1, default 0 for deterministic)
            
        Returns:
            str: Transcribed text
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Audio file not found: {file_path}")
        
        with open(file_path, 'rb') as audio_file:
            return self.transcribe_audio(
                audio_file=audio_file,
                language=language,
                prompt=prompt,
                temperature=temperature
            )
    
    def _truncate_text(self, text: str, max_length: int) -> str:
        """
        Truncate text to max length at sentence boundary.
        
        Args:
            text: Text to truncate
            max_length: Maximum character count
            
        Returns:
            str: Truncated text
        """
        if len(text) <= max_length:
            return text
        
        # Try to break at sentence boundary
        truncated = text[:max_length]
        last_period = truncated.rfind('.')
        last_question = truncated.rfind('?')
        last_exclaim = truncated.rfind('!')
        last_sentence = max(last_period, last_question, last_exclaim)
        
        if last_sentence > max_length * 0.7:  # If we found a good break point
            return truncated[:last_sentence + 1]
        else:
            # No good break point, truncate at word boundary
            last_space = truncated.rfind(' ')
            if last_space > max_length * 0.8:
                return truncated[:last_space] + '...'
            else:
                return truncated + '...'


# Global OpenAI TTS service instance (lazy-loaded)
_openai_tts_service: Optional[OpenAITTSService] = None


def get_openai_tts_service(
    voice: Optional[str] = None,
    model: Optional[str] = None,
    audio_format: Optional[str] = None
) -> OpenAITTSService:
    """
    Get or create global OpenAI TTS service instance.
    
    Lazy-loads the service on first use.
    
    Args:
        voice: Default voice (alloy, echo, fable, onyx, nova, shimmer)
        model: Default model quality (standard or hd)
        audio_format: Default audio format (mp3, opus, aac, flac, wav, pcm)
    
    Returns:
        OpenAITTSService: Global OpenAI TTS service instance
    """
    global _openai_tts_service
    if _openai_tts_service is None:
        _openai_tts_service = OpenAITTSService(
            default_voice=voice or "alloy",
            default_model=model or "standard",
            default_format=audio_format or "mp3"
        )
    return _openai_tts_service
