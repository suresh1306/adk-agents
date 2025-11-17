"""
Voice Agent Service for Tour Planner
Handles speech-to-text, text-to-speech, and voice streaming
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
GROQ_API_URL = "https://api.groq.com/openai/v1"

# OpenAI TTS configuration (fallback to Groq if available)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_TTS_MODEL = "tts-1"
OPENAI_TTS_VOICE = "alloy"  # Options: alloy, echo, fable, onyx, nova, shimmer

class AudioTranscription(BaseModel):
    text: str
    language: Optional[str] = None
    duration: Optional[float] = None

class VoiceAgentService:
    """Service for voice agent capabilities"""

    def __init__(self):
        self.groq_api_key = GROQ_API_KEY
        self.openai_api_key = OPENAI_API_KEY

        if not self.groq_api_key:
            print("⚠️  GROQ_API_KEY not set - voice features will be limited")

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
        voice: str = "alloy",
        model: str = "tts-1"
    ) -> bytes:
        """
        Convert text to speech using OpenAI TTS API

        Args:
            text: Text to synthesize
            voice: Voice to use (alloy, echo, fable, onyx, nova, shimmer)
            model: TTS model (tts-1 or tts-1-hd)

        Returns:
            Audio bytes in MP3 format
        """
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required for text-to-speech")

        async with httpx.AsyncClient(timeout=30.0) as client:
            headers = {
                "Authorization": f"Bearer {self.openai_api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": model,
                "input": text,
                "voice": voice,
                "response_format": "mp3"
            }

            response = await client.post(
                "https://api.openai.com/v1/audio/speech",
                json=payload,
                headers=headers
            )

            if response.status_code != 200:
                error_detail = response.text
                raise Exception(f"Speech synthesis failed: {error_detail}")

            return response.content

    async def synthesize_speech_streaming(
        self,
        text: str,
        voice: str = "alloy",
        chunk_size: int = 4096
    ) -> AsyncGenerator[bytes, None]:
        """
        Stream synthesized speech in chunks

        Args:
            text: Text to synthesize
            voice: Voice to use
            chunk_size: Size of chunks to yield

        Yields:
            Audio chunks
        """
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required for text-to-speech")

        async with httpx.AsyncClient(timeout=60.0) as client:
            headers = {
                "Authorization": f"Bearer {self.openai_api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "tts-1",
                "input": text,
                "voice": voice,
                "response_format": "mp3"
            }

            async with client.stream(
                "POST",
                "https://api.openai.com/v1/audio/speech",
                json=payload,
                headers=headers
            ) as response:
                if response.status_code != 200:
                    error_detail = await response.aread()
                    raise Exception(f"Speech synthesis failed: {error_detail}")

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
        return bool(self.groq_api_key and self.openai_api_key)

# Global voice service instance
voice_service = VoiceAgentService()
