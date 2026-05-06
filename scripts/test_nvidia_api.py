"""Test NVIDIA API connection and model availability."""

import os
import sys

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from openai import OpenAI

# NVIDIA API Configuration
NVIDIA_API_KEY = os.getenv('NVIDIA_API_KEY', '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')
NVIDIA_BASE_URL = os.getenv('NVIDIA_BASE_URL', 'https://integrate.api.nvidia.com/v1')
NVIDIA_MODEL = os.getenv('NVIDIA_MODEL', 'meta/llama-3.1-70b-instruct')

print("Testing NVIDIA API Connection")
print("=" * 60)
print(f"Base URL: {NVIDIA_BASE_URL}")
print(f"Model: {NVIDIA_MODEL}")
print(f"API Key: {NVIDIA_API_KEY[:20]}...{NVIDIA_API_KEY[-4:]}")
print()

try:
    # Initialize client
    client = OpenAI(
        base_url=NVIDIA_BASE_URL,
        api_key=NVIDIA_API_KEY
    )
    
    print("Testing simple completion...")
    
    # Test simple completion
    completion = client.chat.completions.create(
        model=NVIDIA_MODEL,
        messages=[
            {"role": "user", "content": "Say 'Hello from NVIDIA!' in exactly those words."}
        ],
        temperature=0.5,
        max_tokens=50
    )
    
    response = completion.choices[0].message.content
    print(f"Response: {response}")
    print()
    print("[OK] NVIDIA API connection successful!")
    
except Exception as e:
    print(f"[ERROR] NVIDIA API connection failed: {e}")
    sys.exit(1)
