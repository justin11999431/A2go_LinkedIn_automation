"""Status synchronization between Salesrobot and workflow sheet."""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from .status_taxonomy import LeadStatus, StatusTaxonomy

logger = logging.getLogger(__name__)


class StatusSync:
    """Synchronizes status between Salesrobot and workflow sheet."""
    
    # Salesrobot status to internal status mapping
    SALESROBOT_STATUS_MAP = {
        'new': LeadStatus.NEW,
        'invited': LeadStatus.CONNECTION_REQUESTED,
        'connected': LeadStatus.CONNECTED,
        'message_sent': LeadStatus.FIRST_MESSAGE_SENT,
        'replied': LeadStatus.REPLIED,
        'interested': LeadStatus.INTERESTED,
        'not_interested': LeadStatus.NOT_INTERESTED,
        'opted_out': LeadStatus.OPTED_OUT,
        'blocked': LeadStatus.BLOCKED,
        'error': LeadStatus.ERROR,
    }
    
    # Internal status to Salesrobot status mapping
    INTERNAL_STATUS_MAP = {
        LeadStatus.NEW: 'new',
        LeadStatus.IMPORTED: 'new',
        LeadStatus.ENQUEUED: 'new',
        LeadStatus.PROCESSING: 'new',
        LeadStatus.CONNECTION_REQUESTED: 'invited',
        LeadStatus.CONNECTED: 'connected',
        LeadStatus.FIRST_MESSAGE_SENT: 'message_sent',
        LeadStatus.FOLLOW_UP_SENT: 'message_sent',
        LeadStatus.VIEWED: 'message_sent',
        LeadStatus.REPLIED: 'replied',
        LeadStatus.CONVERSATION_STARTED: 'replied',
        LeadStatus.INTERESTED: 'interested',
        LeadStatus.MEETING_SCHEDULED: 'interested',
        LeadStatus.DEMO_REQUESTED: 'interested',
        LeadStatus.PROPOSAL_SENT: 'interested',
        LeadStatus.NEGOTIATION: 'interested',
        LeadStatus.NOT_INTERESTED: 'not_interested',
        LeadStatus.DECLINED: 'not_interested',
        LeadStatus.GHOSTED: 'not_interested',
        LeadStatus.OPTED_OUT: 'opted_out',
        LeadStatus.BLOCKED: 'blocked',
        LeadStatus.REPORTED: 'blocked',
        LeadStatus.STOPPED: 'not_interested',
        LeadStatus.ERROR: 'error',
        LeadStatus.INVALID: 'error',
        LeadStatus.DUPLICATE: 'error',
        LeadStatus.CONVERTED: 'interested',
        LeadStatus.LOST: 'not_interested',
        LeadStatus.ARCHIVED: 'not_interested',
    }
    
    @staticmethod
    def map_salesrobot_status(salesrobot_status: str) -> Optional[LeadStatus]:
        """Map Salesrobot status to internal status.
        
        Args:
            salesrobot_status: Salesrobot status string
            
        Returns:
            Internal LeadStatus or None
        """
        return StatusSync.SALESROBOT_STATUS_MAP.get(salesrobot_status.lower())
    
    @staticmethod
    def map_internal_status(internal_status: LeadStatus) -> str:
        """Map internal status to Salesrobot status.
        
        Args:
            internal_status: Internal LeadStatus
            
        Returns:
            Salesrobot status string
        """
        return StatusSync.INTERNAL_STATUS_MAP.get(internal_status, 'new')
    
    @staticmethod
    def sync_status_from_salesrobot(lead: Dict[str, Any], salesrobot_data: Dict[str, Any]) -> Dict[str, Any]:
        """Sync lead status from Salesrobot data.
        
        Args:
            lead: Current lead data
            salesrobot_data: Salesrobot API response data
            
        Returns:
            Updated lead with synced status
        """
        updated_lead = lead.copy()
        
        # Get Salesrobot status
        salesrobot_status = salesrobot_data.get('status', 'new')
        internal_status = StatusSync.map_salesrobot_status(salesrobot_status)
        
        if internal_status:
            # Check if transition is valid
            current_status = LeadStatus(lead.get('status', LeadStatus.NEW.value))
            if StatusTaxonomy.is_valid_transition(current_status, internal_status):
                updated_lead['status'] = internal_status.value
                updated_lead['last_synced_at'] = datetime.now().isoformat()
                logger.info(f"Synced status from Salesrobot: {salesrobot_status} -> {internal_status.value}")
            else:
                logger.warning(f"Invalid status transition: {current_status.value} -> {internal_status.value}")
        
        return updated_lead
    
    @staticmethod
    def sync_status_to_salesrobot(lead: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare lead status for syncing to Salesrobot.
        
        Args:
            lead: Lead data
            
        Returns:
            Data ready for Salesrobot API
        """
        internal_status = LeadStatus(lead.get('status', LeadStatus.NEW.value))
        salesrobot_status = StatusSync.map_internal_status(internal_status)
        
        return {
            'status': salesrobot_status,
            'lead_id': lead.get('lead_id'),
        }
    
    @staticmethod
    def detect_status_conflict(lead: Dict[str, Any], salesrobot_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Detect status conflict between lead and Salesrobot.
        
        Args:
            lead: Current lead data
            salesrobot_data: Salesrobot API response data
            
        Returns:
            Conflict details or None
        """
        lead_status = LeadStatus(lead.get('status', LeadStatus.NEW.value))
        salesrobot_status = StatusSync.map_salesrobot_status(salesrobot_data.get('status', 'new'))
        
        if salesrobot_status and lead_status != salesrobot_status:
            return {
                'lead_status': lead_status.value,
                'salesrobot_status': salesrobot_status.value,
                'conflict_type': 'status_mismatch',
                'timestamp': datetime.now().isoformat(),
            }
        
        return None
    
    @staticmethod
    def resolve_status_conflict(lead: Dict[str, Any], salesrobot_data: Dict[str, Any], 
                                  strategy: str = 'salesrobot_wins') -> Dict[str, Any]:
        """Resolve status conflict between lead and Salesrobot.
        
        Args:
            lead: Current lead data
            salesrobot_data: Salesrobot API response data
            strategy: Resolution strategy ('salesrobot_wins', 'lead_wins', 'most_recent')
            
        Returns:
            Updated lead with resolved status
        """
        conflict = StatusSync.detect_status_conflict(lead, salesrobot_data)
        
        if not conflict:
            return lead
        
        if strategy == 'salesrobot_wins':
            return StatusSync.sync_status_from_salesrobot(lead, salesrobot_data)
        elif strategy == 'lead_wins':
            return lead
        elif strategy == 'most_recent':
            # Compare timestamps and use most recent
            lead_updated = lead.get('updated_at', '')
            salesrobot_updated = salesrobot_data.get('updated_at', '')
            
            if salesrobot_updated > lead_updated:
                return StatusSync.sync_status_from_salesrobot(lead, salesrobot_data)
            else:
                return lead
        else:
            logger.warning(f"Unknown conflict resolution strategy: {strategy}")
            return lead
