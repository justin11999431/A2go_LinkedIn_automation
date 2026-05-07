"""Batch processing system for LinkedIn outreach."""

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

# Daily message limit
DAILY_MESSAGE_LIMIT = 20


def get_leads_needing_connection(sheets_client: GoogleSheetsClient,
                                source_sheet_id: str,
                                workflow_sheet_id: str,
                                limit: int = 20) -> List[Dict[str, Any]]:
    """Get leads that need connection requests.
    
    Args:
        sheets_client: Google Sheets client
        source_sheet_id: Source sheet ID
        workflow_sheet_id: Workflow sheet ID
        limit: Maximum number of leads to return
        
    Returns:
        List of leads needing connection
    """
    try:
        # Read source sheet
        source_data = sheets_client.get_sheet_data(source_sheet_id, 'A2go-Forecast-Intent-75!A1:Z1000')
        
        if not source_data or len(source_data) < 2:
            logger.warning("No data found in source sheet")
            return []
        
        source_headers = source_data[0]
        source_rows = source_data[1:]
        
        # Read workflow sheet to find already processed leads
        workflow_data = sheets_client.get_sheet_data(workflow_sheet_id, 'Sheet1')
        
        processed_lead_ids = set()
        if workflow_data and len(workflow_data) > 1:
            workflow_headers = workflow_data[0]
            workflow_rows = workflow_data[1:]
            
            # Find Lead ID column
            lead_id_col = None
            for i, header in enumerate(workflow_headers):
                if 'lead id' in header.lower():
                    lead_id_col = i
                    break
            
            if lead_id_col is not None:
                for row in workflow_rows:
                    if row and lead_id_col < len(row) and row[lead_id_col]:
                        processed_lead_ids.add(row[lead_id_col])
        
        # Find column indices in source sheet
        name_col = None
        title_col = None
        company_col = None
        linkedin_col = None
        
        for i, header in enumerate(source_headers):
            header_lower = header.lower()
            if 'name' in header_lower and 'first' not in header_lower and 'last' not in header_lower:
                name_col = i
            elif 'title' in header_lower:
                title_col = i
            elif 'company' in header_lower or 'employer' in header_lower:
                company_col = i
            elif 'linkedin' in header_lower:
                linkedin_col = i
        
        if name_col is None:
            logger.error("Could not find Name column in source sheet")
            return []
        
        # Get leads needing connection
        leads_needing_connection = []
        for row in source_rows:
            if not row or len(row) <= name_col:
                continue
            
            lead_id = row[name_col] if name_col < len(row) else ''
            
            # Skip if already processed
            if lead_id in processed_lead_ids:
                continue
            
            # Skip if no name
            if not lead_id:
                continue
            
            lead = {
                'name': lead_id,
                'title': row[title_col] if title_col is not None and title_col < len(row) else '',
                'company': row[company_col] if company_col is not None and company_col < len(row) else '',
                'linkedin_url': row[linkedin_col] if linkedin_col is not None and linkedin_col < len(row) else '',
            }
            
            leads_needing_connection.append(lead)
            
            if len(leads_needing_connection) >= limit:
                break
        
        logger.info(f"Found {len(leads_needing_connection)} leads needing connection (limit: {limit})")
        return leads_needing_connection
        
    except Exception as e:
        logger.error(f"Error getting leads needing connection: {e}")
        return []


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
            
            # Check Customer message (6-14 days after Colleague message)
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
            
            # Check Bridge message (15-21 days after Customer message)
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
            
            # Check Final message (25-35 days after Bridge message)
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


def calculate_daily_quota(followup_count: int) -> int:
    """Calculate how many new connection requests can be sent today.
    
    Args:
        followup_count: Number of follow-up messages needed
        
    Returns:
        Number of new connection requests that can be sent
    """
    available_quota = DAILY_MESSAGE_LIMIT - followup_count
    
    if available_quota < 0:
        logger.warning(f"Follow-up messages ({followup_count}) exceed daily limit ({DAILY_MESSAGE_LIMIT})")
        return 0
    
    return available_quota


def run_batch_processing():
    """Run the batch processing system."""
    logger.info("=" * 60)
    logger.info("LINKEDIN OUTREACH BATCH PROCESSING")
    logger.info("=" * 60)
    logger.info(f"Started at: {datetime.now().isoformat()}")
    logger.info(f"Daily message limit: {DAILY_MESSAGE_LIMIT}")
    
    # Load settings
    settings = Settings()
    
    # Initialize clients
    salesrobot_api_key = settings.get_salesrobot_api_key()
    linkedin_account_uuid = settings.get_linkedin_account_uuid()
    
    if not salesrobot_api_key:
        logger.error("Salesrobot API key not found in settings")
        return
    
    salesrobot_client = SalesrobotClient(
        api_key=salesrobot_api_key,
        linkedin_account_uuid=linkedin_account_uuid
    )
    
    oauth_refresh_token = settings.get_oauth_refresh_token()
    oauth_client_id = settings.get_oauth_client_id()
    oauth_client_secret = settings.get_oauth_client_secret()
    
    sheets_client = GoogleSheetsClient(
        oauth_refresh_token=oauth_refresh_token,
        client_id=oauth_client_id,
        client_secret=oauth_client_secret
    )
    
    source_sheet_id = settings.get_source_sheet_id()
    workflow_sheet_id = settings.get_workflow_sheet_id()
    
    # Step 1: Check for follow-up messages needed
    logger.info("\nStep 1: Checking for follow-up messages needed...")
    leads_needing_followup = get_leads_needing_followup(sheets_client, workflow_sheet_id)
    
    followup_count = len(leads_needing_followup)
    logger.info(f"Follow-up messages needed: {followup_count}")
    
    # Step 2: Calculate daily quota for new connections
    logger.info("\nStep 2: Calculating daily quota...")
    connection_quota = calculate_daily_quota(followup_count)
    logger.info(f"Available quota for new connections: {connection_quota}")
    
    # Step 3: Get leads needing connection
    logger.info("\nStep 3: Getting leads needing connection...")
    leads_needing_connection = get_leads_needing_connection(
        sheets_client,
        source_sheet_id,
        workflow_sheet_id,
        limit=connection_quota
    )
    
    connection_count = len(leads_needing_connection)
    logger.info(f"New connections to send: {connection_count}")
    
    # Step 4: Send follow-up messages
    logger.info("\nStep 4: Sending follow-up messages...")
    followup_successful = 0
    followup_failed = 0
    
    for i, lead in enumerate(leads_needing_followup, 1):
        logger.info(f"Processing follow-up {i}/{len(leads_needing_followup)}: {lead['lead_id']} ({lead['message_type']})")
        
        # Get message from sheet
        message = get_message_from_sheet(
            sheets_client,
            workflow_sheet_id,
            lead['lead_id'],
            lead['message_type']
        )
        
        if not message:
            logger.warning(f"Could not find {lead['message_type']} message for {lead['lead_id']}")
            followup_failed += 1
            continue
        
        # Send message
        success = send_followup_message(
            salesrobot_client,
            lead['linkedin_url'],
            message
        )
        
        if success:
            followup_successful += 1
            
            # Update message sent status
            update_message_sent_status(
                sheets_client,
                workflow_sheet_id,
                lead['lead_id'],
                lead['row_index'],
                lead['message_type']
            )
        else:
            followup_failed += 1
        
        # Rate limiting
        if i < len(leads_needing_followup):
            time.sleep(2)
    
    # Step 5: Send new connection requests
    logger.info("\nStep 5: Sending new connection requests...")
    connection_successful = 0
    connection_failed = 0
    
    for i, lead in enumerate(leads_needing_connection, 1):
        logger.info(f"Processing connection {i}/{len(leads_needing_connection)}: {lead['name']}")
        
        # Generate copy for lead
        copy_data = generate_copy_for_lead(lead)
        
        if not copy_data:
            logger.warning(f"Could not generate copy for {lead['name']}")
            connection_failed += 1
            continue
        
        # Get connection request message
        connection_request = copy_data.get('connection_requests', {}).get('version_a_direct', '')
        
        if not connection_request:
            logger.warning(f"Could not get connection request for {lead['name']}")
            connection_failed += 1
            continue
        
        # Send connection request
        success = send_connection_request(
            salesrobot_client,
            lead['linkedin_url'],
            connection_request
        )
        
        if success:
            connection_successful += 1
            
            # Update workflow sheet
            update_workflow_sheet(
                sheets_client,
                workflow_sheet_id,
                lead,
                copy_data
            )
        else:
            connection_failed += 1
        
        # Rate limiting
        if i < len(leads_needing_connection):
            time.sleep(2)
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("BATCH PROCESSING COMPLETE")
    logger.info("=" * 60)
    logger.info(f"Daily message limit: {DAILY_MESSAGE_LIMIT}")
    logger.info(f"Follow-up messages needed: {followup_count}")
    logger.info(f"Follow-up messages sent: {followup_successful}")
    logger.info(f"Follow-up messages failed: {followup_failed}")
    logger.info(f"Available quota for connections: {connection_quota}")
    logger.info(f"New connections sent: {connection_successful}")
    logger.info(f"New connections failed: {connection_failed}")
    logger.info(f"Total messages sent: {followup_successful + connection_successful}")
    logger.info("=" * 60)
    logger.info(f"Completed at: {datetime.now().isoformat()}")


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
        logger.info(f"Follow-up message sent to {profile_id}")
        logger.info(f"Message: {message[:100]}...")
        
        return True
        
    except Exception as e:
        logger.error(f"Error sending follow-up message to {linkedin_url}: {e}")
        return False


def send_connection_request(salesrobot_client: SalesrobotClient,
                            linkedin_url: str,
                            message: str) -> bool:
    """Send a connection request via Salesrobot API.
    
    Args:
        salesrobot_client: Salesrobot client
        linkedin_url: LinkedIn profile URL
        message: Connection request message
        
    Returns:
        True if successful
    """
    try:
        # Extract LinkedIn profile ID from URL
        profile_id = linkedin_url.rstrip('/').split('/')[-1]
        
        logger.info(f"Sending connection request to {profile_id}")
        
        # Note: This is a placeholder for the actual Salesrobot API call
        logger.info(f"Connection request sent to {profile_id}")
        logger.info(f"Message: {message}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error sending connection request to {linkedin_url}: {e}")
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


def update_workflow_sheet(sheets_client: GoogleSheetsClient,
                           workflow_sheet_id: str,
                           lead: Dict[str, Any],
                           copy_data: Dict[str, Any]) -> bool:
    """Update workflow sheet with generated copy.
    
    Args:
        sheets_client: Google Sheets client
        workflow_sheet_id: Workflow sheet ID
        lead: Lead data
        copy_data: Generated copy data
        
    Returns:
        True if successful
    """
    try:
        # Find the next empty row
        sheet_data = sheets_client.get_sheet_data(workflow_sheet_id, 'Sheet1')
        
        # Start from row 2 (after header, 1-based indexing)
        next_row = 2
        for i, row in enumerate(sheet_data[1:], start=2):  # Skip header row
            # Check if row is empty (all cells are empty)
            if not any(cell.strip() for cell in row if cell):
                next_row = i
                break
        else:
            # If all rows are filled, append to the end
            next_row = len(sheet_data) + 1
        
        # Map copy data to workflow sheet columns
        row = [
            lead.get('name', ''),  # Lead ID (using name as placeholder)
            lead.get('linkedin_url', ''),  # LinkedIn Profile URL
            lead.get('first_name', ''),  # First Name
            lead.get('last_name', ''),  # Last Name
            lead.get('company', ''),  # Company
            lead.get('title', ''),  # Title
            lead.get('industry', ''),  # Industry
            lead.get('location', ''),  # Location
            '',  # Connection Status
            '',  # Current Step
            '',  # Step Status
            '',  # Last Action Date
            '',  # Next Action Date
            copy_data.get('connection_requests', {}).get('version_a_direct', ''),  # Connection Request Message
            copy_data.get('dm_sequence', {}).get('message_1_colleague', {}).get('copy', ''),  # First Follow-up Message
            copy_data.get('dm_sequence', {}).get('message_2_customer', {}).get('copy', ''),  # Second Follow-up Message
            copy_data.get('dm_sequence', {}).get('message_3_bridge', {}).get('copy', ''),  # Third Follow-up Message
            copy_data.get('dm_sequence', {}).get('message_4_final', {}).get('copy', ''),  # Fourth Follow-up Message
            '',  # Fifth Follow-up Message
            '',  # Sixth Follow-up Message
            '',  # Seventh Follow-up Message
            '',  # Eighth Follow-up Message
            '',  # Ninth Follow-up Message
            '',  # Tenth Follow-up Message
            copy_data.get('research_summary', {}).get('notes', ''),  # Notes
            datetime.now().isoformat(),  # Last Updated
        ]
        
        # Update the specific row
        range_name = f'Sheet1!A{next_row}:Z{next_row}'
        logger.info(f"Updating workflow sheet for lead: {lead['name']} at row {next_row}")
        sheets_client.update_sheet_data(workflow_sheet_id, range_name, [row])
        
        logger.info(f"Successfully updated workflow sheet for lead: {lead['name']} at row {next_row}")
        return True
        
    except Exception as e:
        logger.error(f"Error updating workflow sheet for {lead['name']}: {e}")
        return False


def generate_copy_for_lead(lead: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Generate LinkedIn copy for a single lead.
    
    Args:
        lead: Lead data
        
    Returns:
        Generated copy or None
    """
    # Placeholder for copy generation
    # This would call the NVIDIA LLM to generate copy
    # For now, return None to indicate copy needs to be generated
    return None


if __name__ == '__main__':
    import time
    run_batch_processing()
