"""Schedule connection requests for 8:00am tomorrow."""

import os
import sys
from datetime import datetime, timedelta

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from settings import Settings

# Load settings
settings = Settings()

# Get workflow sheet ID
workflow_sheet_id = settings.get_workflow_sheet_id()

# Calculate tomorrow 8:00am
tomorrow = datetime.now() + timedelta(days=1)
scheduled_time = tomorrow.replace(hour=8, minute=0, second=0, microsecond=0)

print(f"Scheduled time: {scheduled_time.strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Found {len(connection_requests)} connection requests")
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
