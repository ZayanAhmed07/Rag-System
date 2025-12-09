"""
Hybrid Search - Combines semantic search with BM25 keyword matching
"""

from typing import List, Dict, Any, Optional
import numpy as np
from rank_bm25 import BM25Okapi
import asyncio

from embeddings.embedder import EmbeddingModel
from vector_store.qdrant_manager import QdrantManager


class HybridSearcher:
    """
    Implements hybrid search combining:
    - Semantic search (dense embeddings)
    - BM25 keyword search (sparse)
    - RRF (Reciprocal Rank Fusion) for combining results
    """
    
    def __init__(
        self,
        embedder: EmbeddingModel,
        qdrant_manager: QdrantManager,
        collection_name: str = "documents",
        alpha: float = 0.5  # Weight for semantic vs BM25 (0.5 = equal weight)
    ):
        self.embedder = embedder
        self.qdrant_manager = qdrant_manager
        self.collection_name = collection_name
        self.alpha = alpha
        
        # BM25 index will be built from documents
        self.bm25_index = None
        self.documents = []
        self.document_ids = []
    
    async def initialize(self):
        """Initialize BM25 index from vector store"""
        # Check if Qdrant is available
        if not self.qdrant_manager.client:
            print("⚠️  Qdrant not available - skipping BM25 initialization")
            self.documents = []
            self.document_ids = []
            self.bm25_index = None
            return
        
        # Fetch all documents from Qdrant
        points = await self.qdrant_manager.get_all_points(self.collection_name)
        
        self.documents = []
        self.document_ids = []
        
        for point in points:
            self.documents.append(point.payload.get("content", ""))
            self.document_ids.append(point.id)
        
        # Build BM25 index only if we have documents
        if self.documents:
            tokenized_corpus = [doc.lower().split() for doc in self.documents]
            self.bm25_index = BM25Okapi(tokenized_corpus)
            print(f"✅ Initialized BM25 index with {len(self.documents)} documents")
        else:
            print("ℹ️  No documents found - BM25 index empty")
            self.bm25_index = None
    
    async def semantic_search(
        self,
        query: str,
        top_k: int = 5,
        score_threshold: float = 0.0
    ) -> List[Dict[str, Any]]:
        """
        Pure semantic search using embeddings
        
        Args:
            query: Search query
            top_k: Number of results
            score_threshold: Minimum similarity score
            
        Returns:
            List of documents with scores
        """
        # Check if vector store is available
        if not self.qdrant_manager.client:
            print("⚠️  Semantic search unavailable - Qdrant not connected")
            return []
        
        # Generate query embedding
        query_embedding = await self.embedder.embed_query(query)
        
        # Search in Qdrant
        results = await self.qdrant_manager.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            limit=top_k,
            score_threshold=score_threshold
        )
        
        return self._format_results(results, "semantic")
    
    async def bm25_search(
        self,
        query: str,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Pure BM25 keyword search
        
        Args:
            query: Search query
            top_k: Number of results
            
        Returns:
            List of documents with BM25 scores
        """
        if self.bm25_index is None:
            await self.initialize()
        
        if not self.documents:
            return []
        
        # If still no index, return empty
        if self.bm25_index is None or not self.documents:
            print("⚠️  BM25 search unavailable - no documents indexed")
            return []
        
        # Tokenize query
        tokenized_query = query.lower().split()
        
        # Get BM25 scores
        scores = self.bm25_index.get_scores(tokenized_query)
        
        # Get top-k indices
        top_indices = np.argsort(scores)[-top_k:][::-1]
        
        results = []
        for idx in top_indices:
            if scores[idx] > 0:  # Only include non-zero scores
                results.append({
                    "id": self.document_ids[idx],
                    "content": self.documents[idx],
                    "score": float(scores[idx]),
                    "metadata": await self._get_metadata(self.document_ids[idx])
                })
        
        return results
    
    async def hybrid_search(
        self,
        query: str,
        top_k: int = 5,
        alpha: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        Hybrid search combining semantic and BM25 using RRF
        
        Args:
            query: Search query
            top_k: Number of results
            alpha: Weight for semantic vs BM25 (overrides default)
            
        Returns:
            List of documents with combined scores
        """
        if alpha is None:
            alpha = self.alpha
        
        # Run both searches in parallel
        semantic_task = self.semantic_search(query, top_k=top_k * 2)
        bm25_task = self.bm25_search(query, top_k=top_k * 2)
        
        semantic_results, bm25_results = await asyncio.gather(
            semantic_task, bm25_task
        )
        
        # Combine using Reciprocal Rank Fusion (RRF)
        combined_scores = {}
        
        # Add semantic scores
        for rank, result in enumerate(semantic_results):
            doc_id = result["id"]
            # RRF formula: 1 / (k + rank), k=60 is standard
            rrf_score = 1 / (60 + rank + 1)
            combined_scores[doc_id] = {
                "semantic_score": result["score"],
                "semantic_rank": rank,
                "rrf_semantic": rrf_score * alpha,
                "content": result["content"],
                "metadata": result["metadata"]
            }
        
        # Add BM25 scores
        for rank, result in enumerate(bm25_results):
            doc_id = result["id"]
            rrf_score = 1 / (60 + rank + 1)
            
            if doc_id in combined_scores:
                combined_scores[doc_id]["bm25_score"] = result["score"]
                combined_scores[doc_id]["bm25_rank"] = rank
                combined_scores[doc_id]["rrf_bm25"] = rrf_score * (1 - alpha)
            else:
                combined_scores[doc_id] = {
                    "bm25_score": result["score"],
                    "bm25_rank": rank,
                    "rrf_bm25": rrf_score * (1 - alpha),
                    "semantic_score": 0,
                    "rrf_semantic": 0,
                    "content": result["content"],
                    "metadata": result["metadata"]
                }
        
        # Calculate final scores
        final_results = []
        for doc_id, scores in combined_scores.items():
            final_score = scores.get("rrf_semantic", 0) + scores.get("rrf_bm25", 0)
            final_results.append({
                "id": doc_id,
                "content": scores["content"],
                "score": final_score,
                "metadata": scores["metadata"],
                "score_breakdown": {
                    "semantic": scores.get("semantic_score", 0),
                    "bm25": scores.get("bm25_score", 0),
                    "final": final_score
                }
            })
        
        # Sort by final score and return top-k
        final_results.sort(key=lambda x: x["score"], reverse=True)
        return final_results[:top_k]
    
    def _format_results(
        self,
        results: List[Any],
        search_type: str
    ) -> List[Dict[str, Any]]:
        """Format Qdrant results to standard format"""
        formatted = []
        for result in results:
            formatted.append({
                "id": result.id,
                "content": result.payload.get("content", ""),
                "score": result.score,
                "metadata": {
                    "source": result.payload.get("source", "Unknown"),
                    "page": result.payload.get("page"),
                    "chunk_index": result.payload.get("chunk_index"),
                    "search_type": search_type
                }
            })
        return formatted
    
    async def _get_metadata(self, doc_id: str) -> Dict[str, Any]:
        """Get metadata for a document ID"""
        try:
            point = await self.qdrant_manager.get_point(
                collection_name=self.collection_name,
                point_id=doc_id
            )
            return {
                "source": point.payload.get("source", "Unknown"),
                "page": point.payload.get("page"),
                "chunk_index": point.payload.get("chunk_index")
            }
        except:
            return {"source": "Unknown"}
    
    async def update_index(self):
        """Rebuild BM25 index (call after ingesting new documents)"""
        await self.initialize()
