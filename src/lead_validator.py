"""Lead validator for ensuring data quality and completeness."""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import re

logger = logging.getLogger(__name__)


class LeadValidator:
    """Validates lead data for quality and completeness."""
    
    # Required fields for a valid lead
    REQUIRED_FIELDS = [
        'first_name',
        'last_name',
        'email',
        'company',
    ]
    
    # Optional but recommended fields
    RECOMMENDED_FIELDS = [
        'title',
        'linkedin_url',
        'industry',
        'location',
    ]
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format.
        
        Args:
            email: Email address
            
        Returns:
            True if valid, False otherwise
        """
        if not email:
            return False
        
        # Basic email regex pattern
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_linkedin_url(url: str) -> bool:
        """Validate LinkedIn URL format.
        
        Args:
            url: LinkedIn URL
            
        Returns:
            True if valid, False otherwise
        """
        if not url:
            return True  # Optional field
        
        # Basic LinkedIn URL pattern
        pattern = r'^https?://(www\.)?linkedin\.com/in/[\w-]+/?$'
        return re.match(pattern, url) is not None
    
    @staticmethod
    def validate_phone(phone: str) -> bool:
        """Validate phone number format.
        
        Args:
            phone: Phone number
            
        Returns:
            True if valid, False otherwise
        """
        if not phone:
            return True  # Optional field
        
        # Remove common separators
        cleaned = re.sub(r'[\s\-\(\)\.]', '', phone)
        
        # Check if it's a valid phone number (10-15 digits)
        return cleaned.isdigit() and 10 <= len(cleaned) <= 15
    
    @classmethod
    def validate_lead(cls, lead: Dict[str, Any]) -> Dict[str, Any]:
        """Validate lead data.
        
        Args:
            lead: Lead data to validate
            
        Returns:
            Validation result with 'valid' boolean and 'errors' list
        """
        errors = []
        warnings = []
        
        # Check required fields
        for field in cls.REQUIRED_FIELDS:
            if field not in lead or not lead[field]:
                errors.append(f"Missing required field: {field}")
        
        # Check email format if present
        if 'email' in lead and lead['email']:
            if not cls.validate_email(lead['email']):
                errors.append(f"Invalid email format: {lead['email']}")
        
        # Check LinkedIn URL format if present
        if 'linkedin_url' in lead and lead['linkedin_url']:
            if not cls.validate_linkedin_url(lead['linkedin_url']):
                warnings.append(f"Invalid LinkedIn URL format: {lead['linkedin_url']}")
        
        # Check phone format if present
        if 'phone' in lead and lead['phone']:
            if not cls.validate_phone(lead['phone']):
                warnings.append(f"Invalid phone format: {lead['phone']}")
        
        # Check recommended fields
        for field in cls.RECOMMENDED_FIELDS:
            if field not in lead or not lead[field]:
                warnings.append(f"Missing recommended field: {field}")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
        }
    
    @classmethod
    def validate_leads(cls, leads: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate multiple leads.
        
        Args:
            leads: List of leads to validate
            
        Returns:
            Validation summary with valid/invalid counts and details
        """
        valid_leads = []
        invalid_leads = []
        all_errors = []
        all_warnings = []
        
        for i, lead in enumerate(leads):
            result = cls.validate_lead(lead)
            
            if result['valid']:
                valid_leads.append(lead)
            else:
                invalid_leads.append({
                    'index': i,
                    'lead': lead,
                    'errors': result['errors'],
                    'warnings': result['warnings'],
                })
            
            all_errors.extend([f"Lead {i}: {error}" for error in result['errors']])
            all_warnings.extend([f"Lead {i}: {warning}" for warning in result['warnings']])
        
        return {
            'total': len(leads),
            'valid': len(valid_leads),
            'invalid': len(invalid_leads),
            'valid_leads': valid_leads,
            'invalid_leads': invalid_leads,
            'all_errors': all_errors,
            'all_warnings': all_warnings,
        }
    
    @classmethod
    def sanitize_lead(cls, lead: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize lead data by cleaning and normalizing fields.
        
        Args:
            lead: Lead data to sanitize
            
        Returns:
            Sanitized lead data
        """
        sanitized = lead.copy()
        
        # Trim whitespace from string fields
        for key, value in sanitized.items():
            if isinstance(value, str):
                sanitized[key] = value.strip()
        
        # Normalize email to lowercase
        if 'email' in sanitized and sanitized['email']:
            sanitized['email'] = sanitized['email'].lower()
        
        # Normalize LinkedIn URL
        if 'linkedin_url' in sanitized and sanitized['linkedin_url']:
            url = sanitized['linkedin_url'].strip()
            if not url.startswith('http'):
                url = 'https://' + url
            sanitized['linkedin_url'] = url
        
        # Normalize phone number
        if 'phone' in sanitized and sanitized['phone']:
            phone = re.sub(r'[\s\-\(\)\.]', '', sanitized['phone'])
            sanitized['phone'] = phone
        
        return sanitized
