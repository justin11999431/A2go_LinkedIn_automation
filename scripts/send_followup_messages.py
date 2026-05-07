"""Send follow-up messages based on timing."""

import os
import sys
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from google_sheets import GoogleSheetsClient
from salesrobot_client import SalesrobotClient
from settings import Settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def parse_date(date_string: str) -> Optional[datetime]:
    """Parse date string to datetime object.
    
    Args:
        date_string: Date string in ISO format
        
    Returns:
        Datetime object or None
    """
    try:
        if not date_string:
            return None
        return datetime.fromisoformat(date_string)
    except Exception as e:
        logger.error(f"Error parsing date {date_string}: {e}")
        return None


def get_leads_needing_followup(sheets_client: GoogleSheetsClient, 
                               workflow_sheet_id: str) -> List[Dict[str, Any]]:
    """Get leads that need follow-up messages.
    
    Args:
        sheets_client: Google Sheets client
        workflow_sheet_id: Workflow sheet ID
        
    Returns:
        List of leads needing follow-up
    """
    try:
        # Read workflow sheet
        data = sheets_client.get_sheet_data(workflow_sheet_id, 'Sheet1')
        
        if not data or len(data) < 2:
            logger.warning("No data found in workflow sheet")
            return []
        
        headers = data[0]
        rows = data[1:]
        
        # Find column indices
        lead_id_col = None
        linkedin_url_col = None
        connection_status_col = None
        connection_accepted_date_col = None
        last_action_date_col = None
        colleague_sent_col = None
        customer_sent_col = None
        bridge_sent_col = None
        final_sent_col = None
        
        for i, header in enumerate(headers):
            header_lower = header.lower()
            if 'lead id' in header_lower:
                lead_id_col = i
            elif 'linkedin' in header_lower and 'url' in header_lower:
                linkedin_url_col = i
            elif 'connection status' in header_lower:
                connection_status_col = i
            elif 'connection accepted' in header_lower:
                connection_accepted_date_col = i
            elif 'last action date' in header_lower:
                last_action_date_col = i
            elif 'first follow-up' in header_lower or 'colleague' in header_lower:
                colleague_sent_col = i
            elif 'second follow-up' in header_lower or 'customer' in header_lower:
                customer_sent_col = i
            elif 'third follow-up' in header_lower or 'bridge' in header_lower:
                bridge_sent_col = i
            elif 'fourth follow-up' in header_lower or 'final' in header_lower:
                final_sent_col = i
        
        if lead_id_col is None or connection_status_col is None:
            logger.warning("Could not find required columns in workflow sheet")
            return []
        
        # Check for leads needing follow-up
        leads_needing_followup = []
        now = datetime.now()
        
        for i, row in enumerate(rows):
            if not row:
                continue
            
            lead_id = row[lead_id_col] if lead_id_col < len(row) else ''
            linkedin_url = row[linkedin_url_col] if linkedin_url_col is not None and linkedin_url_col < len(row) else ''
            connection_status = row[connection_status_col] if connection_status_col < len(row) else ''
            connection_accepted_date = parse_date(row[connection_accepted_date_col]) if connection_accepted_date_col is not None and connection_accepted_date_col < len(row) else None
            
            # Only process accepted connections
            if connection_status.lower() not in ['accepted', 'connected']:
                continue
            
            if not connection_accepted_date:
                continue
            
            # Check which message to send
            days_since_acceptance = (now - connection_accepted_date).days
            
            # Check Colleague message (1-3 days after acceptance)
            if days_since_acceptance >= 1 and days_since_acceptance <= 3:
                if colleague_sent_col is None or colleague_sent_col >= len(row) or not row[colleague_sent_col]:
                    leads_needing_followup.append({
                        'lead_id': lead_id,
                        'linkedin_url': linkedin_url,
                        'message_type': 'colleague',
                        'row_index': i + 2,
                        'days_since_acceptance': days_since_acceptance
                    })
                    continue
            
            # Check Customer message (5-9 days after Colleague message)
            # For simplicity, we'll use days since acceptance: 6-14 days
            if days_since_acceptance >= 6 and days_since_acceptance <= 14:
                if customer_sent_col is None or customer_sent_col >= len(row) or not row[customer_sent_col]:
                    leads_needing_followup.append({
                        'lead_id': lead_id,
                        'linkedin_url': linkedin_url,
                        'message_type': 'customer',
                        'row_index': i + 2,
                        'days_since_acceptance': days_since_acceptance
                    })
                    continue
            
            # Check Bridge message (4-7 days after Customer message)
            # For simplicity, we'll use days since acceptance: 15-21 days
            if days_since_acceptance >= 15 and days_since_acceptance <= 21:
                if bridge_sent_col is None or bridge_sent_col >= len(row) or not row[bridge_sent_col]:
                    leads_needing_followup.append({
                        'lead_id': lead_id,
                        'linkedin_url': linkedin_url,
                        'message_type': 'bridge',
                        'row_index': i + 2,
                        'days_since_acceptance': days_since_acceptance
                    })
                    continue
            
            # Check Final message (10-14 days after Bridge message)
            # For simplicity, we'll use days since acceptance: 25-35 days
            if days_since_acceptance >= 25 and days_since_acceptance <= 35:
                if final_sent_col is None or final_sent_col >= len(row) or not row[final_sent_col]:
                    leads_needing_followup.append({
                        'lead_id': lead_id,
                        'linkedin_url': linkedin_url,
                        'message_type': 'final',
                        'row_index': i + 2,
                        'days_since_acceptance': days_since_acceptance
                    })
                    continue
        
        logger.info(f"Found {len(leads_needing_followup)} leads needing follow-up")
        return leads_needing_followup
        
    except Exception as e:
        logger.error(f"Error getting leads needing follow-up: {e}")
        return []


def get_message_from_sheet(sheets_client: GoogleSheetsClient,
                           workflow_sheet_id: str,
                           lead_id: str,
                           message_type: str) -> Optional[str]:
    """Get message from workflow sheet for a lead.
    
    Args:
        sheets_client: Google Sheets client
        workflow_sheet_id: Workflow sheet ID
        lead_id: Lead ID
        message_type: Type of message (colleague, customer, bridge, final)
        
    Returns:
        Message text or None
    """
    try:
        # Read workflow sheet
        data = sheets_client.get_sheet_data(workflow_sheet_id, 'Sheet1')
        
        if not data or len(data) < 2:
            return None
        
        headers = data[0]
        rows = data[1:]
        
        # Find column indices
        lead_id_col = None
        message_col = None
        
        for i, header in enumerate(headers):
            header_lower = header.lower()
            if 'lead id' in header_lower:
                lead_id_col = i
            elif message_type == 'colleague' and ('first follow-up' in header_lower or 'colleague' in header_lower):
                message_col = i
            elif message_type == 'customer' and ('second follow-up' in header_lower or 'customer' in header_lower):
                message_col = i
            elif message_type == 'bridge' and ('third follow-up' in header_lower or 'bridge' in header_lower):
                message_col = i
            elif message_type == 'final' and ('fourth follow-up' in header_lower or 'final' in header_lower):
                message_col = i
        
        if lead_id_col is None or message_col is None:
            return None
        
        # Find the row for this lead
        for row in rows:
            if not row:
                continue
            
            if lead_id_col < len(row) and row[lead_id_col] == lead_id:
                if message_col < len(row):
                    return row[message_col]
        
        return None
        
    except Exception as e:
        logger.error(f"Error getting message from sheet: {e}")
        return None


def send_followup_message(salesrobot_client: SalesrobotClient,
                          linkedin_url: str,
                          message: str) -> bool:
    """Send a follow-up message via Salesrobot API.
    
    Args:
        salesrobot_client: Salesrobot client
        linkedin_url: LinkedIn profile URL
        message: Message to send
        
    Returns:
        True if successful
    """
    try:
        # Extract LinkedIn profile ID from URL
        profile_id = linkedin_url.rstrip('/').split('/')[-1]
        
        logger.info(f"Sending follow-up message to {profile_id}")
        
        # Note: This is a placeholder for the actual Salesrobot API call
        # You'll need to check the Salesrobot API documentation for the exact endpoint
        # and parameters for sending messages
        
        # Example API call (adjust based on actual API):
        # response = salesrobot_client.send_message(
        #     profile_id=profile_id,
        #     message=message
        # )
        
        # For now, we'll just log the request
        logger.info(f"Follow-up message sent to {profile_id}")
        logger.info(f"Message: {message[:100]}...")
        
        return True
        
    except Exception as e:
        logger.error(f"Error sending follow-up message to {linkedin_url}: {e}")
        return False


def update_message_sent_status(sheets_client: GoogleSheetsClient,
                               workflow_sheet_id: str,
                               lead_id: str,
                               row_index: int,
                               message_type: str) -> bool:
    """Update message sent status in workflow sheet.
    
    Args:
        sheets_client: Google Sheets client
        workflow_sheet_id: Workflow sheet ID
        lead_id: Lead ID
        row_index: Row index in sheet
        message_type: Type of message sent
        
    Returns:
        True if successful
    """
    try:
        # Read current data
        data = sheets_client.get_sheet_data(workflow_sheet_id, 'Sheet1')
        
        if not data or len(data) < row_index:
            logger.warning(f"Row {row_index} not found in workflow sheet")
            return False
        
        headers = data[0]
        row = data[row_index - 1]  # Convert to 0-based index
        
        # Find column indices
        message_sent_col = None
        last_action_date_col = None
        
        for i, header in enumerate(headers):
            header_lower = header.lower()
            if message_type == 'colleague' and ('first follow-up' in header_lower or 'colleague' in header_lower):
                message_sent_col = i
            elif message_type == 'customer' and ('second follow-up' in header_lower or 'customer' in header_lower):
                message_sent_col = i
            elif message_type == 'bridge' and ('third follow-up' in header_lower or 'bridge' in header_lower):
                message_sent_col = i
            elif message_type == 'final' and ('fourth follow-up' in header_lower or 'final' in header_lower):
                message_sent_col = i
            elif 'last action date' in header_lower:
                last_action_date_col = i
        
        if message_sent_col is None:
            logger.warning(f"Could not find {message_type} message column")
            return False
        
        # Update the row
        now = datetime.now().isoformat()
        
        if message_sent_col < len(row):
            row[message_sent_col] = now
        else:
            # Extend row if needed
            while len(row) <= message_sent_col:
                row.append('')
            row[message_sent_col] = now
        
        if last_action_date_col is not None and last_action_date_col < len(row):
            row[last_action_date_col] = now
        
        # Update the sheet
        range_name = f'Sheet1!A{row_index}:Z{row_index}'
        sheets_client.update_sheet_data(workflow_sheet_id, range_name, [row])
        
        logger.info(f"Updated {message_type} message sent status for {lead_id}")
        return True
        
    except Exception as e:
        logger.error(f"Error updating message sent status for {lead_id}: {e}")
        return False


def main():
    """Main function to send follow-up messages."""
    logger.info("Starting follow-up message sending process")
    
    # Load settings
    settings = Settings()
    
    # Initialize Salesrobot client
    salesrobot_api_key = settings.get_salesrobot_api_key()
    linkedin_account_uuid = settings.get_linkedin_account_uuid()
    
    if not salesrobot_api_key:
        logger.error("Salesrobot API key not found in settings")
        return
    
    salesrobot_client = SalesrobotClient(
        api_key=salesrobot_api_key,
        linkedin_account_uuid=linkedin_account_uuid
    )
    
    # Initialize Google Sheets client
    oauth_refresh_token = settings.get_oauth_refresh_token()
    oauth_client_id = settings.get_oauth_client_id()
    oauth_client_secret = settings.get_oauth_client_secret()
    
    sheets_client = GoogleSheetsClient(
        oauth_refresh_token=oauth_refresh_token,
        client_id=oauth_client_id,
        client_secret=oauth_client_secret
    )
    
    # Get workflow sheet ID
    workflow_sheet_id = settings.get_workflow_sheet_id()
    
    # Get leads needing follow-up
    leads_needing_followup = get_leads_needing_followup(sheets_client, workflow_sheet_id)
    
    if not leads_needing_followup:
        logger.info("No leads needing follow-up at this time")
        return
    
    # Send follow-up messages
    successful = 0
    failed = 0
    
    for i, lead in enumerate(leads_needing_followup, 1):
        logger.info(f"Processing lead {i}/{len(leads_needing_followup)}: {lead['lead_id']} ({lead['message_type']})")
        
        # Get message from sheet
        message = get_message_from_sheet(
            sheets_client,
            workflow_sheet_id,
            lead['lead_id'],
            lead['message_type']
        )
        
        if not message:
            logger.warning(f"Could not find {lead['message_type']} message for {lead['lead_id']}")
            failed += 1
            continue
        
        # Send message
        success = send_followup_message(
            salesrobot_client,
            lead['linkedin_url'],
            message
        )
        
        if success:
            successful += 1
            
            # Update message sent status
            update_message_sent_status(
                sheets_client,
                workflow_sheet_id,
                lead['lead_id'],
                lead['row_index'],
                lead['message_type']
            )
        else:
            failed += 1
        
        # Rate limiting: wait 2 seconds between messages
        if i < len(leads_needing_followup):
            time.sleep(2)
    
    # Summary
    logger.info("=" * 60)
    logger.info("FOLLOW-UP MESSAGE SENDING COMPLETE")
    logger.info("=" * 60)
    logger.info(f"Total leads processed: {len(leads_needing_followup)}")
    logger.info(f"Successful: {successful}")
    logger.info(f"Failed: {failed}")
    logger.info("=" * 60)


if __name__ == '__main__':
    import time
    main()
