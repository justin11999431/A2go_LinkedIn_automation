#!/usr/bin/env python3
"""Lead sync script to sync leads from source sheet to workflow sheet."""

import os
import sys
import logging
from datetime import datetime

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from google_sheets import GoogleSheetsClient
from lead_mapper import LeadMapper
from lead_validator import LeadValidator
from workflow_sheet_writer import WorkflowSheetWriter
from settings import Settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def sync_leads(settings: Settings, dry_run: bool = True) -> dict:
    """Sync leads from source sheet to workflow sheet.
    
    Args:
        settings: Settings object
        dry_run: Whether to run in dry-run mode
        
    Returns:
        Sync results
    """
    logger.info("Starting lead sync...")
    
    results = {
        'timestamp': datetime.now().isoformat(),
        'dry_run': dry_run,
        'source_leads': 0,
        'valid_leads': 0,
        'invalid_leads': 0,
        'synced_leads': 0,
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
        
        source_sheet_id = settings.get_source_sheet_id()
        workflow_sheet_id = settings.get_workflow_sheet_id()
        
        # Fetch leads from source sheet
        logger.info(f"Fetching leads from source sheet: {source_sheet_id}")
        source_data = sheets_client.get_sheet_data(source_sheet_id, 'A2go-Forecast-Intent-75!A1:Z1000')
        
        if not source_data:
            logger.warning("No data found in source sheet")
            return results
        
        # Parse headers
        headers = source_data[0]
        rows = source_data[1:]
        
        logger.info(f"Found {len(rows)} leads in source sheet")
        results['source_leads'] = len(rows)
        
        # Map and validate leads
        valid_leads = []
        invalid_leads = []
        
        for i, row in enumerate(rows, start=2):  # Start at row 2 (after header)
            try:
                # Create row dictionary
                row_dict = {}
                for j, value in enumerate(row):
                    if j < len(headers):
                        row_dict[headers[j]] = value
                
                # Map to internal format
                lead = LeadMapper.map_source_to_internal(row_dict, i)
                
                # Validate lead
                validation_result = LeadValidator.validate_lead(lead)
                
                if validation_result['valid']:
                    valid_leads.append(lead)
                else:
                    invalid_leads.append({
                        'row': i,
                        'lead': lead,
                        'errors': validation_result['errors'],
                    })
            except Exception as e:
                logger.error(f"Error processing row {i}: {e}")
                invalid_leads.append({
                    'row': i,
                    'error': str(e),
                })
        
        results['valid_leads'] = len(valid_leads)
        results['invalid_leads'] = len(invalid_leads)
        
        logger.info(f"Valid leads: {len(valid_leads)}, Invalid leads: {len(invalid_leads)}")
        
        # Fetch existing workflow sheet data
        logger.info(f"Fetching existing data from workflow sheet: {workflow_sheet_id}")
        workflow_data = sheets_client.get_sheet_data(workflow_sheet_id, 'Sheet1!A1:Z1000')
        
        workflow_headers = workflow_data[0] if workflow_data else WorkflowSheetWriter.get_headers()
        workflow_rows = workflow_data[1:] if workflow_data else []
        
        # Sync leads to workflow sheet
        synced_count = 0
        new_leads = []
        
        for lead in valid_leads:
            try:
                # Check if lead already exists
                lead_id = lead['lead_id']
                lead_id_column_index = WorkflowSheetWriter.get_column_index('Lead ID')
                
                existing_row_index = WorkflowSheetWriter.find_existing_row(
                    workflow_data, lead_id, lead_id_column_index
                )
                
                if existing_row_index:
                    # Update existing lead
                    existing_lead = WorkflowSheetWriter.row_to_lead(
                        workflow_rows[existing_row_index - 1], workflow_headers
                    )
                    
                    # Prepare upsert data
                    upsert_lead = WorkflowSheetWriter.prepare_upsert_data(lead, existing_lead)
                    
                    # Convert to row
                    updated_row = WorkflowSheetWriter.lead_to_row(upsert_lead)
                    
                    if not dry_run:
                        # Update row in sheet
                        range_name = f"Sheet1!A{existing_row_index + 1}:Z{existing_row_index + 1}"
                        sheets_client.update_sheet_data(workflow_sheet_id, range_name, [updated_row])
                    
                    logger.debug(f"Updated lead: {lead_id}")
                else:
                    # Collect new leads for batch append
                    new_row = WorkflowSheetWriter.lead_to_row(lead)
                    new_leads.append(new_row)
                    logger.debug(f"Collected new lead: {lead_id}")
                
                synced_count += 1
            except Exception as e:
                logger.error(f"Error syncing lead {lead.get('lead_id', 'unknown')}: {e}")
                results['errors'].append({
                    'lead_id': lead.get('lead_id', 'unknown'),
                    'error': str(e),
                })
        
        # Batch append new leads
        if new_leads and not dry_run:
            try:
                logger.info(f"Batch appending {len(new_leads)} new leads...")
                range_name = "Sheet1!A1"
                sheets_client.append_sheet_data(workflow_sheet_id, range_name, new_leads)
                logger.info(f"Successfully appended {len(new_leads)} new leads")
            except Exception as e:
                logger.error(f"Error batch appending leads: {e}")
                results['errors'].append({
                    'error': f"Batch append failed: {str(e)}",
                })
        
        results['synced_leads'] = synced_count
        
        logger.info(f"Sync complete: {synced_count} leads synced")
        
    except Exception as e:
        logger.error(f"Error during lead sync: {e}")
        results['errors'].append({
            'error': str(e),
        })
    
    return results


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Sync leads from source sheet to workflow sheet')
    parser.add_argument('--dry-run', action='store_true', help='Run in dry-run mode')
    args = parser.parse_args()
    
    # Load settings
    settings = Settings()
    
    # Override dry-run if specified
    if args.dry_run:
        settings.set('automation.dry_run', True)
    
    # Run sync
    results = sync_leads(settings, settings.is_dry_run())
    
    # Print results
    print("\n" + "="*60)
    print("LEAD SYNC RESULTS")
    print("="*60)
    print(f"Timestamp: {results['timestamp']}")
    print(f"Dry Run: {results['dry_run']}")
    print(f"Source Leads: {results['source_leads']}")
    print(f"Valid Leads: {results['valid_leads']}")
    print(f"Invalid Leads: {results['invalid_leads']}")
    print(f"Synced Leads: {results['synced_leads']}")
    
    if results['errors']:
        print(f"\nErrors: {len(results['errors'])}")
        for error in results['errors']:
            print(f"  - {error}")
    
    print("="*60 + "\n")
    
    # Exit with appropriate code
    sys.exit(0 if len(results['errors']) == 0 else 1)


if __name__ == '__main__':
    main()
