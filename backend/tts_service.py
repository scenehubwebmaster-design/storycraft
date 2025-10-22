"""
Text-to-Speech Service using Orpheus-TTS

Provides voice narration for AI DM responses using Orpheus TTS model.
Supports streaming audio generation with ~200ms latency.

Installation:
    pip install orpheus-speech
    # If vllm issues: pip install vllm==0.7.3

Model: canopylabs/orpheus-tts-0.1-finetune-prod
Voice: tara (default DM voice)
Sample Rate: 24000 Hz
Format: WAV (16-bit PCM)
"""

import wave
import io
import time
from typing import Iterator, Optional

try:
    from orpheus_tts import OrpheusModel
    ORPHEUS_AVAILABLE = True
except ImportError:
    ORPHEUS_AVAILABLE = False
    OrpheusModel = None

class TTSService:
    """
    Orpheus TTS service for generating voice narration.
    
    Supports:
    - Streaming audio generation
    - Multiple voice options
    - Emotion tags (<laugh>, <sigh>, etc.)
    - Low-latency generation (~200ms)
    """
    
    def __init__(
        self,
        model_name: str = "canopylabs/orpheus-tts-0.1-finetune-prod",
        max_model_len: int = 2048,
        default_voice: str = "tara"
    ):
        """
        Initialize TTS service with Orpheus model.
        
        Args:
            model_name: HuggingFace model identifier
            max_model_len: Maximum model sequence length
            default_voice: Default voice (tara, leah, jess, leo, dan, mia, zac, zoe)
        """
        if not ORPHEUS_AVAILABLE:
            raise ImportError(
                "Orpheus TTS not available. Install with: pip install orpheus-speech"
            )
        
        print(f"Loading Orpheus TTS model: {model_name}")
        try:
            self.model = OrpheusModel(
                model_name=model_name,
                max_model_len=max_model_len
            )
            self.default_voice = default_voice
            print(f"Orpheus TTS model loaded successfully. Default voice: {default_voice}")
        except Exception as e:
            print(f"Failed to load Orpheus TTS model: {e}")
            raise
    
    def generate_speech_streaming(
        self,
        text: str,
        voice: Optional[str] = None,
        add_dm_personality: bool = True
    ) -> Iterator[bytes]:
        """
        Generate speech audio from text with streaming.
        
        Yields audio chunks as they are generated for low latency.
        
        Args:
            text: Text to convert to speech
            voice: Voice to use (defaults to self.default_voice)
            add_dm_personality: Add DM-appropriate emotion tags
            
        Yields:
            bytes: Audio data chunks (16-bit PCM, 24kHz)
        """
        voice = voice or self.default_voice
        
        # Optionally add personality to DM narration
        if add_dm_personality:
            text = self._add_dm_personality(text)
        
        # Format prompt for Orpheus
        prompt = f"{voice}: {text}"
        
        print(f"Generating speech (voice={voice}, length={len(text)} chars)")
        start_time = time.monotonic()
        
        try:
            # Generate speech tokens (streaming)
            syn_tokens = self.model.generate_speech(
                prompt=prompt,
                voice=voice
            )
            
            # Stream audio chunks
            for audio_chunk in syn_tokens:
                yield audio_chunk
            
            end_time = time.monotonic()
            generation_time = end_time - start_time
            print(f"Speech generation completed in {generation_time:.2f}s")
            
        except Exception as e:
            print(f"Speech generation failed: {e}")
            raise
    
    def generate_speech(
        self,
        text: str,
        voice: Optional[str] = None,
        add_dm_personality: bool = True
    ) -> bytes:
        """
        Generate complete speech audio from text (non-streaming).
        
        Returns complete WAV file as bytes.
        
        Args:
            text: Text to convert to speech
            voice: Voice to use (defaults to self.default_voice)
            add_dm_personality: Add DM-appropriate emotion tags
            
        Returns:
            bytes: Complete WAV file data
        """
        # Collect all chunks
        audio_chunks = list(self.generate_speech_streaming(
            text=text,
            voice=voice,
            add_dm_personality=add_dm_personality
        ))
        
        # Combine into WAV file
        wav_data = self._create_wav_file(audio_chunks)
        return wav_data
    
    def _create_wav_file(self, audio_chunks: list[bytes]) -> bytes:
        """
        Create WAV file from audio chunks.
        
        Args:
            audio_chunks: List of PCM audio data chunks
            
        Returns:
            bytes: Complete WAV file data
        """
        wav_buffer = io.BytesIO()
        
        with wave.open(wav_buffer, "wb") as wf:
            wf.setnchannels(1)  # Mono
            wf.setsampwidth(2)  # 16-bit
            wf.setframerate(24000)  # 24kHz
            
            # Write all chunks
            for chunk in audio_chunks:
                wf.writeframes(chunk)
        
        wav_buffer.seek(0)
        return wav_buffer.read()
    
    def _add_dm_personality(self, text: str) -> str:
        """
        Add emotion tags to make DM narration more expressive.
        
        Supported tags: <laugh>, <chuckle>, <sigh>, <cough>, <sniffle>, 
                       <groan>, <yawn>, <gasp>
        
        Args:
            text: Original text
            
        Returns:
            str: Text with emotion tags added
        """
        # Add chuckle after humor indicators
        if any(word in text.lower() for word in ['haha', 'hehe', 'amusing', 'funny']):
            text = text.replace('.', '. <chuckle>', 1)
        
        # Add gasp after surprise indicators
        if any(word in text.lower() for word in ['suddenly', 'unexpected', 'surprise']):
            text = text.replace('!', '! <gasp>', 1)
        
        # Add dramatic sigh for ominous descriptions
        if any(word in text.lower() for word in ['dark', 'ominous', 'dread', 'evil']):
            # Don't always add - makes it more natural
            if 'darkness' in text.lower():
                text = text.replace('.', '. <sigh>', 1)
        
        return text

# Global TTS service instance (lazy-loaded)
_tts_service: Optional[TTSService] = None

def get_tts_service() -> TTSService:
    """
    Get or create global TTS service instance.
    
    Lazy-loads the model on first use to avoid startup delays.
    
    Returns:
        TTSService: Global TTS service instance
    """
    global _tts_service
    if _tts_service is None:
        _tts_service = TTSService()
    return _tts_service
