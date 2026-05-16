"""Handler for Brevo incoming webhooks."""

import logging
import os
from typing import Dict, Any, Optional
from src.safety import pauseContactAutomation
from src.database import StateDatabase
from src.ghl_client import GHLClient
from src.settings import Settings

logger = logging.getLogger(__name__)

def handle_brevo_webhook(payload: Dict[str, Any]) -> bool:
    """Process incoming webhook events from Brevo.
    
    Expected events: delivered, opened, clicked, unique_opened, 
    soft_bounce, hard_bounce, invalid_email, deferred, complained, 
    unsubscribed, error, blocked, proxy_open, replied.
    
    Args:
        payload: The JSON payload from Brevo.
        
    Returns:
        True if processed successfully.
    """
    event = payload.get("event")
    email = payload.get("email")
    
    if not event or not email:
        logger.error(f"Invalid Brevo webhook payload: {payload}")
        return False

    logger.info(f"Brevo Event Received: {event} for {email}")

    # Unified Pause Safety Invariant
    # We MUST pause automation on 'replied', 'unsubscribed', or 'complained'
    critical_events = ["replied", "unsubscribed", "complained"]
    
    if event in critical_events:
        reason = f"Brevo webhook: {event}"
        logger.info(f"CRITICAL EVENT: {event}. Triggering unified pause for {email}.")
        
        db = StateDatabase()
        state = db.get_state_by_email(email)
        
        if state:
            pauseContactAutomation(state.lead_id, reason)
            
            # Notify GHL of the conversion/reply
            settings = Settings()
            ghl = GHLClient(
                api_key=os.getenv('GHL_PRIVATE_INTEGRATION_TOKEN') or settings.get('ghl.private_integration_token'),
                location_id=os.getenv('GHL_LOCATION_ID') or settings.get('ghl.location_id')
            )
            
            # Post the event as an inbound message
            ghl_contact_id = state.metadata.get('ghl_contact_id')
            if not ghl_contact_id:
                contact = ghl.get_contact_by_email(email)
                if contact: ghl_contact_id = contact['id']
            
            if ghl_contact_id:
                ghl.create_conversation_message(ghl_contact_id, "Email", f"Event: {event}", direction="inbound")
        else:
            logger.error(f"Could not find lead in database for email {email} to pause automation.")
            # Even if not in DB, we should log this heavily as it's a safety gap
            return False

    return True
