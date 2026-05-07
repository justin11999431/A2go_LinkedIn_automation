# Automated Connection Request Sending System

## Overview

This system automates the sending of LinkedIn connection requests using the Salesrobot API. All 20 connection requests have been generated with proper messaging and are ready to be sent.

## Components

### 1. Connection Requests File
- **File**: `scripts/connection_requests.txt`
- **Contents**: 20 connection requests with lead names, LinkedIn URLs, and messages
- **Format**: Structured text file with numbered items

### 2. Send Connection Requests Script
- **File**: `scripts/send_connection_requests.py`
- **Purpose**: Sends connection requests via Salesrobot API
- **Features**:
  - Reads connection requests from `connection_requests.txt`
  - Uses Salesrobot API to send requests
  - Updates workflow sheet with status
  - Handles rate limits (2-second delay between requests)
  - Logs all actions and results

### 3. Test Script
- **File**: `scripts/test_connection_requests.py`
- **Purpose**: Verifies system configuration and setup
- **Tests**:
  - Reading connection requests file
  - Settings configuration (API keys, credentials)
  - Salesrobot client initialization
  - LinkedIn account retrieval

### 4. Schedule Script
- **File**: `scripts/schedule_connection_requests.py`
- **Purpose**: Prepares connection requests for scheduling
- **Features**:
  - Reads connection requests from file
  - Calculates scheduled time (tomorrow 8:00 AM)
  - Creates Windows Task Scheduler batch file

### 5. Batch File
- **File**: `scripts/schedule_connection_requests.bat`
- **Purpose**: Creates Windows Task Scheduler task
- **Schedule**: Tomorrow at 8:00 AM
- **Action**: Runs `send_connection_requests.py`

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
- **Current batch**: 20 requests
- **Delay between requests**: 2 seconds

## Usage

### Option 1: Send Now
Run the send script directly:
```bash
python scripts/send_connection_requests.py
```

### Option 2: Schedule for Tomorrow
Run the batch file to create a Windows Task Scheduler task:
```bash
scripts/schedule_connection_requests.bat
```

The task will run at 8:00 AM tomorrow and send all 20 connection requests.

### Option 3: Test Configuration
Verify everything is configured correctly:
```bash
python scripts/test_connection_requests.py
```

## Connection Requests

All 20 connection requests are ready to send:

1. Walt Walker
2. Vinod Khanna
3. David Gayden
4. R Gallion
5. Joe Pregont
6. Rob Livingston
7. Chris Smith
8. Rachel Andres
9. John Conley
10. Chris Bladl
11. Don Handrow
12. Joseph Pregont
13. Charles Hurd
14. Chris Niemann
15. Tony Marzullo
16. Stephen Easley
17. Emily Morgan
18. Jason Stierl
19. Kenny Rouse
20. Julie Chase-Morefield

## Message Format

All connection requests follow the new messaging guidelines:
- Honest cold approach
- No em-dashes or en-dashes
- Peer-to-peer tone
- No forbidden phrases
- Under 280 characters

Example:
```
Hi Walt, cold connect, won't pretend otherwise. Building out my network of operations leaders deliberately and you came up. No pitch.
```

## Workflow Sheet Updates

After sending connection requests, the workflow sheet will be updated with:
- **Connection Status**: Set to "Sent"
- **Last Action Date**: Timestamp of when request was sent

## Follow-up Messages

Each lead has 4 follow-up messages ready:
1. **Colleague Message**: Value-first insight (1-3 days after acceptance)
2. **Customer Message**: Bellwether question (5-9 days after M1)
3. **Bridge Message**: A2go mention (4-7 days after M2)
4. **Final Message**: Respectful close (10-14 days after M3)

All follow-up messages include Patrick Romeri's signature.

## Troubleshooting

### Test Failed
If the test script fails, check:
1. Salesrobot API key is correct in `settings.json`
2. LinkedIn account UUID is correct
3. Workflow sheet ID is correct
4. OAuth credentials are valid

### Connection Requests Not Sending
If connection requests fail to send:
1. Check Salesrobot API status
2. Verify LinkedIn account is connected
3. Check rate limits haven't been exceeded
4. Review error logs

### Task Scheduler Issues
If the Windows Task Scheduler task doesn't run:
1. Verify batch file path is correct
2. Check Python is in system PATH
3. Run the batch file as administrator
4. Check Task Scheduler logs

## Next Steps

1. **Test the system**: Run `python scripts/test_connection_requests.py`
2. **Send a test request**: Run `python scripts/send_connection_requests.py` with 1 lead
3. **Schedule full batch**: Run `scripts/schedule_connection_requests.bat`
4. **Monitor results**: Check workflow sheet for status updates
5. **Review responses**: Monitor LinkedIn for connection acceptances

## Files

- `scripts/connection_requests.txt` - Connection requests data
- `scripts/send_connection_requests.py` - Main sending script
- `scripts/test_connection_requests.py` - Configuration test script
- `scripts/schedule_connection_requests.py` - Scheduling preparation script
- `scripts/schedule_connection_requests.bat` - Windows Task Scheduler batch file
- `settings.json` - Configuration file
- `LINKEDIN_OUTREACH_SUMMARY.md` - Campaign summary

## Notes

- All connection requests are under 280 characters
- All messages avoid forbidden phrases
- All messages use peer-to-peer tone
- No em-dashes or en-dashes in any messages
- Signature included in all follow-up messages
- Rate limits respected (20/day for connection requests)
- 2-second delay between requests to avoid rate limiting

## Support

For issues or questions:
1. Check the test script output
2. Review error logs
3. Verify configuration in `settings.json`
4. Check Salesrobot API documentation
