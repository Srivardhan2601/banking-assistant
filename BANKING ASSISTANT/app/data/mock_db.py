"""
Mock Database Access Layer:
Loads and queries realistic customer records, loans, transactions,
and government financial schemes.
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional

DATA_DIR = Path(__file__).resolve().parent
CUSTOMERS_FILE = DATA_DIR / "mock_customers.json"
SCHEMES_FILE = DATA_DIR / "schemes_catalog.json"


class MockDatabase:
    """In-memory cache and query layer for mock financial records."""

    def __init__(self):
        self._customers: Dict[str, Any] = {}
        self._schemes: List[Dict[str, Any]] = []
        self._load_data()

    def _load_data(self) -> None:
        if CUSTOMERS_FILE.exists():
            with open(CUSTOMERS_FILE, "r", encoding="utf-8") as f:
                self._customers = json.load(f)
        if SCHEMES_FILE.exists():
            with open(SCHEMES_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                self._schemes = data.get("schemes", [])

    def get_customer(self, customer_id: str) -> Optional[Dict[str, Any]]:
        return self._customers.get(customer_id)

    def list_all_customers(self) -> List[Dict[str, Any]]:
        return list(self._customers.values())

    def get_customer_tickets(self, customer_id: str) -> List[Dict[str, Any]]:
        cust = self.get_customer(customer_id)
        if not cust:
            return []
        return cust.get("support_tickets", [])

    def get_customer_loans(self, customer_id: str) -> List[Dict[str, Any]]:
        cust = self.get_customer(customer_id)
        if not cust:
            return []
        return cust.get("loans", [])

    def get_customer_transactions(self, customer_id: str) -> List[Dict[str, Any]]:
        cust = self.get_customer(customer_id)
        if not cust:
            return []
        return cust.get("transactions", [])

    def get_schemes_catalog(self) -> List[Dict[str, Any]]:
        return self._schemes

    def search_schemes(self, query: str) -> List[Dict[str, Any]]:
        q_lower = query.lower()
        results = []
        for s in self._schemes:
            if (
                q_lower in s.get("name", "").lower()
                or q_lower in s.get("scheme_id", "").lower()
                or q_lower in s.get("target_audience", "").lower()
            ):
                results.append(s)
        return results if results else self._schemes[:2]


# Global singleton instance for easy import across modules
db = MockDatabase()
