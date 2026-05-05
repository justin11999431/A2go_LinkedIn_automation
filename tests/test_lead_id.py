"""Tests for lead ID generation."""

import pytest
from src.lead_mapper import LeadMapper


class TestLeadID:
    """Test lead ID generation."""
    
    def test_generate_lead_id_basic(self):
        """Test basic lead ID generation."""
        lead_id = LeadMapper.generate_lead_id('John', 'Doe', 'john@example.com', 'Acme Corp')
        
        assert lead_id is not None
        assert isinstance(lead_id, str)
        assert len(lead_id) == 16
    
    def test_generate_lead_id_deterministic(self):
        """Test that lead ID generation is deterministic."""
        lead_id1 = LeadMapper.generate_lead_id('John', 'Doe', 'john@example.com', 'Acme Corp')
        lead_id2 = LeadMapper.generate_lead_id('John', 'Doe', 'john@example.com', 'Acme Corp')
        
        assert lead_id1 == lead_id2
    
    def test_generate_lead_id_case_insensitive(self):
        """Test that lead ID generation is case insensitive."""
        lead_id1 = LeadMapper.generate_lead_id('John', 'Doe', 'john@example.com', 'Acme Corp')
        lead_id2 = LeadMapper.generate_lead_id('JOHN', 'DOE', 'JOHN@EXAMPLE.COM', 'ACME CORP')
        
        assert lead_id1 == lead_id2
    
    def test_generate_lead_id_whitespace_insensitive(self):
        """Test that lead ID generation ignores whitespace."""
        lead_id1 = LeadMapper.generate_lead_id('John', 'Doe', 'john@example.com', 'Acme Corp')
        lead_id2 = LeadMapper.generate_lead_id('  John  ', '  Doe  ', '  john@example.com  ', '  Acme Corp  ')
        
        assert lead_id1 == lead_id2
    
    def test_generate_lead_id_different_leads(self):
        """Test that different leads generate different IDs."""
        lead_id1 = LeadMapper.generate_lead_id('John', 'Doe', 'john@example.com', 'Acme Corp')
        lead_id2 = LeadMapper.generate_lead_id('Jane', 'Smith', 'jane@example.com', 'Beta Inc')
        
        assert lead_id1 != lead_id2
    
    def test_generate_lead_id_different_email(self):
        """Test that different emails generate different IDs."""
        lead_id1 = LeadMapper.generate_lead_id('John', 'Doe', 'john@example.com', 'Acme Corp')
        lead_id2 = LeadMapper.generate_lead_id('John', 'Doe', 'john.doe@example.com', 'Acme Corp')
        
        assert lead_id1 != lead_id2
    
    def test_generate_lead_id_different_company(self):
        """Test that different companies generate different IDs."""
        lead_id1 = LeadMapper.generate_lead_id('John', 'Doe', 'john@example.com', 'Acme Corp')
        lead_id2 = LeadMapper.generate_lead_id('John', 'Doe', 'john@example.com', 'Beta Inc')
        
        assert lead_id1 != lead_id2
    
    def test_generate_lead_id_empty_fields(self):
        """Test lead ID generation with empty fields."""
        lead_id = LeadMapper.generate_lead_id('', '', '', '')
        
        assert lead_id is not None
        assert isinstance(lead_id, str)
        assert len(lead_id) == 16
    
    def test_generate_lead_id_special_characters(self):
        """Test lead ID generation with special characters."""
        lead_id = LeadMapper.generate_lead_id('John', 'Doe', 'john+test@example.com', 'Acme & Corp')
        
        assert lead_id is not None
        assert isinstance(lead_id, str)
        assert len(lead_id) == 16
