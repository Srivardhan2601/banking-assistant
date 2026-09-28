"""
Anti-Redundancy & Anti-Reask Guardrail:
Prevents the agent from re-asking the customer for information that is
already present and verified in their Hindsight Cloud memory bank.
"""

import re
from typing import Dict, Any, List, Tuple


# Regex patterns commonly used when an AI agent asks for customer identification facts
REASK_QUESTION_PATTERNS = {
    "account_number": [
        r"(?:provide|share|tell|confirm|enter|give)\s+(?:me\s+)?(?:your\s+)?(?:bank\s+)?account\s+number",
        r"what\s+is\s+your\s+(?:bank\s+)?account\s+number",
        r"apna\s+account\s+number\s+(?:batayein|dein|share\s+karein)",
    ],
    "loan_account_number": [
        r"(?:provide|share|tell|confirm|enter|give)\s+(?:me\s+)?(?:your\s+)?loan\s+(?:account\s+)?(?:number|id)",
        r"what\s+is\s+your\s+loan\s+(?:account\s+)?(?:number|id)",
        r"loan\s+(?:account\s+)?(?:number|id)\s+(?:batayein|share\s+karein)",
    ],
    "phone_number": [
        r"(?:provide|share|tell|confirm|enter|give)\s+(?:me\s+)?(?:your\s+)?(?:registered\s+)?(?:phone|mobile)\s+number",
        r"what\s+is\s+your\s+(?:registered\s+)?(?:phone|mobile)\s+number",
        r"(?:phone|mobile)\s+number\s+(?:batayein|share\s+karein)",
    ],
    "email": [
        r"(?:provide|share|tell|confirm|enter|give)\s+(?:me\s+)?(?:your\s+)?(?:registered\s+)?email",
        r"what\s+is\s+your\s+email",
        r"apna\s+email\s+(?:batayein|share\s+karein)",
    ],
    "name": [
        r"(?:provide|share|tell|confirm)\s+(?:me\s+)?(?:your\s+)?full\s+name",
        r"what\s+is\s+your\s+(?:full\s+)?name",
        r"apka\s+naam\s+kya\s+hai",
    ],
    "ticket_id": [
        r"(?:provide|share|tell|confirm)\s+(?:your\s+)?(?:past\s+|previous\s+)?ticket\s+(?:number|id)",
        r"what\s+is\s+your\s+ticket\s+id",
    ]
}


class AntiReaskGuardrail:
    """
    Ensures the customer is never burdened by repeating information
    already persisted in their Hindsight memory bank.
    """

    def generate_negative_prompt_directives(self, known_facts: Dict[str, Any]) -> str:
        """
        Creates prompt constraints listing known facts that the LLM is explicitly
        forbidden from re-asking.
        """
        if not known_facts:
            return ""

        known_lines = []
        for k, v in known_facts.items():
            if v:
                human_key = k.replace("_", " ").title()
                known_lines.append(f"  - {human_key}: {v}")

        return (
            "\n[ZERO-REDUNDANCY MEMORY ENFORCEMENT]\n"
            "The following customer information is ALREADY VERIFIED and present in your recalled memory:\n"
            + "\n".join(known_lines) + "\n"
            "STRICT MANDATE: You are FORBIDDEN from asking the customer to provide or re-verify any of the above details.\n"
            "Refer to these details directly when answering (e.g. 'For your account ending in ...').\n"
        )

    def scan_and_intercept(
        self,
        candidate_response: str,
        known_facts: Dict[str, Any]
    ) -> Tuple[bool, str, List[str]]:
        """
        Scans outgoing response for any questions attempting to re-ask for known facts.
        If found, replaces the redundant question with proactive acknowledgment.

        Returns:
            has_violations (bool): True if at least one re-ask violation was intercepted.
            sanitized_text (str): Cleaned response with redundant queries removed.
            violated_entities (List[str]): List of entities that the LLM inappropriately asked for.
        """
        sanitized = candidate_response
        violated_entities: List[str] = []

        # Map known fact keys to pattern categories
        entity_key_map = {
            "account_number": "account_number",
            "account_id": "account_number",
            "loan_account_number": "loan_account_number",
            "loan_id": "loan_account_number",
            "registered_mobile": "phone_number",
            "mobile": "phone_number",
            "phone": "phone_number",
            "email": "email",
            "customer_name": "name",
            "name": "name",
            "last_ticket_id": "ticket_id",
        }

        active_categories = set()
        for fact_key, val in known_facts.items():
            if val and fact_key.lower() in entity_key_map:
                active_categories.add(entity_key_map[fact_key.lower()])

        for category in active_categories:
            patterns = REASK_QUESTION_PATTERNS.get(category, [])
            for pat in patterns:
                match = re.search(pat, sanitized, re.IGNORECASE)
                if match:
                    violated_entities.append(category)
                    # Redact or rewrite the question sentence
                    sentence_pattern = r"([^.?!]*" + pat + r"[^.?!]*[.?!]?)"
                    replacement = "I already have your verified details on record. "
                    sanitized = re.sub(sentence_pattern, replacement, sanitized, flags=re.IGNORECASE)

        has_violations = len(violated_entities) > 0
        return has_violations, sanitized.strip(), violated_entities
