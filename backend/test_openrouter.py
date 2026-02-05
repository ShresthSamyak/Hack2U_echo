"""
Quick test to verify OpenRouter API key works
"""
import os
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")

print(f"🔑 Testing API Key: {api_key[:15]}... (Length: {len(api_key) if api_key else 0})")

if not api_key:
    print("❌ ERROR: OPENROUTER_API_KEY not found in .env file!")
    exit(1)

# Test with a simple text request (not vision, to isolate the issue)
response = requests.post(
    url="https://openrouter.ai/api/v1/chat/completions",
    headers={
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "http://localhost:8000",
        "X-Title": "HackUtoo Product AI Test",
        "Content-Type": "application/json"
    },
    json={
        "model": "meta-llama/llama-3.2-3b-instruct:free",  # Free model for testing
        "messages": [
            {"role": "user", "content": "Say hello"}
        ]
    },
    timeout=30
)

print(f"\n📊 Response Status: {response.status_code}")

if response.status_code == 200:
    print("✅ SUCCESS! API key is valid and working!")
    result = response.json()
    print(f"🤖 Response: {result['choices'][0]['message']['content']}")
elif response.status_code == 401:
    print("❌ 401 ERROR - Possible causes:")
    print("   1. API key is invalid/revoked")
    print("   2. Account has no credits")
    print("   3. Account is suspended")
    print(f"\n📄 Response: {response.text}")
elif response.status_code == 402:
    print("❌ 402 ERROR - Out of credits!")
    print("   Add credits at: https://openrouter.ai/credits")
else:
    print(f"❌ ERROR: {response.status_code}")
    print(f"📄 Response: {response.text}")
