"""
Safety, Ethics, Consent, and Danger-Signal Override Layer for Haq Saathi.
Ensures zero legal malpractice, zero sensitive data extraction, and immediate emergency intervention.
"""

import re
from typing import Optional, Dict, Any, List

DANGER_KEYWORDS = {
    "violence": [
        "beat", "beaten", "hit", "attack", "kill", "threat", "violence", "blood",
        "కొట్టారు", "దాడి", "చంపేస్తా", "రక్తం", "గాయపరిచారు", "భయపెడుతున్నారు",
        "मारा", "पीटा", "हमला", "जान से मारने", "खून", "धमकी", "हिंसा",
        "مارا", "پیٹا", "حملہ", "خون", "دھمکی", "جان کا خطرہ"
    ],
    "bonded_labour": [
        "locked", "not allowed to leave", "prisoner", "bonded", "trap", "slave", "passport taken",
        "బయటకు వెళ్లనివ్వడం లేదు", "బంధించారు", "తాళం వేశారు", "వెట్టి చాకిరీ", "బానిస",
        "बंद कर रखा है", "बाहर नहीं जाने दे रहे", "बंधक", "गुलाम", "बंधुआ मजदूरी",
        "بند کر رکھا ہے", "باہر نہیں جانے دیتے", "یرغمال", "بندھوا مزدوری", "غلام"
    ],
    "trafficking": [
        "trafficking", "sold", "smuggled", "kidnap",
        "అమ్మేశారు", "మోసం చేసి తీసుకొచ్చారు", "కిడ్నాప్",
        "बेच दिया", "तस्करी", "धोखे से ले आए", "अपहरण",
        "بیچ دیا", "اسمگلنگ", "اغوا"
    ],
    "child_labour": [
        "child labour", "minor", "child working", "under 14", "small kid",
        "చిన్న పిల్లలు", "మైనర్", "పిల్లలతో పని",
        "बाल मजदूर", "छोटा बच्चा", "नाबालिग", "बच्चे से काम",
        "چھوٹا بچہ", "چھوٹے بچے", "چھوٹے بچوں", "نابالغ", "بچوں سے مزدوری", "بچوں سے کام", "جبری مشقت"
    ],
    "critical_injury": [
        "severe bleeding", "amputation", "head injury", "unconscious", "dying",
        "తీవ్ర రక్తస్రావం", "స్పృహ తప్పి", "చేయి తెగింది", "కాలు విరిగింది",
        "बेहोश", "गंभीर चोट", "अंग कट गया", "खून बह रहा है",
        "بے ہوش", "شدید خون بہہ رہا ہے", "جان لیوا چوٹ"
    ]
}

EMERGENCY_CONTACTS = [
    {
        "name": "Police & Emergency Response Support System (ERSS)",
        "number": "112",
        "desc": "National emergency helpline for immediate physical rescue and safety."
    },
    {
        "name": "Women Helpline (National & Telangana)",
        "number": "181",
        "desc": "24/7 dedicated helpline for women in distress, domestic violence, or abuse."
    },
    {
        "name": "Childline Emergency Support",
        "number": "1098",
        "desc": "Emergency intervention helpline for child protection and child labour rescue."
    },
    {
        "name": "Telangana State Labour Grievance Helpline",
        "number": "1800-425-3525",
        "desc": "Toll-free government helpline for worker exploitation and bonded labour rescue."
    }
]

SPOKEN_CONSENTS = {
    "te-IN": "నమస్కారం! మీ హక్కుల సహాయం కోసం మీ పని వివరాలు మాత్రమే నమోదు చేస్తాము. ఆధార్ లేదా బ్యాంక్ నంబర్లు అడగము.",
    "hi-IN": "नमस्ते! आपके अधिकारों की रक्षा और शिकायत तैयार करने के लिए हम केवल काम की जानकारी लेते हैं। आधार या बैंक विवरण कभी नहीं मांगते।",
    "ur-IN": "آداب! آپ کے حقوق کی رہنمائی اور شکایت تیار کرنے کے لیے ہم صرف کام کی بنیادی معلومات لیتے ہیں۔ آدھار یا بینک تفصیلات کبھی نہیں مانگتے۔",
    "en-IN": "Welcome! We only collect basic work details to draft your wage grievance. We never ask for Aadhaar or bank account numbers."
}

DANGER_RESPONSES = {
    "te-IN": "హెచ్చరిక: మీ భద్రత చాలా ముఖ్యం. ఇది అత్యవసర పరిస్థితి. దయచేసి వెంటనే 112 కు లేదా లేబర్ హెల్ప్‌లైన్ 1800-425-3525 కు కాల్ చేయండి. మేము అధికారుల నంబర్లు చూపిస్తున్నాము.",
    "hi-IN": "चेतावनी: आपकी सुरक्षा सबसे महत्वपूर्ण है। यह गंभीर आपातकालीन स्थिति है। तुरंत 112 या लेबर हेल्पलाइन 1800-425-3525 पर कॉल करें। नीचे सहायता नंबर दिए गए हैं।",
    "ur-IN": "انتباہ: آپ کی حفاظت سب سے اہم ہے۔ یہ ہنگامی صورتحال ہے۔ براہ کرم فوری طور پر 112 یا لیبر ہیلپ لائن 1800-425-3525 پر کال کریں۔ مددگار نمبر نیچے موجود ہیں۔",
    "en-IN": "Emergency Notice: Your personal safety is paramount. This indicates an immediate danger signal. Please dial 112 immediately or the Labour Helpline at 1800-425-3525. Direct emergency contacts are displayed below."
}


def check_danger_signals(text: str) -> Optional[Dict[str, Any]]:
    """
    Scans worker transcript for threats of violence, bonded labour, human trafficking,
    child labour, or severe medical trauma.
    """
    text_clean = text.lower()
    for category, keywords in DANGER_KEYWORDS.items():
        for kw in keywords:
            # Check substring / word boundary
            if kw.lower() in text_clean:
                return {
                    "danger_detected": True,
                    "category": category,
                    "trigger_keyword": kw,
                    "emergency_contacts": EMERGENCY_CONTACTS
                }
    return None


def get_spoken_consent(lang: str = "te-IN") -> str:
    """Returns spoken transparency consent in worker's native language."""
    return SPOKEN_CONSENTS.get(lang, SPOKEN_CONSENTS["en-IN"])


def get_danger_response(lang: str = "te-IN") -> str:
    """Returns compassionate spoken emergency intervention message."""
    return DANGER_RESPONSES.get(lang, DANGER_RESPONSES["en-IN"])


def sanitize_input(text: str) -> str:
    """
    Ensures no 12-digit Aadhaar, 16-digit bank cards, or 10-digit PAN are retained.
    """
    # Scrub 12-digit Aadhaar patterns
    text = re.sub(r'\b\d{4}\s?\d{4}\s?\d{4}\b', '[REDACTED_ID]', text)
    # Scrub 10-digit PAN
    text = re.sub(r'\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b', '[REDACTED_PAN]', text, flags=re.IGNORECASE)
    # Scrub 16-digit card numbers
    text = re.sub(r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b', '[REDACTED_CARD]', text)
    return text
