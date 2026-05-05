#!/usr/bin/env python3
"""Script to print service account email from credentials."""

import os
import sys
import json

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from settings import Settings


def print_service_account_email(settings: Settings) -> dict:
    """Print service account email from credentials.
    
    Args:
        settings: Settings object
        
    Returns:
        Results
    """
    print("Getting service account email...")
    
    results = {
        'success': False,
        'email': '',
        'message': '',
    }
    
    try:
        # Get credentials
        credentials = settings.get_google_credentials()
        
        if not credentials:
            results['success'] = False
            results['message'] = 'Google credentials not found'
            print("✗ Google credentials not found")
            return results
        
        # Parse credentials
        credentials_dict = json.loads(credentials)
        
        # Get email
        email = credentials_dict.get('client_email')
        
        if not email:
            results['success'] = False
            results['message'] = 'Client email not found in credentials'
            print("✗ Client email not found in credentials")
            return results
        
        results['success'] = True
        results['email'] = email
        results['message'] = f"Service account email: {email}"
        print(f"✓ Service account email: {email}")
        
    except json.JSONDecodeError:
        results['success'] = False
        results['message'] = 'Invalid JSON in credentials'
        print("✗ Invalid JSON in credentials")
    except Exception as e:
        results['success'] = False
        results['message'] = f"Error: {e}"
        print(f"✗ Error: {e}")
    
    return results


def main():
    """Main entry point."""
    # Load settings
    settings = Settings()
    
    # Run print
    results = print_service_account_email(settings)
    
    # Print results
    print("\n" + "="*60)
    print("SERVICE ACCOUNT EMAIL")
    print("="*60)
    print(f"Success: {results['success']}")
    print(f"Email: {results['email']}")
    print(f"Message: {results['message']}")
    print("="*60 + "\n")
    
    # Exit with appropriate code
    sys.exit(0 if results['success'] else 1)


if __name__ == '__main__':
    main()
