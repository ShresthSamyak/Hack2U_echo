"""
Check if Supabase database schema is set up correctly
"""
from pathlib import Path
from dotenv import load_dotenv
import os

# Load .env
load_dotenv(Path(__file__).parent / ".env")

from supabase import create_client

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_SERVICE_KEY")
default_brand_id = os.getenv("DEFAULT_BRAND_ID")

if not url or not key:
    print("❌ Missing Supabase credentials")
    exit(1)

client = create_client(url, key)

print("=" * 60)
print("SUPABASE SCHEMA VERIFICATION")
print("=" * 60)

# Check each table
tables = ["brands", "products", "conversations", "analytics"]
schema_ok = True

for table in tables:
    try:
        result = client.table(table).select("*").limit(1).execute()
        print(f"✅ Table '{table}' exists (found {len(result.data)} rows)")
    except Exception as e:
        print(f"❌ Table '{table}' missing or error: {e}")
        schema_ok = False

print()

# Check if default brand exists
if schema_ok:
    print("Checking for default brand...")
    try:
        if default_brand_id:
            brand = client.table("brands").select("*").eq("id", default_brand_id).execute()
            if brand.data:
                print(f"✅ Default brand found: {brand.data[0]['name']} (ID: {default_brand_id})")
            else:
                print(f"⚠️  Default brand ID '{default_brand_id}' not found in database!")
                print("   You may need to run the schema.sql or update DEFAULT_BRAND_ID in .env")
        else:
            # Try to find any brand
            brands = client.table("brands").select("*").limit(1).execute()
            if brands.data:
                print(f"✅ Found brand: {brands.data[0]['name']} (ID: {brands.data[0]['id']})")
                print(f"   💡 Set DEFAULT_BRAND_ID={brands.data[0]['id']} in .env")
            else:
                print("⚠️  No brands found! Run the schema.sql to create the test brand.")
    except Exception as e:
        print(f"❌ Error checking brands: {e}")
        schema_ok = False

print()
print("=" * 60)
if schema_ok:
    print("✅ DATABASE SCHEMA IS READY!")
else:
    print("❌ SCHEMA SETUP NEEDED")
    print("\nNext steps:")
    print("1. Go to https://supabase.com/dashboard")
    print("2. Select your project")
    print("3. Go to 'SQL Editor'")
    print("4. Copy and paste the contents of 'schema.sql'")
    print("5. Run the query")
print("=" * 60)
