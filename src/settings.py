"""Settings management for the automation system."""

import os
import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class Settings:
    """Manages application settings."""
    
    # Default settings
    DEFAULT_SETTINGS = {
        'google': {
            'service_account_json': '',
            'source_sheet_id': '',
            'workflow_sheet_id': '',
        },
        'salesrobot': {
            'api_key': '',
            'base_url': 'https://api.salesrobot.io/v1',
        },
        'automation': {
            'timezone': 'America/Los_Angeles',
            'dry_run': True,
            'batch_size': 50,
            'max_retries': 3,
            'retry_delay': 5,
        },
        'limits': {
            'max_leads_per_day': 100,
            'max_messages_per_day': 200,
            'max_connection_requests_per_day': 20,
            'max_follow_up_messages_per_day': 20,
            'max_voice_messages_per_day': 20,
            'max_video_messages_per_day': 20,
            'max_profile_views_per_day': 20,
            'max_inmail_messages_per_day': 20,
            'max_profile_follows_per_day': 20,
            'max_post_likes_comments_per_day': 20,
            'max_endorsements_per_day': 20,
            'max_withdraw_connection_requests_per_day': 10,
            'max_invite_to_event_per_day': 30,
        },
        'scheduling': {
            'monday_start_time': '08:07',
            'daily_ping_time': '08:17',
            'dashboard_refresh_time': '09:00',
        },
        'limits': {
            'max_leads_per_day': 100,
            'max_messages_per_day': 200,
            'max_connection_requests_per_day': 50,
        },
        'notifications': {
            'enabled': True,
            'email_on_error': True,
            'email_on_completion': True,
            'slack_webhook_url': '',
        },
        'logging': {
            'level': 'INFO',
            'file': 'automation.log',
            'max_size': 10485760,  # 10MB
            'backup_count': 5,
        },
    }
    
    def __init__(self, settings_file: Optional[str] = None):
        """Initialize settings.
        
        Args:
            settings_file: Path to settings file (JSON)
        """
        self.settings_file = settings_file or self._get_default_settings_file()
        self.settings = self._load_settings()
    
    def _get_default_settings_file(self) -> str:
        """Get default settings file path.
        
        Returns:
            Path to settings file
        """
        # Check for settings file in current directory
        current_dir = Path.cwd()
        settings_file = current_dir / 'settings.json'
        
        if settings_file.exists():
            return str(settings_file)
        
        # Check for settings file in user home
        home_dir = Path.home()
        settings_file = home_dir / '.a2go_automation' / 'settings.json'
        
        return str(settings_file)
    
    def _load_settings(self) -> Dict[str, Any]:
        """Load settings from file or use defaults.
        
        Returns:
            Settings dictionary
        """
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r') as f:
                    loaded_settings = json.load(f)
                
                # Merge with defaults
                settings = self._merge_settings(self.DEFAULT_SETTINGS, loaded_settings)
                logger.info(f"Loaded settings from {self.settings_file}")
                return settings
            except Exception as e:
                logger.error(f"Error loading settings: {e}")
                return self.DEFAULT_SETTINGS.copy()
        else:
            logger.info("Using default settings")
            return self.DEFAULT_SETTINGS.copy()
    
    def _merge_settings(self, defaults: Dict[str, Any], loaded: Dict[str, Any]) -> Dict[str, Any]:
        """Merge loaded settings with defaults.
        
        Args:
            defaults: Default settings
            loaded: Loaded settings
            
        Returns:
            Merged settings
        """
        merged = defaults.copy()
        
        for key, value in loaded.items():
            if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                merged[key] = self._merge_settings(merged[key], value)
            else:
                merged[key] = value
        
        return merged
    
    def save_settings(self) -> None:
        """Save settings to file."""
        try:
            # Create directory if it doesn't exist
            settings_dir = os.path.dirname(self.settings_file)
            if settings_dir and not os.path.exists(settings_dir):
                os.makedirs(settings_dir)
            
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
            
            logger.info(f"Saved settings to {self.settings_file}")
        except Exception as e:
            logger.error(f"Error saving settings: {e}")
            raise
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get setting value.
        
        Args:
            key: Setting key (supports dot notation, e.g., 'google.service_account_json')
            default: Default value if key not found
            
        Returns:
            Setting value
        """
        keys = key.split('.')
        value = self.settings
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """Set setting value.
        
        Args:
            key: Setting key (supports dot notation, e.g., 'google.service_account_json')
            value: Value to set
        """
        keys = key.split('.')
        settings = self.settings
        
        for k in keys[:-1]:
            if k not in settings:
                settings[k] = {}
            settings = settings[k]
        
        settings[keys[-1]] = value
    
    def get_google_credentials(self) -> Optional[str]:
        """Get Google service account credentials.
        
        Returns:
            Google service account JSON string or None
        """
        # Check environment variable first
        env_creds = os.getenv('GOOGLE_SERVICE_ACCOUNT_JSON')
        if env_creds:
            return env_creds
        
        # Check settings file
        return self.get('google.service_account_json')
    
    def get_oauth_refresh_token(self) -> Optional[str]:
        """Get OAuth 2.0 refresh token.
        
        Returns:
            OAuth refresh token or None
        """
        # Check environment variable first
        env_token = os.getenv('OAUTH_REFRESH_TOKEN')
        if env_token:
            return env_token
        
        # Check settings file
        return self.get('google.oauth_refresh_token')
    
    def get_oauth_client_id(self) -> Optional[str]:
        """Get OAuth 2.0 client ID.
        
        Returns:
            OAuth client ID or None
        """
        # Check environment variable first
        env_id = os.getenv('OAUTH_CLIENT_ID')
        if env_id:
            return env_id
        
        # Check settings file
        return self.get('google.oauth_client_id')
    
    def get_oauth_client_secret(self) -> Optional[str]:
        """Get OAuth 2.0 client secret.
        
        Returns:
            OAuth client secret or None
        """
        # Check environment variable first
        env_secret = os.getenv('OAUTH_CLIENT_SECRET')
        if env_secret:
            return env_secret
        
        # Check settings file
        return self.get('google.oauth_client_secret')
    
    def get_salesrobot_api_key(self) -> Optional[str]:
        """Get Salesrobot API key.
        
        Returns:
            Salesrobot API key or None
        """
        # Check environment variable first
        env_key = os.getenv('SALESROBOT_API_KEY')
        if env_key:
            return env_key
        
        # Check settings file
        return self.get('salesrobot.api_key')
    
    def get_linkedin_account_uuid(self) -> Optional[str]:
        """Get LinkedIn account UUID.
        
        Returns:
            LinkedIn account UUID or None
        """
        # Check environment variable first
        env_uuid = os.getenv('LINKEDIN_ACCOUNT_UUID')
        if env_uuid:
            return env_uuid
        
        # Check settings file
        return self.get('salesrobot.linkedin_account_uuid')
    
    def get_source_sheet_id(self) -> Optional[str]:
        """Get source Google Sheet ID.
        
        Returns:
            Source sheet ID or None
        """
        # Check environment variable first
        env_id = os.getenv('SOURCE_LEAD_SHEET_ID')
        if env_id:
            return env_id
        
        # Check settings file
        return self.get('google.source_sheet_id')
    
    def get_workflow_sheet_id(self) -> Optional[str]:
        """Get workflow Google Sheet ID.
        
        Returns:
            Workflow sheet ID or None
        """
        # Check environment variable first
        env_id = os.getenv('WORKFLOW_SHEET_ID')
        if env_id:
            return env_id
        
        # Check settings file
        return self.get('google.workflow_sheet_id')
    
    def is_dry_run(self) -> bool:
        """Check if running in dry-run mode.
        
        Returns:
            True if dry-run mode
        """
        return self.get('automation.dry_run', True)
    
    def get_timezone(self) -> str:
        """Get timezone setting.
        
        Returns:
            Timezone string
        """
        return self.get('automation.timezone', 'America/Los_Angeles')
    
    def get_limits(self) -> Dict[str, Any]:
        """Get all limits.
        
        Returns:
            Dictionary of all limits
        """
        return self.get('limits', {})
    
    def get_limit(self, limit_name: str, default: Any = None) -> Any:
        """Get specific limit.
        
        Args:
            limit_name: Name of the limit
            default: Default value if limit not found
            
        Returns:
            Limit value
        """
        return self.get(f'limits.{limit_name}', default)
