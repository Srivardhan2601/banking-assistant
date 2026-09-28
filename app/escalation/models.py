"""
Data models for the deterministic escalation module.
Defines rule triggers, escalation priorities, and decision payloads.
"""

from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class EscalationPriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class EscalationDepartment(str, Enum):
    HUMAN_SUPPORT = "Human Support Desk"
    DISPUTE_OPERATIONS = "Dispute & Chargeback Ops"
    FRAUD_RISK_TEAM = "Fraud & Cyber Risk Unit"
    LOAN_OFFICER = "Specialist Lending Desk"
    COMPLIANCE_LEGAL = "Regulatory Compliance & Ombudsman Desk"


class EscalationVerdict(BaseModel):
    """
    Structured outcome of the escalation evaluation.
    Readable and transparent for human judges, auditors, and customer handover notes.
    """
    is_escalated: bool = Field(
        default=False,
        description="True if any deterministic rule tripped, requiring human takeover."
    )
    rule_id: Optional[str] = Field(
        default=None,
        description="Unique identifier of the rule that triggered the escalation."
    )
    rule_name: Optional[str] = Field(
        default=None,
        description="Human-readable title of the rule."
    )
    reason: Optional[str] = Field(
        default=None,
        description="Clear, deterministic explanation of why this case was escalated."
    )
    department: Optional[EscalationDepartment] = Field(
        default=None,
        description="Target specialized team to route the customer to."
    )
    priority: Optional[EscalationPriority] = Field(
        default=None,
        description="SLA priority level."
    )
    suggested_action: Optional[str] = Field(
        default=None,
        description="Actionable next step for the human agent receiving the case."
    )
    audit_metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Diagnostic metrics (e.g. matched amounts, repeat count, keywords)."
    )
