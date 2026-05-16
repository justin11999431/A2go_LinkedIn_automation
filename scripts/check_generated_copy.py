"""Check generated copy for Walt Walker."""

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

# Read data
data = client.get_sheet_data(workflow_sheet_id, 'Sheet1')

# Print full row
print('Full Row 1 (Walt Walker):')
for i, col in enumerate(data[1]):
    print(f'Column {i}: {col}')
