# LinkedIn Outreach Automation System

## Overview

This system automates the entire LinkedIn outreach process, including:
- Checking for connection acceptances
- Sending follow-up messages based on timing
- Updating workflow sheet with status

## Automation Schedule

### Follow-up Message Schedule:
- **Colleague Message**: 1-3 days after connection acceptance
- **Customer Message**: 6-14 days after connection acceptance
- **Bridge Message**: 15-21 days after connection acceptance
- **Final Message**: 25-35 days after connection acceptance

### Daily Automation:
The automation runs daily at 8:00 AM and performs:
1. Checks for new connection acceptances
2. Sends follow-up messages based on timing
3. Updates workflow sheet with status

## Components

### 1. Check Connection Acceptances
- **File**: `scripts/check_connection_acceptances.py`
- **Purpose**: Checks workflow sheet for accepted connections
- **Updates**: Connection accepted date and last action date

### 2. Send Follow-up Messages
- **File**: `scripts/send_followup_messages.py`
- **Purpose**: Sends follow-up messages based on timing
- **Features**:
  - Determines which message to send based on days since acceptance
  - Gets message from workflow sheet
  - Sends via Salesrobot API
  - Updates message sent status

### 3. Main Automation Script
- **File**: `scripts/run_automation.py`
- **Purpose**: Runs the full automation process
- **Steps**:
  1. Check for connection acceptances
  2. Send follow-up messages

### 4. Batch Files
- **run_automation.bat**: Runs automation manually
- **schedule_automation.bat**: Schedules automation for daily 8:00 AM

## How It Works

### Step 1: Connection Acceptance Check
1. Reads workflow sheet
2. Finds leads with "Accepted" or "Connected" status
3. Updates connection accepted date
4. Updates last action date

### Step 2: Follow-up Message Sending
1. Reads workflow sheet
2. Finds leads needing follow-up based on timing:
   - Colleague: 1-3 days after acceptance
   - Customer: 6-14 days after acceptance
   - Bridge: 15-21 days after acceptance
   - Final: 25-35 days after acceptance
3. Gets message from workflow sheet
4. Sends message via Salesrobot API
5. Updates message sent status
6. Updates last action date

### Step 3: Workflow Sheet Updates
The workflow sheet is updated with:
- **Connection Status**: "Sent", "Accepted", "Connected"
- **Connection Accepted Date**: When connection was accepted
- **Last Action Date**: Timestamp of last action
- **Message Sent Dates**: When each follow-up was sent

## Usage

### Option 1: Run Manually
Run the automation manually:
```bash
scripts\run_automation.bat
```

### Option 2: Schedule for Daily 8:00 AM
Schedule the automation to run daily:
```bash
scripts\schedule_automation.bat
```

This will create a Windows Task Scheduler task that runs daily at 8:00 AM.

### Option 3: Run Individual Scripts
Run individual scripts:
```bash
# Check for connection acceptances
python scripts\check_connection_acceptances.py

# Send follow-up messages
python scripts\send_followup_messages.py
```

## Configuration

### Required Settings
All settings are configured in `settings.json`:

```json
{
  "salesrobot": {
    "api_key": "gtjsDYODvzjB45RKZbsYNDwnGjASGvnDKGjYq53MAJw",
    "linkedin_account_uuid": "dd113af4-85e7-4b58-a033-fefaabb49486"
  },
  "google": {
    "workflow_sheet_id": "1PLG4IMml1ha5VIxlOny7UO134tjhwCa1bAGxp6xs6O4"
  }
}
```

### Rate Limits
- **Connection requests**: 20/day (Salesrobot limit)
- **Follow-up messages**: 20/day (Salesrobot limit)
- **Delay between messages**: 2 seconds

## Workflow Sheet Structure

The workflow sheet tracks:
- **Lead ID**: Unique identifier
- **LinkedIn Profile URL**: LinkedIn profile
- **Connection Status**: Current status (Sent, Accepted, Connected)
- **Connection Accepted Date**: When connection was accepted
- **Last Action Date**: Timestamp of last action
- **First Follow-up Message**: Colleague message
- **Second Follow-up Message**: Customer message
- **Third Follow-up Message**: Bridge message
- **Fourth Follow-up Message**: Final message
- **Message Sent Dates**: When each message was sent

## Message Timing

### Colleague Message (1-3 days after acceptance)
- **Purpose**: Demonstrate understanding, give value
- **Content**: Operational insight, no pitch
- **Signature**: Patrick Romeri signature included

### Customer Message (6-14 days after acceptance)
- **Purpose**: Ask for perspective, invert dynamic
- **Content**: Bellwether question, position as expert
- **Signature**: Patrick Romeri signature included

### Bridge Message (15-21 days after acceptance)
- **Purpose**: Mention A2go, offer value-based next step
- **Content**: Light A2go mention, permission-based CTA
- **Signature**: Patrick Romeri signature included

### Final Message (25-35 days after acceptance)
- **Purpose**: Respectful close, leave door open
- **Content**: Low-pressure, no guilt
- **Signature**: Patrick Romeri signature included

## Troubleshooting

### Automation Not Running
If the automation doesn't run:
1. Check Windows Task Scheduler
2. Verify task is enabled
3. Check task history for errors
4. Run manually to test

### Messages Not Sending
If messages fail to send:
1. Check Salesrobot API status
2. Verify LinkedIn account is connected
3. Check rate limits haven't been exceeded
4. Review error logs

### Workflow Sheet Not Updating
If the workflow sheet doesn't update:
1. Check OAuth credentials are valid
2. Verify workflow sheet ID is correct
3. Check Google Sheets API access
4. Review error logs

### Task Scheduler Issues
If the Windows Task Scheduler task doesn't run:
1. Run batch file as administrator
2. Verify Python is in system PATH
3. Check Task Scheduler logs
4. Verify task is enabled

## Monitoring

### Check Automation Status
Run the automation manually to see current status:
```bash
scripts\run_automation.bat
```

### Check Workflow Sheet
Review the workflow sheet to see:
- Connection status
- Message sent dates
- Last action dates

### Check Logs
Review logs for errors and status updates.

## Next Steps

1. **Schedule the automation**: Run `scripts\schedule_automation.bat`
2. **Test the automation**: Run `scripts\run_automation.bat` manually
3. **Monitor results**: Check workflow sheet for updates
4. **Review responses**: Monitor LinkedIn for responses

## Files

- `scripts/check_connection_acceptances.py` - Check for acceptances
- `scripts/send_followup_messages.py` - Send follow-up messages
- `scripts/run_automation.py` - Main automation script
- `scripts/run_automation.bat` - Manual run batch file
- `scripts/schedule_automation.bat` - Scheduling batch file
- `settings.json` - Configuration file
- `AUTOMATED_SENDING_SYSTEM.md` - Sending system documentation

## Notes

- Automation runs daily at 8:00 AM
- All messages include Patrick Romeri's signature
- Rate limits respected (20/day for messages)
- 2-second delay between messages
- Workflow sheet updated with all actions
- Connection acceptances checked daily
- Follow-up messages sent based on timing

## Support

For issues or questions:
1. Check the automation logs
2. Review error messages
3. Verify configuration in `settings.json`
4. Check Salesrobot API documentation
5. Review Windows Task Scheduler logs
