"""Main automation script to check acceptances and send follow-ups."""

import os
import sys
import logging
from datetime import datetime

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_automation():
    """Run the full automation process."""
    logger.info("=" * 60)
    logger.info("LINKEDIN OUTREACH AUTOMATION")
    logger.info("=" * 60)
    logger.info(f"Started at: {datetime.now().isoformat()}")
    
    # Step 1: Check for connection acceptances
    logger.info("\nStep 1: Checking for connection acceptances...")
    try:
        from check_connection_acceptances import main as check_acceptances
        check_acceptances()
    except Exception as e:
        logger.error(f"Error checking connection acceptances: {e}")
    
    # Step 2: Send follow-up messages
    logger.info("\nStep 2: Sending follow-up messages...")
    try:
        from send_followup_messages import main as send_followups
        send_followups()
    except Exception as e:
        logger.error(f"Error sending follow-up messages: {e}")
    
    logger.info("\n" + "=" * 60)
    logger.info("AUTOMATION COMPLETE")
    logger.info("=" * 60)
    logger.info(f"Completed at: {datetime.now().isoformat()}")


if __name__ == '__main__':
    run_automation()
