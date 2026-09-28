"""
Unit and integration tests for the Voice Interaction Wrapper.
Verifies STT transcription, language detection, translation alignment, and graceful fallback.
"""

import unittest
from app.voice import voice_handler, AudioInputPayload, stt_service, tts_service, language_router


class TestVoiceModule(unittest.TestCase):

    def test_stt_language_detection_hindi(self):
        text = "Mera mudra loan kab tak aayega?"
        lang = stt_service.detect_language_from_text(text)
        self.assertEqual(lang, "hi-IN")

    def test_stt_language_detection_english(self):
        text = "What is the interest rate for PM Mudra Loan?"
        lang = stt_service.detect_language_from_text(text)
        self.assertEqual(lang, "en-IN")

    def test_tts_text_cleaner(self):
        raw = "Your **loan** is [approved](http://example.com) with *8.5%* `rate`."
        clean = tts_service._clean_for_speech(raw)
        self.assertEqual(clean, "Your loan is approved with 8.5% rate.")

    def test_language_router_translates_english_to_hindi_for_tts(self):
        eng = "Your loan application for PM Mudra has been approved."
        aligned = language_router.align_language_for_tts(eng, detected_language="hi-IN")
        # Must be aligned to Hindi for Indic voice
        self.assertTrue(language_router._is_hindi_script(aligned))

    def test_stt_language_detection_tamil(self):
        text = "என் முத்ரா கடன் எப்போது வரும்?"
        lang = stt_service.detect_language_from_text(text)
        self.assertEqual(lang, "ta-IN")

    def test_stt_language_detection_telugu(self):
        text = "నా ముద్రా రుణం ఎప్పుడు వస్తుంది?"
        lang = stt_service.detect_language_from_text(text)
        self.assertEqual(lang, "te-IN")

    def test_stt_language_detection_bengali(self):
        text = "আমার মুদ্রা ঋণ কবে পাব?"
        lang = stt_service.detect_language_from_text(text)
        self.assertEqual(lang, "bn-IN")

    def test_language_router_translates_to_tamil_and_telugu(self):
        eng = "Your loan application for PM Mudra has been approved."
        aligned_ta = language_router.align_language_for_tts(eng, detected_language="ta-IN")
        self.assertTrue(language_router._has_script(aligned_ta, r"[\u0B80-\u0BFF]"))

        aligned_te = language_router.align_language_for_tts(eng, detected_language="te-IN")
        self.assertTrue(language_router._has_script(aligned_te, r"[\u0C00-\u0C7F]"))

    def test_end_to_end_voice_turn(self):
        payload = AudioInputPayload(
            customer_id="CUST-1001",
            language_hint="hi-IN"
        )
        res = voice_handler.handle_voice_turn(
            audio_payload=payload,
            client_transcript="Mera mudra loan kab tak aayega?",
            client_lang="hi-IN"
        )
        self.assertFalse(res.fallback_triggered)
        self.assertEqual(res.stt.detected_language, "hi-IN")
        self.assertTrue(len(res.tts.synthesized_text) > 0)
        self.assertIn("response", res.pipeline_response)


if __name__ == "__main__":
    unittest.main()
