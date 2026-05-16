"""Handler for GoHighLevel incoming webhooks."""

import logging
from typing import Dict, Any
from src.safety import pauseContactAutomation
from src.database import StateDatabase

logger = logging.getLogger(__name__)

def handle_ghl_webhook(payload: Dict[str, Any]) -> bool:
    """Process incoming webhook events from GoHighLevel.
    
    Supported events:
    - appointment_created
    - contact_created
    - contact_tag_added
    
    Args:
        payload: The JSON payload from GHL.
    """
    event_type = payload.get("type")
    
    if event_type == "appointment":
        return _handle_appointment_event(payload)
    elif event_type == "contact_tag_added":
        return _handle_tag_event(payload)
    
    return False

def _handle_appointment_event(payload: Dict[str, Any]) -> bool:
    """Pause automation when an appointment is booked."""
    # GHL V2 payload structure for appointments
    contact_id = payload.get("contactId")
    email = payload.get("email")
    
    if not contact_id and not email:
        logger.error(f"Invalid GHL appointment payload: {payload}")
        return False

    logger.info(f"GHL Appointment Booked: {email or contact_id}")
    
    db = StateDatabase()
    # Lookup by email or GHL contact ID (stored in metadata)
    state = None
    if email:
        state = db.get_state_by_email(email)
    
    if state:
        reason = "GHL Appointment Booked"
        logger.info(f"CONVERSION DETECTED: {email}. Pausing all automation.")
        pauseContactAutomation(state.lead_id, reason)
        return True
    
    return False

def _handle_tag_event(payload: Dict[str, Any]) -> bool:
    """Pause automation if a specific 'Stop' tag is added in GHL."""
    tag = payload.get("tag")
    email = payload.get("email")
    
    if tag == "Stop Outreach":
        logger.info(f"Manual 'Stop Outreach' tag detected in GHL for {email}")
        db = StateDatabase()
        state = db.get_state_by_email(email)
        if state:
            pauseContactAutomation(state.lead_id, "GHL Tag: Stop Outreach")
            return True
            
    return False
