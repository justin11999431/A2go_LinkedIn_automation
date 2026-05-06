"""Clean workflow sheet and write fresh data."""

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

print("Reading current workflow sheet state...")
data = client.get_sheet_data(workflow_sheet_id, 'Sheet1')
print(f"Total rows: {len(data)}")

print("\nClearing all data from rows 2-191...")
# Create empty rows for rows 2-191 (190 rows total)
empty_rows = [[''] * 26] * 190

# Use batch update to clear all rows at once
try:
    client.update_sheet_data(
        workflow_sheet_id,
        'Sheet1!A2:Z191',
        empty_rows
    )
    print("Successfully cleared rows 2-191")
except Exception as e:
    print(f"Error clearing rows: {e}")
    sys.exit(1)

print("\nVerifying cleanup...")
data = client.get_sheet_data(workflow_sheet_id, 'Sheet1')
print(f"Total rows after cleanup: {len(data)}")
print("First 5 rows:")
for i, row in enumerate(data[:5]):
    print(f"Row {i}: {row[:5]}")

print("\nSheet is now clean and ready for fresh data!")
