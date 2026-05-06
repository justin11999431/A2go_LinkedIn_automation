#!/usr/bin/env python3
"""Generate LinkedIn outreach copy using NVIDIA-hosted LLM."""

import os
import sys
import json
import logging
import time
from typing import Dict, Any, List, Optional
from datetime import datetime

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from google_sheets import GoogleSheetsClient
from settings import Settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# NVIDIA API Configuration
NVIDIA_API_KEY = os.getenv('NVIDIA_API_KEY')
NVIDIA_BASE_URL = os.getenv('NVIDIA_BASE_URL', 'https://integrate.api.nvidia.com/v1')
NVIDIA_MODEL = os.getenv('NVIDIA_MODEL', 'meta/llama-3.1-70b-instruct')

# System prompt for B2B LinkedIn Outbound Strategist
SYSTEM_PROMPT = """You are a senior B2B LinkedIn outbound strategist and copywriter specializing in supply chain, industrial manufacturing, distribution, OTIF improvement, and AI-enabled operations.

<context>
Company: A2go.ai
Solution: An AI Agent team / Decision Intelligence Platform that helps industrial manufacturers and distributors improve OTIF, reduce operational firefighting, and make better supply-chain decisions using AI agents on top of existing systems.

Positioning:
- A2go helps companies move from reactive supply-chain firefighting to predictive operational control.
- The solution is relevant when companies struggle with late shipments, order promise failures, premium freight, customer escalations, inventory imbalance, manual expediting, poor visibility, or disconnected planning systems.
- Do not invent ROI claims, case studies, customer names, or performance metrics.
- Use the provided white paper, source material, and approved A2go positioning as the source of truth.
</context>

<inputs>
I will provide:
1. A list of target leads.
2. Their company names.
3. Their LinkedIn profile URLs or profile summaries.
4. Their company LinkedIn pages or website context when available.
5. Any relevant source material about A2go.ai, including the white paper.

For each lead, use the provided LinkedIn/account context to create tailored research insights and messaging copy.
</inputs>

<research_goal>
For each lead/account, identify only the research needed to write relevant LinkedIn copy.

Research for:
- Recent company events
- Operational growth signals
- Hiring signals related to supply chain, operations, planning, ERP, logistics, customer service, or distribution
- Public posts from the lead or company
- Language the company uses around customers, service levels, reliability, growth, operational excellence, AI, automation, or supply chain
- Likely OTIF-related pain triggers
- Relevant personalization hooks

Do not scrape LinkedIn or use prohibited automation.
Use only compliant, public, or user-provided information.
If there is not enough information, use a clearly labeled hypothesis instead of pretending to know.
</research_goal>

<linkedin_messaging_rules>
Follow these rules:

1. Warm up before connecting:
   - Create 2–3 thoughtful comment options based on the prospect's or company's recent posts.
   - Comments should add useful perspective, not pitch A2go.

2. Value-first messaging:
   - Do not pitch in the connection request.
   - Do not pitch in the first DM after acceptance.
   - Start with relevance, curiosity, and operational insight.
   - Introduce A2go only after a useful problem hypothesis or insight has been shared.

3. Avoid generic "bro-etry":
   - No vague one-line paragraphs.
   - No empty motivational phrases.
   - No clickbait.
   - No fake personalization.
   - No generic AI hype.

4. Executive tone:
   - Clear, practical, commercially aware, and concise.
   - Sound like someone who understands supply-chain and operations tradeoffs.
   - Use specific language around OTIF, promise dates, late shipments, expedite costs, inventory, fulfillment, ERP/planning systems, and customer service.

5. Connection request mindset (critical):
   - A connection request is not a sales message. It is an audition for the right to be in the prospect's feed without being filtered as spam. Write to earn the connect, not to sell.
   - The "salesy" feeling in cold outreach comes from the lie — pretending to want connection while obviously wanting to pitch. Disarm by being honest that it's cold, or genuinely have no ask beyond the connection itself.
   - With only name, title, and industry, speak to the role and the industry, not the person. Generic compliments tied to a title ("impressed by your experience as VP of Supply Chain") are immediate spam signals.
   - Drop the "I" opening. Open with them, their world, or an observation — not the sender's perception of them.
   - Skip the fake compliment entirely. If something specifically and verifiably true cannot be said, say nothing complimentary.
   - Specificity beats flattery. The job is to signal "I understand your world," not "I admire you."

6. Forbidden phrases and openers (do not use in connection requests or first-touch DMs):
   - "I came across your profile" / "I noticed your profile" / "Your profile caught my eye"
   - "I was impressed by…" / "Impressed with your experience" / "Your background is impressive"
   - "I'd love to connect" / "I'd love to discuss" / "I'd love to chat" / "I'd love to explore"
   - "Quick question" / "Picking your brain" / "Pick your brain"
   - "Hope this finds you well" / "Hope you're having a great week"
   - Any first-message mention of A2go, the platform, AI agents, decision intelligence, or what the product does
   - Any opening sentence that begins with "I"
   - Any compliment about the prospect's "experience," "career," "track record," or "leadership"
</linkedin_messaging_rules>

<output_required>
For each lead, provide only the following:

1. Lead Research Summary
   - Prospect name
   - Title
   - Company
   - Relevant company/account observations
   - Likely OTIF or operational trigger
   - Personalization angle
   - Confidence level: High / Medium / Low
   - Notes on missing or uncertain information

2. LinkedIn Warm-Up Comments
   Provide 3 options:
   - Comment 1: Operational insight
   - Comment 2: Customer/service-level angle
   - Comment 3: AI, planning, or process-improvement angle

   Each comment should:
   - Be specific to the lead, company, or post topic
   - Avoid pitching
   - Sound natural and thoughtful
   - Be 1–3 sentences

3. Connection Request
   Provide 2 versions, each under 280 characters, neither containing a pitch, neither mentioning A2go or what the sender sells.

   Version A — Honest cold / explicit disarm
   - Names the cold reach openly. Includes an explicit disarm phrase ("no pitch," "not selling," "no agenda," "won't pretend otherwise").
   - Frames the sender as a peer building a deliberate network, not a vendor working a list.
   - No CTA beyond the connection itself.
   - Example structure: "[Name] — cold connect, won't pretend otherwise. Building out my network of [industry] operators deliberately and you came up. No pitch. Open to a hello?"

   Version B — Role-specific observation
   - Opens with a real, current pressure facing people in their exact role/industry. Signals understanding of their world without faking research that wasn't actually done.
   - No ask beyond the connect. May include a soft disarm.
   - Example structure: "Hi [Name] — most [role]s in [industry] I'm talking to right now are wrestling with [specific current pressure]. Connecting with operators in the trenches, that's it. No agenda."

   Both versions must:
   - Avoid every phrase in the Forbidden list.
   - Sound like a peer texting a peer, not a vendor pitching a target.
   - Contain zero references to A2go or what the sender sells.
   - Have no CTA beyond the connection itself.
   - Read naturally if the prospect read it out loud.

4. Post-Acceptance DM Sequence
   Create a 4-message sequence:

   Message 1: Rapport/value message
   - Sent after acceptance.
   - No pitch. No mention of A2go, the platform, or what it does.
   - Open with the prospect's world, not the sender's. Reference a relevant operational theme, role-level pressure, or specific recent post/company event.
   - Optional: a single short line acknowledging the connect, then immediately move to value or perspective. Do not gush.
   - The disarm tone from the connection request carries forward — still earning trust, not yet pitching.

   Message 2: Insight message
   - Share a useful OTIF, planning, inventory, or fulfillment insight.
   - No hard pitch.
   - Make the prospect feel understood.
   - Speak in operator language. Specifics over abstractions.
   - The insight should be genuinely useful to them even if they never reply.

   Message 3: Soft problem hypothesis
   - Introduce a likely business issue.
   - Lightly connect the issue to A2go's perspective (this is the first message where A2go can be named, and only briefly).
   - Use a permission-based CTA ("worth a 15-min compare-notes?" / "want me to send the one-pager?").

   Message 4: Low-pressure final note
   - Brief and respectful.
   - Offer a useful reason to continue the conversation.
   - No guilt, hype, or false urgency.
   - Leave the door open without rattling it.

   For each message, include:
   - Timing (e.g., "Day 0 after accept," "Day 4," "Day 9," "Day 16")
   - Message copy
   - Personalization token used
   - Why this message works

5. Optional Persona Adjustment
   If the lead's title is one of the following, slightly adjust the angle:
   - COO / President / GM: business performance, customer commitments, operating rhythm, margin leakage
   - VP Supply Chain: OTIF, inventory, planning, supplier reliability, exception management
   - VP Operations: throughput, fulfillment, expediting, plant/DC coordination, process reliability
   - CFO: premium freight, working capital, margin leakage, cash conversion, customer penalties

Do not include broad ICP analysis, strategy tables, A/B tests, quality checklists, implementation plans, or general outbound advice unless specifically requested.
</output_required>

<style_constraints>
- Keep DMs under 120 words.
- Keep connection requests under 280 characters.
- Use plain English.
- Avoid excessive buzzwords.
- Avoid emojis.
- Avoid over-personalization that feels fake.
- Make the copy feel researched, relevant, and commercially mature.
- Use natural paragraphing, not one-line "bro-etry."
- Voice in cold messages is peer-to-peer (operator-to-operator), not vendor-to-prospect.
- Default to honesty about cold reach over manufactured warmth. A Josh Braun-style disarm ("cold connect, no pitch") outperforms fake familiarity every time.
- Specificity beats flattery. Skip the compliment if it cannot be made specifically and verifiably true.
- If the message could have been sent by a bot to 10,000 people with name/title swapped in, rewrite it.
</style_constraints>

<failure_handling>
If lead/account research is limited:
- Say what is missing.
- Label assumptions clearly.
- Still produce usable copy based on the best available hypothesis.
- Do not fabricate company events, prospect posts, metrics, or pain points.
- When research is thin, lean harder into Version A (honest cold) for the connection request — it does not require personalization to land, only honesty.

If the A2go white paper or positioning material is missing:
- Use only the A2go context provided in this prompt.
- Avoid specific product claims or quantified results.
- Keep the copy focused on problem awareness and discovery rather than proof claims.
</failure_handling>

IMPORTANT: You must respond with valid JSON only. No markdown, no code blocks, no explanations. Just the JSON object with the following structure:
{
  "research_summary": {
    "prospect_name": "string",
    "title": "string",
    "company": "string",
    "observations": "string",
    "otif_trigger": "string",
    "personalization_angle": "string",
    "confidence_level": "High/Medium/Low",
    "notes": "string"
  },
  "warm_up_comments": {
    "comment_1_operational": "string",
    "comment_2_customer_service": "string",
    "comment_3_ai_planning": "string"
  },
  "connection_requests": {
    "version_a_direct": "string",
    "version_b_contextual": "string"
  },
  "dm_sequence": {
    "message_1_rapport": {
      "timing": "string",
      "copy": "string",
      "personalization_token": "string",
      "why_it_works": "string"
    },
    "message_2_insight": {
      "timing": "string",
      "copy": "string",
      "personalization_token": "string",
      "why_it_works": "string"
    },
    "message_3_problem_hypothesis": {
      "timing": "string",
      "copy": "string",
      "personalization_token": "string",
      "why_it_works": "string"
    },
    "message_4_final_note": {
      "timing": "string",
      "copy": "string",
      "personalization_token": "string",
      "why_it_works": "string"
    }
  }
}"""


def validate_nvidia_config() -> bool:
    """Validate NVIDIA API configuration.
    
    Returns:
        True if configuration is valid
    """
    if not NVIDIA_API_KEY:
        logger.error("NVIDIA_API_KEY environment variable not set")
        return False
    
    if not NVIDIA_BASE_URL:
        logger.error("NVIDIA_BASE_URL environment variable not set")
        return False
    
    if not NVIDIA_MODEL:
        logger.error("NVIDIA_MODEL environment variable not set")
        return False
    
    return True


def initialize_nvidia_client():
    """Initialize NVIDIA OpenAI client.
    
    Returns:
        OpenAI client or None
    """
    try:
        from openai import OpenAI
        
        client = OpenAI(
            base_url=NVIDIA_BASE_URL,
            api_key=NVIDIA_API_KEY
        )
        
        logger.info(f"Initialized NVIDIA client with model: {NVIDIA_MODEL}")
        return client
    except ImportError:
        logger.error("OpenAI library not installed. Run: pip install openai")
        return None
    except Exception as e:
        logger.error(f"Error initializing NVIDIA client: {e}")
        return None


def fetch_leads_needing_copy(sheets_client: GoogleSheetsClient, source_sheet_id: str) -> List[Dict[str, Any]]:
    """Fetch leads that need copy generation.
    
    Args:
        sheets_client: Google Sheets client
        source_sheet_id: Source sheet ID
        
    Returns:
        List of leads needing copy
    """
    try:
        # Fetch all leads from source sheet
        logger.info(f"Fetching leads from source sheet: {source_sheet_id}")
        data = sheets_client.get_sheet_data(source_sheet_id, 'A2go-Forecast-Intent-75!A1:Z1000')
        
        if not data or len(data) < 2:
            logger.warning("No data found in source sheet")
            return []
        
        headers = data[0]
        rows = data[1:]
        
        # Find column indices
        name_col = None
        title_col = None
        company_col = None
        linkedin_col = None
        
        for i, header in enumerate(headers):
            header_lower = header.lower()
            if 'name' in header_lower and 'first' not in header_lower and 'last' not in header_lower:
                name_col = i
            elif 'title' in header_lower:
                title_col = i
            elif 'company' in header_lower or 'employer' in header_lower:
                company_col = i
            elif 'linkedin' in header_lower:
                linkedin_col = i
        
        if name_col is None:
            logger.error("Could not find Name column in source sheet")
            return []
        
        # Parse leads
        leads = []
        for row in rows:
            if not row or len(row) <= name_col:
                continue
            
            lead = {
                'name': row[name_col] if name_col < len(row) else '',
                'title': row[title_col] if title_col is not None and title_col < len(row) else '',
                'company': row[company_col] if company_col is not None and company_col < len(row) else '',
                'linkedin_url': row[linkedin_col] if linkedin_col is not None and linkedin_col < len(row) else '',
            }
            
            # Only include leads with at least a name
            if lead['name']:
                leads.append(lead)
        
        logger.info(f"Found {len(leads)} leads needing copy generation")
        return leads
        
    except Exception as e:
        logger.error(f"Error fetching leads: {e}")
        return []


def generate_copy_for_lead(nvidia_client, lead: Dict[str, Any], retry_count: int = 0) -> Optional[Dict[str, Any]]:
    """Generate LinkedIn copy for a single lead.
    
    Args:
        nvidia_client: NVIDIA OpenAI client
        lead: Lead data
        retry_count: Current retry attempt
        
    Returns:
        Generated copy or None
    """
    try:
        # Construct user message with lead context
        user_message = f"""Generate LinkedIn outreach copy for the following lead:

Prospect Name: {lead['name']}
Title: {lead['title']}
Company: {lead['company']}
LinkedIn URL: {lead['linkedin_url']}

Please generate the LinkedIn outreach copy following the system prompt requirements."""
        
        # Call NVIDIA API
        logger.info(f"Generating copy for lead: {lead['name']}")
        
        completion = nvidia_client.chat.completions.create(
            model=NVIDIA_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message}
            ],
            temperature=0.6,
            top_p=0.7,
            max_tokens=4096,
            response_format={"type": "json_object"}
        )
        
        # Extract response
        response_text = completion.choices[0].message.content
        
        # Parse JSON
        try:
            copy_data = json.loads(response_text)
            logger.info(f"Successfully generated copy for lead: {lead['name']}")
            return copy_data
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON response for {lead['name']}: {e}")
            logger.error(f"Response text: {response_text[:500]}...")
            
            # Retry if we haven't exceeded max retries
            if retry_count < 3:
                logger.info(f"Retrying (attempt {retry_count + 1}/3)...")
                time.sleep(2 ** retry_count)  # Exponential backoff
                return generate_copy_for_lead(nvidia_client, lead, retry_count + 1)
            
            return None
            
    except Exception as e:
        logger.error(f"Error generating copy for {lead['name']}: {e}")
        
        # Retry if we haven't exceeded max retries
        if retry_count < 3:
            logger.info(f"Retrying (attempt {retry_count + 1}/3)...")
            time.sleep(2 ** retry_count)  # Exponential backoff
            return generate_copy_for_lead(nvidia_client, lead, retry_count + 1)
        
        return None


def update_workflow_sheet(sheets_client: GoogleSheetsClient, workflow_sheet_id: str,
                          lead: Dict[str, Any], copy_data: Dict[str, Any]) -> bool:
    """Update workflow sheet with generated copy.

    Args:
        sheets_client: Google Sheets client
        workflow_sheet_id: Workflow sheet ID
        lead: Lead data
        copy_data: Generated copy data

    Returns:
        True if successful
    """
    try:
        # Find the next empty row
        sheet_data = sheets_client.get_sheet_data(workflow_sheet_id, 'Sheet1')

        # Start from row 2 (after header, 1-based indexing)
        next_row = 2
        for i, row in enumerate(sheet_data[1:], start=2):  # Skip header row
            # Check if row is empty (all cells are empty)
            if not any(cell.strip() for cell in row if cell):
                next_row = i
                break
        else:
            # If all rows are filled, append to the end
            next_row = len(sheet_data) + 1

        # Map copy data to workflow sheet columns
        # Based on the actual workflow sheet schema
        row = [
            lead.get('name', ''),  # Lead ID (using name as placeholder)
            lead.get('linkedin_url', ''),  # LinkedIn Profile URL
            lead.get('first_name', ''),  # First Name
            lead.get('last_name', ''),  # Last Name
            lead.get('company', ''),  # Company
            lead.get('title', ''),  # Title
            lead.get('industry', ''),  # Industry
            lead.get('location', ''),  # Location
            '',  # Connection Status
            '',  # Current Step
            '',  # Step Status
            '',  # Last Action Date
            '',  # Next Action Date
            copy_data.get('connection_requests', {}).get('version_a_direct', ''),  # Connection Request Message
            copy_data.get('dm_sequence', {}).get('message_1_rapport', {}).get('copy', ''),  # First Follow-up Message
            copy_data.get('dm_sequence', {}).get('message_2_insight', {}).get('copy', ''),  # Second Follow-up Message
            copy_data.get('dm_sequence', {}).get('message_3_problem_hypothesis', {}).get('copy', ''),  # Third Follow-up Message
            copy_data.get('dm_sequence', {}).get('message_4_final_note', {}).get('copy', ''),  # Fourth Follow-up Message
            '',  # Fifth Follow-up Message
            '',  # Sixth Follow-up Message
            '',  # Seventh Follow-up Message
            '',  # Eighth Follow-up Message
            '',  # Ninth Follow-up Message
            '',  # Tenth Follow-up Message
            copy_data.get('research_summary', {}).get('notes', ''),  # Notes
            datetime.now().isoformat(),  # Last Updated
        ]

        # Update the specific row
        range_name = f'Sheet1!A{next_row}:Z{next_row}'
        logger.info(f"Updating workflow sheet for lead: {lead['name']} at row {next_row}")
        sheets_client.update_sheet_data(workflow_sheet_id, range_name, [row])

        logger.info(f"Successfully updated workflow sheet for lead: {lead['name']} at row {next_row}")
        return True

    except Exception as e:
        logger.error(f"Error updating workflow sheet for {lead['name']}: {e}")
        return False


def generate_copy_for_all_leads(settings: Settings, max_leads: Optional[int] = None) -> Dict[str, Any]:
    """Generate copy for all leads.
    
    Args:
        settings: Settings object
        max_leads: Maximum number of leads to process (for testing)
        
    Returns:
        Generation results
    """
    results = {
        'timestamp': datetime.now().isoformat(),
        'total_leads': 0,
        'processed_leads': 0,
        'successful_leads': 0,
        'failed_leads': 0,
        'errors': [],
    }
    
    try:
        # Validate NVIDIA configuration
        if not validate_nvidia_config():
            return results
        
        # Initialize NVIDIA client
        nvidia_client = initialize_nvidia_client()
        if not nvidia_client:
            return results
        
        # Initialize Google Sheets client
        oauth_refresh_token = settings.get_oauth_refresh_token()
        oauth_client_id = settings.get_oauth_client_id()
        oauth_client_secret = settings.get_oauth_client_secret()
        
        if not oauth_refresh_token or not oauth_client_id or not oauth_client_secret:
            logger.error("OAuth credentials not found in settings")
            return results
        
        sheets_client = GoogleSheetsClient(
            oauth_refresh_token=oauth_refresh_token,
            client_id=oauth_client_id,
            client_secret=oauth_client_secret
        )
        
        # Get sheet IDs
        source_sheet_id = settings.get_source_sheet_id()
        workflow_sheet_id = settings.get_workflow_sheet_id()
        
        if not source_sheet_id or not workflow_sheet_id:
            logger.error("Source or workflow sheet ID not found in settings")
            return results
        
        # Fetch leads needing copy
        leads = fetch_leads_needing_copy(sheets_client, source_sheet_id)
        
        if not leads:
            logger.warning("No leads found needing copy generation")
            return results
        
        results['total_leads'] = len(leads)
        
        # Limit leads for testing if specified
        if max_leads and max_leads < len(leads):
            leads = leads[:max_leads]
            logger.info(f"Limited to {max_leads} leads for testing")
        
        # Generate copy for each lead
        for i, lead in enumerate(leads, start=1):
            logger.info(f"Processing lead {i}/{len(leads)}: {lead['name']}")
            results['processed_leads'] += 1
            
            # Generate copy
            copy_data = generate_copy_for_lead(nvidia_client, lead)
            
            if copy_data:
                # Update workflow sheet
                if update_workflow_sheet(sheets_client, workflow_sheet_id, lead, copy_data):
                    results['successful_leads'] += 1
                else:
                    results['failed_leads'] += 1
                    results['errors'].append({
                        'lead_name': lead['name'],
                        'error': 'Failed to update workflow sheet'
                    })
            else:
                results['failed_leads'] += 1
                results['errors'].append({
                    'lead_name': lead['name'],
                    'error': 'Failed to generate copy'
                })
            
            # Rate limiting between API calls
            if i < len(leads):
                logger.info("Waiting 2 seconds before next lead...")
                time.sleep(2)
        
        logger.info(f"Copy generation complete: {results['successful_leads']}/{results['processed_leads']} successful")
        
    except Exception as e:
        logger.error(f"Error during copy generation: {e}")
        results['errors'].append({
            'error': str(e)
        })
    
    return results


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate LinkedIn outreach copy using NVIDIA LLM')
    parser.add_argument('--max-leads', type=int, help='Maximum number of leads to process (for testing)')
    parser.add_argument('--dry-run', action='store_true', help='Run in dry-run mode (no API calls)')
    args = parser.parse_args()
    
    # Load settings
    settings = Settings()
    
    if args.dry_run:
        logger.info("Running in dry-run mode (no API calls)")
        logger.info("This would process leads and generate copy using NVIDIA LLM")
        logger.info(f"Max leads: {args.max_leads if args.max_leads else 'unlimited'}")
        return
    
    # Run copy generation
    results = generate_copy_for_all_leads(settings, args.max_leads)
    
    # Print results
    print("\n" + "="*60)
    print("COPY GENERATION RESULTS")
    print("="*60)
    print(f"Timestamp: {results['timestamp']}")
    print(f"Total Leads: {results['total_leads']}")
    print(f"Processed Leads: {results['processed_leads']}")
    print(f"Successful Leads: {results['successful_leads']}")
    print(f"Failed Leads: {results['failed_leads']}")
    
    if results['errors']:
        print(f"\nErrors: {len(results['errors'])}")
        for error in results['errors']:
            print(f"  - {error}")
    
    print("="*60 + "\n")
    
    # Exit with appropriate code
    sys.exit(0 if results['failed_leads'] == 0 else 1)


if __name__ == '__main__':
    main()
