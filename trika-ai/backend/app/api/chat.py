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

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
import openai
import os

from ..core.config import get_settings
settings = get_settings()

@router.post("/voice")
async def transcribe_voice(file: UploadFile = File(...)):
    """Transcribe audio using OpenAI Whisper."""
    try:
        # Save temp file
        temp_path = f"temp_{uuid.uuid4()}.wav"
        with open(temp_path, "wb") as buffer:
            buffer.write(await file.read())
        
        # Transcribe
        client = openai.OpenAI(api_key=settings.openai_api_key)
        with open(temp_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
        
        # Cleanup
        os.remove(temp_path)
        return {"text": transcript.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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
    
    # Simple token estimation
    user_tokens = len(request.message) // 4
    
    # Save user message
    user_msg = Message(
        conversation_id=conversation_id,
        role="user",
        content=request.message,
        tokens=user_tokens
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
            try:
                rag_result = await rag_engine.query(request.message)
                if rag_result["documents"]:
                    context = "\n\n".join(rag_result["documents"])
                    sources = rag_result["sources"]
                    # Send sources
                    yield f"data: {json.dumps({'type': 'sources', 'content': sources})}\n\n"
            except Exception:
                pass
        
        # Stream LLM response
        full_response = ""
        try:
            async for chunk in orchestrator.stream_response(
                message=request.message,
                context=context,
                history=history_dicts[:-1]
            ):
                full_response += chunk
                yield f"data: {json.dumps({'type': 'content', 'content': chunk})}\n\n"
        except Exception:
            # Simple fallback for errors
            full_response = "I encountered an error processing your request."
            yield f"data: {json.dumps({'type': 'content', 'content': full_response})}\n\n"
        
        # Save assistant message with token analytics
        asst_tokens = len(full_response) // 4
        asst_msg = Message(
            conversation_id=conversation_id,
            role="assistant",
            content=full_response,
            tokens=asst_tokens
        )
        db.add(asst_msg)
        db.commit()
        
        # Send done signal
        yield f"data: {json.dumps({'type': 'done', 'conversation_id': conversation_id})}\n\n"
        
    except Exception as e:
        yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"


@router.get("/analytics")
async def get_analytics(db: Session = Depends(get_db)):
    """Get usage analytics."""
    messages = db.query(Message).all()
    total_tokens = sum(m.tokens or 0 for m in messages)
    total_chats = db.query(Conversation).count()
    return {
        "total_tokens": total_tokens,
        "total_chats": total_chats,
        "cost_estimate": (total_tokens / 1000) * 0.01 # Mock cost
    }


@router.get("/conversations")
async def list_conversations(db: Session = Depends(get_db)):
    """List all conversations."""
    conversations = db.query(Conversation).order_by(Conversation.created_at.desc()).all()
    return [{"id": c.id, "title": c.title, "created_at": c.created_at} for c in conversations]


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
    return {"message": "Streaming only supported for now"}


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
        # Cascade delete is handled by relationship usually, but let's be safe
        db.query(Message).filter(Message.conversation_id == conversation_id).delete()
        db.delete(db_conv)
        db.commit()
    return {"status": "deleted"}

