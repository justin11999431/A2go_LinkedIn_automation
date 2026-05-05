"""Status taxonomy for canonical lead status definitions."""

from enum import Enum
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class LeadStatus(Enum):
    """Canonical lead status taxonomy."""
    
    # Initial states
    NEW = "new"
    IMPORTED = "imported"
    
    # Processing states
    ENQUEUED = "enqueued"
    PROCESSING = "processing"
    
    # Outreach states
    CONNECTION_REQUESTED = "connection_requested"
    CONNECTED = "connected"
    FIRST_MESSAGE_SENT = "first_message_sent"
    FOLLOW_UP_SENT = "follow_up_sent"
    
    # Engagement states
    VIEWED = "viewed"
    REPLIED = "replied"
    CONVERSATION_STARTED = "conversation_started"
    
    # Positive outcomes
    INTERESTED = "interested"
    MEETING_SCHEDULED = "meeting_scheduled"
    DEMO_REQUESTED = "demo_requested"
    PROPOSAL_SENT = "proposal_sent"
    NEGOTIATION = "negotiation"
    
    # Negative outcomes
    NOT_INTERESTED = "not_interested"
    DECLINED = "declined"
    GHOSTED = "ghosted"
    
    # Stop states
    OPTED_OUT = "opted_out"
    BLOCKED = "blocked"
    REPORTED = "reported"
    STOPPED = "stopped"
    
    # Error states
    ERROR = "error"
    INVALID = "invalid"
    DUPLICATE = "duplicate"
    
    # Final states
    CONVERTED = "converted"
    LOST = "lost"
    ARCHIVED = "archived"


class StatusTaxonomy:
    """Manages status taxonomy and transitions."""
    
    # Status categories
    CATEGORIES = {
        'initial': [LeadStatus.NEW, LeadStatus.IMPORTED],
        'processing': [LeadStatus.ENQUEUED, LeadStatus.PROCESSING],
        'outreach': [LeadStatus.CONNECTION_REQUESTED, LeadStatus.CONNECTED, 
                     LeadStatus.FIRST_MESSAGE_SENT, LeadStatus.FOLLOW_UP_SENT],
        'engagement': [LeadStatus.VIEWED, LeadStatus.REPLIED, LeadStatus.CONVERSATION_STARTED],
        'positive': [LeadStatus.INTERESTED, LeadStatus.MEETING_SCHEDULED, 
                    LeadStatus.DEMO_REQUESTED, LeadStatus.PROPOSAL_SENT, LeadStatus.NEGOTIATION],
        'negative': [LeadStatus.NOT_INTERESTED, LeadStatus.DECLINED, LeadStatus.GHOSTED],
        'stop': [LeadStatus.OPTED_OUT, LeadStatus.BLOCKED, LeadStatus.REPORTED, LeadStatus.STOPPED],
        'error': [LeadStatus.ERROR, LeadStatus.INVALID, LeadStatus.DUPLICATE],
        'final': [LeadStatus.CONVERTED, LeadStatus.LOST, LeadStatus.ARCHIVED],
    }
    
    # Valid status transitions
    VALID_TRANSITIONS = {
        LeadStatus.NEW: [LeadStatus.IMPORTED, LeadStatus.ENQUEUED, LeadStatus.INVALID, LeadStatus.DUPLICATE],
        LeadStatus.IMPORTED: [LeadStatus.ENQUEUED, LeadStatus.INVALID, LeadStatus.DUPLICATE],
        LeadStatus.ENQUEUED: [LeadStatus.PROCESSING, LeadStatus.STOPPED],
        LeadStatus.PROCESSING: [LeadStatus.CONNECTION_REQUESTED, LeadStatus.ERROR, LeadStatus.STOPPED],
        LeadStatus.CONNECTION_REQUESTED: [LeadStatus.CONNECTED, LeadStatus.DECLINED, LeadStatus.ERROR, LeadStatus.STOPPED],
        LeadStatus.CONNECTED: [LeadStatus.FIRST_MESSAGE_SENT, LeadStatus.STOPPED],
        LeadStatus.FIRST_MESSAGE_SENT: [LeadStatus.VIEWED, LeadStatus.REPLIED, LeadStatus.FOLLOW_UP_SENT, LeadStatus.STOPPED],
        LeadStatus.FOLLOW_UP_SENT: [LeadStatus.VIEWED, LeadStatus.REPLIED, LeadStatus.STOPPED],
        LeadStatus.VIEWED: [LeadStatus.REPLIED, LeadStatus.GHOSTED, LeadStatus.STOPPED],
        LeadStatus.REPLIED: [LeadStatus.CONVERSATION_STARTED, LeadStatus.INTERESTED, LeadStatus.NOT_INTERESTED, LeadStatus.STOPPED],
        LeadStatus.CONVERSATION_STARTED: [LeadStatus.INTERESTED, LeadStatus.MEETING_SCHEDULED, LeadStatus.NOT_INTERESTED, LeadStatus.GHOSTED, LeadStatus.STOPPED],
        LeadStatus.INTERESTED: [LeadStatus.MEETING_SCHEDULED, LeadStatus.DEMO_REQUESTED, LeadStatus.NOT_INTERESTED, LeadStatus.STOPPED],
        LeadStatus.MEETING_SCHEDULED: [LeadStatus.DEMO_REQUESTED, LeadStatus.PROPOSAL_SENT, LeadStatus.NOT_INTERESTED, LeadStatus.GHOSTED, LeadStatus.STOPPED],
        LeadStatus.DEMO_REQUESTED: [LeadStatus.PROPOSAL_SENT, LeadStatus.NOT_INTERESTED, LeadStatus.STOPPED],
        LeadStatus.PROPOSAL_SENT: [LeadStatus.NEGOTIATION, LeadStatus.NOT_INTERESTED, LeadStatus.GHOSTED, LeadStatus.STOPPED],
        LeadStatus.NEGOTIATION: [LeadStatus.CONVERTED, LeadStatus.LOST, LeadStatus.STOPPED],
        LeadStatus.NOT_INTERESTED: [LeadStatus.LOST, LeadStatus.ARCHIVED],
        LeadStatus.DECLINED: [LeadStatus.LOST, LeadStatus.ARCHIVED],
        LeadStatus.GHOSTED: [LeadStatus.LOST, LeadStatus.ARCHIVED],
        LeadStatus.OPTED_OUT: [LeadStatus.ARCHIVED],
        LeadStatus.BLOCKED: [LeadStatus.ARCHIVED],
        LeadStatus.REPORTED: [LeadStatus.ARCHIVED],
        LeadStatus.STOPPED: [LeadStatus.ARCHIVED, LeadStatus.ENQUEUED],
        LeadStatus.ERROR: [LeadStatus.ENQUEUED, LeadStatus.INVALID, LeadStatus.ARCHIVED],
        LeadStatus.INVALID: [LeadStatus.ARCHIVED],
        LeadStatus.DUPLICATE: [LeadStatus.ARCHIVED],
        LeadStatus.CONVERTED: [LeadStatus.ARCHIVED],
        LeadStatus.LOST: [LeadStatus.ARCHIVED],
        LeadStatus.ARCHIVED: [],
    }
    
    @staticmethod
    def get_category(status: LeadStatus) -> Optional[str]:
        """Get category for a status.
        
        Args:
            status: Lead status
            
        Returns:
            Category name or None
        """
        for category, statuses in StatusTaxonomy.CATEGORIES.items():
            if status in statuses:
                return category
        return None
    
    @staticmethod
    def is_valid_transition(from_status: LeadStatus, to_status: LeadStatus) -> bool:
        """Check if status transition is valid.
        
        Args:
            from_status: Current status
            to_status: Target status
            
        Returns:
            True if transition is valid
        """
        valid_transitions = StatusTaxonomy.VALID_TRANSITIONS.get(from_status, [])
        return to_status in valid_transitions
    
    @staticmethod
    def get_valid_next_statuses(current_status: LeadStatus) -> List[LeadStatus]:
        """Get valid next statuses for current status.
        
        Args:
            current_status: Current status
            
        Returns:
            List of valid next statuses
        """
        return StatusTaxonomy.VALID_TRANSITIONS.get(current_status, []).copy()
    
    @staticmethod
    def is_final_status(status: LeadStatus) -> bool:
        """Check if status is a final state.
        
        Args:
            status: Lead status
            
        Returns:
            True if status is final
        """
        return status in StatusTaxonomy.CATEGORIES['final']
    
    @staticmethod
    def is_stop_status(status: LeadStatus) -> bool:
        """Check if status is a stop state.
        
        Args:
            status: Lead status
            
        Returns:
            True if status is a stop state
        """
        return status in StatusTaxonomy.CATEGORIES['stop']
    
    @staticmethod
    def is_active_status(status: LeadStatus) -> bool:
        """Check if status is active (not final or stop).
        
        Args:
            status: Lead status
            
        Returns:
            True if status is active
        """
        return not (StatusTaxonomy.is_final_status(status) or StatusTaxonomy.is_stop_status(status))
    
    @staticmethod
    def parse_status(status_string: str) -> Optional[LeadStatus]:
        """Parse status string to LeadStatus enum.
        
        Args:
            status_string: Status string
            
        Returns:
            LeadStatus enum or None
        """
        try:
            return LeadStatus(status_string.lower())
        except ValueError:
            return None
    
    @staticmethod
    def get_all_statuses() -> List[LeadStatus]:
        """Get all possible statuses.
        
        Returns:
            List of all LeadStatus values
        """
        return list(LeadStatus)
