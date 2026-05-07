"""Human-in-loop response detection and stop logic."""

import os
import sys
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from google_sheets import GoogleSheetsClient
from settings import Settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def check_for_responses(sheets_client: GoogleSheetsClient,
                        workflow_sheet_id: str) -> List[Dict[str, Any]]:
    """Check for new responses from prospects.
    
    Args:
        sheets_client: Google Sheets client
        workflow_sheet_id: Workflow sheet ID
        
    Returns:
        List of leads with new responses
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
        reply_status_col = None
        reply_text_col = None
        last_human_update_col = None
        automation_stopped_col = None
        
        for i, header in enumerate(headers):
            header_lower = header.lower()
            if 'lead id' in header_lower:
                lead_id_col = i
            elif 'reply status' in header_lower:
                reply_status_col = i
            elif 'reply text' in header_lower:
                reply_text_col = i
            elif 'last human' in header_lower or 'owner last action' in header_lower:
                last_human_update_col = i
            elif 'automation stopped' in header_lower or 'manual stop' in header_lower:
                automation_stopped_col = i
        
        if lead_id_col is None or reply_status_col is None:
            logger.warning("Could not find required columns in workflow sheet")
            return []
        
        # Check for new responses
        leads_with_responses = []
        now = datetime.now()
        
        for i, row in enumerate(rows):
            if not row:
                continue
            
            lead_id = row[lead_id_col] if lead_id_col < len(row) else ''
            reply_status = row[reply_status_col] if reply_status_col < len(row) else ''
            reply_text = row[reply_text_col] if reply_text_col is not None and reply_text_col < len(row) else ''
            last_human_update = parse_date(row[last_human_update_col]) if last_human_update_col is not None and last_human_update_col < len(row) else None
            automation_stopped = row[automation_stopped_col] if automation_stopped_col is not None and automation_stopped_col < len(row) else ''
            
            # Skip if automation already stopped
            if automation_stopped and automation_stopped.lower() in ['yes', 'true', 'stopped']:
                continue
            
            # Check if there's a new response
            if reply_status and reply_status.lower() in ['replied', 'responded', 'answered']:
                # Check if response is recent (within last 7 days)
                if last_human_update:
                    days_since_response = (now - last_human_update).days
                    if days_since_response <= 7:
                        leads_with_responses.append({
                            'lead_id': lead_id,
                            'row_index': i + 2,
                            'reply_status': reply_status,
                            'reply_text': reply_text,
                            'last_human_update': last_human_update,
                            'days_since_response': days_since_response
                        })
        
        logger.info(f"Found {len(leads_with_responses)} leads with recent responses")
        return leads_with_responses
        
    except Exception as e:
        logger.error(f"Error checking for responses: {e}")
        return []


def stop_automation_for_lead(sheets_client: GoogleSheetsClient,
                           workflow_sheet_id: str,
                           lead_id: str,
                           row_index: int,
                           reason: str) -> bool:
    """Stop automation for a lead due to human response.
    
    Args:
        sheets_client: Google Sheets client
        workflow_sheet_id: Workflow sheet ID
        lead_id: Lead ID
        row_index: Row index in sheet
        reason: Reason for stopping
        
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
        automation_stopped_col = None
        stop_reason_col = None
        last_action_date_col = None
        
        for i, header in enumerate(headers):
            header_lower = header.lower()
            if 'automation stopped' in header_lower or 'manual stop' in header_lower:
                automation_stopped_col = i
            elif 'stop reason' in header_lower or 'notes' in header_lower:
                stop_reason_col = i
            elif 'last action date' in header_lower or 'last updated' in header.lower():
                last_action_date_col = i
        
        if automation_stopped_col is None:
            logger.warning("Could not find Automation Stopped column")
            return False
        
        # Update the row
        now = datetime.now().isoformat()
        
        if automation_stopped_col < len(row):
            row[automation_stopped_col] = 'Yes'
        else:
            # Extend row if needed
            while len(row) <= automation_stopped_col:
                row.append('')
            row[automation_stopped_col] = 'Yes'
        
        if stop_reason_col is not None and stop_reason_col < len(row):
            row[stop_reason_col] = f"Human response detected: {reason}"
        elif stop_reason_col is not None:
            # Extend row if needed
            while len(row) <= stop_reason_col:
                row.append('')
            row[stop_reason_col] = f"Human response detected: {reason}"
        
        if last_action_date_col is not None and last_action_date_col < len(row):
            row[last_action_date_col] = now
        
        # Update the sheet
        range_name = f'Sheet1!A{row_index}:Z{row_index}'
        sheets_client.update_sheet_data(workflow_id, range_name, [row])
        
        logger.info(f"Stopped automation for {lead_id}: {reason}")
        return True
        
    except Exception as e:
        logger.error(f"Error stopping automation for {lead_id}: {e}")
        return False


def should_stop_automation(sheets_client: GoogleSheetsClient,
                           workflow_sheet_id: str,
                           lead_id: str) -> bool:
    """Check if automation should be stopped for a lead.
    
    Args:
        sheets_client: Google Sheets client
        workflow_sheet_id: Workflow sheet ID
        lead_id: Lead ID
        
    Returns:
        True if automation should be stopped
    """
    try:
        # Read workflow sheet
        data = sheets_client.get_sheet_data(workflow_sheet_id, 'Sheet1')
        
        if not data or len(data) < 2:
            return False
        
        headers = data[0]
        rows = data[1:]
        
        # Find column indices
        lead_id_col = None
        automation_stopped_col = None
        
        for i, header in enumerate(headers):
            header_lower = header.lower()
            if 'lead id' in header.lower():
                lead_id_col = i
            elif 'automation stopped' in header_lower or 'manual stop' in header_lower:
                automation_stopped_col = i
        
        if lead_id_col is None or automation_stopped_col is None:
            return False
        
        # Find the row for this lead
        for row in rows:
            if not row:
                continue
            
            if lead_id_col < len(row) and row[lead_id_col] == lead_id:
                if automation_stopped_col < len(row):
                    stopped_value = row[automation_stopped_col]
                    return stopped_value and stopped_value.lower() in ['yes', 'true', 'stopped']
        
        return False
        
    except Exception as e:
        logger.error(f"Error checking if automation should stop for {lead_id}: {e}")
        return False


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


def check_and_stop_for_responses(sheets_client: GoogleSheetsClient,
                                 workflow_sheet_id: str) -> int:
    """Check for responses and stop automation for those leads.
    
    Args:
        sheets_client: Google Sheets client
        workflow_sheet_id: Workflow sheet ID
        
    Returns:
        Number of leads where automation was stopped
    """
    logger.info("Checking for human responses...")
    
    # Check for new responses
    leads_with_responses = check_for_responses(sheets_client, workflow_sheet_id)
    
    if not leads_with_responses:
        logger.info("No new human responses found")
        return 0
    
    # Stop automation for leads with responses
    stopped_count = 0
    for lead in leads_with_responses:
        logger.info(f"Stopping automation for {lead['lead_id']} (response: {lead['reply_status']})")
        
        success = stop_automation_for_lead(
            sheets_client,
            workflow_sheet_id,
            lead['lead_id'],
            lead['row_index'],
            f"Response detected: {lead['reply_status']}"
        )
        
        if success:
            stopped_count += 1
    
    logger.info(f"Stopped automation for {stopped_count} leads due to human responses")
    return stopped_count


def main():
    """Main function to check for human responses."""
    logger.info("Starting human-in-loop response check")
    
    # Load settings
    settings = Settings()
    
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
    
    # Check for responses and stop automation
    stopped_count = check_and_stop_for_responses(sheets_client, workflow_sheet_id)
    
    # Summary
    logger.info("=" * 60)
    logger.info("HUMAN-IN-LOOP RESPONSE CHECK COMPLETE")
    logger.info("=" * 60)
    logger.info(f"Leads with responses: {len(check_for_responses(sheets_client, workflow_sheet_id))}")
    logger.info(f"Automation stopped for: {stopped_count}")
    logger.info("=" * 60)


if __name__ == '__main__':
    main()
