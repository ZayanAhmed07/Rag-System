#!/usr/bin/env python
"""Test Qdrant connection"""

from qdrant_client import QdrantClient

# Initialize Qdrant client
qdrant_client = QdrantClient(
    url="https://6e8f4d12-8c7a-411b-93e3-1d6826a4ecd6.us-west-1-0.aws.cloud.qdrant.io:6333", 
    api_key="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.-DEoLNUz70wt99SQavDAUX3AZrqzBv2PZzvWbauiyJw",
)

# Test connection
try:
    collections = qdrant_client.get_collections()
    print("✅ Connected to Qdrant successfully!")
    if collections.collections:
        print(f"📦 Collections found: {len(collections.collections)}")
        for col in collections.collections:
            print(f"  - {col.name}")
    else:
        print("📦 No collections yet (empty vector store)")
except Exception as e:
    print(f"❌ Connection failed: {e}")
