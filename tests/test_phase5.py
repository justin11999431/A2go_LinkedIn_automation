"""Tests for Phase 5: Sheets to GHL Sync Logic."""

import unittest
from unittest.mock import patch, MagicMock
from src.sync_leads import sync_sheets_to_ghl

class TestPhase5(unittest.TestCase):
    
    @patch('src.sync_leads.Settings')
    @patch('src.sync_leads.GoogleSheetsClient')
    @patch('src.sync_leads.GHLClient')
    @patch('src.sync_leads.StateDatabase')
    def test_sync_logic_flow(self, mock_db, mock_ghl, mock_gs, mock_settings):
        """Test the end-to-end sync logic with mocks."""
        # Setup mocks
        mock_settings_inst = mock_settings.return_value
        mock_settings_inst.is_dry_run.return_value = False
        mock_settings_inst.get_source_sheet_id.return_value = "sheet_123"
        
        mock_gs_inst = mock_gs.return_value
        mock_gs_inst.get_sheet_data.return_value = [
            ["John", "Doe", "john@example.com", "TestCo", "CEO", "link1", "IT", "NY", "123", "123", "123", "123", "addr", "note", "new", "src", "camp", "high", "tag", "yes", "reason", "no"]
        ]
        
        mock_ghl_inst = mock_ghl.return_value
        mock_ghl_inst.upsert_contact.return_value = "ghl_id_456"
        
        mock_db_inst = mock_db.return_value
        mock_db_inst.get_state.return_value = None
        
        # Execute
        sync_sheets_to_ghl()
        
        # Verify
        self.assertTrue(mock_ghl_inst.upsert_contact.called)
        self.assertTrue(mock_db_inst.upsert_state.called)

if __name__ == "__main__":
    unittest.main()
