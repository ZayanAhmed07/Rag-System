"""
Text Chunking - Split documents into chunks for embedding
"""

from typing import List, Dict, Any
import re


class TextChunker:
    """
    Chunk text documents with overlap
    """
    
    def __init__(self, chunk_size: int = 500, overlap: int = 50):
        """
        Initialize chunker
        
        Args:
            chunk_size: Target chunk size in characters
            overlap: Overlap between chunks
        """
        self.chunk_size = chunk_size
        self.overlap = overlap
    
    def chunk_text(self, text: str, metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Chunk text into overlapping segments
        
        Args:
            text: Text to chunk
            metadata: Metadata to attach to each chunk
            
        Returns:
            List of chunks with metadata
        """
        if not text or not text.strip():
            return []
        
        # Split by paragraphs first
        paragraphs = self._split_paragraphs(text)
        
        chunks = []
        current_chunk = ""
        chunk_index = 0
        
        for para in paragraphs:
            # If paragraph is too long, split it
            if len(para) > self.chunk_size:
                # Save current chunk if exists
                if current_chunk:
                    chunks.append(self._create_chunk(current_chunk, chunk_index, metadata))
                    chunk_index += 1
                    current_chunk = ""
                
                # Split long paragraph
                sub_chunks = self._split_long_text(para)
                for sub_chunk in sub_chunks:
                    chunks.append(self._create_chunk(sub_chunk, chunk_index, metadata))
                    chunk_index += 1
            
            # Add paragraph to current chunk
            elif len(current_chunk) + len(para) <= self.chunk_size:
                current_chunk += "\n\n" + para if current_chunk else para
            
            # Start new chunk
            else:
                if current_chunk:
                    chunks.append(self._create_chunk(current_chunk, chunk_index, metadata))
                    chunk_index += 1
                    
                    # Add overlap
                    overlap_text = current_chunk[-self.overlap:] if len(current_chunk) > self.overlap else current_chunk
                    current_chunk = overlap_text + "\n\n" + para
                else:
                    current_chunk = para
        
        # Add final chunk
        if current_chunk:
            chunks.append(self._create_chunk(current_chunk, chunk_index, metadata))
        
        return chunks
    
    def _split_paragraphs(self, text: str) -> List[str]:
        """Split text into paragraphs"""
        # Split by double newlines or more
        paragraphs = re.split(r'\n\s*\n', text)
        return [p.strip() for p in paragraphs if p.strip()]
    
    def _split_long_text(self, text: str) -> List[str]:
        """Split long text by sentences"""
        # Split by sentence boundaries
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        chunks = []
        current = ""
        
        for sentence in sentences:
            if len(current) + len(sentence) <= self.chunk_size:
                current += " " + sentence if current else sentence
            else:
                if current:
                    chunks.append(current)
                current = sentence
        
        if current:
            chunks.append(current)
        
        return chunks
    
    def _create_chunk(self, text: str, index: int, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create chunk with metadata"""
        chunk_metadata = metadata.copy() if metadata else {}
        chunk_metadata["chunk_index"] = index
        chunk_metadata["chunk_length"] = len(text)
        
        return {
            "content": text.strip(),
            "metadata": chunk_metadata
        }
