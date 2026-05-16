"""Adapter for Salesrobot LinkedIn outreach."""

import logging
import os
from typing import Dict, Any, Optional
from src.salesrobot_client import SalesrobotClient
from src.settings import Settings

logger = logging.getLogger(__name__)

class LinkedInAdapter:
    """Adapter to interface with Salesrobot for LinkedIn outreach."""
    
    def __init__(self, is_dry_run: Optional[bool] = None):
        self.settings = Settings()
        self.client = SalesrobotClient(
            api_key=os.getenv('SALESROBOT_API_KEY') or self.settings.get('salesrobot.api_key'),
            linkedin_account_uuid=os.getenv('LINKEDIN_ACCOUNT_UUID') or self.settings.get('salesrobot.linkedin_account_uuid')
        )
        self.is_dry_run = is_dry_run if is_dry_run is not None else self.settings.is_dry_run()

    def send_connection_request(self, linkedin_url: str, message: str) -> bool:
        """Send a LinkedIn connection request via SalesRobot campaign enrollment.

        SalesRobot's recommended pattern is to create a lead record then enroll
        them in a pre-configured campaign that sends the connection request.

        Args:
            linkedin_url: Target LinkedIn profile URL
            message: Personalization note attached to the lead (used by campaign template)
        """
        if self.is_dry_run:
            logger.info(
                f"[DRY RUN] Would send LinkedIn Connection Request to {linkedin_url} "
                f"| Message: {message[:50]}..."
            )
            return True

        try:
            campaign_id = (
                os.getenv('SALESROBOT_CONNECTION_CAMPAIGN_ID')
                or self.settings.get('salesrobot.connection_campaign_id')
            )
            if not campaign_id:
                logger.error(
                    "SALESROBOT_CONNECTION_CAMPAIGN_ID is not set. "
                    "Add it to .env or settings.json before enabling LinkedIn outreach."
                )
                return False

            # Create the lead in SalesRobot (idempotent — duplicate LinkedIn URLs are handled by SR)
            lead_data = {
                "linkedinUrl": linkedin_url,
                "note": message[:300],  # SalesRobot note max 300 chars
                "linkedinAccountUuid": self.client.linkedin_account_uuid
            }
            lead_response = self.client.create_lead(lead_data)

            # SR returns the lead under data.id or id depending on endpoint version
            lead_id = (
                lead_response.get("data", {}).get("id")
                or lead_response.get("id")
            )
            if not lead_id:
                logger.error(
                    f"SalesRobot did not return a lead ID for {linkedin_url}. "
                    f"Response: {lead_response}"
                )
                return False

            # Enroll lead into connection-request campaign
            self.client.enroll_lead_in_campaign(lead_id, campaign_id)
            logger.info(
                f"LinkedIn Connection Request queued via SalesRobot for {linkedin_url} "
                f"(lead_id={lead_id}, campaign_id={campaign_id})"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to send LinkedIn connection request to {linkedin_url}: {e}")
            return False

    def send_followup_message(self, linkedin_url: str, message: str) -> bool:
        """Send a LinkedIn follow-up message to an accepted connection.

        Uses a separate follow-up campaign so message sequencing and timing
        can be controlled independently from the connection campaign.

        Args:
            linkedin_url: Target LinkedIn profile URL
            message: Follow-up message body
        """
        if self.is_dry_run:
            logger.info(
                f"[DRY RUN] Would send LinkedIn Follow-up to {linkedin_url} "
                f"| Message: {message[:50]}..."
            )
            return True

        try:
            campaign_id = (
                os.getenv('SALESROBOT_FOLLOWUP_CAMPAIGN_ID')
                or self.settings.get('salesrobot.followup_campaign_id')
            )
            if not campaign_id:
                logger.error(
                    "SALESROBOT_FOLLOWUP_CAMPAIGN_ID is not set. "
                    "Add it to .env or settings.json before enabling LinkedIn follow-ups."
                )
                return False

            lead_data = {
                "linkedinUrl": linkedin_url,
                "note": message[:300],
                "linkedinAccountUuid": self.client.linkedin_account_uuid
            }
            lead_response = self.client.create_lead(lead_data)

            lead_id = (
                lead_response.get("data", {}).get("id")
                or lead_response.get("id")
            )
            if not lead_id:
                logger.error(
                    f"SalesRobot did not return a lead ID for {linkedin_url}. "
                    f"Response: {lead_response}"
                )
                return False

            self.client.enroll_lead_in_campaign(lead_id, campaign_id)
            logger.info(
                f"LinkedIn Follow-up queued via SalesRobot for {linkedin_url} "
                f"(lead_id={lead_id}, campaign_id={campaign_id})"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to send LinkedIn follow-up to {linkedin_url}: {e}")
            return False
