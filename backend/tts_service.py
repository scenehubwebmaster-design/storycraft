"""
Text-to-Speech Service using Kitten TTS

Provides voice narration for AI DM responses using Kitten TTS model.
Ultra-lightweight (under 25MB) and CPU-optimized - no GPU required!

Installation:
    pip install https://github.com/KittenML/KittenTTS/releases/download/0.1/kittentts-0.1.0-py3-none-any.whl
    pip install soundfile

Model: KittenML/kitten-tts-nano-0.2
Voice: tara (default DM voice, mapped to expr-voice-2-f)
Sample Rate: 24000 Hz
Format: WAV (16-bit PCM)
"""

import io
import time
from typing import Iterator, Optional

try:
    from kittentts import KittenTTS
    import soundfile as sf  # type: ignore[import-not-found]
    KITTEN_AVAILABLE = True
except ImportError:
    KITTEN_AVAILABLE = False
    KittenTTS = None
    sf = None

class TTSService:
    """
    Kitten TTS service for generating voice narration.
    
    Supports:
    - Ultra-lightweight model (under 25MB)
    - CPU-optimized (no GPU required!)
    - Multiple voice options
    - High-quality natural speech
    
    Voice Mapping (8 voices total):
    - tara, leah, jess, mia (female) -> expr-voice-2-f through expr-voice-5-f
    - leo, dan, zac, zoe (male) -> expr-voice-2-m through expr-voice-5-m
    """
    
    # Voice mapping from Orpheus names to Kitten TTS voice IDs
    VOICE_MAP = {
        # Female voices
        "tara": "expr-voice-2-f",  # Clear, professional narrator
        "leah": "expr-voice-3-f",  # Warm, friendly storyteller
        "jess": "expr-voice-4-f",  # Energetic, adventurous tone
        "mia": "expr-voice-5-f",   # Mysterious, dramatic flair
        # Male voices
        "leo": "expr-voice-2-m",   # Deep, authoritative narrator
        "dan": "expr-voice-3-m",   # Calm, classic storyteller
        "zac": "expr-voice-4-m",   # Young, enthusiastic adventurer
        "zoe": "expr-voice-5-m",   # Gender-neutral, versatile
    }
    
    def __init__(
        self,
        model_name: str = "KittenML/kitten-tts-nano-0.2",
        default_voice: str = "tara"
    ):
        """
        Initialize TTS service with Kitten TTS model.
        
        Args:
            model_name: HuggingFace model identifier
            default_voice: Default voice (tara, leah, jess, leo, dan, mia, zac, zoe)
        """
        if not KITTEN_AVAILABLE:
            raise ImportError(
                "Kitten TTS not available. Install with: "
                "pip install https://github.com/KittenML/KittenTTS/releases/download/0.1/kittentts-0.1.0-py3-none-any.whl && "
                "pip install soundfile"
            )
        
        print(f"Loading Kitten TTS model: {model_name}")
        try:
            self.model = KittenTTS(model_name)
            self.default_voice = default_voice
            print(f"Kitten TTS model loaded successfully. Default voice: {default_voice}")
        except Exception as e:
            print(f"Failed to load Kitten TTS model: {e}")
            raise
    
    def generate_speech_streaming(
        self,
        text: str,
        voice: Optional[str] = None,
        add_dm_personality: bool = True
    ) -> Iterator[bytes]:
        """
        Generate speech audio from text with streaming.
        
        Note: Kitten TTS doesn't support true streaming like Orpheus,
        but we maintain the interface for compatibility. Returns the
        complete audio as a single chunk.
        
        Args:
            text: Text to convert to speech
            voice: Voice to use (defaults to self.default_voice)
            add_dm_personality: Add DM-appropriate emotion tags (not supported in Kitten TTS)
            
        Yields:
            bytes: Audio data chunks (16-bit PCM, 24kHz)
        """
        # Generate complete audio and yield as single chunk
        audio_data = self.generate_speech(
            text=text,
            voice=voice,
            add_dm_personality=False  # Kitten TTS doesn't support emotion tags
        )
        yield audio_data
    
    def generate_speech(
        self,
        text: str,
        voice: Optional[str] = None,
        add_dm_personality: bool = True,
        flavor_text_only: bool = False
    ) -> bytes:
        """
        Generate complete speech audio from text.
        
        Returns complete WAV file as bytes.
        
        Args:
            text: Text to convert to speech
            voice: Voice to use (defaults to self.default_voice)
            add_dm_personality: Add DM-appropriate emotion tags (not supported in Kitten TTS)
            flavor_text_only: If True, extract only narrative/flavor text (skip mechanics)
            
        Returns:
            bytes: Complete WAV file data
        """
        voice = voice or self.default_voice
        
        # Extract flavor text if requested (for immersive narration)
        if flavor_text_only:
            text = self._extract_flavor_text(text)
        
        # Clean and preprocess text for TTS
        text = self._preprocess_text(text)
        
        # Map friendly voice name to Kitten TTS voice ID
        kitten_voice = self.VOICE_MAP.get(voice, self.VOICE_MAP["tara"])
        
        print(f"Generating speech (voice={voice} -> {kitten_voice}, length={len(text)} chars)")
        start_time = time.monotonic()
        
        try:
            # Generate audio using Kitten TTS
            # Returns numpy array with sample rate 24000
            audio_array = self.model.generate(text, voice=kitten_voice)
            
            # Convert to WAV format using soundfile
            wav_buffer = io.BytesIO()
            sf.write(wav_buffer, audio_array, 24000, format='WAV', subtype='PCM_16')
            wav_buffer.seek(0)
            wav_data = wav_buffer.read()
            
            end_time = time.monotonic()
            generation_time = end_time - start_time
            print(f"Speech generation completed in {generation_time:.2f}s")
            
            return wav_data
            
        except Exception as e:
            print(f"Speech generation failed: {e}")
            raise
    
    def _preprocess_text(self, text: str) -> str:
        """
        Preprocess text for TTS generation.
        
        Cleans up formatting issues that might cause ONNX errors:
        - Remove extra whitespace
        - Remove special markdown/control characters
        - Ensure text isn't empty
        - Limit length to avoid ONNX errors (Kitten TTS max: ~400 chars)
        
        Args:
            text: Raw text input
            
        Returns:
            str: Cleaned text ready for TTS
        """
        if not text or not text.strip():
            return "No text to speak."
        
        # Remove excessive whitespace
        text = ' '.join(text.split())
        
        # Remove markdown formatting that might confuse TTS
        # Remove bold/italic markers
        text = text.replace('**', '').replace('__', '').replace('*', '').replace('_', '')
        
        # Remove code blocks
        text = text.replace('```', '').replace('`', '')
        
        # Limit length for ONNX model stability
        # Increased from 400 to 2000 characters to support full DM responses
        # Kitten TTS can handle longer texts, but very long ones may cause issues
        max_length = 2000  # characters
        if len(text) > max_length:
            # Try to break at sentence boundary
            truncated = text[:max_length]
            last_period = truncated.rfind('.')
            last_question = truncated.rfind('?')
            last_exclaim = truncated.rfind('!')
            last_sentence = max(last_period, last_question, last_exclaim)
            
            if last_sentence > max_length * 0.6:  # If we found a sentence break
                text = truncated[:last_sentence + 1]
            else:
                # No good break point, truncate at word boundary
                last_space = truncated.rfind(' ')
                if last_space > max_length * 0.8:
                    text = truncated[:last_space] + '...'
                else:
                    text = truncated + '...'
        
        return text.strip()
    
    def _extract_flavor_text(self, text: str) -> str:
        """
        Extract narrative/flavor text from D&D messages, filtering out mechanical details.
        
        This helps create more immersive narration by focusing on descriptive text
        while skipping spell stats, die rolls, and technical information.
        
        Rules:
        - Include: Narrative descriptions, story text, atmospheric details
        - Exclude: Spell metadata (Level, Casting Time, Range, Components, Duration)
        - Exclude: Technical questions and prompts
        - Exclude: Die roll notation (e.g., "8d6", "1d20")
        
        Args:
            text: Full message text
            
        Returns:
            str: Extracted flavor/narrative text, or full text if no clear separation
        """
        import re
        
        lines = text.split('\n')
        flavor_lines = []
        
        # Patterns for mechanical/metadata lines to skip
        skip_patterns = [
            r'^Level\s*&?\s*School:',
            r'^Casting Time:',
            r'^Range:',
            r'^Components:',
            r'^Duration:',
            r'^Attack Bonus:',
            r'^Damage:',
            r'^Armor Class:',
            r'^Hit Points:',
            r'^Speed:',
            r'^STR|DEX|CON|INT|WIS|CHA',
            r'^Saving Throws:',
            r'^Skills:',
            r'^Challenge Rating:',
            r'^\*\*Level\s*&?\s*School',
            r'^\*\*Casting Time',
            r'^\*\*Range',
            r'^\*\*Components',
            r'^\*\*Duration',
            r'^Which direction',  # Questions/prompts
            r'^Please note that',  # Instructions
            r'^Is there anything',  # Questions
            r'^Would you like',  # Questions
            r'^Do you want',  # Questions
            r'^Here are the details',  # Preamble
            r'^The .+ spell is a .+level',  # "The Fireball spell is a 3rd-level..."
            r"^It seems you'?re trying",  # "It seems you're trying to..."
        ]
        
        in_flavor_section = False
        
        for line in lines:
            line_stripped = line.strip()
            
            # Skip empty lines
            if not line_stripped:
                continue
            
            # Check if this line matches any skip pattern
            should_skip = any(re.match(pattern, line_stripped, re.IGNORECASE) for pattern in skip_patterns)
            
            if should_skip:
                # We're in a mechanical section, not flavor
                in_flavor_section = False
                continue
            
            # Skip spell/monster names in isolation (bold headers)
            if re.match(r'^\*\*[A-Z][^*]+\*\*(\s*\([^)]+\))?$', line_stripped):
                continue
            
            # If line looks descriptive (starts with capital, has narrative words)
            # or continues from previous flavor text
            narrative_indicators = [
                'you', 'your', 'the', 'a ', 'an ', 'as ', 'each', 
                'bright', 'dark', 'ancient', 'massive', 'glowing',
                'strikes', 'blasts', 'forms', 'creates', 'appears'
            ]
            
            starts_with_narrative = any(
                line_stripped.lower().startswith(ind) 
                for ind in narrative_indicators
            )
            
            # Keep lines that look like narrative/description
            if starts_with_narrative or in_flavor_section:
                flavor_lines.append(line_stripped)
                in_flavor_section = True
        
        # Join flavor lines
        flavor_text = ' '.join(flavor_lines)
        
        # If we extracted something substantial, use it
        if len(flavor_text) > 50:
            return flavor_text
        
        # If extraction resulted in very little text, return original
        # (might be a simple message without mechanical details)
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
