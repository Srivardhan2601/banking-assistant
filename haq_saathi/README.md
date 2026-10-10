# Haq Saathi (హక్ సాథీ • हक़ साथी • حق ساتھی)
### Voice-First Legal Rights Companion for Informal Workers in India

> **Hackathon Prototype** | Runs 100% offline with **Zero Paid Accounts** | Full end-to-end demo under 2 minutes.

---

## 📌 Reasonable Assumptions Made
1. **Target User Profile**: Informal workers (domestic maids, delivery partners, construction masons, auto drivers) who have low textual literacy and rely on spoken voice in **Telugu**, **Hindi**, or **Urdu**.
2. **Offline-First Resilience**: An offline deterministic synthesis engine is bundled by default so the demo is 100% immune to API rate limits, Wi-Fi drops, or billing thresholds during live judging. Cloud LLMs (Groq Llama 3.3, Claude, OpenAI) can be enabled via single environment variable toggle.
3. **Legal Disclaimer**: Haq Saathi acts strictly as an informational and draft-preparation assistant, never dispensing legal counsel or inventing unverified rupee penalties/statutory sections. All rights are strictly grounded in [`knowledge/rights.json`](file:///c:/Users/sriva/OneDrive/Documents/BANKING%20ASSISTANT/haq_saathi/knowledge/rights.json).
4. **Safety & Zero PII Extraction**: No Aadhaar, PAN, bank account numbers, or private home addresses are ever collected or stored.
5. **Geographic Jurisdiction**: Seeded with 8 realistic official labour offices covering Telangana districts with automated state-level fallback.

---

## 🚀 Quick Start (Max 3 Commands)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Test Suite
```bash
python -m unittest discover -s haq_saathi/tests -v
```

### 3. Launch App
```bash
python -m uvicorn haq_saathi.backend.main:app --host 127.0.0.1 --port 8000 --reload
```
*(Or simply double-click `run.bat` on Windows)*

👉 Open in your browser: **`http://127.0.0.1:8000`**

---

## 🏗️ Architecture Diagram

```
                             +------------------------+
                             |   Informal Worker      |
                             |   (Telugu/Hindi/Urdu)  |
                             +-----------+------------+
                                         |
                                         v
                             [ Web Speech API (STT) ]
                         [ or 1-Tap Quick Problem Cards ]
                                         |
                                         v
+-------------------------------------------------------------------------------+
|                             HAQ SAATHI BACKEND                                |
|                                                                               |
|  [ 1. Safety & Ethics Layer ]                                                 |
|      - Checks Danger Signals (Violence/Bonded Labour/Child Labour -> 112/181) |
|      - PII Sanitization (Redacts Aadhaar, PAN, Credit Cards)                  |
|      - Spoken Transparency Consent                                            |
|                                                                               |
|  [ 2. State Machine (8 States, <= 4 Questions Max) ]                          |
|      GREETING -> UNDERSTAND -> COLLECT_FIELDS (Category, Employer, Period,   |
|      Amount/District) -> EXPLAIN_RIGHTS -> CONFIRM -> GENERATE -> ROUTE -> DONE|
|                                                                               |
|  [ 3. Grounded Retrieval ] <--------> [ knowledge/rights.json ]                |
|      - Payment of Wages Act 1936                                              |
|      - Minimum Wages Act 1948                                                 |
|      - Building & Other Construction Workers (BOCW) Act 1996                  |
|      - Social Security Code 2020 (Gig/Platform Workers)                       |
|                                                                               |
|  [ 4. Labour Jurisdiction Router ] <--> [ data/labour_offices.json ]          |
|      - Matches district (Hyd, RR, Medchal, Warangal, etc.) + category         |
|      - State Labour Commissionerate Fallback                                  |
|                                                                               |
|  [ 5. Multilingual PDF Generator (ReportLab) ]                                |
|      - Google Noto Sans Telugu, Devanagari, & Arabic Unicode Fonts            |
|      - Urdu Bidirectional (BiDi) + Arabic Reshaper Support                    |
|      - Single-Page Official Legal Grievance Petition                          |
|                                                                               |
|  [ 6. SQLite Database (haq_saathi.db) ]                                        |
|      - Stores grievance records without sensitive personal data               |
+-------------------------------------------------------------------------------+
                                         |
                                         v
                             [ Web Speech API (TTS) ]
                                         |
                                         v
                         +-------------------------------+
                         |      Worker Mobile UI         |
                         |  - Spoken Answer (<40 words)  |
                         |  - Download Grievance PDF     |
                         |  - Direct Call Labour Office  |
                         |  - 4-Step Pictorial Checklist |
                         +-------------------------------+
```

---

## ⚙️ Environment Configuration (`.env`)

| Variable | Default | Description |
| :--- | :--- | :--- |
| `LLM_PROVIDER` | `offline` | Engine mode: `offline`, `groq`, `anthropic`, or `openai` |
| `GROQ_API_KEY` | *(empty)* | Optional API Key for Llama 3.3 70B Versatile |
| `ANTHROPIC_API_KEY` | *(empty)* | Optional API Key for Claude 3.5 Sonnet |
| `OPENAI_API_KEY` | *(empty)* | Optional API Key for GPT-4o |
| `HOST` | `127.0.0.1` | Local server bind address |
| `PORT` | `8000` | Local server port |

---

## ⏱️ 90-Second Hackathon Live Demo Script

### Scenario: Domestic Maid in Banjara Hills with 3 Months Unpaid Wages (Telugu)

| Time | Action | What to Say / Click | What Judges See & Hear |
| :--- | :--- | :--- | :--- |
| **0:00 - 0:15** | Open app & Show Zero Barriers | Tap the top right **"⚡ డెమో సినారియోలు"** menu or tap the **"తెలుగు"** language chip. | High-contrast mobile interface with **One Huge Microphone Button**, privacy consent strip, and 4 quick problem cards. Spoken welcome in Telugu. |
| **0:15 - 0:35** | Speak / Click Problem | Tap **"💰 జీతం రాలేదు"** card or hold Mic and say:<br> *"గత మూడు నెలలుగా యజమాని జీతం ఇవ్వలేదు, మొత్తం 18000 రూపాయలు బాకీ ఉంది."* | Live speech transcript appears. Audio wave pulses. Assistant speaks aloud: *"అయ్యో, జీతం రాకపోవడం చాలా కష్టం. మీ యజమాని లేదా కాంట్రాక్టర్ పేరు మరియు జిల్లా ఏమిటి?"* (<30 words, simple spoken words). |
| **0:35 - 0:50** | Answer Follow-up | Tap suggested chip or speak:<br> *"యజమాని పేరు రావు గారు, బంజారాహిల్స్ హైదరాబాద్."* | State machine identifies Employer and Hyderabad district. Question count strictly <= 4. |
| **0:50 - 1:10** | Spoken Rights & Grounding | Assistant explains legal right: *"చట్టం ప్రకారం మీ వేతనం సకాలంలో పొందే పూర్తి హక్కు మీకు ఉంది. యజమాని అక్రమంగా జీతం నిలిపివేయడం నేరం. మేము హైదరాబాద్ లేబర్ ఆఫీసుకు ఫిర్యాదు పత్రం తయారు చేయమంటారా?"* | Click **"ఎందుకు ఈ సమాధానం? (Why this answer?)"** button to show judges the exact grounding in `knowledge/rights.json` (Payment of Wages Act). |
| **1:10 - 1:30** | One-Click Complaint & Routing | Tap **"అవును, ఫిర్యాదు చేయండి (Yes, File)"**. | Instant Generation:<br>1. **One-Page Official Complaint PDF** in Telugu + English Copy with proper Unicode glyphs.<br>2. **Office Card**: Deputy Commissioner of Labour, Hyderabad with one-tap `tel:` call button.<br>3. **Pictorial 4-Step Checklist**: Download PDF -> Visit Office -> Official Notice -> Dues Recovery. |

---

## 🛡️ Safety & Ethics Compliance
- **Violence / Trafficking / Child Labour Override**:
  If a worker mentions danger signals (e.g. *"నన్ను కొట్టారు, తాళం వేశారు"* or *"मारपीट"* or *"چھوٹے بچوں سے مزدوری"*), the normal complaint flow is immediately interrupted. An emergency modal opens directing the worker to **112 (Police ERSS)**, **181 (Women's Helpline)**, **1098 (Childline)**, and **1800-425-3525 (Telangana Labour Grievance)**.
- **PII Scrubbing**:
  Any input containing 12-digit Aadhaar numbers, 16-digit debit/credit card numbers, or PAN numbers is sanitized to `[REDACTED_ID]` before logging or state storage.

---

## 🔍 Known Limitations & Future Roadmap
1. **Dialect Nuance**: Local colloquial slang variations are normalized through keyword expansion; production version will integrate regional Indic Whisper fine-tuned models.
2. **WhatsApp / IVR Integration**: A sample Twilio voice/WhatsApp webhook endpoint is included at `/api/webhook/twilio` to power feature-phone IVR calling.
3. **Wage Slip OCR**: Future versions can accept photos of handwritten wage receipts or WhatsApp chat screenshots to auto-verify unpaid calculations.
