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

2. **Run with Docker**
   ```bash
   docker-compose up --build
   ```

3. **Access**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000/docs
   - ChromaDB: http://localhost:8001

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
