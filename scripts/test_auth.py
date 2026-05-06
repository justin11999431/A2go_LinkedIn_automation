"""Test different Salesrobot API authentication methods."""

import os
import sys
import requests

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.settings import Settings

# Load settings
settings = Settings()
api_key = settings.get_salesrobot_api_key()

# Test different authentication methods
base_url = "https://app.salesrobot.co/api"

print("Testing different authentication methods...\n")

# Method 1: Bearer token (current)
print("1. Testing Bearer token authentication...")
headers1 = {
    'Authorization': f'Bearer {api_key}',
    'Content-Type': 'application/json'
}
try:
    response = requests.get(f"{base_url}/campaigns", headers=headers1, timeout=10)
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.text[:200]}")
except Exception as e:
    print(f"   Error: {e}")

# Method 2: X-API-Key header
print("\n2. Testing X-API-Key header authentication...")
headers2 = {
    'X-API-Key': api_key,
    'Content-Type': 'application/json'
}
try:
    response = requests.get(f"{base_url}/campaigns", headers=headers2, timeout=10)
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.text[:200]}")
except Exception as e:
    print(f"   Error: {e}")

# Method 3: API key in query parameter
print("\n3. Testing API key in query parameter...")
headers3 = {
    'Content-Type': 'application/json'
}
try:
    response = requests.get(f"{base_url}/campaigns?api_key={api_key}", headers=headers3, timeout=10)
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.text[:200]}")
except Exception as e:
    print(f"   Error: {e}")

# Method 4: Basic auth with API key as username
print("\n4. Testing Basic authentication...")
headers4 = {
    'Content-Type': 'application/json'
}
try:
    response = requests.get(f"{base_url}/campaigns", headers=headers4, auth=(api_key, ''), timeout=10)
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.text[:200]}")
except Exception as e:
    print(f"   Error: {e}")

# Method 5: Try different endpoint paths
print("\n5. Testing different endpoint paths...")
endpoints = [
    '/campaigns',
    '/v1/campaigns',
    '/v2/campaigns',
    '/api/campaigns',
    '/campaigns/list',
    '/campaign/all',
    '/me/campaigns'
]

for endpoint in endpoints:
    try:
        response = requests.get(f"{base_url}{endpoint}", headers=headers1, timeout=10)
        print(f"   {endpoint}: {response.status_code}")
        if response.status_code == 200:
            print(f"      SUCCESS! Response: {response.text[:200]}")
    except Exception as e:
        print(f"   {endpoint}: Error - {e}")

print("\nDone!")
