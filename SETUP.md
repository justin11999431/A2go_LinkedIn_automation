# Setup Guide

This guide will help you set up the LinkedIn Salesrobot Automation System.

## Prerequisites

- Python 3.9 or higher
- Google Cloud Project with Google Sheets API enabled
- Salesrobot API account
- GitHub account (for GitHub Actions)

## Step 1: Clone the Repository

```bash
git clone https://github.com/justin11999431/A2go_LinkedIn_automation.git
cd A2go_LinkedIn_automation
```

## Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 3: Set Up Google Sheets API

### 3.1 Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google Sheets API:
   - Go to APIs & Services > Library
   - Search for "Google Sheets API"
   - Click "Enable"

### 3.2 Create Service Account

1. Go to APIs & Services > Credentials
2. Click "Create Credentials" > "Service Account"
3. Fill in the service account details:
   - Name: `linkedin-automation`
   - Description: `Service account for LinkedIn automation`
4. Click "Create and Continue"
5. Skip granting access (we'll do this later)
6. Click "Done"

### 3.3 Create Service Account Key

1. Click on the service account you just created
2. Go to the "Keys" tab
3. Click "Add Key" > "Create new key"
4. Select "JSON" key type
5. Click "Create"
6. Save the JSON file securely (you'll need it later)

### 3.4 Share Google Sheets with Service Account

1. Open your service account JSON file
2. Copy the `client_email` value (e.g., `linkedin-automation@project-id.iam.gserviceaccount.com`)
3. Go to your Google Sheets:
   - Source lead sheet
   - Workflow sheet
4. Click "Share"
5. Paste the service account email
6. Grant "Editor" permissions
7. Click "Send"

## Step 4: Set Up Salesrobot API

### 4.1 Get API Key

1. Log in to your Salesrobot account
2. Go to Settings > API Keys
3. Create a new API key
4. Copy the API key (you'll need it later)

### 4.2 Configure Campaigns

1. Create campaigns in Salesrobot
2. Note down the campaign IDs
3. Update `config/salesrobot.md` with your campaign IDs

## Step 5: Configure Environment Variables

### 5.1 Create .env File (Optional)

Create a `.env` file in the project root:

```env
GOOGLE_SERVICE_ACCOUNT_JSON='{"type":"service_account","project_id":"...","private_key_id":"...","private_key":"...","client_email":"...","client_id":"...","auth_uri":"...","token_uri":"...","auth_provider_x509_cert_url":"...","client_x509_cert_url":"..."}'
SALESROBOT_API_KEY='your-salesrobot-api-key'
SOURCE_LEAD_SHEET_ID='your-source-sheet-id'
WORKFLOW_SHEET_ID='your-workflow-sheet-id'
```

### 5.2 Or Use settings.json

Create a `settings.json` file in the project root:

```json
{
  "google": {
    "service_account_json": "{\"type\":\"service_account\",...}",
    "source_sheet_id": "your-source-sheet-id",
    "workflow_sheet_id": "your-workflow-sheet-id"
  },
  "salesrobot": {
    "api_key": "your-salesrobot-api-key",
    "base_url": "https://api.salesrobot.io/v1"
  },
  "automation": {
    "timezone": "America/Los_Angeles",
    "dry_run": true,
    "batch_size": 50
  }
}
```

## Step 6: Seed Workflow Sheet

Run the seed script to add headers to your workflow sheet:

```bash
python scripts/seed_workflow_headers.py
```

## Step 7: Run Preflight Check

Verify your setup by running the preflight check:

```bash
python scripts/preflight.py
```

This will check:
- Google credentials
- Salesrobot API key
- Google Sheets access
- Salesrobot API access
- System configuration

## Step 8: Test in Dry-Run Mode

Test the system in dry-run mode:

```bash
# Sync leads (dry-run)
python scripts/lead_sync.py --dry-run

# Enroll in campaigns (dry-run)
python scripts/campaign_enroll.py --dry-run
```

## Step 9: Set Up GitHub Actions

### 9.1 Add GitHub Secrets

Go to your GitHub repository settings:
1. Navigate to Settings > Secrets and variables > Actions
2. Click "New repository secret"
3. Add the following secrets:

| Name | Value |
|------|-------|
| `GOOGLE_SERVICE_ACCOUNT_JSON` | Your Google service account JSON (single line) |
| `SALESROBOT_API_KEY` | Your Salesrobot API key |
| `SOURCE_LEAD_SHEET_ID` | Your source Google Sheet ID |
| `WORKFLOW_SHEET_ID` | Your workflow Google Sheet ID |

### 9.2 Enable Workflows

The following workflows are available:
- **Preflight Check**: Runs Monday 8:07 AM UTC
- **Daily Ping**: Runs daily 8:17 AM UTC
- **Manual Run**: Manual trigger with options

## Step 10: Configure Source Sheet

Ensure your source sheet has the following columns:

| Column | Required |
|--------|----------|
| First Name | Yes |
| Last Name | Yes |
| Email | Yes |
| Company | Yes |
| Title | No |
| LinkedIn URL | No |
| Industry | No |
| Location | No |
| Phone | No |
| Notes | No |
| Status | No |
| Source | No |
| Campaign | No |
| Priority | No |
| Tags | No |

## Step 11: Configure Campaigns

Update `config/salesrobot.md` with your campaign IDs:

```yaml
campaigns:
  outreach_q1_2026: "YOUR_CAMPAIGN_ID_1"
  enterprise_prospects: "YOUR_CAMPAIGN_ID_2"
  smb_leads: "YOUR_CAMPAIGN_ID_3"
```

## Step 12: Run First Automation

Once everything is configured:

1. Disable dry-run mode in settings:
   ```json
   {
     "automation": {
       "dry_run": false
     }
   }
   ```

2. Run the manual workflow:
   ```bash
   python scripts/lead_sync.py
   python scripts/campaign_enroll.py
   ```

3. Monitor the workflow sheet for updates

## Troubleshooting

### Google Sheets Access Denied

**Error**: `ApiError: 403 Request had insufficient authentication scopes`

**Solution**:
1. Verify service account email is correct
2. Ensure service account has Editor access to sheets
3. Check that Google Sheets API is enabled

### Salesrobot API Error

**Error**: `401 Unauthorized`

**Solution**:
1. Verify API key is correct
2. Check API key is not expired
3. Ensure API key has necessary permissions

### Rate Limit Exceeded

**Error**: `429 Too Many Requests`

**Solution**:
1. Wait for rate limit to reset
2. Reduce batch size in settings
3. Implement client-side rate limiting

### Module Not Found

**Error**: `ModuleNotFoundError: No module named 'googleapiclient'`

**Solution**:
```bash
pip install -r requirements.txt
```

## Next Steps

- Review [LAUNCH_CHECKLIST.md](LAUNCH_CHECKLIST.md) for launch verification
- Read [config/salesrobot.md](config/salesrobot.md) for Salesrobot configuration
- Read [config/workflow_sheet_schema.md](config/workflow_sheet_schema.md) for workflow sheet details
- Read [config/orchestration.md](config/orchestration.md) for orchestration details

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review the logs in `reports/` directory
3. Check GitHub Actions logs
4. Open an issue on GitHub
