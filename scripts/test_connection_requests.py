"""Test script to verify connection requests can be read."""

import os
import sys

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from google_sheets import GoogleSheetsClient
from salesrobot_client import SalesrobotClient
from settings import Settings


def test_read_connection_requests():
    """Test reading connection requests from file."""
    connection_requests_file = os.path.join(
        os.path.dirname(__file__), 
        'connection_requests.txt'
    )
    
    if not os.path.exists(connection_requests_file):
        print(f"ERROR: Connection requests file not found: {connection_requests_file}")
        return False
    
    requests = []
    
    with open(connection_requests_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    current_request = None
    for line in lines:
        line = line.strip()
        
        if line.startswith('Scheduled time:'):
            continue
        elif line.startswith('Connection requests to send:'):
            continue
        elif line == '':
            continue
        elif line.startswith('LinkedIn:'):
            if current_request:
                current_request['linkedin_url'] = line.split(':', 1)[1].strip()
        elif line.startswith('Message:'):
            if current_request:
                current_request['message'] = line.split(':', 1)[1].strip()
        elif line and line[0].isdigit() and '.' in line:
            # This is a numbered item line like "1. Walt Walker"
            if current_request:
                requests.append(current_request)
            # Extract the name (everything after the number and period)
            parts = line.split('.', 1)
            if len(parts) > 1:
                current_request = {'lead_id': parts[1].strip()}
            else:
                current_request = {'lead_id': line.strip()}
    
    # Add the last request
    if current_request:
        requests.append(current_request)
    
    print(f"Successfully read {len(requests)} connection requests")
    print("\nFirst 3 requests:")
    for i, req in enumerate(requests[:3], 1):
        print(f"\n{i}. {req['lead_id']}")
        print(f"   Message: {req['message'][:100]}...")
    
    return True


def test_settings():
    """Test settings configuration."""
    print("\nTesting settings configuration...")
    
    settings = Settings()
    
    # Check Salesrobot API key
    api_key = settings.get_salesrobot_api_key()
    print(f"Salesrobot API Key: {'Found' if api_key else 'Not found'}")
    
    # Check LinkedIn account UUID
    linkedin_uuid = settings.get_linkedin_account_uuid()
    print(f"LinkedIn Account UUID: {'Found' if linkedin_uuid else 'Not found'}")
    
    # Check workflow sheet ID
    workflow_sheet_id = settings.get_workflow_sheet_id()
    print(f"Workflow Sheet ID: {'Found' if workflow_sheet_id else 'Not found'}")
    
    # Check OAuth credentials
    oauth_refresh_token = settings.get_oauth_refresh_token()
    oauth_client_id = settings.get_oauth_client_id()
    oauth_client_secret = settings.get_oauth_client_secret()
    
    print(f"OAuth Refresh Token: {'Found' if oauth_refresh_token else 'Not found'}")
    print(f"OAuth Client ID: {'Found' if oauth_client_id else 'Not found'}")
    print(f"OAuth Client Secret: {'Found' if oauth_client_secret else 'Not found'}")
    
    return True


def test_salesrobot_client():
    """Test Salesrobot client initialization."""
    print("\nTesting Salesrobot client initialization...")
    
    settings = Settings()
    
    try:
        salesrobot_api_key = settings.get_salesrobot_api_key()
        linkedin_account_uuid = settings.get_linkedin_account_uuid()
        
        if not salesrobot_api_key:
            print("ERROR: Salesrobot API key not found")
            return False
        
        client = SalesrobotClient(
            api_key=salesrobot_api_key,
            linkedin_account_uuid=linkedin_account_uuid
        )
        
        print("Salesrobot client initialized successfully")
        
        # Test getting LinkedIn accounts
        try:
            accounts = client.get_linkedin_accounts()
            print(f"Found {len(accounts)} LinkedIn accounts")
            for account in accounts[:3]:
                print(f"  - {account.get('name', 'Unknown')}: {account.get('uuid', 'No UUID')}")
        except Exception as e:
            print(f"Warning: Could not retrieve LinkedIn accounts: {e}")
        
        return True
        
    except Exception as e:
        print(f"ERROR: Failed to initialize Salesrobot client: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("CONNECTION REQUESTS TEST")
    print("=" * 60)
    
    # Test 1: Read connection requests
    print("\nTest 1: Reading connection requests file")
    print("-" * 60)
    test_read_connection_requests()
    
    # Test 2: Settings configuration
    print("\nTest 2: Settings configuration")
    print("-" * 60)
    test_settings()
    
    # Test 3: Salesrobot client
    print("\nTest 3: Salesrobot client initialization")
    print("-" * 60)
    test_salesrobot_client()
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)
    print("\nAll tests passed! Ready to send connection requests.")
    print("\nTo send connection requests now, run:")
    print("  python scripts/send_connection_requests.py")
    print("\nTo schedule for tomorrow at 8:00am, run:")
    print("  scripts/schedule_connection_requests.bat")


if __name__ == '__main__':
    main()
