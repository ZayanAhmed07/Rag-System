# Quick Start Guide - RAG System

## Installation

### 1. Install Python Dependencies

```powershell
cd backend
pip install -r requirements.txt
```

This installs:
- FastAPI & Uvicorn (API server)
- LangChain & Transformers (LLM & embeddings)
- Qdrant Client (vector database)
- RAGAS (evaluation)
- Rank-BM25 (keyword search)
- OpenAI & Anthropic (LLM providers)
- Redis, Supabase, Weights & Biases (optional monitoring)

### 2. Set Up Environment Variables

Create `backend/.env`:

```env
# Required
OPENAI_API_KEY=sk-your-key-here

# Optional - LLM Configuration
LLM_PROVIDER=openai
LLM_MODEL=gpt-3.5-turbo

# Optional - Embedding Model
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Optional - Vector Store
QDRANT_HOST=localhost
QDRANT_PORT=6333

# Optional - Cache
REDIS_URL=redis://localhost:6379

# Optional - Monitoring
WANDB_ENABLED=false
WANDB_PROJECT=rag-system
```

### 3. Start Services (Optional but Recommended)

If using Docker:

```powershell
# From project root
docker-compose up -d
```

This starts:
- Qdrant (vector database) on port 6333
- Redis (cache) on port 6379
- PostgreSQL/Supabase (logging) on port 5432

### 4. Run the Backend

```powershell
cd backend
python main.py
```

Or with uvicorn directly:

```powershell
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at: `http://localhost:8000`

API docs at: `http://localhost:8000/docs`

### 5. Run the Frontend

```powershell
cd frontend
npm install
npm run dev
```

Frontend will be available at: `http://localhost:5173`

## Quick Test

### Test the API

```powershell
# Health check
curl http://localhost:8000/health

# System info
curl http://localhost:8000/system/info

# Test query (will work even without documents)
curl -X POST http://localhost:8000/query `
  -H "Content-Type: application/json" `
  -d '{\"query\": \"What is RAG?\", \"strategy\": \"hybrid\"}'
```

### Test Evaluation

```powershell
# Compare strategies
curl -X POST http://localhost:8000/query/compare `
  -H "Content-Type: application/json" `
  -d '{\"query\": \"What is semantic search?\", \"strategies\": [\"semantic\", \"hybrid\"]}'

# Get monitoring metrics
curl http://localhost:8000/monitoring/metrics
```

## Without External Services

The system will work without Qdrant, Redis, or databases, but with limited functionality:

- **Without Qdrant**: Can't retrieve documents, but API endpoints work
- **Without Redis**: No caching, but queries still work
- **Without Supabase/PostgreSQL**: No persistent logging, but in-memory tracking works
- **Without W&B**: No external monitoring, but local metrics still available

## Minimal Setup (API Key Only)

If you just want to test the system:

1. Install dependencies: `pip install -r requirements.txt`
2. Set `OPENAI_API_KEY` in `.env`
3. Run `python main.py`
4. API will work but without document retrieval

## Next Steps

1. **Ingest Documents**: Use `/ingest` endpoint to add documents
2. **Test Queries**: Try different strategies (semantic, bm25, hybrid, hyde)
3. **Run Evaluation**: Use the test dataset to benchmark performance
4. **Monitor Costs**: Check `/monitoring/cost` to track token usage
5. **Compare Strategies**: Use `/query/compare` for A/B testing

## Troubleshooting

### "Import could not be resolved" errors

These are IDE warnings. Run `pip install -r requirements.txt` to install packages.

### "RAG pipeline not initialized"

Check that:
1. `OPENAI_API_KEY` is set
2. Qdrant is running (or remove Qdrant from initialization)
3. Check startup logs for errors

### Qdrant connection errors

Start Qdrant with Docker:
```powershell
docker run -p 6333:6333 qdrant/qdrant
```

Or modify `main.py` to skip Qdrant initialization.

### Port already in use

Change the port in `main.py`:
```python
uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
```

## Architecture Overview

```
Frontend (React) ←→ Backend (FastAPI) ←→ Qdrant (Vector DB)
                         ↓
                    OpenAI/Anthropic API
                         ↓
                    Redis (Cache)
                         ↓
                    Supabase (Logs)
                         ↓
                    Weights & Biases (Monitoring)
```

## Key Features Implemented

✅ **4 Retrieval Strategies**: Semantic, BM25, Hybrid, HyDE
✅ **Comprehensive Evaluation**: RAGAS + custom metrics
✅ **A/B Testing**: Built-in strategy comparison
✅ **Cost Tracking**: Real-time token & cost monitoring
✅ **Streaming**: SSE with inline citations
✅ **Caching**: Redis-based query caching
✅ **Monitoring**: Session metrics & W&B integration

## Demo Endpoints

Try these endpoints in your browser or with curl:

- http://localhost:8000 - API info
- http://localhost:8000/docs - Interactive API docs
- http://localhost:8000/health - Health check
- http://localhost:8000/system/info - System status
- http://localhost:8000/monitoring/metrics - Current metrics

Enjoy building with RAG! 🚀
