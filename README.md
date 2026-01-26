# Product Intelligence Agent

A dual-mode AI assistant powered by **OpenRouter's free models** (no API key needed!) that acts as:
- **Pre-Purchase**: Consultative salesperson helping customers find the right product
- **Post-Purchase**: Technical support engineer for troubleshooting and guidance

## 🚀 Quick Start (FREE - No API Key Required!)

```bash
# Backend
cd backend
echo AI_PROVIDER=openrouter > .env
pip install -r requirements.txt
python main.py

# Frontend
cd frontend  
npm run dev
```

Open `http://localhost:5173` - **That's it!** Works completely free without any API keys.

## Features

✨ **Dual Mode Operation**
- PRE_PURCHASE: Product recommendations, room analysis, color matching
- POST_PURCHASE: Troubleshooting, error codes, installation help, maintenance tips

🎨 **Room Image Analysis**
- Upload room photos for placement recommendations
- Color matching with available product variants
- Space assessment and fit validation
- Safety and ventilation considerations

🤖 **Intelligent Agent**
- Powered by OpenRouter free models (Mistral 7B + Qwen2 VL + Llama 3.1)
- Alternative: Google Gemini support included
- Honest product recommendations (never hallucinates specs)
- Safety-first approach (warns when professional help needed)
- Conversation memory for context-aware responses

📦 **Product Catalog**
- Washing Machines
- Refrigerators
- Headphones
- EV Batteries
- (Easily extensible)

## Tech Stack

**Backend:**
- FastAPI (Python)
- OpenRouter API (free tier - Mistral, Qwen, Llama models)
- Alternative: Google Generative AI (Gemini)
- httpx (HTTP client)
- Pillow (image processing)
- Pydantic (data validation)

**Frontend:**
- React + Vite
- Axios (API calls)
- Lucide React (icons)
- Premium glassmorphism design

## Setup Instructions

### Prerequisites
- Python 3.9+
- Node.js 18+
- **No API key required!** (OpenRouter free tier)
- Optional: Google API Key for Gemini ([Get it here](https://makersuite.google.com/app/apikey))

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create virtual environment:
```bash
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file:
```bash
cp .env.example .env
```

5. Edit `.env` - **No API key needed for OpenRouter!**
```
AI_PROVIDER=openrouter
MODE=PRE_PURCHASE
BRAND_NAME=TechHome
```

**Optional**: For Gemini instead:
```
AI_PROVIDER=gemini
GOOGLE_API_KEY=your_actual_api_key_here
```

6. Run the backend:
```bash
python main.py
```

Backend will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Run the development server:
```bash
npm run dev
```

Frontend will be available at `http://localhost:5173`

## API Endpoints

### Chat
```http
POST /chat
{
  "message": "I need a washing machine for a family of 4",
  "category": "washing_machines"
}
```

### Room Analysis
```http
POST /analyze-room
Content-Type: multipart/form-data

file: <image>
```

### Error Code Lookup
```http
POST /error-code
{
  "model_id": "AT-WM-9KG-BLACK",
  "error_code": "E01"
}
```

### Mode Switch
```http
POST /mode
{
  "mode": "POST_PURCHASE"
}
```

## Adding Your Product Data

Replace `backend/data/products.json` with your actual product catalog. Format:

```json
{
  "category_name": [
    {
      "product_id": "unique_id",
      "category": "category_name",
      "brand": "Brand Name",
      "models": [
        {
          "model_id": "MODEL-ID",
          "color": "Color Name",
          "hex_color": "#hexcode",
          "dimensions_cm": [height, width, depth],
          "price": 999,
          "warranty_years": 2,
          "features": ["feature1", "feature2"],
          "installation": "Installation instructions",
          "common_issues": [
            {
              "error": "E01",
              "meaning": "Error meaning",
              "fix": "How to fix"
            }
          ]
        }
      ]
    }
  ]
}
```

## Deployment

### Backend (Google Cloud Run)

1. Create `Dockerfile` in backend directory
2. Build and deploy:
```bash
gcloud run deploy product-agent-api \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### Frontend (Vercel)

1. Update `frontend/src/App.jsx` with your API URL
2. Deploy:
```bash
cd frontend
vercel
```

## Usage Examples

### Pre-Purchase Mode

**User:** "I need a washing machine for my laundry room"

**Agent:** *Asks clarifying questions about space, family size, budget*

**User:** *Uploads room image*

**Agent:** *Analyzes room, recommends best size and color variant*

### Post-Purchase Mode

**User:** "My fridge is showing error E01"

**Agent:** *Looks up error code, provides step-by-step fix*

**User:** "How do I clean the filter?"

**Agent:** *Provides maintenance instructions*

## Safety Features

The agent automatically identifies dangerous operations and warns users:
- High voltage work → "This requires a certified technician"
- Gas connections → Refuses to provide guidance
- Internal electronics → Recommends professional service

## License

MIT License - feel free to use for your products!

## Support

For issues or questions, please open a GitHub issue or contact support.
