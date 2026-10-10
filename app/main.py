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
@app.get("/api/index")
@app.get("/api/index.py")
def get_root():
    """Serves the interactive web demo dashboard."""
    index_file = WEB_DIR / "index.html"
    if not index_file.exists():
        raise HTTPException(status_code=404, detail="Web interface files not found.")
    return FileResponse(index_file)


@app.get("/static/{file_path:path}")
def get_static_file(file_path: str):
    """Explicit static asset route for serverless hosting."""
    target = WEB_DIR / file_path
    if not target.exists() or not target.is_file():
        raise HTTPException(status_code=404, detail="Asset not found")
    return FileResponse(target)


class LoginRequest(BaseModel):
    account_number: str = Field(..., description="Customer primary account number or customer ID")
    pin: str = Field(default="1234", description="4-digit security PIN")


@app.post("/api/auth/login")
def login(req: LoginRequest) -> Dict[str, Any]:
    """Authenticates a customer using their primary account number and 4-digit PIN."""
    acc_clean = req.account_number.strip().upper()
    pin_clean = req.pin.strip()

    if len(pin_clean) != 4 or not pin_clean.isdigit():
        raise HTTPException(status_code=400, detail="Security PIN must be exactly 4 numeric digits.")

    customers = db.list_all_customers()
    matched = None

    for c in customers:
        c_acc = c.get("accounts", [{}])[0].get("account_number", "").upper()
        c_id = c.get("customer_id", "").upper()
        if acc_clean in (c_acc, c_acc.replace("AC-", ""), c_id, c_id.replace("CUST-", "")):
            matched = c
            break

    if not matched:
        # Convenience matching for partial input
        if "1005" in acc_clean or "5002" in acc_clean or "ROHAN" in acc_clean:
            matched = db.get_customer("CUST-1005")
        elif "1001" in acc_clean or "1002" in acc_clean or "AARAV" in acc_clean:
            matched = db.get_customer("CUST-1001")
        elif "1002" in acc_clean or "2009" in acc_clean or "PRIYA" in acc_clean:
            matched = db.get_customer("CUST-1002")
        elif "1003" in acc_clean or "3004" in acc_clean or "VIKRAM" in acc_clean:
            matched = db.get_customer("CUST-1003")
        elif "1004" in acc_clean or "4001" in acc_clean or "SUNITA" in acc_clean:
            matched = db.get_customer("CUST-1004")
        elif "1006" in acc_clean or "6003" in acc_clean or "ANANYA" in acc_clean:
            matched = db.get_customer("CUST-1006")
        elif "1007" in acc_clean or "7001" in acc_clean or "RAJESHWARI" in acc_clean:
            matched = db.get_customer("CUST-1007")
        elif "1008" in acc_clean or "8002" in acc_clean or "KAVITA" in acc_clean:
            matched = db.get_customer("CUST-1008")
        elif "1009" in acc_clean or "9004" in acc_clean or "FARHAN" in acc_clean:
            matched = db.get_customer("CUST-1009")
        elif "1010" in acc_clean or "10109" in acc_clean or "MEERA" in acc_clean:
            matched = db.get_customer("CUST-1010")

    if not matched:
        raise HTTPException(
            status_code=401,
            detail="Account number not recognized. Please use a valid primary account (e.g. AC-5002938491) or select a quick persona."
        )

    # Verify 4-digit security PIN (Demo accounts use default PIN 1234)
    if pin_clean != "1234":
        raise HTTPException(
            status_code=401,
            detail="Incorrect 4-digit security PIN. Please enter your valid PIN (Default PIN: 1234)."
        )

    primary_acc = matched.get("accounts", [{}])[0]
    cust_obj = {
        "id": matched["customer_id"],
        "name": matched["customer_name"],
        "account_number": primary_acc.get("account_number", "AC-5002938491"),
        "account_type": primary_acc.get("account_type", "Advantage Savings"),
        "balance_inr": primary_acc.get("balance_inr", 67000.0),
        "home_branch": matched.get("contact", {}).get("home_branch", "Cyber City, Gurugram"),
    }
    return {
        "status": "SUCCESS",
        "success": True,
        "customer": cust_obj,
        "customer_id": matched["customer_id"],
        "customer_name": matched["customer_name"],
        "account_number": primary_acc.get("account_number", "AC-5002938491"),
        "token": f"sess_tok_{matched['customer_id']}_secure"
    }


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


@app.get("/api/hindsight/status")
def get_hindsight_status():
    """Returns live connection status for Hindsight Cloud Memory."""
    return {
        "status": "ONLINE" if hindsight.is_live else "FALLBACK",
        "is_live": hindsight.is_live,
        "endpoint": hindsight.endpoint,
        "agent_bank_id": hindsight.agent_bank_id,
        "api_key_masked": f"{hindsight.api_key[:8]}...{hindsight.api_key[-6:]}" if hindsight.api_key else None
    }


@app.post("/api/reset")
def reset_memory():
    """Resets Hindsight memory banks to initial state for demo repeatability."""
    hindsight.reset_to_defaults()
    return {"status": "SUCCESS", "message": "Hindsight memory banks reset to clean state."}


# =============================================================================
# Haq Saathi Integration Endpoints (Worker Rights & Grievance Companion)
# =============================================================================

from haq_saathi.backend.engine import engine as haq_engine
from haq_saathi.backend.models import ChatRequest as HaqChatRequest, ChatResponse as HaqChatResponse
from haq_saathi.backend.database import db as haq_db
from haq_saathi.backend.pdf_generator import pdf_service as haq_pdf_service
from haq_saathi.backend.retrieval import retriever as haq_retriever
from haq_saathi.backend.router import router as haq_router

HAQ_PDF_DIR = Path(__file__).resolve().parent.parent / "haq_saathi" / "generated_pdfs"


@app.post("/api/haq/chat", response_model=HaqChatResponse)
def handle_haq_chat(req: HaqChatRequest):
    """Processes worker voice/text inquiries through Haq Saathi conversational rights engine."""
    try:
        return haq_engine.process_turn(req)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/haq/complaint/{complaint_id}")
def get_haq_complaint(complaint_id: str):
    """Retrieves structured complaint record."""
    record = haq_db.get_complaint(complaint_id)
    if not record:
        raise HTTPException(status_code=404, detail="Complaint record not found.")
    return record


@app.get("/api/haq/complaint/{complaint_id}/pdf")
@app.get("/api/complaint/{complaint_id}/pdf")
def get_haq_complaint_pdf(complaint_id: str, lang: Optional[str] = None):
    """Generates and downloads the official one-page grievance petition PDF."""
    record = haq_db.get_complaint(complaint_id)
    if not record:
        raise HTTPException(status_code=404, detail="Complaint record not found.")

    selected_lang = lang or record.get("language", "te-IN")
    lang_code = selected_lang[:2].upper()
    pdf_filename = f"Complaint_{complaint_id}_{lang_code}.pdf"
    pdf_path = HAQ_PDF_DIR / pdf_filename

    if not pdf_path.exists():
        try:
            haq_pdf_service.generate(record, lang=selected_lang)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to generate PDF: {str(e)}")

    if not pdf_path.exists():
        raise HTTPException(status_code=404, detail="PDF not found.")

    return FileResponse(
        path=str(pdf_path),
        media_type="application/pdf",
        filename=pdf_filename,
        headers={"Content-Disposition": f"attachment; filename={pdf_filename}"}
    )


@app.get("/api/haq/offices")
def get_haq_offices():
    """Lists verified labour jurisdiction offices."""
    return haq_router.get_all_offices()


@app.get("/api/haq/rights")
def get_haq_rights():
    """Lists legal rights catalog."""
    return haq_retriever.list_all()


@app.get("/api/haq/scenarios")
def get_haq_scenarios():
    """Returns curated Haq Saathi demo scenarios for informal workers."""
    return [
        {
            "id": "scenario_te_domestic",
            "title": "లక్ష్మి - ఇళ్ల పని మనిషి (తెలుగు)",
            "subtitle": "గృహ కార్మికురాలు • 3 నెలల జీతం బాకీ • హైదరాబాద్",
            "worker_name": "లక్ష్మి (Lakshmi)",
            "worker_category": "domestic_worker",
            "language": "te-IN",
            "district": "Hyderabad",
            "initial_problem": "నమస్కారం, నేను బంజారాహిల్స్‌లో ఒకరి ఇంట్లో వంట పని మరియు శుభ్రం చేసే పని చేస్తున్నాను. గత 3 నెలలుగా యజమాని జీతం ఇవ్వలేదు, అడిగితే తీసేస్తానని బెదిరిస్తున్నారు. మొత్తం 18,000 రూపాయలు రావాలి.",
            "steps": [
                {
                    "user_text": "గత మూడు నెలలుగా యజమాని జీతం ఇవ్వలేదు, మొత్తం 18000 రూపాయలు బాకీ ఉంది.",
                    "notes": "State transitions to DETAILS; identifies domestic worker & unpaid wages."
                },
                {
                    "user_text": "యజమాని పేరు రావు గారు, బంజారాహిల్స్ హైదరాబాద్.",
                    "notes": "Collects employer details and confirms district."
                },
                {
                    "user_text": "అవును, ఫిర్యాదు పత్రం తయారు చేసి లేబర్ ఆఫీసు సమాచారం ఇవ్వండి.",
                    "notes": "Transitions to EXPLAIN_RIGHTS & GENERATE_COMPLAINT."
                }
            ]
        },
        {
            "id": "scenario_hi_delivery",
            "title": "अमित - डिलीवरी राइडर (हिन्दी)",
            "subtitle": "गिग वर्कर • न्यूनतम वेतन से कम व प्रोत्साहन राशि बकाया • वारंगल",
            "worker_name": "अमित (Amit)",
            "worker_category": "delivery_rider",
            "language": "hi-IN",
            "district": "Warangal",
            "initial_problem": "नमस्ते, मैं वारंगल में फूड डिलीवरी का काम करता हूं। कंपनी ने पिछले दो महीनों से तय न्यूनतम गारंटी और इंसेंटिव के 9500 रुपये रोक रखे हैं।",
            "steps": [
                {
                    "user_text": "कंपनी ने दो महीनों से डिलीवरी का 9500 रुपया नहीं दिया है और तय न्यूनतम दर से बहुत कम दे रहे हैं।",
                    "notes": "Identifies delivery rider category and wage grievance."
                },
                {
                    "user_text": "कंपनी का नाम क्विक डिलीवरी हब, वारंगल हनमकोंडा।",
                    "notes": "Captures employer/hub and district."
                },
                {
                    "user_text": "हाँ, कृपया लेबर ऑफिस के लिए आधिकारिक शिकायत पत्र बना दें।",
                    "notes": "Generates complaint and routes to Warangal Labour Office."
                }
            ]
        },
        {
            "id": "scenario_ur_construction",
            "title": "محمد راشد - عمارت ساز مزدور (اردو)",
            "subtitle": "تعمیراتی مزدور • کام پر چوٹ اور علاج کے اخراجات • رنگاریڈی",
            "worker_name": "محمد راشد (Mohammed Rashid)",
            "worker_category": "construction_worker",
            "language": "ur-IN",
            "district": "Rangareddy",
            "initial_problem": "سلام علیکم، میں گچی باؤلی رنگاریڈی میں کنسٹرکشن سائٹ پر میسن کا کام کر رہا تھا۔ کام کے دوران اونچائی سے گرنے کی وجہ سے میرے ہاتھ میں فریکచర్ ہو گیا، ٹھیکیدار نے علاج کا خرچہ اور ایک مہینے کی اجرت 25000 روپے دینے سے انکار کر دیا۔",
            "steps": [
                {
                    "user_text": "سائٹ پر کام کے دوران چوٹ لگی، ٹھیکیدار علاج اور 25000 روپے کی مزدوری نہیں دے رہا ہے۔",
                    "notes": "Identifies construction worker and injury compensation rights under BOCW."
                },
                {
                    "user_text": "ٹھیکیدار کا نام کریم بھائی کنسٹرکشن ہے، گچی باؤلی رنگاریڈی۔",
                    "notes": "Captures employer and Rangareddy jurisdiction."
                },
                {
                    "user_text": "جی ہاں، مجھے لیبر ویلفیئر بورڈ کے لیے شکایت کا خط تیار کر کے دیجیے۔",
                    "notes": "Generates complaint petition with BOCW compensation citation."
                }
            ]
        }
    ]


# Mount static assets for styles and client scripts
if WEB_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(WEB_DIR)), name="static")

