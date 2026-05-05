# Workflow Sheet Schema

## Overview

The workflow sheet tracks the status and progress of leads through the automation pipeline. It serves as the single source of truth for lead status and human intervention.

## Sheet Structure

### Column Headers

| Column Name | Type | Description | Required |
|-------------|------|-------------|----------|
| Lead ID | String | Unique identifier for the lead | Yes |
| First Name | String | Lead's first name | Yes |
| Last Name | String | Lead's last name | Yes |
| Email | String | Lead's email address | Yes |
| Company | String | Lead's company name | Yes |
| Title | String | Lead's job title | No |
| LinkedIn URL | String | LinkedIn profile URL | No |
| Industry | String | Industry | No |
| Location | String | Location | No |
| Phone | String | Phone number | No |
| Status | String | Current status (see Status Taxonomy) | Yes |
| Campaign | String | Associated campaign name | No |
| Priority | String | Priority level (low, medium, high) | No |
| Tags | String | Comma-separated tags | No |
| Created At | DateTime | When lead was created | Yes |
| Updated At | DateTime | When lead was last updated | Yes |
| Last Synced At | DateTime | When lead was last synced with Salesrobot | No |
| Human Notes | String | Notes entered by human | No |
| Human Status | String | Status set by human | No |
| Human Priority | String | Priority set by human | No |
| Human Tags | String | Tags set by human | No |
| Last Human Update | DateTime | When human last updated the lead | No |
| Manual Stop | Boolean | Whether manual stop is requested | No |
| Opt Out Requested | Boolean | Whether lead opted out | No |
| Negative Feedback | Boolean | Whether negative feedback received | No |
| Complaint Risk | Float | Complaint risk score (0-1) | No |
| Account Issue | Boolean | Whether there's an account issue | No |

## Status Taxonomy

### Initial States
- `new`: Lead created but not yet processed
- `imported`: Lead imported from source

### Processing States
- `enqueued`: Lead queued for processing
- `processing`: Lead currently being processed

### Outreach States
- `connection_requested`: Connection request sent
- `connected`: Connection accepted
- `first_message_sent`: First message sent
- `follow_up_sent`: Follow-up message sent

### Engagement States
- `viewed`: Message viewed
- `replied`: Lead replied
- `conversation_started`: Conversation in progress

### Positive Outcomes
- `interested`: Lead expressed interest
- `meeting_scheduled`: Meeting scheduled
- `demo_requested`: Demo requested
- `proposal_sent`: Proposal sent
- `negotiation`: In negotiation

### Negative Outcomes
- `not_interested`: Lead not interested
- `declined`: Connection declined
- `ghosted`: Lead stopped responding

### Stop States
- `opted_out`: Lead opted out
- `blocked`: Lead blocked
- `reported`: Lead reported
- `stopped`: Automation stopped for this lead

### Error States
- `error`: Error occurred
- `invalid`: Invalid data
- `duplicate`: Duplicate lead

### Final States
- `converted`: Lead converted
- `lost`: Lead lost
- `archived`: Lead archived

## Human-Entered Fields

### Protected Fields
The following fields are entered by humans and are preserved during automation updates:

- **Human Notes**: Notes about the lead
- **Human Status**: Status override set by human
- **Human Priority**: Priority override set by human
- **Human Tags**: Tags added by human
- **Last Human Update**: Timestamp of last human update

### Stop Flags
The following flags can be set by humans to stop automation:

- **Manual Stop**: Stop all automation for this lead
- **Opt Out Requested**: Lead has opted out
- **Negative Feedback**: Negative feedback received
- **Complaint Risk**: High complaint risk score
- **Account Issue**: Account issue detected

## Data Types

### String
- Text values
- Maximum length: 500 characters

### Boolean
- Values: `Yes` or `No`
- Stored as strings for compatibility

### DateTime
- Format: `YYYY-MM-DD HH:MM:SS`
- Timezone: UTC

### Float
- Numeric values with decimal
- Range: 0.0 to 1.0 for complaint risk

## Validation Rules

### Required Fields
- Lead ID must be unique
- First Name, Last Name, Email, Company are required
- Email must be valid format
- Status must be valid status value

### Optional Fields
- All other fields are optional
- Empty values are allowed

### Data Integrity
- Lead ID cannot be changed after creation
- Created At cannot be changed
- Updated At is automatically updated

## Upsert Logic

### Insert
- New leads are inserted with all fields
- Created At and Updated At set to current time
- Human fields are empty

### Update
- Existing leads are updated
- Human fields are preserved
- Updated At set to current time
- Other fields are updated from source

### Conflict Resolution
- Human fields always take precedence
- Automation fields are updated unless human override exists
- Last Human Update timestamp is checked

## Indexing

### Primary Index
- Lead ID (unique)

### Secondary Indexes
- Status
- Campaign
- Priority
- Updated At
- Last Human Update

## Query Patterns

### Get All Leads
```
SELECT * FROM workflow_sheet
```

### Get Leads by Status
```
SELECT * FROM workflow_sheet WHERE Status = 'new'
```

### Get Leads by Campaign
```
SELECT * FROM workflow_sheet WHERE Campaign = 'Outreach Q1'
```

### Get Leads with Human Updates
```
SELECT * FROM workflow_sheet WHERE Last Human Update IS NOT NULL
```

### Get Stopped Leads
```
SELECT * FROM workflow_sheet WHERE Manual Stop = 'Yes' OR Opt Out Requested = 'Yes'
```

## Performance Considerations

### Batch Size
- Recommended batch size: 50-100 leads
- Maximum batch size: 500 leads

### Update Frequency
- Recommended: Every 5-10 minutes
- Maximum: Every 1 minute

### Query Optimization
- Use filters to reduce result set
- Limit results when possible
- Use pagination for large datasets

## Security

### Access Control
- Read access for all users
- Write access for authorized users only
- Audit trail for all changes

### Data Privacy
- PII data should be encrypted
- Access logs should be maintained
- Data retention policy should be enforced

## Backup and Recovery

### Backup Strategy
- Daily backups
- Retain backups for 30 days
- Store backups in secure location

### Recovery Procedure
1. Identify backup to restore
2. Verify backup integrity
3. Restore to staging environment
4. Verify data integrity
5. Restore to production
