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
        'linkedin_url': 'LinkedIn Profile URL',
        'first_name': 'First Name',
        'last_name': 'Last Name',
        'company': 'Company',
        'title': 'Title',
        'industry': 'Industry',
        'location': 'Location',
        'connection_status': 'Connection Status',
        'current_step': 'Current Step',
        'step_status': 'Step Status',
        'last_action_date': 'Last Action Date',
        'next_action_date': 'Next Action Date',
        'connection_request_message': 'Connection Request Message',
        'first_follow_up_message': 'First Follow-up Message',
        'second_follow_up_message': 'Second Follow-up Message',
        'third_follow_up_message': 'Third Follow-up Message',
        'fourth_follow_up_message': 'Fourth Follow-up Message',
        'fifth_follow_up_message': 'Fifth Follow-up Message',
        'sixth_follow_up_message': 'Sixth Follow-up Message',
        'seventh_follow_up_message': 'Seventh Follow-up Message',
        'eighth_follow_up_message': 'Eighth Follow-up Message',
        'ninth_follow_up_message': 'Ninth Follow-up Message',
        'tenth_follow_up_message': 'Tenth Follow-up Message',
        'notes': 'Notes',
        'last_updated': 'Last Updated',
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
            'Lead ID',                    # 0
            'LinkedIn Profile URL',       # 1
            'First Name',                 # 2
            'Last Name',                  # 3
            'Company',                    # 4
            'Title',                      # 5
            'Industry',                   # 6
            'Location',                   # 7
            'Connection Status',           # 8
            'Current Step',               # 9
            'Step Status',                # 10
            'Last Action Date',           # 11
            'Next Action Date',           # 12
            'Connection Request Message', # 13
            'First Follow-up Message',    # 14
            'Second Follow-up Message',   # 15
            'Third Follow-up Message',    # 16
            'Fourth Follow-up Message',   # 17
            'Fifth Follow-up Message',    # 18
            'Sixth Follow-up Message',   # 19
            'Seventh Follow-up Message',  # 20
            'Eighth Follow-up Message',   # 21
            'Ninth Follow-up Message',    # 22
            'Tenth Follow-up Message',   # 23
            'Notes',                      # 24
            'Last Updated',               # 25
        ]
        
        # Map internal fields to workflow sheet columns
        field_mapping = {
            'Lead ID': lead.get('lead_id', ''),
            'LinkedIn Profile URL': lead.get('linkedin_url', ''),
            'First Name': lead.get('first_name', ''),
            'Last Name': lead.get('last_name', ''),
            'Company': lead.get('company', ''),
            'Title': lead.get('title', ''),
            'Industry': lead.get('industry', ''),
            'Location': lead.get('location', ''),
            'Connection Status': lead.get('connection_status', ''),
            'Current Step': lead.get('current_step', ''),
            'Step Status': lead.get('step_status', ''),
            'Last Action Date': lead.get('last_action_date', ''),
            'Next Action Date': lead.get('next_action_date', ''),
            'Connection Request Message': lead.get('connection_request_message', ''),
            'First Follow-up Message': lead.get('first_follow_up_message', ''),
            'Second Follow-up Message': lead.get('second_follow_up_message', ''),
            'Third Follow-up Message': lead.get('third_follow_up_message', ''),
            'Fourth Follow-up Message': lead.get('fourth_follow_up_message', ''),
            'Fifth Follow-up Message': lead.get('fifth_follow_up_message', ''),
            'Sixth Follow-up Message': lead.get('sixth_follow_up_message', ''),
            'Seventh Follow-up Message': lead.get('seventh_follow_up_message', ''),
            'Eighth Follow-up Message': lead.get('eighth_follow_up_message', ''),
            'Ninth Follow-up Message': lead.get('ninth_follow_up_message', ''),
            'Tenth Follow-up Message': lead.get('tenth_follow_up_message', ''),
            'Notes': lead.get('notes', ''),
            'Last Updated': lead.get('last_updated', ''),
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
            'LinkedIn Profile URL': 'linkedin_url',
            'First Name': 'first_name',
            'Last Name': 'last_name',
            'Company': 'company',
            'Title': 'title',
            'Industry': 'industry',
            'Location': 'location',
            'Connection Status': 'connection_status',
            'Current Step': 'current_step',
            'Step Status': 'step_status',
            'Last Action Date': 'last_action_date',
            'Next Action Date': 'next_action_date',
            'Connection Request Message': 'connection_request_message',
            'First Follow-up Message': 'first_follow_up_message',
            'Second Follow-up Message': 'second_follow_up_message',
            'Third Follow-up Message': 'third_follow_up_message',
            'Fourth Follow-up Message': 'fourth_follow_up_message',
            'Fifth Follow-up Message': 'fifth_follow_up_message',
            'Sixth Follow-up Message': 'sixth_follow_up_message',
            'Seventh Follow-up Message': 'seventh_follow_up_message',
            'Eighth Follow-up Message': 'eighth_follow_up_message',
            'Ninth Follow-up Message': 'ninth_follow_up_message',
            'Tenth Follow-up Message': 'tenth_follow_up_message',
            'Notes': 'notes',
            'Last Updated': 'last_updated',
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
