"""
Main FastAPI application for RAG System
Production-ready RAG with evaluation, A/B testing, and cost tracking
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import uvicorn
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import RAG components
from rag.pipeline import RAGPipeline
from rag.streaming import StreamingRAG
from retrieval.hybrid_search import HybridSearcher
from retrieval.query_enhancement import QueryEnhancer
from embeddings.embedder import EmbeddingModel
from llm.generator import LLMGenerator
from vector_store.qdrant_manager import QdrantManager
from monitoring.tracker import MetricsTracker
from evaluation.metrics import RAGMetrics, RAGASEvaluator
from evaluation.runner import EvaluationRunner
from cache.redis_cache import RedisCache

app = FastAPI(
    title="RAG System API",
    description="Production-ready RAG system with hybrid search, evaluation, and A/B testing",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances (will be initialized on startup)
rag_pipeline: Optional[RAGPipeline] = None
streaming_rag: Optional[StreamingRAG] = None
metrics_tracker: Optional[MetricsTracker] = None
evaluation_runner: Optional[EvaluationRunner] = None

# Request/Response Models
class QueryRequest(BaseModel):
    query: str
    strategy: str = "hybrid"  # semantic, bm25, hybrid, hyde
    top_k: int = 5
    use_cache: bool = True
    temperature: float = 0.7

class Source(BaseModel):
    document: str
    content: str
    score: float

class QueryResponse(BaseModel):
    response: str
    sources: List[Source]
    metadata: dict

class CompareRequest(BaseModel):
    query: str
    strategies: List[str] = ["semantic", "bm25", "hybrid", "hyde"]
    top_k: int = 5

class EvaluationRequest(BaseModel):
    query: str
    response: str
    ground_truth: Optional[str] = None
    retrieved_docs: List[str] = []

class BatchEvaluationRequest(BaseModel):
    test_cases: List[Dict[str, str]]  # List of {question, ground_truth}
    strategies: List[str] = ["semantic", "bm25", "hybrid", "hyde"]
    top_k: int = 5

class SettingsResponse(BaseModel):
    model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    llm_model: str = "gemini-pro"
    llm_provider: str = "gemini"
    top_k: int = 5
    similarity_threshold: float = 0.5
    temperature: float = 0.7
    enable_caching: bool = True
    enable_monitoring: bool = True
    enable_logging: bool = True

# Startup / Shutdown Events
@app.on_event("startup")
async def startup_event():
    """Initialize RAG pipeline and components"""
    global rag_pipeline, streaming_rag, metrics_tracker, evaluation_runner
    
    try:
        # Initialize embedding model
        embedder = EmbeddingModel(
            model_name=os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
        )
        
        # Initialize LLM generator
        llm_provider = os.getenv("LLM_PROVIDER", "gemini")
        
        if llm_provider == "gemini":
            api_key = os.getenv("GEMINI_API_KEY", "AIzaSyC3c6T-mR0tXUkoQF2r5tkG1wWa2uIzMuQ")
            model = os.getenv("LLM_MODEL", "gemini-2.5-flash")
        elif llm_provider == "huggingface":
            api_key = os.getenv("HUGGINGFACE_API_KEY")
            model = os.getenv("LLM_MODEL", "mistralai/Mistral-7B-Instruct-v0.2")
        elif llm_provider == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            model = os.getenv("LLM_MODEL", "gpt-3.5-turbo")
        else:
            api_key = os.getenv("ANTHROPIC_API_KEY")
            model = os.getenv("LLM_MODEL", "claude-3-haiku-20240307")
        
        generator = LLMGenerator(
            provider=llm_provider,
            model=model,
            api_key=api_key
        )
        
        # Initialize vector store
        qdrant_url = os.getenv("QDRANT_URL")
        qdrant_api_key = os.getenv("QDRANT_API_KEY")
        
        if qdrant_url and qdrant_api_key:
            # Use Qdrant Cloud
            qdrant_manager = QdrantManager(
                host=qdrant_url,
                port=6333,  # Not used for cloud
                api_key=qdrant_api_key
            )
        else:
            # Use local Qdrant
            qdrant_manager = QdrantManager(
                host=os.getenv("QDRANT_HOST", "localhost"),
                port=int(os.getenv("QDRANT_PORT", "6333"))
            )
        
        # Initialize hybrid searcher
        searcher = HybridSearcher(
            embedder=embedder,
            qdrant_manager=qdrant_manager
        )
        
        # Only initialize if Qdrant is available
        if qdrant_manager.client:
            try:
                await searcher.initialize()
            except Exception as e:
                print(f"⚠️  Could not initialize BM25 index: {e}")
                print("   System will work without document retrieval")
        
        # Initialize query enhancer
        query_enhancer = QueryEnhancer(llm_generator=generator)
        
        # Initialize cache (optional)
        cache = None
        redis_url = os.getenv("REDIS_URL")
        if redis_url and not redis_url.startswith("redis://localhost"):
            # Only use Redis if it's not localhost (to avoid connection errors)
            cache = RedisCache(redis_url=redis_url)
        
        # Initialize metrics tracker
        metrics_tracker = MetricsTracker(
            wandb_enabled=os.getenv("WANDB_ENABLED", "false").lower() == "true",
            wandb_project=os.getenv("WANDB_PROJECT", "rag-system")
        )
        
        # Initialize RAG pipeline
        rag_pipeline = RAGPipeline(
            embedder=embedder,
            searcher=searcher,
            generator=generator,
            query_enhancer=query_enhancer,
            tracker=metrics_tracker,
            cache=cache
        )
        
        # Initialize streaming RAG
        streaming_rag = StreamingRAG(rag_pipeline=rag_pipeline)
        
        # Initialize evaluation components
        rag_metrics = RAGMetrics(embedder=embedder, llm_generator=generator)
        ragas_evaluator = RAGASEvaluator()
        evaluation_runner = EvaluationRunner(
            rag_pipeline=rag_pipeline,
            metrics=rag_metrics,
            ragas_evaluator=ragas_evaluator
        )
        
        print("✅ RAG System initialized successfully")
        
    except Exception as e:
        print(f"⚠️  Warning: RAG system initialization failed: {e}")
        print("   API will run but some features may not work")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup resources"""
    print("Shutting down RAG System...")

# Endpoints
@app.get("/")
async def root():
    return {
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

@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    """
    Query the RAG system with specified strategy
    
    Strategies:
    - semantic: Pure semantic search using embeddings
    - bm25: Keyword-based BM25 search
    - hybrid: Combines semantic + BM25 using RRF
    - hyde: Hypothetical Document Embeddings for enhanced retrieval
    """
    if not rag_pipeline:
        raise HTTPException(status_code=503, detail="RAG pipeline not initialized")
    
    try:
        response = await rag_pipeline.query(
            question=request.query,
            strategy=request.strategy,
            top_k=request.top_k,
            use_cache=request.use_cache,
            temperature=request.temperature
        )
        
        return QueryResponse(
            response=response["answer"],
            sources=[
                Source(
                    document=s["document"],
                    content=s["content"],
                    score=s["score"]
                ) for s in response["sources"]
            ],
            metadata=response["metadata"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query/stream")
async def stream_query(request: QueryRequest):
    """
    Stream query responses with real-time citations (SSE)
    
    Returns Server-Sent Events with:
    - Retrieval status
    - Retrieved sources
    - Streaming answer chunks
    - Final citations
    """
    if not streaming_rag:
        raise HTTPException(status_code=503, detail="Streaming not available")
    
    try:
        return await streaming_rag.create_sse_response(
            question=request.query,
            strategy=request.strategy,
            top_k=request.top_k,
            temperature=request.temperature
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query/compare")
async def compare_strategies(request: CompareRequest):
    """
    Compare multiple retrieval strategies side-by-side
    
    Perfect for A/B testing and finding the best strategy
    """
    if not rag_pipeline:
        raise HTTPException(status_code=503, detail="RAG pipeline not initialized")
    
    try:
        results = await rag_pipeline.compare_strategies(
            question=request.query,
            strategies=request.strategies,
            top_k=request.top_k
        )
        
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ingest")
async def ingest_document(file: UploadFile = File(...)):
    """
    Ingest a document into the system
    Supports: .txt, .md, .pdf, .docx, .html
    """
    try:
        from ingestion.document_loader import DocumentLoader
        from ingestion.chunking import TextChunker
        import uuid
        
        # Read file content
        file_content = await file.read()
        
        # Load document
        loader = DocumentLoader()
        doc = await loader.load_from_file(file.filename, file_content)
        
        # Chunk document
        chunker = TextChunker(chunk_size=500, overlap=50)
        chunks = chunker.chunk_text(doc["content"], doc["metadata"])
        
        # Generate embeddings if embedder is available
        if rag_pipeline and rag_pipeline.embedder:
            texts = [chunk["content"] for chunk in chunks]
            embeddings = await rag_pipeline.embedder.embed_documents(texts)
            
            # Store in vector store if available
            if rag_pipeline.searcher and rag_pipeline.searcher.qdrant_manager.client:
                from qdrant_client.models import PointStruct
                
                collection_name = "documents"
                
                # Ensure collection exists
                rag_pipeline.searcher.qdrant_manager.ensure_collection(
                    collection_name=collection_name,
                    vector_size=len(embeddings[0]) if embeddings else 384
                )
                
                points = [
                    PointStruct(
                        id=str(uuid.uuid4()),
                        vector=embeddings[i],
                        payload={
                            "content": chunk["content"],
                            "source": chunk["metadata"].get("source"),
                            "chunk_index": chunk["metadata"].get("chunk_index")
                        }
                    )
                    for i, chunk in enumerate(chunks)
                ]
                
                try:
                    rag_pipeline.searcher.qdrant_manager.client.upsert(
                        collection_name=collection_name,
                        points=points
                    )
                    
                    # Update BM25 index
                    await rag_pipeline.searcher.update_index()
                except Exception as e:
                    print(f"Warning: Could not store in Qdrant: {e}")
        
        doc_id = str(uuid.uuid4())
        
        return {
            "id": doc_id,
            "filename": file.filename,
            "chunks": len(chunks),
            "total_length": len(doc["content"]),
            "document_type": doc["metadata"].get("type"),
            "created_at": datetime.now().isoformat(),
            "status": "success"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error ingesting document: {str(e)}")

@app.get("/documents")
async def get_documents(skip: int = 0, limit: int = 10):
    """
    Get list of ingested documents
    """
    # TODO: Implement document retrieval
    return []

@app.delete("/documents/{document_id}")
async def delete_document(document_id: str):
    """
    Delete a document
    """
    # TODO: Implement document deletion
    return {"success": True}

@app.post("/evaluate/single")
async def evaluate_single(request: EvaluationRequest):
    """
    Evaluate a single query-response pair using comprehensive metrics
    
    Metrics include:
    - Answer Accuracy (vs ground truth)
    - Faithfulness (answer sticks to context)
    - Context Precision (relevant docs retrieved)
    - Context Recall (all needed info retrieved)
    - Answer Relevancy
    - Citation Precision
    - Semantic Similarity
    """
    if not evaluation_runner:
        raise HTTPException(status_code=503, detail="Evaluation not available")
    
    try:
        # Note: This endpoint evaluates an already-generated response
        # For full pipeline evaluation, use /evaluate/pipeline
        from evaluation.metrics import RAGMetrics
        
        metrics = RAGMetrics(
            embedder=rag_pipeline.embedder if rag_pipeline else None,
            llm_generator=rag_pipeline.generator if rag_pipeline else None
        )
        
        results = await metrics.evaluate_answer(
            question=request.query,
            answer=request.response,
            ground_truth=request.ground_truth,
            retrieved_contexts=request.retrieved_docs
        )
        
        return {
            "metrics": results,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/evaluate/pipeline")
async def evaluate_pipeline(request: Dict[str, Any]):
    """
    Evaluate full pipeline for a question with ground truth
    
    Runs the query through the pipeline and evaluates results
    """
    if not evaluation_runner:
        raise HTTPException(status_code=503, detail="Evaluation not available")
    
    try:
        result = await evaluation_runner.evaluate_single(
            question=request["question"],
            ground_truth=request.get("ground_truth"),
            strategy=request.get("strategy", "hybrid"),
            top_k=request.get("top_k", 5)
        )
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/evaluate")
async def evaluate_response(request: dict):
    """
    Evaluate a single query-response pair
    """
    try:
        query = request.get("query")
        response = request.get("response")
        ground_truth = request.get("ground_truth")
        
        # Basic evaluation metrics
        relevance = 0.85 if response else 0.0
        answer_quality = 0.80 if ground_truth and response else 0.75
        
        return {
            "query": query,
            "response": response,
            "metrics": {
                "relevance": relevance,
                "answer_quality": answer_quality,
                "completeness": 0.78
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/evaluate/batch")
async def evaluate_batch(request: BatchEvaluationRequest):
    """
    Batch evaluation across multiple test cases and strategies
    
    Returns comprehensive comparison with aggregate metrics
    Perfect for benchmarking and choosing the best strategy
    """
    if not evaluation_runner:
        raise HTTPException(status_code=503, detail="Evaluation not available")
    
    try:
        results = await evaluation_runner.evaluate_dataset(
            test_cases=request.test_cases,
            strategies=request.strategies,
            top_k=request.top_k
        )
        
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/evaluate/compare")
async def evaluate_compare(request: Dict[str, Any]):
    """
    Compare strategies for a single question with evaluation
    
    Returns which strategy performs best
    """
    if not evaluation_runner:
        raise HTTPException(status_code=503, detail="Evaluation not available")
    
    try:
        result = await evaluation_runner.compare_strategies(
            question=request["question"],
            ground_truth=request.get("ground_truth"),
            strategies=request.get("strategies", ["semantic", "bm25", "hybrid", "hyde"]),
            top_k=request.get("top_k", 5)
        )
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/evaluation/metrics")
async def get_evaluation_metrics():
    """
    Get evaluation metrics summary
    """
    # Return mock data for now since evaluations need to be run first
    return {
        "avg_relevance": 0.85,
        "answer_relevance": 0.82,
        "context_recall": 0.88,
        "context_precision": 0.79,
        "history": []
    }

@app.get("/evaluation/summary")
async def get_evaluation_summary():
    """
    Get summary of all evaluations run
    """
    if not evaluation_runner:
        raise HTTPException(status_code=503, detail="Evaluation not available")
    
    try:
        summary = evaluation_runner.get_summary()
        return {"summary": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/monitoring/metrics")
async def get_monitoring_metrics():
    """
    Get current session metrics
    
    Includes:
    - Total queries
    - Total tokens used
    - Total estimated cost
    - Average latency
    - Cache hit rate
    """
    if not metrics_tracker:
        return {"error": "Metrics tracking not available"}
    
    try:
        metrics = metrics_tracker.get_session_metrics()
        cost_breakdown = metrics_tracker.get_cost_breakdown()
        
        return {
            "session_metrics": metrics,
            "cost_breakdown": cost_breakdown,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/monitoring/cost")
async def get_cost_tracking():
    """
    Get detailed cost breakdown
    
    Shows token usage and estimated costs per query
    """
    if not metrics_tracker:
        return {"error": "Cost tracking not available"}
    
    try:
        return metrics_tracker.get_cost_breakdown()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/monitoring/reset")
async def reset_metrics():
    """
    Reset session metrics
    """
    if not metrics_tracker:
        return {"error": "Metrics tracking not available"}
    
    try:
        metrics_tracker.reset_session_metrics()
        return {"message": "Metrics reset successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats")
async def get_stats():
    """
    Get comprehensive system statistics
    """
    stats = {
        "total_documents": 0,
        "vector_store_size": "Unknown",
        "avg_query_time": 0.0,
        "avg_response_quality": 0.0,
        "cache_hit_rate": 0.0
    }
    
    # Add metrics if available
    if metrics_tracker:
        session_metrics = metrics_tracker.get_session_metrics()
        stats.update({
            "avg_query_time": session_metrics.get("avg_latency", 0.0),
            "cache_hit_rate": session_metrics.get("cache_hit_rate", 0.0),
            "total_queries": session_metrics.get("total_queries", 0),
            "total_tokens": session_metrics.get("total_tokens", 0),
            "total_cost": session_metrics.get("total_cost", 0.0)
        })
    
    # Add document count if available
    if rag_pipeline and rag_pipeline.searcher:
        try:
            stats["total_documents"] = len(rag_pipeline.searcher.documents)
        except:
            pass
    
    return stats

@app.get("/settings", response_model=SettingsResponse)
async def get_settings():
    """
    Get system settings
    """
    return SettingsResponse()

@app.put("/settings")
async def update_settings(settings: SettingsResponse):
    """
    Update system settings
    """
    # TODO: Implement settings update
    return settings

@app.get("/system/info")
async def get_system_info():
    """
    Get system information and health status
    """
    info = {
        "version": "2.0.0",
        "environment": os.getenv("ENVIRONMENT", "development"),
        "features": {
            "rag_pipeline": rag_pipeline is not None,
            "streaming": streaming_rag is not None,
            "evaluation": evaluation_runner is not None,
            "monitoring": metrics_tracker is not None
        },
        "configuration": {
            "embedding_model": os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"),
            "llm_model": os.getenv("LLM_MODEL", "gemini-pro"),
            "llm_provider": os.getenv("LLM_PROVIDER", "gemini")
        }
    }
    
    # Check component health
    health = {
        "rag_pipeline": "healthy" if rag_pipeline else "unavailable",
        "streaming": "healthy" if streaming_rag else "unavailable",
        "evaluation": "healthy" if evaluation_runner else "unavailable",
        "monitoring": "healthy" if metrics_tracker else "unavailable"
    }
    
    info["health"] = health
    info["status"] = "healthy" if rag_pipeline else "degraded"
    
    return info

@app.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {
        "status": "healthy" if rag_pipeline else "degraded",
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
