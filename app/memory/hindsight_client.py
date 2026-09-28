"""
Dual-Mode Hindsight Cloud Client:
Provides Retain, Recall, and Reflect operations for per-customer memory banks.
Connects directly to live Hindsight Cloud API (https://api.hindsight.vectorize.io)
when HINDSIGHT_API_KEY is configured, while synchronizing with in-memory bank models.
"""

import os
import json
import urllib.request
import urllib.error
from urllib.parse import quote
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from .models import CustomerMemoryBank, RecallResult, RetainPayload
from app.data import db

# Load .env file automatically if present
ENV_PATH = Path(__file__).resolve().parents[2] / ".env"
if ENV_PATH.exists():
    with open(ENV_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())


class HindsightClient:
    """
    Client for Hindsight Cloud Memory Layer.
    Implements live cloud-backed Retain, Recall, and Reflect operations
    against https://api.hindsight.vectorize.io with fallback resilience.
    """

    def __init__(self):
        self.api_key = os.getenv("HINDSIGHT_API_KEY")
        self.endpoint = os.getenv("HINDSIGHT_ENDPOINT", "https://api.hindsight.vectorize.io").rstrip("/")
        if self.endpoint.endswith("/v1"):
            self.endpoint = self.endpoint[:-3]
        self.agent_bank_id = os.getenv("HINDSIGHT_AGENT_BANK_ID", "My AI Assistent").strip()
        self.is_live = bool(self.api_key and self.api_key.startswith("hsk_"))
        self._local_banks: Dict[str, CustomerMemoryBank] = {}
        self._initialize_from_mock_db()

    def _bank_id_for(self, customer_id: str) -> str:
        """Standardized Hindsight Cloud memory bank identifier per customer."""
        clean_cid = customer_id.lower().replace("_", "-")
        return f"banking-{clean_cid}"

    def _recall_cloud_bank(self, bank_id: str, query: str) -> List[str]:
        """Recall text memories from a Hindsight Cloud bank."""
        recall_url = f"{self.endpoint}/v1/default/banks/{quote(bank_id, safe='')}/memories/recall"
        payload = json.dumps({"query": query}).encode("utf-8")
        req = urllib.request.Request(
            recall_url,
            data=payload,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
        )
        with urllib.request.urlopen(req, timeout=1.5) as response:
            if response.status != 200:
                return []
            data = json.loads(response.read().decode("utf-8"))
        return [
            str(text)
            for item in data.get("results", [])
            if (text := item.get("text") or item.get("content"))
        ]

    def _initialize_from_mock_db(self) -> None:
        """Seeds local memory banks using verified customer baseline records."""
        self._local_banks.clear()
        for cust in db.list_all_customers():
            cid = cust["customer_id"]
            # Extract known facts
            known = {
                "customer_name": cust.get("customer_name"),
                "registered_mobile": cust.get("contact", {}).get("registered_mobile"),
                "email": cust.get("contact", {}).get("email"),
                "home_branch": cust.get("contact", {}).get("home_branch"),
            }
            # Add account numbers
            primary_acc = next((a for a in cust.get("accounts", []) if a.get("is_primary")), None)
            if primary_acc:
                known["account_number"] = primary_acc.get("account_number")
                known["account_type"] = primary_acc.get("account_type")

            # Add loan numbers
            active_loan = next((l for l in cust.get("loans", []) if l.get("is_current") and l.get("approved_for_display")), None)
            if active_loan:
                known["loan_account_number"] = active_loan.get("loan_id")
                known["loan_scheme"] = active_loan.get("scheme_name")
                known["loan_status"] = active_loan.get("status")

            # Preferences
            prefs = {
                "preferred_language": cust.get("contact", {}).get("preferred_language", "en-IN"),
                "preferred_channel": cust.get("contact", {}).get("preferred_channel", "text")
            }

            # Past tickets as episodes
            episodes = []
            for tck in cust.get("support_tickets", []):
                episodes.append({
                    "episode_id": tck.get("ticket_id"),
                    "type": "ticket",
                    "category": tck.get("category"),
                    "summary": tck.get("subject"),
                    "status": tck.get("status"),
                    "resolution_notes": tck.get("resolution_notes"),
                    "timestamp": tck.get("created_at")
                })

            # Synthesize reflection insights
            reflections = []
            if cid == "CUST-1001":
                reflections.append("Eligible for PM Mudra Kishore tranche disbursement following e-KYC.")
            elif cid == "CUST-1002":
                reflections.append("Recurring UPI Autopay failures on SIP mandate; high frustration index.")
            elif cid == "CUST-1003":
                reflections.append("High-volume international card spender; requires priority concierge care.")
            elif cid == "CUST-1004":
                reflections.append("100% on-time repayment of SVANidhi 1st tranche; eligible for ₹20,000 2nd tranche.")
            elif cid == "CUST-1005":
                reflections.append("Account security hold active; multiple failed geo-location logins.")

            self._local_banks[cid] = CustomerMemoryBank(
                customer_id=cid,
                known_facts=known,
                interaction_episodes=episodes,
                preferences=prefs,
                reflection_insights=reflections
            )

    def recall(self, customer_id: str, query: str = "", top_k: int = 5) -> RecallResult:
        """
        Recalls the customer's memory bank: verified facts, relevant episodes,
        communication preferences, and reflected behavioral insights.
        Executes live query against Hindsight Cloud when configured.
        """
        bank = self._local_banks.get(customer_id)
        if not bank:
            bank = CustomerMemoryBank(customer_id=customer_id)
            self._local_banks[customer_id] = bank

        cloud_memories: List[str] = []
        agent_knowledge: List[str] = []

        # If live Hindsight Cloud API is active, query the cloud bank
        if self.is_live and query:
            try:
                bank_id = self._bank_id_for(customer_id)
                cloud_memories = self._recall_cloud_bank(bank_id, query)
            except urllib.error.HTTPError:
                # 404 or new bank: fallback gracefully to local verified facts
                pass
            except Exception:
                pass
            if self.agent_bank_id and self.agent_bank_id != self._bank_id_for(customer_id):
                try:
                    agent_knowledge = self._recall_cloud_bank(self.agent_bank_id, query)
                except Exception:
                    # A shared-bank failure must not prevent a reply from using verified local data.
                    pass

        # Local episodic and fact matching
        query_lower = query.lower()
        matched_episodes = []
        for ep in bank.interaction_episodes:
            content_str = f"{ep.get('summary', '')} {ep.get('category', '')} {ep.get('resolution_notes', '')}".lower()
            if any(term in content_str for term in query_lower.split() if len(term) > 3):
                matched_episodes.append(ep)
            elif not query:
                matched_episodes.append(ep)

        if not matched_episodes:
            matched_episodes = bank.interaction_episodes[-top_k:]

        semantic_matches = [
            f"Fact: {k} = {v}" for k, v in bank.known_facts.items() if v
        ]
        semantic_matches.extend(f"Cloud Memory: {text}" for text in cloud_memories)
        semantic_matches.extend(f"Agent Knowledge: {text}" for text in agent_knowledge)

        return RecallResult(
            customer_id=customer_id,
            query=query,
            recalled_facts=bank.known_facts,
            relevant_episodes=matched_episodes,
            preferences=bank.preferences,
            reflection_insights=bank.reflection_insights,
            semantic_matches=semantic_matches[:top_k],
            agent_knowledge=agent_knowledge[:top_k]
        )

    def retain(self, payload: RetainPayload) -> bool:
        """
        Persists a newly completed support interaction into Hindsight Cloud
        and local memory bank.
        """
        cid = payload.customer_id
        bank = self._local_banks.get(cid)
        if not bank:
            bank = CustomerMemoryBank(customer_id=cid)
            self._local_banks[cid] = bank

        # Update known facts
        for k, v in payload.extracted_facts.items():
            if v:
                bank.known_facts[k] = v

        # Add new episode locally
        now_utc = datetime.now(timezone.utc)
        new_episode = {
            "episode_id": f"EP-{now_utc.strftime('%Y%m%d%H%M%S')}",
            "type": "conversation_turn",
            "summary": payload.customer_message[:120],
            "agent_response": payload.agent_response[:120],
            "status": payload.status,
            "escalation_triggered": payload.escalation_triggered,
            "timestamp": now_utc.isoformat()
        }
        bank.interaction_episodes.append(new_episode)

        # Sync with Live Hindsight Cloud
        if self.is_live:
            try:
                bank_id = self._bank_id_for(cid)
                retain_url = f"{self.endpoint}/v1/default/banks/{bank_id}/memories"
                content_text = (
                    f"Customer [{cid}] Inquiry: '{payload.customer_message}'. "
                    f"Agent Resolution: '{payload.agent_response}'. "
                    f"Status: {payload.status}."
                )
                req_data = json.dumps({
                    "items": [{"content": content_text, "type": "observation"}]
                }).encode("utf-8")

                req = urllib.request.Request(
                    retain_url,
                    data=req_data,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    }
                )
                with urllib.request.urlopen(req, timeout=4) as response:
                    return response.status in (200, 201)
            except Exception as e:
                print(f"[Hindsight Cloud] Live Retain notice: {e}")

        return True

    def reflect(self, customer_id: str) -> List[str]:
        """
        Executes a Hindsight Reflect operation to summarize behavioral trends
        and update long-term customer journey insights.
        """
        bank = self._local_banks.get(customer_id)
        if not bank:
            return []

        # If live Hindsight Cloud is active, trigger cloud reflection
        if self.is_live:
            try:
                bank_id = self._bank_id_for(customer_id)
                reflect_url = f"{self.endpoint}/v1/default/banks/{bank_id}/reflect"
                payload = json.dumps({"query": "Synthesize customer journey and resolution trends."}).encode("utf-8")
                req = urllib.request.Request(
                    reflect_url,
                    data=payload,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    }
                )
                with urllib.request.urlopen(req, timeout=4) as response:
                    if response.status == 200:
                        data = json.loads(response.read().decode("utf-8"))
                        insight = data.get("text") or data.get("response")
                        if insight and insight not in bank.reflection_insights:
                            bank.reflection_insights.append(str(insight))
            except Exception as e:
                print(f"[Hindsight Cloud] Live Reflect notice: {e}")

        return bank.reflection_insights

    def reset_to_defaults(self) -> None:
        """Resets all customer memory banks to clean initial state."""
        self._initialize_from_mock_db()


# Global client instance
hindsight = HindsightClient()
