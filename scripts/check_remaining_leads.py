"""Generate copy for remaining leads in batches."""

import os
import sys
import logging
from datetime import datetime

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


def get_leads_needing_copy(sheets_client: GoogleSheetsClient,
                           source_sheet_id: str,
                           workflow_sheet_id: str,
                           limit: int = 50) -> list:
    """Get leads that need copy generation.
    
    Args:
        sheets_client: Google Sheets client
        source_sheet_id: Source sheet ID
        workflow_sheet_id: Workflow sheet ID
        limit: Maximum number of leads to return
        
    Returns:
        List of leads needing copy
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
        
        # Get leads needing copy
        leads_needing_copy = []
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
            
            leads_needing_copy.append(lead)
            
            if len(leads_needing_copy) >= limit:
                break
        
        logger.info(f"Found {len(leads_needing_copy)} leads needing copy (limit: {limit})")
        return leads_needing_copy
        
    except Exception as e:
        logger.error(f"Error getting leads needing copy: {e}")
        return []


def main():
    """Main function to generate copy for remaining leads."""
    logger.info("Starting copy generation for remaining leads")
    
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
    
    source_sheet_id = settings.get_source_sheet_id()
    workflow_sheet_id = settings.get_workflow_sheet_id()
    
    # Get leads needing copy (batch of 50)
    leads_needing_copy = get_leads_needing_copy(
        sheets_client,
        source_sheet_id,
        workflow_sheet_id,
        limit=50
    )
    
    if not leads_needing_copy:
        logger.info("No leads needing copy generation")
        return
    
    logger.info(f"Ready to generate copy for {len(leads_needing_copy)} leads")
    logger.info("\nTo generate copy, run:")
    logger.info("  python scripts/generate_copy.py --max-leads 50")
    logger.info("\nOr specify a different batch size:")
    logger.info("  python scripts/generate_copy.py --max-leads 100")


if __name__ == '__main__':
    main()
