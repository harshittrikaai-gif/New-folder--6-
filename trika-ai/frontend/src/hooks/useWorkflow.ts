'use client';

import { useState, useCallback, useRef, useEffect } from 'react';
import { Node, Edge, useNodesState, useEdgesState, addEdge, Connection } from 'reactflow';

export interface WorkflowNode extends Node {
    data: {
        label: string;
        type: string;
        params: Record<string, any>;
    };
}

export interface Workflow {
    id: string;
    name: string;
    description: string;
    nodes: WorkflowNode[];
    edges: Edge[];
}

export interface ExecutionUpdate {
    type: 'start' | 'node_completed' | 'completed' | 'failed' | 'pong';
    timestamp: string;
    [key: string]: any;
}

export function useWorkflow() {
    const [nodes, setNodes, onNodesChange] = useNodesState<WorkflowNode['data']>([]);
    const [edges, setEdges, onEdgesChange] = useEdgesState([]);
    const [selectedNode, setSelectedNode] = useState<WorkflowNode | null>(null);
    const [isExecuting, setIsExecuting] = useState(false);
    const [executionStatus, setExecutionStatus] = useState<ExecutionUpdate | null>(null);
    const [workflowId, setWorkflowId] = useState<string | null>(null);
    const wsRef = useRef<WebSocket | null>(null);

    const onConnect = useCallback(
        (params: Connection) => setEdges((eds) => addEdge({
            ...params,
            animated: true,
            style: { stroke: '#0ea5e9' },
        }, eds)),
        [setEdges]
    );

    const addNode = useCallback((type: string, position: { x: number; y: number }) => {
        const id = crypto.randomUUID();
        const newNode: WorkflowNode = {
            id,
            type: 'custom',
            position,
            data: {
                label: type.charAt(0).toUpperCase() + type.slice(1),
                type,
                params: {},
            },
        };
        setNodes((nds) => [...nds, newNode]);
    }, [setNodes]);

    const updateNodeParams = useCallback((nodeId: string, params: Record<string, any>) => {
        setNodes((nds) =>
            nds.map((node) =>
                node.id === nodeId
                    ? { ...node, data: { ...node.data, params: { ...node.data.params, ...params } } }
                    : node
            )
        );
    }, [setNodes]);

    const connectWebSocket = useCallback((executionId: string) => {
        try {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = `${protocol}//${window.location.host}/ws/workflows/${executionId}`;
            
            wsRef.current = new WebSocket(wsUrl);

            wsRef.current.onopen = () => {
                console.log('WebSocket connected');
                // Send initial ping
                wsRef.current?.send(JSON.stringify({ action: 'ping' }));
            };

            wsRef.current.onmessage = (event) => {
                try {
                    const update = JSON.parse(event.data) as ExecutionUpdate;
                    setExecutionStatus(update);
                    
                    if (update.type === 'completed' || update.type === 'failed') {
                        setIsExecuting(false);
                        if (wsRef.current) {
                            wsRef.current.close();
                        }
                    }
                } catch (error) {
                    console.error('Error parsing WebSocket message:', error);
                }
            };

            wsRef.current.onerror = (error) => {
                console.error('WebSocket error:', error);
            };

            wsRef.current.onclose = () => {
                console.log('WebSocket closed');
            };
        } catch (error) {
            console.error('Error connecting WebSocket:', error);
        }
    }, []);

    useEffect(() => {
        return () => {
            if (wsRef.current) {
                wsRef.current.close();
            }
        };
    }, []);

    const saveWorkflow = useCallback(async (name: string = 'Untitled Workflow') => {
        const workflow = {
            name,
            description: '',
            nodes: nodes.map((n) => ({
                id: n.id,
                config: {
                    type: n.data.type,
                    label: n.data.label,
                    params: n.data.params,
                    position: n.position,
                },
            })),
            edges: edges.map((e) => ({
                id: e.id,
                source: e.source,
                target: e.target,
                source_handle: e.sourceHandle,
                target_handle: e.targetHandle,
            })),
        };

        try {
            // Create or update workflow
            if (!workflowId) {
                const createRes = await fetch('/api/v1/workflows/', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ name, description: '' }),
                });
                
                if (!createRes.ok) throw new Error('Failed to create workflow');
                const created = await createRes.json();
                setWorkflowId(created.id);
                
                // Update with nodes and edges
                const updateRes = await fetch(`/api/v1/workflows/${created.id}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(workflow),
                });
                
                if (!updateRes.ok) throw new Error('Failed to update workflow');
                return created.id;
            } else {
                const updateRes = await fetch(`/api/v1/workflows/${workflowId}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(workflow),
                });
                
                if (!updateRes.ok) throw new Error('Failed to update workflow');
                return workflowId;
            }
        } catch (error) {
            console.error('Error saving workflow:', error);
            throw error;
        }
    }, [nodes, edges, workflowId]);

    const executeWorkflow = useCallback(async (inputData: Record<string, any> = {}) => {
        setIsExecuting(true);
        setExecutionStatus(null);

        try {
            // Save workflow first
            const wfId = await saveWorkflow();

            // Execute workflow
            const execRes = await fetch(`/api/v1/workflows/${wfId}/execute`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(inputData),
            });

            if (!execRes.ok) throw new Error('Failed to execute workflow');
            
            const execution = await execRes.json();
            
            // Connect WebSocket for real-time updates
            connectWebSocket(execution.id);
            
            return execution;
        } catch (error) {
            console.error('Workflow execution error:', error);
            setIsExecuting(false);
            throw error;
        }
    }, [saveWorkflow, connectWebSocket]);

    const loadWorkflow = useCallback(async (id: string) => {
        try {
            const res = await fetch(`/api/v1/workflows/${id}`);
            if (!res.ok) throw new Error('Failed to load workflow');
            
            const workflow = await res.json();
            setWorkflowId(workflow.id);
            
            // Convert back to node/edge format
            const nodesList = workflow.nodes.map((n: any) => ({
                id: n.id,
                type: 'custom',
                position: n.config.position,
                data: {
                    label: n.config.label,
                    type: n.config.type,
                    params: n.config.params,
                },
            }));
            
            const edgesList = workflow.edges.map((e: any) => ({
                id: e.id,
                source: e.source,
                target: e.target,
                sourceHandle: e.source_handle,
                targetHandle: e.target_handle,
                animated: true,
                style: { stroke: '#0ea5e9' },
            }));
            
            setNodes(nodesList);
            setEdges(edgesList);
        } catch (error) {
            console.error('Error loading workflow:', error);
            throw error;
        }
    }, [setNodes, setEdges]);

    const listWorkflows = useCallback(async () => {
        try {
            const res = await fetch('/api/v1/workflows/');
            if (!res.ok) throw new Error('Failed to list workflows');
            return await res.json();
        } catch (error) {
            console.error('Error listing workflows:', error);
            throw error;
        }
    }, []);

    const getExecutionStatus = useCallback(async (executionId: string) => {
        try {
            const res = await fetch(`/api/v1/workflows/executions/${executionId}`);
            if (!res.ok) throw new Error('Failed to get execution status');
            return await res.json();
        } catch (error) {
            console.error('Error getting execution status:', error);
            throw error;
        }
    }, []);

    return {
        nodes,
        edges,
        selectedNode,
        isExecuting,
        executionStatus,
        workflowId,
        onNodesChange,
        onEdgesChange,
        onConnect,
        addNode,
        setSelectedNode,
        updateNodeParams,
        executeWorkflow,
        saveWorkflow,
        loadWorkflow,
        listWorkflows,
        getExecutionStatus,
    };
}
