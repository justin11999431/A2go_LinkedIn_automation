"""Human stop logic for detecting human intervention and stop conditions."""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class HumanStopLogic:
    """Detects human intervention and enforces stop conditions."""
    
    # Human-entered fields that should be preserved
    HUMAN_FIELDS = [
        'human_notes',
        'human_status',
        'human_priority',
        'human_tags',
        'last_human_update',
        'human_override',
    ]
    
    # Stop conditions
    STOP_CONDITIONS = {
        'manual_stop': 'Manual stop requested by human',
        'high_complaint_risk': 'High complaint risk detected',
        'negative_feedback': 'Negative feedback received',
        'opt_out_requested': 'Opt-out requested',
        'account_issue': 'Account issue detected',
        'rate_limit_exceeded': 'Rate limit exceeded',
        'api_error': 'API error occurred',
    }
    
    @staticmethod
    def detect_human_intervention(lead: Dict[str, Any]) -> bool:
        """Detect if human has intervened with a lead.
        
        Args:
            lead: Lead data
            
        Returns:
            True if human intervention detected
        """
        # Check for human-entered fields
        for field in HumanStopLogic.HUMAN_FIELDS:
            if field in lead and lead[field]:
                return True
        
        # Check for manual stop flag
        if lead.get('manual_stop', False):
            return True
        
        return False
    
    @staticmethod
    def should_stop_automation(lead: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Determine if automation should stop for this lead.
        
        Args:
            lead: Lead data
            
        Returns:
            Tuple of (should_stop, reason)
        """
        # Check for manual stop
        if lead.get('manual_stop', False):
            return True, HumanStopLogic.STOP_CONDITIONS['manual_stop']
        
        # Check for opt-out
        if lead.get('opt_out_requested', False):
            return True, HumanStopLogic.STOP_CONDITIONS['opt_out_requested']
        
        # Check for negative feedback
        if lead.get('negative_feedback', False):
            return True, HumanStopLogic.STOP_CONDITIONS['negative_feedback']
        
        # Check for high complaint risk
        if lead.get('complaint_risk', 0) > 0.7:
            return True, HumanStopLogic.STOP_CONDITIONS['high_complaint_risk']
        
        # Check for account issues
        if lead.get('account_issue', False):
            return True, HumanStopLogic.STOP_CONDITIONS['account_issue']
        
        return False, None
    
    @staticmethod
    def preserve_human_fields(source_lead: Dict[str, Any], target_lead: Dict[str, Any]) -> Dict[str, Any]:
        """Preserve human-entered fields when updating lead data.
        
        Args:
            source_lead: Source lead data (from automation)
            target_lead: Target lead data (existing with human fields)
            
        Returns:
            Updated lead with human fields preserved
        """
        updated_lead = source_lead.copy()
        
        # Preserve human-entered fields
        for field in HumanStopLogic.HUMAN_FIELDS:
            if field in target_lead and target_lead[field]:
                updated_lead[field] = target_lead[field]
        
        # Update last human update timestamp if human fields exist
        if any(field in target_lead and target_lead[field] for field in HumanStopLogic.HUMAN_FIELDS):
            updated_lead['last_human_update'] = datetime.now().isoformat()
        
        return updated_lead
    
    @staticmethod
    def check_global_stop_conditions(global_state: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Check global stop conditions that affect all leads.
        
        Args:
            global_state: Global automation state
            
        Returns:
            Tuple of (should_stop, reason)
        """
        # Check for global manual stop
        if global_state.get('global_manual_stop', False):
            return True, "Global manual stop requested"
        
        # Check for rate limit
        if global_state.get('rate_limit_exceeded', False):
            return True, HumanStopLogic.STOP_CONDITIONS['rate_limit_exceeded']
        
        # Check for API errors
        if global_state.get('api_error_count', 0) > 5:
            return True, HumanStopLogic.STOP_CONDITIONS['api_error']
        
        # Check for maintenance mode
        if global_state.get('maintenance_mode', False):
            return True, "System in maintenance mode"
        
        return False, None
    
    @staticmethod
    def get_stop_summary(leads: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get summary of stopped leads and reasons.
        
        Args:
            leads: List of leads
            
        Returns:
            Stop summary with counts and reasons
        """
        stopped_leads = []
        stop_reasons = {}
        
        for lead in leads:
            should_stop, reason = HumanStopLogic.should_stop_automation(lead)
            if should_stop:
                stopped_leads.append(lead)
                stop_reasons[reason] = stop_reasons.get(reason, 0) + 1
        
        return {
            'total_leads': len(leads),
            'stopped_leads': len(stopped_leads),
            'active_leads': len(leads) - len(stopped_leads),
            'stop_reasons': stop_reasons,
            'stopped_leads': stopped_leads,
        }
