"""
Speech transcription module for Kirana Store Management System.

Extracts and adapts transcription logic from voice_demo.py for use in Flask API.
Supports Hindi (hi-IN) and English (en-IN) transcription using Google Speech API.

Requirements:
  pip install SpeechRecognition pydub

System dependency (for audio conversion):
  - Windows: Download ffmpeg.exe and add to PATH
  - Linux: sudo apt-get install ffmpeg
  - macOS: brew install ffmpeg
"""

import os
import tempfile
import logging
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# Check if speech_recognition is available
try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    SPEECH_RECOGNITION_AVAILABLE = False
    logger.warning("speech_recognition not installed. Install with: pip install SpeechRecognition")

# Check if pydub is available for audio conversion
try:
    from pydub import AudioSegment
    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False
    logger.warning("pydub not installed. Install with: pip install pydub")


def convert_audio_to_wav(input_path: str, output_path: Optional[str] = None) -> str:
    """
    Convert audio file to WAV format for speech_recognition compatibility.
    
    Args:
        input_path: Path to input audio file (m4a, mp3, etc.)
        output_path: Optional output path. If None, creates temp file.
    
    Returns:
        Path to converted WAV file
    
    Raises:
        RuntimeError: If pydub is not available
        Exception: If conversion fails
    """
    if not PYDUB_AVAILABLE:
        raise RuntimeError(
            "pydub not installed. Install with: pip install pydub\n"
            "Also ensure ffmpeg is installed on your system."
        )
    
    try:
        # Load audio file (pydub auto-detects format)
        audio = AudioSegment.from_file(input_path)
        
        # Generate output path if not provided
        if output_path is None:
            temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
            output_path = temp_file.name
            temp_file.close()
        
        # Export as WAV (16-bit PCM, which speech_recognition expects)
        audio.export(
            output_path,
            format='wav',
            parameters=['-acodec', 'pcm_s16le', '-ar', '16000', '-ac', '1']
        )
        
        logger.info(f"Converted audio to WAV: {input_path} -> {output_path}")
        return output_path
    
    except Exception as e:
        logger.error(f"Failed to convert audio: {e}")
        raise


def transcribe_audio_file(
    audio_file_path: str,
    language: str = 'hi-IN',
    try_fallback: bool = True
) -> Dict[str, Any]:
    """
    Transcribe audio file to text using Google Speech API.
    
    Extracted from voice_demo.py for use in Flask API.
    Supports Hindi and English with automatic fallback.
    
    Args:
        audio_file_path: Path to audio file (WAV preferred, or any format if pydub available)
        language: Primary language code ('hi-IN' for Hindi, 'en-IN' for English)
        try_fallback: If True, try alternate language if primary fails
    
    Returns:
        dict: {
            'transcript': str,      # Transcribed text
            'language': str,        # Detected language code
            'confidence': float,    # Confidence score (0.0-1.0)
            'error': str (optional) # Error message if any
        }
    
    Raises:
        RuntimeError: If speech_recognition is not available
    """
    if not SPEECH_RECOGNITION_AVAILABLE:
        return {
            'transcript': '',
            'confidence': 0.0,
            'language': language,
            'error': 'speech_recognition not installed. Install with: pip install SpeechRecognition'
        }
    
    recognizer = sr.Recognizer()
    temp_wav_path = None
    
    try:
        # Check if file exists
        if not os.path.exists(audio_file_path):
            return {
                'transcript': '',
                'confidence': 0.0,
                'language': language,
                'error': f'Audio file not found: {audio_file_path}'
            }
        
        # Convert to WAV if needed (non-wav formats)
        file_ext = Path(audio_file_path).suffix.lower()
        if file_ext != '.wav':
            if not PYDUB_AVAILABLE:
                return {
                    'transcript': '',
                    'confidence': 0.0,
                    'language': language,
                    'error': f'Cannot process {file_ext} files. pydub not installed for audio conversion.'
                }
            
            logger.info(f"Converting {file_ext} to WAV for transcription...")
            temp_wav_path = convert_audio_to_wav(audio_file_path)
            audio_path_to_use = temp_wav_path
        else:
            audio_path_to_use = audio_file_path
        
        # Load audio file
        with sr.AudioFile(audio_path_to_use) as source:
            # Adjust for ambient noise
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = recognizer.record(source)
        
        logger.info(f"Processing audio file: {audio_file_path}")
        
        # Try primary language first
        transcript = None
        detected_language = None
        
        try:
            # Try primary language (default: Hindi)
            transcript = recognizer.recognize_google(audio, language=language)
            detected_language = language
            logger.info(f"Transcription successful in {language}")
        
        except sr.UnknownValueError:
            # Speech was unintelligible in primary language
            if try_fallback:
                # Determine fallback languages (try other supported languages)
                supported_languages = ['hi-IN', 'en-IN', 'kn-IN']
                fallback_languages = [lang for lang in supported_languages if lang != language]
                
                for fallback_language in fallback_languages:
                    try:
                        logger.info(f"Primary language failed, trying {fallback_language}...")
                        transcript = recognizer.recognize_google(audio, language=fallback_language)
                        detected_language = fallback_language
                        logger.info(f"Transcription successful in fallback: {fallback_language}")
                        break
                    except sr.UnknownValueError:
                        continue
                
                if transcript is None:
                    # Could not understand in any language
                    logger.warning("Could not understand audio in any language")
                    return {
                        'transcript': '',
                        'confidence': 0.0,
                        'language': language,
                        'error': 'Could not understand audio. Please speak clearly and try again.'
                    }
            else:
                return {
                    'transcript': '',
                    'confidence': 0.0,
                    'language': language,
                    'error': 'Could not understand audio in the specified language.'
                }
        
        except sr.RequestError as e:
            logger.error(f"Speech recognition API error: {e}")
            return {
                'transcript': '',
                'confidence': 0.0,
                'language': language,
                'error': f'Speech recognition service error. Check internet connection. Details: {str(e)}'
            }
        
        # Return successful transcription
        return {
            'transcript': transcript,
            'confidence': 0.9,  # Google Speech API doesn't return confidence for simple requests
            'language': detected_language
        }
    
    except Exception as e:
        logger.error(f"Transcription error: {e}", exc_info=True)
        return {
            'transcript': '',
            'confidence': 0.0,
            'language': language,
            'error': f'Transcription failed: {str(e)}'
        }
    
    finally:
        # Clean up temporary WAV file
        if temp_wav_path and os.path.exists(temp_wav_path):
            try:
                os.remove(temp_wav_path)
                logger.debug(f"Cleaned up temp file: {temp_wav_path}")
            except Exception as e:
                logger.warning(f"Failed to clean up temp file: {e}")


def transcribe_audio_bytes(
    audio_bytes: bytes,
    language: str = 'hi-IN',
    file_format: str = 'm4a'
) -> Dict[str, Any]:
    """
    Transcribe audio from bytes (for direct file upload handling).
    
    Args:
        audio_bytes: Raw audio data
        language: Language code ('hi-IN' or 'en-IN')
        file_format: Original file format (m4a, mp3, wav, etc.)
    
    Returns:
        dict: Same format as transcribe_audio_file()
    """
    temp_input_path = None
    
    try:
        # Save bytes to temporary file
        suffix = f'.{file_format}' if not file_format.startswith('.') else file_format
        temp_file = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
        temp_input_path = temp_file.name
        temp_file.write(audio_bytes)
        temp_file.close()
        
        # Transcribe using file-based function
        return transcribe_audio_file(temp_input_path, language)
    
    finally:
        # Clean up temporary input file
        if temp_input_path and os.path.exists(temp_input_path):
            try:
                os.remove(temp_input_path)
            except Exception as e:
                logger.warning(f"Failed to clean up temp input file: {e}")


# For backward compatibility with voice_demo.py import pattern
def is_available() -> bool:
    """Check if transcription service is available."""
    return SPEECH_RECOGNITION_AVAILABLE

