# Salesrobot Configuration

## API Configuration

### Base URL
```
https://api.salesrobot.io/v1
```

### Authentication
- **Method**: Bearer Token
- **Header**: `Authorization: Bearer <API_KEY>`
- **API Key**: Set via `SALESROBOT_API_KEY` environment variable or settings

## Campaigns

### Campaign Structure
```json
{
  "name": "Campaign Name",
  "description": "Campaign description",
  "settings": {
    "timezone": "America/Los_Angeles",
    "daily_limit": 50,
    "message_delay": 300,
    "connection_request_limit": 25
  }
}
```

### Campaign IDs
Update these with your actual campaign IDs:

```yaml
campaigns:
  outreach_q1_2026: "CAMPAIGN_ID_1"
  enterprise_prospects: "CAMPAIGN_ID_2"
  smb_leads: "CAMPAIGN_ID_3"
```

## Lead Management

### Lead Status Mapping
| Salesrobot Status | Internal Status |
|------------------|-----------------|
| new | new |
| invited | connection_requested |
| connected | connected |
| message_sent | first_message_sent |
| replied | replied |
| interested | interested |
| not_interested | not_interested |
| opted_out | opted_out |
| blocked | blocked |
| error | error |

### Lead Fields
- `first_name`: Lead's first name
- `last_name`: Lead's last name
- `email`: Lead's email address
- `company`: Lead's company name
- `title`: Lead's job title
- `linkedin_url`: LinkedIn profile URL
- `industry`: Industry
- `location`: Location
- `phone`: Phone number
- `notes`: Notes
- `status`: Current status
- `campaign_id`: Associated campaign ID

## Rate Limits

### Default Limits
- **Connection Requests**: 50 per day
- **Messages**: 200 per day
- **Profile Views**: 500 per day

### Rate Limit Handling
- Automatic retry with exponential backoff
- Respect `Retry-After` header
- Stop automation if rate limit exceeded

## Error Handling

### Common Errors
- **401 Unauthorized**: Invalid API key
- **403 Forbidden**: Insufficient permissions
- **429 Too Many Requests**: Rate limit exceeded
- **500 Internal Server Error**: Salesrobot server error

### Error Recovery
- Authentication errors: Stop automation
- Rate limit errors: Wait and retry
- Server errors: Retry with backoff
- Network errors: Retry with backoff

## Best Practices

1. **API Key Security**
   - Never commit API keys to version control
   - Use environment variables or secrets management
   - Rotate API keys regularly

2. **Rate Limiting**
   - Implement client-side rate limiting
   - Monitor usage to avoid hitting limits
   - Use batch operations when possible

3. **Error Handling**
   - Implement comprehensive error handling
   - Log all errors for debugging
   - Implement retry logic with backoff

4. **Data Validation**
   - Validate all data before sending to API
   - Handle validation errors gracefully
   - Sanitize user input

## Testing

### Test API Key
Use test API key for development:
```bash
export SALESROBOT_API_KEY="test_api_key"
```

### Mock API
For testing without real API calls, mock the Salesrobot client:
```python
from unittest.mock import Mock
mock_client = Mock()
mock_client.get_leads.return_value = [...]
```

## Monitoring

### Metrics to Track
- API call count
- Success rate
- Error rate
- Response time
- Rate limit hits

### Alerts
- High error rate (> 5%)
- Rate limit exceeded
- Authentication failures
- Slow response times (> 2s)
