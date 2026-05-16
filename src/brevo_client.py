"""Brevo API client for transactional email sending."""

import requests
import logging
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

class BrevoClient:
    """Client for interacting with Brevo API V3."""
    
    BASE_URL = "https://api.brevo.com/v3"
    
    def __init__(self, api_key: str):
        """Initialize Brevo client.
        
        Args:
            api_key: Brevo API Key
        """
        self.api_key = api_key
        self.headers = {
            "api-key": self.api_key,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    def _request(self, method: str, path: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute an API request."""
        url = f"{self.BASE_URL}{path}"
        try:
            response = requests.request(method, url, headers=self.headers, json=data)
            response.raise_for_status()
            if response.status_code != 204:
                return response.json()
            return {}
        except requests.exceptions.HTTPError as e:
            logger.error(f"Brevo API Error ({method} {path}): {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Brevo Request Error: {e}")
            raise

    def send_email(self, to_email: str, subject: str, html_content: str, 
                   sender_name: str, sender_email: str, 
                   to_name: Optional[str] = None) -> str:
        """Send a transactional email.
        
        Args:
            to_email: Recipient email
            subject: Email subject
            html_content: Email body in HTML
            sender_name: Sender name
            sender_email: Sender email
            to_name: Optional recipient name
            
        Returns:
            Message ID
        """
        payload = {
            "sender": {"name": sender_name, "email": sender_email},
            "to": [{"email": to_email, "name": to_name or to_email}],
            "subject": subject,
            "htmlContent": html_content
        }
        
        result = self._request("POST", "/smtp/email", data=payload)
        message_id = result.get("messageId", "")
        logger.info(f"Email sent to {to_email} via Brevo. Message ID: {message_id}")
        return message_id

    def get_account_info(self) -> Dict[str, Any]:
        """Get Brevo account information (used for verification)."""
        return self._request("GET", "/account")
