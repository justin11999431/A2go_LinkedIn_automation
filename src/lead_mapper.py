"""Lead mapper for converting between source sheet format and internal format."""

import logging
from typing import Dict, Any, Optional
import hashlib

logger = logging.getLogger(__name__)


class LeadMapper:
    """Maps lead data between source sheet format and internal format."""
    
    # Source sheet column mapping (column name -> internal field name)
    SOURCE_COLUMN_MAP = {
        'First Name': 'first_name',
        'Last Name': 'last_name',
        'Email': 'email',
        'Company': 'company',
        'Title': 'title',
        'LinkedIn URL': 'linkedin_url',
        'Industry': 'industry',
        'Location': 'location',
        'Phone': 'phone',
        'Notes': 'notes',
        'Status': 'status',
        'Source': 'source',
        'Campaign': 'campaign',
        'Priority': 'priority',
        'Tags': 'tags',
    }
    
    # Internal format field names
    INTERNAL_FIELDS = [
        'lead_id',
        'first_name',
        'last_name',
        'email',
        'company',
        'title',
        'linkedin_url',
        'industry',
        'location',
        'phone',
        'notes',
        'status',
        'source',
        'campaign',
        'priority',
        'tags',
        'created_at',
        'updated_at',
    ]
    
    @staticmethod
    def generate_lead_id(first_name: str, last_name: str, email: str, company: str) -> str:
        """Generate deterministic lead ID.
        
        Args:
            first_name: Lead's first name
            last_name: Lead's last name
            email: Lead's email
            company: Lead's company
            
        Returns:
            Deterministic lead ID
        """
        # Create a unique string from the lead's identifying information
        unique_string = f"{first_name}|{last_name}|{email}|{company}".lower().strip()
        
        # Generate hash
        hash_object = hashlib.sha256(unique_string.encode())
        hex_dig = hash_object.hexdigest()
        
        # Return first 16 characters as lead ID
        return hex_dig[:16]
    
    @classmethod
    def map_source_to_internal(cls, source_row: Dict[str, Any], row_number: int) -> Dict[str, Any]:
        """Map source sheet row to internal format.
        
        Args:
            source_row: Row from source sheet with column headers as keys
            row_number: Row number in source sheet
            
        Returns:
            Lead in internal format
        """
        internal_lead = {}
        
        # Map columns using the column map
        for source_col, internal_field in cls.SOURCE_COLUMN_MAP.items():
            if source_col in source_row:
                internal_lead[internal_field] = source_row[source_col]
        
        # Generate lead ID if not present
        if 'lead_id' not in internal_lead:
            first_name = internal_lead.get('first_name', '')
            last_name = internal_lead.get('last_name', '')
            email = internal_lead.get('email', '')
            company = internal_lead.get('company', '')
            internal_lead['lead_id'] = cls.generate_lead_id(first_name, last_name, email, company)
        
        # Add metadata
        internal_lead['source_row_number'] = row_number
        internal_lead['created_at'] = internal_lead.get('created_at', '')
        internal_lead['updated_at'] = internal_lead.get('updated_at', '')
        
        return internal_lead
    
    @classmethod
    def map_internal_to_source(cls, internal_lead: Dict[str, Any]) -> Dict[str, Any]:
        """Map internal lead format back to source sheet format.
        
        Args:
            internal_lead: Lead in internal format
            
        Returns:
            Row in source sheet format
        """
        source_row = {}
        
        # Reverse map columns
        for source_col, internal_field in cls.SOURCE_COLUMN_MAP.items():
            if internal_field in internal_lead:
                source_row[source_col] = internal_lead[internal_field]
        
        return source_row
    
    @classmethod
    def get_internal_headers(cls) -> list:
        """Get internal format field headers.
        
        Returns:
            List of internal field names
        """
        return cls.INTERNAL_FIELDS.copy()
    
    @classmethod
    def get_source_headers(cls) -> list:
        """Get source sheet column headers.
        
        Returns:
            List of source column names
        """
        return list(cls.SOURCE_COLUMN_MAP.keys())
