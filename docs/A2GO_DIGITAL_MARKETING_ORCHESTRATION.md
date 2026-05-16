# A2GO Digital Marketing Orchestration

## Overview
This document defines the high-level orchestration logic for the A2go.ai Digital Marketing Workflow. It serves as the master blueprint for multi-channel outreach, safety protocols, and CRM integration.

## Core Architecture
- **CRM Quarterback**: GoHighLevel (GHL) is the central source of truth and orchestration engine.
- **Email**: Brevo handles all outbound email communication.
- **SMS**: MessageBird handles all outbound SMS communication.
- **LinkedIn**: SalesRobot handles all LinkedIn outreach and engagement.
- **Domain/DNS**: Cloudflare manages the A2go.ai domain, DNS, and email authentication (SPF, DKIM, DMARC).
- **Backend**: Python-based orchestration layer that owns the business logic, safety checks, and cross-channel coordination.

## Integration Map
| System | Role | Primary Function |
|--------|------|------------------|
| GoHighLevel | CRM | Lead management, pipeline tracking, trigger center |
| Brevo | Email | Bulk and transactional email outreach |
| MessageBird | SMS | SMS outreach and two-way messaging |
| SalesRobot | LinkedIn | Connection requests, messaging, and profile engagement |
| Google Sheets | Data Cache | Temporary storage for lead processing and mapping |
| Cloudflare | Infrastructure | Domain management and email security |

## Safety Protocols (Human-In-The-Loop)
### Unified Pause Logic
Any event that indicates a need for human intervention MUST trigger a unified pause across ALL channels.

**Unified Function:** `pauseContactAutomation(contactId, reason)`

**Triggers for Pause:**
- Prospect reply (any channel)
- Rep reply (any channel)
- Unsubscribe request
- SMS "STOP" received
- LinkedIn reply received
- Appointment booked
- Do Not Contact (DNC) event

### Implementation Rules
1. **GHL First**: When `pauseContactAutomation` is called, the status must first be updated in GoHighLevel to stop any active GHL workflows.
2. **Channel Propagation**: The pause command must then propagate to Brevo, MessageBird, and SalesRobot to cancel any scheduled tasks for that contact.
3. **Safety First**: If any channel fails to acknowledge the pause, a high-priority alert must be sent to the operations team.

## Data Flow
1. **Lead Intake**: Leads enter via GHL or are imported from validated sources.
2. **Validation**: Backend validates lead data (email format, LinkedIn URL, etc.).
3. **Orchestration**: Backend determines the next best action based on campaign logic.
4. **Execution**: Backend calls the appropriate service (Brevo, SalesRobot, etc.).
5. **Sync**: Results and engagement data are synced back to GHL.

## Critical Rules
- **No Direct Channel Logic**: Channels must not have their own independent pause logic. All pauses must go through the unified `pauseContactAutomation` function.
- **Dry Run Default**: All automation must default to `dry_run: True` until explicitly toggled for production.
- **Human Priority**: Any manual update in GHL or the Workflow Sheet must override automated actions.
