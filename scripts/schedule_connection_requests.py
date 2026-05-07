"""Schedule connection requests for 8:00am tomorrow."""

import os
import sys
from datetime import datetime, timedelta

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

print("Reading workflow sheet...")
data = client.get_sheet_data(workflow_sheet_id, 'Sheet1')

if not data or len(data) < 2:
    print("No data found in workflow sheet")
    sys.exit(1)

headers = data[0]
rows = data[1:]

# Find column indices
lead_id_col = None
linkedin_url_col = None
connection_request_col = None

for i, header in enumerate(headers):
    header_lower = header.lower()
    if 'lead id' in header_lower:
        lead_id_col = i
    elif 'linkedin profile url' in header_lower or 'linkedin' in header_lower:
        linkedin_url_col = i
    elif 'connection request message' in header_lower:
        connection_request_col = i

print(f"Found columns: Lead ID={lead_id_col}, LinkedIn URL={linkedin_url_col}, Connection Request={connection_request_col}")

# Extract connection requests
connection_requests = []
for row in rows:
    if not row:
        continue

    lead_id = row[lead_id_col] if lead_id_col is not None and lead_id_col < len(row) else ''
    linkedin_url = row[linkedin_url_col] if linkedin_url_col is not None and linkedin_url_col < len(row) else ''
    connection_request = row[connection_request_col] if connection_request_col is not None and connection_request_col < len(row) else ''

    if lead_id and linkedin_url and connection_request:
        connection_requests.append({
            'lead_id': lead_id,
            'linkedin_url': linkedin_url,
            'connection_request': connection_request
        })

print(f"Found {len(connection_requests)} connection requests")

# Calculate tomorrow 8:00am
tomorrow = datetime.now() + timedelta(days=1)
scheduled_time = tomorrow.replace(hour=8, minute=0, second=0, microsecond=0)

print(f"\nScheduled time: {scheduled_time.strftime('%Y-%m-%d %H:%M:%S')}")
print(f"\nFound {len(connection_requests)} connection requests")

# Create output file
output_file = os.path.join(os.path.dirname(__file__), 'connection_requests.txt')
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(f"Scheduled time: {scheduled_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    f.write(f"\nConnection requests to send:\n\n")

    for i, req in enumerate(connection_requests, 1):
        f.write(f"{i}. {req['lead_id']}\n")
        f.write(f"   LinkedIn: {req['linkedin_url']}\n")
        f.write(f"   Message: {req['connection_request']}\n\n")

print(f"Connection requests saved to: {output_file}")

# Create a batch file to schedule the task
batch_file_path = os.path.join(os.path.dirname(__file__), 'schedule_connection_requests.bat')

with open(batch_file_path, 'w') as f:
    f.write('@echo off\n')
    f.write('echo Scheduling connection requests for tomorrow at 8:00am...\n')
    f.write(f'schtasks /create /tn "A2go Connection Requests" /tr "python {os.path.join(os.path.dirname(__file__), "send_connection_requests.py")}" /sc once /st 08:00 /sd {tomorrow.strftime("%m/%d/%Y")} /f\n')
    f.write('echo Task scheduled successfully!\n')
    f.write('pause\n')

print(f"\nCreated batch file: {batch_file_path}")
print("Run this batch file to schedule the connection requests.")
print("\nNote: You'll need to create the send_connection_requests.py script to actually send the requests.")
