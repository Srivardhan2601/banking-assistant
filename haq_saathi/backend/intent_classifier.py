"""
Multilingual intent classification for informal worker grievances.
Classifies utterances into: unpaid_wages, below_minimum_wage, no_pf_or_benefits,
workplace_injury, wrongful_termination, or other.
"""

import re
from typing import Tuple
from .models import IntentEnum, WorkerCategory


INTENT_PATTERNS = {
    IntentEnum.UNPAID_WAGES: [
        r"జీతం|కూలి|డబ్బులు.*ఇవ్వలేదు|బాకీ|చెల్లించలేదు|జీతం.*రాలేదు|నెల.*జీతం",
        r"पगार|वेतन|मजदूरी|पैसे.*नहीं.*दिए|बाकी|रुपये.*नहीं.*मिले|महीने.*की.*पगार",
        r"تنخواہ|مزدوری|اجرت|پیسے.*نہیں.*ملے|بقایا|روپے.*نہیں.*دیے",
        r"unpaid|salary.*not.*paid|wages.*due|money.*owed|withheld|pending.*pay|months.*unpaid"
    ],
    IntentEnum.BELOW_MINIMUM_WAGE: [
        r"కనీస.*వేతనం|తక్కువ.*కూలి|తక్కువ.*జీతం|చట్టబద్ధమైన|రేటు.*తక్కువ",
        r"न्यूनतम.*मजदूरी|कम.*पगार|कम.*पैसे|कम.*मजदूरी|कम.*वेतन",
        r"کم.*اجرت|کم.*مزدوری|کم.*تنخواہ|سرکاری.*ریٹ|کم.*پیسے",
        r"minimum.*wage|underpaid|less.*than.*minimum|low.*salary|pay.*too.*little"
    ],
    IntentEnum.WORKPLACE_INJURY: [
        r"గాయం|ప్రమాదం|దెబ్బ|పనిలో.*దెబ్బ|హాస్పిటల్|ఆసుపత్రి|చేయి.*విరిగింది",
        r"चोट|दुर्घटना|हादसा|अस्पताल|काम.*पर.*चोट|फ्रैक्चर|इलाज.*का.*खर्च",
        r"چوٹ|حادثہ|زخمی|ہسپتال|کام.*پر.*چوٹ|علاج",
        r"injury|accident|hurt|hospital|fracture|injured.*at.*work|medical.*expense"
    ],
    IntentEnum.NO_PF_OR_BENEFITS: [
        r"పీఎఫ్|సంక్షేమం|బోర్డు|కార్డు|బీమా|పింఛను|పీ.*ఎఫ్",
        r"पीएफ|फंड|वेलफेयर|कार्ड|बीमा|पेंशन|भत्ता",
        r"پی.*ایف|پینشن|ویلفیئر|کارڈ|فنڈ|انشورنس",
        r"pf|provident.*fund|epf|benefits|bocw|insurance|pension"
    ],
    IntentEnum.WRONGFUL_TERMINATION: [
        r"తీసేశారు|తొలగించారు|పని.*నుంచి.*తీసేశారు|పని.*లేదు.*అన్నారు|ఉద్యోగం.*పోయింది",
        r"काम.*से.*निकाल.*दिया|हटा.*दिया|नौकरी.*से.*निकाला|काम.*बंद.*कर.*दिया",
        r"کام.*سے.*نکال.*دیا|برطرف|نوکری.*ختم",
        r"fired|terminated|dismissed|kicked.*out|sacked|lost.*job|removed.*from.*work"
    ]
}

CATEGORY_PATTERNS = {
    WorkerCategory.DOMESTIC_WORKER: [
        r"ఇంటి.*పని|ఇళ్ల.*పని|వంట|పనిమనిషి|ఆయా|స్వీపర్|క్లీనర్",
        r"घरेलू.*काम|घर.*का.*काम|झाड़ू|पोछा|बाई|खाना.*बनाने|आया",
        r"گھریلو.*ملازم|گھر.*کا.*کام|ملازمہ|آیا|صفائی",
        r"domestic|maid|househelp|cook|cleaning|babysitter"
    ],
    WorkerCategory.DELIVERY_RIDER: [
        r"డెలివరీ|రైడర్|జొమాటో|స్విగ్గీ|బ్లింకిట్|బైక్.*రైడర్",
        r"डिलीवरी|राइडर|जोमैटो|स्विगी|ब्लिंकिट|पार्सल",
        r"ڈیلیوری|رائیڈر|زومیٹو|سوئیگی",
        r"delivery|rider|zomato|swiggy|blinkit|courier|porter"
    ],
    WorkerCategory.CONSTRUCTION_WORKER: [
        r"భవన.*నిర్మాణం|మేస్త్రీ|కూలీ|తాపీ.*పని|లేబర్|సిమెంట్|కంకర",
        r"भवन.*निर्माण|मजदूर|राजमिस्त्री|ठेकेदार|बेलदार|सीमेंट",
        r"تعمیراتی.*مزدور|مستری|مزدور|ٹھیکیدار|سیمنٹ",
        r"construction|mason|builder|site.*worker|labourer|cement"
    ],
    WorkerCategory.GIG_WORKER: [
        r"గిగ్|యాప్.*వర్కర్|క్యాబ్|డ్రైవర్|ఉబర్|ఓలా",
        r"गिग|ऐप.*वर्कर|कैब|ड्राइवर|ओला|उबर",
        r"گگ.*ورکر|کیب.*ڈرائیور|اولا|اوبر",
        r"gig|app.*worker|driver|ola|uber|platform"
    ]
}


def classify_intent(text: str) -> IntentEnum:
    """Classifies user statement into specific grievance intent."""
    text_clean = text.lower().strip()
    for intent, patterns in INTENT_PATTERNS.items():
        for pat in patterns:
            if re.search(pat, text_clean, re.IGNORECASE):
                return intent
    return IntentEnum.OTHER


def extract_worker_category(text: str) -> WorkerCategory:
    """Detects worker sector or category from statement."""
    text_clean = text.lower().strip()
    for cat, patterns in CATEGORY_PATTERNS.items():
        for pat in patterns:
            if re.search(pat, text_clean, re.IGNORECASE):
                return cat
    return WorkerCategory.INFORMAL_WORKER


def extract_key_entities(text: str) -> dict:
    """
    Extracts key informal grievance parameters:
    - Amount (e.g. ₹15,000, 15000, పదిహేను వేలు)
    - Months/Duration (e.g. 3 months, 2 నెలలు, 3 महीने)
    - District in Telangana (e.g. Hyderabad, Warangal, Rangareddy)
    """
    extracted = {}
    
    # Amount patterns: ₹ or Rs followed by digits, or digits followed by k/thousand/వేలు/हजार
    amt_match = re.search(r'(?:₹|rs\.?|inr)?\s*([0-9]{1,3}(?:,[0-9]{3})+|[0-9]{3,7})\b', text, re.IGNORECASE)
    if amt_match:
        val = amt_match.group(1).replace(',', '')
        extracted["amount_owed"] = f"₹{int(val):,}"
    elif re.search(r'([0-9]+)\s*(?:వేలు|వేల|हजार|ہزار|thousand|k)', text, re.IGNORECASE):
        num_m = re.search(r'([0-9]+)\s*(?:వేలు|వేల|हजार|ہزار|thousand|k)', text, re.IGNORECASE)
        val = int(num_m.group(1)) * 1000
        extracted["amount_owed"] = f"₹{val:,}"

    # Months / Duration
    dur_match = re.search(r'([0-9]+|ఒక|రెండు|మూడు|నాలుగు|ఏడు|एक|दो|तीन|चार|چھ|دو|تین)\s*(?:నెలలు|నెలల|నెల|महीने|महीनों|ماہ|مہینے|months?|month)', text, re.IGNORECASE)
    if dur_match:
        extracted["months_unpaid"] = dur_match.group(0).strip()

    # District extraction for Telangana
    districts = [
        "Hyderabad", "Rangareddy", "Medchal", "Medchal-Malkajgiri", "Warangal", 
        "Hanamkonda", "Nizamabad", "Karimnagar", "Khammam", "Nalgonda", 
        "Mahabubnagar", "Siddipet", "Sangareddy", "హైదరాబాద్", "వరంగల్", 
        "రంగారెడ్డి", "నిజామాబాద్", "కరీంనగర్", "हैदराबाद", "वारंगल", 
        "रंगारेड्डी", "निजामाबाद", "करीमनगर", "حیدرآباد", "ورنگل", "رنگا ریڈی"
    ]
    for d in districts:
        if d.lower() in text.lower():
            # Normalize to English district name for routing
            if any(h in d.lower() for h in ["hyd", "హైదరాబాద్", "हैदराबाद", "حیدرآباد"]):
                extracted["district"] = "Hyderabad"
            elif any(w in d.lower() for w in ["war", "hanam", "వరంగల్", "वारंगल", "ورنگل"]):
                extracted["district"] = "Warangal"
            elif any(r in d.lower() for r in ["ranga", "రంగారెడ్డి", "रंगारेड्डी", "رنگا"]):
                extracted["district"] = "Rangareddy"
            elif any(m in d.lower() for m in ["medchal", "మేడ్చల్", "मेडचल", "میڈچل"]):
                extracted["district"] = "Medchal-Malkajgiri"
            elif any(n in d.lower() for n in ["nizam", "నిజామాబాద్", "निजामाबाद", "نظام"]):
                extracted["district"] = "Nizamabad"
            elif any(k in d.lower() for k in ["karim", "కరీంనగర్", "करीमनगर", "کریم"]):
                extracted["district"] = "Karimnagar"
            elif any(kh in d.lower() for kh in ["kham", "ఖమ్మం", "खम्मम", "کھمم"]):
                extracted["district"] = "Khammam"
            else:
                extracted["district"] = d
            break

    return extracted
