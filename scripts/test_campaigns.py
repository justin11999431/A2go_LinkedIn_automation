"""Test Salesrobot API campaigns with LinkedIn account UUID."""

import os
import sys
import requests

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.settings import Settings

# Load settings
settings = Settings()
api_key = settings.get_salesrobot_api_key()

base_url = "https://app.salesrobot.co/api"

headers = {
    'X-API-Key': api_key,
    'Content-Type': 'application/json'
}

linkedin_account_uuid = "dd113af4-85e7-4b58-a033-fefaabb49486"

print("Testing campaigns endpoint with LinkedIn account UUID...\n")

# Test campaigns endpoint with linkedinAccountUuid parameter
try:
    response = requests.get(
        f"{base_url}/campaigns",
        headers=headers,
        params={'linkedinAccountUuid': linkedin_account_uuid},
        timeout=10
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")

print("\nDone!")
