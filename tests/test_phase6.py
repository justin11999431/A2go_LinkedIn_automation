"""Tests for Phase 6: Brevo Email and Webhook Handling."""

import unittest
from unittest.mock import patch, MagicMock
import os
from src.brevo_client import BrevoClient
from src.webhooks.brevo_handler import handle_brevo_webhook
from src.database import StateDatabase
from src.models import SequenceState

class TestPhase6(unittest.TestCase):
    
    def setUp(self):
        self.test_db = "data/test_brevo.db"
        if os.path.exists(self.test_db):
            os.remove(self.test_db)
        self.db = StateDatabase(self.test_db)
        self.client = BrevoClient("test_api_key")

    def tearDown(self):
        if os.path.exists(self.test_db):
            os.remove(self.test_db)

    @patch('requests.request')
    def test_send_email_success(self, mock_request):
        """Test successful email sending."""
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"messageId": "msg_123"}
        mock_request.return_value = mock_response
        
        msg_id = self.client.send_email(
            to_email="test@example.com",
            subject="Hello",
            html_content="<p>Hi</p>",
            sender_name="Sender",
            sender_email="sender@example.com"
        )
        self.assertEqual(msg_id, "msg_123")

    @patch('src.webhooks.brevo_handler.StateDatabase')
    def test_webhook_replied_pauses_automation(self, mock_db_class):
        """Test that a 'replied' event pauses automation."""
        # Setup mock DB
        mock_db_inst = mock_db_class.return_value
        mock_db_inst.db_path = self.test_db
        
        lead_id = "lead_replied"
        email = "replier@example.com"
        
        # Pre-populate state
        state = SequenceState(lead_id=lead_id, email=email, is_paused=False)
        mock_db_inst.get_state_by_email.return_value = state
        
        # Webhook payload
        payload = {
            "event": "replied",
            "email": email
        }
        
        with patch('src.webhooks.brevo_handler.pauseContactAutomation') as mock_pause:
            success = handle_brevo_webhook(payload)
            self.assertTrue(success)
            mock_pause.assert_called_once_with(lead_id, "Brevo webhook: replied")

if __name__ == "__main__":
    unittest.main()
