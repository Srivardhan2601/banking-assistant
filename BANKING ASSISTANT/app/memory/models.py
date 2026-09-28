"""
Data models for Hindsight Cloud Memory Layer.
Defines schemas for Retain, Recall, and Reflect operations.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field


class MemoryItem(BaseModel):
    id: str = Field(..., description="Unique memory record ID.")
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    memory_type: str = Field(..., description="'fact', 'interaction', 'preference', or 'reflection'")
    content: str = Field(..., description="Semantic text representation of the memory.")
    metadata: Dict[str, Any] = Field(default_factory=dict)


class CustomerMemoryBank(BaseModel):
    customer_id: str
    known_facts: Dict[str, Any] = Field(
        default_factory=dict,
        description="Verified customer attributes (e.g. loan ID, account, phone)."
    )
    interaction_episodes: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Chronological record of past support turns and ticket outcomes."
    )
    preferences: Dict[str, Any] = Field(
        default_factory=dict,
        description="Communication and banking preferences."
    )
    reflection_insights: List[str] = Field(
        default_factory=list,
        description="Synthesized patterns from Hindsight Reflect operation."
    )


class RecallResult(BaseModel):
    customer_id: str
    query: str
    recalled_facts: Dict[str, Any] = Field(default_factory=dict)
    relevant_episodes: List[Dict[str, Any]] = Field(default_factory=list)
    preferences: Dict[str, Any] = Field(default_factory=dict)
    reflection_insights: List[str] = Field(default_factory=list)
    semantic_matches: List[str] = Field(default_factory=list)


class RetainPayload(BaseModel):
    customer_id: str
    customer_message: str
    agent_response: str
    extracted_facts: Dict[str, Any] = Field(default_factory=dict)
    escalation_triggered: bool = False
    status: str = "RESOLVED"
