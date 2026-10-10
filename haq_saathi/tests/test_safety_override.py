"""
Automated Unit Tests for Haq Saathi Safety Layer.
Validates danger signals overrides (violence, bonded labour, child labour)
and PII redaction (Aadhaar, PAN, Cards).
"""

import unittest
from haq_saathi.backend.safety import (
    check_danger_signals, get_danger_response, sanitize_input, EMERGENCY_CONTACTS
)


class TestSafetyOverride(unittest.TestCase):

    def test_violence_danger_signal_telugu(self):
        user_input = "యజమాని నన్ను కొట్టారు, గదిలో బంధించారు"
        result = check_danger_signals(user_input)
        self.assertIsNotNone(result)
        self.assertTrue(result["danger_detected"])
        self.assertIn(result["category"], ["violence", "bonded_labour"])

    def test_bonded_labour_hindi(self):
        user_input = "ठेकेदार ने बंधक बना रखा है और जाने नहीं दे रहा"
        result = check_danger_signals(user_input)
        self.assertIsNotNone(result)
        self.assertTrue(result["danger_detected"])
        self.assertEqual(result["category"], "bonded_labour")

    def test_child_labour_urdu(self):
        user_input = "چھوٹے بچوں سے جبری مشقت کروائی جا رہی ہے"
        result = check_danger_signals(user_input)
        self.assertIsNotNone(result)
        self.assertTrue(result["danger_detected"])
        self.assertEqual(result["category"], "child_labour")

    def test_danger_response_provides_emergency_numbers(self):
        res = get_danger_response("te-IN")
        self.assertIn("112", res)
        self.assertIn("1800-425-3525", res)

    def test_pii_redaction(self):
        raw_text = "నా ఆధార్ నంబర్ 5432 9876 1234 మరియు కార్డ్ 4111 2222 3333 4444"
        clean = sanitize_input(raw_text)
        self.assertNotIn("5432 9876 1234", clean)
        self.assertNotIn("4111 2222 3333 4444", clean)
        self.assertIn("[REDACTED_ID]", clean)

    def test_normal_wage_query_not_danger(self):
        user_input = "నాకు 3 నెలల జీతం రాలేదు, యజమాని డబ్బులు ఇవ్వడం లేదు"
        result = check_danger_signals(user_input)
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
