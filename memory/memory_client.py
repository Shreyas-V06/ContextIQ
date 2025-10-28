import os
import asyncio
from dotenv import load_dotenv
from mem0 import Memory

load_dotenv()

#CONFIGURATION FOR MEM0
collection_name = "contextiq_v2.0" 
qdrant_api_key = os.getenv('QDRANT_API_KEY')
reranker_api_key=os.getenv('COHERE_API_KEY')
qdrant_url = "https://60ef5bf6-1994-4134-a1b7-f64738daac50.europe-west3-0.gcp.cloud.qdrant.io:6333"


config = {
    "vector_store": {
        "provider": "qdrant",
        "config": {
            "collection_name": collection_name,
            "url": qdrant_url,
            "api_key": qdrant_api_key,
        },
    },
    "llm": {
        "provider": "gemini",
        "config": {"model": "gemini-2.0-flash", "temperature": 0.1},
    },
    "embedder": {
        "provider": "gemini",
        "config": {"model": "gemini-embedding-001", "embedding_dims": 1536},
    },
    "reranker": {
        "provider": "cohere",
        "config": {
            "model": "rerank-english-v3.0",
            "api_key": reranker_api_key
        }
    }
}


memory = Memory.from_config(config)

#WRAPPER FUNCTIONS FOR CRUD
async def add_single_memory(context: str, user_id: str,prompt:str) -> dict:
    messages = [{"role": "user", "content": context}]
    result = await asyncio.to_thread(
        memory.add, 
        messages, 
        user_id=user_id,
        prompt=prompt,
        infer=False
    )
    return {"status": "success", "message": result}


async def add_interaction_memory(user_message: str, ai_response: str, user_id: str , prompt:str) -> dict:
    messages = [
        {"role": "user", "content": user_message},
        {"role": "assistant", "content": ai_response}
    ]
    result = await asyncio.to_thread(
        memory.add, 
        messages, 
        user_id=user_id,
        prompt=prompt
    )
    return {"status": "success", "message": result}



async def search_memory(query: str, user_id: str) -> str:
    mems = await asyncio.to_thread(
        memory.search, 
        query, 
        user_id=user_id,
        limit=15
    )
    if mems.get("results"):
        context = "\n".join(f"- {m['memory']}" for m in mems["results"])
    else:
        context = "No relevant information found."
    return context

