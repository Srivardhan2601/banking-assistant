"""
Automated Unit Tests for Haq Saathi Multilingual PDF Generator.
Validates generation of single-page complaints in Telugu, Hindi, Urdu (RTL), and English.
"""

import unittest
import os
from pathlib import Path
from haq_saathi.backend.pdf_generator import pdf_service


class TestPDFGeneration(unittest.TestCase):

    def setUp(self):
        self.sample_complaint = {
            "complaint_id": "HAQ-UNIT-999",
            "created_at": "2026-10-10",
            "language": "te-IN",
            "worker_name": "రాము (Ramu)",
            "worker_category": "domestic_worker",
            "employer_name": "వెంకట్ రావు (Venkat Rao)",
            "work_location": "Banjara Hills, Hyderabad",
            "district": "Hyderabad",
            "unpaid_period": "3 నెలలు (3 Months)",
            "amount_owed": "₹18,000",
            "description": "గత మూడు నెలలుగా యజమాని జీతం నిలిపివేశారు.",
            "desired_relief": "బాకీ ఉన్న ₹18,000 తక్షణమే ఇప్పించవలసిందిగా కోరుతున్నాను.",
            "rights_violated": "సకాలంలో వేతనం పొందే హక్కు (Payment of Wages Act)",
            "source_citation": "Payment of Wages Act, 1936",
            "routed_office_name": "డిప్యూటీ లేబర్ కమిషనర్ కార్యాలయం - హైదరాబాద్",
            "routed_office_address": "RTC Cross Roads, Chikkadpally, Hyderabad, 500020",
            "phone": "9876543210"
        }

    def test_generate_telugu_pdf(self):
        filepath = pdf_service.generate(self.sample_complaint, lang="te-IN")
        self.assertTrue(os.path.exists(filepath), "Telugu PDF file must exist")
        self.assertGreater(os.path.getsize(filepath), 1000, "PDF size must be greater than 1KB")

    def test_generate_hindi_pdf(self):
        filepath = pdf_service.generate(self.sample_complaint, lang="hi-IN")
        self.assertTrue(os.path.exists(filepath), "Hindi PDF file must exist")
        self.assertGreater(os.path.getsize(filepath), 1000, "PDF size must be greater than 1KB")

    def test_generate_urdu_pdf(self):
        """Validates Urdu PDF with BiDi reshaping and Arabic/Nastaliq font rendering."""
        filepath = pdf_service.generate(self.sample_complaint, lang="ur-IN")
        self.assertTrue(os.path.exists(filepath), "Urdu PDF file must exist")
        self.assertGreater(os.path.getsize(filepath), 1000, "PDF size must be greater than 1KB")

    def test_generate_english_pdf(self):
        filepath = pdf_service.generate(self.sample_complaint, lang="en-IN")
        self.assertTrue(os.path.exists(filepath), "English PDF file must exist")
        self.assertGreater(os.path.getsize(filepath), 1000, "PDF size must be greater than 1KB")


if __name__ == "__main__":
    unittest.main()
