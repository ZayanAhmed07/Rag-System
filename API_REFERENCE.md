# API Endpoint Reference

Complete reference for all RAG System API endpoints.

Base URL: `http://localhost:8000`

## 📖 Quick Reference

| Category | Endpoint | Method | Description |
|----------|----------|--------|-------------|
| **Query** | `/query` | POST | Standard RAG query |
| | `/query/stream` | POST | Streaming response (SSE) |
| | `/query/compare` | POST | Compare multiple strategies |
| **Evaluation** | `/evaluate/single` | POST | Evaluate single answer |
| | `/evaluate/pipeline` | POST | Evaluate full pipeline |
| | `/evaluate/batch` | POST | Batch evaluation |
| | `/evaluate/compare` | POST | Compare with metrics |
| | `/evaluation/summary` | GET | Evaluation summary |
| **Monitoring** | `/monitoring/metrics` | GET | Session metrics |
| | `/monitoring/cost` | GET | Cost breakdown |
| | `/monitoring/reset` | POST | Reset metrics |
| **System** | `/` | GET | API info |
| | `/health` | GET | Health check |
| | `/system/info` | GET | System status |
| | `/stats` | GET | Statistics |

---

## 🔍 Query Endpoints

### POST /query

Standard RAG query with strategy selection.

**Request:**
```json
{
  "query": "What is Zero Knowledge Proof?",
  "strategy": "hybrid",  // semantic, bm25, hybrid, hyde
  "top_k": 5,
  "use_cache": true,
  "temperature": 0.7
}
```

**Response:**
```json
{
  "response": "Zero Knowledge Proof is a cryptographic method... [1][2]",
  "sources": [
    {
      "document": "crypto_basics.pdf",
      "content": "Zero Knowledge Proofs allow...",
      "score": 0.92
    }
  ],
  "metadata": {
    "strategy": "hybrid",
    "enhanced_query": null,
    "num_retrieved": 5,
    "retrieval_time": 0.23,
    "generation_time": 1.45,
    "total_time": 1.68,
    "tokens_used": 450,
    "estimated_cost": 0.0008,
    "cached": false
  }
}
```

**Strategies:**
- `semantic`: Pure embedding-based similarity
- `bm25`: Keyword-based (TF-IDF)
- `hybrid`: Combines both using RRF
- `hyde`: Hypothetical Document Embeddings

---

### POST /query/stream

Streaming response with Server-Sent Events.

**Request:** Same as `/query`

**Response:** SSE stream with events:

```
event: message
data: {"type": "status", "data": {"status": "retrieving", "message": "Retrieving documents..."}}

event: message
data: {"type": "sources", "data": {"sources": [...]}}

event: message
data: {"type": "status", "data": {"status": "generating", "message": "Generating answer..."}}

event: message
data: {"type": "chunk", "data": {"text": "Zero"}}

event: message
data: {"type": "chunk", "data": {"text": " Knowledge"}}

event: message
data: {"type": "complete", "data": {"answer": "...", "citations": [1, 2], "metadata": {...}}}
```

---

### POST /query/compare

Compare multiple retrieval strategies side-by-side.

**Request:**
```json
{
  "query": "What is semantic search?",
  "strategies": ["semantic", "bm25", "hybrid", "hyde"],
  "top_k": 5
}
```

**Response:**
```json
{
  "question": "What is semantic search?",
  "strategies": {
    "semantic": {
      "answer": "Semantic search uses embeddings...",
      "num_sources": 5,
      "total_time": 1.23,
      "tokens_used": 450,
      "estimated_cost": 0.0008
    },
    "hybrid": {
      "answer": "Semantic search combines...",
      "num_sources": 5,
      "total_time": 1.45,
      "tokens_used": 480,
      "estimated_cost": 0.0009
    },
    "hyde": {
      "answer": "Using hypothetical documents...",
      "num_sources": 5,
      "total_time": 1.67,
      "tokens_used": 520,
      "estimated_cost": 0.0010
    }
  },
  "comparison_metadata": {
    "timestamp": "2024-01-15T10:30:00",
    "top_k": 5
  }
}
```

---

## 📊 Evaluation Endpoints

### POST /evaluate/single

Evaluate a single query-response pair.

**Request:**
```json
{
  "query": "What is RAG?",
  "response": "RAG combines retrieval with generation...",
  "ground_truth": "Retrieval Augmented Generation combines...",
  "retrieved_docs": [
    "RAG systems retrieve relevant documents...",
    "The generation phase uses retrieved context..."
  ]
}
```

**Response:**
```json
{
  "metrics": {
    "answer_accuracy": 0.87,
    "faithfulness": 0.92,
    "context_precision": 0.85,
    "context_recall": 0.88,
    "answer_relevancy": 0.90,
    "citation_precision": 1.0,
    "semantic_similarity": 0.89,
    "answer_length": 45,
    "overall_score": 0.89
  },
  "timestamp": "2024-01-15T10:30:00"
}
```

---

### POST /evaluate/pipeline

Evaluate the full pipeline with a test question.

**Request:**
```json
{
  "question": "What is HyDE?",
  "ground_truth": "HyDE generates hypothetical answers...",
  "strategy": "hybrid",
  "top_k": 5
}
```

**Response:**
```json
{
  "question": "What is HyDE?",
  "strategy": "hybrid",
  "answer": "HyDE (Hypothetical Document Embeddings)...",
  "ground_truth": "HyDE generates hypothetical answers...",
  "metrics": {
    "answer_accuracy": 0.91,
    "faithfulness": 0.94,
    "overall_score": 0.92
  },
  "sources": [...],
  "metadata": {
    "total_time": 2.34,
    "tokens_used": 520
  },
  "evaluation_time": 3.45,
  "timestamp": "2024-01-15T10:30:00"
}
```

---

### POST /evaluate/batch

Batch evaluation across multiple test cases and strategies.

**Request:**
```json
{
  "test_cases": [
    {
      "question": "What is ZKP?",
      "ground_truth": "Zero Knowledge Proof is..."
    },
    {
      "question": "What is RAG?",
      "ground_truth": "Retrieval Augmented Generation..."
    }
  ],
  "strategies": ["semantic", "hybrid", "hyde"],
  "top_k": 5
}
```

**Response:**
```json
{
  "results_by_strategy": {
    "semantic": [
      {"question": "...", "metrics": {...}},
      {"question": "...", "metrics": {...}}
    ],
    "hybrid": [...],
    "hyde": [...]
  },
  "aggregated_metrics": {
    "semantic": {
      "overall_score": {"mean": 0.84, "min": 0.78, "max": 0.90, "std": 0.06},
      "faithfulness": {"mean": 0.86, "min": 0.80, "max": 0.92, "std": 0.06}
    },
    "hybrid": {
      "overall_score": {"mean": 0.89, "min": 0.85, "max": 0.93, "std": 0.04}
    }
  },
  "comparison_table": {
    "strategy": ["hybrid", "hyde", "semantic"],
    "overall_score_mean": [0.89, 0.87, 0.84],
    "faithfulness_mean": [0.91, 0.89, 0.86],
    "rank": [1, 2, 3]
  },
  "num_test_cases": 2,
  "strategies_tested": ["semantic", "hybrid", "hyde"],
  "timestamp": "2024-01-15T10:30:00"
}
```

---

### POST /evaluate/compare

Compare strategies for a single question with full evaluation.

**Request:**
```json
{
  "question": "What is Reciprocal Rank Fusion?",
  "ground_truth": "RRF is a method for combining...",
  "strategies": ["semantic", "hybrid"],
  "top_k": 5
}
```

**Response:**
```json
{
  "question": "What is Reciprocal Rank Fusion?",
  "results": {
    "semantic": {
      "answer": "...",
      "metrics": {"overall_score": 0.84}
    },
    "hybrid": {
      "answer": "...",
      "metrics": {"overall_score": 0.91}
    }
  },
  "winner": {
    "strategy": "hybrid",
    "score": 0.91
  },
  "timestamp": "2024-01-15T10:30:00"
}
```

---

### GET /evaluation/summary

Get summary of all evaluation runs.

**Response:**
```json
{
  "summary": "=== Evaluation Summary ===\n\nHYBRID:\n  Number of evaluations: 10\n  Average Overall Score: 0.891\n  Average Faithfulness: 0.915\n\nSEMANTIC:\n  Number of evaluations: 10\n  Average Overall Score: 0.842\n  Average Faithfulness: 0.867\n"
}
```

---

## 📈 Monitoring Endpoints

### GET /monitoring/metrics

Get current session metrics.

**Response:**
```json
{
  "session_metrics": {
    "total_queries": 42,
    "total_tokens": 21500,
    "total_cost": 0.0387,
    "avg_latency": 1.34,
    "cache_hits": 8,
    "cache_hit_rate": 0.19
  },
  "cost_breakdown": {
    "total_cost": 0.0387,
    "total_tokens": 21500,
    "avg_cost_per_query": 0.0009,
    "avg_tokens_per_query": 512
  },
  "timestamp": "2024-01-15T10:30:00"
}
```

---

### GET /monitoring/cost

Detailed cost breakdown.

**Response:**
```json
{
  "total_cost": 0.0387,
  "total_tokens": 21500,
  "avg_cost_per_query": 0.0009,
  "avg_tokens_per_query": 512
}
```

---

### POST /monitoring/reset

Reset session metrics.

**Response:**
```json
{
  "message": "Metrics reset successfully"
}
```

---

## 🔧 System Endpoints

### GET /

API information.

**Response:**
```json
{
  "message": "RAG System API",
  "version": "2.0.0",
  "status": "operational",
  "features": [
    "Hybrid Search (Semantic + BM25)",
    "Query Enhancement (HyDE)",
    "Streaming Responses",
    "Citation Tracking",
    "Comprehensive Evaluation (RAGAS)",
    "A/B Testing",
    "Cost & Token Tracking"
  ]
}
```

---

### GET /health

Health check.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00"
}
```

---

### GET /system/info

System information and health status.

**Response:**
```json
{
  "version": "2.0.0",
  "environment": "development",
  "features": {
    "rag_pipeline": true,
    "streaming": true,
    "evaluation": true,
    "monitoring": true
  },
  "configuration": {
    "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
    "llm_model": "gpt-3.5-turbo",
    "llm_provider": "openai"
  },
  "health": {
    "rag_pipeline": "healthy",
    "streaming": "healthy",
    "evaluation": "healthy",
    "monitoring": "healthy"
  },
  "status": "healthy"
}
```

---

### GET /stats

System statistics.

**Response:**
```json
{
  "total_documents": 150,
  "vector_store_size": "2.3GB",
  "avg_query_time": 1.34,
  "cache_hit_rate": 0.19,
  "total_queries": 42,
  "total_tokens": 21500,
  "total_cost": 0.0387
}
```

---

## 🔍 Error Responses

All endpoints return standard error responses:

```json
{
  "detail": "Error message describing what went wrong"
}
```

Common status codes:
- `200` - Success
- `400` - Bad Request (invalid input)
- `500` - Internal Server Error
- `503` - Service Unavailable (component not initialized)

---

## 📝 Usage Examples

### cURL Examples

```bash
# Basic query
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is RAG?", "strategy": "hybrid"}'

# Compare strategies
curl -X POST http://localhost:8000/query/compare \
  -H "Content-Type: application/json" \
  -d '{"query": "What is semantic search?", "strategies": ["semantic", "hybrid"]}'

# Get metrics
curl http://localhost:8000/monitoring/metrics
```

### Python Examples

```python
import requests

# Query
response = requests.post("http://localhost:8000/query", json={
    "query": "What is Zero Knowledge Proof?",
    "strategy": "hybrid",
    "top_k": 5
})
result = response.json()
print(result["response"])

# Evaluation
response = requests.post("http://localhost:8000/evaluate/pipeline", json={
    "question": "What is HyDE?",
    "ground_truth": "HyDE generates hypothetical answers...",
    "strategy": "hybrid"
})
metrics = response.json()["metrics"]
print(f"Overall Score: {metrics['overall_score']}")
```

---

## 🎯 Interactive Documentation

Visit `http://localhost:8000/docs` for interactive Swagger/OpenAPI documentation where you can test all endpoints directly in your browser!

---

**Complete API reference for the RAG System** 🚀
