"""Workflow API endpoints."""
from typing import List, Dict, Any
from datetime import datetime
import uuid

from fastapi import APIRouter, HTTPException, BackgroundTasks

from ..models.workflow import (
    Workflow, WorkflowCreate, WorkflowUpdate,
    WorkflowExecution, ExecutionStatus
)
from ..workflow.executor import WorkflowExecutor

router = APIRouter(prefix="/workflows", tags=["workflows"])

# In-memory storage (replace with database in production)
workflows: Dict[str, Workflow] = {}
executions: Dict[str, WorkflowExecution] = {}


@router.get("/", response_model=List[Workflow])
async def list_workflows():
    """List all workflows."""
    return list(workflows.values())


@router.post("/", response_model=Workflow)
async def create_workflow(request: WorkflowCreate):
    """Create a new workflow."""
    workflow = Workflow(
        id=str(uuid.uuid4()),
        name=request.name,
        description=request.description
    )
    workflows[workflow.id] = workflow
    return workflow


@router.get("/{workflow_id}", response_model=Workflow)
async def get_workflow(workflow_id: str):
    """Get a workflow by ID."""
    if workflow_id not in workflows:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return workflows[workflow_id]


@router.put("/{workflow_id}", response_model=Workflow)
async def update_workflow(workflow_id: str, request: WorkflowUpdate):
    """Update a workflow."""
    if workflow_id not in workflows:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    workflow = workflows[workflow_id]
    update_data = request.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(workflow, field, value)
    
    workflow.updated_at = datetime.utcnow()
    workflows[workflow_id] = workflow
    return workflow


@router.delete("/{workflow_id}")
async def delete_workflow(workflow_id: str):
    """Delete a workflow."""
    if workflow_id not in workflows:
        raise HTTPException(status_code=404, detail="Workflow not found")
    del workflows[workflow_id]
    return {"status": "deleted"}


@router.post("/{workflow_id}/execute", response_model=WorkflowExecution)
async def execute_workflow(
    workflow_id: str,
    input_data: Dict[str, Any],
    background_tasks: BackgroundTasks
):
    """Execute a workflow."""
    if workflow_id not in workflows:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    workflow = workflows[workflow_id]
    execution = WorkflowExecution(
        id=str(uuid.uuid4()),
        workflow_id=workflow_id,
        input_data=input_data,
        status=ExecutionStatus.PENDING
    )
    executions[execution.id] = execution
    
    # Run execution in background
    background_tasks.add_task(run_workflow, execution.id, workflow)
    
    return execution


async def run_workflow(execution_id: str, workflow: Workflow):
    """Background task to run workflow."""
    execution = executions[execution_id]
    execution.status = ExecutionStatus.RUNNING
    execution.started_at = datetime.utcnow()
    
    try:
        executor = WorkflowExecutor()
        result = await executor.execute(workflow, execution.input_data)
        
        execution.output_data = result.get("output", {})
        execution.node_outputs = result.get("node_outputs", {})
        execution.status = ExecutionStatus.COMPLETED
    except Exception as e:
        execution.status = ExecutionStatus.FAILED
        execution.error = str(e)
    finally:
        execution.completed_at = datetime.utcnow()
        executions[execution_id] = execution


@router.get("/{workflow_id}/executions", response_model=List[WorkflowExecution])
async def list_executions(workflow_id: str):
    """List executions for a workflow."""
    return [e for e in executions.values() if e.workflow_id == workflow_id]


@router.get("/executions/{execution_id}", response_model=WorkflowExecution)
async def get_execution(execution_id: str):
    """Get execution status."""
    if execution_id not in executions:
        raise HTTPException(status_code=404, detail="Execution not found")
    return executions[execution_id]
