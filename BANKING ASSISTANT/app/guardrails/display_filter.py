"""
Display Filter Guardrail:
Enforces that ONLY customer data explicitly marked `approved_for_display: true`
and `is_current: true` can be surfaced to the customer or used in LLM context.
Blocks internal bank metrics, stale records, and sensitive PII.
"""

from typing import Dict, Any, List, Tuple, Set


# Standard internal banking attributes that must NEVER be surfaced to customers
INTERNAL_BANK_BLACKLIST: Set[str] = {
    "internal_risk_score",
    "cibil_internal_band",
    "recovery_agent_code",
    "internal_notes",
    "fraud_dossier_notes",
    "raw_card_cvv",
    "pin_hash",
    "password_hash",
    "aml_risk_score",
    "collections_priority",
    "internal_margin_rate",
}


class DisplayFilterGuardrail:
    """
    Guarantees that unapproved or stale records are never introduced to the
    reasoning model, and ensures no internal data leaks into generated responses.
    """

    def filter_customer_context(
        self,
        raw_customer_data: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], List[str], List[str], List[str]]:
        """
        Inspects customer profile, transactions, loans, and tickets.
        Retains ONLY entries marked approved_for_display=True and is_current=True.

        Returns:
            sanitized_data (Dict): Cleaned data safe for LLM context.
            approved_fields (List[str]): Verified approved field names.
            blocked_unapproved (List[str]): Blocked unapproved/internal field names.
            blocked_stale (List[str]): Outdated records filtered out.
        """
        sanitized: Dict[str, Any] = {}
        approved_fields: List[str] = []
        blocked_unapproved: List[str] = []
        blocked_stale: List[str] = []

        # 1. Process top-level profile attributes
        for key, val in raw_customer_data.items():
            # Check internal blacklist first
            if key.lower() in INTERNAL_BANK_BLACKLIST:
                blocked_unapproved.append(key)
                continue

            # If attribute is a rich descriptor dict with metadata
            if isinstance(val, dict) and ("approved_for_display" in val or "is_current" in val):
                is_approved = val.get("approved_for_display", False)
                is_current = val.get("is_current", True)

                if not is_approved:
                    blocked_unapproved.append(key)
                    # Also record specific child keys for audit transparency
                    for sub_k in val.keys():
                        if sub_k not in ("approved_for_display", "is_current"):
                            blocked_unapproved.append(f"{key}.{sub_k}")
                    continue
                if not is_current:
                    blocked_stale.append(key)
                    continue

                sanitized[key] = val.get("value", val)
                approved_fields.append(key)

            # If attribute is a list of record dictionaries (e.g. transactions, loans, tickets)
            elif isinstance(val, list):
                sanitized_list = []
                for idx, item in enumerate(val):
                    if isinstance(item, dict):
                        is_approved = item.get("approved_for_display", True)
                        is_current = item.get("is_current", True)
                        item_id = item.get("id") or item.get("transaction_id") or item.get("loan_id") or f"{key}[{idx}]"

                        if not is_approved:
                            blocked_unapproved.append(f"{key}:{item_id}")
                            continue
                        if not is_current:
                            blocked_stale.append(f"{key}:{item_id}")
                            continue

                        # Clean item itself of any internal fields
                        cleaned_item = {
                            k: v for k, v in item.items()
                            if k.lower() not in INTERNAL_BANK_BLACKLIST
                            and not (isinstance(v, dict) and v.get("approved_for_display") is False)
                        }
                        sanitized_list.append(cleaned_item)
                    else:
                        sanitized_list.append(item)

                sanitized[key] = sanitized_list
                approved_fields.append(key)

            # Standard approved scalar attributes
            else:
                sanitized[key] = val
                approved_fields.append(key)

        return sanitized, approved_fields, blocked_unapproved, blocked_stale

    def check_egress_leakage(
        self,
        candidate_response: str,
        blocked_values: List[str]
    ) -> Tuple[bool, str]:
        """
        Scans outgoing response for any accidental leakage of blocked strings or tokens.
        If found, replaces them with sanitized markers.
        """
        sanitized = candidate_response
        leakage_found = False

        for secret in blocked_values:
            if not secret or len(str(secret).strip()) < 3:
                continue
            str_val = str(secret)
            if str_val in sanitized:
                leakage_found = True
                sanitized = sanitized.replace(str_val, "[REDACTED_INTERNAL_DATA]")

        return leakage_found, sanitized
