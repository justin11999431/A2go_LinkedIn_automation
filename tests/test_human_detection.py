"""Tests for human detection logic."""

import pytest
from src.human_stop_logic import HumanStopLogic


class TestHumanStopLogic:
    """Test human stop logic detection."""
    
    def test_detect_human_intervention_with_human_fields(self):
        """Test detection when human fields are present."""
        lead = {
            'human_notes': 'Called lead, interested',
            'first_name': 'John',
            'last_name': 'Doe',
        }
        
        result = HumanStopLogic.detect_human_intervention(lead)
        assert result is True
    
    def test_detect_human_intervention_without_human_fields(self):
        """Test detection when no human fields are present."""
        lead = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
        }
        
        result = HumanStopLogic.detect_human_intervention(lead)
        assert result is False
    
    def test_detect_human_intervention_with_manual_stop(self):
        """Test detection with manual stop flag."""
        lead = {
            'manual_stop': True,
            'first_name': 'John',
        }
        
        result = HumanStopLogic.detect_human_intervention(lead)
        assert result is True
    
    def test_should_stop_with_manual_stop(self):
        """Test should stop with manual stop."""
        lead = {'manual_stop': True}
        
        should_stop, reason = HumanStopLogic.should_stop_automation(lead)
        assert should_stop is True
        assert 'manual stop' in reason.lower()
    
    def test_should_stop_with_opt_out(self):
        """Test should stop with opt-out requested."""
        lead = {'opt_out_requested': True}
        
        should_stop, reason = HumanStopLogic.should_stop_automation(lead)
        assert should_stop is True
        assert 'opt-out' in reason.lower()
    
    def test_should_stop_with_negative_feedback(self):
        """Test should stop with negative feedback."""
        lead = {'negative_feedback': True}
        
        should_stop, reason = HumanStopLogic.should_stop_automation(lead)
        assert should_stop is True
        assert 'negative feedback' in reason.lower()
    
    def test_should_stop_with_high_complaint_risk(self):
        """Test should stop with high complaint risk."""
        lead = {'complaint_risk': 0.8}
        
        should_stop, reason = HumanStopLogic.should_stop_automation(lead)
        assert should_stop is True
        assert 'complaint risk' in reason.lower()
    
    def test_should_not_stop_with_low_complaint_risk(self):
        """Test should not stop with low complaint risk."""
        lead = {'complaint_risk': 0.5}
        
        should_stop, reason = HumanStopLogic.should_stop_automation(lead)
        assert should_stop is False
        assert reason is None
    
    def test_preserve_human_fields(self):
        """Test preservation of human fields."""
        source_lead = {
            'first_name': 'John',
            'last_name': 'Doe',
            'status': 'new',
        }
        
        target_lead = {
            'first_name': 'John',
            'last_name': 'Doe',
            'status': 'new',
            'human_notes': 'Called lead',
            'human_status': 'interested',
            'human_priority': 'high',
        }
        
        result = HumanStopLogic.preserve_human_fields(source_lead, target_lead)
        
        assert result['human_notes'] == 'Called lead'
        assert result['human_status'] == 'interested'
        assert result['human_priority'] == 'high'
        assert 'last_human_update' in result
    
    def test_check_global_stop_conditions_with_manual_stop(self):
        """Test global stop with manual stop."""
        global_state = {'global_manual_stop': True}
        
        should_stop, reason = HumanStopLogic.check_global_stop_conditions(global_state)
        assert should_stop is True
        assert 'manual stop' in reason.lower()
    
    def test_check_global_stop_conditions_with_rate_limit(self):
        """Test global stop with rate limit exceeded."""
        global_state = {'rate_limit_exceeded': True}
        
        should_stop, reason = HumanStopLogic.check_global_stop_conditions(global_state)
        assert should_stop is True
        assert 'rate limit' in reason.lower()
    
    def test_check_global_stop_conditions_with_api_errors(self):
        """Test global stop with too many API errors."""
        global_state = {'api_error_count': 6}
        
        should_stop, reason = HumanStopLogic.check_global_stop_conditions(global_state)
        assert should_stop is True
        assert 'api error' in reason.lower()
    
    def test_check_global_stop_conditions_no_stop(self):
        """Test global stop with no stop conditions."""
        global_state = {
            'global_manual_stop': False,
            'rate_limit_exceeded': False,
            'api_error_count': 2,
            'maintenance_mode': False,
        }
        
        should_stop, reason = HumanStopLogic.check_global_stop_conditions(global_state)
        assert should_stop is False
        assert reason is None
    
    def test_get_stop_summary(self):
        """Test stop summary generation."""
        leads = [
            {'manual_stop': True, 'first_name': 'John'},
            {'opt_out_requested': True, 'first_name': 'Jane'},
            {'first_name': 'Bob'},
        ]
        
        summary = HumanStopLogic.get_stop_summary(leads)
        
        assert summary['total_leads'] == 3
        assert summary['stopped_leads'] == 2
        assert summary['active_leads'] == 1
        assert len(summary['stop_reasons']) == 2
