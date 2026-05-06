"""Check workflow sheet data."""

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
data = client.get_sheet_data(workflow_sheet_id, 'Sheet1!A1:Z1000')

if data and len(data) > 0:
    headers = data[0]
    rows = data[1:]
    
    print(f"Workflow Sheet Data:")
    print(f"Headers ({len(headers)}):")
    for i, header in enumerate(headers):
        print(f"  {i+1}. {header}")
    print(f"\nTotal rows: {len(rows)}")
    
    # Check for non-empty rows
    non_empty_rows = [row for row in rows if any(row)]
    print(f"Non-empty rows: {len(non_empty_rows)}")
    if non_empty_rows:
        print(f"\nFirst non-empty row:")
        for i, value in enumerate(non_empty_rows[0]):
            if i < len(headers):
                print(f"  {headers[i]}: {value}")
else:
    print("No data found in workflow sheet")
