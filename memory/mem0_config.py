from mem0 import Memory
from memory.qdrant_client import *

config = {
    "vector_store": {
        "provider": "qdrant",
        "config": {
            "collection_name": collection_name,
            "url": "https://60ef5bf6-1994-4134-a1b7-f64738daac50.europe-west3-0.gcp.cloud.qdrant.io:6333",
            "api_key": qdrant_api_key,
        },
    },
    "llm": {
        "provider": "gemini",
        "config": {"model": "gemini-2.0-flash", "temperature": 0.1},
    },
    "embedder": {
        "provider": "gemini",
        "config": {"model": "gemini-embedding-001","embedding_dims":1536},
    },
}



