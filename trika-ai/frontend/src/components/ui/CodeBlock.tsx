import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { useState } from 'react';
import { Check, Copy } from 'lucide-react';

interface CodeBlockProps {
    language: string;
    value: string;
}

export const CodeBlock = ({ language, value }: CodeBlockProps) => {
    const [copied, setCopied] = useState(false);

    const copyToClipboard = () => {
        navigator.clipboard.writeText(value);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    return (
        <div className="relative group rounded-lg overflow-hidden my-4 border border-white/10">
            <div className="flex items-center justify-between px-4 py-2 bg-black/50 backdrop-blur border-b border-white/5">
                <span className="text-xs text-gray-400 uppercase font-mono">{language}</span>
                <button
                    onClick={copyToClipboard}
                    className="p-1 hover:bg-white/10 rounded transition-colors text-gray-400 hover:text-white"
                >
                    {copied ? <Check size={14} /> : <Copy size={14} />}
                </button>
            </div>
            <SyntaxHighlighter
                language={language}
                style={vscDarkPlus}
                customStyle={{
                    margin: 0,
                    background: 'rgba(0,0,0,0.3)',
                    padding: '1.5rem',
                    fontSize: '0.875rem',
                }}
                wrapLines={true}
            >
                {value}
            </SyntaxHighlighter>
        </div>
    );
};
