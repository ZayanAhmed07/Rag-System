# System Architecture

## Overview
This RAG system consists of multiple components working together:

1. **Document Ingestion Pipeline** - Loads, chunks, and indexes documents
2. **Embedding Service** - Converts text to dense vectors
3. **Vector Store** - Stores and searches embeddings (Qdrant)
4. **Retrieval Engine** - Hybrid search combining BM25 and semantic search
5. **Query Enhancement** - HyDE, query rewriting, and optimization
6. **LLM Generator** - Generates responses using retrieved context
7. **Evaluation Framework** - Metrics for answer quality
8. **Caching Layer** - Redis for performance optimization
9. **Monitoring** - Tracks performance and quality metrics

## Data Flow
1. User query comes in
2. Query is enhanced (rewritten, HyDE queries generated)
3. Hybrid search retrieves relevant documents
4. LLM generates response with retrieved context
5. Response is streamed to user
6. Evaluation metrics are computed and logged

## Technology Stack
- **Framework**: FastAPI (async)
- **Embeddings**: Sentence Transformers
- **Vector DB**: Qdrant
- **LLM**: HuggingFace models (configurable)
- **Database**: PostgreSQL
- **Cache**: Redis
- **Frontend**: React + Vite + Tailwind
