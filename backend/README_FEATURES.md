# RAG System - Production Ready

A comprehensive Retrieval Augmented Generation system with advanced features including hybrid search, evaluation framework, A/B testing, and cost tracking.

## 🎯 Features

### Core RAG Pipeline
- ✅ **Document Ingestion** - PDFs, websites, markdown, databases
- ✅ **Smart Chunking** - Recursive and semantic chunking strategies
- ✅ **Embeddings** - HuggingFace sentence-transformers
- ✅ **Vector Storage** - Qdrant integration
- ✅ **Hybrid Search** - Combines semantic (dense) + BM25 (keyword) search
- ✅ **Query Enhancement** - HyDE and query rewriting
- ✅ **Context Building** - Intelligent prompt construction
- ✅ **LLM Generation** - OpenAI/Anthropic with inline citations

### Retrieval Strategies

1. **Semantic Search** - Pure embedding-based similarity
2. **BM25 Search** - Keyword-based ranking (TF-IDF)
3. **Hybrid Search** - RRF (Reciprocal Rank Fusion) combining both
4. **HyDE** - Hypothetical Document Embeddings for enhanced retrieval

### Evaluation Framework (🔥 What Sets This Apart)

Comprehensive metrics using RAGAS and custom implementations:

| Metric | Purpose |
|--------|---------|
| Answer Accuracy | Compare to ground truth |
| Faithfulness | Does answer stick to context? |
| Context Precision | Are retrieved docs relevant? |
| Context Recall | Is all needed info retrieved? |
| Answer Relevancy | Is answer relevant to question? |
| Citation Precision | Are citations correct? |
| Semantic Similarity | Embedding-based comparison |

### A/B Testing Framework

Compare strategies side-by-side:
- Automatic strategy comparison
- Performance metrics per strategy
- Cost and latency tracking
- Logs to Supabase/W&B

### Cost Tracking & Optimization

- Real-time token counting
- Estimated costs per query
- Session-wide metrics
- Token optimization utilities
- Context compression

### Streaming Support

- Server-Sent Events (SSE)
- Real-time answer generation
- Inline citations as they appear
- Source highlighting

## 📦 Installation

```bash
# Install dependencies
pip install -r backend/requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys

# Start services (Qdrant, Redis)
docker-compose up -d

# Run backend
cd backend
python main.py
```

## 🔧 Configuration

Create `.env` file:

```env
# LLM Configuration
LLM_PROVIDER=openai
LLM_MODEL=gpt-3.5-turbo
OPENAI_API_KEY=your_key_here

# Embedding Model
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Vector Store
QDRANT_HOST=localhost
QDRANT_PORT=6333

# Cache (Optional)
REDIS_URL=redis://localhost:6379

# Monitoring (Optional)
WANDB_ENABLED=false
WANDB_PROJECT=rag-system
```

## 🚀 API Endpoints

### Query Endpoints

```bash
# Basic query
POST /query
{
  "query": "What is Zero Knowledge Proof?",
  "strategy": "hybrid",
  "top_k": 5,
  "temperature": 0.7
}

# Streaming query
POST /query/stream
{
  "query": "Explain RAG systems",
  "strategy": "hyde",
  "top_k": 5
}

# Compare strategies
POST /query/compare
{
  "query": "What is BM25?",
  "strategies": ["semantic", "bm25", "hybrid", "hyde"],
  "top_k": 5
}
```

### Evaluation Endpoints

```bash
# Evaluate single answer
POST /evaluate/single
{
  "query": "What is RAG?",
  "response": "RAG combines retrieval with generation...",
  "ground_truth": "Retrieval Augmented Generation...",
  "retrieved_docs": ["doc1", "doc2"]
}

# Evaluate full pipeline
POST /evaluate/pipeline
{
  "question": "What is HyDE?",
  "ground_truth": "HyDE generates hypothetical...",
  "strategy": "hybrid",
  "top_k": 5
}

# Batch evaluation
POST /evaluate/batch
{
  "test_cases": [
    {"question": "Q1", "ground_truth": "A1"},
    {"question": "Q2", "ground_truth": "A2"}
  ],
  "strategies": ["semantic", "hybrid", "hyde"],
  "top_k": 5
}

# Compare strategies with evaluation
POST /evaluate/compare
{
  "question": "What is semantic search?",
  "ground_truth": "Semantic search uses embeddings...",
  "strategies": ["semantic", "bm25", "hybrid"]
}
```

### Monitoring Endpoints

```bash
# Get metrics
GET /monitoring/metrics

# Get cost breakdown
GET /monitoring/cost

# Reset metrics
POST /monitoring/reset

# System stats
GET /stats

# System health
GET /system/info
GET /health
```

## 📊 Strategy Comparison Example

```python
import requests

response = requests.post("http://localhost:8000/query/compare", json={
    "query": "What is Reciprocal Rank Fusion?",
    "strategies": ["semantic", "bm25", "hybrid", "hyde"]
})

# Returns performance comparison:
{
  "semantic": {
    "answer": "...",
    "num_sources": 5,
    "total_time": 1.23,
    "tokens_used": 450,
    "estimated_cost": 0.0008
  },
  "hybrid": {
    "answer": "...",
    "num_sources": 5,
    "total_time": 1.45,
    "tokens_used": 480,
    "estimated_cost": 0.0009
  },
  ...
}
```

## 📈 Evaluation Example

Run comprehensive evaluation:

```python
from evaluation.test_dataset import get_test_dataset
import requests

# Get test dataset
test_cases = get_test_dataset(limit=10)

# Run batch evaluation
response = requests.post("http://localhost:8000/evaluate/batch", json={
    "test_cases": test_cases,
    "strategies": ["semantic", "bm25", "hybrid", "hyde"]
})

# Returns aggregate metrics and comparison table
results = response.json()
print(results["comparison_table"])

# Example output:
# | Strategy | Overall Score | Faithfulness | Context Precision |
# |----------|--------------|--------------|-------------------|
# | hybrid   | 0.89        | 0.91         | 0.87             |
# | hyde     | 0.87        | 0.89         | 0.85             |
# | semantic | 0.84        | 0.86         | 0.82             |
# | bm25     | 0.78        | 0.80         | 0.76             |
```

## 🎯 Key Differentiators

### 1. Comprehensive Evaluation
Most RAG projects skip evaluation. This includes:
- RAGAS integration
- Custom metrics
- Automated benchmarking
- Strategy comparison

### 2. A/B Testing Built-in
- Compare strategies automatically
- Track performance over time
- Log to database for analysis

### 3. Cost Tracking
- Real-time token counting
- Cost estimation per query
- Session-wide metrics
- Optimization suggestions

### 4. Production Features
- Caching (Redis)
- Monitoring (W&B)
- Streaming responses
- Error handling
- Health checks

### 5. Multiple Retrieval Strategies
Not just semantic search - includes BM25, hybrid, and HyDE out of the box.

## 🔬 Architecture

```
┌─────────────┐
│   Query     │
└──────┬──────┘
       │
       ▼
┌─────────────────────┐
│ Query Enhancement   │  (HyDE, Rewriting)
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ Retrieval Strategy  │
│ • Semantic          │
│ • BM25              │
│ • Hybrid (RRF)      │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ Context Building    │  (Prompt Engineering)
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ LLM Generation      │  (With Citations)
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ Response            │  (Answer + Sources)
└─────────────────────┘
       │
       ▼
┌─────────────────────┐
│ Evaluation          │  (RAGAS Metrics)
└─────────────────────┘
       │
       ▼
┌─────────────────────┐
│ Monitoring          │  (Cost, Tokens, Logs)
└─────────────────────┘
```

## 📝 Project Structure

```
backend/
├── rag/
│   ├── pipeline.py          # Main RAG orchestration
│   └── streaming.py         # SSE streaming support
├── retrieval/
│   ├── hybrid_search.py     # Hybrid search (Semantic + BM25)
│   └── query_enhancement.py # HyDE, query rewriting
├── llm/
│   └── generator.py         # LLM wrapper with citations
├── evaluation/
│   ├── metrics.py           # RAGAS + custom metrics
│   ├── runner.py            # Evaluation orchestration
│   └── test_dataset.py      # Test cases
├── monitoring/
│   └── tracker.py           # Cost & token tracking
├── embeddings/
│   └── embedder.py          # Embedding generation
├── vector_store/
│   └── qdrant_manager.py    # Qdrant operations
├── cache/
│   └── redis_cache.py       # Redis caching
└── main.py                  # FastAPI application
```

## 🎓 Learning Resources

This project demonstrates:
- Production RAG architecture
- Multiple retrieval strategies
- Comprehensive evaluation (RAGAS)
- A/B testing framework
- Cost optimization
- Real-time streaming
- Monitoring and observability

Perfect for portfolio and interviews!

## 📄 License

MIT License - See LICENSE file for details

## 🤝 Contributing

Contributions welcome! This is a learning project showcasing best practices.

## 📧 Contact

Questions? Open an issue or reach out!

---

**⭐ Star this repo if you find it useful!**

This is a portfolio project demonstrating production-ready RAG with features that most projects miss.
