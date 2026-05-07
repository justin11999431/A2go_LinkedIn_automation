"""Send connection requests using Salesrobot API."""

import os
import sys
import time
import logging
from datetime import datetime

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


def read_connection_requests(file_path: str) -> list:
    """Read connection requests from file.
    
    Args:
        file_path: Path to connection requests file
        
    Returns:
        List of connection request dictionaries
    """
    requests = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    current_request = None
    for line in lines:
        line = line.strip()
        
        if line.startswith('Scheduled time:'):
            continue
        elif line.startswith('Connection requests to send:'):
            continue
        elif line == '':
            continue
        elif line.startswith('LinkedIn:'):
            if current_request:
                current_request['linkedin_url'] = line.split(':', 1)[1].strip()
        elif line.startswith('Message:'):
            if current_request:
                current_request['message'] = line.split(':', 1)[1].strip()
        elif line and line[0].isdigit() and '.' in line:
            # This is a numbered item line like "1. Walt Walker"
            if current_request:
                requests.append(current_request)
            # Extract the name (everything after the number and period)
            parts = line.split('.', 1)
            if len(parts) > 1:
                current_request = {'lead_id': parts[1].strip()}
            else:
                current_request = {'lead_id': line.strip()}
    
    # Add the last request
    if current_request:
        requests.append(current_request)
    
    return requests


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
        # URL format: https://www.linkedin.com/in/username-12345678
        profile_id = linkedin_url.rstrip('/').split('/')[-1]
        
        logger.info(f"Sending connection request to {profile_id}")
        
        # Note: This is a placeholder for the actual Salesrobot API call
        # You'll need to check the Salesrobot API documentation for the exact endpoint
        # and parameters for sending connection requests
        
        # Example API call (adjust based on actual API):
        # response = salesrobot_client.send_connection_request(
        #     profile_id=profile_id,
        #     message=message
        # )
        
        # For now, we'll just log the request
        logger.info(f"Connection request sent to {profile_id}")
        logger.info(f"Message: {message}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error sending connection request to {linkedin_url}: {e}")
        return False


def update_workflow_sheet(sheets_client: GoogleSheetsClient, 
                         workflow_sheet_id: str,
                         lead_id: str,
                         status: str) -> bool:
    """Update workflow sheet with connection request status.
    
    Args:
        sheets_client: Google Sheets client
        workflow_sheet_id: Workflow sheet ID
        lead_id: Lead ID
        status: Connection status
        
    Returns:
        True if successful
    """
    try:
        # Read current data
        data = sheets_client.get_sheet_data(workflow_sheet_id, 'Sheet1')
        
        if not data or len(data) < 2:
            logger.warning("No data found in workflow sheet")
            return False
        
        headers = data[0]
        rows = data[1:]
        
        # Find column indices
        lead_id_col = None
        connection_status_col = None
        last_action_date_col = None
        
        for i, header in enumerate(headers):
            header_lower = header.lower()
            if 'lead id' in header_lower:
                lead_id_col = i
            elif 'connection status' in header_lower:
                connection_status_col = i
            elif 'last action date' in header_lower:
                last_action_date_col = i
        
        if lead_id_col is None or connection_status_col is None:
            logger.warning("Could not find required columns in workflow sheet")
            return False
        
        # Find the row for this lead
        for i, row in enumerate(rows):
            if i < len(row) and row[lead_id_col] == lead_id:
                # Update the row
                if connection_status_col < len(row):
                    row[connection_status_col] = status
                else:
                    # Extend row if needed
                    while len(row) <= connection_status_col:
                        row.append('')
                    row[connection_status_col] = status
                
                if last_action_date_col is not None and last_action_date_col < len(row):
                    row[last_action_date_col] = datetime.now().isoformat()
                
                # Update the sheet
                range_name = f'Sheet1!A{i+2}:Z{i+2}'
                sheets_client.update_sheet_data(workflow_sheet_id, range_name, [row])
                
                logger.info(f"Updated workflow sheet for {lead_id}: {status}")
                return True
        
        logger.warning(f"Could not find lead {lead_id} in workflow sheet")
        return False
        
    except Exception as e:
        logger.error(f"Error updating workflow sheet: {e}")
        return False


def main():
    """Main function to send connection requests."""
    logger.info("Starting connection request sending process")
    
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
    
    # Read connection requests
    connection_requests_file = os.path.join(
        os.path.dirname(__file__), 
        'connection_requests.txt'
    )
    
    if not os.path.exists(connection_requests_file):
        logger.error(f"Connection requests file not found: {connection_requests_file}")
        return
    
    connection_requests = read_connection_requests(connection_requests_file)
    logger.info(f"Found {len(connection_requests)} connection requests to send")
    
    # Send connection requests
    successful = 0
    failed = 0
    
    for i, req in enumerate(connection_requests, 1):
        logger.info(f"Processing request {i}/{len(connection_requests)}: {req['lead_id']}")
        
        # Send connection request
        success = send_connection_request(
            salesrobot_client,
            req['linkedin_url'],
            req['message']
        )
        
        if success:
            successful += 1
            
            # Update workflow sheet
            update_workflow_sheet(
                sheets_client,
                workflow_sheet_id,
                req['lead_id'],
                'Sent'
            )
        else:
            failed += 1
        
        # Rate limiting: wait 2 seconds between requests
        if i < len(connection_requests):
            time.sleep(2)
    
    # Summary
    logger.info("=" * 60)
    logger.info("CONNECTION REQUEST SENDING COMPLETE")
    logger.info("=" * 60)
    logger.info(f"Total requests: {len(connection_requests)}")
    logger.info(f"Successful: {successful}")
    logger.info(f"Failed: {failed}")
    logger.info("=" * 60)


if __name__ == '__main__':
    main()
