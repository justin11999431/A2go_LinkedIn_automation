"""Core safety logic for unified automation pausing."""

import logging
from typing import Optional
from datetime import datetime
from src.database import StateDatabase

logger = logging.getLogger(__name__)

def pauseContactAutomation(lead_id: str, reason: str, db_path: str = "data/automation.db") -> bool:
    """Unified function to immediately stop all automated outreach for a contact.
    
    This is the core safety invariant of the A2go.ai system.
    
    Args:
        lead_id: Unique identifier for the lead/contact.
        reason: Clear reason for the pause (e.g., 'Replied on LinkedIn', 'Opt-out').
        db_path: Path to the state database.
        
    Returns:
        True if the pause was successfully recorded.
    """
    logger.info(f"PAUSE REQUESTED: Lead {lead_id} | Reason: {reason}")
    
    db = StateDatabase(db_path)
    state = db.get_state(lead_id)
    
    if not state:
        # If no state exists, we can't pause what we don't know about.
        # However, for safety, if lead_id IS an email, we can use it.
        from src.models import SequenceState
        email = lead_id if "@" in lead_id else "unknown@example.com"
        state = SequenceState(lead_id=lead_id, email=email)
    
    state.is_paused = True
    state.pause_reason = reason
    state.last_interaction_at = datetime.now()
    
    try:
        db.upsert_state(state)
        logger.info(f"PAUSE SUCCESSFUL: Lead {lead_id} is now paused.")
        
        # NOTE: In future phases, this will trigger:
        # 1. GHL status update
        # 2. Brevo cancellation
        # 3. MessageBird cancellation
        # 4. SalesRobot cancellation
        
        return True
    except Exception as e:
        logger.error(f"PAUSE FAILED: Lead {lead_id} could not be paused! Error: {e}")
        # CRITICAL: This is a safety failure. Should trigger emergency notifications.
        return False

def is_automation_paused(lead_id: str, db_path: str = "data/automation.db") -> bool:
    """Check if automation is paused for a contact.
    
    Args:
        lead_id: Unique identifier for the lead.
        db_path: Path to the state database.
        
    Returns:
        True if automation is paused.
    """
    db = StateDatabase(db_path)
    state = db.get_state(lead_id)
    return state.is_paused if state else False
