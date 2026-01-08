'use client';

import { motion } from 'framer-motion';
import ReactMarkdown from 'react-markdown';
import { CodeBlock } from '@/components/ui/CodeBlock';

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
        <div className="space-y-8 max-w-4xl mx-auto pb-10">
            {messages.map((message, index) => (
                <motion.div
                    key={message.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.4, ease: "easeOut" }}
                    className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                    <div className={`flex gap-4 max-w-[85%] ${message.role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>
                        {/* Avatar */}
                        <div className="shrink-0 flex flex-col justify-end">
                            <div className={`w-8 h-8 rounded-xl flex items-center justify-center border border-white/10 ${message.role === 'user'
                                    ? 'bg-gradient-to-br from-purple-500/20 to-cyan-500/20'
                                    : 'bg-primary-500/20'
                                }`}>
                                <span className="text-sm">
                                    {message.role === 'user' ? '👤' : '✨'}
                                </span>
                            </div>
                        </div>

                        {/* Content Bubble */}
                        <div
                            className={`relative px-6 py-5 shadow-xl ${message.role === 'user'
                                ? 'bg-gradient-to-br from-purple-600 to-indigo-600 rounded-3xl rounded-tr-md text-white border border-white/10'
                                : 'glass-dark rounded-3xl rounded-tl-md text-gray-200 border border-white/5'
                                }`}
                        >
                            {/* Header for assistant */}
                            {message.role === 'assistant' && (
                                <div className="flex items-center gap-2 mb-3 pb-3 border-b border-white/5">
                                    <span className="text-xs font-machina font-bold text-transparent bg-clip-text bg-gradient-to-r from-primary-400 to-purple-400">
                                        TRIKA AI
                                    </span>
                                    <span className="text-[10px] text-gray-500 uppercase tracking-widest">
                                        {new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                    </span>
                                </div>
                            )}

                            <div className={`prose prose-invert prose-p:leading-relaxed prose-pre:p-0 prose-pre:bg-transparent max-w-none ${message.role === 'user' ? 'text-white' : 'text-gray-300'
                                }`}>
                                <ReactMarkdown
                                    components={{
                                        code({ node, className, children, ...props }) {
                                            const match = /language-(\w+)/.exec(className || '');
                                            return match ? (
                                                <CodeBlock
                                                    language={match[1]}
                                                    value={String(children).replace(/\n$/, '')}
                                                />
                                            ) : (
                                                <code className="bg-white/10 px-1.5 py-0.5 rounded text-sm text-primary-300 font-mono" {...props}>
                                                    {children}
                                                </code>
                                            )
                                        }
                                    }}
                                >
                                    {message.content}
                                </ReactMarkdown>
                            </div>
                        </div>
                    </div>
                </motion.div>
            ))}

            {/* Sources section with improved design */}
            {sources.length > 0 && (
                <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="ml-12 max-w-[80%]"
                >
                    <div className="glass-dark border border-white/5 rounded-2xl p-5">
                        <h4 className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-4 flex items-center gap-2">
                            <svg className="w-4 h-4 text-primary-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                            </svg>
                            Verified Sources
                        </h4>
                        <div className="grid gap-3">
                            {sources.slice(0, 3).map((source, i) => (
                                <div key={i} className="group p-3 bg-white/5 hover:bg-white/10 rounded-xl border border-white/5 transition-colors cursor-default">
                                    <p className="text-sm text-gray-300 line-clamp-2 leading-relaxed mb-2">
                                        {source.content}
                                    </p>
                                    <div className="flex items-center justify-between">
                                        <div className="flex items-center gap-2">
                                            <span className="text-xs text-primary-400 font-mono bg-primary-500/10 px-2 py-0.5 rounded">
                                                {(source.score * 100).toFixed(0)}% Match
                                            </span>
                                            {source.metadata?.filename && (
                                                <span className="text-xs text-gray-500 flex items-center gap-1">
                                                    <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                                                    </svg>
                                                    {source.metadata.filename}
                                                </span>
                                            )}
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </motion.div>
            )}
        </div>
    );
}
