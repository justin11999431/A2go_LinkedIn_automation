# LinkedIn Outreach Campaign - Summary

## Completed Tasks

### 1. Signature Added to All Messages
- Added Patrick Romeri's signature to all LinkedIn messages
- Signature includes:
  - Name: Patrick Romeri
  - Title: Director of Marketing
  - Company: Analytics2Go, Inc.
  - Mobile: +1 508-808-4820
  - Website: www.a2go.ai

### 2. Generated Copy for 20 Leads
Successfully generated LinkedIn outreach copy for 20 leads:

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

### 3. Connection Requests Prepared
- All 20 connection requests extracted and saved to `connection_requests.txt`
- Each connection request follows the new messaging guidelines:
  - Honest cold approach
  - No em-dashes or en-dashes
  - Peer-to-peer tone
  - No forbidden phrases
  - Under 280 characters

### 4. Scheduling Setup
- Created `schedule_connection_requests.py` script
- Scheduled time: Tomorrow at 8:00 AM (2026-05-07 08:00:00)
- Created batch file for Windows Task Scheduler

## Next Steps

### Option 1: Manual Sending
You can manually send the connection requests by:
1. Opening `connection_requests.txt`
2. Copying each message
3. Sending via LinkedIn

### Option 2: Automated Sending (Requires Salesrobot API)
To automate the connection requests:

1. **Create `send_connection_requests.py` script:**
   - Read connection requests from `connection_requests.txt`
   - Use Salesrobot API to send connection requests
   - Handle rate limits (20/day for most actions)

2. **Schedule the task:**
   - Run `schedule_connection_requests.bat`
   - This will create a Windows Task Scheduler task
   - The task will run at 8:00 AM tomorrow

### Option 3: Use Salesrobot Campaign
If you have a Salesrobot campaign set up:
1. Import the 20 leads into your Salesrobot campaign
2. Upload the connection request messages
3. Schedule the campaign to start at 8:00 AM tomorrow

## Files Created

- `scripts/add_signatures.py` - Script to add signature to all messages
- `scripts/schedule_connection_requests.py` - Script to prepare connection requests
- `scripts/connection_requests.txt` - List of all 20 connection requests
- `scripts/schedule_connection_requests.bat` - Batch file for Windows Task Scheduler

## Workflow Sheet Status

The workflow sheet now contains:
- 20 leads with complete messaging
- Connection requests ready to send
- 4 follow-up messages per lead (Colleague, Customer, Bridge, Final)
- All messages include Patrick Romeri's signature
- All messages follow the new messaging guidelines

## Notes

- All connection requests are under 280 characters
- All messages avoid forbidden phrases
- All messages use peer-to-peer tone
- No em-dashes or en-dashes in any messages
- Signature included in all follow-up messages (not connection requests)

## Rate Limits

Remember Salesrobot API rate limits:
- 20/day for most actions
- 10/day for withdraw requests
- 30/day for event invites

Since we have 20 connection requests, they should all be able to be sent in one day without hitting rate limits.
