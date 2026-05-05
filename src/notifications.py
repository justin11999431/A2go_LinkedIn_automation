"""Notification system for automation events and alerts."""

import logging
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

logger = logging.getLogger(__name__)


class NotificationType(Enum):
    """Types of notifications."""
    
    # Success notifications
    TASK_COMPLETED = "task_completed"
    MILESTONE_REACHED = "milestone_reached"
    
    # Warning notifications
    WARNING = "warning"
    RATE_LIMIT_WARNING = "rate_limit_warning"
    
    # Error notifications
    ERROR = "error"
    CRITICAL_ERROR = "critical_error"
    
    # Info notifications
    INFO = "info"
    STATUS_UPDATE = "status_update"


class NotificationPriority(Enum):
    """Priority levels for notifications."""
    
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class NotificationChannel(Enum):
    """Notification channels."""
    
    EMAIL = "email"
    SLACK = "slack"
    WEBHOOK = "webhook"
    LOG = "log"


class Notification:
    """Represents a notification."""
    
    def __init__(self, notification_type: NotificationType, title: str, 
                 message: str, priority: NotificationPriority = NotificationPriority.MEDIUM,
                 metadata: Optional[Dict[str, Any]] = None):
        """Initialize notification.
        
        Args:
            notification_type: Type of notification
            title: Notification title
            message: Notification message
            priority: Notification priority
            metadata: Additional metadata
        """
        self.type = notification_type
        self.title = title
        self.message = message
        self.priority = priority
        self.metadata = metadata or {}
        self.timestamp = datetime.now().isoformat()
        self.sent = False
        self.channels = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert notification to dictionary.
        
        Returns:
            Dictionary representation
        """
        return {
            'type': self.type.value,
            'title': self.title,
            'message': self.message,
            'priority': self.priority.value,
            'metadata': self.metadata,
            'timestamp': self.timestamp,
            'sent': self.sent,
            'channels': self.channels,
        }


class NotificationManager:
    """Manages notification sending and routing."""
    
    def __init__(self, settings: Optional[Dict[str, Any]] = None):
        """Initialize notification manager.
        
        Args:
            settings: Notification settings
        """
        self.settings = settings or {}
        self.notifications = []
        self.enabled = self.settings.get('enabled', True)
        
        # Channel configurations
        self.email_enabled = self.settings.get('email_on_error', True)
        self.slack_webhook_url = self.settings.get('slack_webhook_url', '')
        self.webhook_url = self.settings.get('webhook_url', '')
    
    def create_notification(self, notification_type: NotificationType, title: str, 
                          message: str, priority: NotificationPriority = NotificationPriority.MEDIUM,
                          metadata: Optional[Dict[str, Any]] = None) -> Notification:
        """Create a notification.
        
        Args:
            notification_type: Type of notification
            title: Notification title
            message: Notification message
            priority: Notification priority
            metadata: Additional metadata
            
        Returns:
            Notification object
        """
        notification = Notification(notification_type, title, message, priority, metadata)
        self.notifications.append(notification)
        return notification
    
    def send_notification(self, notification: Notification, 
                          channels: Optional[List[NotificationChannel]] = None) -> bool:
        """Send notification through specified channels.
        
        Args:
            notification: Notification to send
            channels: Channels to send through (default: all configured)
            
        Returns:
            True if sent successfully
        """
        if not self.enabled:
            logger.info("Notifications disabled, skipping")
            return False
        
        if channels is None:
            channels = self._get_default_channels(notification)
        
        success = True
        
        for channel in channels:
            try:
                if channel == NotificationChannel.EMAIL:
                    self._send_email(notification)
                elif channel == NotificationChannel.SLACK:
                    self._send_slack(notification)
                elif channel == NotificationChannel.WEBHOOK:
                    self._send_webhook(notification)
                elif channel == NotificationChannel.LOG:
                    self._log_notification(notification)
                
                notification.channels.append(channel.value)
                logger.info(f"Sent notification via {channel.value}")
            except Exception as e:
                logger.error(f"Failed to send notification via {channel.value}: {e}")
                success = False
        
        notification.sent = success
        return success
    
    def _get_default_channels(self, notification: Notification) -> List[NotificationChannel]:
        """Get default channels for notification type.
        
        Args:
            notification: Notification
            
        Returns:
            List of default channels
        """
        channels = [NotificationChannel.LOG]
        
        # Add email for errors
        if notification.type in [NotificationType.ERROR, NotificationType.CRITICAL_ERROR]:
            if self.email_enabled:
                channels.append(NotificationChannel.EMAIL)
        
        # Add Slack if configured
        if self.slack_webhook_url:
            channels.append(NotificationChannel.SLACK)
        
        # Add webhook if configured
        if self.webhook_url:
            channels.append(NotificationChannel.WEBHOOK)
        
        return channels
    
    def _send_email(self, notification: Notification) -> None:
        """Send notification via email.
        
        Args:
            notification: Notification to send
        """
        # Placeholder for email sending logic
        # In production, integrate with email service (SendGrid, AWS SES, etc.)
        logger.info(f"Email notification: {notification.title} - {notification.message}")
    
    def _send_slack(self, notification: Notification) -> None:
        """Send notification via Slack webhook.
        
        Args:
            notification: Notification to send
        """
        if not REQUESTS_AVAILABLE:
            logger.warning("Requests library not available, cannot send Slack notification")
            return
        
        if not self.slack_webhook_url:
            logger.warning("Slack webhook URL not configured")
            return
        
        payload = {
            'text': f"*{notification.title}*",
            'attachments': [{
                'color': self._get_slack_color(notification.priority),
                'text': notification.message,
                'fields': [
                    {'title': 'Priority', 'value': notification.priority.value, 'short': True},
                    {'title': 'Type', 'value': notification.type.value, 'short': True},
                ],
                'footer': f"Sent at {notification.timestamp}",
            }]
        }
        
        response = requests.post(self.slack_webhook_url, json=payload, timeout=10)
        response.raise_for_status()
    
    def _send_webhook(self, notification: Notification) -> None:
        """Send notification via webhook.
        
        Args:
            notification: Notification to send
        """
        if not REQUESTS_AVAILABLE:
            logger.warning("Requests library not available, cannot send webhook notification")
            return
        
        if not self.webhook_url:
            logger.warning("Webhook URL not configured")
            return
        
        payload = notification.to_dict()
        
        response = requests.post(self.webhook_url, json=payload, timeout=10)
        response.raise_for_status()
    
    def _log_notification(self, notification: Notification) -> None:
        """Log notification.
        
        Args:
            notification: Notification to log
        """
        log_level = self._get_log_level(notification.priority)
        logger.log(log_level, f"Notification: {notification.title} - {notification.message}")
    
    def _get_slack_color(self, priority: NotificationPriority) -> str:
        """Get Slack color for priority.
        
        Args:
            priority: Notification priority
            
        Returns:
            Slack color code
        """
        color_map = {
            NotificationPriority.LOW: '#36a64f',  # green
            NotificationPriority.MEDIUM: '#ff9900',  # orange
            NotificationPriority.HIGH: '#ff0000',  # red
            NotificationPriority.URGENT: '#000000',  # black
        }
        return color_map.get(priority, '#ff9900')
    
    def _get_log_level(self, priority: NotificationPriority) -> int:
        """Get log level for priority.
        
        Args:
            priority: Notification priority
            
        Returns:
            Log level constant
        """
        level_map = {
            NotificationPriority.LOW: logging.INFO,
            NotificationPriority.MEDIUM: logging.WARNING,
            NotificationPriority.HIGH: logging.ERROR,
            NotificationPriority.URGENT: logging.CRITICAL,
        }
        return level_map.get(priority, logging.WARNING)
    
    def get_notifications(self, limit: Optional[int] = None) -> List[Notification]:
        """Get notifications.
        
        Args:
            limit: Maximum number of notifications to return
            
        Returns:
            List of notifications
        """
        if limit:
            return self.notifications[-limit:]
        return self.notifications.copy()
    
    def clear_notifications(self) -> None:
        """Clear all notifications."""
        self.notifications = []
        logger.info("Cleared all notifications")
