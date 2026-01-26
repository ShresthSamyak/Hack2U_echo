"""
Check if conversations are being stored in Supabase
"""
from pathlib import Path
from dotenv import load_dotenv
import os

# Load .env
load_dotenv(Path(__file__).parent / ".env")

from supabase import create_client

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_SERVICE_KEY")

client = create_client(url, key)

print("=" * 60)
print("CHECKING STORED CONVERSATIONS")
print("=" * 60)

# Get all conversations
conversations = client.table("conversations").select("*").execute()

print(f"\n✅ Found {len(conversations.data)} conversations in database\n")

for conv in conversations.data[:5]:  # Show first 5
    msg_count = len(conv.get('messages', []))
    print(f"Session: {conv['session_id'][:20]}...")
    print(f"  Mode: {conv['mode']}")
    print(f"  Messages: {msg_count}")
    print(f"  Product: {conv.get('model_id', 'None')}")
    print(f"  Created: {conv['created_at'][:19]}")
    if msg_count > 0:
        print(f"  Last message: {conv['messages'][-1]['content'][:50]}...")
    print()

print("=" * 60)
