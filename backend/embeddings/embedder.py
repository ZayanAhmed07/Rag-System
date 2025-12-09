"""
Embedding Model - Generates embeddings using HuggingFace models
"""

from typing import List, Union
import numpy as np


class EmbeddingModel:
    """
    Wrapper for sentence transformers embedding models
    """
    
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """
        Initialize embedding model
        
        Args:
            model_name: HuggingFace model name
        """
        self.model_name = model_name
        self.model = None
        self._initialize_model()
    
    def _initialize_model(self):
        """Load the embedding model"""
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(self.model_name)
            print(f"✅ Loaded embedding model: {self.model_name}")
        except ImportError:
            print("⚠️  sentence-transformers not installed. Run: pip install sentence-transformers")
        except Exception as e:
            print(f"⚠️  Failed to load embedding model: {e}")
    
    async def embed_query(self, text: str) -> List[float]:
        """
        Generate embedding for a query
        
        Args:
            text: Query text
            
        Returns:
            Embedding vector
        """
        if not self.model:
            raise ValueError("Embedding model not initialized")
        
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.tolist()
    
    async def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple documents
        
        Args:
            texts: List of document texts
            
        Returns:
            List of embedding vectors
        """
        if not self.model:
            raise ValueError("Embedding model not initialized")
        
        embeddings = self.model.encode(texts, convert_to_numpy=True, show_progress_bar=True)
        return embeddings.tolist()
    
    def embed_query_sync(self, text: str) -> List[float]:
        """Synchronous version of embed_query"""
        if not self.model:
            raise ValueError("Embedding model not initialized")
        
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.tolist()
    
    def get_embedding_dimension(self) -> int:
        """Get the dimension of embeddings"""
        if not self.model:
            return 384  # Default for all-MiniLM-L6-v2
        return self.model.get_sentence_embedding_dimension()
