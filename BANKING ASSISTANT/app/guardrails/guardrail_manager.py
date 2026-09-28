"""
Unified Guardrail Manager:
Coordinates Data Entitlement and Anti-Redundancy policies.
Produces comprehensive GuardrailAuditReport for transparent judge verification.
"""

from typing import Dict, Any, List, Tuple, Optional
from .models import GuardrailAuditReport
from .display_filter import DisplayFilterGuardrail
from .anti_reask import AntiReaskGuardrail


class GuardrailManager:
    """
    Unified manager executing context sanitization, negative constraint synthesis,
    and post-generation compliance inspection.
    """

    def __init__(self):
        self.display_filter = DisplayFilterGuardrail()
        self.anti_reask = AntiReaskGuardrail()

    def process_pre_inference(
        self,
        raw_customer_data: Dict[str, Any],
        known_memory_facts: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], str, GuardrailAuditReport]:
        """
        Executes pre-inference guardrails:
        1. Strips unapproved (approved_for_display=False) and stale (is_current=False) data.
        2. Injects zero-redundancy prompt constraints for known memory facts.

        Returns:
            sanitized_context: Clean dict safe for LLM context injection.
            prompt_constraints: String directives to append to the LLM system prompt.
            audit_report: Live audit report with stripped fields & protected facts.
        """
        audit = GuardrailAuditReport()

        # Step 1: Whitelist & Stale Filtering
        sanitized_context, approved, blocked_unapproved, blocked_stale = (
            self.display_filter.filter_customer_context(raw_customer_data)
        )
        audit.approved_fields_passed = approved
        audit.blocked_unapproved_fields = blocked_unapproved
        audit.blocked_stale_records = blocked_stale

        # Step 2: Anti-Reask Constraints
        audit.known_entities_protected = [
            k for k, v in known_memory_facts.items() if v
        ]
        prompt_constraints = self.anti_reask.generate_negative_prompt_directives(
            known_memory_facts
        )

        return sanitized_context, prompt_constraints, audit

    def process_post_inference(
        self,
        candidate_response: str,
        blocked_values: List[str],
        known_memory_facts: Dict[str, Any],
        audit: Optional[GuardrailAuditReport] = None
    ) -> Tuple[str, GuardrailAuditReport]:
        """
        Executes post-inference compliance inspection:
        1. Scans for accidental data leakage of blocked internal values.
        2. Detects and redacts any attempts to re-ask the customer for known facts.

        Returns:
            final_response: Cleaned, compliant response text.
            audit: Updated GuardrailAuditReport.
        """
        audit = audit or GuardrailAuditReport()
        current_text = candidate_response

        # Step 1: Leakage Check
        leakage_found, current_text = self.display_filter.check_egress_leakage(
            current_text, blocked_values
        )
        if leakage_found:
            audit.leakage_detected = True
            audit.sanitized_output_applied = True

        # Step 2: Anti-Reask Interception
        has_violations, current_text, violations = self.anti_reask.scan_and_intercept(
            current_text, known_memory_facts
        )
        if has_violations:
            audit.reask_violations_intercepted = violations
            audit.sanitized_output_applied = True

        # Overall pass status: pass is True if no unhandled leakage or severe violation
        audit.passed = not audit.leakage_detected

        return current_text, audit
