# Launch Checklist

Use this checklist to verify your setup before launching the LinkedIn Salesrobot Automation System.

## Pre-Launch Checklist

### 1. Google Sheets Setup

- [ ] Google Cloud Project created
- [ ] Google Sheets API enabled
- [ ] Service account created
- [ ] Service account key downloaded and saved securely
- [ ] Service account email copied
- [ ] Service account granted Editor access to source sheet
- [ ] Service account granted Editor access to workflow sheet
- [ ] Source sheet ID noted
- [ ] Workflow sheet ID noted

### 2. Salesrobot Setup

- [ ] Salesrobot account created
- [ ] API key generated
- [ ] API key saved securely
- [ ] Campaigns created in Salesrobot
- [ ] Campaign IDs noted
- [ ] Campaign IDs added to config/salesrobot.md

### 3. Source Sheet Configuration

- [ ] Source sheet has required columns:
  - [ ] First Name
  - [ ] Last Name
  - [ ] Email
  - [ ] Company
- [ ] Source sheet has optional columns (if needed):
  - [ ] Title
  - [ ] LinkedIn URL
  - [ ] Industry
  - [ ] Location
  - [ ] Phone
  - [ ] Notes
  - [ ] Status
  - [ ] Source
  - [ ] Campaign
  - [ ] Priority
  - [ ] Tags
- [ ] Source sheet contains test data
- [ ] Test data is valid (no missing required fields)
- [ ] Test data has valid email addresses

### 4. Workflow Sheet Configuration

- [ ] Workflow sheet created
- [ ] Workflow sheet headers seeded
- [ ] Workflow sheet has correct column structure
- [ ] Workflow sheet is empty (or has test data only)

### 5. Environment Configuration

- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Environment variables set (or settings.json created):
  - [ ] GOOGLE_SERVICE_ACCOUNT_JSON
  - [ ] SALESROBOT_API_KEY
  - [ ] SOURCE_LEAD_SHEET_ID
  - [ ] WORKFLOW_SHEET_ID
- [ ] Timezone configured (default: America/Los_Angeles)
- [ ] Dry-run mode enabled (for testing)

### 6. Code Configuration

- [ ] Repository cloned
- [ ] All files present and correct
- [ ] Configuration files reviewed:
  - [ ] config/salesrobot.md
  - [ ] config/workflow_sheet_schema.md
  - [ ] config/orchestration.md
- [ ] Sales copy templates reviewed (copy/sales_copy.md)

### 7. Testing

- [ ] Preflight check passes:
  ```bash
  python scripts/preflight.py
  ```
- [ ] Lead sync works in dry-run mode:
  ```bash
  python scripts/lead_sync.py --dry-run
  ```
- [ ] Campaign enrollment works in dry-run mode:
  ```bash
  python scripts/campaign_enroll.py --dry-run
  ```
- [ ] Workflow sheet headers seeded:
  ```bash
  python scripts/seed_workflow_headers.py
  ```
- [ ] Service account email printed:
  ```bash
  python scripts/print_service_account_email.py
  ```

### 8. GitHub Actions Setup

- [ ] Repository pushed to GitHub
- [ ] GitHub Secrets configured:
  - [ ] GOOGLE_SERVICE_ACCOUNT_JSON
  - [ ] SALESROBOT_API_KEY
  - [ ] SOURCE_LEAD_SHEET_ID
  - [ ] WORKFLOW_SHEET_ID
- [ ] Workflows enabled:
  - [ ] preflight.yml
  - [ ] daily_ping.yml
  - [ ] manual_run.yml
- [ ] Workflow schedules reviewed:
  - [ ] Monday 8:07 AM UTC
  - [ ] Daily 8:17 AM UTC

### 9. Security

- [ ] API keys not committed to version control
- [ ] Service account JSON not committed to version control
- [ ] .gitignore configured correctly
- [ ] Secrets stored in GitHub Secrets
- [ ] Access logs enabled
- [ ] Audit trail configured

### 10. Monitoring

- [ ] Logging configured
- [ ] Log level set appropriately
- [ ] Log rotation configured
- [ ] Error notifications configured
- [ ] Dashboard monitoring set up
- [ ] Alerts configured for critical errors

## Launch Readiness Checklist

### 11. Dry-Run Testing

- [ ] Full workflow tested in dry-run mode
- [ ] Lead sync tested with real data
- [ ] Campaign enrollment tested with real data
- [ ] Status sync tested
- [ ] Human stop logic tested
- [ ] Error handling tested
- [ ] Rate limiting tested

### 12. Data Validation

- [ ] All test leads validated successfully
- [ ] No duplicate lead IDs
- [ ] All email addresses valid
- [ ] All LinkedIn URLs valid (if present)
- [ ] All phone numbers valid (if present)
- [ ] All required fields present

### 13. Performance Testing

- [ ] System tested with expected load
- [ ] Batch size optimized
- [ ] Rate limits respected
- [ ] API response times acceptable
- [ ] Memory usage acceptable
- [ ] No memory leaks detected

### 14. Documentation

- [ ] SETUP.md reviewed and understood
- [ ] LAUNCH_CHECKLIST.md completed
- [ ] config/salesrobot.md reviewed
- [ ] config/workflow_sheet_schema.md reviewed
- [ ] config/orchestration.md reviewed
- [ ] copy/sales_copy.md reviewed
- [ ] README.md reviewed

### 15. Rollback Plan

- [ ] Rollback procedure documented
- [ ] Backup strategy in place
- [ ] Data backup verified
- [ ] Configuration backup verified
- [ ] Rollback tested

## Post-Launch Checklist

### 16. Initial Launch

- [ ] Dry-run mode disabled
- [ ] First manual run executed
- [ ] Results verified
- [ ] Workflow sheet updated correctly
- [ ] No errors in logs
- [ ] All leads processed correctly

### 17. Monitoring

- [ ] System monitored for first 24 hours
- [ ] No critical errors detected
- [ ] Performance metrics within expected range
- [ ] Rate limits not exceeded
- [ ] All notifications received

### 18. Validation

- [ ] Leads synced correctly
- [ ] Campaigns enrolled correctly
- [ ] Status updates working
- [ ] Human stop logic working
- [ ] Dashboard updating correctly

### 19. Optimization

- [ ] Batch size optimized
- [ ] Schedule times optimized
- [ ] Error handling refined
- [ ] Notification settings adjusted
- [ ] Logging level adjusted

### 20. Documentation Updates

- [ ] Any issues documented
- [ ] Lessons learned recorded
- [ ] Configuration changes documented
- [ ] Setup guide updated (if needed)
- [ ] Runbook created

## Ongoing Maintenance Checklist

### Weekly

- [ ] Review logs for errors
- [ ] Check dashboard metrics
- [ ] Verify API quotas
- [ ] Review rate limit usage
- [ ] Check for failed workflows

### Monthly

- [ ] Review and rotate API keys
- [ ] Review and update documentation
- [ ] Review and optimize performance
- [ ] Review and update configuration
- [ ] Review and update sales copy

### Quarterly

- [ ] Full system audit
- [ ] Security review
- [ ] Performance review
- [ ] Cost review
- [ ] Feature review and planning

## Emergency Procedures

### Critical Errors

- [ ] Emergency contact list created
- [ ] Emergency shutdown procedure documented
- [ ] Emergency rollback procedure documented
- [ ] Emergency communication plan documented

### Data Issues

- [ ] Data recovery procedure documented
- [ ] Data validation procedure documented
- [ ] Data cleanup procedure documented

### Security Issues

- [ ] Security incident response plan documented
- [ ] Security breach procedure documented
- [ ] Security notification procedure documented

## Sign-Off

### Pre-Launch Sign-Off

- [ ] Technical lead sign-off
- [ ] Business lead sign-off
- [ ] Security lead sign-off
- [ ] Operations lead sign-off

### Launch Sign-Off

- [ ] Launch authorization received
- [ ] Launch time confirmed
- [ ] Launch team notified
- [ ] Stakeholders notified

### Post-Launch Sign-Off

- [ ] Launch successful confirmed
- [ ] All systems operational
- [ ] Monitoring active
- [ ] Support team notified

## Notes

Use this section for any additional notes or observations during the launch process.

```
Date: _______________
Time: _______________
Notes: _______________


Date: _______________
Time: _______________
Notes: _______________
```
