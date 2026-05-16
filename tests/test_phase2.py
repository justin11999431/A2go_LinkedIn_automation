"""Tests for Phase 2: Database Schema and Sequence State."""

import unittest
import os
from datetime import datetime, timedelta
from src.models import Lead, SequenceState
from src.database import StateDatabase

class TestPhase2(unittest.TestCase):
    
    def setUp(self):
        self.test_db = "data/test_automation.db"
        self.db = StateDatabase(self.test_db)
        
    def tearDown(self):
        if os.path.exists(self.test_db):
            os.remove(self.test_db)
            
    def test_lead_model(self):
        """Test Lead model validation."""
        lead = Lead(
            lead_id="test_id",
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            company="TestCorp"
        )
        self.assertEqual(lead.lead_id, "test_id")
        self.assertEqual(lead.status, "new")
        
    def test_sequence_state_persistence(self):
        """Test saving and retrieving sequence state."""
        lead_id = "test_lead_123"
        state = SequenceState(
            lead_id=lead_id,
            current_email_step=1,
            email_status="sent",
            next_step_due_at=datetime.now() + timedelta(days=2)
        )
        
        self.db.upsert_state(state)
        
        retrieved = self.db.get_state(lead_id)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.current_email_step, 1)
        self.assertEqual(retrieved.email_status, "sent")
        self.assertFalse(retrieved.is_paused)
        
    def test_pause_state_update(self):
        """Test updating pause state."""
        lead_id = "test_lead_456"
        state = SequenceState(lead_id=lead_id)
        self.db.upsert_state(state)
        
        # Update to paused
        state.is_paused = True
        state.pause_reason = "Replied"
        self.db.upsert_state(state)
        
        retrieved = self.db.get_state(lead_id)
        self.assertTrue(retrieved.is_paused)
        self.assertEqual(retrieved.pause_reason, "Replied")

if __name__ == "__main__":
    unittest.main()
