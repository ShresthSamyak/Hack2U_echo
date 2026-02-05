"""
Test conversation creation after brand fix
"""
from pathlib import Path
from dotenv import load_dotenv
import os
import uuid

load_dotenv(Path(__file__).parent / ".env")

from database import db

print("=" * 60)
print("TESTING CONVERSATION CREATION")
print("=" * 60)

if not db.enabled:
    print("❌ Database not enabled")
    exit(1)

brand_id = os.getenv("DEFAULT_BRAND_ID")
print(f"\nUsing brand_id: {brand_id}")

# Create a test conversation
session_id = str(uuid.uuid4())
print(f"Creating conversation with session_id: {session_id}")

try:
    success = db.create_conversation(
        session_id=session_id,
        brand_id=brand_id,
        mode="PRE_PURCHASE",
        model_id="AT-WM-9KG-BLACK"
    )
    
    if success:
        print("✅ Conversation created successfully!")
        
        # Try to add a message
        msg_success = db.add_message(session_id, "user", "Hello!")
        if msg_success:
            print("✅ Message added successfully!")
        else:
            print("❌ Failed to add message")
        
        # Retrieve the conversation
        conv = db.get_conversation(session_id)
        if conv:
            print(f"✅ Retrieved conversation with {len(conv.get('messages', []))} messages")
        
        # Clean up
        db.delete_conversation(session_id)
        print("✅ Test conversation deleted")
    else:
        print("❌ Failed to create conversation")
        
except Exception as e:
    print(f"❌ Error: {e}")

print("=" * 60)
