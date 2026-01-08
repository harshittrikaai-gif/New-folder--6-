'use client';

import { useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
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
    }, [messages, isLoading]);

    return (
        <div className="flex flex-col h-full relative z-10">
            {/* Messages area */}
            <div className="flex-1 overflow-y-auto overflow-x-hidden px-4 py-8 custom-scrollbar">
                <AnimatePresence mode="wait">
                    {messages.length === 0 ? (
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            exit={{ opacity: 0 }}
                            className="h-full flex flex-col items-center justify-center text-center max-w-2xl mx-auto"
                        >
                            {/* Animated Logo Container */}
                            <div className="relative mb-10 group cursor-pointer">
                                <div className="absolute -inset-10 bg-gradient-to-tr from-purple-600 to-cyan-600 rounded-full blur-[50px] opacity-20 group-hover:opacity-40 transition-opacity duration-700"></div>
                                <motion.div
                                    animate={{ rotate: 360 }}
                                    transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
                                    className="relative z-10 w-24 h-24 rounded-full border border-white/10 flex items-center justify-center bg-black/50 backdrop-blur-xl"
                                >
                                    <div className="w-16 h-16 rounded-full border border-white/20 flex items-center justify-center">
                                        <span className="text-4xl">💠</span>
                                    </div>
                                </motion.div>
                            </div>

                            <motion.h2
                                initial={{ y: 20, opacity: 0 }}
                                animate={{ y: 0, opacity: 1 }}
                                transition={{ delay: 0.2 }}
                                className="text-4xl md:text-5xl font-machina font-bold bg-clip-text text-transparent bg-gradient-to-r from-white via-gray-200 to-gray-500 mb-4 tracking-tight"
                            >
                                Trika AI <span className="text-primary-500">System</span>
                            </motion.h2>

                            <motion.p
                                initial={{ y: 20, opacity: 0 }}
                                animate={{ y: 0, opacity: 1 }}
                                transition={{ delay: 0.3 }}
                                className="text-lg text-gray-400 max-w-md font-light leading-relaxed mb-12"
                            >
                                Initiate dialogue with the multi-agent neural network.
                                <br />
                                <span className="text-xs uppercase tracking-[0.2em] text-gray-600 mt-2 block">System Online v1.0</span>
                            </motion.p>

                            <motion.div
                                initial={{ y: 20, opacity: 0 }}
                                animate={{ y: 0, opacity: 1 }}
                                transition={{ delay: 0.4 }}
                                className="grid grid-cols-1 sm:grid-cols-2 gap-4 w-full"
                            >
                                {[
                                    { text: 'Explain quantum computing', icon: '🌌' },
                                    { text: 'Analyze this document', icon: '📄' },
                                    { text: 'Debug my code', icon: '🐛' },
                                    { text: 'Write a blog post', icon: '✍️' },
                                ].map((suggestion, i) => (
                                    <motion.button
                                        key={suggestion.text}
                                        whileHover={{ scale: 1.02, backgroundColor: 'rgba(255,255,255,0.08)' }}
                                        whileTap={{ scale: 0.98 }}
                                        onClick={() => sendMessage(suggestion.text)}
                                        className="group flex flex-col items-start p-4 rounded-2xl bg-white/5 border border-white/5 hover:border-primary-500/30 transition-all duration-300"
                                    >
                                        <span className="text-2xl mb-2 grayscale group-hover:grayscale-0 transition-all">{suggestion.icon}</span>
                                        <span className="text-sm font-medium text-gray-300 group-hover:text-white">{suggestion.text}</span>
                                    </motion.button>
                                ))}
                            </motion.div>
                        </motion.div>
                    ) : (
                        <>
                            <MessageList messages={messages} sources={sources} />
                            {isLoading && (
                                <motion.div
                                    initial={{ opacity: 0, scale: 0.9 }}
                                    animate={{ opacity: 1, scale: 1 }}
                                    className="flex items-center gap-3 text-gray-400 max-w-3xl mx-auto pl-4 mt-4"
                                >
                                    <div className="flex gap-1.5 h-4 items-center">
                                        {[0, 1, 2].map((i) => (
                                            <motion.div
                                                key={i}
                                                animate={{
                                                    height: [4, 16, 4],
                                                    backgroundColor: ['#a78bfa', '#c084fc', '#a78bfa']
                                                }}
                                                transition={{
                                                    duration: 0.8,
                                                    repeat: Infinity,
                                                    delay: i * 0.15
                                                }}
                                                className="w-1 rounded-full bg-primary-400"
                                            />
                                        ))}
                                    </div>
                                    <span className="text-xs uppercase tracking-widest text-primary-400">Processing</span>
                                </motion.div>
                            )}
                            <div ref={messagesEndRef} className="h-4" />
                        </>
                    )}
                </AnimatePresence>
            </div>

            {/* Input area */}
            <div className="p-4 md:p-6 mb-4 max-w-4xl mx-auto w-full">
                <ChatInput onSend={sendMessage} disabled={isLoading} />
                <p className="text-center text-[10px] text-gray-600 mt-2 font-mono">
                    Trika AI can make mistakes. Consider checking important information.
                </p>
            </div>
        </div>
    );
}
