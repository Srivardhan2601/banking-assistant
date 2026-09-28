"""
Data models for the Financial Services Guardrail Layer.
Defines schemas for display entitlement, memory anti-redundancy, and audit logs.
"""

from typing import List, Dict, Any, Optional, Set
from pydantic import BaseModel, Field


class GuardrailAuditReport(BaseModel):
    """
    Transparent audit log capturing all guardrail interventions.
    Rendered directly in the judge dashboard and API response.
    """
    passed: bool = Field(
        default=True,
        description="True if all guardrail checks passed without severe integrity violations."
    )
    approved_fields_passed: List[str] = Field(
        default_factory=list,
        description="Attributes verified with approved_for_display=True and is_current=True."
    )
    blocked_unapproved_fields: List[str] = Field(
        default_factory=list,
        description="Internal or non-approved fields stripped before context assembly."
    )
    blocked_stale_records: List[str] = Field(
        default_factory=list,
        description="Outdated records stripped because is_current=False."
    )
    known_entities_protected: List[str] = Field(
        default_factory=list,
        description="Entities present in Hindsight memory shielded from re-asking."
    )
    reask_violations_intercepted: List[str] = Field(
        default_factory=list,
        description="Agent questions asking for already-known info that were intercepted/blocked."
    )
    leakage_detected: bool = Field(
        default=False,
        description="True if sensitive unapproved tokens were detected in candidate response."
    )
    sanitized_output_applied: bool = Field(
        default=False,
        description="True if the response was sanitized or rewritten by the guardrail."
    )
