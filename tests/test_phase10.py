"""Tests for Phase 10: GHL Appointment Monitoring."""

import unittest
from unittest.mock import patch, MagicMock
from src.webhooks.ghl_handler import handle_ghl_webhook
from src.models import SequenceState

class TestPhase10(unittest.TestCase):
    
    @patch('src.webhooks.ghl_handler.StateDatabase')
    @patch('src.webhooks.ghl_handler.pauseContactAutomation')
    def test_appointment_webhook_pauses_automation(self, mock_pause, mock_db_class):
        """Test that a GHL appointment webhook pauses automation."""
        mock_db_inst = mock_db_class.return_value
        
        email = "booked@example.com"
        state = SequenceState(lead_id="lead_booked", email=email, is_paused=False)
        mock_db_inst.get_state_by_email.return_value = state
        
        # GHL V2 Appointment Payload
        payload = {
            "type": "appointment",
            "contactId": "ghl_contact_123",
            "email": email
        }
        
        success = handle_ghl_webhook(payload)
        self.assertTrue(success)
        mock_pause.assert_called_once_with("lead_booked", "GHL Appointment Booked")

    @patch('src.webhooks.ghl_handler.StateDatabase')
    @patch('src.webhooks.ghl_handler.pauseContactAutomation')
    def test_stop_tag_webhook_pauses_automation(self, mock_pause, mock_db_class):
        """Test that a 'Stop Outreach' tag pauses automation."""
        mock_db_inst = mock_db_class.return_value
        
        email = "stop_me@example.com"
        state = SequenceState(lead_id="lead_stop", email=email, is_paused=False)
        mock_db_inst.get_state_by_email.return_value = state
        
        payload = {
            "type": "contact_tag_added",
            "tag": "Stop Outreach",
            "email": email
        }
        
        success = handle_ghl_webhook(payload)
        self.assertTrue(success)
        mock_pause.assert_called_once_with("lead_stop", "GHL Tag: Stop Outreach")

if __name__ == "__main__":
    unittest.main()
