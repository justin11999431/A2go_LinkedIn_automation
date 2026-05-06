"""Workflow sheet writer for upserting lead data to workflow sheet."""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from lead_mapper import LeadMapper
from human_stop_logic import HumanStopLogic

logger = logging.getLogger(__name__)


class WorkflowSheetWriter:
    """Writes lead data to workflow sheet with upsert logic."""
    
    # Workflow sheet column mapping (internal field -> column name)
    WORKFLOW_COLUMN_MAP = {
        'lead_id': 'Lead ID',
        'first_name': 'First Name',
        'last_name': 'Last Name',
        'email': 'Email',
        'company': 'Company',
        'title': 'Title',
        'linkedin_url': 'LinkedIn URL',
        'industry': 'Industry',
        'location': 'Location',
        'phone': 'Phone',
        'status': 'Automation Status',
        'campaign': 'Campaign Name',
        'priority': 'Priority',
        'tags': 'Tags',
        'created_at': 'Created At',
        'updated_at': 'Updated At',
        'last_synced_at': 'Last Synced At',
        'human_notes': 'Notes',
        'human_status': 'Human Status',
        'human_priority': 'Human Priority',
        'human_tags': 'Human Tags',
        'last_human_update': 'Owner Last Action Date',
        'manual_stop': 'Manual Stop',
        'opt_out_requested': 'Opt-Out / Do Not Contact',
        'negative_feedback': 'Negative Feedback',
        'complaint_risk': 'Complaint Risk',
        'account_issue': 'Account Issue',
    }
    
    @staticmethod
    def lead_to_row(lead: Dict[str, Any]) -> List[Any]:
        """Convert lead to workflow sheet row.
        
        Args:
            lead: Lead data
            
        Returns:
            List of values for workflow sheet row
        """
        # Actual workflow sheet column order
        columns = [
            'Lead ID',                    # 1
            'Campaign Name',              # 2
            'Salesrobot Campaign ID',     # 3
            'Salesrobot Lead ID',         # 4
            'Persona',                    # 5
            'Personalization Note',      # 6
            'Pain Point',                 # 7
            'Offer / CTA',                # 8
            'Connection Request Copy',   # 9
            'Follow-Up 1 Copy',           # 10
            'Follow-Up 2 Copy',           # 11
            'Follow-Up 3 Copy',           # 12
            'Automation Status',          # 13
            'Connection Sent Date',       # 14
            'Connection Accepted Date',   # 15
            'Last Message Sent Date',     # 16
            'Reply Status',               # 17
            'Reply Text',                 # 18
            'Human Response Detected',    # 19
            'Human In Loop Owner',        # 20
            'Owner Last Action Date',     # 21
            'Meeting Booked',             # 22
            'Opt-Out / Do Not Contact',   # 23
            'Error Message',              # 24
            'Last Synced At',             # 25
            'Notes',                      # 26
        ]
        
        # Map internal fields to workflow sheet columns
        field_mapping = {
            'Lead ID': lead.get('lead_id', ''),
            'Campaign Name': lead.get('campaign', 'A2go | Forecasting'),
            'Salesrobot Campaign ID': lead.get('salesrobot_campaign_id', ''),
            'Salesrobot Lead ID': lead.get('salesrobot_lead_id', ''),
            'Persona': lead.get('title', ''),
            'Personalization Note': lead.get('notes', ''),
            'Pain Point': '',
            'Offer / CTA': '',
            'Connection Request Copy': '',
            'Follow-Up 1 Copy': '',
            'Follow-Up 2 Copy': '',
            'Follow-Up 3 Copy': '',
            'Automation Status': lead.get('status', 'new'),
            'Connection Sent Date': lead.get('connection_sent_date', ''),
            'Connection Accepted Date': lead.get('connection_accepted_date', ''),
            'Last Message Sent Date': lead.get('last_message_sent_date', ''),
            'Reply Status': lead.get('reply_status', ''),
            'Reply Text': lead.get('reply_text', ''),
            'Human Response Detected': lead.get('human_response_detected', ''),
            'Human In Loop Owner': lead.get('human_in_loop_owner', ''),
            'Owner Last Action Date': lead.get('last_human_update', ''),
            'Meeting Booked': lead.get('meeting_booked', ''),
            'Opt-Out / Do Not Contact': 'Yes' if lead.get('opt_out_requested') else 'No',
            'Error Message': lead.get('error_message', ''),
            'Last Synced At': lead.get('last_synced_at', ''),
            'Notes': lead.get('human_notes', ''),
        }
        
        # Create row in correct column order
        row = []
        for column in columns:
            value = field_mapping.get(column, '')
            
            # Handle list fields (like tags)
            if isinstance(value, list):
                value = ', '.join(str(v) for v in value)
            
            # Handle boolean fields
            if isinstance(value, bool):
                value = 'Yes' if value else 'No'
            
            # Handle None values
            if value is None:
                value = ''
            
            row.append(value)
        
        return row
    
    @staticmethod
    def row_to_lead(row: List[Any], headers: List[str]) -> Dict[str, Any]:
        """Convert workflow sheet row to lead.
        
        Args:
            row: Workflow sheet row values
            headers: Workflow sheet column headers
            
        Returns:
            Lead data
        """
        lead = {}
        
        # Map workflow sheet columns to internal fields
        column_to_field = {
            'Lead ID': 'lead_id',
            'Campaign Name': 'campaign',
            'Salesrobot Campaign ID': 'salesrobot_campaign_id',
            'Salesrobot Lead ID': 'salesrobot_lead_id',
            'Persona': 'title',
            'Personalization Note': 'notes',
            'Pain Point': 'pain_point',
            'Offer / CTA': 'offer_cta',
            'Connection Request Copy': 'connection_request_copy',
            'Follow-Up 1 Copy': 'follow_up_1_copy',
            'Follow-Up 2 Copy': 'follow_up_2_copy',
            'Follow-Up 3 Copy': 'follow_up_3_copy',
            'Automation Status': 'status',
            'Connection Sent Date': 'connection_sent_date',
            'Connection Accepted Date': 'connection_accepted_date',
            'Last Message Sent Date': 'last_message_sent_date',
            'Reply Status': 'reply_status',
            'Reply Text': 'reply_text',
            'Human Response Detected': 'human_response_detected',
            'Human In Loop Owner': 'human_in_loop_owner',
            'Owner Last Action Date': 'last_human_update',
            'Meeting Booked': 'meeting_booked',
            'Opt-Out / Do Not Contact': 'opt_out_requested',
            'Error Message': 'error_message',
            'Last Synced At': 'last_synced_at',
            'Notes': 'human_notes',
        }
        
        for i, value in enumerate(row):
            if i < len(headers):
                column_name = headers[i]
                internal_field = column_to_field.get(column_name)
                
                if internal_field:
                    # Handle boolean fields
                    if value in ['Yes', 'No']:
                        value = value == 'Yes'
                    
                    # Handle empty strings
                    if value == '':
                        value = None
                    
                    lead[internal_field] = value
        
        return lead
    
    @staticmethod
    def find_existing_row(worksheet_data: List[List[Any]], lead_id: str, 
                          lead_id_column_index: int = 0) -> Optional[int]:
        """Find existing row for lead in worksheet.
        
        Args:
            worksheet_data: Worksheet data (including headers)
            lead_id: Lead ID to find
            lead_id_column_index: Index of Lead ID column
            
        Returns:
            Row index (0-based) or None
        """
        # Skip header row
        for i, row in enumerate(worksheet_data[1:], start=1):
            if i < len(worksheet_data) and len(row) > lead_id_column_index:
                if str(row[lead_id_column_index]) == str(lead_id):
                    return i
        
        return None
    
    @staticmethod
    def prepare_upsert_data(lead: Dict[str, Any], existing_lead: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Prepare lead data for upsert (insert or update).
        
        Args:
            lead: New lead data
            existing_lead: Existing lead data (if updating)
            
        Returns:
            Lead data ready for upsert
        """
        upsert_lead = lead.copy()
        
        # Preserve human-entered fields if existing lead exists and is not empty
        if existing_lead and any(existing_lead.values()):
            upsert_lead = HumanStopLogic.preserve_human_fields(lead, existing_lead)
        
        # Update timestamp
        upsert_lead['updated_at'] = datetime.now().isoformat()
        
        # Set created_at if new lead
        if not existing_lead or not any(existing_lead.values()):
            upsert_lead['created_at'] = datetime.now().isoformat()
        
        return upsert_lead
    
    @staticmethod
    def get_headers() -> List[str]:
        """Get workflow sheet column headers.
        
        Returns:
            List of column headers
        """
        return list(WorkflowSheetWriter.WORKFLOW_COLUMN_MAP.values())
    
    @staticmethod
    def get_column_index(column_name: str) -> Optional[int]:
        """Get column index for column name.
        
        Args:
            column_name: Column name
            
        Returns:
            Column index (0-based) or None
        """
        headers = WorkflowSheetWriter.get_headers()
        try:
            return headers.index(column_name)
        except ValueError:
            return None
