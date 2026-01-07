import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
    title: 'Trika AI',
    description: 'AI-powered platform with RAG, agents, and workflow automation',
    icons: {
        icon: '/favicon.ico',
    },
};

export default function RootLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <html lang="en" className="dark">
            <body className="antialiased">
                <div className="min-h-screen flex flex-col">
                    {/* Navigation */}
                    <nav className="glass-dark sticky top-0 z-50 px-6 py-4">
                        <div className="max-w-7xl mx-auto flex items-center justify-between">
                            <div className="flex items-center gap-2">
                                <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary-500 to-purple-500 flex items-center justify-center">
                                    <span className="text-white font-bold text-xl">T</span>
                                </div>
                                <span className="text-xl font-bold gradient-text">Trika AI</span>
                            </div>

                            <div className="flex items-center gap-6">
                                <a href="/" className="text-gray-300 hover:text-white transition-colors">
                                    Chat
                                </a>
                                <a href="/workflow" className="text-gray-300 hover:text-white transition-colors">
                                    Workflows
                                </a>
                            </div>
                        </div>
                    </nav>

                    {/* Main content */}
                    <main className="flex-1">
                        {children}
                    </main>
                </div>
            </body>
        </html>
    );
}
