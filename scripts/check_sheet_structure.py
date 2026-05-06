"""Check workflow sheet structure and identify bad records."""

import os
import sys

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from google_sheets import GoogleSheetsClient
from settings import Settings

# Load settings
settings = Settings()

# Initialize client
oauth_refresh_token = settings.get_oauth_refresh_token()
oauth_client_id = settings.get_oauth_client_id()
oauth_client_secret = settings.get_oauth_client_secret()

client = GoogleSheetsClient(
    oauth_refresh_token=oauth_refresh_token,
    client_id=oauth_client_id,
    client_secret=oauth_client_secret
)

# Get workflow sheet data
workflow_sheet_id = settings.get_workflow_sheet_id()

# Get rows 1-105 in one request
print("Checking rows 1-105:")
print("=" * 80)

data = client.get_sheet_data(workflow_sheet_id, 'Sheet1!A1:Z105')

if data and len(data) > 0:
    headers = data[0]
    rows = data[1:]
    
    print(f"Headers: {headers[:10]}...")
    print(f"Total rows: {len(rows)}")
    
    # Show rows 2-105
    for i, row in enumerate(rows, start=2):
        if i <= 105:
            print(f"\nRow {i}:")
            # Show first 10 columns
            for j, value in enumerate(row[:10]):
                if value:
                    print(f"  {headers[j]}: {value}")
            
            # Check if row has data in expected columns
            if len(row) > 0 and row[0]:  # Lead ID column
                print(f"  (Row has {len([v for v in row if v])} non-empty values)")
else:
    print("No data found")
