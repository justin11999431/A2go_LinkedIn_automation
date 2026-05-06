# LinkedIn Outreach Copy Generation

This script automates the generation of LinkedIn outreach copy using NVIDIA-hosted LLMs via the OpenAI Python SDK.

## Features

- **AI-Powered Copy Generation**: Uses NVIDIA-hosted LLMs to generate personalized LinkedIn outreach copy
- **Structured JSON Output**: Forces LLM to return copy in strict JSON format for easy parsing
- **Rate Limiting**: Includes built-in rate limiting and retry logic
- **Error Handling**: Comprehensive error handling with exponential backoff
- **Batch Processing**: Processes multiple leads efficiently
- **Workflow Integration**: Automatically updates workflow sheet with generated copy

## Prerequisites

1. **NVIDIA API Key**: Get your API key from [NVIDIA NGC](https://catalog.ngc.nvidia.com/)
2. **OpenAI Python SDK**: Install with `pip install openai`
3. **Environment Variables**: Configure NVIDIA API credentials

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file in the project root:

```bash
# NVIDIA API Configuration
NVIDIA_API_KEY=your_nvidia_api_key_here
NVIDIA_BASE_URL=https://integrate.api.nvidia.com/v1
NVIDIA_MODEL=meta/llama-3.1-70b-instruct
```

Or set environment variables directly:

```bash
export NVIDIA_API_KEY=your_nvidia_api_key_here
export NVIDIA_BASE_URL=https://integrate.api.nvidia.com/v1
export NVIDIA_MODEL=meta/llama-3.1-70b-instruct
```

### 3. Configure Google Sheets

Ensure your `settings.json` has the correct sheet IDs:

```json
{
  "google": {
    "source_sheet_id": "your_source_sheet_id",
    "workflow_sheet_id": "your_workflow_sheet_id"
  }
}
```

## Usage

### Basic Usage

Generate copy for all leads:

```bash
python scripts/generate_copy.py
```

### Testing Mode

Process a limited number of leads:

```bash
python scripts/generate_copy.py --max-leads 5
```

### Dry Run Mode

Test without making API calls:

```bash
python scripts/generate_copy.py --dry-run
```

## Output Structure

The script generates structured JSON output with the following fields:

### Research Summary
- Prospect name
- Title
- Company
- Observations
- OTIF trigger
- Personalization angle
- Confidence level
- Notes

### Warm-Up Comments
- Comment 1: Operational insight
- Comment 2: Customer/service-level angle
- Comment 3: AI, planning, or process-improvement angle

### Connection Requests
- Version A: Direct and concise
- Version B: Warmer and more contextual

### DM Sequence
- Message 1: Rapport/value message
- Message 2: Insight message
- Message 3: Soft problem hypothesis
- Message 4: Low-pressure final note

Each message includes:
- Timing
- Copy
- Personalization token
- Why it works

## Workflow Sheet Mapping

The generated copy is mapped to the workflow sheet columns:

| Column | Source |
|--------|---------|
| Lead ID | Lead name |
| Campaign Name | "A2go | Forecasting" |
| Persona | Lead title |
| Personalization Note | Personalization angle |
| Pain Point | OTIF trigger |
| Connection Request Copy | Connection request version A |
| Follow-Up 1 Copy | DM message 1 |
| Follow-Up 2 Copy | DM message 2 |
| Follow-Up 3 Copy | DM message 3 |
| Notes | Research notes |

## Rate Limiting

The script includes built-in rate limiting:

- **API Call Delay**: 2 seconds between API calls
- **Retry Logic**: Exponential backoff (2s, 4s, 8s)
- **Max Retries**: 3 attempts per lead

## Error Handling

The script handles various error scenarios:

- **JSON Parsing Errors**: Retries with exponential backoff
- **API Errors**: Retries with exponential backoff
- **Missing Data**: Uses available information and notes gaps
- **Network Errors**: Retries with exponential backoff

## Supported NVIDIA Models

The script supports any NVIDIA-hosted LLM. Popular options:

- `meta/llama-3.1-70b-instruct` (default)
- `meta/llama-3.1-405b-instruct`
- `mistralai/mistral-nemotron`
- `meta/llama-3.1-8b-instruct`

## Troubleshooting

### NVIDIA API Key Not Found

```
Error: NVIDIA_API_KEY environment variable not set
```

**Solution**: Set the `NVIDIA_API_KEY` environment variable or add it to your `.env` file.

### OpenAI Library Not Installed

```
Error: OpenAI library not installed. Run: pip install openai
```

**Solution**: Install the OpenAI library:
```bash
pip install openai
```

### JSON Parsing Errors

```
Error parsing JSON response
```

**Solution**: The script automatically retries with exponential backoff. If errors persist, check the NVIDIA model response format.

### Rate Limit Errors

```
Error: Rate limit exceeded
```

**Solution**: The script includes built-in rate limiting. If you still encounter rate limits, increase the delay between API calls.

## Best Practices

1. **Test First**: Use `--max-leads` to test with a small batch
2. **Monitor Usage**: Track NVIDIA API usage to avoid exceeding quotas
3. **Review Output**: Manually review generated copy before sending
4. **Customize Prompt**: Modify the system prompt in the script for your specific use case
5. **Update Limits**: Adjust rate limiting based on your NVIDIA API tier

## Integration with Salesrobot

The generated copy is automatically formatted for Salesrobot consumption:

- **Connection Requests**: Mapped to connection request copy field
- **DM Sequence**: Mapped to follow-up copy fields
- **Personalization**: Mapped to personalization note field
- **Pain Points**: Mapped to pain point field

## Notes

- The script uses the "B2B LinkedIn Outbound Strategist" persona for copy generation
- All copy follows LinkedIn's best practices and messaging rules
- The script avoids generic "bro-etry" and focuses on value-first messaging
- Connection requests are kept under 280 characters
- DMs are kept under 120 words
- No emojis or excessive buzzwords are used

## Support

For issues or questions:
1. Check the logs for detailed error messages
2. Verify your NVIDIA API credentials
3. Ensure Google Sheets access is configured correctly
4. Review the generated JSON output structure
