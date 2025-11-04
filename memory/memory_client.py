import os
import asyncio
from dotenv import load_dotenv
from mem0 import Memory
from initializers.initialize_db import initialize_db
from fastapi import APIRouter
from initializers.initialize_db import initialize_db

load_dotenv()

#CONFIGURATION FOR MEM0
collection_name = "wisdom_v1_test" 
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

memory_router=APIRouter()
#WRAPPER FUNCTIONS FOR CRUD
async def add_single_memory(context: str, user_id: str) -> dict:
    messages = [{"role": "user", "content": context}]
    result = await asyncio.to_thread(
        memory.add, 
        messages, 
        user_id=user_id,
        infer=False
    )
    db=initialize_db()
    client=db.wisdom
    for mem in result['results']:
        client.memories.insert_one(mem)
    return {"status": "success", "message": result}

async def add_interaction_memory(user_message: str, ai_response: str, user_id: str , prompt:str=None) -> dict:
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
    db=initialize_db()
    client=db.wisdom
    for mem in result['results']:
        client.memories.insert_one(mem)
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

def search_memory_sync(query: str) -> str:
    mems = memory.search(
        query, 
        user_id="central-memories",
        limit=15

    )
    if mems.get("results"):
        context = "\n".join(f"- {m['memory']}" for m in mems["results"])
    else:
        context = "No relevant information found."
    return context


def add_interaction_memory_sync(user_message: str, ai_response: str, user_id: str , prompt:str=None) -> dict:
    messages = [
        {"role": "user", "content": user_message},
        {"role": "assistant", "content": ai_response}
    ]
    result = memory.add(
        messages, 
        user_id=user_id,
        prompt=prompt
    )
    db=initialize_db()
    client=db.wisdom
    for memory in result['results']:
        client.memories.insert_one(memory)
    return {"status": "success", "message": result}

@memory_router.post('/api/memory/add')
async def add_memory(context:str,user_id:str):
    return await add_single_memory(context=context,user_id=user_id)

@memory_router.put('/api/memory/edit')
def edit_memory(memory_id:str,new_memory:str):
    updates={
        "$set":{"memory":new_memory}
    }
    db=initialize_db()
    client=db.wisdom
    client.memories.update_one({"id":memory_id},update=updates)
    memory.update(memory_id=memory_id,data=new_memory)
    return {"status":"success","event":"edit"}

@memory_router.delete('/api/memory/delete')
def delete_memory(memory_id):
    db=initialize_db()
    client=db.wisdom
    client.memories.delete_one({"id":memory_id})
    memory.delete(memory_id=memory_id)
    return {"status":"success","event":"delete"}

@memory_router.get('/api/memory')
def get_all_memories():
    db = initialize_db()
    client = db.wisdom
    memories = client.memories.find({}) 
    all_memories = []
    for mem in memories:
        mem['_id'] = str(mem['_id'])
        all_memories.append(mem)
    return {"status": "success", "event": "get_all", "memories": all_memories}