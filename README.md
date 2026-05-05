# LinkedIn Salesrobot Automation System

Complete RevOps automation repository for LinkedIn outreach with Google Sheets integration, Salesrobot orchestration, and GitHub Actions scheduling.

## Features

- **Google Sheets Integration**: Two-way sync with source and workflow sheets
- **Salesrobot Orchestration**: Automated campaign management and lead processing
- **GitHub Actions Scheduling**: Timezone-aware automation (America/Los_Angeles)
- **Human-in-Loop**: Stop conditions and manual override capabilities
- **Comprehensive Testing**: Full test suite with pytest
- **Dashboard**: Real-time metrics and monitoring

## Quick Start

1. **Clone and Setup**
   ```bash
   git clone https://github.com/justin11999431/A2go_LinkedIn_automation.git
   cd A2go_LinkedIn_automation
   pip install -r requirements.txt
   ```

2. **Configure GitHub Secrets**
   - `GOOGLE_SERVICE_ACCOUNT_JSON`: Google service account credentials
   - `SALESROBOT_API_KEY`: Salesrobot API key
   - `SOURCE_LEAD_SHEET_ID`: Source Google Sheet ID
   - `WORKFLOW_SHEET_ID`: Workflow Google Sheet ID

3. **Run Preflight Check**
   ```bash
   python scripts/preflight.py
   ```

## Project Structure

```
A2go_LinkedIn_automation/
├── .github/workflows/     # GitHub Actions workflows
├── config/               # Configuration files
├── copy/                 # Sales copy templates
├── scripts/              # Utility scripts
├── src/                  # Core Python modules
├── tests/                # Test suite
├── data/                 # Local data storage
└── reports/              # Generated reports
```

## Workflows

- **preflight**: Verify access and configuration
- **monday_start**: Monday 8:07 AM America/Los_Angeles
- **daily_ping**: Daily 8:17 AM America/Los_Angeles
- **dashboard_refresh**: Daily 9:00 AM America/Los_Angeles
- **manual_run**: Manual trigger with dry-run mode

## Documentation

- [SETUP.md](SETUP.md) - Detailed setup instructions
- [LAUNCH_CHECKLIST.md](LAUNCH_CHECKLIST.md) - Launch verification checklist
- [config/salesrobot.md](config/salesrobot.md) - Salesrobot configuration
- [config/workflow_sheet_schema.md](config/workflow_sheet_schema.md) - Workflow sheet schema
- [copy/sales_copy.md](copy/sales_copy.md) - Sales copy templates

## Testing

```bash
# Run all tests
pytest tests/

# Run specific test
pytest tests/test_google_sheets.py

# Run with coverage
pytest --cov=src tests/
```

## License

Proprietary - All rights reserved
