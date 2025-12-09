"""
Evaluation Metrics - Comprehensive RAG evaluation using RAGAS and custom metrics
"""

from typing import List, Dict, Any, Optional
import numpy as np
from datetime import datetime
import asyncio


class RAGMetrics:
    """
    Comprehensive metrics for RAG evaluation including RAGAS
    """
    
    def __init__(self, embedder=None, llm_generator=None):
        """
        Args:
            embedder: Embedding model for semantic similarity
            llm_generator: LLM for LLM-based metrics
        """
        self.embedder = embedder
        self.llm_generator = llm_generator
    
    async def evaluate_answer(
        self,
        question: str,
        answer: str,
        ground_truth: Optional[str] = None,
        retrieved_contexts: Optional[List[str]] = None,
        include_all_metrics: bool = True
    ) -> Dict[str, Any]:
        """
        Comprehensive evaluation of a single answer
        
        Args:
            question: Original question
            answer: Generated answer
            ground_truth: Reference answer (if available)
            retrieved_contexts: Retrieved document chunks
            include_all_metrics: Whether to compute all metrics
            
        Returns:
            Dict with all metric scores
        """
        metrics = {}
        
        # 1. Answer Accuracy (if ground truth available)
        if ground_truth:
            metrics["answer_accuracy"] = await self.answer_accuracy(
                answer, ground_truth
            )
        
        # 2. Faithfulness - does answer stick to context?
        if retrieved_contexts and self.llm_generator:
            metrics["faithfulness"] = await self.faithfulness(
                answer, retrieved_contexts
            )
        
        # 3. Context Precision - are retrieved contexts relevant?
        if retrieved_contexts and ground_truth and self.llm_generator:
            metrics["context_precision"] = await self.context_precision(
                question, retrieved_contexts, ground_truth
            )
        
        # 4. Context Recall - are all relevant contexts retrieved?
        if retrieved_contexts and ground_truth and self.llm_generator:
            metrics["context_recall"] = await self.context_recall(
                retrieved_contexts, ground_truth
            )
        
        # 5. Answer Relevancy - is answer relevant to question?
        if self.llm_generator:
            metrics["answer_relevancy"] = await self.answer_relevancy(
                question, answer
            )
        
        # 6. Citation Precision - are citations correct?
        if retrieved_contexts:
            metrics["citation_precision"] = self.citation_precision(
                answer, retrieved_contexts
            )
        
        # 7. Semantic Similarity (if ground truth available)
        if ground_truth and self.embedder:
            metrics["semantic_similarity"] = await self.semantic_similarity(
                answer, ground_truth
            )
        
        # 8. Answer Length Metrics
        metrics["answer_length"] = len(answer.split())
        
        # 9. Overall Score (weighted average)
        metrics["overall_score"] = self._calculate_overall_score(metrics)
        
        return metrics
    
    async def answer_accuracy(
        self,
        answer: str,
        ground_truth: str
    ) -> float:
        """
        Compare answer to ground truth using LLM
        
        Returns:
            Score 0-1
        """
        if not self.llm_generator:
            # Fallback to simple word overlap
            answer_words = set(answer.lower().split())
            truth_words = set(ground_truth.lower().split())
            if len(truth_words) == 0:
                return 0.0
            overlap = len(answer_words & truth_words) / len(truth_words)
            return min(overlap, 1.0)
        
        prompt = f"""Compare the following answer to the ground truth. Rate how accurate the answer is on a scale of 0-10.
Consider factual correctness and completeness.

Ground Truth: {ground_truth}

Answer: {answer}

Score (0-10):"""
        
        try:
            response = await self.llm_generator.generate(
                prompt=prompt,
                max_tokens=10,
                temperature=0
            )
            
            # Extract score
            score = float(response.strip().split()[0])
            return min(max(score / 10.0, 0.0), 1.0)
        except:
            return 0.0
    
    async def faithfulness(
        self,
        answer: str,
        contexts: List[str]
    ) -> float:
        """
        Measure if answer is faithful to retrieved contexts
        Uses LLM to verify each claim
        
        Returns:
            Score 0-1
        """
        if not self.llm_generator:
            return 0.0
        
        # Extract claims from answer
        claims_prompt = f"""Break down the following answer into individual factual claims (one per line):

Answer: {answer}

Claims:"""
        
        try:
            claims_response = await self.llm_generator.generate(
                prompt=claims_prompt,
                max_tokens=300,
                temperature=0
            )
            
            claims = [c.strip() for c in claims_response.split("\n") if c.strip()]
            claims = [c.lstrip("0123456789.-) ") for c in claims]
            
            if not claims:
                return 1.0
            
            # Verify each claim against contexts
            context_text = "\n\n".join(contexts)
            
            faithful_count = 0
            for claim in claims:
                verify_prompt = f"""Context:
{context_text}

Claim: {claim}

Is this claim supported by the context? Answer only "Yes" or "No".

Answer:"""
                
                verification = await self.llm_generator.generate(
                    prompt=verify_prompt,
                    max_tokens=5,
                    temperature=0
                )
                
                if "yes" in verification.lower():
                    faithful_count += 1
            
            return faithful_count / len(claims)
            
        except Exception as e:
            print(f"Faithfulness calculation failed: {e}")
            return 0.0
    
    async def context_precision(
        self,
        question: str,
        contexts: List[str],
        ground_truth: str
    ) -> float:
        """
        Measure precision of retrieved contexts
        What fraction of retrieved contexts are relevant?
        
        Returns:
            Score 0-1
        """
        if not self.llm_generator:
            return 0.0
        
        relevant_count = 0
        
        for context in contexts:
            prompt = f"""Question: {question}

Context: {context}

Is this context relevant for answering the question? Answer only "Yes" or "No".

Answer:"""
            
            try:
                response = await self.llm_generator.generate(
                    prompt=prompt,
                    max_tokens=5,
                    temperature=0
                )
                
                if "yes" in response.lower():
                    relevant_count += 1
            except:
                pass
        
        return relevant_count / len(contexts) if contexts else 0.0
    
    async def context_recall(
        self,
        contexts: List[str],
        ground_truth: str
    ) -> float:
        """
        Measure recall of retrieved contexts
        Does the context contain info needed to answer?
        
        Returns:
            Score 0-1
        """
        if not self.llm_generator:
            return 0.0
        
        context_text = "\n\n".join(contexts)
        
        prompt = f"""Ground Truth Answer: {ground_truth}

Retrieved Contexts:
{context_text}

What percentage (0-100) of the information in the ground truth can be found in the contexts?

Percentage:"""
        
        try:
            response = await self.llm_generator.generate(
                prompt=prompt,
                max_tokens=10,
                temperature=0
            )
            
            percentage = float(response.strip().split()[0].rstrip('%'))
            return min(max(percentage / 100.0, 0.0), 1.0)
        except:
            return 0.0
    
    async def answer_relevancy(
        self,
        question: str,
        answer: str
    ) -> float:
        """
        Measure if answer is relevant to question
        
        Returns:
            Score 0-1
        """
        if not self.llm_generator:
            return 0.0
        
        prompt = f"""Question: {question}

Answer: {answer}

Rate how relevant this answer is to the question on a scale of 0-10.

Score (0-10):"""
        
        try:
            response = await self.llm_generator.generate(
                prompt=prompt,
                max_tokens=10,
                temperature=0
            )
            
            score = float(response.strip().split()[0])
            return min(max(score / 10.0, 0.0), 1.0)
        except:
            return 0.0
    
    def citation_precision(
        self,
        answer: str,
        contexts: List[str]
    ) -> float:
        """
        Measure if citations in answer are valid
        
        Returns:
            Score 0-1
        """
        import re
        
        # Extract citations [N]
        citations = re.findall(r'\[(\d+)\]', answer)
        
        if not citations:
            # No citations used
            return 0.0
        
        valid_citations = [int(c) for c in citations if int(c) <= len(contexts)]
        
        return len(valid_citations) / len(citations) if citations else 0.0
    
    async def semantic_similarity(
        self,
        answer: str,
        ground_truth: str
    ) -> float:
        """
        Calculate semantic similarity using embeddings
        
        Returns:
            Cosine similarity 0-1
        """
        if not self.embedder:
            return 0.0
        
        try:
            answer_emb = await self.embedder.embed_query(answer)
            truth_emb = await self.embedder.embed_query(ground_truth)
            
            # Cosine similarity
            similarity = np.dot(answer_emb, truth_emb) / (
                np.linalg.norm(answer_emb) * np.linalg.norm(truth_emb)
            )
            
            return float(similarity)
        except:
            return 0.0
    
    def _calculate_overall_score(self, metrics: Dict[str, Any]) -> float:
        """
        Calculate weighted overall score
        """
        weights = {
            "answer_accuracy": 0.25,
            "faithfulness": 0.20,
            "context_precision": 0.15,
            "context_recall": 0.15,
            "answer_relevancy": 0.15,
            "citation_precision": 0.05,
            "semantic_similarity": 0.05
        }
        
        total_score = 0.0
        total_weight = 0.0
        
        for metric, weight in weights.items():
            if metric in metrics:
                total_score += metrics[metric] * weight
                total_weight += weight
        
        return total_score / total_weight if total_weight > 0 else 0.0


class RAGASEvaluator:
    """
    RAGAS-based evaluation (using the ragas library)
    """
    
    def __init__(self):
        try:
            from ragas import evaluate
            from ragas.metrics import (
                faithfulness,
                answer_relevancy,
                context_precision,
                context_recall
            )
            self.evaluate = evaluate
            self.metrics = [
                faithfulness,
                answer_relevancy,
                context_precision,
                context_recall
            ]
            self.available = True
        except ImportError:
            self.available = False
            print("RAGAS not available - using custom metrics only")
    
    async def evaluate_dataset(
        self,
        questions: List[str],
        answers: List[str],
        ground_truths: List[str],
        contexts: List[List[str]]
    ) -> Dict[str, Any]:
        """
        Evaluate using RAGAS library
        
        Args:
            questions: List of questions
            answers: List of generated answers
            ground_truths: List of reference answers
            contexts: List of retrieved contexts per question
            
        Returns:
            RAGAS evaluation results
        """
        if not self.available:
            return {"error": "RAGAS library not installed"}
        
        # Format data for RAGAS
        data = {
            "question": questions,
            "answer": answers,
            "ground_truth": ground_truths,
            "contexts": contexts
        }
        
        try:
            from datasets import Dataset
            dataset = Dataset.from_dict(data)
            
            # Run RAGAS evaluation
            results = self.evaluate(dataset, metrics=self.metrics)
            
            return results
        except Exception as e:
            return {"error": str(e)}
