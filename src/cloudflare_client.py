"""Cloudflare API client for DNS management and verification."""

import requests
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class CloudflareClient:
    """Client for interacting with Cloudflare API V4."""
    
    BASE_URL = "https://api.cloudflare.com/client/v4"
    
    def __init__(self, api_token: str, account_id: str):
        """Initialize Cloudflare client.
        
        Args:
            api_token: Cloudflare API Token
            account_id: Cloudflare Account ID
        """
        self.api_token = api_token
        self.account_id = account_id
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }

    def _request(self, method: str, path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute an API request."""
        url = f"{self.BASE_URL}{path}"
        try:
            response = requests.request(method, url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            logger.error(f"Cloudflare API Error: {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Cloudflare Request Error: {e}")
            raise

    def get_zones(self) -> List[Dict[str, Any]]:
        """List all zones for the account."""
        result = self._request("GET", "/zones")
        return result.get("result", [])

    def get_dns_records(self, zone_id: str) -> List[Dict[str, Any]]:
        """List DNS records for a specific zone."""
        result = self._request("GET", f"/zones/{zone_id}/dns_records")
        return result.get("result", [])

    def audit_email_auth(self, zone_name: str) -> Dict[str, Any]:
        """Audit SPF, DKIM, and DMARC for a domain.
        
        Args:
            zone_name: Domain name (e.g., 'a2gotools.com')
        """
        zones = self.get_zones()
        zone = next((z for z in zones if z['name'] == zone_name), None)
        
        if not zone:
            return {"error": f"Zone {zone_name} not found in account."}
            
        records = self.get_dns_records(zone['id'])
        
        audit = {
            "spf": {"status": "missing", "record": None},
            "dkim": {"status": "missing", "records": []},
            "dmarc": {"status": "missing", "record": None}
        }
        
        for r in records:
            content = r.get("content", "")
            type = r.get("type", "")
            name = r.get("name", "")
            
            if type == "TXT" and "v=spf1" in content:
                audit["spf"] = {"status": "found", "record": content}
            elif type == "TXT" and "v=DMARC1" in content:
                audit["dmarc"] = {"status": "found", "record": content}
            elif type == "TXT" and ("dkim" in name or "domainkey" in name):
                audit["dkim"]["status"] = "found"
                audit["dkim"]["records"].append(content)
                
        return audit
