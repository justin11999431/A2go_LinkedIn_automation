"""Validation logic for the automation system."""

import os
import logging
from typing import Dict, Any, List
from src.settings import Settings

logger = logging.getLogger(__name__)

def validate_environment() -> Dict[str, Any]:
    """Validate the entire environment and configuration.
    
    Returns:
        Dictionary with validation results.
    """
    settings = Settings()
    validation_results = settings.validate()
    
    # Additional environment checks
    env = os.getenv('NODE_ENV', 'development')
    validation_results['environment'] = env
    
    # Check for safety overrides
    safety_mode = os.getenv('SAFETY_MODE', 'true').lower() == 'true'
    dry_run = os.getenv('DRY_RUN', 'true').lower() == 'true'
    
    validation_results['safety_mode_env'] = safety_mode
    validation_results['dry_run_env'] = dry_run
    
    if not safety_mode:
        validation_results['warnings'].append("SAFETY_MODE environment variable is set to FALSE.")
    
    if not dry_run:
        validation_results['warnings'].append("DRY_RUN environment variable is set to FALSE.")
        
    return validation_results

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    results = validate_environment()
    if results['valid']:
        logger.info("Configuration is VALID")
    else:
        logger.error("Configuration is INVALID")
        for error in results['errors']:
            logger.error(f"  - {error}")
    
    for warning in results['warnings']:
        logger.warning(f"  - {warning}")
