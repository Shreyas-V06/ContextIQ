from typing import Annotated, TypedDict
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage

class State(TypedDict):
    """Conversation state passed between nodes"""
    messages: Annotated[list[BaseMessage], add_messages] 
    thread_id: str                                        


