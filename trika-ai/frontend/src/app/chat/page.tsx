import ChatWindow from '@/components/chat/ChatWindow';

export default function ChatPage() {
    return (
        <div className="h-[calc(100vh-72px)] flex">
            {/* Sidebar - File uploads */}
            <aside className="w-64 glass-dark border-r border-white/5 p-4 hidden lg:block">
                <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wide mb-4">
                    Documents
                </h2>
                <div className="space-y-2">
                    <button className="w-full px-4 py-3 rounded-xl border-2 border-dashed border-gray-600 text-gray-400 hover:border-primary-500 hover:text-primary-400 transition-all flex items-center justify-center gap-2">
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                        </svg>
                        Upload Document
                    </button>
                </div>

                <div className="mt-6">
                    <p className="text-xs text-gray-500 text-center">
                        Upload PDFs, text files, or markdown to enable RAG
                    </p>
                </div>
            </aside>

            {/* Chat area */}
            <div className="flex-1 flex flex-col">
                <ChatWindow />
            </div>
        </div>
    );
}
