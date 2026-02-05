# Echo - Product Intelligence Agent

A dual-mode AI assistant that provides intelligent product assistance powered by free AI models. Acts as both a consultative sales agent and technical support engineer.

## Overview

Echo is an AI-powered product intelligence system that operates in two modes:
- **PRE_PURCHASE Mode**: Helps customers find the right product by understanding their needs, analyzing room spaces, and recommending suitable variants
- **POST_PURCHASE Mode**: Provides technical support, troubleshooting guidance, error code explanations, and maintenance instructions

## Quick Start

### Backend Setup

```bash
cd backend
pip install -r requirements.txt
python main.py
```

API will be available at `http://localhost:8000`

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Application will be available at `http://localhost:3000`

## Features

### Dual Mode Operation
- PRE_PURCHASE: Product recommendations, room analysis, color matching
- POST_PURCHASE: Troubleshooting, error codes, installation help, maintenance guidance

### Room Image Analysis
- Upload room photos for placement recommendations
- Color matching with available product variants
- Space assessment and fit validation
- Safety and ventilation considerations

### Intelligent AI Agent
- Powered by Groq (llama-3.3-70b-versatile)
- Alternative providers: Google Gemini, OpenRouter
- Honest product recommendations
- Safety-first approach with professional service warnings
- RAG-powered responses using Pinecone vector database
- Free local embeddings using sentence-transformers

### Product Catalog
Currently supports:
- Washing Machines
- Refrigerators
- Headphones
- EV Batteries
- Easily extensible to any product category

## Tech Stack

### Backend
- FastAPI (Python web framework)
- Groq API (primary AI provider)
- Pinecone (vector database for RAG)
- sentence-transformers (local embeddings)
- Pillow (image processing)
- Pydantic (data validation)
- Supabase (PostgreSQL database for conversations)

### Frontend
- Next.js 15 (React framework)
- Redux Toolkit (state management)
- TailwindCSS (styling)
- Lucide React (icons)

## Prerequisites

- Python 3.9+
- Node.js 18+
- Groq API Key (free at https://console.groq.com)
- Pinecone API Key (free tier available)
- Optional: Supabase account for conversation history

## Environment Configuration

### Backend (.env)

```env
# AI Provider
AI_PROVIDER=groq
GROQ_API_KEY=your_groq_key_here

# Vector Database
PINECONE_API_KEY=your_pinecone_key_here
PINECONE_INDEX_NAME=product-manuals

# Operation Mode
MODE=PRE_PURCHASE

# Brand Configuration
BRAND_NAME=echo
PRODUCT_CATEGORY=home_appliances

# Optional: Conversation History
SUPABASE_URL=your_supabase_project_url
SUPABASE_SERVICE_KEY=your_supabase_service_key
```

## API Endpoints

### Chat
```http
POST /chat
Content-Type: application/json

{
  "message": "How do I install the washing machine?",
  "model_id": "AT-WM-9KG-BLACK"
}
```

### Health Check
```http
GET /
```

## Adding Product Data

### 1. Update Product Catalog

Edit `backend/data/products.json`:

```json
{
  "category_name": [
    {
      "product_id": "unique_id",
      "name": "Product Name",
      "category": "category_name",
      "brand": "Brand Name",
      "models": [
        {
          "model_id": "MODEL-ID",
          "name": "Model Name",
          "color": "Color",
          "price": 999,
          "features": ["feature1", "feature2"]
        }
      ]
    }
  ]
}
```

### 2. Add Product Manual

Create `backend/data/sample_[category]_manual.json`:

```json
{
  "model_id": "MODEL-ID",
  "sections": {
    "installation": "Installation instructions...",
    "troubleshooting": "Common issues and fixes...",
    "maintenance": "Maintenance guide..."
  }
}
```

### 3. Index in Vector Database

```bash
cd backend
python indexing.py
```

## Project Structure

```
echo/
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── agent_groq.py          # Groq AI agent
│   ├── retrieval.py           # RAG retrieval logic
│   ├── indexing.py            # Vector DB indexing
│   ├── config.py              # Configuration
│   └── data/
│       ├── products.json      # Product catalog
│       └── sample_*.json      # Product manuals
├── frontend/
│   ├── app/                   # Next.js pages
│   ├── components/            # React components
│   └── lib/                   # Utilities
└── README.md
```

## Usage Examples

### PRE_PURCHASE Mode

User: "I need a washing machine for my family"

Agent: Asks clarifying questions about:
- Family size
- Laundry frequency
- Available space
- Budget
- Color preferences

Then recommends the best matching product variant.

### POST_PURCHASE Mode

User: "My washing machine shows error E03"

Agent: 
- Looks up error code in product manual
- Explains what the error means
- Provides step-by-step troubleshooting
- Issues safety warnings if needed

## Safety Features

The agent automatically identifies dangerous operations:
- High voltage work: Recommends certified technician
- Gas connections: Refuses to provide guidance
- Internal electronics: Suggests professional service

## Deployment

### Backend (Cloud Run, Railway, Render)

```bash
# Using Docker
docker build -t echo-backend backend/
docker run -p 8000:8000 echo-backend
```

### Frontend (Vercel, Netlify)

```bash
cd frontend
vercel deploy
```

## Development

### Running Tests

```bash
# Backend
cd backend
python test_conversation.py

# Frontend
cd frontend
npm test
```

### Adding New AI Providers

Create a new agent file like `agent_[provider].py` and update `config.py`.

## Cost Breakdown

- Groq API: Free tier (30 requests/minute)
- Pinecone: Free tier (1 index, 100K vectors)
- Embeddings: Free (local sentence-transformers)
- Supabase: Free tier (500MB database)

Total development cost: $0/month

## License

MIT License

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## Support

For issues or questions, please open a GitHub issue.