"""Print available Salesrobot campaigns."""

import os
import sys

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from salesrobot_client import SalesrobotClient
from settings import Settings

# Load settings
settings = Settings()

# Initialize client
api_key = settings.get_salesrobot_api_key()
linkedin_account_uuid = settings.get_linkedin_account_uuid()
client = SalesrobotClient(api_key, linkedin_account_uuid)

# Get campaigns
campaigns_response = client.get_campaigns()

print(f"Raw response type: {type(campaigns_response)}")
print(f"Raw response: {campaigns_response}")
print()

# Check if response is a dictionary with a 'data' field
if isinstance(campaigns_response, dict):
    print("Response is a dictionary")
    if 'data' in campaigns_response:
        campaigns = campaigns_response['data']
        print(f"Found {len(campaigns)} campaigns in 'data' field:\n")
        
        for i, campaign in enumerate(campaigns, start=1):
            print(f"{i}. Campaign UUID: {campaign.get('uuid', 'N/A')}")
            print(f"   Name: {campaign.get('name', 'N/A')}")
            print(f"   Status: {campaign.get('campaignStatus', 'N/A')}")
            print(f"   Type: {campaign.get('campaignType', 'N/A')}")
            print(f"   Family: {campaign.get('campaignFamily', 'N/A')}")
            print()
    else:
        print("No 'data' field in response")
        print(f"Available keys: {campaigns_response.keys()}")
elif isinstance(campaigns_response, list):
    print("Response is a list")
    print(f"Found {len(campaigns_response)} campaigns:\n")
    
    for i, campaign in enumerate(campaigns_response, start=1):
        print(f"{i}. Campaign UUID: {campaign.get('uuid', 'N/A')}")
        print(f"   Name: {campaign.get('name', 'N/A')}")
        print(f"   Status: {campaign.get('campaignStatus', 'N/A')}")
        print(f"   Type: {campaign.get('campaignType', 'N/A')}")
        print(f"   Family: {campaign.get('campaignFamily', 'N/A')}")
        print()
else:
    print(f"Unexpected response type: {type(campaigns_response)}")
