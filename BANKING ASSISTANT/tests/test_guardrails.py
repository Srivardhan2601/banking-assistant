"""
Unit tests for the Financial Services Guardrail Layer.
Verifies data entitlement (approved_for_display / is_current) and memory anti-redundancy.
"""

import unittest
from app.guardrails import (
    DisplayFilterGuardrail,
    AntiReaskGuardrail,
    GuardrailManager,
    GuardrailAuditReport
)


class TestDisplayFilterGuardrail(unittest.TestCase):

    def setUp(self):
        self.filter = DisplayFilterGuardrail()

    def test_blocks_internal_blacklisted_fields(self):
        raw_data = {
            "customer_name": "Aarav Sharma",
            "internal_risk_score": 792,
            "cibil_internal_band": "TIER-1-PRIME",
            "password_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            "account_balance": {"value": 154200.0, "approved_for_display": True, "is_current": True}
        }
        sanitized, approved, blocked_unapproved, blocked_stale = self.filter.filter_customer_context(raw_data)

        self.assertNotIn("internal_risk_score", sanitized)
        self.assertNotIn("cibil_internal_band", sanitized)
        self.assertNotIn("password_hash", sanitized)
        self.assertIn("internal_risk_score", blocked_unapproved)
        self.assertIn("cibil_internal_band", blocked_unapproved)
        self.assertIn("account_balance", sanitized)
        self.assertEqual(sanitized["account_balance"], 154200.0)

    def test_blocks_unapproved_and_stale_records(self):
        raw_data = {
            "loans": [
                {
                    "loan_id": "LN-ACTIVE-01",
                    "type": "Home Loan",
                    "approved_for_display": True,
                    "is_current": True,
                    "outstanding": 3200000.0
                },
                {
                    "loan_id": "LN-CONFIDENTIAL-02",
                    "type": "Internal Bridge Loan",
                    "approved_for_display": False,
                    "is_current": True,
                    "outstanding": 500000.0
                },
                {
                    "loan_id": "LN-EXPIRED-03",
                    "type": "Old Auto Loan",
                    "approved_for_display": True,
                    "is_current": False,
                    "outstanding": 0.0
                }
            ]
        }
        sanitized, approved, blocked_unapproved, blocked_stale = self.filter.filter_customer_context(raw_data)

        self.assertEqual(len(sanitized["loans"]), 1)
        self.assertEqual(sanitized["loans"][0]["loan_id"], "LN-ACTIVE-01")
        self.assertTrue(any("LN-CONFIDENTIAL-02" in b for b in blocked_unapproved))
        self.assertTrue(any("LN-EXPIRED-03" in s for s in blocked_stale))

    def test_egress_leakage_redaction(self):
        blocked = ["SECRET_TOKEN_999", "TIER-1-PRIME"]
        candidate = "Your internal tier code is TIER-1-PRIME with token SECRET_TOKEN_999."
        leaked, cleaned = self.filter.check_egress_leakage(candidate, blocked)

        self.assertTrue(leaked)
        self.assertNotIn("TIER-1-PRIME", cleaned)
        self.assertNotIn("SECRET_TOKEN_999", cleaned)
        self.assertIn("[REDACTED_INTERNAL_DATA]", cleaned)


class TestAntiReaskGuardrail(unittest.TestCase):

    def setUp(self):
        self.guardrail = AntiReaskGuardrail()
        self.known_facts = {
            "account_number": "AC-99482103",
            "loan_account_number": "LN-552190",
            "registered_mobile": "9876543210",
        }

    def test_generates_negative_prompt_directives(self):
        directives = self.guardrail.generate_negative_prompt_directives(self.known_facts)
        self.assertIn("AC-99482103", directives)
        self.assertIn("LN-552190", directives)
        self.assertIn("FORBIDDEN", directives)

    def test_intercepts_reasking_for_account_number(self):
        candidate = "Hello! Please share your account number so I can check your balance."
        has_violations, cleaned, violations = self.guardrail.scan_and_intercept(candidate, self.known_facts)

        self.assertTrue(has_violations)
        self.assertIn("account_number", violations)
        self.assertNotIn("share your account number", cleaned)

    def test_intercepts_reasking_for_loan_number(self):
        candidate = "Could you please provide your loan account number?"
        has_violations, cleaned, violations = self.guardrail.scan_and_intercept(candidate, self.known_facts)

        self.assertTrue(has_violations)
        self.assertIn("loan_account_number", violations)
        self.assertNotIn("provide your loan account number", cleaned)


class TestGuardrailManager(unittest.TestCase):

    def setUp(self):
        self.mgr = GuardrailManager()

    def test_end_to_end_pre_and_post_guardrail(self):
        raw_customer = {
            "customer_name": "Priya Patel",
            "internal_risk_score": 850,
            "account_number": {"value": "AC-12345", "approved_for_display": True, "is_current": True}
        }
        known_facts = {"account_number": "AC-12345"}

        # Pre-inference
        sanitized_ctx, directives, audit = self.mgr.process_pre_inference(raw_customer, known_facts)
        self.assertNotIn("internal_risk_score", sanitized_ctx)
        self.assertIn("account_number", sanitized_ctx)
        self.assertIn("internal_risk_score", audit.blocked_unapproved_fields)
        self.assertIn("AC-12345", directives)

        # Post-inference
        candidate = "Please provide your account number to proceed. Also score is 850."
        final_text, audit_post = self.mgr.process_post_inference(
            candidate_response=candidate,
            blocked_values=["850"],
            known_memory_facts=known_facts,
            audit=audit
        )
        self.assertTrue(audit_post.sanitized_output_applied)
        self.assertIn("account_number", audit_post.reask_violations_intercepted)
        self.assertTrue(audit_post.leakage_detected)
        self.assertNotIn("850", final_text)


if __name__ == "__main__":
    unittest.main()
