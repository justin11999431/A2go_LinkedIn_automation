"""Stop rules for automation system."""

import logging
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)


class StopRuleType(Enum):
    """Types of stop rules."""
    
    # Manual stops
    MANUAL_STOP = "manual_stop"
    GLOBAL_MANUAL_STOP = "global_manual_stop"
    
    # Rate-based stops
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    MAX_LEADS_PER_DAY_REACHED = "max_leads_per_day_reached"
    MAX_MESSAGES_PER_DAY_REACHED = "max_messages_per_day_reached"
    
    # Salesrobot action limits
    MAX_CONNECTION_REQUESTS_REACHED = "max_connection_requests_reached"
    MAX_FOLLOW_UP_MESSAGES_REACHED = "max_follow_up_messages_reached"
    MAX_VOICE_MESSAGES_REACHED = "max_voice_messages_reached"
    MAX_VIDEO_MESSAGES_REACHED = "max_video_messages_reached"
    MAX_PROFILE_VIEWS_REACHED = "max_profile_views_reached"
    MAX_INMAIL_MESSAGES_REACHED = "max_inmail_messages_reached"
    MAX_PROFILE_FOLLOWS_REACHED = "max_profile_follows_reached"
    MAX_POST_LIKES_COMMENTS_REACHED = "max_post_likes_comments_reached"
    MAX_ENDORSEMENTS_REACHED = "max_endorsements_reached"
    MAX_WITHDRAW_CONNECTION_REQUESTS_REACHED = "max_withdraw_connection_requests_reached"
    MAX_INVITE_TO_EVENT_REACHED = "max_invite_to_event_reached"
    
    # Error-based stops
    ERROR_THRESHOLD_EXCEEDED = "error_threshold_exceeded"
    CRITICAL_ERROR = "critical_error"
    
    # Time-based stops
    MAINTENANCE_WINDOW = "maintenance_window"
    BUSINESS_HOURS_ONLY = "business_hours_only"
    
    # Lead-specific stops
    LEAD_OPT_OUT = "lead_opt_out"
    LEAD_BLOCKED = "lead_blocked"
    LEAD_NEGATIVE_FEEDBACK = "lead_negative_feedback"
    LEAD_HIGH_COMPLAINT_RISK = "lead_high_complaint_risk"


class StopRule:
    """Represents a stop rule."""
    
    def __init__(self, rule_type: StopRuleType, name: str, description: str,
                 check_function: Callable, enabled: bool = True):
        """Initialize stop rule.
        
        Args:
            rule_type: Type of stop rule
            name: Rule name
            description: Rule description
            check_function: Function to check if rule should trigger
            enabled: Whether rule is enabled
        """
        self.type = rule_type
        self.name = name
        self.description = description
        self.check_function = check_function
        self.enabled = enabled
        self.trigger_count = 0
        self.last_triggered = None
    
    def check(self, context: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Check if stop rule should trigger.
        
        Args:
            context: Context data for checking
            
        Returns:
            Tuple of (should_stop, reason)
        """
        if not self.enabled:
            return False, None
        
        should_stop, reason = self.check_function(context)
        
        if should_stop:
            self.trigger_count += 1
            self.last_triggered = datetime.now().isoformat()
            logger.warning(f"Stop rule triggered: {self.name} - {reason}")
        
        return should_stop, reason
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert stop rule to dictionary.
        
        Returns:
            Dictionary representation
        """
        return {
            'type': self.type.value,
            'name': self.name,
            'description': self.description,
            'enabled': self.enabled,
            'trigger_count': self.trigger_count,
            'last_triggered': self.last_triggered,
        }


class StopRulesManager:
    """Manages stop rules for automation system."""
    
    def __init__(self):
        """Initialize stop rules manager."""
        self.rules: List[StopRule] = []
        self.global_state = {
            'leads_processed_today': 0,
            'messages_sent_today': 0,
            'error_count': 0,
            'last_reset': datetime.now().isoformat(),
            # Salesrobot action counters
            'connection_requests_today': 0,
            'follow_up_messages_today': 0,
            'voice_messages_today': 0,
            'video_messages_today': 0,
            'profile_views_today': 0,
            'inmail_messages_today': 0,
            'profile_follows_today': 0,
            'post_likes_comments_today': 0,
            'endorsements_today': 0,
            'withdraw_connection_requests_today': 0,
            'invite_to_event_today': 0,
        }
        self._initialize_default_rules()
    
    def _initialize_default_rules(self) -> None:
        """Initialize default stop rules."""
        # Manual stop rules
        self.add_rule(StopRule(
            StopRuleType.MANUAL_STOP,
            "Manual Stop",
            "Manual stop requested for specific lead",
            lambda ctx: (ctx.get('manual_stop', False), "Manual stop requested"),
        ))
        
        self.add_rule(StopRule(
            StopRuleType.GLOBAL_MANUAL_STOP,
            "Global Manual Stop",
            "Global manual stop requested",
            lambda ctx: (ctx.get('global_manual_stop', False), "Global manual stop requested"),
        ))
        
        # Rate limit rules
        self.add_rule(StopRule(
            StopRuleType.RATE_LIMIT_EXCEEDED,
            "Rate Limit Exceeded",
            "API rate limit has been exceeded",
            lambda ctx: (ctx.get('rate_limit_exceeded', False), "Rate limit exceeded"),
        ))
        
        self.add_rule(StopRule(
            StopRuleType.MAX_LEADS_PER_DAY_REACHED,
            "Max Leads Per Day",
            "Maximum leads per day limit reached",
            lambda ctx: (
                ctx.get('leads_processed_today', 0) >= ctx.get('max_leads_per_day', 100),
                f"Max leads per day reached: {ctx.get('leads_processed_today', 0)}/{ctx.get('max_leads_per_day', 100)}"
            ),
        ))
        
        self.add_rule(StopRule(
            StopRuleType.MAX_MESSAGES_PER_DAY_REACHED,
            "Max Messages Per Day",
            "Maximum messages per day limit reached",
            lambda ctx: (
                ctx.get('messages_sent_today', 0) >= ctx.get('max_messages_per_day', 200),
                f"Max messages per day reached: {ctx.get('messages_sent_today', 0)}/{ctx.get('max_messages_per_day', 200)}"
            ),
        ))
        
        # Salesrobot action limit rules
        self.add_rule(StopRule(
            StopRuleType.MAX_CONNECTION_REQUESTS_REACHED,
            "Max Connection Requests",
            "Maximum connection requests per day limit reached",
            lambda ctx: (
                ctx.get('connection_requests_today', 0) >= ctx.get('max_connection_requests_per_day', 20),
                f"Max connection requests reached: {ctx.get('connection_requests_today', 0)}/{ctx.get('max_connection_requests_per_day', 20)}"
            ),
        ))
        
        self.add_rule(StopRule(
            StopRuleType.MAX_FOLLOW_UP_MESSAGES_REACHED,
            "Max Follow-Up Messages",
            "Maximum follow-up messages per day limit reached",
            lambda ctx: (
                ctx.get('follow_up_messages_today', 0) >= ctx.get('max_follow_up_messages_per_day', 20),
                f"Max follow-up messages reached: {ctx.get('follow_up_messages_today', 0)}/{ctx.get('max_follow_up_messages_per_day', 20)}"
            ),
        ))
        
        self.add_rule(StopRule(
            StopRuleType.MAX_VOICE_MESSAGES_REACHED,
            "Max Voice Messages",
            "Maximum voice messages per day limit reached",
            lambda ctx: (
                ctx.get('voice_messages_today', 0) >= ctx.get('max_voice_messages_per_day', 20),
                f"Max voice messages reached: {ctx.get('voice_messages_today', 0)}/{ctx.get('max_voice_messages_per_day', 20)}"
            ),
        ))
        
        self.add_rule(StopRule(
            StopRuleType.MAX_VIDEO_MESSAGES_REACHED,
            "Max Video Messages",
            "Maximum video messages per day limit reached",
            lambda ctx: (
                ctx.get('video_messages_today', 0) >= ctx.get('max_video_messages_per_day', 20),
                f"Max video messages reached: {ctx.get('video_messages_today', 0)}/{ctx.get('max_video_messages_per_day', 20)}"
            ),
        ))
        
        self.add_rule(StopRule(
            StopRuleType.MAX_PROFILE_VIEWS_REACHED,
            "Max Profile Views",
            "Maximum profile views per day limit reached",
            lambda ctx: (
                ctx.get('profile_views_today', 0) >= ctx.get('max_profile_views_per_day', 20),
                f"Max profile views reached: {ctx.get('profile_views_today', 0)}/{ctx.get('max_profile_views_per_day', 20)}"
            ),
        ))
        
        self.add_rule(StopRule(
            StopRuleType.MAX_INMAIL_MESSAGES_REACHED,
            "Max InMail Messages",
            "Maximum InMail messages per day limit reached",
            lambda ctx: (
                ctx.get('inmail_messages_today', 0) >= ctx.get('max_inmail_messages_per_day', 20),
                f"Max InMail messages reached: {ctx.get('inmail_messages_today', 0)}/{ctx.get('max_inmail_messages_per_day', 20)}"
            ),
        ))
        
        self.add_rule(StopRule(
            StopRuleType.MAX_PROFILE_FOLLOWS_REACHED,
            "Max Profile Follows",
            "Maximum profile follows per day limit reached",
            lambda ctx: (
                ctx.get('profile_follows_today', 0) >= ctx.get('max_profile_follows_per_day', 20),
                f"Max profile follows reached: {ctx.get('profile_follows_today', 0)}/{ctx.get('max_profile_follows_per_day', 20)}"
            ),
        ))
        
        self.add_rule(StopRule(
            StopRuleType.MAX_POST_LIKES_COMMENTS_REACHED,
            "Max Post Likes & Comments",
            "Maximum post likes & comments per day limit reached",
            lambda ctx: (
                ctx.get('post_likes_comments_today', 0) >= ctx.get('max_post_likes_comments_per_day', 20),
                f"Max post likes & comments reached: {ctx.get('post_likes_comments_today', 0)}/{ctx.get('max_post_likes_comments_per_day', 20)}"
            ),
        ))
        
        self.add_rule(StopRule(
            StopRuleType.MAX_ENDORSEMENTS_REACHED,
            "Max Endorsements",
            "Maximum endorsements per day limit reached",
            lambda ctx: (
                ctx.get('endorsements_today', 0) >= ctx.get('max_endorsements_per_day', 20),
                f"Max endorsements reached: {ctx.get('endorsements_today', 0)}/{ctx.get('max_endorsements_per_day', 20)}"
            ),
        ))
        
        self.add_rule(StopRule(
            StopRuleType.MAX_WITHDRAW_CONNECTION_REQUESTS_REACHED,
            "Max Withdraw Connection Requests",
            "Maximum withdraw connection requests per day limit reached",
            lambda ctx: (
                ctx.get('withdraw_connection_requests_today', 0) >= ctx.get('max_withdraw_connection_requests_per_day', 10),
                f"Max withdraw connection requests reached: {ctx.get('withdraw_connection_requests_today', 0)}/{ctx.get('max_withdraw_connection_requests_per_day', 10)}"
            ),
        ))
        
        self.add_rule(StopRule(
            StopRuleType.MAX_INVITE_TO_EVENT_REACHED,
            "Max Invite to Event",
            "Maximum invite to event per day limit reached",
            lambda ctx: (
                ctx.get('invite_to_event_today', 0) >= ctx.get('max_invite_to_event_per_day', 30),
                f"Max invite to event reached: {ctx.get('invite_to_event_today', 0)}/{ctx.get('max_invite_to_event_per_day', 30)}"
            ),
        ))
        
        # Error-based rules
        self.add_rule(StopRule(
            StopRuleType.ERROR_THRESHOLD_EXCEEDED,
            "Error Threshold Exceeded",
            "Error threshold has been exceeded",
            lambda ctx: (
                ctx.get('error_count', 0) >= ctx.get('max_errors', 5),
                f"Error threshold exceeded: {ctx.get('error_count', 0)}/{ctx.get('max_errors', 5)}"
            ),
        ))
        
        self.add_rule(StopRule(
            StopRuleType.CRITICAL_ERROR,
            "Critical Error",
            "Critical error occurred",
            lambda ctx: (ctx.get('critical_error', False), "Critical error occurred"),
        ))
        
        # Lead-specific rules
        self.add_rule(StopRule(
            StopRuleType.LEAD_OPT_OUT,
            "Lead Opt Out",
            "Lead has opted out",
            lambda ctx: (ctx.get('opt_out_requested', False), "Lead opted out"),
        ))
        
        self.add_rule(StopRule(
            StopRuleType.LEAD_BLOCKED,
            "Lead Blocked",
            "Lead has been blocked",
            lambda ctx: (ctx.get('blocked', False), "Lead blocked"),
        ))
        
        self.add_rule(StopRule(
            StopRuleType.LEAD_NEGATIVE_FEEDBACK,
            "Lead Negative Feedback",
            "Lead has provided negative feedback",
            lambda ctx: (ctx.get('negative_feedback', False), "Lead negative feedback"),
        ))
        
        self.add_rule(StopRule(
            StopRuleType.LEAD_HIGH_COMPLAINT_RISK,
            "Lead High Complaint Risk",
            "Lead has high complaint risk",
            lambda ctx: (ctx.get('complaint_risk', 0) > 0.7, f"High complaint risk: {ctx.get('complaint_risk', 0)}"),
        ))
    
    def add_rule(self, rule: StopRule) -> None:
        """Add a stop rule.
        
        Args:
            rule: Stop rule to add
        """
        self.rules.append(rule)
        logger.info(f"Added stop rule: {rule.name}")
    
    def remove_rule(self, rule_name: str) -> bool:
        """Remove a stop rule.
        
        Args:
            rule_name: Name of rule to remove
            
        Returns:
            True if rule was removed
        """
        for i, rule in enumerate(self.rules):
            if rule.name == rule_name:
                self.rules.pop(i)
                logger.info(f"Removed stop rule: {rule_name}")
                return True
        return False
    
    def enable_rule(self, rule_name: str) -> bool:
        """Enable a stop rule.
        
        Args:
            rule_name: Name of rule to enable
            
        Returns:
            True if rule was enabled
        """
        for rule in self.rules:
            if rule.name == rule_name:
                rule.enabled = True
                logger.info(f"Enabled stop rule: {rule_name}")
                return True
        return False
    
    def disable_rule(self, rule_name: str) -> bool:
        """Disable a stop rule.
        
        Args:
            rule_name: Name of rule to disable
            
        Returns:
            True if rule was disabled
        """
        for rule in self.rules:
            if rule.name == rule_name:
                rule.enabled = False
                logger.info(f"Disabled stop rule: {rule_name}")
                return True
        return False
    
    def check_rules(self, context: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Check all stop rules.
        
        Args:
            context: Context data for checking
            
        Returns:
            Tuple of (should_stop, reason)
        """
        for rule in self.rules:
            should_stop, reason = rule.check(context)
            if should_stop:
                return True, f"{rule.name}: {reason}"
        
        return False, None
    
    def check_global_rules(self) -> tuple[bool, Optional[str]]:
        """Check global stop rules.
        
        Returns:
            Tuple of (should_stop, reason)
        """
        return self.check_rules(self.global_state)
    
    def check_lead_rules(self, lead: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Check lead-specific stop rules.
        
        Args:
            lead: Lead data
            
        Returns:
            Tuple of (should_stop, reason)
        """
        return self.check_rules(lead)
    
    def update_global_state(self, updates: Dict[str, Any]) -> None:
        """Update global state.
        
        Args:
            updates: State updates
        """
        self.global_state.update(updates)
        logger.debug(f"Updated global state: {updates}")
    
    def increment_counter(self, counter_name: str, value: int = 1) -> None:
        """Increment a global counter.
        
        Args:
            counter_name: Name of counter
            value: Value to increment by
        """
        if counter_name not in self.global_state:
            self.global_state[counter_name] = 0
        self.global_state[counter_name] += value
        logger.debug(f"Incremented {counter_name} to {self.global_state[counter_name]}")
    
    def reset_daily_counters(self) -> None:
        """Reset daily counters."""
        self.global_state['leads_processed_today'] = 0
        self.global_state['messages_sent_today'] = 0
        self.global_state['error_count'] = 0
        # Reset Salesrobot action counters
        self.global_state['connection_requests_today'] = 0
        self.global_state['follow_up_messages_today'] = 0
        self.global_state['voice_messages_today'] = 0
        self.global_state['video_messages_today'] = 0
        self.global_state['profile_views_today'] = 0
        self.global_state['inmail_messages_today'] = 0
        self.global_state['profile_follows_today'] = 0
        self.global_state['post_likes_comments_today'] = 0
        self.global_state['endorsements_today'] = 0
        self.global_state['withdraw_connection_requests_today'] = 0
        self.global_state['invite_to_event_today'] = 0
        self.global_state['last_reset'] = datetime.now().isoformat()
        logger.info("Reset daily counters")
    
    def get_rules_summary(self) -> Dict[str, Any]:
        """Get summary of all rules.
        
        Returns:
            Rules summary
        """
        return {
            'total_rules': len(self.rules),
            'enabled_rules': sum(1 for r in self.rules if r.enabled),
            'disabled_rules': sum(1 for r in self.rules if not r.enabled),
            'rules': [r.to_dict() for r in self.rules],
            'global_state': self.global_state,
        }
    
    def get_triggered_rules(self) -> List[Dict[str, Any]]:
        """Get rules that have been triggered.
        
        Returns:
            List of triggered rules
        """
        return [r.to_dict() for r in self.rules if r.trigger_count > 0]
