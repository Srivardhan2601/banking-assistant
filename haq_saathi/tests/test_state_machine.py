"""
Automated Unit Tests for Haq Saathi State Machine.
Validates sequential state transitions, question count enforcement (<= 4),
and entity collection.
"""

import unittest
from haq_saathi.backend.models import StateEnum, IntentEnum
from haq_saathi.backend.state_machine import state_machine


class TestStateMachine(unittest.TestCase):

    def setUp(self):
        self.sm = state_machine
        self.session = self.sm.get_initial_session()

    def test_initial_state(self):
        self.assertEqual(self.session["current_state"], StateEnum.GREETING)
        self.assertEqual(self.session["question_count"], 0)
        # All collected fields should start as None
        populated = [k for k, v in self.session["collected_fields"].items() if v is not None]
        self.assertEqual(len(populated), 0)

    def test_transition_from_greeting_to_understand(self):
        next_state, action, options, next_field = self.sm.transition(
            session=self.session,
            user_text="నమస్కారం, నా జీతం రాలేదు",
            extracted_entities={"intent": IntentEnum.UNPAID_WAGES},
            is_danger=False
        )
        self.assertIn(next_state, [StateEnum.UNDERSTAND_PROBLEM, StateEnum.COLLECT_FIELDS])

    def test_question_count_never_exceeds_four(self):
        """Validates that at most 4 follow-up questions are asked."""
        sess = self.sm.get_initial_session()
        sess["current_state"] = StateEnum.COLLECT_FIELDS
        sess["question_count"] = 4  # already asked 4 questions

        next_state, action, options, next_field = self.sm.transition(
            session=sess,
            user_text="హైదరాబాద్ జిల్లా",
            extracted_entities={"district": "Hyderabad"},
            is_danger=False
        )
        # Must move forward to EXPLAIN_RIGHTS or CONFIRM, never stay in COLLECT_FIELDS
        self.assertIn(next_state, [StateEnum.EXPLAIN_RIGHTS, StateEnum.CONFIRM])

    def test_confirm_to_generate_complaint(self):
        sess = self.sm.get_initial_session()
        sess["current_state"] = StateEnum.CONFIRM
        sess["collected_fields"] = {
            "worker_category": "domestic_worker",
            "employer_name": "Rao Garu",
            "months_unpaid": "3 months",
            "amount_owed": "₹15,000",
            "district": "Hyderabad"
        }

        next_state, action, options, next_field = self.sm.transition(
            session=sess,
            user_text="అవును, ఫిర్యాదు తయారు చేయండి",
            extracted_entities={},
            is_danger=False
        )
        self.assertEqual(next_state, StateEnum.GENERATE_COMPLAINT)


if __name__ == "__main__":
    unittest.main()
