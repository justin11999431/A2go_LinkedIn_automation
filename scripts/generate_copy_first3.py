"""Generate copy for specific leads by name."""

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
from openai import OpenAI

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# NVIDIA API Configuration
NVIDIA_API_KEY = os.getenv('NVIDIA_API_KEY', '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')
NVIDIA_BASE_URL = os.getenv('NVIDIA_BASE_URL', 'https://integrate.api.nvidia.com/v1')
NVIDIA_MODEL = os.getenv('NVIDIA_MODEL', 'meta/llama-3.1-70b-instruct')

# System prompt (same as generate_copy.py)
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
   Provide 2 versions:
   - Version A: Direct and concise
   - Version B: Warmer and more contextual

Each connection request must:
   - Be under 280 characters
   - Avoid pitching
   - Reference a relevant business issue, post, role, or company context

4. Post-Acceptance DM Sequence
   Create a 4-message sequence:

   Message 1: Rapport/value message
   - Sent after acceptance
   - No pitch
   - Reference a relevant observation, trigger, or operational theme

   Message 2: Insight message
   - Share a useful OTIF, planning, inventory, or fulfillment insight
   - No hard pitch
   - Make the prospect feel understood

   Message 3: Soft problem hypothesis
   - Introduce a likely business issue
   - Lightly connect the issue to A2go's perspective
   - Use a permission-based CTA

   Message 4: Low-pressure final note
   - Brief and respectful
   - Offer a useful reason to continue the conversation
   - No guilt, hype, or false urgency

For each message, include:
   - Timing
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
</style_constraints>

<failure_handling>
If lead/account research is limited:
- Say what is missing.
- Label assumptions clearly.
- Still produce usable copy based on the best available hypothesis.
- Do not fabricate company events, prospect posts, metrics, or pain points.

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


def fetch_leads_by_name(sheets_client: GoogleSheetsClient, source_sheet_id: str, 
                        lead_names: List[str]) -> List[Dict[str, Any]]:
    """Fetch specific leads by name.
    
    Args:
        sheets_client: Google Sheets client
        source_sheet_id: Source sheet ID
        lead_names: List of lead names to fetch
        
    Returns:
        List of leads
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
            
            lead_name = row[name_col] if name_col < len(row) else ''
            
            # Check if this lead is in our target list
            if lead_name in lead_names:
                lead = {
                    'name': lead_name,
                    'title': row[title_col] if title_col is not None and title_col < len(row) else '',
                    'company': row[company_col] if company_col is not None and company_col < len(row) else '',
                    'linkedin_url': row[linkedin_col] if linkedin_col is not None and linkedin_col < len(row) else '',
                }
                leads.append(lead)
        
        logger.info(f"Found {len(leads)} matching leads")
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
        # Map copy data to workflow sheet columns
        row = [
            lead.get('name', ''),  # Lead ID (using name as placeholder)
            'A2go | Forecasting',  # Campaign Name
            '',  # Salesrobot Campaign ID
            '',  # Salesrobot Lead ID
            lead.get('title', ''),  # Persona
            copy_data.get('research_summary', {}).get('personalization_angle', ''),  # Personalization Note
            copy_data.get('research_summary', {}).get('otif_trigger', ''),  # Pain Point
            '',  # Offer / CTA
            copy_data.get('connection_requests', {}).get('version_a_direct', ''),  # Connection Request Copy
            copy_data.get('dm_sequence', {}).get('message_1_rapport', {}).get('copy', ''),  # Follow-Up 1 Copy
            copy_data.get('dm_sequence', {}).get('message_2_insight', {}).get('copy', ''),  # Follow-Up 2 Copy
            copy_data.get('dm_sequence', {}).get('message_3_problem_hypothesis', {}).get('copy', ''),  # Follow-Up 3 Copy
            'new',  # Automation Status
            '',  # Connection Sent Date
            '',  # Connection Accepted Date
            '',  # Last Message Sent Date
            '',  # Reply Status
            '',  # Reply Text
            '',  # Human Response Detected
            '',  # Human In Loop Owner
            datetime.now().isoformat(),  # Owner Last Action Date
            '',  # Meeting Booked
            'No',  # Opt-Out / Do Not Contact
            '',  # Error Message
            datetime.now().isoformat(),  # Last Synced At
            copy_data.get('research_summary', {}).get('notes', ''),  # Notes
        ]
        
        # Append to workflow sheet
        logger.info(f"Updating workflow sheet for lead: {lead['name']}")
        sheets_client.append_sheet_data(workflow_sheet_id, 'Sheet1!A1', [row])
        
        logger.info(f"Successfully updated workflow sheet for lead: {lead['name']}")
        return True
        
    except Exception as e:
        logger.error(f"Error updating workflow sheet for {lead['name']}: {e}")
        return False


def main():
    """Main entry point."""
    # Load settings
    settings = Settings()
    
    # Initialize NVIDIA client
    nvidia_client = OpenAI(
        base_url=NVIDIA_BASE_URL,
        api_key=NVIDIA_API_KEY
    )
    
    # Initialize Google Sheets client
    oauth_refresh_token = settings.get_oauth_refresh_token()
    oauth_client_id = settings.get_oauth_client_id()
    oauth_client_secret = settings.get_oauth_client_secret()
    
    if not oauth_refresh_token or not oauth_client_id or not oauth_client_secret:
        logger.error("OAuth credentials not found in settings")
        return
    
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
        return
    
    # Get first 3 leads from source sheet
    logger.info("Fetching first 3 leads from source sheet...")
    data = sheets_client.get_sheet_data(source_sheet_id, 'A2go-Forecast-Intent-75!A1:Z5')
    
    if not data or len(data) < 2:
        logger.error("No data found in source sheet")
        return
    
    headers = data[0]
    rows = data[1:]
    
    # Find name column
    name_col = None
    for i, header in enumerate(headers):
        if 'name' in header.lower() and 'first' not in header.lower() and 'last' not in header.lower():
            name_col = i
            break
    
    if name_col is None:
        logger.error("Could not find Name column")
        return
    
    # Get first 3 lead names
    lead_names = []
    for row in rows[:3]:
        if row and len(row) > name_col:
            lead_names.append(row[name_col])
    
    logger.info(f"Found {len(lead_names)} leads: {lead_names}")
    
    # Fetch leads by name
    leads = fetch_leads_by_name(sheets_client, source_sheet_id, lead_names)
    
    # Generate copy for each lead
    for i, lead in enumerate(leads, start=1):
        logger.info(f"Processing lead {i}/{len(leads)}: {lead['name']}")
        
        # Generate copy
        copy_data = generate_copy_for_lead(nvidia_client, lead)
        
        if copy_data:
            # Update workflow sheet
            update_workflow_sheet(sheets_client, workflow_sheet_id, lead, copy_data)
            print(f"\n{'='*60}")
            print(f"Generated copy for: {lead['name']}")
            print(f"{'='*60}")
            print(f"\nResearch Summary:")
            print(f"  Name: {copy_data.get('research_summary', {}).get('prospect_name', 'N/A')}")
            print(f"  Title: {copy_data.get('research_summary', {}).get('title', 'N/A')}")
            print(f"  Company: {copy_data.get('research_summary', {}).get('company', 'N/A')}")
            print(f"  OTIF Trigger: {copy_data.get('research_summary', {}).get('otif_trigger', 'N/A')}")
            print(f"  Confidence: {copy_data.get('research_summary', {}).get('confidence_level', 'N/A')}")
            print(f"\nConnection Request A:")
            print(f"  {copy_data.get('connection_requests', {}).get('version_a_direct', 'N/A')}")
            print(f"\nConnection Request B:")
            print(f"  {copy_data.get('connection_requests', {}).get('version_b_contextual', 'N/A')}")
            print(f"\nDM Message 1:")
            print(f"  {copy_data.get('dm_sequence', {}).get('message_1_rapport', {}).get('copy', 'N/A')}")
            print(f"\nDM Message 2:")
            print(f"  {copy_data.get('dm_sequence', {}).get('message_2_insight', {}).get('copy', 'N/A')}")
            print(f"\nDM Message 3:")
            print(f"  {copy_data.get('dm_sequence', {}).get('message_3_problem_hypothesis', {}).get('copy', 'N/A')}")
            print(f"\nDM Message 4:")
            print(f"  {copy_data.get('dm_sequence', {}).get('message_4_final_note', {}).get('copy', 'N/A')}")
            print(f"\n{'='*60}\n")
        else:
            print(f"Failed to generate copy for {lead['name']}")
        
        # Rate limiting between API calls
        if i < len(leads):
            logger.info("Waiting 2 seconds before next lead...")
            time.sleep(2)


if __name__ == '__main__':
    main()
