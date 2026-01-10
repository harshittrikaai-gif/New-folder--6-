"""Workflow API endpoints."""
from typing import List, Dict, Any
from datetime import datetime
import uuid

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from sqlalchemy.orm import Session

from ..db.database import get_db
from ..db.models import Workflow as WorkflowDB, WorkflowExecution as ExecutionDB
from ..models.workflow import (
    Workflow, WorkflowCreate, WorkflowUpdate,
    WorkflowExecution, ExecutionStatus
)
from ..workflow.executor import WorkflowExecutor

router = APIRouter(prefix="/workflows", tags=["workflows"])


def _to_workflow_model(db_workflow: WorkflowDB) -> Workflow:
    """Convert database workflow to Pydantic model."""
    return Workflow(
        id=db_workflow.id,
        name=db_workflow.name,
        description=db_workflow.description or "",
        nodes=db_workflow.nodes or [],
        edges=db_workflow.edges or [],
        variables=db_workflow.variables or {},
        created_at=db_workflow.created_at,
        updated_at=db_workflow.updated_at,
    )


def _to_execution_model(db_execution: ExecutionDB) -> WorkflowExecution:
    """Convert database execution to Pydantic model."""
    return WorkflowExecution(
        id=db_execution.id,
        workflow_id=db_execution.workflow_id,
        status=ExecutionStatus(db_execution.status),
        input_data=db_execution.input_data or {},
        output_data=db_execution.output_data or {},
        node_outputs=db_execution.node_outputs or {},
        error=db_execution.error,
        started_at=db_execution.started_at,
        completed_at=db_execution.completed_at,
    )


@router.get("/", response_model=List[Workflow])
async def list_workflows(db: Session = Depends(get_db)):
    """List all workflows."""
    workflows = db.query(WorkflowDB).all()
    return [_to_workflow_model(w) for w in workflows]


@router.post("/", response_model=Workflow)
async def create_workflow(
    request: WorkflowCreate,
    db: Session = Depends(get_db)
):
    """Create a new workflow."""
    workflow_id = str(uuid.uuid4())
    
    db_workflow = WorkflowDB(
        id=workflow_id,
        name=request.name,
        description=request.description,
        nodes=[],
        edges=[],
        variables={},
    )
    
    db.add(db_workflow)
    db.commit()
    db.refresh(db_workflow)
    
    return _to_workflow_model(db_workflow)


@router.get("/{workflow_id}", response_model=Workflow)
async def get_workflow(
    workflow_id: str,
    db: Session = Depends(get_db)
):
    """Get a workflow by ID."""
    db_workflow = db.query(WorkflowDB).filter(WorkflowDB.id == workflow_id).first()
    
    if not db_workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    return _to_workflow_model(db_workflow)


@router.put("/{workflow_id}", response_model=Workflow)
async def update_workflow(
    workflow_id: str,
    request: WorkflowUpdate,
    db: Session = Depends(get_db)
):
    """Update a workflow."""
    db_workflow = db.query(WorkflowDB).filter(WorkflowDB.id == workflow_id).first()
    
    if not db_workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    # Update fields
    if request.name is not None:
        db_workflow.name = request.name
    if request.description is not None:
        db_workflow.description = request.description
    if request.nodes is not None:
        db_workflow.nodes = [n.model_dump() for n in request.nodes]
    if request.edges is not None:
        db_workflow.edges = [e.model_dump() for e in request.edges]
    if request.variables is not None:
        db_workflow.variables = request.variables
    
    db_workflow.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(db_workflow)
    
    return _to_workflow_model(db_workflow)


@router.delete("/{workflow_id}")
async def delete_workflow(
    workflow_id: str,
    db: Session = Depends(get_db)
):
    """Delete a workflow."""
    db_workflow = db.query(WorkflowDB).filter(WorkflowDB.id == workflow_id).first()
    
    if not db_workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    db.delete(db_workflow)
    db.commit()
    
    return {"status": "deleted"}


@router.post("/{workflow_id}/execute", response_model=WorkflowExecution)
async def execute_workflow(
    workflow_id: str,
    input_data: Dict[str, Any],
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Execute a workflow."""
    db_workflow = db.query(WorkflowDB).filter(WorkflowDB.id == workflow_id).first()
    
    if not db_workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    execution_id = str(uuid.uuid4())
    
    db_execution = ExecutionDB(
        id=execution_id,
        workflow_id=workflow_id,
        status="pending",
        input_data=input_data,
        output_data={},
        node_outputs={},
    )
    
    db.add(db_execution)
    db.commit()
    db.refresh(db_execution)
    
    # Run execution in background
    background_tasks.add_task(run_workflow, execution_id, db_workflow, db)
    
    return _to_execution_model(db_execution)


async def run_workflow(
    execution_id: str,
    db_workflow: WorkflowDB,
    db: Session
):
    """Background task to run workflow."""
    execution = db.query(ExecutionDB).filter(ExecutionDB.id == execution_id).first()
    
    if not execution:
        return
    
    execution.status = "running"
    execution.started_at = datetime.utcnow()
    db.commit()
    
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
        result = await executor.execute(workflow, execution.input_data)
        
        execution.output_data = result.get("output", {})
        execution.node_outputs = result.get("node_outputs", {})
        execution.status = "completed"
    except Exception as e:
        execution.status = "failed"
        execution.error = str(e)
        print(f"Workflow execution error: {e}")
    finally:
        execution.completed_at = datetime.utcnow()
        db.commit()


@router.get("/{workflow_id}/executions", response_model=List[WorkflowExecution])
async def list_executions(
    workflow_id: str,
    db: Session = Depends(get_db)
):
    """List executions for a workflow."""
    db_workflow = db.query(WorkflowDB).filter(WorkflowDB.id == workflow_id).first()
    
    if not db_workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    executions = db.query(ExecutionDB).filter(
        ExecutionDB.workflow_id == workflow_id
    ).order_by(ExecutionDB.created_at.desc()).all()
    
    return [_to_execution_model(e) for e in executions]


@router.get("/executions/{execution_id}", response_model=WorkflowExecution)
async def get_execution(
    execution_id: str,
    db: Session = Depends(get_db)
):
    """Get execution status."""
    db_execution = db.query(ExecutionDB).filter(ExecutionDB.id == execution_id).first()
    
    if not db_execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    
    return _to_execution_model(db_execution)
