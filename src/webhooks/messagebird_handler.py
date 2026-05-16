"""Handler for MessageBird incoming webhooks."""

import logging
from typing import Dict, Any, Optional
from src.safety import pauseContactAutomation
from src.database import StateDatabase
from src.ghl_client import GHLClient
from src.settings import Settings

logger = logging.getLogger(__name__)

def handle_messagebird_webhook(payload: Dict[str, Any]) -> bool:
    """Process incoming SMS messages from MessageBird.
    
    Expected payload format:
    {
        "id": "...",
        "originator": "recipient_phone",
        "recipient": "our_bird_number",
        "body": "reply text"
    }
    """
    originator = payload.get("originator")
    body = payload.get("body", "").strip().lower()
    
    if not originator:
        logger.error(f"Invalid MessageBird webhook payload: {payload}")
        return False

    logger.info(f"SMS Received from {originator}: {body}")

    # Unified Pause Safety Invariant
    reason = f"SMS reply received: {body[:30]}"
    logger.info(f"SMS reply detected. Triggering unified pause for lead with phone {originator}.")
    
    db = StateDatabase()
    state = db.get_state_by_phone(originator)
    
    if state:
        pauseContactAutomation(state.lead_id, reason)
        
        # Notify GHL
        settings = Settings()
        ghl = GHLClient(settings.get('ghl.private_integration_token'), settings.get('ghl.location_id'))
        
        ghl_contact_id = state.metadata.get('ghl_contact_id')
        if not ghl_contact_id:
            contact = ghl.get_contact_by_email(state.email)
            if contact: ghl_contact_id = contact['id']
            
        if ghl_contact_id:
            ghl.create_conversation_message(ghl_contact_id, "SMS", body, direction="inbound")
            
        return True
    else:
        logger.error(f"Could not find lead in database for phone {originator} to pause automation.")
        return False
