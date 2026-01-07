'use client';

import { useState, useRef, KeyboardEvent } from 'react';

interface ChatInputProps {
    onSend: (message: string, files?: File[], model?: string) => void;
    disabled?: boolean;
}

export default function ChatInput({ onSend, disabled }: ChatInputProps) {
    const [input, setInput] = useState('');
    const [files, setFiles] = useState<File[]>([]);
    const [selectedModel, setSelectedModel] = useState('gpt-4-turbo-preview');
    const fileInputRef = useRef<HTMLInputElement>(null);
    const textareaRef = useRef<HTMLTextAreaElement>(null);

    const handleSubmit = () => {
        if (input.trim() || files.length > 0) {
            onSend(input.trim(), files, selectedModel);
            setInput('');
            setFiles([]);
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

    return (
        <div className="glass rounded-2xl p-2">
            {/* File previews */}
            {files.length > 0 && (
                <div className="flex gap-2 p-2 mb-2 border-b border-white/10">
                    {files.map((file, i) => (
                        <div
                            key={i}
                            className="flex items-center gap-2 px-3 py-2 bg-white/10 rounded-lg text-sm"
                        >
                            <span>📎</span>
                            <span className="truncate max-w-[150px]">{file.name}</span>
                            <button
                                onClick={() => setFiles(files.filter((_, idx) => idx !== i))}
                                className="text-gray-400 hover:text-white"
                            >
                                ×
                            </button>
                        </div>
                    ))}
                </div>
            )}

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
                    className="p-3 rounded-xl text-gray-400 hover:text-white hover:bg-white/10 transition-colors"
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
                    onChange={(e) => setInput(e.target.value)}
                    onKeyDown={handleKeyDown}
                    placeholder="Ask anything..."
                    disabled={disabled}
                    rows={1}
                    className="flex-1 bg-transparent resize-none px-4 py-3 text-white placeholder-gray-500 focus:outline-none"
                    style={{ minHeight: '48px', maxHeight: '200px' }}
                />

                {/* Model Selector */}
                <select
                    onChange={(e) => setSelectedModel(e.target.value)}
                    value={selectedModel}
                    className="bg-black/20 text-xs text-gray-400 rounded-lg px-2 py-1 outline-none border border-white/10 hover:border-white/20 transition-colors"
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

                {/* Send button */}
                <button
                    onClick={handleSubmit}
                    disabled={disabled || (!input.trim() && files.length === 0)}
                    className="p-3 rounded-xl bg-gradient-to-r from-primary-500 to-purple-500 text-white hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed transition-opacity"
                >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                    </svg>
                </button>
            </div>
        </div>
    );
}
