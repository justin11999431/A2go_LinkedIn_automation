# Agent Session Memory

> **Last Updated:** 2026-05-15 16:30 PT — Verified GitHub remote configured and up-to-date; Railway.app explained.

> **RULE:** Before making any changes, read this file, README.md, and any relevant .md docs in `/docs`. After completing a major task, update this file.

---

## Project Context

**Project:** A2go.ai Multi-Channel Marketing Orchestration System  
**Repo Path:** `c:\Users\cooki\.gemini\A2go_LinkedIn_automation\`  
**Purpose:** Automate personalized outreach to prospects across Email (Brevo), SMS (MessageBird), and LinkedIn (SalesRobot), with GoHighLevel (GHL) acting as the central CRM "quarterback." The system reads leads from a Google Sheet, syncs them to GHL, and manages multi-step sequences with safety pauses.  
**Business Context:** A2go.ai, Sarasota FL. Sub-account URL: `https://app.a2gotools.com/` | GHL Location ID: `70svxGoCa8ftJhU1r9cb`

---

## Current Goal

Validate end-to-end live pilot for contacts **"Sherlock Holmes"** and **"Justin Robinson"**, and ensure all GHL automations exist and are correctly configured to:
1. Kick off outreach when a new contact is synced
2. Post Email/SMS/LinkedIn activity to the GHL Unified Inbox
3. Pause all outreach on reply, appointment, or explicit stop signal

---

## Important User Requirements

- **GHL is the quarterback.** All activity (email sent, LinkedIn message sent, SMS sent) must appear in the GHL Unified Inbox / Conversations tab.
- **End-user notifications** must go to the user's GHL account (not necessarily the a2gotools.com email address).
- **New contacts entering GHL** must kick off the full sequence automatically via a GHL Workflow.
- **All GHL Workflow webhook URLs must be real** — format `https://services.leadconnectorhq.com/hooks/{locationId}/webhook-trigger/{uuid}`. Fake/placeholder URLs like `https://api.a2go.ai/...` are NOT acceptable.
- **No secrets or API keys** may be stored in this file.
- **Dry run** must be controllable via the `.env` file (`DRY_RUN=true/false`). Default is `true` (safe).
- **`AGENT_SESSION_MEMORY.md` must be read before any coding session begins.**

---

## Systems / Tools Involved

| System | Role | Auth Method |
|---|---|---|
| GoHighLevel (GHL) | CRM, Orchestration Hub, Unified Inbox | Private Integration Token (PIT) |
| Brevo | Transactional + Bulk Email | API Key (V3 xkeysib-...) |
| MessageBird | SMS (Outbound + Inbound) | API Key + Workspace Key |
| SalesRobot | LinkedIn Outreach | API Key + LinkedIn Account UUID |
| Google Sheets | Lead Data Cache | OAuth 2.0 (service account + refresh token) |
| Cloudflare | DNS / Email Auth (SPF, DKIM, DMARC) | API Token |
| SQLite (`data/automation.db`) | Local Sequence State | File-based |

---

## Files Reviewed

| File | Purpose |
|---|---|
| `src/sequencer.py` | Core orchestration engine — runs iteration over all active leads, dispatches email + LinkedIn steps, posts activity to GHL |
| `src/ghl_client.py` | GHL V2 API client — contact upsert, tag management, note creation, conversation messaging |
| `src/linkedin_adapter.py` | Wraps SalesRobot API for connection requests and follow-up messages |
| `src/sync_leads.py` | Reads Google Sheet (`A2go-Forecast-Intent-75`), maps rows, upserts contacts to GHL with tag `A2go_Sync`, creates local DB state |
| `src/lead_mapper.py` | Defines column mapping from Google Sheet structure to internal lead model |
| `src/brevo_client.py` | Transactional email via Brevo REST API |
| `src/settings.py` | Loads `settings.json` + validates required env vars |
| `src/database.py` | SQLite wrapper for `SequenceState` persistence |
| `src/webhooks/ghl_handler.py` | Inbound webhook handler from GHL (pause logic) |
| `src/webhooks/brevo_handler.py` | Inbound webhook handler from Brevo (reply detection → pause) |
| `src/webhooks/messagebird_handler.py` | Inbound webhook handler from MessageBird (SMS reply → pause) |
| `docs/A2GO_DIGITAL_MARKETING_ORCHESTRATION.md` | Master blueprint for the system architecture |
| `docs/SECRETS.txt` | Reference for credential names/locations (DO NOT store actual keys here) |
| `.env` | Live credentials — must contain all required env vars (see below) |
| `settings.json` | Fallback config — env vars take priority |
| `data/automation.db` | Active local sequence state for all leads |
| `scratch/pilot_run.py` | One-off script that manually enlists Sherlock Holmes + Justin Robinson and runs one sequencer iteration |

---

## Decisions Made

1. **Credentials Priority:** `os.getenv()` always takes priority over `settings.json`. Sequencer and all clients were updated to follow this pattern.
2. **GHL Contact Search:** Changed from `/contacts/search` (invalid) to `/contacts/` with `query` parameter for V2 compatibility.
3. **Custom Fields Format:** GHL V2 API expects `customFields` as `[{"id": "key", "value": "val"}]`. The `upsert_contact` method now auto-transforms a dict input into this format.
4. **GHL Workflows use native actions, not fake webhooks:** Because we have no publicly hosted backend server, GHL workflows should use native GHL actions (Add Tag, DND All Channels, Remove from Workflow, Add Note) rather than outbound webhook actions pointing to a fake URL.
5. **LinkedIn is NOT yet fully wired to SalesRobot production API.** The `send_connection_request` method in `linkedin_adapter.py` has a commented-out actual API call. It logs correctly but does not actually send. This is intentional until the SalesRobot endpoint is confirmed.
6. **`CLAUDE.md` does not exist in this repo.** No conflicts found.
7. **GHL Unified Inbox posting** is implemented via `GHLClient.create_conversation_message()` which calls `/conversations/messages`. It falls back to `add_note()` on failure.
8. **Railway.app** is the deployment target. It provides easy GitHub integration, free tier, and handles databases/TLS/env vars. The `railway.json` is pre-configured with gunicorn.
9. **GitHub Actions workflows** exist in `.github/workflows/` — no additional setup needed for CI/CD.

---

## Changes Completed

| File | Change |
|---|---|
| `src/sequencer.py` | Added `import os`; credentials now read from `os.getenv()` first; dry-run logic cleaned up |
| `src/linkedin_adapter.py` | Added `import os`; `__init__` now accepts `is_dry_run` param; credentials read from env vars |
| `src/ghl_client.py` | Fixed contact search endpoint (`/contacts/` + `query` param); fixed custom fields dict→list transform in `upsert_contact` |
| `src/sync_leads.py` | Fixed Google Sheet range parsing; added `linkedin_url` to `customFields` dict in GHL sync payload |
| `src/lead_mapper.py` | Reordered `SOURCE_COLUMN_MAP` to match production sheet (`A2go-Forecast-Intent-75`) column order |
| `src/settings.py` | Added `GHL_LOCATION_ID` to required env var validation |
| **GHL Workflows (browser)** | Created 3 new workflows via AI builder: `A2go Sync Tag Handler` (Published), `Appointment Status Webhook` (Published), `Stop Outreach Webhook` (Published) |
| **GHL Workflows — webhook actions** | ✅ User manually replaced all fake `https://api.a2go.ai/...` webhook actions with native GHL actions (DND All Channels, Remove from Workflow, Add Tag, Add Note). All 3 workflows confirmed Published. |
| `src/linkedin_adapter.py` | ✅ Wired real SalesRobot API: `send_connection_request` and `send_followup_message` now use `create_lead` + `enroll_lead_in_campaign`. Requires `SALESROBOT_CONNECTION_CAMPAIGN_ID` and `SALESROBOT_FOLLOWUP_CAMPAIGN_ID` in `.env`. |
| `src/sync_leads.py` | ✅ Standardized GHL credentials to use `os.getenv()` first (matching sequencer.py pattern). |
| `src/webhooks/brevo_handler.py` | ✅ Standardized GHL credentials to use `os.getenv()` first. |
| `server.py` | ✅ NEW — Unified Flask webhook server hosting `/webhooks/ghl`, `/webhooks/brevo`, `/webhooks/messagebird`, and `/health`. Optional shared-secret auth via `WEBHOOK_SECRET` env var. |
| `Procfile` | ✅ NEW — gunicorn startup command for Railway/Heroku deployment. |
| `railway.json` | ✅ NEW — Railway deployment config with health check at `/health`. |
| `requirements.txt` | ✅ Added `flask>=3.0.0` and `gunicorn>=21.2.0`. |
| `.env` | ✅ Fixed `SALESROBOT_CONNECTION_CAMPAIGN_ID` (was literal 'None') to real UUID `8612a4aa-2729-4105-9694-1f80f19be3c2`. Added `SALESROBOT_FOLLOWUP_CAMPAIGN_ID` (same campaign). Set `BREVO_SENDER_EMAIL=outreach@a2gotools.com`. Updated PORT to 8080. Added `WEBHOOK_SECRET` placeholder. |
| **GitHub Remote** | ✅ VERIFIED — Remote `origin` already configured for `https://github.com/justin11999431/A2go_LinkedIn_automation`. Master branch is up-to-date. |
| **GitHub Actions** | ✅ PRESENT — 3 workflows exist: `daily_ping.yml`, `manual_run.yml`, `preflight.yml` in `.github/workflows/`. |

---

## Tests / Validation Completed

| Test | Method | Result |
|---|---|---|
| GHL API authentication | `test_ghl_auth.py` | ✅ PASSED — Token valid, Location: A2go.ai |
| Brevo email delivery | `pilot_run.py` | ✅ PASSED — Emails delivered to `sherlock@a2go.ai` and `justin@a2go.ai` with real Message IDs |
| Local DB state advancement | `check_pilot.py` | ✅ PASSED — Both leads advanced to Email Step 1, `is_paused = false` |
| GHL contact search | Implicit via pilot run | ⚠️ PARTIAL — Returns 422 on some queries; contact sync works but lookup is not always reliable |
| LinkedIn connection request | `pilot_run.py` (dry run) | ✅ PASSED (dry run only) — Not tested in production |
| GHL Unified Inbox posting | Code review only | ⚠️ NOT LIVE TESTED — `create_conversation_message` exists but no verified message appeared in GHL |
| GHL Workflows trigger | Not tested | ❌ NOT TESTED — Workflows exist in GHL but were never triggered with a real contact |
| Webhook server local | `python server.py` + Python urllib | ✅ PASSED — `/health` returned `{"status":"ok"}` with HTTP 200 |
| SalesRobot campaign IDs | Read from SECRETS.txt + .env verified | ✅ CONFIRMED — `8612a4aa-2729-4105-9694-1f80f19be3c2` (A2go_Pat_LinkedIn) |

---

## Known Issues / Risks

1. **GHL Workflow webhook actions contain fake URLs.** The AI-generated workflows may have outbound webhook actions pointing to `https://api.a2go.ai/webhooks/ghl/pause`. These need to be **manually replaced** with:
   - Native GHL actions: **DND All Channels + Remove from Workflow + Add Tag `Outreach_Stopped`**
   - OR a real hosted endpoint (requires deploying the Python backend publicly)
   
2. **LinkedIn production calls are stubs.** `linkedin_adapter.py` line ~54: `self.client._make_request(...)` is commented out. Real SalesRobot API call must be implemented before LinkedIn goes live.

3. **No public-facing webhook receiver.** The `src/webhooks/` handlers (Brevo, MessageBird, GHL) exist in code but are not deployed anywhere. Inbound reply detection (the "pause on reply" safety mechanism) is NOT active in production.

1. **GHL Conversations API posting** — the `/conversations/messages` endpoint format for custom message types (like "LinkedIn") may not be supported natively. Needs live testing.

2. **Browser agent quota exhausted** — browser automation via the agent is unavailable for approximately 164 hours from 2026-05-14 ~15:00 PT. Manual GHL configuration required in the interim.

3. **Pilot contacts are synthetic** — `sherlock@a2go.ai` and `justin@a2go.ai` are test addresses. Real contacts have not been enrolled in production.

---

## Next Best Actions

1. ~~**[Manual — GHL]** Fix fake webhook actions~~ ✅ **DONE 2026-05-14**
2. ~~**[Code] LinkedIn Production API**~~ ✅ **DONE 2026-05-14** — `send_connection_request` + `send_followup_message` wired to SalesRobot `create_lead` + `enroll_lead_in_campaign`.
3. ~~**[Code] Credential standardization**~~ ✅ **DONE 2026-05-14** — All modules now use `os.getenv()` first for GHL credentials.
4. ~~**[REQUIRED BEFORE LINKEDIN GOES LIVE]** SalesRobot Campaign IDs~~ ✅ **DONE 2026-05-15**
   - `SALESROBOT_CONNECTION_CAMPAIGN_ID=8612a4aa-2729-4105-9694-1f80f19be3c2` (A2go_Pat_LinkedIn)
   - `SALESROBOT_FOLLOWUP_CAMPAIGN_ID=8612a4aa-2729-4105-9694-1f80f19be3c2` (same — create dedicated campaign later)
5. **[Infrastructure — ACTIVE NEXT]** Deploy `server.py` to Railway:
   - ✅ GitHub repo already configured (`https://github.com/justin11999431/A2go_LinkedIn_automation`)
   - Connect Railway to the GitHub repo
   - Set all env vars in Railway dashboard (copy from `.env`, never commit secrets)
   - Railway will provide a public URL like `https://a2go-webhooks-production.railway.app`
   - Copy that URL and configure it in:
     - **GHL**: Settings → Integrations → Webhooks — set inbound webhook URL
     - **Brevo**: Settings → Webhooks — add URL for replied/unsubscribed events
     - **MessageBird**: Flow Builder — update the HTTP action URL
6. **[Testing]** After deployment:
   - Hit `GET https://your-railway-url.railway.app/health` — expect `{"status": "ok"}`
   - Manually add tag `Stop Outreach` to a test contact in GHL — verify automation pauses in `data/automation.db`
   - Send a reply email to Brevo sender address — verify it triggers a pause
7. **[Production]** Set `DRY_RUN=false` in Railway env vars once LinkedIn campaign IDs are confirmed.

---

## Agent Instructions Going Forward

- **Read this file first, every session, before touching any code.**
- **Never store secrets, API keys, or tokens in this file or any tracked file.**
- The GHL Location ID is `70svxGoCa8ftJhU1r9cb`. The GHL sub-account URL is `https://app.a2gotools.com/`.
- The production Google Sheet tab is named **`A2go-Forecast-Intent-75`**.
- The local state database is at `data/automation.db` (SQLite). Use `check_pilot.py` to inspect it.
- `DRY_RUN=true` is the safe default. Always verify before switching to `false`.
- GHL V2 API base URL: `https://services.leadconnectorhq.com`. GHL-generated webhook trigger URLs follow the format: `https://services.leadconnectorhq.com/hooks/{locationId}/webhook-trigger/{uuid}`.
- The `CLAUDE.md` file does not exist in this repo. If it is created, read it immediately.
- When the browser quota resets, pick up from **Next Best Action #1** (fixing GHL workflow webhook actions manually or via browser automation).
- Do not claim tests passed unless you have seen real log output or a real API response confirming success.
