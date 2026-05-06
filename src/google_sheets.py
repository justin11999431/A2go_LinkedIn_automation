"""Google Sheets integration for lead management and workflow tracking."""

import os
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

try:
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    from google.oauth2 import service_account
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False

logger = logging.getLogger(__name__)


class GoogleSheetsClient:
    """Client for interacting with Google Sheets API."""
    
    def __init__(self, credentials_json: Optional[str] = None, 
                 oauth_refresh_token: Optional[str] = None,
                 client_id: Optional[str] = None,
                 client_secret: Optional[str] = None):
        """Initialize Google Sheets client.
        
        Args:
            credentials_json: JSON string of service account credentials
            oauth_refresh_token: OAuth 2.0 refresh token
            client_id: OAuth 2.0 client ID
            client_secret: OAuth 2.0 client secret
        """
        if not GOOGLE_AVAILABLE:
            raise ImportError("Google API libraries not installed. Run: pip install google-api-python-client")
        
        self.credentials = None
        self.service = None
        
        if credentials_json:
            self._authenticate_service_account(credentials_json)
        elif oauth_refresh_token and client_id and client_secret:
            self._authenticate_oauth(oauth_refresh_token, client_id, client_secret)
    
    def _authenticate_service_account(self, credentials_json: str) -> None:
        """Authenticate with Google Sheets API using service account.
        
        Args:
            credentials_json: JSON string of service account credentials
        """
        try:
            credentials_dict = json.loads(credentials_json)
            self.credentials = service_account.Credentials.from_service_account_info(
                credentials_dict,
                scopes=['https://www.googleapis.com/auth/spreadsheets']
            )
            self.service = build('sheets', 'v4', credentials=self.credentials)
            logger.info("Successfully authenticated with Google Sheets API (Service Account)")
        except Exception as e:
            logger.error(f"Failed to authenticate with Google Sheets: {e}")
            raise
    
    def _authenticate_oauth(self, refresh_token: str, client_id: str, client_secret: str) -> None:
        """Authenticate with Google Sheets API using OAuth 2.0.
        
        Args:
            refresh_token: OAuth 2.0 refresh token
            client_id: OAuth 2.0 client ID
            client_secret: OAuth 2.0 client secret
        """
        try:
            # Create credentials from refresh token
            self.credentials = Credentials(
                token=None,
                refresh_token=refresh_token,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=client_id,
                client_secret=client_secret,
                scopes=['https://www.googleapis.com/auth/spreadsheets']
            )
            
            # Refresh the token
            self.credentials.refresh(Request())
            
            # Build service
            self.service = build('sheets', 'v4', credentials=self.credentials)
            logger.info("Successfully authenticated with Google Sheets API (OAuth 2.0)")
        except Exception as e:
            logger.error(f"Failed to authenticate with Google Sheets OAuth: {e}")
            raise
    
    def get_sheet_data(self, sheet_id: str, range_name: str) -> List[List[Any]]:
        """Get data from a Google Sheet.
        
        Args:
            sheet_id: Google Sheet ID
            range_name: Range to read (e.g., 'Sheet1!A1:Z1000')
            
        Returns:
            List of rows, where each row is a list of values
        """
        if not self.service:
            raise RuntimeError("Not authenticated. Call _authenticate() first.")
        
        try:
            sheet = self.service.spreadsheets()
            result = sheet.values().get(
                spreadsheetId=sheet_id,
                range=range_name
            ).execute()
            
            values = result.get('values', [])
            logger.info(f"Retrieved {len(values)} rows from sheet {sheet_id}")
            return values
        except HttpError as e:
            logger.error(f"Error reading sheet {sheet_id}: {e}")
            raise
    
    def update_sheet_data(self, sheet_id: str, range_name: str, values: List[List[Any]]) -> None:
        """Update data in a Google Sheet.
        
        Args:
            sheet_id: Google Sheet ID
            range_name: Range to update (e.g., 'Sheet1!A1:Z1000')
            values: Data to write
        """
        if not self.service:
            raise RuntimeError("Not authenticated. Call _authenticate() first.")
        
        try:
            body = {'values': values}
            sheet = self.service.spreadsheets()
            result = sheet.values().update(
                spreadsheetId=sheet_id,
                range=range_name,
                valueInputOption='RAW',
                body=body
            ).execute()
            
            logger.info(f"Updated {result.get('updatedRows')} rows in sheet {sheet_id}")
        except HttpError as e:
            logger.error(f"Error updating sheet {sheet_id}: {e}")
            raise
    
    def append_sheet_data(self, sheet_id: str, range_name: str, values: List[List[Any]]) -> None:
        """Append data to a Google Sheet.
        
        Args:
            sheet_id: Google Sheet ID
            range_name: Range to append to (e.g., 'Sheet1!A1')
            values: Data to append
        """
        if not self.service:
            raise RuntimeError("Not authenticated. Call _authenticate() first.")
        
        try:
            body = {'values': values}
            sheet = self.service.spreadsheets()
            result = sheet.values().append(
                spreadsheetId=sheet_id,
                range=range_name,
                valueInputOption='RAW',
                body=body
            ).execute()
            
            logger.info(f"Appended {result.get('updates').get('updatedRows')} rows to sheet {sheet_id}")
        except HttpError as e:
            logger.error(f"Error appending to sheet {sheet_id}: {e}")
            raise
    
    def batch_update(self, sheet_id: str, requests: List[Dict[str, Any]]) -> None:
        """Execute batch update on Google Sheet.
        
        Args:
            sheet_id: Google Sheet ID
            requests: List of update requests
        """
        if not self.service:
            raise RuntimeError("Not authenticated. Call _authenticate() first.")
        
        try:
            body = {'requests': requests}
            sheet = self.service.spreadsheets()
            sheet.batchUpdate(spreadsheetId=sheet_id, body=body).execute()
            logger.info(f"Executed batch update with {len(requests)} requests")
        except HttpError as e:
            logger.error(f"Error in batch update: {e}")
            raise
