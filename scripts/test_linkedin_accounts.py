"""Test Salesrobot API to find LinkedIn account UUID."""

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

print("Testing endpoints to find LinkedIn account UUID...\n")

# Try different endpoints that might return LinkedIn accounts
endpoints = [
    '/linkedin-accounts',
    '/linkedinAccounts',
    '/accounts',
    '/me',
    '/user',
    '/profile',
    '/accounts/linkedin',
    '/v1/linkedin-accounts',
    '/v1/linkedinAccounts',
    '/v1/accounts',
    '/v1/me',
    '/v1/user',
    '/v1/profile',
]

for endpoint in endpoints:
    try:
        response = requests.get(f"{base_url}{endpoint}", headers=headers, timeout=10)
        print(f"{endpoint}: {response.status_code}")
        if response.status_code == 200:
            print(f"   SUCCESS! Response: {response.text[:500]}")
        elif response.status_code != 404:
            print(f"   Response: {response.text[:200]}")
    except Exception as e:
        print(f"{endpoint}: Error - {e}")

print("\nDone!")
