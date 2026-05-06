#!/usr/bin/env python3
"""Preflight check script to verify system configuration and access."""

import os
import sys
import json
import logging
from datetime import datetime

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from google_sheets import GoogleSheetsClient
from salesrobot_client import SalesrobotClient
from settings import Settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def check_google_credentials(settings: Settings) -> dict:
    """Check Google credentials.
    
    Args:
        settings: Settings object
        
    Returns:
        Check result
    """
    logger.info("Checking Google credentials...")
    
    # Check for service account credentials
    credentials = settings.get_google_credentials()
    
    # Check for OAuth credentials
    oauth_refresh_token = settings.get_oauth_refresh_token()
    oauth_client_id = settings.get_oauth_client_id()
    oauth_client_secret = settings.get_oauth_client_secret()
    
    # Determine which authentication method to use
    if credentials:
        # Service account authentication
        try:
            credentials_dict = json.loads(credentials)
            required_fields = ['type', 'project_id', 'private_key_id', 'private_key', 'client_email']
            
            for field in required_fields:
                if field not in credentials_dict:
                    return {
                        'status': 'FAIL',
                        'message': f'Missing required field in credentials: {field}',
                        'details': 'Ensure your service account JSON is complete'
                    }
            
            return {
                'status': 'PASS',
                'message': 'Google service account credentials valid',
                'details': f'Service account: {credentials_dict.get("client_email", "unknown")}'
            }
        except json.JSONDecodeError:
            return {
                'status': 'FAIL',
                'message': 'Invalid JSON in credentials',
                'details': 'Ensure GOOGLE_SERVICE_ACCOUNT_JSON is valid JSON'
            }
    
    elif oauth_refresh_token and oauth_client_id and oauth_client_secret:
        # OAuth 2.0 authentication
        return {
            'status': 'PASS',
            'message': 'Google OAuth 2.0 credentials valid',
            'details': f'Client ID: {oauth_client_id[:20]}...'
        }
    
    else:
        return {
            'status': 'FAIL',
            'message': 'Google credentials not found',
            'details': 'Set GOOGLE_SERVICE_ACCOUNT_JSON or OAuth credentials (OAUTH_REFRESH_TOKEN, OAUTH_CLIENT_ID, OAUTH_CLIENT_SECRET)'
        }


def check_salesrobot_api_key(settings: Settings) -> dict:
    """Check Salesrobot API key.
    
    Args:
        settings: Settings object
        
    Returns:
        Check result
    """
    logger.info("Checking Salesrobot API key...")
    
    api_key = settings.get_salesrobot_api_key()
    
    if not api_key:
        return {
            'status': 'FAIL',
            'message': 'Salesrobot API key not found',
            'details': 'Set SALESROBOT_API_KEY environment variable or configure in settings.json'
        }
    
    if len(api_key) < 10:
        return {
            'status': 'FAIL',
            'message': 'Invalid API key format',
            'details': 'API key should be at least 10 characters'
        }
    
    return {
        'status': 'PASS',
        'message': 'Salesrobot API key valid',
        'details': f'API key: {api_key[:8]}...{api_key[-4:]}'
    }


def check_google_sheets_access(settings: Settings) -> dict:
    """Check access to Google Sheets.
    
    Args:
        settings: Settings object
        
    Returns:
        Check result
    """
    logger.info("Checking Google Sheets access...")
    
    source_sheet_id = settings.get_source_sheet_id()
    workflow_sheet_id = settings.get_workflow_sheet_id()
    
    if not source_sheet_id:
        return {
            'status': 'FAIL',
            'message': 'Source sheet ID not found',
            'details': 'Set SOURCE_LEAD_SHEET_ID environment variable or configure in settings.json'
        }
    
    if not workflow_sheet_id:
        return {
            'status': 'FAIL',
            'message': 'Workflow sheet ID not found',
            'details': 'Set WORKFLOW_SHEET_ID environment variable or configure in settings.json'
        }
    
    try:
        # Try service account first
        credentials = settings.get_google_credentials()
        
        # Try OAuth if service account not available
        oauth_refresh_token = settings.get_oauth_refresh_token()
        oauth_client_id = settings.get_oauth_client_id()
        oauth_client_secret = settings.get_oauth_client_secret()
        
        if credentials:
            client = GoogleSheetsClient(credentials_json=credentials)
        elif oauth_refresh_token and oauth_client_id and oauth_client_secret:
            client = GoogleSheetsClient(
                oauth_refresh_token=oauth_refresh_token,
                client_id=oauth_client_id,
                client_secret=oauth_client_secret
            )
        else:
            return {
                'status': 'FAIL',
                'message': 'No Google credentials available',
                'details': 'Set GOOGLE_SERVICE_ACCOUNT_JSON or OAuth credentials'
            }
        
        # Test access to source sheet
        source_data = client.get_sheet_data(source_sheet_id, 'A2go-Forecast-Intent-75!A1:Z1')
        
        # Test access to workflow sheet
        workflow_data = client.get_sheet_data(workflow_sheet_id, 'Sheet1!A1:Z1')
        
        return {
            'status': 'PASS',
            'message': 'Google Sheets access verified',
            'details': f'Source sheet: {len(source_data)} columns, Workflow sheet: {len(workflow_data)} columns'
        }
    except Exception as e:
        return {
            'status': 'FAIL',
            'message': 'Failed to access Google Sheets',
            'details': str(e)
        }


def check_salesrobot_api_access(settings: Settings) -> dict:
    """Check access to Salesrobot API.
    
    Args:
        settings: Settings object
        
    Returns:
        Check result
    """
    logger.info("Checking Salesrobot API access...")
    
    try:
        api_key = settings.get_salesrobot_api_key()
        linkedin_account_uuid = settings.get_linkedin_account_uuid()
        
        if not linkedin_account_uuid:
            return {
                'status': 'FAIL',
                'message': 'LinkedIn account UUID not found',
                'details': 'Set LINKEDIN_ACCOUNT_UUID environment variable or configure in settings.json'
            }
        
        client = SalesrobotClient(api_key, linkedin_account_uuid)
        
        # Test API access by getting campaigns
        campaigns = client.get_campaigns()
        
        return {
            'status': 'PASS',
            'message': 'Salesrobot API access verified',
            'details': f'Found {len(campaigns)} campaigns'
        }
    except Exception as e:
        return {
            'status': 'FAIL',
            'message': 'Failed to access Salesrobot API',
            'details': str(e)
        }


def check_configuration(settings: Settings) -> dict:
    """Check system configuration.
    
    Args:
        settings: Settings object
        
    Returns:
        Check result
    """
    logger.info("Checking system configuration...")
    
    checks = []
    
    # Check timezone
    timezone = settings.get_timezone()
    checks.append(f'Timezone: {timezone}')
    
    # Check dry run mode
    dry_run = settings.is_dry_run()
    checks.append(f'Dry run mode: {dry_run}')
    
    # Check batch size
    batch_size = settings.get('automation.batch_size', 50)
    checks.append(f'Batch size: {batch_size}')
    
    return {
        'status': 'PASS',
        'message': 'Configuration valid',
        'details': ', '.join(checks)
    }


def run_preflight_check() -> dict:
    """Run all preflight checks.
    
    Returns:
        Preflight check results
    """
    logger.info("Starting preflight check...")
    
    results = {
        'timestamp': datetime.now().isoformat(),
        'checks': [],
        'summary': {
            'total': 0,
            'passed': 0,
            'failed': 0,
        }
    }
    
    # Load settings
    settings = Settings()
    
    # Run checks
    checks = [
        ('Google Credentials', check_google_credentials, settings),
        ('Salesrobot API Key', check_salesrobot_api_key, settings),
        ('Google Sheets Access', check_google_sheets_access, settings),
        ('Salesrobot API Access', check_salesrobot_api_access, settings),
        ('Configuration', check_configuration, settings),
    ]
    
    for check_name, check_func, check_args in checks:
        result = check_func(check_args)
        result['check'] = check_name
        results['checks'].append(result)
        results['summary']['total'] += 1
        
        if result['status'] == 'PASS':
            results['summary']['passed'] += 1
        else:
            results['summary']['failed'] += 1
    
    # Determine overall status
    results['status'] = 'PASS' if results['summary']['failed'] == 0 else 'FAIL'
    
    logger.info(f"Preflight check complete: {results['summary']['passed']}/{results['summary']['total']} passed")
    
    return results


def main():
    """Main entry point."""
    results = run_preflight_check()
    
    # Print results
    print("\n" + "="*60)
    print("PREFLIGHT CHECK RESULTS")
    print("="*60)
    print(f"Status: {results['status']}")
    print(f"Timestamp: {results['timestamp']}")
    print(f"Summary: {results['summary']['passed']}/{results['summary']['total']} passed")
    print("\n")
    
    for check in results['checks']:
        status_symbol = "[PASS]" if check['status'] == 'PASS' else "[FAIL]"
        print(f"{status_symbol} {check['check']}: {check['message']}")
        if check['status'] == 'FAIL':
            print(f"  Details: {check['details']}")
    
    print("\n" + "="*60)
    
    # Exit with appropriate code
    sys.exit(0 if results['status'] == 'PASS' else 1)


if __name__ == '__main__':
    main()
