"""
Query Enhancement - Implements HyDE and query rewriting
"""

from typing import List, Optional
import asyncio


class QueryEnhancer:
    """
    Enhances queries using:
    - HyDE (Hypothetical Document Embeddings)
    - Query rewriting for clarity
    - Multi-query generation
    """
    
    def __init__(self, llm_generator):
        """
        Args:
            llm_generator: LLM generator for query enhancement
        """
        self.llm_generator = llm_generator
    
    async def hyde(self, query: str) -> str:
        """
        HyDE: Generate a hypothetical answer, then use it for retrieval
        
        This technique generates what a good answer might look like,
        then searches for documents similar to that hypothetical answer.
        Often improves retrieval quality.
        
        Args:
            query: Original user query
            
        Returns:
            Hypothetical document (answer) to use for search
        """
        prompt = f"""Given the following question, write a brief, factual answer (2-3 sentences) as if you were answering from a knowledge base.
Don't say "I don't know" - make an educated guess based on the question.

Question: {query}

Hypothetical Answer:"""
        
        try:
            response = await self.llm_generator.generate(
                prompt=prompt,
                max_tokens=150,
                temperature=0.7
            )
            
            hypothetical_doc = response.strip()
            
            # Combine original query with hypothetical answer
            enhanced = f"{query}\n\n{hypothetical_doc}"
            
            return enhanced
            
        except Exception as e:
            print(f"HyDE generation failed: {e}")
            # Fallback to original query
            return query
    
    async def rewrite(self, query: str) -> str:
        """
        Rewrite query for better clarity and searchability
        
        Args:
            query: Original query
            
        Returns:
            Rewritten query
        """
        prompt = f"""Rewrite the following question to be clearer and more specific, while preserving the original intent.
Make it more suitable for semantic search.

Original: {query}

Rewritten:"""
        
        try:
            response = await self.llm_generator.generate(
                prompt=prompt,
                max_tokens=100,
                temperature=0.5
            )
            
            rewritten = response.strip()
            
            # If rewrite seems bad, use original
            if len(rewritten) < 10 or len(rewritten) > len(query) * 3:
                return query
            
            return rewritten
            
        except Exception as e:
            print(f"Query rewrite failed: {e}")
            return query
    
    async def generate_multi_queries(
        self,
        query: str,
        num_queries: int = 3
    ) -> List[str]:
        """
        Generate multiple variations of the query
        Useful for multi-query retrieval strategies
        
        Args:
            query: Original query
            num_queries: Number of query variations to generate
            
        Returns:
            List of query variations (including original)
        """
        prompt = f"""Given the following question, generate {num_queries - 1} alternative phrasings that ask for the same information in different ways.

Original Question: {query}

Alternative Questions (one per line):"""
        
        try:
            response = await self.llm_generator.generate(
                prompt=prompt,
                max_tokens=200,
                temperature=0.8
            )
            
            # Parse response
            variations = [line.strip() for line in response.split("\n") if line.strip()]
            variations = [q.lstrip("123456789.-) ") for q in variations]
            
            # Add original query
            all_queries = [query] + variations[:num_queries - 1]
            
            return all_queries
            
        except Exception as e:
            print(f"Multi-query generation failed: {e}")
            return [query]
    
    async def expand_with_keywords(self, query: str) -> str:
        """
        Expand query with relevant keywords and synonyms
        
        Args:
            query: Original query
            
        Returns:
            Expanded query with keywords
        """
        prompt = f"""Given the following question, provide 5-7 relevant keywords and synonyms that would help find related information.

Question: {query}

Keywords (comma-separated):"""
        
        try:
            response = await self.llm_generator.generate(
                prompt=prompt,
                max_tokens=100,
                temperature=0.6
            )
            
            keywords = response.strip()
            
            # Combine original with keywords
            expanded = f"{query} {keywords}"
            
            return expanded
            
        except Exception as e:
            print(f"Keyword expansion failed: {e}")
            return query
    
    async def decompose_query(self, query: str) -> List[str]:
        """
        Decompose complex query into simpler sub-questions
        
        Args:
            query: Complex query
            
        Returns:
            List of simpler sub-questions
        """
        prompt = f"""Break down the following complex question into 2-4 simpler sub-questions that, when answered together, would answer the original question.

Complex Question: {query}

Sub-questions (one per line):"""
        
        try:
            response = await self.llm_generator.generate(
                prompt=prompt,
                max_tokens=200,
                temperature=0.7
            )
            
            # Parse sub-questions
            sub_questions = [line.strip() for line in response.split("\n") if line.strip()]
            sub_questions = [q.lstrip("123456789.-) ") for q in sub_questions]
            
            return sub_questions if sub_questions else [query]
            
        except Exception as e:
            print(f"Query decomposition failed: {e}")
            return [query]
