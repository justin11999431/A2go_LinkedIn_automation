"""Tests for Phase 9: MessageBird SMS and Webhook Handling."""

import unittest
from unittest.mock import patch, MagicMock
import os
from src.messagebird_client import MessageBirdClient
from src.webhooks.messagebird_handler import handle_messagebird_webhook
from src.database import StateDatabase
from src.models import SequenceState

class TestPhase9(unittest.TestCase):
    
    def setUp(self):
        self.test_db = "data/test_sms.db"
        if os.path.exists(self.test_db):
            os.remove(self.test_db)
        self.db = StateDatabase(self.test_db)
        self.client = MessageBirdClient("test_api_key")

    def tearDown(self):
        if os.path.exists(self.test_db):
            os.remove(self.test_db)

    @patch('requests.post')
    def test_send_sms_success(self, mock_post):
        """Test successful SMS sending."""
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"id": "sms_123"}
        mock_post.return_value = mock_response
        
        msg_id = self.client.send_sms(to_phone="+1234567890", body="Hello")
        self.assertEqual(msg_id, "sms_123")

    @patch('src.webhooks.messagebird_handler.StateDatabase')
    def test_webhook_reply_pauses_automation(self, mock_db_class):
        """Test that an SMS reply pauses automation."""
        mock_db_inst = mock_db_class.return_value
        
        lead_id = "lead_sms_replied"
        phone = "+1987654321"
        
        state = SequenceState(lead_id=lead_id, email="test@ex.com", phone=phone, is_paused=False)
        mock_db_inst.get_state_by_phone.return_value = state
        
        payload = {
            "originator": phone,
            "body": "Stop"
        }
        
        with patch('src.webhooks.messagebird_handler.pauseContactAutomation') as mock_pause:
            success = handle_messagebird_webhook(payload)
            self.assertTrue(success)
            mock_pause.assert_called_once_with(lead_id, "SMS reply received: stop")

if __name__ == "__main__":
    unittest.main()
