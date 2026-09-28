"""
End-to-End Orchestrator Integration Tests:
Verifies happy path, deterministic escalation paths, and zero-redundancy memory enforcement.
"""

import unittest
from app.orchestrator import orchestrator
from app.memory import hindsight


class TestOrchestratorIntegration(unittest.TestCase):

    def setUp(self):
        hindsight.reset_to_defaults()

    def test_happy_path_does_not_repeat_questions(self):
        """
        Demo Path 1: Aarav Sharma asks about his PM Mudra Loan.
        The orchestrator must NOT ask for his loan ID, account, or phone number.
        """
        cid = "CUST-1001"
        res = orchestrator.process_message(
            customer_id=cid,
            customer_message="What is the current status of my PM Mudra loan application?",
            channel="text",
            detected_language="en-IN"
        )

        self.assertFalse(res["is_escalated"])
        response_text = res["response"].lower()

        # Must mention the known loan
        self.assertIn("mudra", response_text)
        self.assertIn("approved", response_text)

        # Must NOT re-ask for known identifiers
        self.assertNotIn("what is your loan", response_text)
        self.assertNotIn("provide your account", response_text)
        self.assertNotIn("share your phone", response_text)

        # Guardrail audit must report blocked internal fields
        audit = res["guardrail_audit"]
        self.assertTrue(any("internal_risk_score" in f for f in audit["blocked_unapproved_fields"]))
        self.assertTrue(any("cibil_internal_band" in f for f in audit["blocked_unapproved_fields"]))

    def test_escalation_path_repeated_unresolved_tickets(self):
        """
        Demo Path 2: Priya Patel has 2 unresolved tickets regarding UPI Autopay.
        Orchestrator must deterministically escalate under Rule ESC-04 without asking redundant questions.
        """
        cid = "CUST-1002"
        res = orchestrator.process_message(
            customer_id=cid,
            customer_message="My SIP auto debit failed again this month!",
            channel="text",
            detected_language="en-IN"
        )

        self.assertTrue(res["is_escalated"])
        self.assertEqual(res["escalation"]["rule_id"], "ESC-04")
        self.assertEqual(res["escalation"]["priority"], "HIGH")
        self.assertIn("Human Support Desk", res["escalation"]["department"])

    def test_escalation_path_high_value_dispute(self):
        """
        Demo Path 3: Disputed amount > ₹25,000 threshold.
        Must deterministically escalate under Rule ESC-03.
        """
        cid = "CUST-1003"
        res = orchestrator.process_message(
            customer_id=cid,
            customer_message="I want to dispute a transaction charge of ₹48,500 on my credit card in Dubai!",
            channel="text",
            detected_language="en-IN"
        )

        self.assertTrue(res["is_escalated"])
        self.assertEqual(res["escalation"]["rule_id"], "ESC-03")
        self.assertEqual(res["escalation"]["priority"], "HIGH")
        self.assertIn("Dispute & Chargeback Ops", res["escalation"]["department"])

    def test_multilingual_hindi_happy_path(self):
        """
        Demo Path 4: Sunita Devi inquires about PM SVANidhi in Hindi.
        """
        cid = "CUST-1004"
        res = orchestrator.process_message(
            customer_id=cid,
            customer_message="Mera svanidhi ka agla loan kab milega?",
            channel="voice",
            detected_language="hi-IN"
        )

        self.assertFalse(res["is_escalated"])
        self.assertIn("20,000", res["response"])

    def test_combined_loan_and_refund_question_answers_both_parts_carefully(self):
        res = orchestrator.process_message(
            customer_id="CUST-1001",
            customer_message="What is my loan disbursement date, and what refund period is guaranteed?",
            channel="text",
            detected_language="en-IN"
        )

        response_text = res["response"].lower()
        self.assertIn("expected disbursement date", response_text)
        self.assertIn("estimate, not a guarantee", response_text)
        self.assertIn("refund", response_text)
        self.assertIn("can't verify a refund period or guarantee", response_text)
        self.assertNotIn("all verification details are complete", response_text)


if __name__ == "__main__":
    unittest.main()
