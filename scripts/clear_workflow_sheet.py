"""Clear workflow sheet data (except headers)."""

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
data = client.get_sheet_data(workflow_sheet_id, 'Sheet1!A1:Z1')

if data and len(data) > 0:
    headers = data[0]
    
    print(f"Clearing workflow sheet (keeping headers)...")
    print(f"Headers: {headers[:5]}...")
    
    # Clear all data except headers
    # We'll update the sheet to only have the header row
    client.update_sheet_data(workflow_sheet_id, 'Sheet1!A2:Z1000', [[]])
    
    print("Workflow sheet cleared successfully!")
else:
    print("No headers found in workflow sheet")
