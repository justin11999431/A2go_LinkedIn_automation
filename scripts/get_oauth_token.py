#!/usr/bin/env python3
"""OAuth 2.0 authorization script to get refresh token for Google Sheets API."""

import os
import sys
import json
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading
import time

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    GOOGLE_AUTH_AVAILABLE = True
except ImportError:
    GOOGLE_AUTH_AVAILABLE = False

# OAuth 2.0 Configuration
# Replace these with your actual OAuth credentials
CLIENT_ID = os.getenv('OAUTH_CLIENT_ID', 'your-client-id-here')
CLIENT_SECRET = os.getenv('OAUTH_CLIENT_SECRET', 'your-client-secret-here')
REDIRECT_URI = "http://localhost:8080"
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# Token storage file
TOKEN_FILE = "oauth_token.json"


class CallbackHandler(BaseHTTPRequestHandler):
    """HTTP server to handle OAuth callback."""
    
    def do_GET(self):
        """Handle GET request for OAuth callback."""
        query = urlparse(self.path).query
        params = parse_qs(query)
        
        if 'code' in params:
            # Get authorization code
            auth_code = params['code'][0]
            
            # Send response
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"""
                <html>
                <head><title>Authorization Successful</title></head>
                <body>
                    <h1>Authorization Successful!</h1>
                    <p>You can close this window and return to the terminal.</p>
                </body>
                </html>
            """)
            
            # Store auth code for main thread
            self.server.auth_code = auth_code
        else:
            # Error response
            self.send_response(400)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"""
                <html>
                <head><title>Authorization Failed</title></head>
                <body>
                    <h1>Authorization Failed</h1>
                    <p>No authorization code received.</p>
                </body>
                </html>
            """)
    
    def log_message(self, format, *args):
        """Suppress default logging."""
        pass


def get_refresh_token():
    """Get OAuth 2.0 refresh token.
    
    Returns:
        Refresh token or None
    """
    print("="*60)
    print("Google Sheets OAuth 2.0 Authorization")
    print("="*60)
    
    if not GOOGLE_AUTH_AVAILABLE:
        print("\n❌ Error: Google Auth libraries not installed")
        print("Please run: pip install google-auth-oauthlib")
        return None
    
    # Check if credentials are set
    if CLIENT_ID == 'your-client-id-here' or CLIENT_SECRET == 'your-client-secret-here':
        print("\n❌ Error: OAuth credentials not set")
        print("Please set OAUTH_CLIENT_ID and OAUTH_CLIENT_SECRET environment variables")
        print("Or edit this script and replace the placeholder values")
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
    
    # Start local server to handle callback
    server = HTTPServer(('localhost', 8080), CallbackHandler)
    server.auth_code = None
    server_thread = threading.Thread(target=server.handle_request)
    server_thread.daemon = True
    server_thread.start()
    
    # Generate authorization URL
    auth_url, _ = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'
    )
    
    print("\n📋 Step 1: Authorize the application")
    print("-" * 60)
    print("Opening browser for authorization...")
    print(f"\nAuthorization URL:\n{auth_url}\n")
    
    # Open browser
    webbrowser.open(auth_url)
    
    print("⏳ Waiting for authorization...")
    print("   (A browser window should have opened)")
    print("   (Complete the authorization in the browser)")
    
    # Wait for callback
    timeout = 120  # 2 minutes
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        if hasattr(server, 'auth_code') and server.auth_code:
            break
        time.sleep(1)
    
    # Shutdown server
    server.shutdown()
    
    # Check if we got the code
    if not hasattr(server, 'auth_code') or not server.auth_code:
        print("\n❌ Error: Authorization timed out or failed")
        print("Please try again")
        return None
    
    print("✅ Authorization code received")
    
    # Exchange authorization code for tokens
    print("\n📋 Step 2: Exchanging authorization code for tokens...")
    print("-" * 60)
    
    try:
        flow.fetch_token(code=server.auth_code)
        credentials = flow.credentials
        
        print("✅ Tokens received successfully")
        
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
        with open(TOKEN_FILE, 'w') as f:
            json.dump(token_data, f, indent=2)
        
        print(f"\n✅ Tokens saved to: {TOKEN_FILE}")
        
        # Display refresh token
        print("\n" + "="*60)
        print("🎉 SUCCESS!")
        print("="*60)
        print(f"\nYour Refresh Token:\n{credentials.refresh_token}\n")
        print("="*60)
        print("\n📝 Next Steps:")
        print("1. Copy the refresh token above")
        print("2. Add it to GitHub as OAUTH_REFRESH_TOKEN secret")
        print("3. Keep the oauth_token.json file safe")
        print("="*60)
        
        return credentials.refresh_token
        
    except Exception as e:
        print(f"\n❌ Error exchanging tokens: {e}")
        return None


def main():
    """Main entry point."""
    refresh_token = get_refresh_token()
    
    if refresh_token:
        print("\n✅ Authorization complete!")
        print(f"Refresh token: {refresh_token}")
        sys.exit(0)
    else:
        print("\n❌ Authorization failed")
        sys.exit(1)


if __name__ == '__main__':
    main()
