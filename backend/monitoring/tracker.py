"""
Metrics Tracker - Tracks cost, tokens, latency, and logs to database
"""

from typing import Dict, Any, Optional
import time
from datetime import datetime
import uuid
import json


class MetricsTracker:
    """
    Tracks and logs RAG pipeline metrics
    - Token usage and costs
    - Latency
    - Query patterns
    - A/B test results
    """
    
    def __init__(
        self,
        supabase_client=None,
        wandb_enabled: bool = False,
        wandb_project: Optional[str] = None
    ):
        """
        Args:
            supabase_client: Supabase client for logging
            wandb_enabled: Enable Weights & Biases logging
            wandb_project: W&B project name
        """
        self.supabase = supabase_client
        self.wandb_enabled = wandb_enabled
        
        if wandb_enabled:
            try:
                import wandb
                wandb.init(project=wandb_project or "rag-system")
                self.wandb = wandb
            except ImportError:
                print("wandb not installed - disabling W&B logging")
                self.wandb_enabled = False
        
        self.active_queries = {}
        self.session_metrics = {
            "total_queries": 0,
            "total_tokens": 0,
            "total_cost": 0.0,
            "avg_latency": 0.0,
            "cache_hits": 0
        }
    
    async def start_query(self, query: str, strategy: str) -> str:
        """
        Start tracking a query
        
        Args:
            query: User query
            strategy: Retrieval strategy
            
        Returns:
            Query ID for tracking
        """
        query_id = str(uuid.uuid4())
        
        self.active_queries[query_id] = {
            "query": query,
            "strategy": strategy,
            "start_time": time.time(),
            "status": "in_progress"
        }
        
        return query_id
    
    async def complete_query(
        self,
        query_id: str,
        response: Optional[Dict[str, Any]] = None,
        success: bool = True,
        error: Optional[str] = None
    ):
        """
        Complete query tracking and log results
        
        Args:
            query_id: Query ID from start_query
            response: Query response with metadata
            success: Whether query succeeded
            error: Error message if failed
        """
        if query_id not in self.active_queries:
            return
        
        query_data = self.active_queries[query_id]
        latency = time.time() - query_data["start_time"]
        
        # Extract metrics from response
        tokens_used = 0
        cost = 0.0
        num_sources = 0
        
        if response:
            metadata = response.get("metadata", {})
            tokens_used = metadata.get("tokens_used", 0)
            cost = metadata.get("estimated_cost", 0.0)
            num_sources = len(response.get("sources", []))
        
        # Update session metrics
        self.session_metrics["total_queries"] += 1
        self.session_metrics["total_tokens"] += tokens_used
        self.session_metrics["total_cost"] += cost
        
        # Calculate running average latency
        n = self.session_metrics["total_queries"]
        old_avg = self.session_metrics["avg_latency"]
        self.session_metrics["avg_latency"] = (old_avg * (n - 1) + latency) / n
        
        # Prepare log entry
        log_entry = {
            "query_id": query_id,
            "query": query_data["query"],
            "strategy": query_data["strategy"],
            "success": success,
            "error": error,
            "latency": latency,
            "tokens_used": tokens_used,
            "estimated_cost": cost,
            "num_sources": num_sources,
            "timestamp": datetime.now().isoformat()
        }
        
        if response:
            log_entry["answer"] = response.get("answer", "")[:500]  # Truncate
            log_entry["citations"] = response.get("citations", [])
        
        # Log to Supabase
        if self.supabase:
            await self._log_to_supabase(log_entry)
        
        # Log to W&B
        if self.wandb_enabled:
            self._log_to_wandb(log_entry)
        
        # Clean up
        del self.active_queries[query_id]
    
    async def log_query(
        self,
        query: str,
        strategy: str,
        cached: bool = False,
        latency: float = 0.0
    ):
        """
        Quick log for cached queries
        
        Args:
            query: User query
            strategy: Strategy used
            cached: Was response cached
            latency: Response time
        """
        if cached:
            self.session_metrics["cache_hits"] += 1
            self.session_metrics["total_queries"] += 1
        
        log_entry = {
            "query_id": str(uuid.uuid4()),
            "query": query,
            "strategy": strategy,
            "cached": cached,
            "latency": latency,
            "timestamp": datetime.now().isoformat()
        }
        
        if self.supabase:
            await self._log_to_supabase(log_entry)
    
    async def log_ab_test(
        self,
        query: str,
        strategy_a: str,
        strategy_b: str,
        results_a: Dict[str, Any],
        results_b: Dict[str, Any],
        winner: Optional[str] = None,
        metrics: Optional[Dict[str, Any]] = None
    ):
        """
        Log A/B test comparison
        
        Args:
            query: Test query
            strategy_a: First strategy
            strategy_b: Second strategy
            results_a: Results from strategy A
            results_b: Results from strategy B
            winner: Which strategy won
            metrics: Comparison metrics
        """
        log_entry = {
            "test_id": str(uuid.uuid4()),
            "query": query,
            "strategy_a": strategy_a,
            "strategy_b": strategy_b,
            "winner": winner,
            "metrics": metrics,
            "results_a_summary": {
                "tokens": results_a.get("metadata", {}).get("tokens_used", 0),
                "cost": results_a.get("metadata", {}).get("estimated_cost", 0),
                "latency": results_a.get("metadata", {}).get("total_time", 0)
            },
            "results_b_summary": {
                "tokens": results_b.get("metadata", {}).get("tokens_used", 0),
                "cost": results_b.get("metadata", {}).get("estimated_cost", 0),
                "latency": results_b.get("metadata", {}).get("total_time", 0)
            },
            "timestamp": datetime.now().isoformat()
        }
        
        if self.supabase:
            await self._log_ab_test_to_supabase(log_entry)
        
        if self.wandb_enabled:
            self.wandb.log({
                "ab_test": log_entry,
                "winner": winner
            })
    
    def get_session_metrics(self) -> Dict[str, Any]:
        """Get current session metrics"""
        metrics = self.session_metrics.copy()
        
        # Add cache hit rate
        if metrics["total_queries"] > 0:
            metrics["cache_hit_rate"] = metrics["cache_hits"] / metrics["total_queries"]
        else:
            metrics["cache_hit_rate"] = 0.0
        
        return metrics
    
    def get_cost_breakdown(self) -> Dict[str, Any]:
        """Get detailed cost breakdown"""
        return {
            "total_cost": self.session_metrics["total_cost"],
            "total_tokens": self.session_metrics["total_tokens"],
            "avg_cost_per_query": (
                self.session_metrics["total_cost"] / self.session_metrics["total_queries"]
                if self.session_metrics["total_queries"] > 0 else 0
            ),
            "avg_tokens_per_query": (
                self.session_metrics["total_tokens"] / self.session_metrics["total_queries"]
                if self.session_metrics["total_queries"] > 0 else 0
            )
        }
    
    async def _log_to_supabase(self, log_entry: Dict[str, Any]):
        """Log to Supabase query_logs table"""
        if not self.supabase:
            return
        
        try:
            # Insert into query_logs table
            self.supabase.table("query_logs").insert(log_entry).execute()
        except Exception as e:
            print(f"Failed to log to Supabase: {e}")
    
    async def _log_ab_test_to_supabase(self, log_entry: Dict[str, Any]):
        """Log A/B test to Supabase"""
        if not self.supabase:
            return
        
        try:
            self.supabase.table("ab_tests").insert(log_entry).execute()
        except Exception as e:
            print(f"Failed to log A/B test to Supabase: {e}")
    
    def _log_to_wandb(self, log_entry: Dict[str, Any]):
        """Log to Weights & Biases"""
        if not self.wandb_enabled:
            return
        
        try:
            self.wandb.log({
                "query": log_entry["query"][:100],
                "strategy": log_entry["strategy"],
                "success": log_entry["success"],
                "latency": log_entry["latency"],
                "tokens": log_entry.get("tokens_used", 0),
                "cost": log_entry.get("estimated_cost", 0),
                "num_sources": log_entry.get("num_sources", 0)
            })
        except Exception as e:
            print(f"Failed to log to W&B: {e}")
    
    def reset_session_metrics(self):
        """Reset session metrics"""
        self.session_metrics = {
            "total_queries": 0,
            "total_tokens": 0,
            "total_cost": 0.0,
            "avg_latency": 0.0,
            "cache_hits": 0
        }


class TokenOptimizer:
    """
    Utilities for optimizing token usage
    """
    
    @staticmethod
    def trim_context(
        contexts: list,
        max_tokens: int,
        tokenizer
    ) -> list:
        """
        Trim contexts to fit within token budget
        
        Args:
            contexts: List of context strings
            max_tokens: Maximum tokens allowed
            tokenizer: Tokenizer (e.g., tiktoken encoder)
            
        Returns:
            Trimmed contexts
        """
        trimmed = []
        total_tokens = 0
        
        for context in contexts:
            context_tokens = len(tokenizer.encode(context))
            
            if total_tokens + context_tokens <= max_tokens:
                trimmed.append(context)
                total_tokens += context_tokens
            else:
                # Partial include if space available
                remaining_tokens = max_tokens - total_tokens
                if remaining_tokens > 100:  # Only if meaningful amount left
                    tokens = tokenizer.encode(context)[:remaining_tokens]
                    trimmed.append(tokenizer.decode(tokens))
                break
        
        return trimmed
    
    @staticmethod
    def score_and_rerank(
        contexts: list,
        scores: list,
        top_k: int
    ) -> list:
        """
        Rerank and select top-k contexts by score
        
        Args:
            contexts: List of contexts
            scores: List of relevance scores
            top_k: Number to keep
            
        Returns:
            Top-k contexts
        """
        scored_contexts = list(zip(contexts, scores))
        scored_contexts.sort(key=lambda x: x[1], reverse=True)
        return [ctx for ctx, _ in scored_contexts[:top_k]]
