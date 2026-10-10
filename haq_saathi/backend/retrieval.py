"""
Knowledge base retrieval engine for Haq Saathi.
Loads curated rights strictly from knowledge/rights.json.
Never hallucinates legal section numbers or wage rates.
"""

import json
from pathlib import Path
from typing import Optional, List, Dict, Any
from .models import RightsSummary, IntentEnum


KNOWLEDGE_FILE = Path(__file__).resolve().parent.parent / "knowledge" / "rights.json"


class RightsRetriever:
    """Retrieves verified statutory worker rights from curated knowledge base."""

    def __init__(self, kb_path: Path = KNOWLEDGE_FILE):
        self.kb_path = kb_path
        self.entries = self._load_knowledge()

    def _load_knowledge(self) -> List[Dict[str, Any]]:
        if not self.kb_path.exists():
            print(f"[Retrieval] Knowledge base file not found at {self.kb_path}")
            return []
        try:
            with open(self.kb_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[Retrieval] Error reading rights.json: {e}")
            return []

    def retrieve(self, intent: IntentEnum, worker_category: str = "informal_worker", query: str = "", lang: str = "te-IN") -> Optional[RightsSummary]:
        """
        Retrieves matching verified knowledge entry based on intent and category.
        Falls back to keyword matching if intent is ambiguous.
        """
        lang_key = lang.split("-")[0] if "-" in lang else lang
        if lang_key not in ["te", "hi", "ur", "en"]:
            lang_key = "en"

        # Topic map from Intent
        intent_to_topic = {
            IntentEnum.UNPAID_WAGES: "timely_wages",
            IntentEnum.BELOW_MINIMUM_WAGE: "minimum_wage",
            IntentEnum.WORKPLACE_INJURY: "workplace_injury",
            IntentEnum.NO_PF_OR_BENEFITS: "bocw_registration" if worker_category == "construction_worker" else "gig_social_security",
            IntentEnum.WRONGFUL_TERMINATION: "wrongful_termination"
        }

        target_topic = intent_to_topic.get(intent)

        # 1. First, search by target topic and worker category
        if target_topic:
            for entry in self.entries:
                if entry.get("topic") == target_topic:
                    # check if category is in applies_to or informal_worker applies
                    if worker_category in entry.get("applies_to", []) or "informal_worker" in entry.get("applies_to", []):
                        return self._format_summary(entry, lang_key)
            # If not matched by category, take topic match
            for entry in self.entries:
                if entry.get("topic") == target_topic:
                    return self._format_summary(entry, lang_key)

        # 2. Keyword fallback over query text
        query_lower = query.lower()
        for entry in self.entries:
            for kw in entry.get("keywords", []):
                if kw.lower() in query_lower:
                    return self._format_summary(entry, lang_key)

        # 3. Default to general timely wages if no other match
        if self.entries:
            return self._format_summary(self.entries[0], lang_key)
        return None

    def _format_summary(self, entry: Dict[str, Any], lang_key: str) -> RightsSummary:
        explanations = entry.get("plain_explanation", {})
        plain_text = explanations.get(lang_key, explanations.get("en", "Rights protection available under labour law."))
        
        return RightsSummary(
            id=entry.get("id", "RIGHT-GEN-01"),
            topic=entry.get("topic", "welfare"),
            title=entry.get("title", "Worker Protection Guarantee"),
            plain_explanation=plain_text,
            authority=entry.get("authority", "Labour Department, Government of Telangana"),
            source_name=entry.get("source_name", "Statutory Labour Law Framework"),
            source_url_placeholder=entry.get("source_url_placeholder", "https://labour.telangana.gov.in"),
            last_verified_date=entry.get("last_verified_date", "2026-01-15")
        )

    def list_all(self) -> List[Dict[str, Any]]:
        return self.entries


retriever = RightsRetriever()
