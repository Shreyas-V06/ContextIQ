from langgraph.graph import StateGraph,START,END
from langgraph.checkpoint.memory import MemorySaver
from schemas import State
from langchain_core.messages import HumanMessage,SystemMessage
from initializers.initialize_llm  import initialize_chat_llm
from memory.memory_client import add_interaction_memory_sync,search_memory_sync
from prompts.rag import get_rag_prompt
from fastapi import APIRouter

chatbot_router = APIRouter()
memory = MemorySaver()

@chatbot_router.get("/api/chat")
def send_message(thread_id:str,user_message:str):
    config = {"configurable": {
    "thread_id": thread_id
    }}
    state={
        "messages":[HumanMessage(content=user_message)],
        "thread_id":thread_id
    }
    result=graph.invoke(state,config=config)
    return result["messages"][-1].content


def chatbot(state: State):
    msgs = state["messages"]
    uid = state["thread_id"]
    context=None
    context = search_memory_sync(query=msgs[-1].content)
    system = SystemMessage(content=get_rag_prompt(query=msgs[-1].content,context=context))
    llm=initialize_chat_llm()
    response = llm.invoke([system] + msgs)
    success=add_interaction_memory_sync(user_message=msgs[-1].content,ai_response=response.content,user_id="chatbot-memories")
    return {"messages": [response]}


graph_builder = StateGraph(State)
graph_builder.add_node("chatbot", chatbot)
graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", END)
graph = graph_builder.compile(checkpointer=memory)





