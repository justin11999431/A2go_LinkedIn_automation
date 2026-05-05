"""Workflow sheet writer for upserting lead data to workflow sheet."""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from .lead_mapper import LeadMapper
from .human_stop_logic import HumanStopLogic

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
        'status': 'Status',
        'campaign': 'Campaign',
        'priority': 'Priority',
        'tags': 'Tags',
        'created_at': 'Created At',
        'updated_at': 'Updated At',
        'last_synced_at': 'Last Synced At',
        'human_notes': 'Human Notes',
        'human_status': 'Human Status',
        'human_priority': 'Human Priority',
        'human_tags': 'Human Tags',
        'last_human_update': 'Last Human Update',
        'manual_stop': 'Manual Stop',
        'opt_out_requested': 'Opt Out Requested',
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
        row = []
        
        for internal_field, column_name in WorkflowSheetWriter.WORKFLOW_COLUMN_MAP.items():
            value = lead.get(internal_field, '')
            
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
        
        # Create reverse mapping
        column_to_field = {v: k for k, v in WorkflowSheetWriter.WORKFLOW_COLUMN_MAP.items()}
        
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
        
        # Preserve human-entered fields if existing lead exists
        if existing_lead:
            upsert_lead = HumanStopLogic.preserve_human_fields(lead, existing_lead)
        
        # Update timestamp
        upsert_lead['updated_at'] = datetime.now().isoformat()
        
        # Set created_at if new lead
        if not existing_lead:
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
