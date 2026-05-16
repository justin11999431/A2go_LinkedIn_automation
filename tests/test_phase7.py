"""Tests for Phase 7: Cohort Sequencing Engine."""

import unittest
from unittest.mock import patch, MagicMock
import os
from datetime import datetime, timedelta
from src.sequencer import Sequencer
from src.database import StateDatabase
from src.models import SequenceState

class TestPhase7(unittest.TestCase):
    
    def setUp(self):
        self.test_db = "data/test_sequencer.db"
        if os.path.exists(self.test_db):
            os.remove(self.test_db)
        self.db = StateDatabase(self.test_db)
        
    def tearDown(self):
        if os.path.exists(self.test_db):
            os.remove(self.test_db)

    @patch('src.sequencer.BrevoClient')
    @patch('src.sequencer.Settings')
    def test_sequencer_advances_step(self, mock_settings, mock_brevo_class):
        """Test that the sequencer advances a lead to the next step when due."""
        # Setup mocks
        mock_settings_inst = mock_settings.return_value
        mock_settings_inst.is_dry_run.return_value = False
        
        lead_id = "seq_test_1"
        email = "test@example.com"
        
        # Create a lead at step 0 (not started)
        state = SequenceState(
            lead_id=lead_id, 
            email=email, 
            current_email_step=0,
            next_step_due_at=datetime.now() - timedelta(minutes=1) # Due now
        )
        self.db.upsert_state(state)
        
        sequencer = Sequencer(self.test_db)
        sequencer.run_iteration()
        
        # Verify state updated to step 1
        updated_state = self.db.get_state(lead_id)
        self.assertEqual(updated_state.current_email_step, 1)
        self.assertIsNotNone(updated_state.next_step_due_at)
        self.assertTrue(updated_state.next_step_due_at > datetime.now())

    @patch('src.sequencer.BrevoClient')
    @patch('src.sequencer.Settings')
    def test_sequencer_respects_pause(self, mock_settings, mock_brevo_class):
        """Test that the sequencer ignores paused leads."""
        lead_id = "seq_test_paused"
        state = SequenceState(
            lead_id=lead_id, 
            email="paused@example.com", 
            current_email_step=1,
            is_paused=True,
            next_step_due_at=datetime.now() - timedelta(days=1)
        )
        self.db.upsert_state(state)
        
        sequencer = Sequencer(self.test_db)
        sequencer.run_iteration()
        
        # Verify state remains at step 1
        updated_state = self.db.get_state(lead_id)
        self.assertEqual(updated_state.current_email_step, 1)
        self.assertTrue(updated_state.is_paused)

if __name__ == "__main__":
    unittest.main()
