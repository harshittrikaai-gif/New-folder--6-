'use client';

import { useState, useRef, KeyboardEvent } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface ChatInputProps {
    onSend: (message: string, files?: File[], model?: string) => void;
    disabled?: boolean;
}

export default function ChatInput({ onSend, disabled }: ChatInputProps) {
    const [input, setInput] = useState('');
    const [files, setFiles] = useState<File[]>([]);
    const [selectedModel, setSelectedModel] = useState('gpt-4-turbo-preview');
    const [isFocused, setIsFocused] = useState(false);
    const fileInputRef = useRef<HTMLInputElement>(null);
    const textareaRef = useRef<HTMLTextAreaElement>(null);

    const handleSubmit = () => {
        if (input.trim() || files.length > 0) {
            onSend(input.trim(), files, selectedModel);
            setInput('');
            setFiles([]);
            if (textareaRef.current) {
                textareaRef.current.style.height = '52px';
            }
        }
    };

    const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSubmit();
        }
    };

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files) {
            setFiles(Array.from(e.target.files));
        }
    };

    // Auto-resize textarea
    const handleInput = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
        setInput(e.target.value);
        if (textareaRef.current) {
            textareaRef.current.style.height = 'auto';
            textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 200)}px`;
        }
    };

    return (
        <div className={`relative transition-all duration-300 ${isFocused ? 'scale-[1.01]' : ''}`}>
            {/* Glow effect */}
            <div className={`absolute -inset-0.5 bg-gradient-to-r from-primary-500 to-purple-500 rounded-2xl blur opacity-30 transition duration-500 ${isFocused ? 'opacity-70' : ''}`}></div>

            <div className="relative glass-dark rounded-2xl p-2 border border-white/10">
                {/* File previews */}
                <AnimatePresence>
                    {files.length > 0 && (
                        <motion.div
                            initial={{ height: 0, opacity: 0 }}
                            animate={{ height: 'auto', opacity: 1 }}
                            exit={{ height: 0, opacity: 0 }}
                            className="flex gap-2 p-2 mb-2 border-b border-white/5 overflow-hidden"
                        >
                            {files.map((file, i) => (
                                <motion.div
                                    key={i}
                                    initial={{ scale: 0.8, opacity: 0 }}
                                    animate={{ scale: 1, opacity: 1 }}
                                    exit={{ scale: 0.8, opacity: 0 }}
                                    className="flex items-center gap-2 px-3 py-1.5 bg-white/10 rounded-lg text-xs border border-white/5"
                                >
                                    <span className="text-primary-400">📄</span>
                                    <span className="truncate max-w-[120px] text-gray-300">{file.name}</span>
                                    <button
                                        onClick={() => setFiles(files.filter((_, idx) => idx !== i))}
                                        className="text-gray-500 hover:text-white transition-colors"
                                    >
                                        ×
                                    </button>
                                </motion.div>
                            ))}
                        </motion.div>
                    )}
                </AnimatePresence>

                <div className="flex items-end gap-2">
                    {/* File upload button */}
                    <input
                        ref={fileInputRef}
                        type="file"
                        multiple
                        onChange={handleFileChange}
                        className="hidden"
                        accept=".pdf,.txt,.md,.docx"
                    />
                    <button
                        onClick={() => fileInputRef.current?.click()}
                        className="p-3 mb-0.5 rounded-xl text-gray-400 hover:text-white hover:bg-white/10 transition-colors tooltip relative group"
                        disabled={disabled}
                    >
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13" />
                        </svg>
                    </button>

                    {/* Text input */}
                    <textarea
                        ref={textareaRef}
                        value={input}
                        onChange={handleInput}
                        onKeyDown={handleKeyDown}
                        onFocus={() => setIsFocused(true)}
                        onBlur={() => setIsFocused(false)}
                        placeholder="Ask anything..."
                        disabled={disabled}
                        rows={1}
                        className="flex-1 bg-transparent resize-none px-4 py-3.5 text-white placeholder-gray-500 focus:outline-none max-h-[200px]"
                        style={{ minHeight: '52px' }}
                    />

                    <div className="flex flex-col gap-1 pb-1">
                        {/* Voice transcribe button */}
                        <button
                            onClick={async () => {
                                if (disabled) return;
                                try {
                                    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                                    const mediaRecorder = new MediaRecorder(stream);
                                    const audioChunks: Blob[] = [];

                                    mediaRecorder.ondataavailable = (event) => {
                                        audioChunks.push(event.data);
                                    };

                                    mediaRecorder.onstop = async () => {
                                        const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                                        const formData = new FormData();
                                        formData.append('file', audioBlob, 'voice.wav');

                                        const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
                                        const response = await fetch(`${API_URL}/api/v1/chat/voice`, {
                                            method: 'POST',
                                            body: formData,
                                        });
                                        const data = await response.json();
                                        if (data.text) setInput(prev => prev + ' ' + data.text);
                                        stream.getTracks().forEach(track => track.stop());
                                    };

                                    mediaRecorder.start();
                                    setTimeout(() => mediaRecorder.stop(), 3000); // Record for 3 seconds for demo
                                } catch (err) {
                                    console.error('Voice error:', err);
                                }
                            }}
                            className="p-3 mb-0.5 rounded-xl text-gray-400 hover:text-primary-400 hover:bg-white/10 transition-colors"
                            title="Voice Input (3s)"
                        >
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
                            </svg>
                        </button>

                        {/* Model Selector - Compact */}
                        <div className="relative">
                            <select
                                onChange={(e) => setSelectedModel(e.target.value)}
                                value={selectedModel}
                                className="appearance-none bg-black/40 text-[10px] text-gray-400 rounded-lg pl-2 pr-6 py-1 outline-none border border-white/5 hover:border-white/20 transition-colors cursor-pointer w-[100px]"
                            >
                                <optgroup label="OpenAI">
                                    <option value="gpt-4-turbo-preview">GPT-4 Turbo</option>
                                    <option value="gpt-3.5-turbo">GPT-3.5</option>
                                    <option value="gpt-4">GPT-4</option>
                                </optgroup>
                                <optgroup label="Anthropic">
                                    <option value="claude-3-opus-20240229">Claude 3 Opus</option>
                                    <option value="claude-3-sonnet-20240229">Claude 3 Sonnet</option>
                                </optgroup>
                            </select>
                            <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-gray-500">
                                <svg className="h-3 w-3 fill-current" viewBox="0 0 20 20">
                                    <path d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clipRule="evenodd" fillRule="evenodd" />
                                </svg>
                            </div>
                        </div>

                        {/* Send button */}
                        <motion.button
                            onClick={handleSubmit}
                            disabled={disabled || (!input.trim() && files.length === 0)}
                            whileHover={{ scale: 1.05 }}
                            whileTap={{ scale: 0.95 }}
                            className="p-2.5 rounded-xl bg-gradient-to-r from-primary-500 to-purple-500 text-white shadow-lg shadow-purple-500/20 disabled:opacity-50 disabled:shadow-none disabled:cursor-not-allowed"
                        >
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                            </svg>
                        </motion.button>
                    </div>
                </div>
            </div>
        </div>
    );
}
