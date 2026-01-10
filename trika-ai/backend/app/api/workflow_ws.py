"""WebSocket support for real-time workflow execution monitoring."""
import json
import logging
from typing import Set, Dict, Any
from datetime import datetime

from fastapi import WebSocket, WebSocketDisconnect, APIRouter
from sqlalchemy.orm import Session

from ..db.database import get_db
from ..db.models import WorkflowExecution as ExecutionDB, Workflow as WorkflowDB
from ..models.workflow import Workflow, WorkflowExecution
from ..workflow.executor import WorkflowExecutor

logger = logging.getLogger(__name__)

router = APIRouter(tags=["workflows"])

# Store active WebSocket connections
active_connections: Dict[str, Set[WebSocket]] = {}


class ConnectionManager:
    """Manage WebSocket connections for workflow execution."""
    
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}
    
    async def connect(self, execution_id: str, websocket: WebSocket):
        """Accept new WebSocket connection."""
        await websocket.accept()
        if execution_id not in self.active_connections:
            self.active_connections[execution_id] = set()
        self.active_connections[execution_id].add(websocket)
    
    def disconnect(self, execution_id: str, websocket: WebSocket):
        """Remove WebSocket connection."""
        if execution_id in self.active_connections:
            self.active_connections[execution_id].discard(websocket)
            if not self.active_connections[execution_id]:
                del self.active_connections[execution_id]
    
    async def broadcast(self, execution_id: str, message: Dict[str, Any]):
        """Broadcast message to all connected clients for this execution."""
        if execution_id not in self.active_connections:
            return
        
        disconnected = set()
        for connection in self.active_connections[execution_id]:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to client: {e}")
                disconnected.add(connection)
        
        # Clean up disconnected clients
        for connection in disconnected:
            self.disconnect(execution_id, connection)


manager = ConnectionManager()


@router.websocket("/ws/workflows/{execution_id}")
async def websocket_endpoint(execution_id: str, websocket: WebSocket):
    """WebSocket endpoint for workflow execution monitoring."""
    await manager.connect(execution_id, websocket)
    
    try:
        while True:
            # Keep connection open and listen for client messages
            data = await websocket.receive_text()
            
            # Process client messages (e.g., pause, cancel)
            try:
                message = json.loads(data)
                action = message.get("action")
                
                if action == "ping":
                    await websocket.send_json({"type": "pong"})
                elif action == "cancel":
                    logger.info(f"Cancel requested for execution {execution_id}")
                    # TODO: Implement cancellation logic
                    
            except json.JSONDecodeError:
                await websocket.send_json({"error": "Invalid JSON"})
    
    except WebSocketDisconnect:
        manager.disconnect(execution_id, websocket)
        logger.info(f"Client disconnected from execution {execution_id}")


async def broadcast_execution_update(
    execution_id: str,
    update_type: str,
    data: Dict[str, Any]
):
    """Broadcast execution update to all connected clients."""
    message = {
        "type": update_type,
        "timestamp": datetime.utcnow().isoformat(),
        **data
    }
    await manager.broadcast(execution_id, message)


async def run_workflow_with_streaming(
    execution_id: str,
    db_workflow: WorkflowDB,
    input_data: Dict[str, Any],
    db: Session
):
    """Run workflow with real-time streaming updates."""
    execution = db.query(ExecutionDB).filter(ExecutionDB.id == execution_id).first()
    
    if not execution:
        return
    
    execution.status = "running"
    execution.started_at = datetime.utcnow()
    db.commit()
    
    # Notify clients of start
    await broadcast_execution_update(
        execution_id,
        "start",
        {"workflow_id": db_workflow.id, "workflow_name": db_workflow.name}
    )
    
    try:
        # Convert database workflow to Pydantic model
        workflow = Workflow(
            id=db_workflow.id,
            name=db_workflow.name,
            description=db_workflow.description or "",
            nodes=db_workflow.nodes or [],
            edges=db_workflow.edges or [],
            variables=db_workflow.variables or {},
            created_at=db_workflow.created_at,
            updated_at=db_workflow.updated_at,
        )
        
        executor = WorkflowExecutor()
        
        # Execute with node progress updates
        result = await executor.execute_with_progress(
            workflow,
            input_data,
            callback=lambda node_id, output: broadcast_execution_update(
                execution_id,
                "node_completed",
                {"node_id": node_id, "output": output}
            )
        )
        
        execution.output_data = result.get("output", {})
        execution.node_outputs = result.get("node_outputs", {})
        execution.status = "completed"
        
        # Notify clients of completion
        await broadcast_execution_update(
            execution_id,
            "completed",
            {
                "output": execution.output_data,
                "node_outputs": execution.node_outputs
            }
        )
    
    except Exception as e:
        execution.status = "failed"
        execution.error = str(e)
        logger.error(f"Workflow execution error: {e}")
        
        # Notify clients of failure
        await broadcast_execution_update(
            execution_id,
            "failed",
            {"error": str(e)}
        )
    
    finally:
        execution.completed_at = datetime.utcnow()
        db.commit()
