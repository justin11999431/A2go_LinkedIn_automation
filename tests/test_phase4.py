"""Tests for Phase 4: GHL Client Integration."""

import unittest
from unittest.mock import patch, MagicMock
from src.ghl_client import GHLClient

class TestPhase4(unittest.TestCase):
    
    def setUp(self):
        self.api_key = "test_pit_token"
        self.location_id = "test_loc_id"
        self.client = GHLClient(self.api_key, self.location_id)

    @patch('requests.request')
    def test_get_contact_by_email_found(self, mock_request):
        """Test lookup when contact exists."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "contacts": [{"id": "contact_123", "email": "test@example.com"}]
        }
        mock_request.return_value = mock_response
        
        contact = self.client.get_contact_by_email("test@example.com")
        self.assertIsNotNone(contact)
        self.assertEqual(contact["id"], "contact_123")

    @patch('requests.request')
    def test_get_contact_by_email_not_found(self, mock_request):
        """Test lookup when contact doesn't exist."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"contacts": []}
        mock_request.return_value = mock_response
        
        contact = self.client.get_contact_by_email("notfound@example.com")
        self.assertIsNone(contact)

    @patch('src.ghl_client.GHLClient.get_contact_by_email')
    @patch('requests.request')
    def test_upsert_contact_new(self, mock_request, mock_lookup):
        """Test creating a new contact."""
        mock_lookup.return_value = None
        
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"contact": {"id": "new_id"}}
        mock_request.return_value = mock_response
        
        contact_id = self.client.upsert_contact({"email": "new@example.com", "firstName": "New"})
        self.assertEqual(contact_id, "new_id")
        # Verify POST was called
        self.assertEqual(mock_request.call_args[0][0], "POST")

    @patch('src.ghl_client.GHLClient.get_contact_by_email')
    @patch('requests.request')
    def test_upsert_contact_existing(self, mock_request, mock_lookup):
        """Test updating an existing contact."""
        mock_lookup.return_value = {"id": "existing_id"}
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"contact": {"id": "existing_id"}}
        mock_request.return_value = mock_response
        
        contact_id = self.client.upsert_contact({"email": "old@example.com", "firstName": "Updated"})
        self.assertEqual(contact_id, "existing_id")
        # Verify PUT was called
        self.assertEqual(mock_request.call_args[0][0], "PUT")

if __name__ == "__main__":
    unittest.main()
