"""
FastAPI Server for AI Banking Support Assistant.
Provides endpoints for text chat, voice processing, customer memory inspection,
and serves the interactive judge demo dashboard.
"""

from pathlib import Path
from typing import Optional, Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from app.orchestrator import orchestrator
from app.voice import voice_handler, AudioInputPayload
from app.data import db
from app.memory import hindsight

app = FastAPI(
    title="AI Banking Support",
    description="Compliant AI Support Agent for Financial Services with Hindsight Cloud Memory & Voice",
    version="1.0.0"
)

WEB_DIR = Path(__file__).resolve().parent / "web"


# =============================================================================
# Request / Response Schemas
# =============================================================================

class ChatRequest(BaseModel):
    customer_id: str = Field(..., description="Target customer ID (e.g. CUST-1001)")
    message: str = Field(..., description="Customer message text")
    channel: str = Field(default="text", description="'text' or 'voice'")
    detected_language: str = Field(default="en-IN", description="Language code")


class VoiceRequest(BaseModel):
    customer_id: str
    client_transcript: Optional[str] = None
    client_lang: Optional[str] = "en-IN"
    audio_base64: Optional[str] = None
    audio_mime: Optional[str] = "audio/webm"


# =============================================================================
# REST Endpoints
# =============================================================================

@app.get("/")
def get_root():
    """Serves the interactive web demo dashboard."""
    index_file = WEB_DIR / "index.html"
    if not index_file.exists():
        raise HTTPException(status_code=404, detail="Web interface files not found.")
    return FileResponse(index_file)


@app.post("/api/chat")
def handle_chat(req: ChatRequest) -> Dict[str, Any]:
    """Processes customer text inquiries through the full compliant pipeline."""
    try:
        output = orchestrator.process_message(
            customer_id=req.customer_id,
            customer_message=req.message,
            channel=req.channel,
            detected_language=req.detected_language
        )
        return output
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/voice/process")
def handle_voice(req: VoiceRequest) -> Dict[str, Any]:
    """Processes speech input via the modular voice wrapper."""
    try:
        payload = AudioInputPayload(
            customer_id=req.customer_id,
            audio_base64=req.audio_base64,
            audio_mime=req.audio_mime or "audio/webm",
            language_hint=req.client_lang
        )
        turn_res = voice_handler.handle_voice_turn(
            audio_payload=payload,
            client_transcript=req.client_transcript,
            client_lang=req.client_lang
        )
        return turn_res.model_dump()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/voice/tts")
def stream_tts(text: str, lang: str = "en-IN"):
    """Streams synthesized speech audio (MP3) for any text and language across all 8 Indic/global languages."""
    from fastapi.responses import Response
    from app.voice.tts_adapter import tts_service
    audio_bytes = tts_service.get_audio_bytes(text, lang)
    if not audio_bytes:
        raise HTTPException(status_code=500, detail="TTS synthesis failed or unavailable")
    return Response(content=audio_bytes, media_type="audio/mp3")


@app.get("/api/customers")
def list_customers():
    """Lists all mock customer personas with their metadata and test scenarios."""
    customers = db.list_all_customers()
    summary = []
    for c in customers:
        summary.append({
            "customer_id": c["customer_id"],
            "customer_name": c["customer_name"],
            "language": c.get("contact", {}).get("preferred_language", "en-IN"),
            "channel": c.get("contact", {}).get("preferred_channel", "text"),
            "fraud_alert": c.get("fraud_alert_active", False),
            "account_count": len(c.get("accounts", [])),
            "loan_count": len(c.get("loans", [])),
            "ticket_count": len(c.get("support_tickets", []))
        })
    return summary


@app.get("/api/customers/{customer_id}")
def get_customer_details(customer_id: str):
    """Returns raw customer record plus live Hindsight Cloud memory bank."""
    cust = db.get_customer(customer_id)
    if not cust:
        raise HTTPException(status_code=404, detail="Customer not found.")
    memory = hindsight.recall(customer_id, query="")
    return {
        "profile": cust,
        "memory_bank": memory.model_dump()
    }


@app.get("/api/schemes")
def get_schemes():
    """Returns authoritative banking schemes knowledge catalog."""
    return db.get_schemes_catalog()


@app.post("/api/reset")
def reset_memory():
    """Resets Hindsight memory banks to initial state for demo repeatability."""
    hindsight.reset_to_defaults()
    return {"status": "SUCCESS", "message": "Hindsight memory banks reset to clean state."}


# Mount static assets for styles and client scripts
if WEB_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(WEB_DIR)), name="static")
