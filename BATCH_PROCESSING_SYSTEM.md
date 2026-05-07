# LinkedIn Outreach Batch Processing System

## Overview

This system automates LinkedIn outreach in batches, processing up to 20 new leads per day while respecting the daily message limit and ensuring follow-up messages are sent on schedule.

## Key Features

### 1. Daily Message Limit Management
- **Total daily limit**: 20 messages
- **Dynamic quota calculation**: Adjusts new connection requests based on follow-up messages needed
- **Example**: If 2 follow-ups are needed, only 18 new connection requests are sent

### 2. Follow-up Message Sequencing
- **Colleague Message**: 1-3 days after connection acceptance
- **Customer Message**: 6-14 days after connection acceptance
- **Bridge Message**: 15-21 days after connection acceptance
- **Final Message**: 25-35 days after connection acceptance

### 3. Human-in-Loop Response Detection
- **Automatic response detection**: Checks for prospect responses
- **Immediate stop**: Stops all automation for leads with responses
- **Persistent stop**: Automation does not resume for stopped leads
- **Response window**: Checks for responses within last 7 days
- **Status tracking**: Updates workflow sheet with stop reason

### 4. Batch Processing
- **New connections**: Up to 20 per day (adjusted for follow-ups)
- **Follow-up messages**: Sent based on timing, not batch size
- **No disruption**: Previous leads' messaging sequences are preserved
- **Response-aware**: Skips leads where automation is stopped

## How It Works

### Daily at 9:00 AM:

#### Step 1: Check for Follow-up Messages
1. Reads workflow sheet
2. Finds leads needing follow-up based on timing
3. Counts follow-up messages needed

#### Step 2: Calculate Daily Quota
```
Available quota = 20 - follow-up_messages_needed
```

#### Step 3: Get New Leads
1. Reads source sheet
2. Finds leads not yet in workflow sheet
3. Limits to available quota

#### Step 4: Send Follow-up Messages
1. Gets message from workflow sheet
2. Sends via Salesrobot API
3. Updates message sent status

#### Step 5: Send New Connection Requests
1. Generates copy for new leads
2. Sends connection requests
3. Updates workflow sheet

## Example Scenarios

### Scenario 1: No Follow-ups Needed
- **Follow-up messages needed**: 0
- **Available quota**: 20
- **New connections**: 20

### Scenario 2: 2 Follow-ups Needed
- **Follow-up messages needed**: 2
- **Available quota**: 18
- **New connections**: 18

### Scenario 3: 5 Follow-ups Needed
- **Follow-up messages needed**: 5
- **Available quota**: 15
- **New connections**: 15

### Scenario 4: 20 Follow-ups Needed
- **Follow-up messages needed**: 20
- **Available quota**: 0
- **New connections**: 0

## Usage

### Option 1: Schedule Daily 9:00 AM Automation
Run this to schedule daily automation:
```bash
scripts\schedule_batch_processing.bat
```

### Option 2: Run Manually
Run batch processing manually:
```bash
python scripts\batch_processing.py
```

### Option 3: Check Remaining Leads
Check how many leads need copy:
```bash
python scripts\check_remaining_leads.py
```

### Option 4: Generate Copy in Batches
Generate copy for remaining leads:
```bash
python scripts\generate_copy.py --max-leads 50
```

## Components

### 1. Batch Processing Script
- **File**: `scripts/batch_processing.py`
- **Purpose**: Main batch processing system
- **Features**:
  - Calculates daily quota
  - Processes follow-up messages
  - Sends new connection requests
  - Updates workflow sheet

### 2. Check Remaining Leads Script
- **File**: `scripts/check_remaining_leads.py`
- **Purpose**: Check how many leads need copy
- **Features**:
  - Reads source sheet
  - Checks workflow sheet
  - Reports remaining leads

### 3. Generate Copy Script
- **File**: `scripts/generate_copy.py`
- **Purpose**: Generate LinkedIn copy for leads
- **Features**:
  - NVIDIA LLM-powered copy generation
  - Batch processing support
  - Updates workflow sheet

### 4. Batch Files
- **schedule_batch_processing.bat**: Schedule daily 9:00 AM automation

## Configuration

### Required Settings
All settings are in `settings.json`:

```json
{
  "salesrobot": {
    "api_key": "gtjsDYODvzjB45RKZbsYNDwnGjASGvnDKGjYq53MAJw",
    "linkedin_account_uuid": "dd113af4-85e7-4b58-a033-fefaabb49486"
  },
  "google": {
    "source_sheet_id": "1nCyhA1ubXaCljUJ0ON6y1v6czRzXlFoT5MRzeeX7Fns",
    "workflow_sheet_id": "1PLG4IMml1ha5VIxlOny7UO134tjhwCa1bAGxp6xs6O4"
  }
}
```

### Rate Limits
- **Total daily limit**: 20 messages
- **Connection requests**: Adjusted based on follow-ups
- **Follow-up messages**: Sent based on timing
- **Delay between messages**: 2 seconds

## Workflow Sheet Structure

The workflow sheet tracks:
- **Lead ID**: Unique identifier
- **LinkedIn Profile URL**: LinkedIn profile
- **Connection Status**: Current status (Sent, Accepted, Connected)
- **Connection Accepted Date**: When connection was accepted
- **Last Action Date**: Timestamp of last action
- **Reply Status**: Response status from prospect
- **Reply Text**: Response text from prospect
- **Last Human Update**: When prospect last responded
- **Automation Stopped**: Whether automation is stopped (Yes/No)
- **Stop Reason**: Reason for stopping automation
- **Follow-up Messages**: 4 messages per lead
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

## Human-in-Loop Response Detection

### How It Works
The system automatically detects when a prospect responds to any message and immediately stops all automation for that lead.

### Detection Criteria
- **Response window**: Checks for responses within last 7 days
- **Response types**: Replied, Responded, Answered
- **Detection method**: Checks Reply Status and Last Human Update columns

### Stop Behavior
- **Immediate stop**: All automation stops for that lead
- **Persistent stop**: Automation does not resume for stopped leads
- **Status update**: Workflow sheet marked with "Automation Stopped: Yes"
- **Reason tracking**: Stop reason recorded in workflow sheet

### Example Scenarios

#### Scenario 1: Prospect responds to connection request
- **Detection**: Response detected in workflow sheet
- **Action**: Automation stops immediately
- **Result**: No follow-up messages sent
- **Status**: "Automation Stopped: Yes - Response detected: Replied"

#### Scenario 2: Prospect responds to follow-up message
- **Detection**: Response detected in workflow sheet
- **Action**: Automation stops immediately
- **Result**: No further messages sent
- **Status**: "Automation Stopped: Yes - Response detected: Responded"

#### Scenario 3: No response
- **Detection**: No response in workflow sheet
- **Action**: Automation continues normally
- **Result**: Follow-up messages sent on schedule
- **Status**: "Automation Stopped: No"

### Benefits
- **Respectful**: Stops when prospect engages
- **Professional**: Doesn't overwhelm prospects
- **Compliant**: Follows LinkedIn best practices
- **Trackable**: All stops are logged

### Implementation
The human-in-loop check runs daily at 9:00 AM as part of the batch processing:
1. Checks for new responses
2. Stops automation for leads with responses
3. Updates workflow sheet with stop status
4. Skips stopped leads in all future processing

## Troubleshooting

### Batch Processing Not Running
If the batch processing doesn't run:
1. Check Windows Task Scheduler
2. Verify task is enabled
3. Check task history for errors
4. Run manually to test

### Quota Calculation Issues
If quota calculation seems wrong:
1. Check follow-up message timing
2. Verify workflow sheet data
3. Review daily message limit
4. Check for duplicate entries

### Messages Not Sending
If messages fail to send:
1. Check Salesrobot API status
2. Verify LinkedIn account is connected
3. Check rate limits
4. Review error logs

### Copy Generation Issues
If copy generation fails:
1. Check NVIDIA API key
2. Verify source sheet data
3. Check workflow sheet structure
4. Review error logs

## Monitoring

### Check Batch Processing Status
Run batch processing manually to see current status:
```bash
python scripts\batch_processing.py
```

### Check Remaining Leads
Check how many leads need copy:
```bash
python scripts\check_remaining_leads.py
```

### Check Human Responses
Check for new human responses:
```bash
python scripts\check_human_responses.py
```

### Check Workflow Sheet
Review the workflow sheet to see:
- Connection status
- Message sent dates
- Last action dates
- Remaining leads
- Automation stopped status
- Stop reasons

## Next Steps

1. **Schedule the batch processing**: Run `scripts\schedule_batch_processing.bat`
2. **Check remaining leads**: Run `scripts\check_remaining_leads.py`
3. **Generate copy in batches**: Run `python scripts\generate_copy.py --max-leads 50`
4. **Monitor results**: Check workflow sheet for updates
5. **Review responses**: Monitor LinkedIn for responses

## Files

- `scripts/batch_processing.py` - Main batch processing system with human-in-loop
- `scripts/check_remaining_leads.py` - Check remaining leads
- `scripts/check_human_responses.py` - Check for human responses
- `scripts/generate_copy.py` - Generate copy for leads
- `scripts/schedule_batch_processing.bat` - Schedule daily 9:00 AM
- `settings.json` - Configuration file
- `BATCH_PROCESSING_SYSTEM.md` - This documentation

## Notes

- Batch processing runs daily at 9:00 AM
- Daily message limit: 20 total messages
- Quota adjusted based on follow-up messages needed
- All messages include Patrick Romeri signature
- Workflow sheet updated with all actions
- Rate limits respected (2-second delay between messages)
- Previous leads' messaging sequences preserved
- **Human-in-loop response detection enabled**
- **Automation stops immediately when prospect responds**
- **Stopped leads are skipped in all future processing**
- **Response window: 7 days**
- **Stop status is persistent**

## Support

For issues or questions:
1. Check the batch processing logs
2. Review error messages
3. Verify configuration in `settings.json`
4. Check Salesrobot API documentation
5. Review Windows Task Scheduler logs
