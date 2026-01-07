'use client';

import ReactMarkdown from 'react-markdown';

interface Message {
    id: string;
    role: 'user' | 'assistant';
    content: string;
    timestamp: Date;
}

interface Source {
    content: string;
    metadata: Record<string, any>;
    score: number;
}

interface MessageListProps {
    messages: Message[];
    sources: Source[];
}

export default function MessageList({ messages, sources }: MessageListProps) {
    return (
        <div className="space-y-6 max-w-3xl mx-auto">
            {messages.map((message) => (
                <div
                    key={message.id}
                    className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                    <div
                        className={`max-w-[85%] ${message.role === 'user'
                                ? 'bg-gradient-to-r from-primary-600 to-purple-600 rounded-2xl rounded-tr-md'
                                : 'glass rounded-2xl rounded-tl-md'
                            } px-5 py-4`}
                    >
                        {message.role === 'assistant' && (
                            <div className="flex items-center gap-2 mb-2">
                                <div className="w-6 h-6 rounded-lg bg-gradient-to-br from-primary-500 to-purple-500 flex items-center justify-center">
                                    <span className="text-xs">✨</span>
                                </div>
                                <span className="text-xs text-gray-400 font-medium">Trika AI</span>
                            </div>
                        )}

                        <div className={`prose prose-invert prose-sm max-w-none ${message.role === 'user' ? 'text-white' : 'text-gray-200'
                            }`}>
                            <ReactMarkdown>{message.content}</ReactMarkdown>
                        </div>

                        <div className="mt-2 text-xs text-gray-500">
                            {new Date(message.timestamp).toLocaleTimeString()}
                        </div>
                    </div>
                </div>
            ))}

            {/* Sources card */}
            {sources.length > 0 && (
                <div className="glass rounded-xl p-4">
                    <h4 className="text-sm font-medium text-gray-400 mb-3 flex items-center gap-2">
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                        </svg>
                        Sources
                    </h4>
                    <div className="space-y-2">
                        {sources.slice(0, 3).map((source, i) => (
                            <div key={i} className="text-xs text-gray-400 p-2 bg-white/5 rounded-lg">
                                <p className="line-clamp-2">{source.content}</p>
                                {source.metadata?.filename && (
                                    <span className="text-primary-400 mt-1 block">
                                        📄 {source.metadata.filename}
                                    </span>
                                )}
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
}
