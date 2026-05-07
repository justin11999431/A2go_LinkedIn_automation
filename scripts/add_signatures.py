"""Add signature to all messages in workflow sheet."""

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

# Signature
SIGNATURE = """
Patrick Romeri
Director of Marketing
Analytics2Go, Inc.
M +1 508-808-4820
W www.a2go.ai"""

print("Reading workflow sheet...")
data = client.get_sheet_data(workflow_sheet_id, 'Sheet1')

if not data or len(data) < 2:
    print("No data found in workflow sheet")
    sys.exit(1)

headers = data[0]
rows = data[1:]

# Find column indices for messages
connection_request_col = None
message_1_col = None
message_2_col = None
message_3_col = None
message_4_col = None

for i, header in enumerate(headers):
    header_lower = header.lower()
    if 'connection request' in header_lower:
        connection_request_col = i
    elif 'first follow-up' in header_lower or 'message 1' in header_lower:
        message_1_col = i
    elif 'second follow-up' in header_lower or 'message 2' in header_lower:
        message_2_col = i
    elif 'third follow-up' in header_lower or 'message 3' in header_lower:
        message_3_col = i
    elif 'fourth follow-up' in header_lower or 'message 4' in header_lower:
        message_4_col = i

print(f"Found columns: Connection Request={connection_request_col}, Message 1={message_1_col}, Message 2={message_2_col}, Message 3={message_3_col}, Message 4={message_4_col}")

# Update rows with signature
updated_rows = []
for row in rows:
    if not row:
        continue

    # Add signature to messages (not connection request)
    if message_1_col is not None and message_1_col < len(row) and row[message_1_col]:
        row[message_1_col] = row[message_1_col] + SIGNATURE

    if message_2_col is not None and message_2_col < len(row) and row[message_2_col]:
        row[message_2_col] = row[message_2_col] + SIGNATURE

    if message_3_col is not None and message_3_col < len(row) and row[message_3_col]:
        row[message_3_col] = row[message_3_col] + SIGNATURE

    if message_4_col is not None and message_4_col < len(row) and row[message_4_col]:
        row[message_4_col] = row[message_4_col] + SIGNATURE

    updated_rows.append(row)

print(f"Updated {len(updated_rows)} rows with signature")

# Update the sheet
if updated_rows:
    print("Updating workflow sheet...")
    client.update_sheet_data(workflow_sheet_id, 'Sheet1!A2:Z' + str(len(updated_rows) + 1), updated_rows)
    print("Successfully updated workflow sheet with signatures")
else:
    print("No rows to update")
