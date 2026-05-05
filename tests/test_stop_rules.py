"""Tests for stop rules."""

import pytest
from src.stop_rules import StopRule, StopRulesManager, StopRuleType


class TestStopRule:
    """Test stop rule functionality."""
    
    def test_stop_rule_creation(self):
        """Test creating a stop rule."""
        rule = StopRule(
            StopRuleType.MANUAL_STOP,
            "Test Rule",
            "Test description",
            lambda ctx: (True, "Test reason"),
        )
        
        assert rule.type == StopRuleType.MANUAL_STOP
        assert rule.name == "Test Rule"
        assert rule.description == "Test description"
        assert rule.enabled is True
        assert rule.trigger_count == 0
    
    def test_stop_rule_check_triggers(self):
        """Test stop rule that triggers."""
        rule = StopRule(
            StopRuleType.MANUAL_STOP,
            "Test Rule",
            "Test description",
            lambda ctx: (True, "Test reason"),
        )
        
        should_stop, reason = rule.check({})
        
        assert should_stop is True
        assert reason == "Test reason"
        assert rule.trigger_count == 1
        assert rule.last_triggered is not None
    
    def test_stop_rule_check_does_not_trigger(self):
        """Test stop rule that does not trigger."""
        rule = StopRule(
            StopRuleType.MANUAL_STOP,
            "Test Rule",
            "Test description",
            lambda ctx: (False, None),
        )
        
        should_stop, reason = rule.check({})
        
        assert should_stop is False
        assert reason is None
        assert rule.trigger_count == 0
        assert rule.last_triggered is None
    
    def test_stop_rule_disabled(self):
        """Test disabled stop rule."""
        rule = StopRule(
            StopRuleType.MANUAL_STOP,
            "Test Rule",
            "Test description",
            lambda ctx: (True, "Test reason"),
            enabled=False,
        )
        
        should_stop, reason = rule.check({})
        
        assert should_stop is False
        assert reason is None
        assert rule.trigger_count == 0
    
    def test_stop_rule_to_dict(self):
        """Test converting stop rule to dictionary."""
        rule = StopRule(
            StopRuleType.MANUAL_STOP,
            "Test Rule",
            "Test description",
            lambda ctx: (True, "Test reason"),
        )
        
        rule.check({})
        
        result = rule.to_dict()
        
        assert result['type'] == 'manual_stop'
        assert result['name'] == 'Test Rule'
        assert result['description'] == 'Test description'
        assert result['enabled'] is True
        assert result['trigger_count'] == 1
        assert result['last_triggered'] is not None


class TestStopRulesManager:
    """Test stop rules manager functionality."""
    
    def test_manager_initialization(self):
        """Test manager initialization with default rules."""
        manager = StopRulesManager()
        
        assert len(manager.rules) > 0
        assert manager.global_state is not None
    
    def test_add_rule(self):
        """Test adding a rule."""
        manager = StopRulesManager()
        initial_count = len(manager.rules)
        
        rule = StopRule(
            StopRuleType.MANUAL_STOP,
            "Custom Rule",
            "Custom description",
            lambda ctx: (True, "Custom reason"),
        )
        manager.add_rule(rule)
        
        assert len(manager.rules) == initial_count + 1
    
    def test_remove_rule(self):
        """Test removing a rule."""
        manager = StopRulesManager()
        initial_count = len(manager.rules)
        
        # Add a custom rule
        rule = StopRule(
            StopRuleType.MANUAL_STOP,
            "Custom Rule",
            "Custom description",
            lambda ctx: (True, "Custom reason"),
        )
        manager.add_rule(rule)
        
        # Remove the rule
        result = manager.remove_rule("Custom Rule")
        
        assert result is True
        assert len(manager.rules) == initial_count
    
    def test_remove_nonexistent_rule(self):
        """Test removing a rule that doesn't exist."""
        manager = StopRulesManager()
        
        result = manager.remove_rule("Nonexistent Rule")
        
        assert result is False
    
    def test_enable_rule(self):
        """Test enabling a rule."""
        manager = StopRulesManager()
        
        # Disable a rule first
        manager.disable_rule("Manual Stop")
        
        # Enable it
        result = manager.enable_rule("Manual Stop")
        
        assert result is True
    
    def test_disable_rule(self):
        """Test disabling a rule."""
        manager = StopRulesManager()
        
        result = manager.disable_rule("Manual Stop")
        
        assert result is True
    
    def test_check_rules_with_trigger(self):
        """Test checking rules that trigger."""
        manager = StopRulesManager()
        
        context = {'manual_stop': True}
        should_stop, reason = manager.check_rules(context)
        
        assert should_stop is True
        assert reason is not None
    
    def test_check_rules_without_trigger(self):
        """Test checking rules that don't trigger."""
        manager = StopRulesManager()
        
        context = {}
        should_stop, reason = manager.check_rules(context)
        
        assert should_stop is False
        assert reason is None
    
    def test_check_global_rules(self):
        """Test checking global rules."""
        manager = StopRulesManager()
        
        manager.update_global_state({'global_manual_stop': True})
        should_stop, reason = manager.check_global_rules()
        
        assert should_stop is True
        assert reason is not None
    
    def test_check_lead_rules(self):
        """Test checking lead-specific rules."""
        manager = StopRulesManager()
        
        lead = {'opt_out_requested': True}
        should_stop, reason = manager.check_lead_rules(lead)
        
        assert should_stop is True
        assert reason is not None
    
    def test_update_global_state(self):
        """Test updating global state."""
        manager = StopRulesManager()
        
        manager.update_global_state({'test_key': 'test_value'})
        
        assert manager.global_state['test_key'] == 'test_value'
    
    def test_increment_counter(self):
        """Test incrementing a counter."""
        manager = StopRulesManager()
        
        manager.increment_counter('test_counter', 5)
        
        assert manager.global_state['test_counter'] == 5
    
    def test_increment_counter_new(self):
        """Test incrementing a new counter."""
        manager = StopRulesManager()
        
        manager.increment_counter('new_counter')
        
        assert manager.global_state['new_counter'] == 1
    
    def test_reset_daily_counters(self):
        """Test resetting daily counters."""
        manager = StopRulesManager()
        
        manager.increment_counter('leads_processed_today', 10)
        manager.increment_counter('messages_sent_today', 20)
        manager.increment_counter('error_count', 2)
        
        manager.reset_daily_counters()
        
        assert manager.global_state['leads_processed_today'] == 0
        assert manager.global_state['messages_sent_today'] == 0
        assert manager.global_state['error_count'] == 0
    
    def test_get_rules_summary(self):
        """Test getting rules summary."""
        manager = StopRulesManager()
        
        summary = manager.get_rules_summary()
        
        assert 'total_rules' in summary
        assert 'enabled_rules' in summary
        assert 'disabled_rules' in summary
        assert 'rules' in summary
        assert 'global_state' in summary
        assert summary['total_rules'] > 0
    
    def test_get_triggered_rules(self):
        """Test getting triggered rules."""
        manager = StopRulesManager()
        
        # Trigger a rule
        manager.check_rules({'manual_stop': True})
        
        triggered = manager.get_triggered_rules()
        
        assert len(triggered) > 0
        assert any(rule['trigger_count'] > 0 for rule in triggered)
