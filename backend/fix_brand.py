"""
Fix the brand ID mismatch - create the brand or show existing brands
"""
from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv(Path(__file__).parent / ".env")

from supabase import create_client

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_SERVICE_KEY")
desired_brand_id = os.getenv("DEFAULT_BRAND_ID")

client = create_client(url, key)

print("=" * 60)
print("BRAND ID FIX")
print("=" * 60)

# Check existing brands
brands = client.table("brands").select("*").execute()

print(f"\nCurrent brands in database: {len(brands.data)}")
for brand in brands.data:
    print(f"  - {brand['name']}: {brand['id']}")

print(f"\nDesired brand ID from .env: {desired_brand_id}")

# Check if desired brand exists
brand_exists = any(b['id'] == desired_brand_id for b in brands.data)

if brand_exists:
    print("\n✅ Brand already exists!")
else:
    print("\n⚠️  Brand doesn't exist. Creating it now...")
    try:
        # Create the brand with the specific ID
        result = client.table("brands").insert({
            "id": desired_brand_id,
            "name": "TechHome",
            "api_key": f"test_{desired_brand_id}",
            "settings": {
                "brand_name": "TechHome",
                "default_mode": "PRE_PURCHASE"
            }
        }).execute()
        print(f"✅ Created brand: {result.data[0]['name']} (ID: {result.data[0]['id']})")
    except Exception as e:
        print(f"❌ Error creating brand: {e}")
        print("\nAlternative: Use an existing brand ID in your .env file:")
        if brands.data:
            print(f"  DEFAULT_BRAND_ID={brands.data[0]['id']}")

print("=" * 60)
