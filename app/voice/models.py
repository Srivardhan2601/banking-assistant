"""
Data models for the Voice Interaction Module.
Defines schemas for STT, TTS, language detection, and audio response payloads.
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class AudioInputPayload(BaseModel):
    audio_base64: Optional[str] = Field(
        default=None,
        description="Base64 encoded raw audio or wav/webm data from microphone."
    )
    audio_mime: str = Field(
        default="audio/webm",
        description="MIME type of the audio stream (e.g. audio/webm, audio/wav)."
    )
    customer_id: str = Field(..., description="Target customer ID.")
    language_hint: Optional[str] = Field(
        default=None,
        description="Optional ISO language code hint (e.g. 'hi-IN', 'en-IN')."
    )


class STTResult(BaseModel):
    transcript: str = Field(..., description="Transcribed customer speech.")
    detected_language: str = Field(
        default="en-IN",
        description="Detected BCP-47 language tag (e.g. 'hi-IN', 'en-IN', 'ta-IN')."
    )
    confidence: float = Field(
        default=0.95,
        description="STT transcription confidence score (0.0 to 1.0)."
    )
    provider_used: str = Field(
        default="web_speech_or_mock",
        description="Provider executing the transcription (Sarvam, Google, WebSpeech)."
    )


class TTSResult(BaseModel):
    audio_base64: Optional[str] = Field(
        default=None,
        description="Base64 synthesized audio file (e.g. mp3/wav/ogg)."
    )
    audio_mime: str = Field(default="audio/wav")
    language: str = Field(default="en-IN")
    synthesized_text: str = Field(..., description="Exact text passed into the TTS engine.")
    provider_used: str = Field(default="browser_or_sarvam")


class VoiceTurnResult(BaseModel):
    stt: STTResult
    tts: TTSResult
    pipeline_response: Dict[str, Any]
    fallback_triggered: bool = False
    fallback_reason: Optional[str] = None
