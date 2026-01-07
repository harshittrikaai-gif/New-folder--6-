'use client';

import { useState, useRef, useEffect } from 'react';
import MessageList from './MessageList';
import ChatInput from './ChatInput';
import { useChat } from '@/hooks/useChat';

export default function ChatWindow() {
    const { messages, isLoading, sendMessage, sources } = useChat();
    const messagesEndRef = useRef<HTMLDivElement>(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    return (
        <div className="flex flex-col h-full">
            {/* Messages area */}
            <div className="flex-1 overflow-y-auto px-4 py-6">
                {messages.length === 0 ? (
                    <div className="h-full flex flex-col items-center justify-center text-center">
                        <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-primary-500 to-purple-500 flex items-center justify-center mb-6 animate-float">
                            <span className="text-4xl">✨</span>
                        </div>
                        <h2 className="text-2xl font-bold gradient-text mb-2">
                            Welcome to Trika AI
                        </h2>
                        <p className="text-gray-400 max-w-md">
                            I'm your AI assistant powered by RAG and multi-agent orchestration.
                            Upload documents or ask me anything!
                        </p>

                        <div className="mt-8 grid grid-cols-2 gap-3 max-w-lg">
                            {[
                                '💡 Explain quantum computing',
                                '📊 Analyze my documents',
                                '🔧 Help me debug code',
                                '✍️ Write a blog post',
                            ].map((suggestion) => (
                                <button
                                    key={suggestion}
                                    onClick={() => sendMessage(suggestion.slice(2).trim())}
                                    className="glass px-4 py-3 rounded-xl text-sm text-left hover:bg-white/10 transition-colors"
                                >
                                    {suggestion}
                                </button>
                            ))}
                        </div>
                    </div>
                ) : (
                    <>
                        <MessageList messages={messages} sources={sources} />
                        <div ref={messagesEndRef} />
                    </>
                )}
            </div>

            {/* Loading indicator */}
            {isLoading && (
                <div className="px-4 py-2">
                    <div className="flex items-center gap-2 text-gray-400">
                        <div className="flex gap-1">
                            <span className="w-2 h-2 rounded-full bg-primary-500 animate-bounce" style={{ animationDelay: '0ms' }} />
                            <span className="w-2 h-2 rounded-full bg-primary-500 animate-bounce" style={{ animationDelay: '150ms' }} />
                            <span className="w-2 h-2 rounded-full bg-primary-500 animate-bounce" style={{ animationDelay: '300ms' }} />
                        </div>
                        <span className="text-sm">Thinking...</span>
                    </div>
                </div>
            )}

            {/* Input area */}
            <div className="p-4 border-t border-white/5">
                <ChatInput onSend={sendMessage} disabled={isLoading} />
            </div>
        </div>
    );
}
