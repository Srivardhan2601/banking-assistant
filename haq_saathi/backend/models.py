"""
Pydantic data models and enumerations for Haq Saathi.
"""

from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class LanguageEnum(str, Enum):
    TELUGU = "te-IN"
    HINDI = "hi-IN"
    URDU = "ur-IN"
    ENGLISH = "en-IN"


class WorkerCategory(str, Enum):
    DOMESTIC_WORKER = "domestic_worker"
    DELIVERY_RIDER = "delivery_rider"
    CONSTRUCTION_WORKER = "construction_worker"
    GIG_WORKER = "gig_worker"
    INFORMAL_WORKER = "informal_worker"


class IntentEnum(str, Enum):
    UNPAID_WAGES = "unpaid_wages"
    BELOW_MINIMUM_WAGE = "below_minimum_wage"
    NO_PF_OR_BENEFITS = "no_pf_or_benefits"
    WORKPLACE_INJURY = "workplace_injury"
    WRONGFUL_TERMINATION = "wrongful_termination"
    OTHER = "other"


class StateEnum(str, Enum):
    GREETING = "GREETING"
    UNDERSTAND_PROBLEM = "UNDERSTAND_PROBLEM"
    COLLECT_FIELDS = "COLLECT_FIELDS"
    EXPLAIN_RIGHTS = "EXPLAIN_RIGHTS"
    CONFIRM = "CONFIRM"
    GENERATE_COMPLAINT = "GENERATE_COMPLAINT"
    ROUTE = "ROUTE"
    DONE = "DONE"
    DANGER_OVERRIDE = "DANGER_OVERRIDE"


class ChatRequest(BaseModel):
    session_id: str = Field(..., description="Unique browser session ID")
    language: str = Field(default="te-IN", description="'te-IN', 'hi-IN', 'ur-IN', or 'en-IN'")
    user_text: str = Field(..., description="Transcribed voice text or user input")


class CollectedFields(BaseModel):
    worker_category: Optional[str] = None
    employer_name: Optional[str] = None
    months_unpaid: Optional[str] = None
    amount_owed: Optional[str] = None
    district: Optional[str] = None
    work_location: Optional[str] = None
    injury_details: Optional[str] = None
    worker_name: Optional[str] = None
    optional_phone: Optional[str] = None


class OfficeDetails(BaseModel):
    office_id: str
    district: str
    office_name: str
    address: str
    phone: str
    helpline: str
    working_hours: str
    jurisdiction: str
    is_state_fallback: bool = False


class RightsSummary(BaseModel):
    id: str
    topic: str
    title: str
    plain_explanation: str
    authority: str
    source_name: str
    source_url_placeholder: str
    last_verified_date: str


class ChatResponse(BaseModel):
    session_id: str
    reply_text: str
    reply_language: str
    current_state: StateEnum
    next_action: str
    collected_fields: Dict[str, Any]
    suggested_options: List[str]
    rights_summary: Optional[RightsSummary] = None
    office_details: Optional[OfficeDetails] = None
    complaint_id: Optional[str] = None
    checklist: Optional[List[Dict[str, str]]] = None
    danger_flag: bool = False
    danger_message: Optional[str] = None
    emergency_contacts: Optional[List[Dict[str, str]]] = None


class ComplaintRecord(BaseModel):
    complaint_id: str
    created_at: str
    language: str
    worker_name: str
    worker_category: str
    employer_name: str
    work_location: str
    district: str
    unpaid_period: str
    amount_owed: str
    description: str
    desired_relief: str
    rights_violated: str
    source_citation: str
    routed_office_id: str
    routed_office_name: str
    routed_office_address: str
    phone: Optional[str] = None
