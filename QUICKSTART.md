# OpenRouter Setup (FREE - No API Key Required!)

The system now uses **OpenRouter's free models** by default. You don't need any API key to get started!

## Free Models Used

- **Text conversations**: `mistralai/mistral-7b-instruct` (fast, reliable)
- **Image analysis**: `qwen/qwen2-vl-7b-instruct` (vision model)
- **Complex reasoning**: `meta-llama/llama-3.1-8b-instruct` (better reasoning)

## Quick Start (No API Key Needed!)

### 1. Backend Setup

```bash
cd backend

# Create .env file (minimal config)
echo AI_PROVIDER=openrouter > .env
echo MODE=PRE_PURCHASE >> .env
echo BRAND_NAME=TechHome >> .env

# Install dependencies
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# Run backend
python main.py
```

### 2. Frontend Setup

```bash
cd frontend
npm run dev
```

### 3. Access Application

Open browser: `http://localhost:5173`

That's it! The system works **completely free** without any API keys.

## Optional: Get Better Performance with API Key

OpenRouter has a free tier, but you can optionally add an API key for:
- Higher rate limits
- Priority access
- Better performance

Get free API key: https://openrouter.ai/keys

Then add to `.env`:
```
OPENROUTER_API_KEY=your_key_here
```

## Alternative: Use Google Gemini

If you prefer Google Gemini instead:

1. Get API key: https://makersuite.google.com/app/apikey

2. Update `.env`:
```
AI_PROVIDER=gemini
GOOGLE_API_KEY=your_gemini_key
```

## How It Works

The system automatically:
- Routes text queries → Mistral 7B
- Routes image analysis → Qwen2 VL 7B
- Routes complex reasoning → Llama 3.1 8B

All **completely free** through OpenRouter!

## Testing

Same testing flow as before:

**Pre-Purchase:**
- "I need a washing machine"
- Upload room image
- "What color matches my room?"

**Post-Purchase:**
- Switch to POST_PURCHASE mode
- "My washing machine shows error E01"
- "How do I clean the filter?"

## Benefits of OpenRouter

✅ **Free**: No costs, no credit card
✅ **No API Key**: Works out of the box
✅ **Multiple Models**: Best model for each task
✅ **Good Performance**: Fast and reliable
✅ **Privacy**: No vendor lock-in
