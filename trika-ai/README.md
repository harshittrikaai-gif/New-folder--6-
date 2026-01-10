# Trika AI

Trika AI is a full-stack RAG (Retrieval Augmented Generation) and Multi-Agent orchestration platform. It features a FastAPI backend with LangChain/LangGraph and a Next.js frontend.

## Features
- **RAG Engine**: Chat with your documents (PDF, Markdown, Text).
- **Multi-Agent System**: Orchestrates research and response agents.
- **Modern UI**: Dark-themed, responsive interface built with TailwindCSS.
- **Workflow Automation**: Extensible workflow engine.

## Quick Start

1. **Clone and configure**
   ```bash
   cd trika-ai
   cp .env.example .env
   # Add your OPENAI_API_KEY to .env
   ```

   **Vector Database Configuration (.env):**
   ```env
   # Provider: chroma (default), pinecone, or sqlite (local)
   VECTOR_STORE_PROVIDER=chroma
   
   # If using Pinecone:
   PINECONE_API_KEY=your-key
   PINECONE_ENV=your-env
   PINECONE_INDEX=trika-index
   ```

2. **Run with Docker**
   ```bash
   docker-compose up --build
   ```

3. **Access**
   - Main App (via Nginx): http://localhost (Port 80)
   - Backend API: http://localhost/api/v1/docs
   - ChromaDB: Internalized (expose only for debugging if needed)

## Production Deployment

Trika AI is production-ready with:
- **Nginx Reverse Proxy**: Single entry point for frontend, backend, and WebSocket.
- **Rate Limiting**: Integrated `slowapi` to prevent abuse.
- **JWT Authentication**: Secure user sessions.
- **Multi-Stage Docker Builds**: Optimized image sizes and security.
- **Gunicorn/Uvicorn**: High-performance production server.


## Development

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Architecture

```
trika-ai/
├── backend/          # FastAPI + LangChain/LangGraph
│   ├── app/
│   │   ├── api/      # REST endpoints
│   │   ├── core/     # Config & auth
│   │   ├── engine/   # RAG & agents
│   │   ├── workflow/ # Execution engine
│   │   └── models/   # Pydantic schemas
│   └── main.py
├── frontend/         # Next.js 14
│   └── src/
│       ├── app/      # Pages
│       ├── components/
│       └── hooks/
└── docker-compose.yml
```

## License

MIT
