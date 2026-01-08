"""Chat API endpoints with streaming support."""
import json
import uuid
from typing import AsyncGenerator

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from ..db.database import get_db
from ..db.models import Conversation, Message
from ..models.chat import ChatRequest, ChatResponse, ChatMessage, MessageRole, StreamChunk
from ..engine.rag import RAGEngine
from ..engine.agents import AgentOrchestrator

router = APIRouter(prefix="/chat", tags=["chat"])

async def generate_stream(
    request: ChatRequest, 
    rag_engine: RAGEngine,
    orchestrator: AgentOrchestrator,
    db: Session
) -> AsyncGenerator[str, None]:
    """Generate streaming response."""
    conversation_id = request.conversation_id or str(uuid.uuid4())
    
    # Initialize conversation if new
    db_conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not db_conv:
        db_conv = Conversation(id=conversation_id, title=request.message[:50])
        db.add(db_conv)
        db.commit()
    
    # Save user message
    user_msg = Message(
        conversation_id=conversation_id,
        role="user",
        content=request.message
    )
    db.add(user_msg)
    db.commit()
    
    # Get history for context
    history_msgs = db.query(Message).filter(
        Message.conversation_id == conversation_id
    ).order_by(Message.created_at).all()
    
    history_dicts = [{"role": m.role, "content": m.content} for m in history_msgs]
    
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
            history=history_dicts[:-1] # Exclude current message as it's added by orchestrator? 
            # Note: Orchestrator likely appends the current message itself, let's check agent.py logic.
            # AgentOrchestrator.stream_response appends the message passed in `message` arg.
            # So history should NOT include the current message.
        ):
            full_response += chunk
            yield f"data: {json.dumps({'type': 'content', 'content': chunk})}\n\n"
        
        # Save assistant message
        asst_msg = Message(
            conversation_id=conversation_id,
            role="assistant",
            content=full_response
        )
        db.add(asst_msg)
        db.commit()
        
        # Send done signal
        yield f"data: {json.dumps({'type': 'done', 'conversation_id': conversation_id})}\n\n"
        
    except Exception as e:
        yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"


@router.post("/")
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    """Send a chat message and get streaming response."""
    rag_engine = RAGEngine()
    orchestrator = AgentOrchestrator(model_name=request.model)
    
    if request.stream:
        return StreamingResponse(
            generate_stream(request, rag_engine, orchestrator, db),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            }
        )
    else:
        # Non-streaming response not fully implemented with DB yet for brevity
        pass


@router.get("/conversations/{conversation_id}")
async def get_conversation(conversation_id: str, db: Session = Depends(get_db)):
    """Get conversation history."""
    db_conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not db_conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
        
    messages = db.query(Message).filter(
        Message.conversation_id == conversation_id
    ).order_by(Message.created_at).all()
    
    return {
        "conversation_id": conversation_id, 
        "messages": [{"role": m.role, "content": m.content, "timestamp": m.created_at} for m in messages]
    }


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str, db: Session = Depends(get_db)):
    """Delete a conversation."""
    db_conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if db_conv:
        db.delete(db_conv)
        db.commit()
    return {"status": "deleted"}
