"""Chat API endpoints with streaming support."""
import json
import uuid
from typing import AsyncGenerator

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from ..models.chat import ChatRequest, ChatResponse, ChatMessage, MessageRole, StreamChunk
from ..engine.rag import RAGEngine
from ..engine.agents import AgentOrchestrator

router = APIRouter(prefix="/chat", tags=["chat"])

# In-memory conversation store (replace with database in production)
conversations: dict = {}


async def generate_stream(
    request: ChatRequest, 
    rag_engine: RAGEngine,
    orchestrator: AgentOrchestrator
) -> AsyncGenerator[str, None]:
    """Generate streaming response."""
    conversation_id = request.conversation_id or str(uuid.uuid4())
    
    # Initialize conversation if new
    if conversation_id not in conversations:
        conversations[conversation_id] = []
    
    # Add user message
    conversations[conversation_id].append({
        "role": "user",
        "content": request.message
    })
    
    try:
        # Get RAG context if documents exist
        context = ""
        sources = []
        if request.message:
            rag_result = await rag_engine.query(request.message)
            if rag_result["documents"]:
                context = "\n\n".join(rag_result["documents"])
                sources = rag_result["sources"]
                # Send sources
                yield f"data: {json.dumps({'type': 'sources', 'content': sources})}\n\n"
        
        # Stream LLM response
        full_response = ""
        async for chunk in orchestrator.stream_response(
            message=request.message,
            context=context,
            history=conversations[conversation_id]
        ):
            full_response += chunk
            yield f"data: {json.dumps({'type': 'content', 'content': chunk})}\n\n"
        
        # Save assistant message
        conversations[conversation_id].append({
            "role": "assistant",
            "content": full_response
        })
        
        # Send done signal
        yield f"data: {json.dumps({'type': 'done', 'conversation_id': conversation_id})}\n\n"
        
    except Exception as e:
        yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"


@router.post("/")
async def chat(request: ChatRequest):
    """Send a chat message and get streaming response."""
    rag_engine = RAGEngine()
    orchestrator = AgentOrchestrator(model_name=request.model)
    
    if request.stream:
        return StreamingResponse(
            generate_stream(request, rag_engine, orchestrator),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            }
        )
    else:
        # Non-streaming response
        conversation_id = request.conversation_id or str(uuid.uuid4())
        response = await orchestrator.generate_response(
            message=request.message,
            context="",
            history=conversations.get(conversation_id, [])
        )
        
        return ChatResponse(
            id=str(uuid.uuid4()),
            conversation_id=conversation_id,
            message=ChatMessage(
                id=str(uuid.uuid4()),
                role=MessageRole.ASSISTANT,
                content=response
            )
        )


@router.get("/conversations/{conversation_id}")
async def get_conversation(conversation_id: str):
    """Get conversation history."""
    if conversation_id not in conversations:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"conversation_id": conversation_id, "messages": conversations[conversation_id]}


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """Delete a conversation."""
    if conversation_id in conversations:
        del conversations[conversation_id]
    return {"status": "deleted"}
