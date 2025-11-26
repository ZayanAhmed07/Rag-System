-- Database schema for RAG System
-- Tables for storing queries, responses, and metadata

CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255),
    content TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS query_logs (
    id SERIAL PRIMARY KEY,
    query TEXT NOT NULL,
    response TEXT,
    retrieved_docs INTEGER,
    response_time FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS evaluation_results (
    id SERIAL PRIMARY KEY,
    query_id INTEGER REFERENCES query_logs(id),
    relevance_score FLOAT,
    answer_relevance FLOAT,
    context_recall FLOAT,
    context_precision FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_query_logs_created ON query_logs(created_at);
CREATE INDEX idx_documents_created ON documents(created_at);
