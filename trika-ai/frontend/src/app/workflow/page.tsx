import WorkflowCanvas from '@/components/workflow/WorkflowCanvas';

export default function WorkflowPage() {
    return (
        <div className="h-[calc(100vh-72px)] flex">
            {/* Node palette */}
            <aside className="w-64 glass-dark border-r border-white/5 p-4">
                <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wide mb-4">
                    Nodes
                </h2>

                <div className="space-y-2">
                    {[
                        { type: 'input', label: 'Input', icon: '📥', color: 'from-green-500 to-emerald-600' },
                        { type: 'llm', label: 'LLM', icon: '🤖', color: 'from-purple-500 to-violet-600' },
                        { type: 'rag', label: 'RAG Query', icon: '🔍', color: 'from-blue-500 to-cyan-600' },
                        { type: 'code', label: 'Code', icon: '💻', color: 'from-orange-500 to-amber-600' },
                        { type: 'http', label: 'HTTP', icon: '🌐', color: 'from-pink-500 to-rose-600' },
                        { type: 'condition', label: 'Condition', icon: '🔀', color: 'from-yellow-500 to-orange-600' },
                        { type: 'transform', label: 'Transform', icon: '🔄', color: 'from-teal-500 to-cyan-600' },
                        { type: 'output', label: 'Output', icon: '📤', color: 'from-red-500 to-rose-600' },
                    ].map((node) => (
                        <div
                            key={node.type}
                            draggable
                            className={`px-4 py-3 rounded-xl bg-gradient-to-r ${node.color} cursor-grab active:cursor-grabbing flex items-center gap-3 hover:scale-[1.02] transition-transform`}
                        >
                            <span className="text-xl">{node.icon}</span>
                            <span className="font-medium text-white">{node.label}</span>
                        </div>
                    ))}
                </div>
            </aside>

            {/* Canvas */}
            <div className="flex-1">
                <WorkflowCanvas />
            </div>

            {/* Properties panel */}
            <aside className="w-72 glass-dark border-l border-white/5 p-4">
                <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wide mb-4">
                    Properties
                </h2>

                <div className="text-gray-500 text-sm text-center py-8">
                    Select a node to edit its properties
                </div>
            </aside>
        </div>
    );
}
