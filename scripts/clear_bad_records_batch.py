"""Clear bad records using batch operations."""

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

# Get workflow sheet ID
workflow_sheet_id = settings.get_workflow_sheet_id()

print("Clearing rows 2-105 using batch operation...")

# Create empty rows for rows 2-105
empty_rows = [[''] * 26] * 104  # 104 rows, 26 columns each

# Use batch update to clear all rows at once
try:
    client.update_sheet_data(
        workflow_sheet_id,
        'Sheet1!A2:Z105',
        empty_rows
    )
    print("Successfully cleared rows 2-105")
except Exception as e:
    print(f"Error clearing rows: {e}")
