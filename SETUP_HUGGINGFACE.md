# 🚀 Quick Setup with HuggingFace (100% FREE!)

No OpenAI API key needed! Use HuggingFace's free Inference API instead.

## Step 1: Get HuggingFace Token (FREE)

1. Go to https://huggingface.co/settings/tokens
2. Create a new token (Read access is enough)
3. Copy your token (starts with `hf_...`)

## Step 2: Create .env File

Create `backend/.env`:

```env
# Your HuggingFace token
HUGGINGFACE_API_KEY=hf_your_actual_token_here

# Use HuggingFace for LLM
LLM_PROVIDER=huggingface
LLM_MODEL=mistralai/Mistral-7B-Instruct-v0.2

# Embedding model (local, no API needed)
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

## Step 3: Install Dependencies

```powershell
cd backend
pip install fastapi uvicorn httpx tiktoken sse-starlette sentence-transformers
```

## Step 4: Run the Backend

```powershell
python main.py
```

Visit: http://localhost:8000/docs

## Available FREE Models

In your `.env`, you can use any of these models:

### Recommended (Best Performance):
```env
LLM_MODEL=mistralai/Mistral-7B-Instruct-v0.2
```

### Alternatives:
```env
# Meta's Llama 2
LLM_MODEL=meta-llama/Llama-2-7b-chat-hf

# Google's FLAN-T5 (Fast)
LLM_MODEL=google/flan-t5-xxl

# Falcon
LLM_MODEL=tiiuae/falcon-7b-instruct

# Zephyr (Smaller, faster)
LLM_MODEL=HuggingFaceH4/zephyr-7b-beta
```

## Features Still Work!

✅ All 4 retrieval strategies (semantic, BM25, hybrid, HyDE)
✅ Evaluation metrics
✅ A/B testing
✅ Streaming responses
✅ Cost tracking (shows $0.00 - it's FREE!)
✅ All endpoints

## Test It

```bash
# Health check
curl http://localhost:8000/health

# Test query
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"What is RAG?\", \"strategy\": \"hybrid\"}"
```

## Notes

- **HuggingFace Inference API is FREE** for most models
- First request might be slow (cold start)
- Rate limits: ~1000 requests/hour (plenty for development)
- No credit card needed!

## If You Get Rate Limited

Option 1: Wait a few minutes
Option 2: Use a different model
Option 3: Create another HuggingFace account (free)

---

**Now you have a production-ready RAG system with $0 API costs!** 🎉
