# Orchestration Configuration

## Overview

This document describes the orchestration logic for the LinkedIn Salesrobot automation system, including workflow execution, scheduling, and error handling.

## Workflow Execution

### Main Workflow

The main automation workflow consists of the following steps:

1. **Preflight Check**
   - Verify API credentials
   - Check access to Google Sheets
   - Validate configuration
   - Test Salesrobot API connection

2. **Lead Sync**
   - Fetch leads from source sheet
   - Validate lead data
   - Map to internal format
   - Check for duplicates

3. **Campaign Enrollment**
   - Filter eligible leads
   - Enroll leads in campaigns
   - Update workflow sheet
   - Track enrollment status

4. **Status Sync**
   - Fetch status from Salesrobot
   - Map to internal status
   - Update workflow sheet
   - Detect conflicts

5. **Human Stop Check**
   - Check for manual stops
   - Check for opt-outs
   - Check for negative feedback
   - Stop automation if needed

6. **Dashboard Update**
   - Update metrics
   - Record events
   - Generate reports
   - Send notifications

### Workflow States

| State | Description | Next States |
|-------|-------------|-------------|
| idle | Not running | preflight, running |
| preflight | Running preflight checks | running, error |
| running | Main workflow executing | syncing, stopping |
| syncing | Syncing data with APIs | running, error |
| stopping | Stopping gracefully | idle, error |
| error | Error occurred | idle, stopping |

## Scheduling

### Timezone
All schedules use `America/Los_Angeles` timezone.

### Scheduled Workflows

#### Monday Start
- **Schedule**: Every Monday at 8:07 AM
- **Workflow**: Full workflow execution
- **Actions**:
  - Preflight check
  - Lead sync
  - Campaign enrollment
  - Status sync
  - Dashboard update

#### Daily Ping
- **Schedule**: Daily at 8:17 AM
- **Workflow**: Status sync only
- **Actions**:
  - Preflight check
  - Status sync
  - Dashboard update

#### Dashboard Refresh
- **Schedule**: Daily at 9:00 AM
- **Workflow**: Dashboard update only
- **Actions**:
  - Fetch latest metrics
  - Update dashboard
  - Generate reports

#### Manual Run
- **Schedule**: Manual trigger only
- **Workflow**: Configurable
- **Actions**:
  - Preflight check (optional)
  - Lead sync (optional)
  - Campaign enrollment (optional)
  - Status sync (optional)
  - Dashboard update (optional)

### Schedule Configuration

```yaml
schedules:
  monday_start:
    enabled: true
    cron: "7 8 * * 1"
    timezone: "America/Los_Angeles"
    workflow: "full"
  
  daily_ping:
    enabled: true
    cron: "17 8 * * *"
    timezone: "America/Los_Angeles"
    workflow: "status_sync"
  
  dashboard_refresh:
    enabled: true
    cron: "0 9 * * *"
    timezone: "America/Los_Angeles"
    workflow: "dashboard"
  
  manual_run:
    enabled: true
    workflow: "full"
    dry_run: true
```

## Error Handling

### Error Categories

#### Authentication Errors
- **Severity**: Critical
- **Action**: Stop automation
- **Notification**: Email + Slack
- **Retry**: No

#### Authorization Errors
- **Severity**: Critical
- **Action**: Stop automation
- **Notification**: Email + Slack
- **Retry**: No

#### API Errors
- **Severity**: High
- **Action**: Retry with backoff
- **Notification**: Slack
- **Retry**: Yes (3 times)

#### Rate Limit Errors
- **Severity**: Medium
- **Action**: Wait and retry
- **Notification**: Slack
- **Retry**: Yes (after wait time)

#### Timeout Errors
- **Severity**: Medium
- **Action**: Retry with backoff
- **Notification**: Log only
- **Retry**: Yes (2 times)

#### Data Validation Errors
- **Severity**: Low
- **Action**: Skip lead
- **Notification**: Log only
- **Retry**: No

#### Data Conflict Errors
- **Severity**: Medium
- **Action**: Resolve conflict
- **Notification**: Slack
- **Retry**: No

#### System Errors
- **Severity**: High
- **Action**: Stop automation
- **Notification**: Email + Slack
- **Retry**: No

### Error Recovery

#### Retry Strategy
- **Exponential Backoff**: 5s, 10s, 20s
- **Max Retries**: 3
- **Retry Delay**: Configurable

#### Stop Conditions
- Critical errors: Stop immediately
- High severity errors: Stop after retry
- Medium severity errors: Continue with warning
- Low severity errors: Continue silently

## Rate Limiting

### API Rate Limits

#### Salesrobot API
- **Connection Requests**: 20 per day
- **Follow-Up Messages**: 20 per day
- **Voice Messages**: 20 per day
- **Video Messages**: 20 per day
- **Profile Views**: 20 per day
- **InMail Messages**: 20 per day
- **Profile Follows**: 20 per day
- **Post Likes & Comments**: 20 per day
- **Endorsements**: 20 per day
- **Withdraw Connection Requests**: 10 per day
- **Invite to Event**: 30 per day

#### Google Sheets API
- **Read Operations**: 100 per minute
- **Write Operations**: 100 per minute
- **Batch Operations**: 50 per batch

### Client-Side Rate Limiting

#### Token Bucket Algorithm
- **Bucket Size**: 100 tokens
- **Refill Rate**: 1 token per second
- **Request Cost**: 1 token per request

#### Throttling
- **Concurrent Requests**: Max 5
- **Queue Size**: Max 100
- **Timeout**: 30 seconds

## Data Flow

### Lead Data Flow

```
Source Sheet → Lead Sync → Validation → Mapping → 
Campaign Enrollment → Status Sync → Workflow Sheet
```

### Status Data Flow

```
Salesrobot API → Status Sync → Mapping → Conflict Resolution → 
Workflow Sheet → Dashboard
```

### Human Intervention Flow

```
Human Update → Workflow Sheet → Human Stop Check → 
Stop Automation → Notification
```

## Concurrency

### Parallel Processing

#### Lead Processing
- **Batch Size**: 50 leads
- **Parallel Workers**: 5
- **Queue Size**: 100

#### API Calls
- **Concurrent Calls**: 5
- **Rate Limit**: 10 per second
- **Timeout**: 30 seconds

### Synchronization

#### Critical Sections
- Lead ID generation
- Status updates
- Counter increments

#### Locking
- **Lead Lock**: Per-lead locking
- **Global Lock**: For global state
- **Timeout**: 10 seconds

## Monitoring

### Metrics

#### Workflow Metrics
- Workflow execution time
- Lead processing rate
- Success rate
- Error rate

#### API Metrics
- API call count
- API response time
- API error rate
- Rate limit hits

#### Business Metrics
- Leads enrolled
- Leads converted
- Response rate
- Opt-out rate

### Alerts

#### Critical Alerts
- Workflow failure
- Authentication error
- Rate limit exceeded

#### Warning Alerts
- High error rate (> 5%)
- Slow response time (> 2s)
- Low success rate (< 95%)

#### Info Alerts
- Workflow completed
- Milestone reached
- Status update

## Logging

### Log Levels

#### DEBUG
- Detailed execution flow
- Variable values
- API request/response

#### INFO
- Workflow start/stop
- Lead processing
- Status updates

#### WARNING
- Retry attempts
- Rate limit warnings
- Data validation warnings

#### ERROR
- API errors
- System errors
- Workflow failures

#### CRITICAL
- Authentication errors
- Critical system failures
- Data corruption

### Log Retention
- **Retention Period**: 30 days
- **Max Size**: 10GB
- **Rotation**: Daily

## Testing

### Unit Tests
- Lead mapper tests
- Lead validator tests
- Status taxonomy tests
- Stop rules tests

### Integration Tests
- Google Sheets integration
- Salesrobot API integration
- Workflow execution
- Error handling

### End-to-End Tests
- Full workflow execution
- Scheduled workflows
- Manual workflows
- Error recovery

## Deployment

### Environment Variables

#### Required
- `GOOGLE_SERVICE_ACCOUNT_JSON`: Google credentials
- `SALESROBOT_API_KEY`: Salesrobot API key
- `SOURCE_LEAD_SHEET_ID`: Source sheet ID
- `WORKFLOW_SHEET_ID`: Workflow sheet ID

#### Optional
- `TIMEZONE`: Timezone (default: America/Los_Angeles)
- `DRY_RUN`: Dry run mode (default: true)
- `LOG_LEVEL`: Log level (default: INFO)

### Configuration Files

#### settings.json
```json
{
  "google": {
    "service_account_json": "",
    "source_sheet_id": "",
    "workflow_sheet_id": ""
  },
  "salesrobot": {
    "api_key": "",
    "base_url": "https://api.salesrobot.io/v1"
  },
  "automation": {
    "timezone": "America/Los_Angeles",
    "dry_run": true,
    "batch_size": 50
  }
}
```

## Security

### API Key Management
- Never commit API keys to version control
- Use environment variables or secrets
- Rotate API keys regularly
- Monitor API key usage

### Data Encryption
- Encrypt sensitive data at rest
- Use HTTPS for all API calls
- Validate SSL certificates

### Access Control
- Implement role-based access control
- Audit all access attempts
- Use least privilege principle

## Performance Optimization

### Caching
- Cache lead data for 5 minutes
- Cache status data for 1 minute
- Cache configuration for 1 hour

### Batching
- Batch API calls when possible
- Batch database writes
- Batch notifications

### Lazy Loading
- Load data on demand
- Use pagination for large datasets
- Implement streaming for large files
