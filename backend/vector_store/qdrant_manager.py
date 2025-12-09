"""
Qdrant Vector Store Manager
"""

from typing import List, Dict, Any, Optional


class QdrantManager:
    """
    Manages Qdrant vector database operations
    """
    
    def __init__(self, host: str = "localhost", port: int = 6333, api_key: Optional[str] = None):
        """
        Initialize Qdrant client
        
        Args:
            host: Qdrant host
            port: Qdrant port
            api_key: Optional API key for cloud
        """
        self.host = host
        self.port = port
        self.api_key = api_key
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Qdrant client"""
        try:
            from qdrant_client import QdrantClient
            
            if self.api_key:
                self.client = QdrantClient(url=self.host, api_key=self.api_key)
                print(f"✅ Connected to Qdrant Cloud at {self.host}")
            else:
                self.client = QdrantClient(host=self.host, port=self.port)
                print(f"✅ Connected to Qdrant at {self.host}:{self.port}")
        except ImportError:
            print("⚠️  qdrant-client not installed. Vector store unavailable.")
        except Exception as e:
            print(f"⚠️  Could not connect to Qdrant: {e}")
    
    async def search(
        self,
        collection_name: str,
        query_vector: List[float],
        limit: int = 5,
        score_threshold: float = 0.0
    ) -> List[Any]:
        """
        Search for similar vectors
        
        Args:
            collection_name: Collection name
            query_vector: Query embedding
            limit: Number of results
            score_threshold: Minimum similarity score
            
        Returns:
            List of search results
        """
        if not self.client:
            return []
        
        try:
            from qdrant_client.models import SearchRequest, SearchParams
            
            results = self.client.query_points(
                collection_name=collection_name,
                query=query_vector,
                limit=limit,
                score_threshold=score_threshold
            )
            return results.points if hasattr(results, 'points') else []
        except Exception as e:
            print(f"Search error: {e}")
            return []
    
    async def get_all_points(self, collection_name: str) -> List[Any]:
        """Get all points from collection"""
        if not self.client:
            return []
        
        try:
            result = self.client.scroll(
                collection_name=collection_name,
                limit=10000
            )
            return result[0] if result else []
        except Exception as e:
            print(f"Error getting points: {e}")
            return []
    
    async def get_point(self, collection_name: str, point_id: str) -> Any:
        """Get a specific point by ID"""
        if not self.client:
            return None
        
        try:
            return self.client.retrieve(
                collection_name=collection_name,
                ids=[point_id]
            )[0]
        except Exception as e:
            print(f"Error getting point: {e}")
            return None
    
    def ensure_collection(self, collection_name: str, vector_size: int = 384):
        """
        Ensure collection exists, create if it doesn't
        
        Args:
            collection_name: Name of the collection
            vector_size: Size of the embedding vectors
        """
        if not self.client:
            return False
        
        try:
            from qdrant_client.models import Distance, VectorParams
            
            # Check if collection exists
            try:
                self.client.get_collection(collection_name)
                return True  # Collection exists
            except:
                # Collection doesn't exist, create it
                self.client.create_collection(
                    collection_name=collection_name,
                    vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE)
                )
                print(f"✅ Created collection: {collection_name}")
                return True
        except Exception as e:
            print(f"⚠️  Error ensuring collection: {e}")
            return False
