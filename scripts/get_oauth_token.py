#!/usr/bin/env python3
"""OAuth 2.0 authorization script to get refresh token for Google Sheets API."""

import os
import sys
import json
import webbrowser

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    GOOGLE_AUTH_AVAILABLE = True
except ImportError:
    GOOGLE_AUTH_AVAILABLE = False

# OAuth 2.0 Configuration
CLIENT_ID = os.getenv('OAUTH_CLIENT_ID', '')
CLIENT_SECRET = os.getenv('OAUTH_CLIENT_SECRET', '')
REDIRECT_URI = "http://localhost:8080"
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# Token storage file
TOKEN_FILE = "oauth_token.json"


def get_refresh_token():
    """Get OAuth 2.0 refresh token.
    
    Returns:
        Refresh token or None
    """
    print("="*60)
    print("Google Sheets OAuth 2.0 Authorization")
    print("="*60)
    
    if not GOOGLE_AUTH_AVAILABLE:
        print("\nError: Google Auth libraries not installed")
        print("Please run: pip install google-auth-oauthlib")
        return None
    
    # Create OAuth flow
    client_config = {
        "installed": {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [REDIRECT_URI]
        }
    }
    
    flow = InstalledAppFlow.from_client_config(
        client_config,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )
    
    # Generate authorization URL
    auth_url, _ = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'
    )
    
    print("\nStep 1: Authorize the application")
    print("-" * 60)
    print("Opening browser for authorization...")
    print(f"\nAuthorization URL:\n{auth_url}\n")
    
    # Open browser
    webbrowser.open(auth_url)
    
    print("After authorizing in the browser:")
    print("1. You will be redirected to a page that shows 'Authorization Successful'")
    print("2. Look at the URL in your browser address bar")
    print("3. Copy the 'code' parameter from the URL")
    print("4. Paste it below")
    print("\nExample URL: http://localhost:8080/?code=4/0AeoWuM-AZsPnR0aDU7BoRkho43704nYP0fNfE9KRmTyIZBGcPsbac2vJa5hGqmRhSH4c5g&scope=...")
    print("\nPaste the code here:")
    
    # Get authorization code from user
    auth_code = input().strip()
    
    if not auth_code:
        print("\nError: No authorization code provided")
        return None
    
    print("\nAuthorization code received")
    
    # Exchange authorization code for tokens
    print("\nStep 2: Exchanging authorization code for tokens...")
    print("-" * 60)
    
    try:
        flow.fetch_token(code=auth_code)
        credentials = flow.credentials
        
        print("Tokens received successfully")
        
        # Save credentials
        token_data = {
            "token": credentials.token,
            "refresh_token": credentials.refresh_token,
            "token_uri": credentials.token_uri,
            "client_id": credentials.client_id,
            "client_secret": credentials.client_secret,
            "scopes": credentials.scopes,
            "expiry": credentials.expiry.isoformat() if credentials.expiry else None
        }
        
        # Save to file
        token_path = os.path.join(os.path.dirname(__file__), '..', TOKEN_FILE)
        with open(token_path, 'w') as f:
            json.dump(token_data, f, indent=2)
        
        print(f"\nTokens saved to: {token_path}")
        
        # Display refresh token
        print("\n" + "="*60)
        print("SUCCESS!")
        print("="*60)
        print(f"\nYour Refresh Token:\n{credentials.refresh_token}\n")
        print("="*60)
        print("\nNext Steps:")
        print("1. Copy the refresh token above")
        print("2. Add it to GitHub as OAUTH_REFRESH_TOKEN secret")
        print("3. Keep the oauth_token.json file safe")
        print("="*60)
        
        return credentials.refresh_token
        
    except Exception as e:
        print(f"\nError exchanging tokens: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """Main entry point."""
    # Check for required credentials
    if not CLIENT_ID or not CLIENT_SECRET:
        print("Error: OAuth credentials not provided")
        print("Please set OAUTH_CLIENT_ID and OAUTH_CLIENT_SECRET environment variables")
        sys.exit(1)
    
    refresh_token = get_refresh_token()
    
    if refresh_token:
        print("\nAuthorization complete!")
        print(f"Refresh token: {refresh_token}")
        sys.exit(0)
    else:
        print("\nAuthorization failed")
        sys.exit(1)


if __name__ == '__main__':
    main()
