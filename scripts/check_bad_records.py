"""Check specific rows in workflow sheet to identify bad records."""

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

# Check rows 2-101 (the bad records)
print("Checking rows 2-101 (bad records):")
print("=" * 80)

for row_num in range(2, 102):
    data = client.get_sheet_data(workflow_sheet_id, f'Sheet1!A{row_num}:Z{row_num}')
    
    if data and len(data) > 0:
        row = data[0]
        if any(row):  # Only show non-empty rows
            print(f"\nRow {row_num}:")
            for i, value in enumerate(row):
                if value:  # Only show non-empty values
                    print(f"  Column {i+1}: {value}")

print("\n" + "=" * 80)
print("Checking row 101 (the one you can see):")
print("=" * 80)

data = client.get_sheet_data(workflow_sheet_id, 'Sheet1!A101:Z101')
if data and len(data) > 0:
    row = data[0]
    print(f"\nRow 101:")
    for i, value in enumerate(row):
        print(f"  Column {i+1} ({i}): {value}")
