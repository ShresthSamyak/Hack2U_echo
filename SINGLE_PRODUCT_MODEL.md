# Single-Product Agent Model

The system now works as a **single-product AI representative** - like having a dedicated expert for one specific product.

## How It Works

### Identity
The agent represents **exactly ONE product** at a time:
- Product Name: e.g., "AquaTech Pro 9000"
- Brand: e.g., "AquaTech"  
- Model: e.g., "AT-WM-9KG-BLACK"
- Category: e.g., "washing_machine"

### Behavior
The agent acts like:
- **The engineer who designed this product**
- **The official salesperson for this exact model**

### Scope Enforcement
The agent will **reject off-topic questions**:

❌ "Tell me about other washing machines"  
✅ "I'm the AI assistant for AquaTech Pro 9000 only..."

❌ "Compare this to Brand X"  
✅ "I can only help with AquaTech Pro 9000..."

❌ "What's the weather?"  
✅ "I'm the AI assistant for AquaTech Pro 9000 only..."

## Setting the Product

### Option 1: Default Product (Environment Variables)

Set in `.env`:
```bash
DEFAULT_PRODUCT_ID=wm_2026_pro
DEFAULT_MODEL_ID=AT-WM-9KG-BLACK
```

Agent will load this product on startup.

### Option 2: Per-Session (API Call)

Send `model_id` with each chat request:

```http
POST /chat
{
  "message": "How do I clean the filter?",
  "model_id": "AT-WM-9KG-BLACK"
}
```

Agent automatically switches to that product.

### Option 3: Multi-Tenant (Your Implementation)

For production with multiple products:
1. Store user → product mapping in your database
2. Look up user's product
3. Send `model_id` in each request
4. Agent maintains context for that specific product

## Knowledge Priority

The agent uses knowledge in this order:

1. **RAG Documents** (when you add document retrieval)
   - Product manuals
   - Installation guides
   - Troubleshooting docs

2. **Structured Product Data** (from `products.json`)
   - Specs, features, prices
   - Error codes and fixes
   - Warranty info

3. **Conversation Context**
   - What user said before
   - Current problem being solved

## Example: Washing Machine Agent

```
User: "Hi"
Agent: "Hello! I'm the AI expert for the AquaTech Pro 9000 
washing machine. How can I help you today?"

User: "Tell me about refrigerators"
Agent: "I'm the AI assistant for AquaTech Pro 9000 only. 
I can help with questions about this washing machine, its 
usage, setup, issues, warranty, or buying details. What 
would you like to know about the AquaTech Pro 9000?"

User: "What colors does it come in?"
Agent: "The AquaTech Pro 9000 is available in three colors:
- Matte Black (#1a1a1a) - $420
- Pearl White (#f5f5f5) - $420
- Brushed Silver (#c0c0c0) - $450

All models have the same features: inverter motor, steam 
wash, wifi connectivity, and auto detergent dispenser. 
Would you like help choosing a color for your space?"
```

## Benefits

✅ **Focused**: No confusion about which product you're discussing  
✅ **Accurate**: Can't mix up specs from different products  
✅ **Professional**: Feels like talking to a product specialist  
✅ **Scalable**: Easy to deploy many product-specific agents  
✅ **Honest**: Won't recommend products it doesn't represent

## Adding RAG Documents

Future enhancement (not yet implemented):

```python
# Example: Add product manual retrieval
from langchain import FAISS

# Load product manuals
manual_chunks = load_manual("AT-WM-9KG-BLACK")

# Retrieve relevant sections
rag_context = retrieve_relevant(user_query, manual_chunks)

# Pass to agent
response = await agent.generate_response(
    user_query=query,
    rag_context=rag_context  # Priority 1
)
```

## Frontend Integration

Update `App.jsx` to send `model_id`:

```javascript
// Set product when user selects it
const selectedModel = "AT-WM-9KG-BLACK";

// Include in every chat message
const response = await axios.post(`${API_BASE}/chat`, {
  message: userMessage,
  model_id: selectedModel  // <-- Agent loads this product
});
```

## Real-World Example

**Appliance Store Website:**
- User browses to "AquaTech Pro 9000" product page
- Chat widget appears: "Questions about this product?"
- Agent is initialized with that exact model
- All conversations are about ONLY that product
- User can't accidentally get info about wrong product
