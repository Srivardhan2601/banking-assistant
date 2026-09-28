"""
Voice Interaction Wrapper:
Wraps the core text pipeline with Speech-to-Text and Text-to-Speech without
modifying the core orchestrator, Hindsight memory layer, or escalation logic.
"""

from typing import Dict, Any, Optional
from .models import AudioInputPayload, STTResult, TTSResult, VoiceTurnResult
from .stt_adapter import stt_service
from .tts_adapter import tts_service
from .language_router import language_router


class VoiceHandler:
    """
    Dedicated voice interface layer.
    Orchestrates: Speech In -> STT -> Language Detection -> Core Pipeline -> Language Alignment -> TTS -> Speech Out.
    """

    def __init__(self, orchestrator=None):
        self._orchestrator = orchestrator

    @property
    def orchestrator(self):
        if self._orchestrator is None:
            from app.orchestrator import orchestrator
            self._orchestrator = orchestrator
        return self._orchestrator

    def handle_voice_turn(
        self,
        audio_payload: AudioInputPayload,
        client_transcript: Optional[str] = None,
        client_lang: Optional[str] = None
    ) -> VoiceTurnResult:
        """
        Processes a full audio turn from microphone/input to synthesized audio output.
        """
        # Step 1: Speech-to-Text with auto-detected language
        stt_res = stt_service.transcribe(
            audio_payload=audio_payload,
            client_transcript=client_transcript,
            client_lang=client_lang
        )

        # Step 2: Graceful fallback check
        if not stt_res.transcript or stt_res.confidence < 0.5:
            return VoiceTurnResult(
                stt=stt_res,
                tts=TTSResult(
                    audio_base64=None,
                    synthesized_text="I could not hear you clearly. Please type your message in the chat.",
                    language="en-IN"
                ),
                pipeline_response={
                    "response": "I could not hear you clearly. Please type your message in the chat.",
                    "is_escalated": False
                },
                fallback_triggered=True,
                fallback_reason="Low STT confidence or silent audio input."
            )

        # Step 3: Route to core text pipeline UNCHANGED
        pipeline_output = self.orchestrator.process_message(
            customer_id=audio_payload.customer_id,
            customer_message=stt_res.transcript,
            channel="voice",
            detected_language=stt_res.detected_language
        )

        raw_response_text = pipeline_output.get("response", "")

        # Step 4: Language Alignment for TTS (Translate if English response into Indic voice)
        spoken_text = language_router.align_language_for_tts(
            text=raw_response_text,
            detected_language=stt_res.detected_language,
            customer_preference=pipeline_output.get("customer_preference", {}).get("preferred_language")
        )

        # Step 5: Text-to-Speech synthesis
        tts_res = tts_service.synthesize(
            text=spoken_text,
            target_language=stt_res.detected_language
        )

        return VoiceTurnResult(
            stt=stt_res,
            tts=tts_res,
            pipeline_response=pipeline_output,
            fallback_triggered=False
        )


# Instantiate global voice handler
voice_handler = VoiceHandler()

