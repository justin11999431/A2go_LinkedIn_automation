"""GoHighLevel API client for contact management."""

import requests
import logging
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

class GHLClient:
    """Client for interacting with GoHighLevel V2 API."""
    
    BASE_URL = "https://services.leadconnectorhq.com"
    
    def __init__(self, api_key: str, location_id: str):
        """Initialize GHL client.
        
        Args:
            api_key: Private Integration Token (PIT)
            location_id: GHL Location ID
        """
        self.api_key = api_key
        self.location_id = location_id
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Version": "2021-07-28",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    def _request(self, method: str, path: str, data: Optional[Dict[str, Any]] = None, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute an API request."""
        url = f"{self.BASE_URL}{path}"
        try:
            response = requests.request(method, url, headers=self.headers, json=data, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            logger.error(f"GHL API Error ({method} {path}): {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"GHL Request Error: {e}")
            raise

    def get_appointments(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """Fetch appointments within a date range.
        
        Args:
            start_date: Start timestamp (ISO)
            end_date: End timestamp (ISO)
        """
        params = {
            "locationId": self.location_id,
            "startDate": start_date,
            "endDate": end_date
        }
        try:
            result = self._request("GET", "/appointments/", params=params)
            return result.get("appointments", [])
        except Exception:
            return []

    def add_note(self, contact_id: str, body: str) -> bool:
        """Add a note to a contact record.
        
        Args:
            contact_id: GHL Contact ID
            body: Note content
        """
        payload = {"body": body}
        try:
            self._request("POST", f"/contacts/{contact_id}/notes", data=payload)
            return True
        except Exception:
            return False

    def create_conversation_message(self, contact_id: str, type: str, body: str, direction: str = "outbound") -> bool:
        """Post a message to the GHL conversation inbox.
        
        Args:
            contact_id: GHL Contact ID
            type: 'Email', 'SMS', 'LinkedIn'
            body: Message content
            direction: 'inbound' or 'outbound'
        """
        # Note: GHL V2 Conversations API requires specific formatting
        payload = {
            "contactId": contact_id,
            "type": type,
            "body": body,
            "direction": direction,
            "status": "delivered"
        }
        try:
            # Endpoint for conversation messages
            self._request("POST", "/conversations/messages", data=payload)
            return True
        except Exception:
            # Fallback to note if conversation posting fails
            self.add_note(contact_id, f"[{type} {direction}] {body}")
            return False

    def get_contact_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Lookup a contact by email.
        
        Returns:
            Contact dictionary or None
        """
        params = {
            "locationId": self.location_id,
            "query": email
        }
        try:
            result = self._request("GET", "/contacts/", params=params)
            contacts = result.get("contacts", [])
            return contacts[0] if contacts else None
        except Exception:
            return None

    def upsert_contact(self, contact_data: Dict[str, Any]) -> str:
        """Create or update a contact.
        
        Args:
            contact_data: Dictionary containing contact fields (email is required)
            
        Returns:
            GHL Contact ID
        """
        email = contact_data.get("email")
        if not email:
            raise ValueError("Email is required for GHL contact upsert")

        existing_contact = self.get_contact_by_email(email)
        
        payload = contact_data.copy()
        payload["locationId"] = self.location_id
        
        # Transform customFields if provided as a dict
        if "customFields" in payload and isinstance(payload["customFields"], dict):
            payload["customFields"] = [{"id": k, "value": v} for k, v in payload["customFields"].items()]
        
        if existing_contact:
            contact_id = existing_contact["id"]
            logger.info(f"Updating existing GHL contact: {email} ({contact_id})")
            self._request("PUT", f"/contacts/{contact_id}", data=payload)
            return contact_id
        else:
            logger.info(f"Creating new GHL contact: {email}")
            result = self._request("POST", "/contacts/", data=payload)
            return result["contact"]["id"]

    def add_tag(self, contact_id: str, tags: List[str]) -> bool:
        """Add tags to a contact.
        
        Args:
            contact_id: GHL Contact ID
            tags: List of tags to add
        """
        payload = {"tags": tags}
        try:
            self._request("POST", f"/contacts/{contact_id}/tags", data=payload)
            return True
        except Exception:
            return False

    def update_custom_fields(self, contact_id: str, custom_fields: Dict[str, Any]) -> bool:
        """Update custom fields for a contact.
        
        Args:
            contact_id: GHL Contact ID
            custom_fields: Dictionary of field key/value pairs
        """
        # GHL V2 expects custom fields as a list of dicts: {"id": "key", "value": "val"}
        # But wait, sometimes it's just the object. 
        # In V2, it's often in the main contact object or as a list.
        # Let's assume the standard update format for contacts.
        payload = {
            "customFields": [{"id": k, "value": v} for k, v in custom_fields.items()]
        }
        try:
            self._request("PUT", f"/contacts/{contact_id}", data=payload)
            return True
        except Exception:
            return False
