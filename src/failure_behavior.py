"""Failure behavior handling for automation system."""

import logging
from typing import Dict, Any, Optional, Callable
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class FailureType(Enum):
    """Types of failures that can occur."""
    
    # Authentication failures
    AUTHENTICATION_ERROR = "authentication_error"
    AUTHORIZATION_ERROR = "authorization_error"
    
    # API failures
    API_ERROR = "api_error"
    RATE_LIMIT_ERROR = "rate_limit_error"
    TIMEOUT_ERROR = "timeout_error"
    
    # Data failures
    DATA_VALIDATION_ERROR = "data_validation_error"
    DATA_CONFLICT_ERROR = "data_conflict_error"
    DATA_NOT_FOUND_ERROR = "data_not_found_error"
    
    # System failures
    SYSTEM_ERROR = "system_error"
    NETWORK_ERROR = "network_error"
    
    # Business logic failures
    BUSINESS_RULE_ERROR = "business_rule_error"
    WORKFLOW_ERROR = "workflow_error"


class FailureSeverity(Enum):
    """Severity levels for failures."""
    
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class FailureBehavior:
    """Handles failure behavior and recovery strategies."""
    
    # Default failure behaviors
    DEFAULT_BEHAVIORS = {
        FailureType.AUTHENTICATION_ERROR: {
            'severity': FailureSeverity.CRITICAL,
            'action': 'stop',
            'retry': False,
            'notify': True,
        },
        FailureType.AUTHORIZATION_ERROR: {
            'severity': FailureSeverity.CRITICAL,
            'action': 'stop',
            'retry': False,
            'notify': True,
        },
        FailureType.API_ERROR: {
            'severity': FailureSeverity.HIGH,
            'action': 'retry',
            'retry_count': 3,
            'retry_delay': 5,
            'notify': True,
        },
        FailureType.RATE_LIMIT_ERROR: {
            'severity': FailureSeverity.MEDIUM,
            'action': 'wait',
            'wait_time': 3600,  # 1 hour
            'notify': True,
        },
        FailureType.TIMEOUT_ERROR: {
            'severity': FailureSeverity.MEDIUM,
            'action': 'retry',
            'retry_count': 2,
            'retry_delay': 10,
            'notify': False,
        },
        FailureType.DATA_VALIDATION_ERROR: {
            'severity': FailureSeverity.LOW,
            'action': 'skip',
            'retry': False,
            'notify': False,
        },
        FailureType.DATA_CONFLICT_ERROR: {
            'severity': FailureSeverity.MEDIUM,
            'action': 'resolve',
            'retry': False,
            'notify': True,
        },
        FailureType.DATA_NOT_FOUND_ERROR: {
            'severity': FailureSeverity.LOW,
            'action': 'skip',
            'retry': False,
            'notify': False,
        },
        FailureType.SYSTEM_ERROR: {
            'severity': FailureSeverity.HIGH,
            'action': 'stop',
            'retry': False,
            'notify': True,
        },
        FailureType.NETWORK_ERROR: {
            'severity': FailureSeverity.MEDIUM,
            'action': 'retry',
            'retry_count': 3,
            'retry_delay': 5,
            'notify': False,
        },
        FailureType.BUSINESS_RULE_ERROR: {
            'severity': FailureSeverity.MEDIUM,
            'action': 'skip',
            'retry': False,
            'notify': True,
        },
        FailureType.WORKFLOW_ERROR: {
            'severity': FailureSeverity.HIGH,
            'action': 'stop',
            'retry': False,
            'notify': True,
        },
    }
    
    def __init__(self, custom_behaviors: Optional[Dict[FailureType, Dict[str, Any]]] = None):
        """Initialize failure behavior handler.
        
        Args:
            custom_behaviors: Custom failure behaviors to override defaults
        """
        self.behaviors = self.DEFAULT_BEHAVIORS.copy()
        
        if custom_behaviors:
            for failure_type, behavior in custom_behaviors.items():
                self.behaviors[failure_type] = behavior
    
    def get_behavior(self, failure_type: FailureType) -> Dict[str, Any]:
        """Get behavior for a failure type.
        
        Args:
            failure_type: Type of failure
            
        Returns:
            Behavior configuration
        """
        return self.behaviors.get(failure_type, {
            'severity': FailureSeverity.MEDIUM,
            'action': 'skip',
            'retry': False,
            'notify': True,
        })
    
    def handle_failure(self, failure_type: FailureType, error: Exception, 
                       context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Handle a failure according to its behavior.
        
        Args:
            failure_type: Type of failure
            error: Exception that occurred
            context: Additional context about the failure
            
        Returns:
            Handling result
        """
        behavior = self.get_behavior(failure_type)
        
        result = {
            'failure_type': failure_type.value,
            'severity': behavior['severity'].value,
            'action': behavior['action'],
            'error_message': str(error),
            'error_type': type(error).__name__,
            'timestamp': datetime.now().isoformat(),
            'context': context or {},
        }
        
        # Log the failure
        log_level = self._get_log_level(behavior['severity'])
        logger.log(log_level, f"Failure: {failure_type.value} - {error}")
        
        # Execute action
        action = behavior['action']
        
        if action == 'stop':
            result['should_stop'] = True
            result['message'] = "Stopping automation due to critical failure"
        elif action == 'retry':
            result['should_retry'] = True
            result['retry_count'] = behavior.get('retry_count', 0)
            result['retry_delay'] = behavior.get('retry_delay', 0)
            result['message'] = f"Will retry {result['retry_count']} times with {result['retry_delay']}s delay"
        elif action == 'wait':
            result['should_wait'] = True
            result['wait_time'] = behavior.get('wait_time', 0)
            result['message'] = f"Will wait {result['wait_time']} seconds before continuing"
        elif action == 'skip':
            result['should_skip'] = True
            result['message'] = "Skipping this item and continuing"
        elif action == 'resolve':
            result['should_resolve'] = True
            result['message'] = "Attempting to resolve conflict"
        
        # Check if notification should be sent
        result['should_notify'] = behavior.get('notify', False)
        
        return result
    
    def _get_log_level(self, severity: FailureSeverity) -> int:
        """Get log level for severity.
        
        Args:
            severity: Failure severity
            
        Returns:
            Log level constant
        """
        severity_map = {
            FailureSeverity.LOW: logging.INFO,
            FailureSeverity.MEDIUM: logging.WARNING,
            FailureSeverity.HIGH: logging.ERROR,
            FailureSeverity.CRITICAL: logging.CRITICAL,
        }
        return severity_map.get(severity, logging.WARNING)
    
    def should_stop_automation(self, failure_type: FailureType) -> bool:
        """Check if automation should stop for a failure type.
        
        Args:
            failure_type: Type of failure
            
        Returns:
            True if automation should stop
        """
        behavior = self.get_behavior(failure_type)
        return behavior['action'] == 'stop'
    
    def get_retry_strategy(self, failure_type: FailureType) -> Optional[Dict[str, Any]]:
        """Get retry strategy for a failure type.
        
        Args:
            failure_type: Type of failure
            
        Returns:
            Retry strategy or None
        """
        behavior = self.get_behavior(failure_type)
        
        if behavior['action'] == 'retry':
            return {
                'retry_count': behavior.get('retry_count', 0),
                'retry_delay': behavior.get('retry_delay', 0),
            }
        
        return None
    
    def classify_error(self, error: Exception) -> FailureType:
        """Classify an exception into a failure type.
        
        Args:
            error: Exception to classify
            
        Returns:
            Failure type
        """
        error_type = type(error).__name__.lower()
        error_message = str(error).lower()
        
        # Check for specific error patterns
        if 'auth' in error_type or 'unauthorized' in error_message:
            return FailureType.AUTHORIZATION_ERROR
        elif 'permission' in error_message:
            return FailureType.AUTHORIZATION_ERROR
        elif 'timeout' in error_type or 'timeout' in error_message:
            return FailureType.TIMEOUT_ERROR
        elif 'rate limit' in error_message or '429' in error_message:
            return FailureType.RATE_LIMIT_ERROR
        elif 'not found' in error_message or '404' in error_message:
            return FailureType.DATA_NOT_FOUND_ERROR
        elif 'conflict' in error_message or '409' in error_message:
            return FailureType.DATA_CONFLICT_ERROR
        elif 'validation' in error_type or 'invalid' in error_message:
            return FailureType.DATA_VALIDATION_ERROR
        elif 'network' in error_type or 'connection' in error_message:
            return FailureType.NETWORK_ERROR
        elif 'api' in error_type or 'http' in error_type:
            return FailureType.API_ERROR
        else:
            return FailureType.SYSTEM_ERROR
