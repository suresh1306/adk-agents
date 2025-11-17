"""
Voice Agent Service for Tour Planner
Handles speech-to-text, text-to-speech, and voice streaming using Groq API
"""

import asyncio
import base64
import io
import os
from typing import AsyncGenerator, Optional
import httpx
from pydantic import BaseModel

# Groq API configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_WHISPER_MODEL = "whisper-large-v3-turbo"
GROQ_TTS_MODEL = "playai-tts"
GROQ_API_URL = "https://api.groq.com/openai/v1"

# Available TTS voices for Groq PlayAI
GROQ_TTS_VOICES = [
    # Female voices
    "Aaliyah-PlayAI",    # Young, energetic female
    "Adelaide-PlayAI",   # Mature, professional female
    "Arista-PlayAI",     # Clear, articulate female
    "Celeste-PlayAI",    # Warm, friendly female
    "Cheyenne-PlayAI",   # Expressive female
    "Deedee-PlayAI",     # Playful female
    "Eleanor-PlayAI",    # Sophisticated female
    "Gail-PlayAI",       # Confident female
    "Indigo-PlayAI",     # Modern female
    "Jennifer-PlayAI",   # Professional female
    "Judy-PlayAI",       # Cheerful female
    "Mamaw-PlayAI",      # Grandmother-like female

    # Male voices
    "Angelo-PlayAI",     # Young male
    "Atlas-PlayAI",      # Strong, authoritative male
    "Basil-PlayAI",      # Mature male
    "Briggs-PlayAI",     # Professional male
    "Calum-PlayAI",      # Friendly male
    "Chip-PlayAI",       # Energetic male
    "Cillian-PlayAI",    # Warm male
    "Fritz-PlayAI",      # Distinctive male
    "Mason-PlayAI",      # Casual male
    "Mikail-PlayAI",     # Sophisticated male
    "Mitch-PlayAI",      # Conversational male
]

# Default voice
DEFAULT_VOICE = "Jennifer-PlayAI"  # Professional, clear female voice

class AudioTranscription(BaseModel):
    text: str
    language: Optional[str] = None
    duration: Optional[float] = None

class VoiceAgentService:
    """Service for voice agent capabilities using Groq API"""

    def __init__(self):
        self.groq_api_key = GROQ_API_KEY

        if not self.groq_api_key:
            print("⚠️  GROQ_API_KEY not set - voice features will be disabled")

    async def transcribe_audio(
        self,
        audio_data: bytes,
        content_type: str = "audio/webm"
    ) -> AudioTranscription:
        """
        Transcribe audio using Groq Whisper API

        Args:
            audio_data: Raw audio bytes
            content_type: MIME type of audio (audio/webm, audio/wav, etc.)

        Returns:
            AudioTranscription with text and metadata
        """
        if not self.groq_api_key:
            raise ValueError("GROQ_API_KEY is required for transcription")

        # Determine file extension from content type
        ext_map = {
            "audio/webm": "webm",
            "audio/wav": "wav",
            "audio/mp3": "mp3",
            "audio/mpeg": "mp3",
            "audio/ogg": "ogg",
            "audio/flac": "flac",
        }
        extension = ext_map.get(content_type, "webm")

        async with httpx.AsyncClient(timeout=30.0) as client:
            files = {
                "file": (f"audio.{extension}", audio_data, content_type)
            }
            data = {
                "model": GROQ_WHISPER_MODEL,
                "response_format": "verbose_json",
                "language": "en"  # Auto-detect or specify
            }
            headers = {
                "Authorization": f"Bearer {self.groq_api_key}"
            }

            response = await client.post(
                f"{GROQ_API_URL}/audio/transcriptions",
                files=files,
                data=data,
                headers=headers
            )

            if response.status_code != 200:
                error_detail = response.text
                raise Exception(f"Transcription failed: {error_detail}")

            result = response.json()

            return AudioTranscription(
                text=result.get("text", ""),
                language=result.get("language"),
                duration=result.get("duration")
            )

    async def synthesize_speech(
        self,
        text: str,
        voice: str = DEFAULT_VOICE,
        model: str = "playai-tts"
    ) -> bytes:
        """
        Convert text to speech using Groq PlayAI TTS API

        Args:
            text: Text to synthesize
            voice: Voice to use (see GROQ_TTS_VOICES for available options)
            model: TTS model (playai-tts)

        Returns:
            Audio bytes in MP3 format
        """
        if not self.groq_api_key:
            raise ValueError("GROQ_API_KEY is required for text-to-speech")

        # Validate voice
        if voice not in GROQ_TTS_VOICES:
            print(f"⚠️  Voice '{voice}' not in available voices, using default '{DEFAULT_VOICE}'")
            voice = DEFAULT_VOICE

        async with httpx.AsyncClient(timeout=30.0) as client:
            headers = {
                "Authorization": f"Bearer {self.groq_api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": GROQ_TTS_MODEL,
                "input": text,
                "voice": voice,
                "response_format": "mp3"
            }

            response = await client.post(
                f"{GROQ_API_URL}/audio/speech",
                json=payload,
                headers=headers
            )

            if response.status_code != 200:
                error_detail = response.text

                # Check for terms acceptance requirement
                if "model_terms_required" in error_detail:
                    raise Exception(
                        "PlayAI TTS requires terms acceptance. "
                        "Please visit https://console.groq.com/playground?model=playai-tts "
                        "and accept the terms, then restart the server."
                    )

                raise Exception(f"Speech synthesis failed: {error_detail}")

            return response.content

    async def synthesize_speech_streaming(
        self,
        text: str,
        voice: str = DEFAULT_VOICE,
        chunk_size: int = 4096
    ) -> AsyncGenerator[bytes, None]:
        """
        Stream synthesized speech in chunks using Groq PlayAI TTS

        Args:
            text: Text to synthesize
            voice: Voice to use (see GROQ_TTS_VOICES for available options)
            chunk_size: Size of chunks to yield

        Yields:
            Audio chunks
        """
        if not self.groq_api_key:
            raise ValueError("GROQ_API_KEY is required for text-to-speech")

        # Validate voice
        if voice not in GROQ_TTS_VOICES:
            print(f"⚠️  Voice '{voice}' not in available voices, using default '{DEFAULT_VOICE}'")
            voice = DEFAULT_VOICE

        async with httpx.AsyncClient(timeout=60.0) as client:
            headers = {
                "Authorization": f"Bearer {self.groq_api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": GROQ_TTS_MODEL,
                "input": text,
                "voice": voice,
                "response_format": "mp3"
            }

            async with client.stream(
                "POST",
                f"{GROQ_API_URL}/audio/speech",
                json=payload,
                headers=headers
            ) as response:
                if response.status_code != 200:
                    error_detail = await response.aread()
                    error_text = error_detail.decode('utf-8') if isinstance(error_detail, bytes) else str(error_detail)

                    # Check for terms acceptance requirement
                    if "model_terms_required" in error_text:
                        raise Exception(
                            "PlayAI TTS requires terms acceptance. "
                            "Please visit https://console.groq.com/playground?model=playai-tts "
                            "and accept the terms, then restart the server."
                        )

                    raise Exception(f"Speech synthesis failed: {error_text}")

                async for chunk in response.aiter_bytes(chunk_size):
                    if chunk:
                        yield chunk

    async def process_voice_message(
        self,
        audio_data: bytes,
        content_type: str = "audio/webm"
    ) -> str:
        """
        Process a voice message: transcribe audio to text

        Args:
            audio_data: Raw audio bytes
            content_type: MIME type of audio

        Returns:
            Transcribed text
        """
        transcription = await self.transcribe_audio(audio_data, content_type)
        return transcription.text

    def is_voice_enabled(self) -> bool:
        """Check if voice features are enabled"""
        return bool(self.groq_api_key)

# Global voice service instance
voice_service = VoiceAgentService()
