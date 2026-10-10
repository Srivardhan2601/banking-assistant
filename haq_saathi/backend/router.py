"""
District and worker-category routing engine for Haq Saathi.
Matches informal workers to verified Telangana labour department offices.
"""

import json
from pathlib import Path
from typing import Optional, List, Dict, Any
from .models import OfficeDetails


OFFICES_FILE = Path(__file__).resolve().parent.parent / "data" / "labour_offices.json"


class LabourOfficeRouter:
    """Routes complaints to jurisdiction offices based on District and Category."""

    def __init__(self, data_path: Path = OFFICES_FILE):
        self.data_path = data_path
        self.offices = self._load_offices()
        self.state_fallback = self._get_fallback_office()

    def _load_offices(self) -> List[Dict[str, Any]]:
        if not self.data_path.exists():
            print(f"[Router] Offices data file not found at {self.data_path}")
            return []
        try:
            with open(self.data_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[Router] Error reading labour_offices.json: {e}")
            return []

    def _get_fallback_office(self) -> Dict[str, Any]:
        for o in self.offices:
            if o.get("is_state_fallback"):
                return o
        if self.offices:
            return self.offices[-1]
        return {
            "office_id": "DEFAULT-STATE",
            "district": "Telangana State",
            "office_name": "Office of the Commissioner of Labour, Telangana State",
            "address": "T. Anjaiah Bhavan, RTC X Roads, Hyderabad - 500020",
            "phone": "+91-40-27616233",
            "helpline": "1800-425-3525",
            "working_hours": "10:30 AM - 5:00 PM",
            "jurisdiction": "Statewide Jurisdiction",
            "is_state_fallback": True
        }

    DISTRICT_ALIASES = {
        "హైదరాబాద్": "hyderabad",
        "हैदराबाद": "hyderabad",
        "حیدرآباد": "hyderabad",
        "hyd": "hyderabad",
        "వరంగల్": "warangal",
        "वारंगल": "warangal",
        "ورنگل": "warangal",
        "రంగారెడ్డి": "rangareddy",
        "रंगारेड्डी": "rangareddy",
        "رنگا ریڈی": "rangareddy",
        "మేడ్చల్": "medchal",
        "मेडचल": "medchal",
        "میڈچل": "medchal",
        "నిజామాబాద్": "nizamabad",
        "निज़ामाबाद": "nizamabad",
        "కరీంనగర్": "karimnagar",
        "करीमनगर": "karimnagar",
        "ఖమ్మం": "khammam",
        "खम्मम": "khammam"
    }

    def route_complaint(self, district: Optional[str] = None, worker_category: str = "informal_worker") -> OfficeDetails:
        """
        Routing logic:
        1. Match by district (case-insensitive substring & multilingual aliases)
        2. Match by worker category within that district if multiple entries exist
        3. Fall back to state-level headquarters
        """
        if not district:
            return self._to_office_details(self.state_fallback)

        district_clean = district.lower().strip()
        # Check alias
        for alias, canon in self.DISTRICT_ALIASES.items():
            if alias in district_clean:
                district_clean = canon
                break

        matching_district_offices = []

        for o in self.offices:
            if o.get("is_state_fallback"):
                continue
            office_dist = o.get("district", "").lower()
            if district_clean in office_dist or office_dist in district_clean:
                matching_district_offices.append(o)

        if matching_district_offices:
            # Check worker category match
            for o in matching_district_offices:
                if worker_category in o.get("categories_handled", []):
                    return self._to_office_details(o)
            # Default to first district office match
            return self._to_office_details(matching_district_offices[0])

        # If district not found in localized list, return statewide grievance cell
        return self._to_office_details(self.state_fallback)

    def _to_office_details(self, data: Dict[str, Any]) -> OfficeDetails:
        return OfficeDetails(
            office_id=data.get("office_id", "OFFICE-01"),
            district=data.get("district", "Telangana"),
            office_name=data.get("office_name", "District Labour Office"),
            address=data.get("address", "Collectorate Compound"),
            phone=data.get("phone", "+91-40-27616233"),
            helpline=data.get("helpline", "1800-425-3525"),
            working_hours=data.get("working_hours", "10:30 AM - 5:00 PM"),
            jurisdiction=data.get("jurisdiction", "District Level"),
            is_state_fallback=data.get("is_state_fallback", False)
        )

    def list_all_offices(self) -> List[Dict[str, Any]]:
        return self.offices

    def get_all_offices(self) -> List[Dict[str, Any]]:
        return self.offices


router = LabourOfficeRouter()
