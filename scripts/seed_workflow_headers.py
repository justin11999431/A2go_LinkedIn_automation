#!/usr/bin/env python3
"""Script to seed workflow sheet headers."""

import os
import sys

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from google_sheets import GoogleSheetsClient
from workflow_sheet_writer import WorkflowSheetWriter
from settings import Settings


def seed_workflow_headers(settings: Settings) -> dict:
    """Seed workflow sheet with headers.
    
    Args:
        settings: Settings object
        
    Returns:
        Seed results
    """
    print("Seeding workflow sheet headers...")
    
    results = {
        'success': False,
        'message': '',
    }
    
    try:
        # Initialize client
        credentials = settings.get_google_credentials()
        sheets_client = GoogleSheetsClient(credentials)
        
        workflow_sheet_id = settings.get_workflow_sheet_id()
        
        # Get headers
        headers = WorkflowSheetWriter.get_headers()
        
        # Write headers to sheet
        range_name = "Sheet1!A1:Z1"
        sheets_client.update_sheet_data(workflow_sheet_id, range_name, [headers])
        
        results['success'] = True
        results['message'] = f"Successfully seeded {len(headers)} headers to workflow sheet"
        print(f"✓ Seeded {len(headers)} headers to workflow sheet")
        
    except Exception as e:
        results['success'] = False
        results['message'] = f"Error seeding headers: {e}"
        print(f"✗ Error seeding headers: {e}")
    
    return results


def main():
    """Main entry point."""
    # Load settings
    settings = Settings()
    
    # Run seed
    results = seed_workflow_headers(settings)
    
    # Print results
    print("\n" + "="*60)
    print("WORKFLOW SHEET HEADER SEED RESULTS")
    print("="*60)
    print(f"Success: {results['success']}")
    print(f"Message: {results['message']}")
    print("="*60 + "\n")
    
    # Exit with appropriate code
    sys.exit(0 if results['success'] else 1)


if __name__ == '__main__':
    main()
