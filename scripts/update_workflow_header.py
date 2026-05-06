"""Update workflow sheet header to match new column mapping."""

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

# New header row
new_header = [
    'Lead ID',
    'LinkedIn Profile URL',
    'First Name',
    'Last Name',
    'Company',
    'Title',
    'Industry',
    'Location',
    'Connection Status',
    'Current Step',
    'Step Status',
    'Last Action Date',
    'Next Action Date',
    'Connection Request Message',
    'First Follow-up Message',
    'Second Follow-up Message',
    'Third Follow-up Message',
    'Fourth Follow-up Message',
    'Fifth Follow-up Message',
    'Sixth Follow-up Message',
    'Seventh Follow-up Message',
    'Eighth Follow-up Message',
    'Ninth Follow-up Message',
    'Tenth Follow-up Message',
    'Notes',
    'Last Updated',
]

print("Updating workflow sheet header...")
try:
    client.update_sheet_data(workflow_sheet_id, 'Sheet1!A1:Z1', [new_header])
    print("Successfully updated header row")
except Exception as e:
    print(f"Error updating header: {e}")
    sys.exit(1)

print("\nVerifying header update...")
data = client.get_sheet_data(workflow_sheet_id, 'Sheet1')
print("New header row:")
print(data[0])

print("\nHeader updated successfully!")
