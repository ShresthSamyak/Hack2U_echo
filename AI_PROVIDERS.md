# AI Provider Comparison

The system supports both **OpenRouter** (free) and **Google Gemini**.

## OpenRouter (Recommended - FREE!)

### ✅ Advantages
- **Completely free** - no API key needed
- **Multiple specialized models**:
  - Text: `mistralai/mistral-7b-instruct`
  - Vision: `qwen/qwen2-vl-7b-instruct`
  - Reasoning: `meta-llama/llama-3.1-8b-instruct`
- **Dynamic routing** - best model for each task
- **No vendor lock-in**
- **Good performance**

### ❌ Considerations
- Slightly slower than paid tiers
- Rate limits on free tier (generous)
- May have occasional capacity issues

### Setup
```bash
echo AI_PROVIDER=openrouter > backend/.env
```

That's it! No API key needed.

---

## Google Gemini (Alternative)

### ✅ Advantages
- **Single unified model** (Gemini Pro + Vision)
- **Fast responses**
- **Generous free tier**
- **High quality**
- **Good rate limits**

### ❌ Considerations
- **Requires API key** (free from Google)
- Vendor lock-in to Google

### Setup
```bash
# Get API key: https://makersuite.google.com/app/apikey
echo AI_PROVIDER=gemini > backend/.env
echo GOOGLE_API_KEY=your_key_here >> backend/.env
```

---

## Which Should You Use?

**Use OpenRouter if:**
- ✅ You want to start immediately (no signup)
- ✅ You want completely free operation
- ✅ You prefer model flexibility
- ✅ You're building an MVP

**Use Gemini if:**
- ✅ You already have a Google account
- ✅ You want fastest response times
- ✅ You prefer unified AI experience
- ✅ You're okay with getting an API key

---

## Switching Between Providers

Simply change `AI_PROVIDER` in `.env`:

```bash
# Use OpenRouter (free)
AI_PROVIDER=openrouter

# Use Gemini
AI_PROVIDER=gemini
GOOGLE_API_KEY=your_key_here
```

Restart backend - that's it!

---

## Performance Comparison

| Feature | OpenRouter | Gemini |
|---------|-----------|--------|
| Cost | Free | Free |
| API Key Required | No | Yes |
| Text Quality | Excellent | Excellent |
| Vision Quality | Very Good | Excellent |
| Response Speed | Good | Very Fast |
| Rate Limits | Generous | Generous |
| Context Memory | ✅ | ✅ |
| Safety Detection | ✅ | ✅ |

Both work great! **OpenRouter is recommended** for immediate, no-setup use.
