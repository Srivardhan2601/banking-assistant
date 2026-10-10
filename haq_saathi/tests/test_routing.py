"""
Automated Unit Tests for Haq Saathi District & Worker Category Routing.
Validates district-first matching and state-level fallback.
"""

import unittest
from haq_saathi.backend.router import router


class TestRouting(unittest.TestCase):

    def test_hyderabad_routing(self):
        office = router.route_complaint("Hyderabad", "domestic_worker")
        self.assertEqual(office.district, "Hyderabad")
        self.assertIn("Hyderabad", office.office_name)
        self.assertIn("27616233", office.phone)

    def test_warangal_delivery_routing(self):
        office = router.route_complaint("Warangal", "delivery_rider")
        self.assertEqual(office.district, "Warangal")
        self.assertIn("Warangal", office.office_name)

    def test_rangareddy_construction_routing(self):
        office = router.route_complaint("Rangareddy", "construction_worker")
        self.assertEqual(office.district, "Rangareddy")
        self.assertIn("Rangareddy", office.office_name)

    def test_fallback_for_unlisted_district(self):
        """Unlisted or unknown district should fall back to Telangana State Labour Commissionerate."""
        office = router.route_complaint("Adilabad", "informal_worker")
        self.assertIsNotNone(office)
        self.assertTrue("State" in office.office_name or "Telangana" in office.jurisdiction or office.district == "All Telangana")

    def test_telugu_district_name_resolution(self):
        """Telugu script district name should resolve correctly."""
        office = router.route_complaint("హైదరాబాద్", "domestic_worker")
        self.assertEqual(office.district, "Hyderabad")


if __name__ == "__main__":
    unittest.main()
