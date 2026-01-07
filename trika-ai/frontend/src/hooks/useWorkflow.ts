'use client';

import { useState, useCallback } from 'react';
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

export function useWorkflow() {
    const [nodes, setNodes, onNodesChange] = useNodesState<WorkflowNode['data']>([]);
    const [edges, setEdges, onEdgesChange] = useEdgesState([]);
    const [selectedNode, setSelectedNode] = useState<WorkflowNode | null>(null);
    const [isExecuting, setIsExecuting] = useState(false);

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

    const executeWorkflow = useCallback(async (inputData: Record<string, any> = {}) => {
        setIsExecuting(true);

        try {
            // First save the workflow
            const workflow = {
                name: 'Untitled Workflow',
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
                })),
            };

            const saveRes = await fetch('/api/workflows/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name: workflow.name }),
            });
            const savedWorkflow = await saveRes.json();

            // Update workflow with nodes/edges
            await fetch(`/api/workflows/${savedWorkflow.id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(workflow),
            });

            // Execute
            const execRes = await fetch(`/api/workflows/${savedWorkflow.id}/execute`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(inputData),
            });

            return await execRes.json();
        } catch (error) {
            console.error('Workflow execution error:', error);
            throw error;
        } finally {
            setIsExecuting(false);
        }
    }, [nodes, edges]);

    return {
        nodes,
        edges,
        selectedNode,
        isExecuting,
        onNodesChange,
        onEdgesChange,
        onConnect,
        addNode,
        setSelectedNode,
        updateNodeParams,
        executeWorkflow,
    };
}
