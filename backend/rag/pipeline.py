"""
RAG Pipeline - Core orchestration for Retrieval Augmented Generation
"""

from typing import List, Dict, Any, Optional
import asyncio
from datetime import datetime
import json

from embeddings.embedder import EmbeddingModel
from retrieval.hybrid_search import HybridSearcher
from retrieval.query_enhancement import QueryEnhancer
from llm.generator import LLMGenerator
from monitoring.tracker import MetricsTracker
from cache.redis_cache import RedisCache


class RAGPipeline:
    """
    Complete RAG pipeline with multiple retrieval strategies
    """
    
    def __init__(
        self,
        embedder: EmbeddingModel,
        searcher: HybridSearcher,
        generator: LLMGenerator,
        query_enhancer: Optional[QueryEnhancer] = None,
        tracker: Optional[MetricsTracker] = None,
        cache: Optional[RedisCache] = None
    ):
        self.embedder = embedder
        self.searcher = searcher
        self.generator = generator
        self.query_enhancer = query_enhancer
        self.tracker = tracker
        self.cache = cache
    
    async def query(
        self,
        question: str,
        strategy: str = "hybrid",  # semantic, bm25, hybrid, hyde
        top_k: int = 5,
        use_cache: bool = True,
        include_sources: bool = True,
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """
        Execute a RAG query with specified strategy
        
        Args:
            question: User question
            strategy: Retrieval strategy (semantic, bm25, hybrid, hyde)
            top_k: Number of documents to retrieve
            use_cache: Whether to use caching
            include_sources: Include source documents in response
            temperature: LLM temperature
            
        Returns:
            Dict with answer, citations, sources, and metadata
        """
        start_time = datetime.now()
        
        # Check cache
        if use_cache and self.cache:
            cache_key = f"query:{strategy}:{question}:{top_k}"
            cached = await self.cache.get(cache_key)
            if cached:
                if self.tracker:
                    await self.tracker.log_query(
                        query=question,
                        strategy=strategy,
                        cached=True,
                        latency=0
                    )
                return json.loads(cached)
        
        # Track start
        if self.tracker:
            query_id = await self.tracker.start_query(question, strategy)
        
        try:
            # Step 1: Query Enhancement (if HyDE)
            enhanced_query = question
            if strategy == "hyde" and self.query_enhancer:
                enhanced_query = await self.query_enhancer.hyde(question)
            elif strategy in ["hybrid", "semantic"] and self.query_enhancer:
                # Optional: query rewriting for clarity
                enhanced_query = await self.query_enhancer.rewrite(question)
            
            # Step 2: Retrieve Documents
            if strategy == "semantic":
                results = await self.searcher.semantic_search(
                    query=enhanced_query,
                    top_k=top_k
                )
            elif strategy == "bm25":
                results = await self.searcher.bm25_search(
                    query=enhanced_query,
                    top_k=top_k
                )
            elif strategy == "hybrid":
                results = await self.searcher.hybrid_search(
                    query=enhanced_query,
                    top_k=top_k
                )
            elif strategy == "hyde":
                # For HyDE, use semantic search with enhanced query
                results = await self.searcher.semantic_search(
                    query=enhanced_query,
                    top_k=top_k
                )
            else:
                raise ValueError(f"Unknown strategy: {strategy}")
            
            # Step 3: Build Context
            context = self._build_context(results)
            
            # Step 4: Generate Answer with Citations
            generation_result = await self.generator.generate_with_citations(
                question=question,
                context=context,
                temperature=temperature
            )
            
            # Step 5: Format Response
            response = {
                "answer": generation_result["answer"],
                "citations": generation_result["citations"],
                "sources": self._format_sources(results) if include_sources else [],
                "metadata": {
                    "strategy": strategy,
                    "enhanced_query": enhanced_query if enhanced_query != question else None,
                    "num_retrieved": len(results),
                    "retrieval_time": generation_result.get("retrieval_time", 0),
                    "generation_time": generation_result.get("generation_time", 0),
                    "total_time": (datetime.now() - start_time).total_seconds(),
                    "tokens_used": generation_result.get("tokens_used", 0),
                    "estimated_cost": generation_result.get("estimated_cost", 0),
                    "cached": False
                }
            }
            
            # Cache result
            if use_cache and self.cache:
                await self.cache.set(
                    cache_key,
                    json.dumps(response),
                    expire=3600  # 1 hour
                )
            
            # Track completion
            if self.tracker:
                await self.tracker.complete_query(
                    query_id=query_id,
                    response=response,
                    success=True
                )
            
            return response
            
        except Exception as e:
            if self.tracker:
                await self.tracker.complete_query(
                    query_id=query_id,
                    response=None,
                    success=False,
                    error=str(e)
                )
            raise
    
    def _build_context(self, results: List[Dict[str, Any]]) -> str:
        """Build context from retrieved documents"""
        context_parts = []
        for idx, doc in enumerate(results):
            context_parts.append(
                f"[{idx + 1}] {doc['metadata'].get('source', 'Unknown')}\n{doc['content']}\n"
            )
        return "\n".join(context_parts)
    
    def _format_sources(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format source documents for response"""
        sources = []
        for doc in results:
            sources.append({
                "document": doc['metadata'].get('source', 'Unknown'),
                "content": doc['content'][:300] + "..." if len(doc['content']) > 300 else doc['content'],
                "score": doc.get('score', 0.0),
                "page": doc['metadata'].get('page'),
                "chunk_id": doc.get('id')
            })
        return sources
    
    async def compare_strategies(
        self,
        question: str,
        strategies: List[str] = ["bm25", "semantic", "hybrid", "hyde"],
        top_k: int = 5
    ) -> Dict[str, Any]:
        """
        Compare multiple retrieval strategies
        
        Args:
            question: User question
            strategies: List of strategies to compare
            top_k: Number of documents per strategy
            
        Returns:
            Comparison results with metrics
        """
        results = {}
        
        # Run all strategies in parallel
        tasks = [
            self.query(question, strategy=strategy, top_k=top_k, use_cache=False)
            for strategy in strategies
        ]
        
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        for strategy, response in zip(strategies, responses):
            if isinstance(response, Exception):
                results[strategy] = {"error": str(response)}
            else:
                results[strategy] = {
                    "answer": response["answer"],
                    "num_sources": len(response["sources"]),
                    "total_time": response["metadata"]["total_time"],
                    "tokens_used": response["metadata"]["tokens_used"],
                    "estimated_cost": response["metadata"]["estimated_cost"]
                }
        
        return {
            "question": question,
            "strategies": results,
            "comparison_metadata": {
                "timestamp": datetime.now().isoformat(),
                "top_k": top_k
            }
        }
