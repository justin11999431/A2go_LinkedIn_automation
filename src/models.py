"""Models for lead data and sequence state."""

from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from datetime import datetime

class Lead(BaseModel):
    """Lead data model."""
    lead_id: str
    first_name: str
    last_name: str
    email: str
    company: str
    title: Optional[str] = None
    linkedin_url: Optional[str] = None
    phone: Optional[str] = None
    status: str = "new"
    cohort_id: Optional[str] = None
    ghl_contact_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class ChannelState(BaseModel):
    """State for a specific outreach channel."""
    status: str = "pending"  # pending, active, completed, paused, error
    last_action: Optional[str] = None
    last_action_at: Optional[datetime] = None

class SequenceState(BaseModel):
    """Tracks the state of a lead in the 7-email sequence and multi-channel workflow."""
    lead_id: str
    email: str
    phone: Optional[str] = None
    current_email_step: int = 0  # 0 to 7
    current_linkedin_step: int = 0  # 0: None, 1: ConnReq, 2-5: Followups
    email_status: str = "pending"
    linkedin_status: str = "pending"
    sms_status: str = "pending"
    last_interaction_at: Optional[datetime] = None
    is_paused: bool = False
    pause_reason: Optional[str] = None
    next_step_due_at: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
