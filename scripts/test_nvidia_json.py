"""Test NVIDIA API JSON output format."""

import os
import sys
import json

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from openai import OpenAI

# NVIDIA API Configuration
NVIDIA_API_KEY = os.getenv('NVIDIA_API_KEY', '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')
NVIDIA_BASE_URL = os.getenv('NVIDIA_BASE_URL', 'https://integrate.api.nvidia.com/v1')
NVIDIA_MODEL = os.getenv('NVIDIA_MODEL', 'meta/llama-3.1-70b-instruct')

print("Testing NVIDIA API JSON Output Format")
print("=" * 60)

try:
    # Initialize client
    client = OpenAI(
        base_url=NVIDIA_BASE_URL,
        api_key=NVIDIA_API_KEY
    )
    
    print("Testing JSON output format...")
    
    # Test JSON output
    completion = client.chat.completions.create(
        model=NVIDIA_MODEL,
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant. Always respond with valid JSON only."
            },
            {
                "role": "user",
                "content": "Generate a simple JSON object with the following structure: {\"name\": \"John\", \"title\": \"Engineer\", \"company\": \"Tech Corp\"}. Return only the JSON, no markdown, no code blocks."
            }
        ],
        temperature=0.5,
        max_tokens=200,
        response_format={"type": "json_object"}
    )
    
    response = completion.choices[0].message.content
    print(f"Response: {response}")
    print()
    
    # Try to parse JSON
    try:
        parsed = json.loads(response)
        print("Parsed JSON:")
        print(json.dumps(parsed, indent=2))
        print()
        print("[OK] JSON output format working correctly!")
    except json.JSONDecodeError as e:
        print(f"[ERROR] Failed to parse JSON: {e}")
        sys.exit(1)
    
except Exception as e:
    print(f"[ERROR] NVIDIA API JSON test failed: {e}")
    sys.exit(1)
