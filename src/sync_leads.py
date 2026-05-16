"""Sync leads from Google Sheets to GoHighLevel."""

import logging
import os
from src.settings import Settings
from src.google_sheets import GoogleSheetsClient
from src.ghl_client import GHLClient
from src.lead_mapper import LeadMapper
from src.database import StateDatabase
from src.models import SequenceState

logger = logging.getLogger(__name__)

def sync_sheets_to_ghl():
    """Main synchronization function."""
    settings = Settings()
    
    # Check for dry run
    is_dry_run = settings.is_dry_run()
    if is_dry_run:
        logger.info("DRY RUN ENABLED: No live API calls will be made to GHL.")

    # Initialize clients
    gs_client = GoogleSheetsClient(
        oauth_refresh_token=settings.get_oauth_refresh_token(),
        client_id=settings.get_oauth_client_id(),
        client_secret=settings.get_oauth_client_secret()
    )
    
    ghl_client = GHLClient(
        api_key=os.getenv('GHL_PRIVATE_INTEGRATION_TOKEN') or settings.get('ghl.private_integration_token'),
        location_id=os.getenv('GHL_LOCATION_ID') or settings.get('ghl.location_id')
    )
    
    db = StateDatabase()
    
    source_sheet_id = settings.get_source_sheet_id()
    if not source_sheet_id:
        logger.error("No source sheet ID configured.")
        return

    # Read leads from sheet
    # Assuming data starts from row 2 (headers in row 1)
    # Range should cover all columns in SOURCE_COLUMN_MAP
    headers = LeadMapper.get_source_headers()
    max_col = chr(ord('A') + len(headers) - 1)
    range_name = f"A2go-Forecast-Intent-75!A2:{max_col}1000"
    
    rows = gs_client.get_sheet_data(source_sheet_id, range_name)
    if not rows:
        logger.info("No leads found in source sheet.")
        return

    logger.info(f"Processing {len(rows)} leads from Google Sheets.")

    for i, row in enumerate(rows):
        # Convert row list to dict using headers
        source_row = dict(zip(headers, row))
        
        # Map to internal format
        internal_lead = LeadMapper.map_source_to_internal(source_row, i + 2)
        email = internal_lead.get('email')
        
        if not email:
            logger.warning(f"Skipping row {i+2}: No email address.")
            continue

        # Check if already in local DB (to avoid redundant GHL calls if desired)
        state = db.get_state(internal_lead['lead_id'])
        if state and state.is_paused:
            logger.info(f"Skipping lead {email}: Automation is paused.")
            continue

        # Sync to GHL
        ghl_data = {
            "firstName": internal_lead.get('first_name'),
            "lastName": internal_lead.get('last_name'),
            "email": email,
            "phone": internal_lead.get('phone'),
            "companyName": internal_lead.get('company'),
            "tags": ["A2go_Sync"],
            "customFields": {
                "linkedin_url": internal_lead.get('linkedin_url')
            }
        }
        
        if not is_dry_run:
            try:
                ghl_id = ghl_client.upsert_contact(ghl_data)
                logger.info(f"Synced {email} to GHL: {ghl_id}")
                
                # Initialize local state if not exists
                if not state:
                    new_state = SequenceState(
                        lead_id=internal_lead['lead_id'],
                        email=email,
                        phone=internal_lead.get('phone'),
                        metadata=internal_lead
                    )
                    db.upsert_state(new_state)
            except Exception as e:
                logger.error(f"Failed to sync {email} to GHL: {e}")
        else:
            logger.info(f"[DRY RUN] Would sync {email} to GHL.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    sync_sheets_to_ghl()
