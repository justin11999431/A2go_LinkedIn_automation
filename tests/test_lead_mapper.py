"""Tests for lead mapper."""

import pytest
from src.lead_mapper import LeadMapper


class TestLeadMapper:
    """Test lead mapping functionality."""
    
    def test_map_source_to_internal_basic(self):
        """Test basic mapping from source to internal format."""
        source_row = {
            'First Name': 'John',
            'Last Name': 'Doe',
            'Email': 'john@example.com',
            'Company': 'Acme Corp',
        }
        
        result = LeadMapper.map_source_to_internal(source_row, 1)
        
        assert result['first_name'] == 'John'
        assert result['last_name'] == 'Doe'
        assert result['email'] == 'john@example.com'
        assert result['company'] == 'Acme Corp'
        assert 'lead_id' in result
        assert result['source_row_number'] == 1
    
    def test_map_source_to_internal_with_all_fields(self):
        """Test mapping with all source fields."""
        source_row = {
            'First Name': 'John',
            'Last Name': 'Doe',
            'Email': 'john@example.com',
            'Company': 'Acme Corp',
            'Title': 'CEO',
            'LinkedIn URL': 'https://linkedin.com/in/johndoe',
            'Industry': 'Technology',
            'Location': 'San Francisco',
            'Phone': '+1-555-1234',
            'Notes': 'VIP lead',
            'Status': 'new',
            'Source': 'LinkedIn',
            'Campaign': 'Outreach Q1',
            'Priority': 'high',
            'Tags': 'vip,enterprise',
        }
        
        result = LeadMapper.map_source_to_internal(source_row, 1)
        
        assert result['first_name'] == 'John'
        assert result['title'] == 'CEO'
        assert result['linkedin_url'] == 'https://linkedin.com/in/johndoe'
        assert result['industry'] == 'Technology'
        assert result['location'] == 'San Francisco'
        assert result['phone'] == '+1-555-1234'
        assert result['notes'] == 'VIP lead'
        assert result['status'] == 'new'
        assert result['source'] == 'LinkedIn'
        assert result['campaign'] == 'Outreach Q1'
        assert result['priority'] == 'high'
        assert result['tags'] == 'vip,enterprise'
    
    def test_map_source_to_internal_generates_lead_id(self):
        """Test that mapping generates lead ID."""
        source_row = {
            'First Name': 'John',
            'Last Name': 'Doe',
            'Email': 'john@example.com',
            'Company': 'Acme Corp',
        }
        
        result = LeadMapper.map_source_to_internal(source_row, 1)
        
        assert 'lead_id' in result
        assert len(result['lead_id']) == 16
    
    def test_map_internal_to_source_basic(self):
        """Test basic mapping from internal to source format."""
        internal_lead = {
            'lead_id': 'abc123',
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'company': 'Acme Corp',
        }
        
        result = LeadMapper.map_internal_to_source(internal_lead)
        
        assert result['First Name'] == 'John'
        assert result['Last Name'] == 'Doe'
        assert result['Email'] == 'john@example.com'
        assert result['Company'] == 'Acme Corp'
    
    def test_map_internal_to_source_with_all_fields(self):
        """Test mapping with all internal fields."""
        internal_lead = {
            'lead_id': 'abc123',
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'company': 'Acme Corp',
            'title': 'CEO',
            'linkedin_url': 'https://linkedin.com/in/johndoe',
            'industry': 'Technology',
            'location': 'San Francisco',
            'phone': '+1-555-1234',
            'notes': 'VIP lead',
            'status': 'new',
            'source': 'LinkedIn',
            'campaign': 'Outreach Q1',
            'priority': 'high',
            'tags': 'vip,enterprise',
        }
        
        result = LeadMapper.map_internal_to_source(internal_lead)
        
        assert result['First Name'] == 'John'
        assert result['Title'] == 'CEO'
        assert result['LinkedIn URL'] == 'https://linkedin.com/in/johndoe'
        assert result['Industry'] == 'Technology'
        assert result['Location'] == 'San Francisco'
        assert result['Phone'] == '+1-555-1234'
        assert result['Notes'] == 'VIP lead'
        assert result['Status'] == 'new'
        assert result['Source'] == 'LinkedIn'
        assert result['Campaign'] == 'Outreach Q1'
        assert result['Priority'] == 'high'
        assert result['Tags'] == 'vip,enterprise'
    
    def test_get_internal_headers(self):
        """Test getting internal field headers."""
        headers = LeadMapper.get_internal_headers()
        
        assert isinstance(headers, list)
        assert 'lead_id' in headers
        assert 'first_name' in headers
        assert 'last_name' in headers
        assert 'email' in headers
        assert 'company' in headers
    
    def test_get_source_headers(self):
        """Test getting source column headers."""
        headers = LeadMapper.get_source_headers()
        
        assert isinstance(headers, list)
        assert 'First Name' in headers
        assert 'Last Name' in headers
        assert 'Email' in headers
        assert 'Company' in headers
    
    def test_roundtrip_mapping(self):
        """Test that roundtrip mapping preserves data."""
        source_row = {
            'First Name': 'John',
            'Last Name': 'Doe',
            'Email': 'john@example.com',
            'Company': 'Acme Corp',
            'Title': 'CEO',
        }
        
        # Map to internal
        internal = LeadMapper.map_source_to_internal(source_row, 1)
        
        # Map back to source
        source_again = LeadMapper.map_internal_to_source(internal)
        
        # Verify key fields are preserved
        assert source_again['First Name'] == source_row['First Name']
        assert source_again['Last Name'] == source_row['Last Name']
        assert source_again['Email'] == source_row['Email']
        assert source_again['Company'] == source_row['Company']
        assert source_again['Title'] == source_row['Title']
