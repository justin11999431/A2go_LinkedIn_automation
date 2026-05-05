"""Tests for lead validator."""

import pytest
from src.lead_validator import LeadValidator


class TestLeadValidator:
    """Test lead validation functionality."""
    
    def test_validate_email_valid(self):
        """Test validation of valid email."""
        assert LeadValidator.validate_email('john@example.com') is True
        assert LeadValidator.validate_email('john.doe@example.co.uk') is True
        assert LeadValidator.validate_email('john+test@example.com') is True
    
    def test_validate_email_invalid(self):
        """Test validation of invalid email."""
        assert LeadValidator.validate_email('') is False
        assert LeadValidator.validate_email('invalid') is False
        assert LeadValidator.validate_email('invalid@') is False
        assert LeadValidator.validate_email('@example.com') is False
        assert LeadValidator.validate_email('invalid@example') is False
    
    def test_validate_linkedin_url_valid(self):
        """Test validation of valid LinkedIn URL."""
        assert LeadValidator.validate_linkedin_url('https://linkedin.com/in/johndoe') is True
        assert LeadValidator.validate_linkedin_url('https://www.linkedin.com/in/johndoe') is True
        assert LeadValidator.validate_linkedin_url('http://linkedin.com/in/johndoe') is True
        assert LeadValidator.validate_linkedin_url('') is True  # Optional field
    
    def test_validate_linkedin_url_invalid(self):
        """Test validation of invalid LinkedIn URL."""
        assert LeadValidator.validate_linkedin_url('not-a-url') is False
        assert LeadValidator.validate_linkedin_url('https://example.com/in/johndoe') is False
        assert LeadValidator.validate_linkedin_url('https://linkedin.com/profile/johndoe') is False
    
    def test_validate_phone_valid(self):
        """Test validation of valid phone number."""
        assert LeadValidator.validate_phone('+1-555-1234') is True
        assert LeadValidator.validate_phone('555-1234') is True
        assert LeadValidator.validate_phone('(555) 123-4567') is True
        assert LeadValidator.validate_phone('5551234567') is True
        assert LeadValidator.validate_phone('') is True  # Optional field
    
    def test_validate_phone_invalid(self):
        """Test validation of invalid phone number."""
        assert LeadValidator.validate_phone('abc') is False
        assert LeadValidator.validate_phone('123') is False  # Too short
        assert LeadValidator.validate_phone('12345678901234567890') is False  # Too long
    
    def test_validate_lead_valid(self):
        """Test validation of valid lead."""
        lead = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'company': 'Acme Corp',
        }
        
        result = LeadValidator.validate_lead(lead)
        
        assert result['valid'] is True
        assert len(result['errors']) == 0
    
    def test_validate_lead_missing_required_field(self):
        """Test validation with missing required field."""
        lead = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            # Missing company
        }
        
        result = LeadValidator.validate_lead(lead)
        
        assert result['valid'] is False
        assert len(result['errors']) > 0
        assert any('company' in error.lower() for error in result['errors'])
    
    def test_validate_lead_invalid_email(self):
        """Test validation with invalid email."""
        lead = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'invalid-email',
            'company': 'Acme Corp',
        }
        
        result = LeadValidator.validate_lead(lead)
        
        assert result['valid'] is False
        assert len(result['errors']) > 0
        assert any('email' in error.lower() for error in result['errors'])
    
    def test_validate_lead_with_warnings(self):
        """Test validation with warnings."""
        lead = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'company': 'Acme Corp',
            'linkedin_url': 'not-a-url',
            'phone': 'abc',
        }
        
        result = LeadValidator.validate_lead(lead)
        
        assert result['valid'] is True
        assert len(result['warnings']) > 0
    
    def test_validate_leads_all_valid(self):
        """Test validation of multiple valid leads."""
        leads = [
            {
                'first_name': 'John',
                'last_name': 'Doe',
                'email': 'john@example.com',
                'company': 'Acme Corp',
            },
            {
                'first_name': 'Jane',
                'last_name': 'Smith',
                'email': 'jane@example.com',
                'company': 'Beta Inc',
            },
        ]
        
        result = LeadValidator.validate_leads(leads)
        
        assert result['total'] == 2
        assert result['valid'] == 2
        assert result['invalid'] == 0
        assert len(result['valid_leads']) == 2
        assert len(result['invalid_leads']) == 0
    
    def test_validate_leads_mixed(self):
        """Test validation of mixed valid and invalid leads."""
        leads = [
            {
                'first_name': 'John',
                'last_name': 'Doe',
                'email': 'john@example.com',
                'company': 'Acme Corp',
            },
            {
                'first_name': 'Jane',
                'last_name': 'Smith',
                'email': 'invalid-email',
                'company': 'Beta Inc',
            },
        ]
        
        result = LeadValidator.validate_leads(leads)
        
        assert result['total'] == 2
        assert result['valid'] == 1
        assert result['invalid'] == 1
        assert len(result['valid_leads']) == 1
        assert len(result['invalid_leads']) == 1
    
    def test_sanitize_lead(self):
        """Test lead sanitization."""
        lead = {
            'first_name': '  John  ',
            'last_name': '  Doe  ',
            'email': '  JOHN@EXAMPLE.COM  ',
            'company': '  Acme Corp  ',
            'linkedin_url': 'linkedin.com/in/johndoe',
            'phone': '  555-1234  ',
        }
        
        result = LeadValidator.sanitize_lead(lead)
        
        assert result['first_name'] == 'John'
        assert result['last_name'] == 'Doe'
        assert result['email'] == 'john@example.com'
        assert result['company'] == 'Acme Corp'
        assert result['linkedin_url'] == 'https://linkedin.com/in/johndoe'
        assert result['phone'] == '5551234'
    
    def test_sanitize_lead_preserves_non_string_fields(self):
        """Test that sanitization preserves non-string fields."""
        lead = {
            'first_name': 'John',
            'priority': 'high',
            'complaint_risk': 0.5,
        }
        
        result = LeadValidator.sanitize_lead(lead)
        
        assert result['first_name'] == 'John'
        assert result['priority'] == 'high'
        assert result['complaint_risk'] == 0.5
