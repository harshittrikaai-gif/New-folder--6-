'use client';

import React, { useState, useEffect } from 'react';
import { BarChart3, TrendingUp, DollarSign, MessageSquare, Zap, Loader2, RefreshCw } from 'lucide-react';
import { motion } from 'framer-motion';

interface AnalyticsData {
    total_tokens: number;
    total_chats: number;
    cost_estimate: number;
}

export default function AnalyticsDashboard() {
    const [data, setData] = useState<AnalyticsData | null>(null);
    const [loading, setLoading] = useState(true);

    const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

    const fetchData = async () => {
        try {
            setLoading(true);
            const response = await fetch(`${API_URL}/api/v1/chat/analytics`);
            const json = await response.json();
            setData(json);
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchData();
    }, []);

    if (loading && !data) {
        return (
            <div className="min-h-[calc(100vh-80px)] flex items-center justify-center">
                <Loader2 className="w-10 h-10 animate-spin text-primary-500" />
            </div>
        );
    }

    return (
        <div className="min-h-[calc(100vh-80px)] p-8">
            <div className="max-w-6xl mx-auto space-y-8">
                {/* Header */}
                <div className="flex items-center justify-between">
                    <div>
                        <h1 className="text-4xl font-bold gradient-text">Usage Analytics</h1>
                        <p className="text-gray-400 mt-2">Monitor token consumption and platform performance.</p>
                    </div>
                    <button
                        onClick={fetchData}
                        className="p-3 rounded-xl bg-white/5 hover:bg-white/10 transition-colors border border-white/10"
                    >
                        <RefreshCw className={`w-5 h-5 ${loading ? 'animate-spin' : ''}`} />
                    </button>
                </div>

                {/* Stats Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="glass-card p-6 rounded-2xl space-y-4"
                    >
                        <div className="w-12 h-12 rounded-xl bg-primary-500/20 flex items-center justify-center text-primary-500">
                            <Zap className="w-6 h-6" />
                        </div>
                        <div>
                            <p className="text-sm text-gray-400">Total Tokens</p>
                            <p className="text-3xl font-bold">{data?.total_tokens.toLocaleString()}</p>
                        </div>
                        <div className="flex items-center gap-2 text-xs text-green-500">
                            <TrendingUp className="w-3 h-3" />
                            <span>12% from last week</span>
                        </div>
                    </motion.div>

                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.1 }}
                        className="glass-card p-6 rounded-2xl space-y-4"
                    >
                        <div className="w-12 h-12 rounded-xl bg-green-500/20 flex items-center justify-center text-green-500">
                            <DollarSign className="w-6 h-6" />
                        </div>
                        <div>
                            <p className="text-sm text-gray-400">Estimated Cost</p>
                            <p className="text-3xl font-bold">${data?.cost_estimate.toFixed(2)}</p>
                        </div>
                        <p className="text-xs text-gray-500">Based on $0.01 per 1k tokens</p>
                    </motion.div>

                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.2 }}
                        className="glass-card p-6 rounded-2xl space-y-4"
                    >
                        <div className="w-12 h-12 rounded-xl bg-blue-500/20 flex items-center justify-center text-blue-500">
                            <MessageSquare className="w-6 h-6" />
                        </div>
                        <div>
                            <p className="text-sm text-gray-400">Total Chats</p>
                            <p className="text-3xl font-bold">{data?.total_chats}</p>
                        </div>
                        <p className="text-xs text-gray-500">Across all users</p>
                    </motion.div>

                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.3 }}
                        className="glass-card p-6 rounded-2xl space-y-4"
                    >
                        <div className="w-12 h-12 rounded-xl bg-purple-500/20 flex items-center justify-center text-purple-500">
                            <BarChart3 className="w-6 h-6" />
                        </div>
                        <div>
                            <p className="text-sm text-gray-400">Efficiency</p>
                            <p className="text-3xl font-bold">98.4%</p>
                        </div>
                        <p className="text-xs text-gray-500">Workflow success rate</p>
                    </motion.div>
                </div>

                {/* Charts Placeholder/Mock */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    <div className="glass-card p-8 rounded-2xl h-80 flex flex-col items-center justify-center text-center space-y-4">
                        <BarChart3 className="w-12 h-12 text-gray-600" />
                        <div>
                            <h3 className="text-xl font-bold">Token Usage Over Time</h3>
                            <p className="text-gray-500 text-sm">Interactive charts coming in Phase 3</p>
                        </div>
                        <div className="flex items-end gap-2 h-20">
                            {[40, 70, 45, 90, 65, 80, 50, 85].map((h, i) => (
                                <motion.div
                                    key={i}
                                    initial={{ height: 0 }}
                                    animate={{ height: `${h}%` }}
                                    className="w-8 bg-primary-500/30 rounded-t-md hover:bg-primary-500 transition-all pointer-events-none"
                                />
                            ))}
                        </div>
                    </div>

                    <div className="glass-card p-8 rounded-2xl h-80 flex flex-col items-center justify-center text-center space-y-4">
                        <Zap className="w-12 h-12 text-gray-600" />
                        <div>
                            <h3 className="text-xl font-bold">Agent Performance</h3>
                            <p className="text-gray-500 text-sm">Success vs Failure distribution</p>
                        </div>
                        <div className="w-40 h-40 rounded-full border-[10px] border-primary-500/20 border-t-primary-500 border-r-primary-500 flex items-center justify-center relative">
                            <span className="text-2xl font-bold">75%</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
