from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Dict, Any
from langchain_core.messages import HumanMessage, AIMessage
from services.graph import app as graph_app
import json
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    metadata: Dict[str, Any]

@router.post("/chat")
async def chat_stream(request: ChatRequest):
    # Convert incoming messages to LangChain message types
    langchain_messages = []
    for msg in request.messages:
        if msg.role == "user":
            langchain_messages.append(HumanMessage(content=msg.content))
        elif msg.role == "assistant":
            langchain_messages.append(AIMessage(content=msg.content))
            
    initial_state = {
        "messages": langchain_messages,
        "video_a_context": [],
        "video_b_context": [],
        "metadata": request.metadata
    }
    
    async def generate_sse():
        try:
            # Using astream_events to get the streaming tokens from the LLM
            async for event in graph_app.astream_events(initial_state, version="v2"):
                if event["event"] == "on_chat_model_stream":
                    chunk = event["data"]["chunk"].content
                    if chunk:
                        yield f"data: {json.dumps({'content': chunk})}\n\n"
        except Exception as e:
            logger.error(f"Error in chat stream: {e}")
            error_msg = "⚠️ AI Analysis failed. This is usually due to an invalid OpenAI/Groq API key in the .env file."
            if "AuthenticationError" in str(e) or "401" in str(e):
                error_msg = "⚠️ Authentication Error: Your OpenAI/Groq API key is invalid or has expired."
            yield f"data: {json.dumps({'content': error_msg})}\n\n"
                    
        yield "data: [DONE]\n\n"
        
    return StreamingResponse(generate_sse(), media_type="text/event-stream")
