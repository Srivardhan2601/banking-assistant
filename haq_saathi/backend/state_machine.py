"""
Deterministic State Machine for Haq Saathi.
Manages transition flow:
GREETING -> UNDERSTAND_PROBLEM -> COLLECT_FIELDS -> EXPLAIN_RIGHTS -> CONFIRM -> GENERATE_COMPLAINT -> ROUTE -> DONE.
Supports DANGER_OVERRIDE at any state for worker safety.
"""

from typing import Dict, Any, List, Optional, Tuple
from .models import StateEnum, IntentEnum, WorkerCategory


# Suggested tap-to-pick options for accessibility without speaking
QUICK_OPTIONS = {
    StateEnum.GREETING: {
        "te": ["జీతం ఇవ్వలేదు", "కనీస వేతనం రాలేదు", "పనిలో దెబ్బ తగిలింది", "తీసేశారు"],
        "hi": ["पगार नहीं मिली", "न्यूनतम मजदूरी से कम", "काम पर चोट लगी", "काम से निकाल दिया"],
        "ur": ["تنخواہ نہیں ملی", "کم اجرت ملی", "کام پر چوٹ لگی", "کام سے نکال دیا"],
        "en": ["Salary Not Paid", "Below Minimum Wage", "Injury at Work", "Wrongful Firing"]
    },
    "ask_category": {
        "te": ["ఇళ్ల పని (Domestic)", "డెలివరీ రైడర్ (Delivery)", "భవన నిర్మాణం (Construction)", "ఇతర అసంఘటిత పని"],
        "hi": ["घरेलू काम (Domestic)", "डिलीवरी राइडर (Delivery)", "भवन निर्माण (Construction)", "अन्य काम"],
        "ur": ["گھریلو کام (Domestic)", "ڈیلیوری رائیڈر (Delivery)", "تعمیراتی کام (Construction)", "دیگر کام"],
        "en": ["Domestic Worker", "Delivery Rider", "Construction Worker", "Other Labour"]
    },
    "ask_period": {
        "te": ["1 నెల (1 Month)", "2 నెలలు (2 Months)", "3 నెలలు (3 Months)", "3+ నెలల కంటే ఎక్కువ"],
        "hi": ["1 महीना (1 Month)", "2 महीने (2 Months)", "3 महीने (3 Months)", "3 महीने से ज्यादा"],
        "ur": ["1 مہینہ (1 Month)", "2 مہینے (2 Months)", "3 مہینے (3 Months)", "3 مہینے سے زیادہ"],
        "en": ["1 Month", "2 Months", "3 Months", "More than 3 Months"]
    },
    "ask_district": {
        "te": ["హైదరాబాద్ (Hyderabad)", "రంగారెడ్డి (Rangareddy)", "మేడ్చల్ (Medchal)", "వరంగల్ (Warangal)"],
        "hi": ["हैदराबाद (Hyderabad)", "रंगारेड्डी (Rangareddy)", "मेडचल (Medchal)", "वारंगल (Warangal)"],
        "ur": ["حیدرآباد (Hyderabad)", "رنگا ریڈی (Rangareddy)", "میڈچل (Medchal)", "ورنگل (Warangal)"],
        "en": ["Hyderabad", "Rangareddy", "Medchal", "Warangal"]
    },
    StateEnum.CONFIRM: {
        "te": ["అవును, ఫిర్యాదు చేయండి (Yes, File)", "కాదు, సమాచారం చాలు (No)"],
        "hi": ["हाँ, शिकायत दर्ज करें (Yes, File)", "नहीं, केवल जानकारी चाहिए (No)"],
        "ur": ["ہاں، شکایت درج کریں (Yes, File)", "نہیں، صرف معلومات چاہیے (No)"],
        "en": ["Yes, File Complaint", "No, Information Only"]
    },
    StateEnum.DONE: {
        "te": ["PDF డౌన్‌లోడ్ చేయండి", "మళ్లీ చదవండి (Replay)", "కొత్త సంభాషణ (Reset)"],
        "hi": ["PDF डाउनलोड करें", "दोबारा सुनें (Replay)", "नई शिकायत (Reset)"],
        "ur": ["PDF ڈاؤنلوڈ کریں", "دوبارہ سنیں (Replay)", "نئی شکایت (Reset)"],
        "en": ["Download PDF", "Replay Voice", "New Complaint"]
    }
}


class FlowStateMachine:
    """Manages predictable state transitions and required field tracking."""

    @staticmethod
    def get_initial_session() -> Dict[str, Any]:
        return {
            "state": StateEnum.GREETING,
            "current_state": StateEnum.GREETING,
            "intent": IntentEnum.OTHER,
            "collected_fields": {
                "worker_category": None,
                "employer_name": None,
                "months_unpaid": None,
                "amount_owed": None,
                "district": None,
                "worker_name": None
            },
            "step_count": 0,
            "question_count": 0,
            "rights_retrieved_id": None,
            "complaint_id": None
        }

    @staticmethod
    def get_next_missing_field(collected: Dict[str, Any]) -> Optional[str]:
        """Order of 4 questions max: category -> employer -> period -> amount/district."""
        if not collected.get("worker_category"):
            return "worker_category"
        if not collected.get("employer_name"):
            return "employer_name"
        if not collected.get("months_unpaid"):
            return "months_unpaid"
        if not collected.get("amount_owed") or not collected.get("district"):
            return "amount_owed_or_district"
        return None

    @staticmethod
    def transition(session: Dict[str, Any], user_text: str, extracted_entities: Dict[str, Any], is_danger: bool) -> Tuple[StateEnum, str, List[str], Optional[str]]:
        """
        Determines the next state, the next action required, and suggested options.
        Returns: (next_state, next_action, suggested_options, next_field_to_ask)
        """
        if is_danger:
            session["state"] = StateEnum.DANGER_OVERRIDE
            session["current_state"] = StateEnum.DANGER_OVERRIDE
            return StateEnum.DANGER_OVERRIDE, "EMERGENCY_REFERRAL", ["112 కి కాల్ చేయండి (Call 112)", "లేబర్ హెల్ప్‌లైన్ (1800-425-3525)"], None

        current = session.get("current_state") or session.get("state", StateEnum.GREETING)
        collected = session.get("collected_fields", {})

        # Merge extracted entities
        for k, v in extracted_entities.items():
            if v and not collected.get(k):
                collected[k] = v

        lang_code = session.get("language", "te-IN")[:2]

        # 1. GREETING -> UNDERSTAND_PROBLEM
        if current == StateEnum.GREETING:
            session["state"] = StateEnum.UNDERSTAND_PROBLEM
            session["current_state"] = StateEnum.UNDERSTAND_PROBLEM
            options = QUICK_OPTIONS[StateEnum.GREETING].get(lang_code, QUICK_OPTIONS[StateEnum.GREETING]["en"])
            return StateEnum.UNDERSTAND_PROBLEM, "LISTEN_PROBLEM", options, None

        # 2. UNDERSTAND_PROBLEM -> COLLECT_FIELDS (or directly EXPLAIN_RIGHTS if fields already complete)
        if current == StateEnum.UNDERSTAND_PROBLEM:
            missing = FlowStateMachine.get_next_missing_field(collected)
            if missing and session.get("question_count", 0) < 4:
                session["state"] = StateEnum.COLLECT_FIELDS
                session["current_state"] = StateEnum.COLLECT_FIELDS
                session["question_count"] = session.get("question_count", 0) + 1
                opts = FlowStateMachine._get_options_for_field(missing, lang_code)
                return StateEnum.COLLECT_FIELDS, f"ASK_{missing.upper()}", opts, missing
            else:
                session["state"] = StateEnum.EXPLAIN_RIGHTS
                session["current_state"] = StateEnum.EXPLAIN_RIGHTS
                return StateEnum.EXPLAIN_RIGHTS, "EXPLAIN_RIGHTS", ["ఫిర్యాదు సిద్ధం చేయండి (File Complaint)", "మరిన్ని వివరాలు (More Info)"], None

        # 3. COLLECT_FIELDS loop (enforcing at most 4 follow-up questions)
        if current == StateEnum.COLLECT_FIELDS:
            q_count = session.get("question_count", 0)
            missing = FlowStateMachine.get_next_missing_field(collected)
            if missing and q_count < 4:
                session["question_count"] = q_count + 1
                opts = FlowStateMachine._get_options_for_field(missing, lang_code)
                return StateEnum.COLLECT_FIELDS, f"ASK_{missing.upper()}", opts, missing
            else:
                # All 4 essential details in or 4 question cap reached!
                session["state"] = StateEnum.EXPLAIN_RIGHTS
                session["current_state"] = StateEnum.EXPLAIN_RIGHTS
                return StateEnum.EXPLAIN_RIGHTS, "EXPLAIN_RIGHTS", ["ఫిర్యాదు సిద్ధం చేయండి (File Complaint)", "హక్కుల వివరాలు (More Info)"], None

        # 4. EXPLAIN_RIGHTS -> CONFIRM or GENERATE_COMPLAINT
        if current == StateEnum.EXPLAIN_RIGHTS:
            user_lower = user_text.lower()
            affirmative = any(w in user_lower for w in ["yes", "అవును", "హా", "हाँ", "हा", "ہاں", "file", "okay", "సరే", "సరేనండి", "చెయ్యండి", "కండి", "చేయండి", "ఫిర్యాదు", "शिकायत", "خط"])
            if affirmative:
                session["state"] = StateEnum.GENERATE_COMPLAINT
                session["current_state"] = StateEnum.GENERATE_COMPLAINT
                return StateEnum.GENERATE_COMPLAINT, "GENERATE_COMPLAINT", QUICK_OPTIONS[StateEnum.DONE].get(lang_code, QUICK_OPTIONS[StateEnum.DONE]["en"]), None
            else:
                session["state"] = StateEnum.CONFIRM
                session["current_state"] = StateEnum.CONFIRM
                opts = QUICK_OPTIONS[StateEnum.CONFIRM].get(lang_code, QUICK_OPTIONS[StateEnum.CONFIRM]["en"])
                return StateEnum.CONFIRM, "ASK_CONFIRMATION", opts, None

        # 5. CONFIRM -> GENERATE_COMPLAINT / ROUTE
        if current == StateEnum.CONFIRM:
            user_lower = user_text.lower()
            affirmative = any(w in user_lower for w in ["yes", "అవును", "హా", "हाँ", "हा", "ہاں", "file", "okay", "సరే", "సరేనండి", "చెయ్యండి", "కండి", "చేయండి"])
            if affirmative or "no" not in user_lower:
                session["state"] = StateEnum.GENERATE_COMPLAINT
                session["current_state"] = StateEnum.GENERATE_COMPLAINT
                return StateEnum.GENERATE_COMPLAINT, "GENERATE_COMPLAINT", QUICK_OPTIONS[StateEnum.DONE].get(lang_code, QUICK_OPTIONS[StateEnum.DONE]["en"]), None
            else:
                session["state"] = StateEnum.DONE
                session["current_state"] = StateEnum.DONE
                return StateEnum.DONE, "SESSION_CLOSED", ["సమాచారం సేవ్ అయింది", "కొత్త ప్రశ్న"], None

        # 6. GENERATE_COMPLAINT / ROUTE -> DONE
        if current in [StateEnum.ROUTE, StateEnum.GENERATE_COMPLAINT]:
            session["state"] = StateEnum.DONE
            session["current_state"] = StateEnum.DONE
            return StateEnum.DONE, "COMPLAINT_READY", QUICK_OPTIONS[StateEnum.DONE].get(lang_code, QUICK_OPTIONS[StateEnum.DONE]["en"]), None

        # Default fallback
        return current, "CONTINUE", ["సరే", "ముందుకు సాగండి"], None

    @staticmethod
    def _get_options_for_field(field_name: str, lang_code: str) -> List[str]:
        if field_name == "worker_category":
            return QUICK_OPTIONS["ask_category"].get(lang_code, QUICK_OPTIONS["ask_category"]["en"])
        elif field_name == "months_unpaid":
            return QUICK_OPTIONS["ask_period"].get(lang_code, QUICK_OPTIONS["ask_period"]["en"])
        elif field_name == "amount_owed_or_district":
            return QUICK_OPTIONS["ask_district"].get(lang_code, QUICK_OPTIONS["ask_district"]["en"])
        return ["సరే (OK)", "తెలియదు (Not Sure)"]


state_machine = FlowStateMachine()
