# Production-Ready RAG System

A complete Retrieval-Augmented Generation system with evaluation, monitoring, and production deployment.

## Features
- 🔍 Hybrid Search (Semantic + BM25)
- 🚀 Query Enhancement (HyDE, Rewriting)
- ⚡ Response Streaming
- 📊 Comprehensive Evaluation (RAGAS-style)
- 💾 Redis Caching
- 📈 Performance Monitoring
- 🔄 A/B Testing Framework

## Quick Start

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API keys
python main.py
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### Database Setup
```bash
# Initialize PostgreSQL schema
psql $DATABASE_URL -f backend/database/schema.sql
```

## API Endpoints
- POST /query - Query the RAG system
- POST /query/stream - Streaming responses
- POST /ingest - Ingest documents
- POST /evaluate - Evaluate responses
- GET /stats - System statistics

## Testing
```bash
cd backend
pytest tests/
```

## Documentation
See `/docs` folder for detailed documentation.
