'use client';

import React, { useState, useEffect } from 'react';
import { FileText, Trash2, Upload, Database, CheckCircle2, AlertCircle, Loader2 } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

interface FileInfo {
    id: string;
    filename: string;
    content_type: string;
    size: number;
    indexed: boolean;
    created_at: string;
}

export default function KnowledgeBase() {
    const [files, setFiles] = useState<FileInfo[]>([]);
    const [loading, setLoading] = useState(true);
    const [uploading, setUploading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

    const fetchFiles = async () => {
        try {
            setLoading(true);
            const response = await fetch(`${API_URL}/api/v1/files/`);
            if (!response.ok) throw new Error('Failed to fetch files');
            const data = await response.json();
            setFiles(data.files);
        } catch (err: any) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchFiles();
    }, []);

    const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (!file) return;

        setUploading(true);
        setError(null);

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch(`${API_URL}/api/v1/files/upload`, {
                method: 'POST',
                body: formData,
            });

            if (!response.ok) throw new Error('Upload failed');

            await fetchFiles();
        } catch (err: any) {
            setError(err.message);
        } finally {
            setUploading(false);
        }
    };

    const handleDelete = async (id: string) => {
        try {
            const response = await fetch(`${API_URL}/api/v1/files/${id}`, {
                method: 'DELETE',
            });
            if (!response.ok) throw new Error('Delete failed');
            setFiles(files.filter(f => f.id !== id));
        } catch (err: any) {
            setError(err.message);
        }
    };

    return (
        <div className="min-h-[calc(100vh-80px)] p-8">
            <div className="max-w-6xl mx-auto space-y-8">
                {/* Header */}
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
                    <div>
                        <h1 className="text-4xl font-bold gradient-text">Knowledge Base</h1>
                        <p className="text-gray-400 mt-2">Manage documents for RAG (Retrieval-Augmented Generation).</p>
                    </div>

                    <label className="relative group cursor-pointer inline-flex items-center gap-2 px-6 py-3 rounded-xl bg-primary-500 hover:bg-primary-600 transition-all font-semibold shadow-lg shadow-primary-500/20 active:scale-95">
                        {uploading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Upload className="w-5 h-5" />}
                        <span>{uploading ? 'Checking...' : 'Upload Document'}</span>
                        <input
                            type="file"
                            className="hidden"
                            onChange={handleUpload}
                            disabled={uploading}
                        />
                    </label>
                </div>

                {/* Main Stats / Info */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div className="glass-card p-6 rounded-2xl flex items-center gap-4">
                        <div className="w-12 h-12 rounded-xl bg-blue-500/20 flex items-center justify-center text-blue-500">
                            <Database className="w-6 h-6" />
                        </div>
                        <div>
                            <p className="text-sm text-gray-400">Total Documents</p>
                            <p className="text-2xl font-bold">{files.length}</p>
                        </div>
                    </div>
                    <div className="glass-card p-6 rounded-2xl flex items-center gap-4">
                        <div className="w-12 h-12 rounded-xl bg-green-500/20 flex items-center justify-center text-green-500">
                            <CheckCircle2 className="w-6 h-6" />
                        </div>
                        <div>
                            <p className="text-sm text-gray-400">Indexed Successfully</p>
                            <p className="text-2xl font-bold">{files.filter(f => f.indexed).length}</p>
                        </div>
                    </div>
                    <div className="glass-card p-6 rounded-2xl flex items-center gap-4">
                        <div className="w-12 h-12 rounded-xl bg-purple-500/20 flex items-center justify-center text-purple-500">
                            <FileText className="w-6 h-6" />
                        </div>
                        <div>
                            <p className="text-sm text-gray-400">Total Storage</p>
                            <p className="text-2xl font-bold">
                                {(files.reduce((acc, f) => acc + f.size, 0) / 1024 / 1024).toFixed(2)} MB
                            </p>
                        </div>
                    </div>
                </div>

                {/* Error Banner */}
                <AnimatePresence>
                    {error && (
                        <motion.div
                            initial={{ opacity: 0, y: -20 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: -20 }}
                            className="bg-red-500/10 border border-red-500/20 p-4 rounded-xl flex items-center gap-3 text-red-500"
                        >
                            <AlertCircle className="w-5 h-5" />
                            <p>{error}</p>
                        </motion.div>
                    )}
                </AnimatePresence>

                {/* Document List */}
                <div className="glass-card rounded-2xl overflow-hidden border border-white/5">
                    <table className="w-full text-left">
                        <thead className="bg-white/5 border-b border-white/5">
                            <tr>
                                <th className="px-6 py-4 font-semibold text-gray-300">File Name</th>
                                <th className="px-6 py-4 font-semibold text-gray-300">Status</th>
                                <th className="px-6 py-4 font-semibold text-gray-300">Size</th>
                                <th className="px-6 py-4 font-semibold text-gray-300 text-right">Actions</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-white/5 text-gray-400">
                            {loading ? (
                                <tr>
                                    <td colSpan={4} className="px-6 py-20 text-center">
                                        <Loader2 className="w-10 h-10 animate-spin mx-auto opacity-20" />
                                    </td>
                                </tr>
                            ) : files.length === 0 ? (
                                <tr>
                                    <td colSpan={4} className="px-6 py-20 text-center text-gray-500">
                                        No documents found. Upload one to get started!
                                    </td>
                                </tr>
                            ) : (
                                files.map((file) => (
                                    <motion.tr
                                        key={file.id}
                                        layout
                                        initial={{ opacity: 0 }}
                                        animate={{ opacity: 1 }}
                                        className="hover:bg-white/5 transition-colors group"
                                    >
                                        <td className="px-6 py-4">
                                            <div className="flex items-center gap-3">
                                                <div className="w-10 h-10 rounded-lg bg-gray-500/10 flex items-center justify-center">
                                                    <FileText className="w-5 h-5 text-gray-400" />
                                                </div>
                                                <span className="font-medium text-gray-200">{file.filename}</span>
                                            </div>
                                        </td>
                                        <td className="px-6 py-4">
                                            {file.indexed ? (
                                                <div className="flex items-center gap-1.5 text-green-500 text-sm">
                                                    <CheckCircle2 className="w-4 h-4" />
                                                    <span>Indexed</span>
                                                </div>
                                            ) : (
                                                <div className="flex items-center gap-1.5 text-yellow-500 text-sm">
                                                    <AlertCircle className="w-4 h-4" />
                                                    <span>Pending</span>
                                                </div>
                                            )}
                                        </td>
                                        <td className="px-6 py-4 text-sm">
                                            {(file.size / 1024).toFixed(1)} KB
                                        </td>
                                        <td className="px-6 py-4 text-right">
                                            <button
                                                onClick={() => handleDelete(file.id)}
                                                className="p-2 rounded-lg hover:bg-red-500/20 hover:text-red-500 transition-all text-gray-500"
                                            >
                                                <Trash2 className="w-5 h-5" />
                                            </button>
                                        </td>
                                    </motion.tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
}
