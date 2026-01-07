/** @type {import('next').NextConfig} */
const nextConfig = {
    output: 'standalone',
    experimental: {
        serverActions: true,
    },
    async rewrites() {
        return [
            {
                source: '/api/:path*',
                destination: 'http://backend:8000/api/v1/:path*',
            },
        ];
    },
};

module.exports = nextConfig;
