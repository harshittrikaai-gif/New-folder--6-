'use client';

import { useCallback, useMemo } from 'react';
import ReactFlow, {
    Background,
    Controls,
    MiniMap,
    Node,
    NodeProps,
    Handle,
    Position,
} from 'reactflow';
import 'reactflow/dist/style.css';
import { useWorkflow } from '@/hooks/useWorkflow';

// Custom node component
function CustomNode({ data, selected }: NodeProps) {
    const nodeColors: Record<string, string> = {
        input: 'from-green-500 to-emerald-600',
        llm: 'from-purple-500 to-violet-600',
        rag: 'from-blue-500 to-cyan-600',
        code: 'from-orange-500 to-amber-600',
        http: 'from-pink-500 to-rose-600',
        condition: 'from-yellow-500 to-orange-600',
        transform: 'from-teal-500 to-cyan-600',
        output: 'from-red-500 to-rose-600',
    };

    const nodeIcons: Record<string, string> = {
        input: '📥',
        llm: '🤖',
        rag: '🔍',
        code: '💻',
        http: '🌐',
        condition: '🔀',
        transform: '🔄',
        output: '📤',
    };

    return (
        <div
            className={`px-4 py-3 rounded-xl bg-gradient-to-r ${nodeColors[data.type] || 'from-gray-500 to-gray-600'} min-w-[150px] ${selected ? 'ring-2 ring-white ring-offset-2 ring-offset-transparent' : ''
                }`}
        >
            <Handle
                type="target"
                position={Position.Left}
                className="!w-3 !h-3 !bg-white !border-2 !border-gray-800"
            />

            <div className="flex items-center gap-2">
                <span className="text-xl">{nodeIcons[data.type] || '⚙️'}</span>
                <span className="font-medium text-white text-sm">{data.label}</span>
            </div>

            <Handle
                type="source"
                position={Position.Right}
                className="!w-3 !h-3 !bg-white !border-2 !border-gray-800"
            />
        </div>
    );
}

export default function WorkflowCanvas() {
    const {
        nodes,
        edges,
        onNodesChange,
        onEdgesChange,
        onConnect,
        addNode,
        executeWorkflow,
        isExecuting,
    } = useWorkflow();

    const nodeTypes = useMemo(() => ({
        custom: CustomNode,
    }), []);

    const onDrop = useCallback(
        (event: React.DragEvent) => {
            event.preventDefault();

            const reactFlowBounds = event.currentTarget.getBoundingClientRect();
            const type = event.dataTransfer.getData('application/reactflow');

            if (!type) return;

            const position = {
                x: event.clientX - reactFlowBounds.left - 75,
                y: event.clientY - reactFlowBounds.top - 25,
            };

            addNode(type, position);
        },
        [addNode]
    );

    const onDragOver = useCallback((event: React.DragEvent) => {
        event.preventDefault();
        event.dataTransfer.dropEffect = 'move';
    }, []);

    return (
        <div className="h-full w-full relative">
            <ReactFlow
                nodes={nodes}
                edges={edges}
                onNodesChange={onNodesChange}
                onEdgesChange={onEdgesChange}
                onConnect={onConnect}
                onDrop={onDrop}
                onDragOver={onDragOver}
                nodeTypes={nodeTypes}
                fitView
                className="bg-transparent"
                defaultEdgeOptions={{
                    animated: true,
                    style: { stroke: '#0ea5e9', strokeWidth: 2 },
                }}
            >
                <Background
                    color="#1e293b"
                    gap={20}
                    size={1}
                />
                <Controls
                    className="!bg-dark-800 !border-white/10 !rounded-xl overflow-hidden [&>button]:!bg-dark-800 [&>button]:!border-white/10 [&>button]:!text-white [&>button:hover]:!bg-dark-700"
                />
                <MiniMap
                    className="!bg-dark-900 !rounded-xl !border !border-white/10"
                    nodeColor={(n) => {
                        const colors: Record<string, string> = {
                            input: '#10b981',
                            llm: '#8b5cf6',
                            rag: '#0ea5e9',
                            code: '#f97316',
                            http: '#ec4899',
                            condition: '#eab308',
                            transform: '#14b8a6',
                            output: '#ef4444',
                        };
                        return colors[n.data?.type] || '#64748b';
                    }}
                />
            </ReactFlow>

            {/* Run button */}
            <div className="absolute bottom-6 right-6">
                <button
                    onClick={() => executeWorkflow({})}
                    disabled={isExecuting || nodes.length === 0}
                    className="px-6 py-3 rounded-xl bg-gradient-to-r from-primary-500 to-purple-500 text-white font-medium flex items-center gap-2 hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed transition-opacity shadow-lg shadow-primary-500/25"
                >
                    {isExecuting ? (
                        <>
                            <svg className="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
                                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                            </svg>
                            Running...
                        </>
                    ) : (
                        <>
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                            </svg>
                            Run Workflow
                        </>
                    )}
                </button>
            </div>
        </div>
    );
}
