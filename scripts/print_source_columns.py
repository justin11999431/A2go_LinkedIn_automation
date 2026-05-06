"""Print source sheet column names."""

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

# Get source sheet data
source_sheet_id = settings.get_source_sheet_id()
data = client.get_sheet_data(source_sheet_id, 'A2go-Forecast-Intent-75!A1:Z1')

if data and len(data) > 0:
    headers = data[0]
    print("Source Sheet Column Names:")
    for i, header in enumerate(headers, start=1):
        print(f"  {i}. {header}")
else:
    print("No data found in source sheet")
