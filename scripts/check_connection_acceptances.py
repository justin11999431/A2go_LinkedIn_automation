"""Check for connection acceptances and update workflow sheet."""

import os
import sys
import logging
from datetime import datetime, timedelta

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


def check_connection_acceptances(sheets_client: GoogleSheetsClient, 
                                 workflow_sheet_id: str) -> list:
    """Check for connection acceptances in workflow sheet.
    
    Args:
        sheets_client: Google Sheets client
        workflow_sheet_id: Workflow sheet ID
        
    Returns:
        List of leads with accepted connections
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
        connection_status_col = None
        connection_accepted_date_col = None
        last_action_date_col = None
        
        for i, header in enumerate(headers):
            header_lower = header.lower()
            if 'lead id' in header_lower:
                lead_id_col = i
            elif 'connection status' in header_lower:
                connection_status_col = i
            elif 'connection accepted' in header_lower:
                connection_accepted_date_col = i
            elif 'last action date' in header_lower:
                last_action_date_col = i
        
        if lead_id_col is None or connection_status_col is None:
            logger.warning("Could not find required columns in workflow sheet")
            return []
        
        # Check for accepted connections
        accepted_leads = []
        for i, row in enumerate(rows):
            if not row:
                continue
            
            lead_id = row[lead_id_col] if lead_id_col < len(row) else ''
            connection_status = row[connection_status_col] if connection_status_col < len(row) else ''
            
            # Check if connection is accepted
            if connection_status.lower() in ['accepted', 'connected']:
                accepted_leads.append({
                    'lead_id': lead_id,
                    'row_index': i + 2,  # +2 because of header row and 0-based indexing
                    'row': row
                })
        
        logger.info(f"Found {len(accepted_leads)} accepted connections")
        return accepted_leads
        
    except Exception as e:
        logger.error(f"Error checking connection acceptances: {e}")
        return []


def update_connection_accepted_date(sheets_client: GoogleSheetsClient,
                                    workflow_sheet_id: str,
                                    lead_id: str,
                                    row_index: int) -> bool:
    """Update connection accepted date for a lead.
    
    Args:
        sheets_client: Google Sheets client
        workflow_sheet_id: Workflow sheet ID
        lead_id: Lead ID
        row_index: Row index in sheet
        
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
        connection_accepted_date_col = None
        last_action_date_col = None
        
        for i, header in enumerate(headers):
            header_lower = header.lower()
            if 'connection accepted' in header_lower:
                connection_accepted_date_col = i
            elif 'last action date' in header_lower:
                last_action_date_col = i
        
        if connection_accepted_date_col is None:
            logger.warning("Could not find Connection Accepted Date column")
            return False
        
        # Update the row
        now = datetime.now().isoformat()
        
        if connection_accepted_date_col < len(row):
            row[connection_accepted_date_col] = now
        else:
            # Extend row if needed
            while len(row) <= connection_accepted_date_col:
                row.append('')
            row[connection_accepted_date_col] = now
        
        if last_action_date_col is not None and last_action_date_col < len(row):
            row[last_action_date_col] = now
        
        # Update the sheet
        range_name = f'Sheet1!A{row_index}:Z{row_index}'
        sheets_client.update_sheet_data(workflow_sheet_id, range_name, [row])
        
        logger.info(f"Updated connection accepted date for {lead_id}")
        return True
        
    except Exception as e:
        logger.error(f"Error updating connection accepted date for {lead_id}: {e}")
        return False


def main():
    """Main function to check for connection acceptances."""
    logger.info("Starting connection acceptance check")
    
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
    
    # Check for connection acceptances
    accepted_leads = check_connection_acceptances(sheets_client, workflow_sheet_id)
    
    if not accepted_leads:
        logger.info("No new connection acceptances found")
        return
    
    # Update connection accepted dates
    updated = 0
    for lead in accepted_leads:
        success = update_connection_accepted_date(
            sheets_client,
            workflow_sheet_id,
            lead['lead_id'],
            lead['row_index']
        )
        
        if success:
            updated += 1
    
    # Summary
    logger.info("=" * 60)
    logger.info("CONNECTION ACCEPTANCE CHECK COMPLETE")
    logger.info("=" * 60)
    logger.info(f"Total accepted connections: {len(accepted_leads)}")
    logger.info(f"Updated connection accepted dates: {updated}")
    logger.info("=" * 60)


if __name__ == '__main__':
    main()
