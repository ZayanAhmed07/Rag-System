# API Reference

## Query Endpoint

### POST /query
Submit a query to the RAG system and get a response.

**Request Body:**
```json
{
  "query": "What is machine learning?",
  "top_k": 5,
  "use_cache": true,
  "hybrid_search": true
}
```

**Response:**
```json
{
  "response": "Machine learning is...",
  "sources": [
    {
      "document": "filename.pdf",
      "content": "...",
      "score": 0.95
    }
  ],
  "metadata": {
    "retrieval_time": 0.23,
    "generation_time": 1.45,
    "cached": false
  }
}
```

## Stream Query Endpoint

### POST /query/stream
Get responses streamed back in real-time.

Uses Server-Sent Events (SSE) for streaming responses.

## Document Ingestion

### POST /ingest
Ingest documents into the system.

**Request Body:**
```json
{
  "file": "<binary file data>",
  "document_type": "pdf"
}
```

## Evaluation

### POST /evaluate
Evaluate a query-response pair.

**Request Body:**
```json
{
  "query": "...",
  "response": "...",
  "ground_truth": "...",
  "retrieved_docs": ["doc1", "doc2"]
}
```

## Statistics

### GET /stats
Get system statistics and metrics.

**Response:**
```json
{
  "total_documents": 1523,
  "vector_store_size": "2.4GB",
  "avg_query_time": 0.45,
  "avg_response_quality": 0.82,
  "cache_hit_rate": 0.34
}
```
