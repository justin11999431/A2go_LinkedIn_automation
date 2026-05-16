"""Tests for Phase 11: Cloudflare DNS Verification."""

import unittest
from unittest.mock import patch, MagicMock
from src.cloudflare_client import CloudflareClient

class TestPhase11(unittest.TestCase):
    
    def setUp(self):
        self.client = CloudflareClient("test_token", "test_acc")

    @patch('requests.request')
    def test_audit_email_auth_found(self, mock_request):
        """Test auditing when records are present."""
        # Mock zones response
        mock_zones = MagicMock()
        mock_zones.status_code = 200
        mock_zones.json.return_value = {"result": [{"id": "zone_123", "name": "a2gotools.com"}]}
        
        # Mock dns records response
        mock_records = MagicMock()
        mock_records.status_code = 200
        mock_records.json.return_value = {"result": [
            {"type": "TXT", "name": "a2gotools.com", "content": "v=spf1 include:spf.brevo.com ~all"},
            {"type": "TXT", "name": "_dmarc.a2gotools.com", "content": "v=DMARC1; p=none;"},
            {"type": "TXT", "name": "mail._domainkey.a2gotools.com", "content": "v=DKIM1; k=rsa; p=..."}
        ]}
        
        mock_request.side_effect = [mock_zones, mock_records]
        
        audit = self.client.audit_email_auth("a2gotools.com")
        
        self.assertEqual(audit["spf"]["status"], "found")
        self.assertEqual(audit["dmarc"]["status"], "found")
        self.assertEqual(audit["dkim"]["status"], "found")
        self.assertIn("v=spf1", audit["spf"]["record"])

if __name__ == "__main__":
    unittest.main()
