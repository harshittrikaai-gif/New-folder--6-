'use client';

import { useState, useCallback } from 'react';

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

export function useChat() {
    const [messages, setMessages] = useState<Message[]>([]);
    const [sources, setSources] = useState<Source[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [conversationId, setConversationId] = useState<string | null>(null);

    const sendMessage = useCallback(async (content: string, files?: File[]) => {
        if (!content.trim() && (!files || files.length === 0)) return;

        let currentFiles = files || [];

        // Upload files first
        if (currentFiles.length > 0) {
            try {
                const uploadPromises = currentFiles.map(async (file) => {
                    const formData = new FormData();
                    formData.append('file', file);
                    await fetch('/api/files/upload', {
                        method: 'POST',
                        body: formData,
                    });
                });
                await Promise.all(uploadPromises);
            } catch (err) {
                console.error("Error uploading files:", err);
                // Continue sending message even if upload fails? 
                // Better to notify user, but for now we proceed or maybe just log.
            }
        }

        // Add user message
        const userMessage: Message = {
            id: crypto.randomUUID(),
            role: 'user',
            content: content || (currentFiles.length > 0 ? `[Uploaded ${currentFiles.length} files]` : ''),
            timestamp: new Date(),
        };
        setMessages((prev) => [...prev, userMessage]);
        setIsLoading(true);
        setSources([]);

        try {
            const response = await fetch('/api/chat/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: content || "Analyze the uploaded documents.",
                    conversation_id: conversationId,
                    stream: true,
                }),
            });

            if (!response.ok) throw new Error('Failed to send message');

            const reader = response.body?.getReader();
            const decoder = new TextDecoder();

            let assistantContent = '';
            const assistantMessage: Message = {
                id: crypto.randomUUID(),
                role: 'assistant',
                content: '',
                timestamp: new Date(),
            };
            setMessages((prev) => [...prev, assistantMessage]);

            while (reader) {
                const { done, value } = await reader.read();
                if (done) break;

                const chunk = decoder.decode(value);
                const lines = chunk.split('\n').filter((line) => line.startsWith('data: '));

                for (const line of lines) {
                    try {
                        const data = JSON.parse(line.slice(6));

                        if (data.type === 'content') {
                            assistantContent += data.content;
                            setMessages((prev) =>
                                prev.map((msg) =>
                                    msg.id === assistantMessage.id
                                        ? { ...msg, content: assistantContent }
                                        : msg
                                )
                            );
                        } else if (data.type === 'sources') {
                            setSources(data.content);
                        } else if (data.type === 'done') {
                            setConversationId(data.conversation_id);
                        }
                    } catch (e) {
                        // Ignore parse errors for incomplete chunks
                    }
                }
            }
        } catch (error) {
            console.error('Chat error:', error);
            // Add error message
            setMessages((prev) => [
                ...prev,
                {
                    id: crypto.randomUUID(),
                    role: 'assistant',
                    content: 'Sorry, something went wrong. Please try again.',
                    timestamp: new Date(),
                },
            ]);
        } finally {
            setIsLoading(false);
        }
    }, [conversationId]);

    const clearMessages = useCallback(() => {
        setMessages([]);
        setSources([]);
        setConversationId(null);
    }, []);

    return {
        messages,
        sources,
        isLoading,
        conversationId,
        sendMessage,
        clearMessages,
    };
}
