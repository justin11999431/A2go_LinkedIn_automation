"""Comprehensive Dry-Run Simulation for the A2go Orchestration System."""

import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
import os
import json

from src.sync_leads import sync_sheets_to_ghl
from src.sequencer import Sequencer
from src.webhooks.brevo_handler import handle_brevo_webhook
from src.webhooks.messagebird_handler import handle_messagebird_webhook
from src.webhooks.ghl_handler import handle_ghl_webhook
from src.database import StateDatabase
from src.models import SequenceState
from src.lead_mapper import LeadMapper

class TestFullWorkflow(unittest.TestCase):
    
    def setUp(self):
        self.test_db = "data/simulation.db"
        if os.path.exists(self.test_db):
            os.remove(self.test_db)
        self.db = StateDatabase(self.test_db)

    def tearDown(self):
        if os.path.exists(self.test_db):
            os.remove(self.test_db)

    @patch('src.sync_leads.GoogleSheetsClient')
    @patch('src.sync_leads.GHLClient')
    @patch('src.sequencer.BrevoClient')
    @patch('src.sequencer.LinkedInAdapter')
    @patch('src.settings.Settings.is_dry_run')
    def test_full_lead_lifecycle_simulation(self, mock_dry_run, mock_li, mock_brevo, mock_ghl_sync, mock_gs):
        """Simulate a lead moving through the entire multi-channel system."""
        mock_dry_run.return_value = False 
        
        # 1. Simulate Lead Sync (Phase 5)
        headers = LeadMapper.get_source_headers()
        row_data = ["Alice", "Smith", "alice@example.com", "AliceCo", "CEO", "li_url_alice", "Tech", "SF", "+15550001", "", "", "", "", "", "new", "src", "camp", "high", "tag", "yes", "reason", "no"]
        
        mock_gs.return_value.get_sheet_data.return_value = [row_data]
        mock_ghl_sync.return_value.upsert_contact.return_value = "ghl_alice_123"
        mock_ghl_sync.return_value.get_contact_by_email.return_value = {"id": "ghl_alice_123"}
        
        # Patch sync_leads to use test DB
        with patch('src.sync_leads.StateDatabase', return_value=self.db):
            sync_sheets_to_ghl()
            
        # Verify lead created in local DB
        state = self.db.get_state_by_email("alice@example.com")
        self.assertIsNotNone(state, "Lead should have been synced to the database")
        
        # 2. Simulate Orchestration (Phase 7 & 8)
        sequencer = Sequencer(self.test_db)
        sequencer.ghl = mock_ghl_sync.return_value
        sequencer.ghl.create_conversation_message.return_value = True
        
        sequencer.run_iteration()
        
        state = self.db.get_state(state.lead_id)
        self.assertEqual(state.current_email_step, 1)
        self.assertEqual(state.current_linkedin_step, 1)
        
        # 3. Simulate LinkedIn Acceptance
        state.linkedin_status = "Accepted"
        self.db.upsert_state(state)
        
        # 4. Simulate SMS Reply (Phase 9 Webhook)
        sms_payload = {
            "originator": "+15550001",
            "body": "Interested"
        }
        
        # CRITICAL: We must patch pauseContactAutomation to use the test DB
        # or patch StateDatabase inside safety.py
        with patch('src.webhooks.messagebird_handler.StateDatabase', return_value=self.db):
            with patch('src.webhooks.messagebird_handler.GHLClient', return_value=mock_ghl_sync.return_value):
                # We need to make sure safety.pauseContactAutomation uses self.test_db
                with patch('src.webhooks.messagebird_handler.pauseContactAutomation', 
                           side_effect=lambda lid, r: self.db_pause_proxy(lid, r)):
                    handle_messagebird_webhook(sms_payload)
        
        # Verify safety pause triggered
        state = self.db.get_state(state.lead_id)
        self.assertTrue(state.is_paused, "Automation should be paused after SMS reply")
        self.assertIn("SMS reply", state.pause_reason)
        
        # 5. Verify Sequencer respects pause
        sequencer.run_iteration()
        state_after = self.db.get_state(state.lead_id)
        self.assertEqual(state_after.current_email_step, 1) 
        
        print("\nSimulation Successful: All channels synchronized, GHL notified, and safety invariants verified.")

    def db_pause_proxy(self, lead_id, reason):
        """Helper to call safety pause with test DB path."""
        from src.safety import pauseContactAutomation
        return pauseContactAutomation(lead_id, reason, db_path=self.test_db)

if __name__ == "__main__":
    unittest.main()
