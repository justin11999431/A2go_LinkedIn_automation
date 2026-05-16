"""Tests for Phase 3: pauseContactAutomation."""

import unittest
import os
from src.safety import pauseContactAutomation, is_automation_paused
from src.database import StateDatabase
from src.models import SequenceState

class TestPhase3(unittest.TestCase):
    
    def setUp(self):
        self.test_db = "data/test_safety.db"
        # Ensure clean state
        if os.path.exists(self.test_db):
            os.remove(self.test_db)
            
    def tearDown(self):
        if os.path.exists(self.test_db):
            os.remove(self.test_db)
            
    def test_pause_contact_automation(self):
        """Test the unified pause function."""
        lead_id = "safety_test_1"
        reason = "Test reply"
        
        # Initial check
        self.assertFalse(is_automation_paused(lead_id, self.test_db))
        
        # Execute pause
        success = pauseContactAutomation(lead_id, reason, self.test_db)
        self.assertTrue(success)
        
        # Verify state
        self.assertTrue(is_automation_paused(lead_id, self.test_db))
        
        db = StateDatabase(self.test_db)
        state = db.get_state(lead_id)
        self.assertEqual(state.pause_reason, reason)
        self.assertTrue(state.is_paused)

    def test_pause_existing_contact(self):
        """Test pausing a contact that already has state."""
        lead_id = "safety_test_2"
        db = StateDatabase(self.test_db)
        db.upsert_state(SequenceState(lead_id=lead_id, current_email_step=3))
        
        pauseContactAutomation(lead_id, "User opt-out", self.test_db)
        
        state = db.get_state(lead_id)
        self.assertEqual(state.current_email_step, 3)
        self.assertTrue(state.is_paused)

if __name__ == "__main__":
    unittest.main()
