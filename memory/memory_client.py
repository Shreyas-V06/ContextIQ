from memory.qdrant_client import *
from memory.mem0_config import *

memory = Memory.from_config(config)

def add_single_memory(memory:str,user_id:str) -> dict:
    messages = [ {"role": "user", "content": memory} ]
    result=memory.add(messages, user_id=user_id)
    return {"status":"success","message":result}


def add_interaction_memory(user_message:str,ai_response:str,user_id:str) -> dict:
    messages = [ {"role": "user", "content": user_message} , {"role": "assistant", "content": ai_response}]
    result=memory.add(messages, user_id=user_id)
    return {"status":"success","message":result}


def search_memory(message: str, user_id: str) -> str:   
    mems = memory.search(message, user_id=user_id)
    if mems.get("results"):
        context = "\n".join(f"- {m['memory']}" for m in mems["results"])
    else:
        context = "No relevant information found."
    return context

