"""
Evaluation Runner - Orchestrates comprehensive RAG evaluation
"""

from typing import List, Dict, Any, Optional
import asyncio
from datetime import datetime
import json
import pandas as pd

from evaluation.metrics import RAGMetrics, RAGASEvaluator


class EvaluationRunner:
    """
    Runs comprehensive evaluation experiments
    """
    
    def __init__(
        self,
        rag_pipeline,
        metrics: RAGMetrics,
        ragas_evaluator: Optional[RAGASEvaluator] = None
    ):
        self.rag_pipeline = rag_pipeline
        self.metrics = metrics
        self.ragas_evaluator = ragas_evaluator
        self.results = []
    
    async def evaluate_single(
        self,
        question: str,
        ground_truth: Optional[str] = None,
        strategy: str = "hybrid",
        top_k: int = 5
    ) -> Dict[str, Any]:
        """
        Evaluate a single query
        
        Args:
            question: Test question
            ground_truth: Reference answer
            strategy: Retrieval strategy
            top_k: Number of documents
            
        Returns:
            Evaluation results
        """
        start_time = datetime.now()
        
        # Run query
        response = await self.rag_pipeline.query(
            question=question,
            strategy=strategy,
            top_k=top_k,
            use_cache=False
        )
        
        # Extract contexts
        contexts = [source["content"] for source in response["sources"]]
        
        # Evaluate
        eval_metrics = await self.metrics.evaluate_answer(
            question=question,
            answer=response["answer"],
            ground_truth=ground_truth,
            retrieved_contexts=contexts
        )
        
        result = {
            "question": question,
            "strategy": strategy,
            "answer": response["answer"],
            "ground_truth": ground_truth,
            "metrics": eval_metrics,
            "sources": response["sources"],
            "metadata": response["metadata"],
            "evaluation_time": (datetime.now() - start_time).total_seconds(),
            "timestamp": datetime.now().isoformat()
        }
        
        self.results.append(result)
        return result
    
    async def evaluate_dataset(
        self,
        test_cases: List[Dict[str, str]],
        strategies: List[str] = ["semantic", "bm25", "hybrid", "hyde"],
        top_k: int = 5
    ) -> Dict[str, Any]:
        """
        Evaluate multiple test cases across strategies
        
        Args:
            test_cases: List of {question, ground_truth} dicts
            strategies: Strategies to test
            top_k: Number of documents
            
        Returns:
            Comprehensive evaluation results
        """
        results_by_strategy = {strategy: [] for strategy in strategies}
        
        for test_case in test_cases:
            question = test_case["question"]
            ground_truth = test_case.get("ground_truth")
            
            print(f"Evaluating: {question[:50]}...")
            
            # Test each strategy
            for strategy in strategies:
                try:
                    result = await self.evaluate_single(
                        question=question,
                        ground_truth=ground_truth,
                        strategy=strategy,
                        top_k=top_k
                    )
                    results_by_strategy[strategy].append(result)
                except Exception as e:
                    print(f"Error with {strategy}: {e}")
                    results_by_strategy[strategy].append({
                        "question": question,
                        "strategy": strategy,
                        "error": str(e)
                    })
        
        # Calculate aggregate metrics
        aggregated = self._aggregate_results(results_by_strategy)
        
        # Create comparison table
        comparison = self._create_comparison_table(aggregated)
        
        return {
            "results_by_strategy": results_by_strategy,
            "aggregated_metrics": aggregated,
            "comparison_table": comparison,
            "num_test_cases": len(test_cases),
            "strategies_tested": strategies,
            "timestamp": datetime.now().isoformat()
        }
    
    async def compare_strategies(
        self,
        question: str,
        ground_truth: Optional[str] = None,
        strategies: List[str] = ["semantic", "bm25", "hybrid", "hyde"],
        top_k: int = 5
    ) -> Dict[str, Any]:
        """
        Compare strategies for a single question
        
        Args:
            question: Test question
            ground_truth: Reference answer
            strategies: Strategies to compare
            top_k: Number of documents
            
        Returns:
            Comparison results with winner
        """
        results = {}
        
        # Evaluate with each strategy
        for strategy in strategies:
            try:
                result = await self.evaluate_single(
                    question=question,
                    ground_truth=ground_truth,
                    strategy=strategy,
                    top_k=top_k
                )
                results[strategy] = result
            except Exception as e:
                results[strategy] = {"error": str(e)}
        
        # Determine winner
        winner = self._determine_winner(results)
        
        return {
            "question": question,
            "results": results,
            "winner": winner,
            "timestamp": datetime.now().isoformat()
        }
    
    def _aggregate_results(
        self,
        results_by_strategy: Dict[str, List[Dict]]
    ) -> Dict[str, Dict[str, float]]:
        """
        Aggregate metrics across test cases
        """
        aggregated = {}
        
        for strategy, results in results_by_strategy.items():
            if not results or "error" in results[0]:
                continue
            
            # Collect all metric scores
            metric_scores = {}
            for result in results:
                if "metrics" in result:
                    for metric, score in result["metrics"].items():
                        if isinstance(score, (int, float)):
                            if metric not in metric_scores:
                                metric_scores[metric] = []
                            metric_scores[metric].append(score)
            
            # Calculate averages
            aggregated[strategy] = {}
            for metric, scores in metric_scores.items():
                aggregated[strategy][metric] = {
                    "mean": sum(scores) / len(scores),
                    "min": min(scores),
                    "max": max(scores),
                    "std": pd.Series(scores).std() if len(scores) > 1 else 0
                }
        
        return aggregated
    
    def _create_comparison_table(
        self,
        aggregated: Dict[str, Dict[str, Dict]]
    ) -> pd.DataFrame:
        """
        Create comparison table
        """
        rows = []
        
        for strategy, metrics in aggregated.items():
            row = {"strategy": strategy}
            for metric, stats in metrics.items():
                row[f"{metric}_mean"] = round(stats["mean"], 3)
            rows.append(row)
        
        df = pd.DataFrame(rows)
        
        # Add ranking column based on overall_score
        if "overall_score_mean" in df.columns:
            df = df.sort_values("overall_score_mean", ascending=False)
            df["rank"] = range(1, len(df) + 1)
        
        return df
    
    def _determine_winner(
        self,
        results: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Determine best strategy based on overall_score
        """
        best_strategy = None
        best_score = -1
        
        for strategy, result in results.items():
            if "error" not in result and "metrics" in result:
                score = result["metrics"].get("overall_score", 0)
                if score > best_score:
                    best_score = score
                    best_strategy = strategy
        
        return {
            "strategy": best_strategy,
            "score": best_score
        }
    
    def export_results(self, filepath: str):
        """Export results to JSON"""
        with open(filepath, "w") as f:
            json.dump(self.results, f, indent=2)
        print(f"Results exported to {filepath}")
    
    def get_summary(self) -> str:
        """Get text summary of results"""
        if not self.results:
            return "No evaluation results available"
        
        # Group by strategy
        by_strategy = {}
        for result in self.results:
            strategy = result.get("strategy", "unknown")
            if strategy not in by_strategy:
                by_strategy[strategy] = []
            by_strategy[strategy].append(result)
        
        summary = "=== Evaluation Summary ===\n\n"
        
        for strategy, results in by_strategy.items():
            summary += f"\n{strategy.upper()}:\n"
            summary += f"  Number of evaluations: {len(results)}\n"
            
            # Average scores
            if results and "metrics" in results[0]:
                avg_overall = sum(r["metrics"].get("overall_score", 0) for r in results) / len(results)
                avg_faithfulness = sum(r["metrics"].get("faithfulness", 0) for r in results) / len(results)
                
                summary += f"  Average Overall Score: {avg_overall:.3f}\n"
                summary += f"  Average Faithfulness: {avg_faithfulness:.3f}\n"
        
        return summary
