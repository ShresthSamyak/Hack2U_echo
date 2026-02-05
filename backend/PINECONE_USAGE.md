# Pinecone Vector Database Integration

## Quick Start Guide

### 1. Setup

**Install dependencies:**
```bash
pip install -r requirements.txt
```

**Set environment variables** in `.env`:
```bash
# Required for RAG retrieval
PINECONE_API_KEY=your_pinecone_api_key
OPENAI_EMBEDDING_KEY=your_openai_api_key

# Optional - keep your existing settings
AI_PROVIDER=openrouter
BRAND_NAME=TechHome
```

**Get API Keys:**
- Pinecone: https://app.pinecone.io (Free tier available)
- OpenAI: https://platform.openai.com/api-keys (Pay-as-you-go for embeddings ~$0.0001 per 1K tokens)

---

### 2. Index Product Manuals

**Option A: Index all products from `products.json`**

```bash
python indexing.py
```

This will:
- Read all products from `data/products.json`
- Chunk manual data, warranty, troubleshooting, etc.
- Generate embeddings using OpenAI
- Upload to Pinecone with product-specific namespaces

**Option B: Index single product manually**

```python
from indexing import initialize_pinecone, index_product_manual
import json

# Initialize
initialize_pinecone("your_pinecone_api_key")

# Load product data
with open("data/sample_battery_manual.json") as f:
    battery_data = json.load(f)

# Index it
await index_product_manual("VM-LI-48V-100AH", battery_data)
```

---

### 3. Use RAG in Your API

**Update `main.py` to use retrieval:**

```python
from retrieval import initialize_pinecone, retrieve_documents
from config import settings

# Initialize on startup
@app.on_event("startup")
async def startup_event():
    if settings.pinecone_api_key:
        initialize_pinecone(
            settings.pinecone_api_key,
            settings.pinecone_index_name
        )

# Use in chat endpoint
@app.post("/chat")
async def chat(request: ChatRequest):
    product_context = None
    rag_context = None
    
    if request.model_id:
        # Get product data
        result = product_db.get_model_by_id(request.model_id)
        if result:
            product_context = {"product": result[0], "model": result[1]}
            
            # Retrieve relevant documents from vector DB
            rag_context = await retrieve_documents(
                product_id=request.model_id,
                query=request.message,
                top_k=3
            )
    
    # Generate response with RAG context
    response = await agent.generate_response(
        user_query=request.message,
        product_context=product_context,
        rag_context=rag_context  # Agent prioritizes this!
    )
    
    return ChatResponse(response=response, mode=agent.mode)
```

---

### 4. Testing

**Test retrieval:**

```python
from retrieval import initialize_pinecone, retrieve_documents

initialize_pinecone("your_api_key")

# Query for battery
docs = await retrieve_documents(
    product_id="VM-LI-48V-100AH",
    query="How do I install this battery?",
    top_k=3
)

print(docs)
```

Expected output:
```
[installation] Installation steps:
1. Turn off vehicle main power
2. Disconnect existing battery safely
...
(relevance: 0.89)
```

---

## Data Format

Your `products.json` should include `manual`, `repair_policy`, `warranty_details`, etc.:

```json
{
  "ev_batteries": [
    {
      "product_id": "battery_2026_pro",
      "name": "VoltMax Lithium Battery",
      "models": [
        {
          "model_id": "VM-LI-48V-100AH",
          "manual": {
            "overview": "...",
            "installation_steps": [...],
            "safety_guidelines": [...]
          },
          "battery_health": {...},
          "repair_policy": {...},
          "warranty_details": {...}
        }
      ]
    }
  ]
}
```

See `data/sample_battery_manual.json` for complete example.

---

## How It Works

1. **Indexing** (`indexing.py`):
   - Reads product data from JSON
   - Chunks manual sections into searchable pieces
   - Generates embeddings (1536-dim vectors)
   - Uploads to Pinecone namespace `product_{model_id}`

2. **Retrieval** (`retrieval.py`):
   - Takes user query
   - Generates query embedding
   - Searches Pinecone namespace for that specific product
   - Returns top-k most relevant chunks

3. **Agent** uses retrieved documents as **highest priority** knowledge source

---

## Cost Estimation

**OpenAI Embeddings** (text-embedding-ada-002):
- Cost: $0.0001 per 1K tokens
- Example: 10 products × 20 chunks × 200 tokens = 40K tokens = **$0.004**
- Queries: ~100 tokens each = $0.00001 per query

**Pinecone**:
- Free tier: 1 index, 100K vectors
- Should cover 100-500 products easily

Total cost for small catalogs: **~$1-2/month**

---

## Troubleshooting

**"No documents found"**
- Check namespace exists: `index.describe_index_stats()`
- Verify product_id matches exactly

**"Embedding API error"**
- Check OPENAI_EMBEDDING_KEY is set
- Verify API key has credits

**"Pinecone connection failed"**
- Check PINECONE_API_KEY is valid
- Ensure index name matches config
