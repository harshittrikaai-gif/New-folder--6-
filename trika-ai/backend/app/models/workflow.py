"""Workflow Pydantic models."""
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
import uuid


class NodeType(str, Enum):
    """Available workflow node types."""
    LLM = "llm"
    CODE = "code"
    HTTP = "http"
    CONDITION = "condition"
    LOOP = "loop"
    INPUT = "input"
    OUTPUT = "output"
    RAG = "rag"
    TRANSFORM = "transform"


class NodePosition(BaseModel):
    """Node position on canvas."""
    x: float
    y: float


class NodeConfig(BaseModel):
    """Node configuration."""
    type: NodeType
    label: str
    params: Dict[str, Any] = {}
    position: NodePosition


class WorkflowEdge(BaseModel):
    """Connection between nodes."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source: str
    target: str
    source_handle: Optional[str] = None
    target_handle: Optional[str] = None


class WorkflowNode(BaseModel):
    """Workflow node with full config."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    config: NodeConfig
    data: Dict[str, Any] = {}


class Workflow(BaseModel):
    """Complete workflow definition."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str = ""
    nodes: List[WorkflowNode] = []
    edges: List[WorkflowEdge] = []
    variables: Dict[str, Any] = {}
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class WorkflowCreate(BaseModel):
    """Request to create workflow."""
    name: str
    description: str = ""


class WorkflowUpdate(BaseModel):
    """Request to update workflow."""
    name: Optional[str] = None
    description: Optional[str] = None
    nodes: Optional[List[WorkflowNode]] = None
    edges: Optional[List[WorkflowEdge]] = None
    variables: Optional[Dict[str, Any]] = None


class ExecutionStatus(str, Enum):
    """Workflow execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class WorkflowExecution(BaseModel):
    """Workflow execution record."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    workflow_id: str
    status: ExecutionStatus = ExecutionStatus.PENDING
    input_data: Dict[str, Any] = {}
    output_data: Dict[str, Any] = {}
    node_outputs: Dict[str, Any] = {}  # Output per node
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
