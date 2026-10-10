"""
Core Conversation & Workflow Orchestrator for Haq Saathi.
Combines State Machine, Safety Overrides, Retrieval, LLM, Router, and SQLite DB.
"""

import uuid
import datetime
from typing import Dict, Any, Optional, List

from .models import (
    ChatRequest, ChatResponse, StateEnum, IntentEnum, WorkerCategory,
    RightsSummary, OfficeDetails, ComplaintRecord
)
from .safety import check_danger_signals, get_danger_response, get_spoken_consent, sanitize_input
from .intent_classifier import classify_intent, extract_worker_category, extract_key_entities
from .retrieval import retriever
from .router import router
from .state_machine import state_machine, QUICK_OPTIONS
from .llm_adapter import llm_adapter
from .database import db
from .pdf_generator import pdf_service


# In-memory sessions store with session IDs
SESSIONS: Dict[str, Dict[str, Any]] = {}


def get_or_create_session(session_id: str, lang: str = "te-IN") -> Dict[str, Any]:
    if session_id not in SESSIONS:
        sess = state_machine.get_initial_session()
        sess["session_id"] = session_id
        sess["language"] = lang
        sess["history"] = []
        SESSIONS[session_id] = sess
    else:
        if lang:
            SESSIONS[session_id]["language"] = lang
    return SESSIONS[session_id]


def build_next_steps_checklist(office: OfficeDetails, amount: str, lang: str = "te-IN") -> List[Dict[str, str]]:
    """Builds 4 plain-language pictorial next-steps checklist."""
    lang_code = lang.split("-")[0] if "-" in lang else "en"
    
    checklists = {
        "te": [
            {
                "step": "1",
                "icon": "📄",
                "title": "ఫిర్యాదు పత్రం (PDF) డౌన్‌లోడ్ చేసుకోండి",
                "desc": "కింద ఉన్న బటన్ ద్వారా మీ ఫిర్యాదు కాపీని సేవ్ చేసుకోండి లేదా ప్రింట్ తీయండి."
            },
            {
                "step": "2",
                "icon": "🏢",
                "title": f"{office.district} లేబర్ ఆఫీసును సంప్రదించండి",
                "desc": f"కార్యాలయం: {office.address} ({office.working_hours}). ఫోన్: {office.phone}"
            },
            {
                "step": "3",
                "icon": "⚖️",
                "title": "యజమానికి అధికారిక నోటీసు",
                "desc": f"లేబర్ అధికారి యజమానికి నోటీసు జారీ చేసి విచారణకు పిలుస్తారు."
            },
            {
                "step": "4",
                "icon": "💰",
                "title": f"బాకీ ఉన్న {amount} వసూలు",
                "desc": "అధికారి సమక్షంలో రాజీ లేదా వేతన రికవరీ ఉత్తర్వు ద్వారా మీ కూలి మీకు అందుతుంది."
            }
        ],
        "hi": [
            {
                "step": "1",
                "icon": "📄",
                "title": "शिकायत पत्र (PDF) डाउनलोड करें",
                "desc": "नीचे दिए गए बटन से अपने शिकायत पत्र की प्रति सुरक्षित करें।"
            },
            {
                "step": "2",
                "icon": "🏢",
                "title": f"{office.district} श्रम कार्यालय में जमा करें",
                "desc": f"पता: {office.address}। फोन: {office.phone} (समय: {office.working_hours})।"
            },
            {
                "step": "3",
                "icon": "⚖️",
                "title": "नियोक्ता को कानूनी नोटिस",
                "desc": "श्रम अधिकारी नियोक्ता/ठेकेदार को समन भेजकर तलब करेंगे।"
            },
            {
                "step": "4",
                "icon": "💰",
                "title": f"बकाया {amount} की वसूली",
                "desc": "अधिकारी की मध्यस्थता से आपकी बकाया मजदूरी का भुगतान सुनिश्चित कराया जाएगा।"
            }
        ],
        "ur": [
            {
                "step": "1",
                "icon": "📄",
                "title": "شکایتی خط (PDF) محفوظ کریں",
                "desc": "نیچے دیے گئے بٹن سے اپنے باقاعدہ شکایتی خط کا پرنٹ یا پی ڈی ایف لیں۔"
            },
            {
                "step": "2",
                "icon": "🏢",
                "title": f"{office.district} لیبر آفس میں پیش کریں",
                "desc": f"پتہ: {office.address}۔ فون: {office.phone}۔"
            },
            {
                "step": "3",
                "icon": "⚖️",
                "title": "مالک یا ٹھیکیدار کو نوٹس",
                "desc": "لیبر آفیسر مالک کو طلب کر کے تحریری جواب طلب کریں گے۔"
            },
            {
                "step": "4",
                "icon": "💰",
                "title": f"واجب الادا {amount} کی واپسی",
                "desc": "باضابطہ قانونی تصفیے کے ذریعے آپ کی اجرت آپ کو دلوائی جائے گی۔"
            }
        ],
        "en": [
            {
                "step": "1",
                "icon": "📄",
                "title": "Download Petition Draft (PDF)",
                "desc": "Save or print your drafted wage recovery grievance letter below."
            },
            {
                "step": "2",
                "icon": "🏢",
                "title": f"Submit to {office.district} Labour Office",
                "desc": f"Location: {office.address}. Contact: {office.phone}."
            },
            {
                "step": "3",
                "icon": "⚖️",
                "title": "Official Summons to Employer",
                "desc": "The Conciliation Officer issues notice to the employer to appear with wage records."
            },
            {
                "step": "4",
                "icon": "💰",
                "title": f"Recovery of Dues ({amount})",
                "desc": "Earned remuneration is disbursed under statutory conciliation settlement."
            }
        ]
    }
    return checklists.get(lang_code, checklists["en"])


class HaqSaathiEngine:
    """End-to-end conversation processor."""

    def process_turn(self, req: ChatRequest) -> ChatResponse:
        session = get_or_create_session(req.session_id, req.language)
        sanitized_input = sanitize_input(req.user_text)

        # 1. Safety & Danger Check (Zero Tolerance for violence/trafficking/child labour)
        danger_check = check_danger_signals(sanitized_input)
        if danger_check:
            danger_reply = get_danger_response(req.language)
            session["state"] = StateEnum.DANGER_OVERRIDE
            session["danger_triggered"] = True

            return ChatResponse(
                session_id=req.session_id,
                reply_text=danger_reply,
                reply_language=req.language,
                current_state=StateEnum.DANGER_OVERRIDE,
                next_action="EMERGENCY_REFERRAL",
                collected_fields=session["collected_fields"],
                suggested_options=["112 కి కాల్ చేయండి (Call 112)", "లేబర్ హెల్ప్‌లైన్ (1800-425-3525)"],
                danger_flag=True,
                danger_message="Immediate emergency assistance required.",
                emergency_contacts=danger_check.get("emergency_contacts")
            )

        # 2. Extract Entities & Classify Intent
        extracted = extract_key_entities(sanitized_input)
        if not session.get("intent") or session.get("intent") == IntentEnum.OTHER:
            detected_intent = classify_intent(sanitized_input)
            if detected_intent != IntentEnum.OTHER:
                session["intent"] = detected_intent

        detected_category = extract_worker_category(sanitized_input)
        if detected_category != WorkerCategory.INFORMAL_WORKER:
            extracted["worker_category"] = detected_category.value

        # Check if user mentioned employer name specifically
        if "employer_name" not in session["collected_fields"] or not session["collected_fields"]["employer_name"]:
            # If current prompt was asking for employer name, take text directly
            prev_action = session.get("last_action", "")
            if "EMPLOYER_NAME" in prev_action:
                clean_name = sanitized_input.strip()
                # filter out generic phrases
                if clean_name and len(clean_name) > 2 and clean_name.lower() not in ["yes", "no", "ok", "సరే", "పేరు"]:
                    extracted["employer_name"] = clean_name

        # If user spoke their own name
        prev_action = session.get("last_action", "")
        if "WORKER_NAME" in prev_action:
            extracted["worker_name"] = sanitized_input.strip()

        # Update session collected fields
        for k, v in extracted.items():
            if v:
                session["collected_fields"][k] = v

        # 3. Retrieve Rights
        worker_cat = session["collected_fields"].get("worker_category") or "informal_worker"
        current_intent = session.get("intent", IntentEnum.UNPAID_WAGES)
        rights_summary = retriever.retrieve(current_intent, worker_cat, sanitized_input, req.language)
        if rights_summary:
            session["rights_retrieved_id"] = rights_summary.id

        # 4. Route Labour Office
        district = session["collected_fields"].get("district")
        routed_office = router.route_complaint(district, worker_cat)

        # 5. State Machine Transition
        next_state, next_action, suggested_opts, next_field = state_machine.transition(
            session=session,
            user_text=sanitized_input,
            extracted_entities=extracted,
            is_danger=False
        )
        session["last_action"] = next_action

        # 6. Generate Complaint if State Transitioned to ROUTE or DONE
        complaint_id = session.get("complaint_id")
        checklist = None

        if next_state in [StateEnum.GENERATE_COMPLAINT, StateEnum.ROUTE, StateEnum.DONE]:
            if not complaint_id:
                complaint_id = f"HAQ-{datetime.datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
                session["complaint_id"] = complaint_id

                amount = session["collected_fields"].get("amount_owed") or "₹15,000 [అంచనా బాకీ]"
                unpaid_p = session["collected_fields"].get("months_unpaid") or "3 నెలలు"
                emp_name = session["collected_fields"].get("employer_name") or "Concerned Contractor / Employer"
                dist_val = session["collected_fields"].get("district") or "Hyderabad"
                w_name = session["collected_fields"].get("worker_name") or "Aggrieved Worker"

                # Persist to SQLite
                record = ComplaintRecord(
                    complaint_id=complaint_id,
                    created_at=datetime.date.today().isoformat(),
                    language=req.language,
                    worker_name=w_name,
                    worker_category=worker_cat,
                    employer_name=emp_name,
                    work_location=f"{dist_val}, Telangana",
                    district=dist_val,
                    unpaid_period=unpaid_p,
                    amount_owed=amount,
                    description=f"Grievance filed for {unpaid_p} of withheld remuneration under statutory protections.",
                    desired_relief=f"Summon employer and recover unpaid dues totaling {amount}.",
                    rights_violated=rights_summary.title if rights_summary else "Timely Payment of Wages",
                    source_citation=rights_summary.source_name if rights_summary else "Payment of Wages Act",
                    routed_office_id=routed_office.office_id,
                    routed_office_name=routed_office.office_name,
                    routed_office_address=routed_office.address,
                    phone=session["collected_fields"].get("optional_phone")
                )
                db.save_complaint(record)

                # Pre-generate localized PDF
                try:
                    pdf_service.generate(record.model_dump(), lang=req.language)
                    pdf_service.generate(record.model_dump(), lang="en-IN")
                except Exception as e:
                    print(f"[Engine] PDF pre-generate notice: {e}")

            amount_val = session["collected_fields"].get("amount_owed") or "₹15,000"
            checklist = build_next_steps_checklist(routed_office, amount_val, req.language)

        # 7. Generate Spoken Language Response (Under 40 words, simple spoken words)
        spoken_reply = llm_adapter.generate_spoken_reply(
            current_state=next_state,
            user_text=sanitized_input,
            lang=req.language,
            collected=session["collected_fields"],
            rights=rights_summary,
            office=routed_office,
            next_field_to_ask=next_field
        )

        return ChatResponse(
            session_id=req.session_id,
            reply_text=spoken_reply,
            reply_language=req.language,
            current_state=next_state,
            next_action=next_action,
            collected_fields=session["collected_fields"],
            suggested_options=suggested_opts,
            rights_summary=rights_summary,
            office_details=routed_office,
            complaint_id=complaint_id,
            checklist=checklist,
            danger_flag=False
        )


engine = HaqSaathiEngine()
