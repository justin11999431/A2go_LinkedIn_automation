"""Sequencer engine for coordinating multi-step outreach."""

import logging
import os
from datetime import datetime, timedelta
from typing import List, Optional
from src.settings import Settings
from src.database import StateDatabase
from src.models import SequenceState
from src.brevo_client import BrevoClient
from src.ghl_client import GHLClient
from src.linkedin_adapter import LinkedInAdapter
from src.templates import EMAIL_TEMPLATES, LINKEDIN_TEMPLATES

logger = logging.getLogger(__name__)

class Sequencer:
    """Orchestrates the timing and execution of sequence steps."""
    
    def __init__(self, db_path: str = "data/automation.db"):
        self.settings = Settings()
        self.db = StateDatabase(db_path)
        self.brevo = BrevoClient(os.getenv('BREVO_API_KEY') or self.settings.get('brevo.api_key'))
        self.ghl = GHLClient(
            api_key=os.getenv('GHL_PRIVATE_INTEGRATION_TOKEN') or self.settings.get('ghl.private_integration_token'),
            location_id=os.getenv('GHL_LOCATION_ID') or self.settings.get('ghl.location_id')
        )
        # Consistent dry run handling
        dry_run_env = os.getenv('DRY_RUN', 'true').lower()
        self.is_dry_run = (dry_run_env == 'true')
        
        self.linkedin = LinkedInAdapter(is_dry_run=self.is_dry_run)

    def run_iteration(self):
        """Run one iteration of the sequencer across all active leads."""
        logger.info("Starting sequence iteration...")
        
        conn = self.db._get_connection()
        try:
            cursor = conn.execute("SELECT lead_id FROM sequence_state WHERE is_paused = 0")
            lead_ids = [row[0] for row in cursor.fetchall()]
        finally:
            conn.close()

        for lead_id in lead_ids:
            self.process_lead(lead_id)

    def process_lead(self, lead_id: str):
        """Process a single lead's next step (Email and LinkedIn)."""
        state = self.db.get_state(lead_id)
        if not state or state.is_paused:
            return

        now = datetime.now()
        
        # 1. Process Email Sequence
        if not state.next_step_due_at or state.next_step_due_at <= now:
            self._handle_email_sequence(state, now)
            
        # 2. Process LinkedIn Sequence (Parallel or staggered)
        self._handle_linkedin_sequence(state, now)

    def _handle_email_sequence(self, state: SequenceState, now: datetime):
        """Logic for advancing email steps."""
        next_step = state.current_email_step + 1
        if next_step > 7:
            return

        if self.execute_email_step(state, next_step):
            state.current_email_step = next_step
            state.last_interaction_at = now
            state.next_step_due_at = now + timedelta(days=2)
            self.db.upsert_state(state)
            logger.info(f"Lead {state.email} advanced to Email Step {next_step}")

    def _handle_linkedin_sequence(self, state: SequenceState, now: datetime):
        """Logic for advancing LinkedIn steps."""
        # Initial Connection Request (Step 0 -> 1)
        if state.current_linkedin_step == 0:
            if self.execute_linkedin_step(state, "connection_request"):
                state.current_linkedin_step = 1
                self.db.upsert_state(state)
                logger.info(f"Lead {state.email} sent LinkedIn Connection Request")
        
        # Follow-ups (Requires LinkedIn Status to be 'Accepted')
        # In this implementation, we'd check state.linkedin_status == 'accepted'
        # which would be updated by a background checker script.
        elif state.linkedin_status.lower() in ['accepted', 'connected']:
            # Staggered follow-ups (Colleague, Customer, Bridge, Final)
            next_li_step = state.current_linkedin_step + 1
            if next_li_step > 5:
                return
            
            # Map step number to template key
            li_map = {2: "colleague", 3: "customer", 4: "bridge", 5: "final"}
            template_key = li_map.get(next_li_step)
            
            if template_key and self.execute_linkedin_step(state, template_key):
                state.current_linkedin_step = next_li_step
                self.db.upsert_state(state)
                logger.info(f"Lead {state.email} advanced to LinkedIn Step {next_li_step} ({template_key})")

    def execute_email_step(self, state: SequenceState, step_number: int) -> bool:
        """Send the specified email for the given step."""
        template = EMAIL_TEMPLATES.get(step_number)
        if not template:
            return False

        params = self._get_template_params(state)
        subject = template['subject'].format(**params)
        html = template['html'].format(**params)

        sender_name = self.settings.get('brevo.sender_name', 'A2go.ai')
        sender_email = self.settings.get('brevo.sender_email', 'outreach@a2gotools.com')

        if self.is_dry_run:
            logger.info(f"[DRY RUN] Email {step_number} to {state.email}")
            return True
        else:
            try:
                self.brevo.send_email(state.email, subject, html, sender_name, sender_email, params['first_name'])
                # Notify GHL
                self._notify_ghl(state, "Email", f"Sent: {subject}")
                return True
            except Exception:
                return False

    def execute_linkedin_step(self, state: SequenceState, template_key: str) -> bool:
        """Execute a LinkedIn step via the adapter."""
        template = LINKEDIN_TEMPLATES.get(template_key)
        if not template:
            return False

        params = self._get_template_params(state)
        message = template.format(**params)
        linkedin_url = state.metadata.get('linkedin_url')

        if not linkedin_url:
            logger.warning(f"No LinkedIn URL for {state.email}")
            return False

        if template_key == "connection_request":
            success = self.linkedin.send_connection_request(linkedin_url, message)
            if success and not self.is_dry_run:
                self._notify_ghl(state, "LinkedIn", f"Connection Request: {message[:100]}...")
            return success
        else:
            success = self.linkedin.send_followup_message(linkedin_url, message)
            if success and not self.is_dry_run:
                self._notify_ghl(state, "LinkedIn", f"Follow-up ({template_key}): {message[:100]}...")
            return success

    def _notify_ghl(self, state: SequenceState, type: str, body: str, direction: str = "outbound"):
        """Utility to post activity to GHL."""
        # Find GHL contact ID if not in metadata
        ghl_contact_id = state.metadata.get('ghl_contact_id')
        if not ghl_contact_id:
            contact = self.ghl.get_contact_by_email(state.email)
            if contact:
                ghl_contact_id = contact['id']
                state.metadata['ghl_contact_id'] = ghl_contact_id
                self.db.upsert_state(state)
        
        if ghl_contact_id:
            self.ghl.create_conversation_message(ghl_contact_id, type, body, direction)

    def _get_template_params(self, state: SequenceState) -> Dict[str, str]:
        """Helper to extract template parameters from metadata."""
        return {
            'first_name': state.metadata.get('first_name', 'there'),
            'company': state.metadata.get('company', 'your company'),
            'industry': state.metadata.get('industry', 'your industry'),
            'location': state.metadata.get('location', 'your area')
        }

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    sequencer = Sequencer()
    sequencer.run_iteration()
