from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from chatbot.graph import chatbot_router
from memory.memory_client import memory_router
from listeners.file_ingestors import file_router
from listeners.meeting_bot import meeting_router

app=FastAPI()

@app.get('/')
def root():
    return {
        "name": "Wisdom API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
    }

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"], 
    expose_headers=["Content-Type"], 
)

app.include_router(memory_router)
app.include_router(chatbot_router)
app.include_router(file_router)
app.include_router(meeting_router)
