"""
FastAPI Application Entry Point for Haq Saathi.
Voice-First Legal Rights Companion for Informal Workers in India.
Provides chat engine, PDF downloads, rights catalog, office routing, and demo scenarios.
"""

import os
from pathlib import Path
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException, Query, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

from .models import ChatRequest, ChatResponse, ComplaintRecord
from .engine import engine, SESSIONS
from .database import db
from .pdf_generator import pdf_service
from .retrieval import retriever
from .router import router

app = FastAPI(
    title="Haq Saathi - Voice Legal Companion",
    description="Voice-first legal rights companion and grievance generator for informal workers in India.",
    version="1.0.0"
)

# Enable CORS for local development and web frontends
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"
PDF_DIR = Path(__file__).resolve().parent.parent / "generated_pdfs"


@app.post("/api/chat", response_model=ChatResponse)
async def chat_turn(req: ChatRequest):
    """
    Core conversation turn endpoint.
    Orchestrates safety checks, state transitions, rights retrieval,
    office routing, and generates under-40-words spoken audio reply.
    """
    try:
        response = engine.process_turn(req)
        return response
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Engine processing error: {str(e)}")


@app.get("/api/complaint/{complaint_id}")
async def get_complaint(complaint_id: str):
    """Retrieves structured complaint details from SQLite."""
    record = db.get_complaint(complaint_id)
    if not record:
        raise HTTPException(status_code=404, detail="Complaint record not found.")
    return record


@app.get("/api/complaint/{complaint_id}/pdf")
async def get_complaint_pdf(complaint_id: str, lang: Optional[str] = Query(default=None)):
    """
    Generates and downloads the official one-page complaint PDF.
    Supports Telugu, Hindi, Urdu, and English versions.
    """
    record = db.get_complaint(complaint_id)
    if not record:
        raise HTTPException(status_code=404, detail="Complaint record not found.")

    selected_lang = lang or record.get("language", "te-IN")
    lang_code = selected_lang[:2].upper()
    pdf_filename = f"Complaint_{complaint_id}_{lang_code}.pdf"
    pdf_path = PDF_DIR / pdf_filename

    # If file does not exist, generate it now
    if not pdf_path.exists():
        try:
            pdf_service.generate(record, lang=selected_lang)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to generate PDF: {str(e)}")

    if not pdf_path.exists():
        raise HTTPException(status_code=404, detail="PDF generation failed or file not found.")

    return FileResponse(
        path=str(pdf_path),
        media_type="application/pdf",
        filename=pdf_filename,
        headers={"Content-Disposition": f"attachment; filename={pdf_filename}"}
    )


@app.get("/api/offices")
async def get_labour_offices():
    """Lists all seeded Telangana labour jurisdiction offices."""
    return router.get_all_offices()


@app.get("/api/rights")
async def get_rights_catalog():
    """Lists all verified knowledge-base legal rights entries."""
    return retriever.get_all_rights()


@app.get("/api/scenarios")
async def get_demo_scenarios():
    """
    Returns 3 curated hackathon demo scenarios:
    1. Telugu Domestic Worker (3 months unpaid wages in Hyderabad)
    2. Hindi Delivery Rider (Pay below minimum wage in Warangal)
    3. Urdu Construction Labourer (Workplace injury in Rangareddy)
    """
    scenarios = [
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
            "initial_problem": "سلام علیکم، میں گچی باؤلی رنگاریڈی میں کنسٹرکشن سائٹ پر میسن کا کام کر رہا تھا۔ کام کے دوران اونچائی سے گرنے کی وجہ سے میرے ہاتھ میں فریکچر ہو گیا، ٹھیکیدار نے علاج کا خرچہ اور ایک مہینے کی اجرت 25000 روپے دینے سے انکار کر دیا۔",
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
    return scenarios


@app.post("/api/webhook/twilio")
async def twilio_webhook(request: Request):
    """
    Optional stretch endpoint: Twilio WhatsApp / Voice webhook.
    Accepts form data from Twilio and returns TwiML response.
    """
    form_data = await request.form()
    from_user = form_data.get("From", "voice_user")
    speech_result = form_data.get("SpeechResult") or form_data.get("Body") or "నమస్కారం, జీతం రాలేదు"
    
    # Process turn with same engine
    req = ChatRequest(
        session_id=f"twilio_{from_user}",
        user_text=speech_result,
        language="te-IN"
    )
    res = engine.process_turn(req)
    
    # Return simple TwiML Voice XML
    twiml_response = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say language="te-IN">{res.reply_text}</Say>
    <Gather input="speech" language="te-IN" timeout="5" />
</Response>"""
    return Response(content=twiml_response, media_type="application/xml")


# Mount Frontend Static Assets
if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

    @app.get("/", response_class=HTMLResponse)
    async def serve_index():
        index_file = FRONTEND_DIR / "index.html"
        if index_file.exists():
            return HTMLResponse(content=index_file.read_text(encoding="utf-8"))
        return HTMLResponse("<h2>Frontend is loading...</h2>")
else:
    @app.get("/")
    async def index_placeholder():
        return {"status": "ok", "message": "Haq Saathi API is active"}
