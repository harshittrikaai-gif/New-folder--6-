"""Chat message Pydantic models."""
from datetime import datetime
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field


class MessageRole(str, Enum):
    """Chat message roles."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class FileAttachment(BaseModel):
    """File attachment for multimodal chat."""
    filename: str
    content_type: str
    size: int
    url: Optional[str] = None


class ChatMessage(BaseModel):
    """Single chat message."""
    id: str = Field(default_factory=lambda: "")
    role: MessageRole
    content: str
    attachments: List[FileAttachment] = []
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: dict = {}


class ChatRequest(BaseModel):
    """Chat request from client."""
    message: str
    conversation_id: Optional[str] = None
    attachments: List[FileAttachment] = []
    stream: bool = True


class ChatResponse(BaseModel):
    """Chat response to client."""
    id: str
    conversation_id: str
    message: ChatMessage
    sources: List[dict] = []  # RAG sources


class StreamChunk(BaseModel):
    """Streaming response chunk."""
    type: str = "content"  # content, source, done, error
    content: Optional[str] = None
    metadata: dict = {}
