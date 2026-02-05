"""
Quick test to verify Supabase connection
"""
from pathlib import Path
from dotenv import load_dotenv
import os

# Load .env
load_dotenv(Path(__file__).parent / ".env")

print("=" * 50)
print("SUPABASE CONNECTION TEST")
print("=" * 50)

# Check env vars
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_SERVICE_KEY")

print(f"\n✓ SUPABASE_URL: {url[:30]}..." if url else "✗ SUPABASE_URL: NOT FOUND")
print(f"✓ SUPABASE_SERVICE_KEY: {key[:30]}..." if key else "✗ SUPABASE_SERVICE_KEY: NOT FOUND")

# Try to connect
if url and key:
    print("\n📡 Attempting connection...")
    try:
        from supabase import create_client
        client = create_client(url, key)
        print("✅ Supabase client created successfully!")
        
        # Try a simple query
        print("\n🔍 Testing database query...")
        result = client.table("conversations").select("*").limit(1).execute()
        print(f"✅ Database query successful! Found {len(result.data)} conversations")
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
else:
    print("\n❌ Missing credentials - cannot connect")

print("\n" + "=" * 50)
