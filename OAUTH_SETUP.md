# OAuth 2.0 Setup Guide

## Overview

Since you cannot create a service account API key due to organization admin settings, we'll use OAuth 2.0 authentication instead.

## What You Need

You need your OAuth 2.0 credentials from Google Cloud Console:

- **Client ID**: Your OAuth client ID
- **Client Secret**: Your OAuth client secret

## Step 1: Get Your OAuth Credentials

If you don't have OAuth credentials yet:

1. Go to Google Cloud Console: https://console.cloud.google.com/
2. Create a new project or select existing one
3. Enable Google Sheets API
4. Go to APIs & Services > Credentials
5. Create OAuth 2.0 Client ID:
   - Application type: "Web application"
   - Name: "LinkedIn Automation"
   - Authorized redirect URIs: `http://localhost:8080`
6. Copy your Client ID and Client Secret

## Step 2: Get Refresh Token

### Option A: Use the Automated Script (Recommended)

1. **Install additional dependencies**:
   ```bash
   cd C:\Users\cooki\.gemini\A2go_LinkedIn_automation
   pip install google-auth-oauthlib
   ```

2. **Set your OAuth credentials**:
   ```bash
   # Windows PowerShell
   $env:OAUTH_CLIENT_ID="your-client-id-here"
   $env:OAUTH_CLIENT_SECRET="your-client-secret-here"
   
   # Or edit scripts/get_oauth_token.py and replace the placeholders
   ```

3. **Run the OAuth token script**:
   ```bash
   python scripts/get_oauth_token.py
   ```

4. **Follow the prompts**:
   - A browser window will open
   - Sign in to your Google account
   - Grant permissions to access Google Sheets
   - The script will automatically get your refresh token

5. **Save the refresh token**:
   - The script will display your refresh token
   - Copy it for the next step

### Option B: Manual Authorization

1. Go to OAuth Playground: https://developers.google.com/oauthplayground/

2. Configure OAuth playground:
   - Click the gear icon (⚙️) in the top right
   - Check "Use your own OAuth credentials"
   - Enter your Client ID and Client Secret
   - Click "Save"

3. Select scopes:
   - Find "Google Sheets API"
   - Expand it and select:
     - `https://www.googleapis.com/auth/spreadsheets`
   - Click "Authorize APIs"

4. Authorize:
   - Sign in to your Google account
   - Grant permissions
   - You'll be redirected back to OAuth playground

5. Exchange authorization code:
   - Click "Exchange authorization code for tokens"
   - You'll see your refresh token in the response

## Step 3: Add OAuth Credentials to GitHub

Go to: https://github.com/justin11999431/A2go_LinkedIn_automation/settings/secrets/actions

Add these 3 secrets:

### 1. OAUTH_REFRESH_TOKEN
```
your-refresh-token-here
```

### 2. OAUTH_CLIENT_ID
```
your-client-id-here
```

### 3. OAUTH_CLIENT_SECRET
```
your-client-secret-here
```

## Step 4: Add Sheet IDs

Add these 2 secrets:

### 4. SOURCE_LEAD_SHEET_ID
```
1nCyhA1ubXaCljUJ0ON6y1v6czRzXlFoT5MRzeeX7Fns
```

### 5. WORKFLOW_SHEET_ID
```
1PLG4IMml1ha5VIxlOny7UO134tjhwCa1bAGxp6xs6O4
```

## Step 5: Share Your Google Sheets

**Important**: You need to share your Google Sheets with the OAuth client email.

### Find Your OAuth Client Email

Your OAuth client email is typically:
```
[client-id]@developer.gserviceaccount.com
```

Example: `1234567890-abcdef@developer.gserviceaccount.com`

### Share Both Sheets

1. **Source Sheet**:
   - Open your source Google Sheet
   - Click "Share"
   - Paste your OAuth client email
   - Grant "Editor" permissions
   - Click "Send"

2. **Workflow Sheet**:
   - Open your workflow Google Sheet
   - Click "Share"
   - Paste your OAuth client email
   - Grant "Editor" permissions
   - Click "Send"

## Step 6: Test the Setup

### Run Preflight Check

```bash
cd C:\Users\cooki\.gemini\A2go_LinkedIn_automation
python scripts/preflight.py
```

This should now pass with OAuth credentials!

### Test in Dry-Run Mode

```bash
python scripts/lead_sync.py --dry-run
python scripts/campaign_enroll.py --dry-run
```

## How OAuth 2.0 Works

### Authentication Flow

1. **One-time setup**: You authorize the application once
2. **Refresh token**: You get a refresh token that doesn't expire
3. **Access token**: The refresh token is used to get short-lived access tokens
4. **Automatic refresh**: The system automatically refreshes access tokens when needed

### Advantages

✅ **No service account needed**: Works with your existing OAuth credentials
✅ **Automatic token refresh**: No manual intervention needed
✅ **Secure**: Uses industry-standard OAuth 2.0
✅ **Reliable**: Works well with automation and GitHub Actions

### Token Storage

- **Refresh token**: Stored in GitHub Secrets (never expires)
- **Access token**: Generated automatically when needed (expires in 1 hour)
- **Token file**: `oauth_token.json` created locally for reference

## Troubleshooting

### Error: "Invalid Grant"

**Cause**: Refresh token has been revoked or is invalid

**Solution**:
1. Re-run the authorization script
2. Get a new refresh token
3. Update the GitHub secret

### Error: "Access Denied"

**Cause**: OAuth client doesn't have access to the sheets

**Solution**:
1. Verify you shared the sheets with the OAuth client email
2. Check that you granted "Editor" permissions
3. Make sure the sheet IDs are correct

### Error: "Token Expired"

**Cause**: Access token expired (should auto-refresh)

**Solution**:
- This should happen automatically
- If it persists, check your refresh token is valid

## Security Notes

⚠️ **Important Security Considerations**:

1. **Keep secrets secure**: Never commit secrets to version control
2. **Rotate tokens**: Consider rotating refresh tokens periodically
3. **Monitor access**: Check Google Account security settings for unauthorized access
4. **Revoke if needed**: You can revoke access from Google Account settings

## Summary

You now have a complete OAuth 2.0 setup that:

✅ Works without service account API keys
✅ Uses your existing OAuth credentials
✅ Automatically refreshes tokens
✅ Integrates with GitHub Actions
✅ Provides secure authentication

## Next Steps

1. Get your OAuth credentials from Google Cloud Console
2. Run the OAuth token script to get your refresh token
3. Add all 5 secrets to GitHub
4. Share your Google Sheets with the OAuth client email
5. Run preflight check to verify everything works
6. Test in dry-run mode before going live

The system is now ready to use OAuth 2.0 authentication! 🎉
