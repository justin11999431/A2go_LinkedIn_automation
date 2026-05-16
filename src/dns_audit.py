"""Utility to audit DNS authentication records."""

import logging
from src.settings import Settings
from src.cloudflare_client import CloudflareClient

logger = logging.getLogger(__name__)

def run_dns_audit():
    """Run a DNS authentication audit for the main sending domain."""
    settings = Settings()
    
    api_token = settings.get('cloudflare.api_token')
    account_id = settings.get('cloudflare.account_id')
    domain = settings.get('cloudflare.domain', 'a2gotools.com')
    
    if not api_token or not account_id:
        logger.error("Cloudflare credentials missing in settings.")
        return

    cf = CloudflareClient(api_token, account_id)
    logger.info(f"Auditing DNS for domain: {domain}")
    
    results = cf.audit_email_auth(domain)
    
    if "error" in results:
        logger.error(results["error"])
        return

    logger.info("-" * 40)
    logger.info(f"SPF: {results['spf']['status']} - {results['spf']['record']}")
    logger.info(f"DMARC: {results['dmarc']['status']} - {results['dmarc']['record']}")
    logger.info(f"DKIM: {results['dkim']['status']} ({len(results['dkim']['records'])} records found)")
    logger.info("-" * 40)
    
    # Simple recommendation logic
    if results['spf']['status'] == 'missing':
        logger.warning("ACTION REQUIRED: Add SPF record to prevent email bouncing.")
    if results['dmarc']['status'] == 'missing':
        logger.warning("ACTION REQUIRED: Add DMARC record for better deliverability.")
        
    return results

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_dns_audit()
