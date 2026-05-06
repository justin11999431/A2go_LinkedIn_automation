"""Salesrobot mapper for converting between internal format and Salesrobot format."""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from status_taxonomy import LeadStatus, StatusTaxonomy
from status_sync import StatusSync

logger = logging.getLogger(__name__)


class SalesrobotMapper:
    """Maps lead data between internal format and Salesrobot format."""
    
    # Internal field to Salesrobot field mapping
    INTERNAL_TO_SALESROBOT_MAP = {
        'first_name': 'first_name',
        'last_name': 'last_name',
        'email': 'email',
        'company': 'company',
        'title': 'job_title',
        'linkedin_url': 'linkedin_profile_url',
        'industry': 'industry',
        'location': 'location',
        'phone': 'phone_number',
        'notes': 'notes',
        'status': 'status',
        'campaign': 'campaign_id',
    }
    
    # Salesrobot field to internal field mapping
    SALESROBOT_TO_INTERNAL_MAP = {v: k for k, v in INTERNAL_TO_SALESROBOT_MAP.items()}
    
    @staticmethod
    def map_to_salesrobot(lead: Dict[str, Any]) -> Dict[str, Any]:
        """Map internal lead format to Salesrobot format.
        
        Args:
            lead: Lead in internal format
            
        Returns:
            Lead in Salesrobot format
        """
        salesrobot_lead = {}
        
        # Map fields using the field map
        for internal_field, salesrobot_field in SalesrobotMapper.INTERNAL_TO_SALESROBOT_MAP.items():
            if internal_field in lead and lead[internal_field]:
                salesrobot_lead[salesrobot_field] = lead[internal_field]
        
        # Map status using status sync
        if 'status' in lead:
            internal_status = LeadStatus(lead['status'])
            salesrobot_lead['status'] = StatusSync.map_internal_status(internal_status)
        
        # Add required Salesrobot fields
        if 'lead_id' in lead:
            salesrobot_lead['external_id'] = lead['lead_id']
        
        return salesrobot_lead
    
    @staticmethod
    def map_from_salesrobot(salesrobot_lead: Dict[str, Any]) -> Dict[str, Any]:
        """Map Salesrobot lead format to internal format.
        
        Args:
            salesrobot_lead: Lead in Salesrobot format
            
        Returns:
            Lead in internal format
        """
        internal_lead = {}
        
        # Map fields using the field map
        for salesrobot_field, internal_field in SalesrobotMapper.SALESROBOT_TO_INTERNAL_MAP.items():
            if salesrobot_field in salesrobot_lead and salesrobot_lead[salesrobot_field]:
                internal_lead[internal_field] = salesrobot_lead[salesrobot_field]
        
        # Map status using status sync
        if 'status' in salesrobot_lead:
            internal_status = StatusSync.map_salesrobot_status(salesrobot_lead['status'])
            if internal_status:
                internal_lead['status'] = internal_status.value
        
        # Add lead_id from external_id
        if 'external_id' in salesrobot_lead:
            internal_lead['lead_id'] = salesrobot_lead['external_id']
        elif 'id' in salesrobot_lead:
            internal_lead['lead_id'] = salesrobot_lead['id']
        
        # Add timestamps
        if 'created_at' in salesrobot_lead:
            internal_lead['created_at'] = salesrobot_lead['created_at']
        if 'updated_at' in salesrobot_lead:
            internal_lead['updated_at'] = salesrobot_lead['updated_at']
        
        return internal_lead
    
    @staticmethod
    def map_campaign_to_salesrobot(campaign: Dict[str, Any]) -> Dict[str, Any]:
        """Map internal campaign format to Salesrobot format.
        
        Args:
            campaign: Campaign in internal format
            
        Returns:
            Campaign in Salesrobot format
        """
        salesrobot_campaign = {
            'name': campaign.get('name', ''),
            'description': campaign.get('description', ''),
        }
        
        # Map campaign settings
        if 'settings' in campaign:
            settings = campaign['settings']
            salesrobot_campaign.update(settings)
        
        return salesrobot_campaign
    
    @staticmethod
    def map_campaign_from_salesrobot(salesrobot_campaign: Dict[str, Any]) -> Dict[str, Any]:
        """Map Salesrobot campaign format to internal format.
        
        Args:
            salesrobot_campaign: Campaign in Salesrobot format
            
        Returns:
            Campaign in internal format
        """
        internal_campaign = {
            'name': salesrobot_campaign.get('name', ''),
            'description': salesrobot_campaign.get('description', ''),
            'campaign_id': salesrobot_campaign.get('id', ''),
        }
        
        # Extract settings
        settings = {}
        for key, value in salesrobot_campaign.items():
            if key not in ['name', 'description', 'id', 'created_at', 'updated_at']:
                settings[key] = value
        
        if settings:
            internal_campaign['settings'] = settings
        
        # Add timestamps
        if 'created_at' in salesrobot_campaign:
            internal_campaign['created_at'] = salesrobot_campaign['created_at']
        if 'updated_at' in salesrobot_campaign:
            internal_campaign['updated_at'] = salesrobot_campaign['updated_at']
        
        return internal_campaign
    
    @staticmethod
    def map_stats_from_salesrobot(salesrobot_stats: Dict[str, Any]) -> Dict[str, Any]:
        """Map Salesrobot stats to internal format.
        
        Args:
            salesrobot_stats: Stats from Salesrobot API
            
        Returns:
            Stats in internal format
        """
        return {
            'total_leads': salesrobot_stats.get('total_leads', 0),
            'active_leads': salesrobot_stats.get('active_leads', 0),
            'connected_leads': salesrobot_stats.get('connected_leads', 0),
            'replied_leads': salesrobot_stats.get('replied_leads', 0),
            'interested_leads': salesrobot_stats.get('interested_leads', 0),
            'not_interested_leads': salesrobot_stats.get('not_interested_leads', 0),
            'opted_out_leads': salesrobot_stats.get('opted_out_leads', 0),
            'messages_sent': salesrobot_stats.get('messages_sent', 0),
            'connection_requests_sent': salesrobot_stats.get('connection_requests_sent', 0),
            'response_rate': salesrobot_stats.get('response_rate', 0.0),
            'updated_at': datetime.now().isoformat(),
        }
