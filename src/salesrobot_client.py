"""Salesrobot API client for campaign and lead management."""

import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

logger = logging.getLogger(__name__)


class SalesrobotClient:
    """Client for interacting with Salesrobot API."""
    
    BASE_URL = "https://app.salesrobot.co/api"
    
    def __init__(self, api_key: Optional[str] = None, linkedin_account_uuid: Optional[str] = None):
        """Initialize Salesrobot client.
        
        Args:
            api_key: Salesrobot API key
            linkedin_account_uuid: LinkedIn account UUID (required for most operations)
        """
        if not REQUESTS_AVAILABLE:
            raise ImportError("Requests library not installed. Run: pip install requests")
        
        self.api_key = api_key or os.getenv('SALESROBOT_API_KEY')
        if not self.api_key:
            raise ValueError("API key required. Set SALESROBOT_API_KEY environment variable or pass api_key parameter.")
        
        self.linkedin_account_uuid = linkedin_account_uuid or os.getenv('LINKEDIN_ACCOUNT_UUID')
        
        self.headers = {
            'X-API-Key': self.api_key,
            'Content-Type': 'application/json'
        }
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """Make HTTP request to Salesrobot API.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint
            data: Request body data
            
        Returns:
            Response JSON
        """
        url = f"{self.BASE_URL}{endpoint}"
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=self.headers, params=data)
            elif method == 'POST':
                response = requests.post(url, headers=self.headers, json=data)
            elif method == 'PUT':
                response = requests.put(url, headers=self.headers, json=data)
            elif method == 'DELETE':
                response = requests.delete(url, headers=self.headers)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            raise
    
    def get_linkedin_accounts(self) -> List[Dict[str, Any]]:
        """Get all LinkedIn accounts.
        
        Returns:
            List of LinkedIn accounts
        """
        return self._make_request('GET', '/linkedinAccounts')
    
    def get_campaigns(self) -> List[Dict[str, Any]]:
        """Get all campaigns.
        
        Returns:
            List of campaigns
        """
        if not self.linkedin_account_uuid:
            raise ValueError("linkedin_account_uuid required. Set LINKEDIN_ACCOUNT_UUID environment variable or pass linkedin_account_uuid parameter.")
        
        params = {'linkedinAccountUuid': self.linkedin_account_uuid}
        response = self._make_request('GET', '/campaigns', params)
        
        # Extract campaigns from response
        if isinstance(response, dict) and 'data' in response:
            if isinstance(response['data'], dict) and 'data' in response['data']:
                return response['data']['data']
            elif isinstance(response['data'], list):
                return response['data']
        
        return []
    
    def get_campaign(self, campaign_id: str) -> Dict[str, Any]:
        """Get campaign details.
        
        Args:
            campaign_id: Campaign ID
            
        Returns:
            Campaign details
        """
        return self._make_request('GET', f'/campaigns/{campaign_id}')
    
    def create_campaign(self, name: str, settings: Dict[str, Any]) -> Dict[str, Any]:
        """Create new campaign.
        
        Args:
            name: Campaign name
            settings: Campaign settings
            
        Returns:
            Created campaign
        """
        data = {'name': name, **settings}
        return self._make_request('POST', '/campaigns', data)
    
    def update_campaign(self, campaign_id: str, settings: Dict[str, Any]) -> Dict[str, Any]:
        """Update campaign.
        
        Args:
            campaign_id: Campaign ID
            settings: Campaign settings to update
            
        Returns:
            Updated campaign
        """
        return self._make_request('PUT', f'/campaigns/{campaign_id}', settings)
    
    def delete_campaign(self, campaign_id: str) -> None:
        """Delete campaign.
        
        Args:
            campaign_id: Campaign ID
        """
        self._make_request('DELETE', f'/campaigns/{campaign_id}')
    
    def get_leads(self, campaign_id: Optional[str] = None, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get leads.
        
        Args:
            campaign_id: Filter by campaign ID
            status: Filter by status
            
        Returns:
            List of leads
        """
        params = {}
        if campaign_id:
            params['campaign_id'] = campaign_id
        if status:
            params['status'] = status
        
        return self._make_request('GET', '/leads', params)
    
    def get_lead(self, lead_id: str) -> Dict[str, Any]:
        """Get lead details.
        
        Args:
            lead_id: Lead ID
            
        Returns:
            Lead details
        """
        return self._make_request('GET', f'/leads/{lead_id}')
    
    def create_lead(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new lead.
        
        Args:
            lead_data: Lead data
            
        Returns:
            Created lead
        """
        return self._make_request('POST', '/leads', lead_data)
    
    def update_lead(self, lead_id: str, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update lead.
        
        Args:
            lead_id: Lead ID
            lead_data: Lead data to update
            
        Returns:
            Updated lead
        """
        return self._make_request('PUT', f'/leads/{lead_id}', lead_data)
    
    def delete_lead(self, lead_id: str) -> None:
        """Delete lead.
        
        Args:
            lead_id: Lead ID
        """
        self._make_request('DELETE', f'/leads/{lead_id}')
    
    def enroll_lead_in_campaign(self, lead_id: str, campaign_id: str) -> Dict[str, Any]:
        """Enroll lead in campaign.
        
        Args:
            lead_id: Lead ID
            campaign_id: Campaign ID
            
        Returns:
            Enrollment result
        """
        return self._make_request('POST', f'/leads/{lead_id}/enroll', {'campaign_id': campaign_id})
    
    def unenroll_lead_from_campaign(self, lead_id: str, campaign_id: str) -> None:
        """Unenroll lead from campaign.
        
        Args:
            lead_id: Lead ID
            campaign_id: Campaign ID
        """
        self._make_request('DELETE', f'/leads/{lead_id}/campaigns/{campaign_id}')
    
    def get_campaign_stats(self, campaign_id: str) -> Dict[str, Any]:
        """Get campaign statistics.
        
        Args:
            campaign_id: Campaign ID
            
        Returns:
            Campaign statistics
        """
        return self._make_request('GET', f'/campaigns/{campaign_id}/stats')
