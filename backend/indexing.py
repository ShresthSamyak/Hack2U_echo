"""
Product Manual Indexing for Pinecone Vector Database
Chunks and indexes product manuals into product-specific namespaces
Uses FREE local embeddings (no API costs!)
"""

import json
import asyncio
from typing import Dict, List
import retrieval  # Import module instead of individual items
from uuid import uuid4


def chunk_manual_data(model_id: str, manual_data: Dict) -> List[Dict]:
    """
    Convert manual JSON structure into indexable chunks
    
    Args:
        model_id: Product model ID
        manual_data: Manual dictionary from products.json
    
    Returns:
        List of chunks with metadata
    """
    chunks = []
    
    # 1. Overview
    if "overview" in manual_data:
        chunks.append({
            "text": manual_data["overview"],
            "section": "overview",
            "model_id": model_id
        })
    
    # 2. Installation Steps
    if "installation_steps" in manual_data:
        installation_text = "Installation steps:\n" + "\n".join(
            f"{i+1}. {step}" for i, step in enumerate(manual_data["installation_steps"])
        )
        chunks.append({
            "text": installation_text,
            "section": "installation",
            "model_id": model_id
        })
    
    # 3. First Time Use
    if "first_time_use" in manual_data:
        first_use_text = "First time use instructions:\n" + "\n".join(
            f"- {item}" for item in manual_data["first_time_use"]
        )
        chunks.append({
            "text": first_use_text,
            "section": "first_time_use",
            "model_id": model_id
        })
    
    # 4. Daily Usage
    if "daily_usage" in manual_data:
        usage_text = "Daily usage guidelines:\n" + "\n".join(
            f"- {item}" for item in manual_data["daily_usage"]
        )
        chunks.append({
            "text": usage_text,
            "section": "daily_usage",
            "model_id": model_id
        })
    
    # 5. Safety Guidelines
    if "safety_guidelines" in manual_data:
        safety_text = "SAFETY GUIDELINES:\n" + "\n".join(
            f"⚠️ {item}" for item in manual_data["safety_guidelines"]
        )
        chunks.append({
            "text": safety_text,
            "section": "safety",
            "model_id": model_id
        })
    
    # 6. Do Not
    if "do_not" in manual_data:
        donot_text = "DO NOT:\n" + "\n".join(
            f"❌ {item}" for item in manual_data["do_not"]
        )
        chunks.append({
            "text": donot_text,
            "section": "warnings",
            "model_id": model_id
        })
    
    # 7. Environmental Conditions
    if "environmental_conditions" in manual_data:
        chunks.append({
            "text": f"Environmental conditions: {manual_data['environmental_conditions']}",
            "section": "specifications",
            "model_id": model_id
        })
    
    # 8. Storage
    if "storage" in manual_data:
        chunks.append({
            "text": f"Storage instructions: {manual_data['storage']}",
            "section": "storage",
            "model_id": model_id
        })
    
    return chunks


def chunk_additional_data(model_id: str, data: Dict, data_type: str) -> List[Dict]:
    """
    Chunk additional structured data (battery_health, repair_policy, warranty, etc.)
    
    Args:
        model_id: Product model ID
        data: Dictionary to chunk
        data_type: Type of data (e.g., "battery_health", "repair_policy")
    
    Returns:
        List of chunks
    """
    chunks = []
    
    # Convert nested dict to readable text
    text = f"{data_type.replace('_', ' ').title()}:\n"
    text += json.dumps(data, indent=2)
    
    chunks.append({
        "text": text,
        "section": data_type,
        "model_id": model_id
    })
    
    return chunks


def index_product_manual(model_id: str, product_data: Dict):
    """
    Index a single product's manual into Pinecone
    Uses FREE local embeddings (no API costs!)
    
    Args:
        model_id: Product model ID
        product_data: Full product data including manual, battery_health, repair_policy, etc.
    """
    if retrieval.index is None:
        print("Error: Pinecone index not initialized. Call initialize_pinecone() first.")
        return
    
    namespace = f"product_{model_id}"
    all_chunks = []
    
    # 1. Chunk manual data
    if "manual" in product_data:
        manual_chunks = chunk_manual_data(model_id, product_data["manual"])
        all_chunks.extend(manual_chunks)
    
    # 2. Chunk battery health data (if exists)
    if "battery_health" in product_data:
        health_chunks = chunk_additional_data(model_id, product_data["battery_health"], "battery_health")
        all_chunks.extend(health_chunks)
    
    # 3. Chunk repair policy
    if "repair_policy" in product_data:
        repair_chunks = chunk_additional_data(model_id, product_data["repair_policy"], "repair_policy")
        all_chunks.extend(repair_chunks)
    
    # 4. Chunk warranty details
    if "warranty_details" in product_data:
        warranty_chunks = chunk_additional_data(model_id, product_data["warranty_details"], "warranty_details")
        all_chunks.extend(warranty_chunks)
    
    # 5. Chunk troubleshooting flow
    if "troubleshooting_flow" in product_data:
        troubleshooting_chunks = chunk_additional_data(model_id, product_data["troubleshooting_flow"], "troubleshooting")
        all_chunks.extend(troubleshooting_chunks)
    
    # 6. Chunk lifecycle info
    if "lifecycle" in product_data:
        lifecycle_chunks = chunk_additional_data(model_id, product_data["lifecycle"], "lifecycle")
        all_chunks.extend(lifecycle_chunks)
    
    print(f"Indexing {len(all_chunks)} chunks for {model_id}...")
    
    # Generate embeddings using FREE local model and upsert to Pinecone
    vectors = []
    for chunk in all_chunks:
        # Get embedding using FREE local model
        embedding = retrieval.get_embedding(chunk["text"])
        
        # Create vector
        vector_id = str(uuid4())
        vectors.append({
            "id": vector_id,
            "values": embedding,
            "metadata": {
                "text": chunk["text"],
                "section": chunk["section"],
                "model_id": chunk["model_id"]
            }
        })
    
    # Upsert in batches of 100
    batch_size = 100
    for i in range(0, len(vectors), batch_size):
        batch = vectors[i:i + batch_size]
        retrieval.index.upsert(vectors=batch, namespace=namespace)
        print(f"  Uploaded batch {i//batch_size + 1}/{(len(vectors)-1)//batch_size + 1}")
    
    print(f"✅ Successfully indexed {model_id} into namespace '{namespace}'")


def index_all_products(products_file: str = "data/products.json"):
    """
    Index all products from products.json file
    
    Args:
        products_file: Path to products.json
    """
    with open(products_file, 'r', encoding='utf-8') as f:
        products = json.load(f)
    
    # Flatten product structure
    all_products = []
    for category, product_list in products.items():
        for product in product_list:
            for model in product.get("models", []):
                # Combine product and model data
                combined_data = {
                    **model,
                    "product_name": product.get("name", ""),
                    "brand": product.get("brand", ""),
                    "category": category
                }
                all_products.append(combined_data)
    
    print(f"Found {len(all_products)} products to index\n")
    
    for product in all_products:
        model_id = product.get("model_id")
        if model_id:
            index_product_manual(model_id, product)
            print()  # Blank line between products
        else:
            print(f"⚠️ Skipping product without model_id")
    
    print("🎉 All products indexed successfully!")


# CLI for manual indexing
if __name__ == "__main__":
    import sys
    import os
    from dotenv import load_dotenv
    
    # Load environment variables from .env file
    load_dotenv()
    
    # Get Pinecone API key from environment
    pinecone_api_key = os.getenv("PINECONE_API_KEY")
    
    if not pinecone_api_key:
        print("❌ Error: PINECONE_API_KEY not found in .env file")
        print("\n📝 Please add your Pinecone API key to .env:")
        print("   PINECONE_API_KEY=your_key_here")
        print("\n   Get your key from: https://app.pinecone.io")
        sys.exit(1)
    
    # Initialize Pinecone (will also load FREE local embedding model)
    print("Initializing Pinecone and loading embedding model...")
    retrieval.initialize_pinecone(pinecone_api_key)
    
    # Index all products
    index_all_products()

