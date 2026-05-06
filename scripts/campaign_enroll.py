#!/usr/bin/env python3
"""Campaign enrollment script to enroll leads in Salesrobot campaigns."""

import os
import sys
import logging
from datetime import datetime

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from google_sheets import GoogleSheetsClient
from salesrobot_client import SalesrobotClient
from salesrobot_mapper import SalesrobotMapper
from human_stop_logic import HumanStopLogic
from stop_rules import StopRulesManager
from settings import Settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def enroll_leads_in_campaigns(settings: Settings, dry_run: bool = True) -> dict:
    """Enroll eligible leads in Salesrobot campaigns.
    
    Args:
        settings: Settings object
        dry_run: Whether to run in dry-run mode
        
    Returns:
        Enrollment results
    """
    logger.info("Starting campaign enrollment...")
    
    results = {
        'timestamp': datetime.now().isoformat(),
        'dry_run': dry_run,
        'total_leads': 0,
        'eligible_leads': 0,
        'enrolled_leads': 0,
        'skipped_leads': 0,
        'errors': [],
    }
    
    try:
        # Initialize clients
        credentials = settings.get_google_credentials()
        
        # Try OAuth if service account not available
        oauth_refresh_token = settings.get_oauth_refresh_token()
        oauth_client_id = settings.get_oauth_client_id()
        oauth_client_secret = settings.get_oauth_client_secret()
        
        if credentials:
            sheets_client = GoogleSheetsClient(credentials_json=credentials)
        elif oauth_refresh_token and oauth_client_id and oauth_client_secret:
            sheets_client = GoogleSheetsClient(
                oauth_refresh_token=oauth_refresh_token,
                client_id=oauth_client_id,
                client_secret=oauth_client_secret
            )
        else:
            raise ValueError("No Google credentials available")
        
        api_key = settings.get_salesrobot_api_key()
        linkedin_account_uuid = settings.get_linkedin_account_uuid()
        salesrobot_client = SalesrobotClient(api_key, linkedin_account_uuid)
        
        workflow_sheet_id = settings.get_workflow_sheet_id()
        
        # Initialize stop rules manager
        stop_rules = StopRulesManager()
        
        # Fetch leads from workflow sheet
        logger.info(f"Fetching leads from workflow sheet: {workflow_sheet_id}")
        workflow_data = sheets_client.get_sheet_data(workflow_sheet_id, 'Sheet1!A1:Z1000')
        
        if not workflow_data:
            logger.warning("No data found in workflow sheet")
            return results
        
        headers = workflow_data[0]
        rows = workflow_data[1:]
        
        logger.info(f"Found {len(rows)} leads in workflow sheet")
        results['total_leads'] = len(rows)
        
        # Get campaigns from Salesrobot
        logger.info("Fetching campaigns from Salesrobot")
        campaigns = salesrobot_client.get_campaigns()
        logger.info(f"Found {len(campaigns)} campaigns")
        
        # Create campaign ID map
        campaign_map = {c['name']: c['uuid'] for c in campaigns}
        
        # Process leads
        enrolled_count = 0
        skipped_count = 0
        
        for row in rows:
            try:
                # Parse lead from row
                lead = {}
                for i, value in enumerate(row):
                    if i < len(headers):
                        lead[headers[i]] = value
                
                lead_id = lead.get('Lead ID')
                
                if not lead_id:
                    logger.warning("Skipping lead without Lead ID")
                    skipped_count += 1
                    continue
                
                # Check stop conditions
                should_stop, stop_reason = stop_rules.check_lead_rules(lead)
                if should_stop:
                    logger.debug(f"Skipping lead {lead_id}: {stop_reason}")
                    skipped_count += 1
                    continue
                
                # Check if already enrolled
                status = lead.get('Status', 'new')
                if status not in ['new', 'imported']:
                    logger.debug(f"Skipping lead {lead_id}: already processed (status: {status})")
                    skipped_count += 1
                    continue
                
                # Get campaign
                campaign_name = lead.get('Campaign Name') or lead.get('Campaign')
                if not campaign_name:
                    # Use default campaign if none specified
                    campaign_name = 'A2go | Forecasting'
                    logger.debug(f"Using default campaign for lead {lead_id}: {campaign_name}")
                
                if campaign_name not in campaign_map:
                    logger.warning(f"Skipping lead {lead_id}: campaign '{campaign_name}' not found")
                    skipped_count += 1
                    continue
                
                campaign_id = campaign_map.get(campaign_name)
                if not campaign_id:
                    logger.warning(f"Skipping lead {lead_id}: campaign not found ({campaign_name})")
                    skipped_count += 1
                    continue
                
                # Map lead to Salesrobot format
                salesrobot_lead = SalesrobotMapper.map_to_salesrobot(lead)
                
                if not dry_run:
                    # Create lead in Salesrobot
                    created_lead = salesrobot_client.create_lead(salesrobot_lead)
                    salesrobot_lead_id = created_lead.get('id')
                    
                    # Enroll lead in campaign
                    salesrobot_client.enroll_lead_in_campaign(salesrobot_lead_id, campaign_id)
                    
                    logger.info(f"Enrolled lead {lead_id} in campaign {campaign_name}")
                else:
                    logger.info(f"[DRY RUN] Would enroll lead {lead_id} in campaign {campaign_name}")
                
                enrolled_count += 1
                
            except Exception as e:
                logger.error(f"Error enrolling lead: {e}")
                results['errors'].append({
                    'lead_id': lead.get('Lead ID', 'unknown'),
                    'error': str(e),
                })
        
        results['eligible_leads'] = enrolled_count + skipped_count
        results['enrolled_leads'] = enrolled_count
        results['skipped_leads'] = skipped_count
        
        logger.info(f"Enrollment complete: {enrolled_count} enrolled, {skipped_count} skipped")
        
    except Exception as e:
        logger.error(f"Error during campaign enrollment: {e}")
        results['errors'].append({
            'error': str(e),
        })
    
    return results


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Enroll leads in Salesrobot campaigns')
    parser.add_argument('--dry-run', action='store_true', help='Run in dry-run mode')
    args = parser.parse_args()
    
    # Load settings
    settings = Settings()
    
    # Override dry-run if specified
    if args.dry_run:
        settings.set('automation.dry_run', True)
    
    # Run enrollment
    results = enroll_leads_in_campaigns(settings, settings.is_dry_run())
    
    # Print results
    print("\n" + "="*60)
    print("CAMPAIGN ENROLLMENT RESULTS")
    print("="*60)
    print(f"Timestamp: {results['timestamp']}")
    print(f"Dry Run: {results['dry_run']}")
    print(f"Total Leads: {results['total_leads']}")
    print(f"Eligible Leads: {results['eligible_leads']}")
    print(f"Enrolled Leads: {results['enrolled_leads']}")
    print(f"Skipped Leads: {results['skipped_leads']}")
    
    if results['errors']:
        print(f"\nErrors: {len(results['errors'])}")
        for error in results['errors']:
            print(f"  - {error}")
    
    print("="*60 + "\n")
    
    # Exit with appropriate code
    sys.exit(0 if len(results['errors']) == 0 else 1)


if __name__ == '__main__':
    main()
