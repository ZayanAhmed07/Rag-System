"""
Streaming Support - SSE streaming with inline citations
"""

from typing import AsyncGenerator, Dict, Any
import json
import asyncio
from datetime import datetime
from sse_starlette.sse import EventSourceResponse


class StreamingRAG:
    """
    Handles streaming responses with real-time citations
    """
    
    def __init__(self, rag_pipeline):
        """
        Args:
            rag_pipeline: RAGPipeline instance
        """
        self.rag_pipeline = rag_pipeline
    
    async def stream_query(
        self,
        question: str,
        strategy: str = "hybrid",
        top_k: int = 5,
        temperature: float = 0.7
    ) -> AsyncGenerator[str, None]:
        """
        Stream query response with citations
        
        Yields:
            JSON strings with streaming events
        """
        try:
            # Step 1: Send "retrieving" status
            yield self._format_event("status", {
                "status": "retrieving",
                "message": "Retrieving relevant documents..."
            })
            
            await asyncio.sleep(0.1)  # Small delay for UI
            
            # Step 2: Retrieve documents
            if strategy == "hyde":
                enhanced_query = await self.rag_pipeline.query_enhancer.hyde(question)
            else:
                enhanced_query = question
            
            # Get documents based on strategy
            if strategy == "semantic":
                results = await self.rag_pipeline.searcher.semantic_search(
                    query=enhanced_query,
                    top_k=top_k
                )
            elif strategy == "bm25":
                results = await self.rag_pipeline.searcher.bm25_search(
                    query=enhanced_query,
                    top_k=top_k
                )
            elif strategy in ["hybrid", "hyde"]:
                results = await self.rag_pipeline.searcher.hybrid_search(
                    query=enhanced_query,
                    top_k=top_k
                )
            else:
                results = []
            
            # Step 3: Send sources
            sources = []
            for idx, doc in enumerate(results):
                source = {
                    "index": idx + 1,
                    "document": doc['metadata'].get('source', 'Unknown'),
                    "content": doc['content'][:200] + "..." if len(doc['content']) > 200 else doc['content'],
                    "score": doc.get('score', 0.0),
                    "page": doc['metadata'].get('page')
                }
                sources.append(source)
            
            yield self._format_event("sources", {"sources": sources})
            
            await asyncio.sleep(0.1)
            
            # Step 4: Send "generating" status
            yield self._format_event("status", {
                "status": "generating",
                "message": "Generating answer..."
            })
            
            # Build context
            context = self.rag_pipeline._build_context(results)
            
            # Step 5: Stream answer
            full_answer = ""
            async for chunk in self.rag_pipeline.generator.generate_streaming(
                question=question,
                context=context,
                temperature=temperature
            ):
                full_answer += chunk
                yield self._format_event("chunk", {"text": chunk})
            
            # Step 6: Extract and send final metadata
            citations = self.rag_pipeline.generator._extract_citations(full_answer)
            
            yield self._format_event("complete", {
                "answer": full_answer,
                "citations": citations,
                "metadata": {
                    "strategy": strategy,
                    "num_sources": len(sources),
                    "timestamp": datetime.now().isoformat()
                }
            })
            
        except Exception as e:
            yield self._format_event("error", {
                "error": str(e),
                "message": "An error occurred during processing"
            })
    
    def _format_event(self, event_type: str, data: Dict[str, Any]) -> str:
        """Format SSE event"""
        return json.dumps({
            "type": event_type,
            "data": data,
            "timestamp": datetime.now().isoformat()
        })
    
    async def create_sse_response(
        self,
        question: str,
        strategy: str = "hybrid",
        top_k: int = 5,
        temperature: float = 0.7
    ) -> EventSourceResponse:
        """
        Create Server-Sent Events response
        
        Args:
            question: User question
            strategy: Retrieval strategy
            top_k: Number of documents
            temperature: LLM temperature
            
        Returns:
            EventSourceResponse for FastAPI
        """
        async def event_generator():
            async for event in self.stream_query(
                question=question,
                strategy=strategy,
                top_k=top_k,
                temperature=temperature
            ):
                yield {
                    "event": "message",
                    "data": event
                }
        
        return EventSourceResponse(event_generator())


class StreamingFormatter:
    """
    Utility for formatting streaming responses with citations
    """
    
    @staticmethod
    def highlight_citations(text: str, sources: list) -> str:
        """
        Convert citation markers to HTML with tooltips
        
        Args:
            text: Text with [N] citations
            sources: List of source documents
            
        Returns:
            HTML formatted text with clickable citations
        """
        import re
        
        def replace_citation(match):
            num = int(match.group(1))
            if num <= len(sources):
                source = sources[num - 1]
                doc_name = source.get('document', 'Unknown')
                content_preview = source.get('content', '')[:100]
                
                return f'<span class="citation" data-source="{num}" title="{doc_name}: {content_preview}">[{num}]</span>'
            return match.group(0)
        
        return re.sub(r'\[(\d+)\]', replace_citation, text)
    
    @staticmethod
    def format_source_card(source: Dict[str, Any], index: int) -> Dict[str, Any]:
        """
        Format source for frontend display
        
        Args:
            source: Source document
            index: Source index (1-based)
            
        Returns:
            Formatted source card data
        """
        return {
            "id": index,
            "title": source['metadata'].get('source', f'Source {index}'),
            "content": source['content'][:300] + "..." if len(source['content']) > 300 else source['content'],
            "score": round(source.get('score', 0.0), 3),
            "page": source['metadata'].get('page'),
            "highlighted": False
        }
