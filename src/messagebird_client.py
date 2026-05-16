"""MessageBird API client for SMS sending."""

import requests
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class MessageBirdClient:
    """Client for interacting with MessageBird API."""
    
    BASE_URL = "https://rest.messagebird.com"
    
    def __init__(self, api_key: str):
        """Initialize MessageBird client.
        
        Args:
            api_key: MessageBird Access Key
        """
        self.api_key = api_key
        self.headers = {
            "Authorization": f"AccessKey {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    def send_sms(self, to_phone: str, body: str, originator: str = "A2go") -> str:
        """Send an SMS message.
        
        Args:
            to_phone: Recipient phone number (E.164 format)
            body: Message content
            originator: Sender ID or phone number
            
        Returns:
            Message ID
        """
        payload = {
            "recipients": [to_phone],
            "originator": originator,
            "body": body
        }
        
        try:
            url = f"{self.BASE_URL}/messages"
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            result = response.json()
            message_id = result.get("id", "")
            logger.info(f"SMS sent to {to_phone} via MessageBird. ID: {message_id}")
            return message_id
        except requests.exceptions.HTTPError as e:
            logger.error(f"MessageBird API Error: {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"MessageBird Request Error: {e}")
            raise
