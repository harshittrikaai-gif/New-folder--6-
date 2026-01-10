# System Architecture - OpenAI Integration

## High-Level Architecture

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                        User's Browser                         ┃
┃                   http://localhost:3000                       ┃
┃                                                               ┃
┃  ┌─────────────────────────────────────────────────────────┐ ┃
┃  │  Next.js Frontend Application                           │ ┃
┃  │                                                         │ ┃
┃  │  ┌────────────────────────────────────────────────────┐│ ┃
┃  │  │ /src/pages/chat/                                   ││ ┃
┃  │  │ • ChatWindow.tsx - Main chat UI                    ││ ┃
┃  │  │ • MessageList.tsx - Display messages               ││ ┃
┃  │  │ • ChatInput.tsx - Input form                       ││ ┃
┃  │  └────────────────────────────────────────────────────┘│ ┃
┃  │                                                         │ ┃
┃  │  ┌────────────────────────────────────────────────────┐│ ┃
┃  │  │ /src/hooks/useChat.ts                              ││ ┃
┃  │  │ • Manages chat state (messages, loading)           ││ ┃
┃  │  │ • Handles SSE stream parsing                       ││ ┃
┃  │  │ • Sends POST /api/v1/chat/                         ││ ┃
┃  │  └────────────────────────────────────────────────────┘│ ┃
┃  └─────────────────────────────────────────────────────────┘ ┃
┗━━━━━━━━━━━━━━━━━━━┬━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
                    │
                    │ HTTP POST with JSON body
                    │ ┌─────────────────────────────────────┐
                    │ │ {                                   │
                    │ │   "message": "Hello!",              │
                    │ │   "conversation_id": "optional",    │
                    │ │   "stream": true                    │
                    │ │ }                                   │
                    │ └─────────────────────────────────────┘
                    │
                    ▼
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                FastAPI Backend Server                         ┃
┃              http://localhost:8000/api/v1                     ┃
┃                                                               ┃
┃  ┌─────────────────────────────────────────────────────────┐ ┃
┃  │ /app/api/chat.py - Chat Endpoints                      │ ┃
┃  │                                                         │ ┃
┃  │ @router.post("/")                                      │ ┃
┃  │ async def chat(request: ChatRequest, db: Session):     │ ┃
┃  │     return StreamingResponse(                          │ ┃
┃  │         generate_stream(request, rag_engine,           │ ┃
┃  │                        orchestrator, db)               │ ┃
┃  │     )                                                  │ ┃
┃  └─────────────────────────────────────────────────────────┘ ┃
┃                          │                                    ┃
┃                          ▼                                    ┃
┃  ┌─────────────────────────────────────────────────────────┐ ┃
┃  │ generate_stream() - Streaming Generator                │ ┃
┃  │                                                         │ ┃
┃  │ 1. Get or create conversation in database              │ ┃
┃  │ 2. Save user message to database                       │ ┃
┃  │ 3. Retrieve conversation history                       │ ┃
┃  │ 4. Call AgentOrchestrator.stream_response()            │ ┃
┃  │ 5. Yield chunks as Server-Sent Events:                │ ┃
┃  │    data: {"type": "content", "content": "chunk"}       │ ┃
┃  │    data: {"type": "done", "conversation_id": "..."}    │ ┃
┃  │ 6. Save assistant message to database                  │ ┃
┃  └─────────────────────────────────────────────────────────┘ ┃
┃                          │                                    ┃
┃                          ▼                                    ┃
┃  ┌─────────────────────────────────────────────────────────┐ ┃
┃  │ /app/engine/agents.py - Orchestrator                   │ ┃
┃  │                                                         │ ┃
┃  │ class AgentOrchestrator:                               │ ┃
┃  │   def __init__(model_name):                            │ ┃
┃  │     self.llm = ChatOpenAI(                             │ ┃
┃  │       model=model_name,                                │ ┃
┃  │       api_key=settings.openai_api_key,                │ ┃
┃  │       streaming=True                                   │ ┃
┃  │     )                                                  │ ┃
┃  │                                                         │ ┃
┃  │   async def stream_response(message, context, history):│ ┃
┃  │     # Build system prompt with optional context        │ ┃
┃  │     # Format message history                           │ ┃
┃  │     # Stream from ChatOpenAI.astream()                 │ ┃
┃  │     async for chunk in self.llm.astream(messages):     │ ┃
┃  │       if hasattr(chunk, 'content') and chunk.content:  │ ┃
┃  │         yield chunk.content                            │ ┃
┃  └─────────────────────────────────────────────────────────┘ ┃
┃                          │                                    ┃
┃  ┌────────────────────────┼────────────────────────────────┐ ┃
┃  │                        ▼                                │ ┃
┃  │  ┌──────────────────────────────────────────────────┐  │ ┃
┃  │  │ Database (SQLAlchemy ORM)                        │  │ ┃
┃  │  │                                                  │  │ ┃
┃  │  │ • Conversation table                            │  │ ┃
┃  │  │   - id (UUID)                                   │  │ ┃
┃  │  │   - title                                       │  │ ┃
┃  │  │   - created_at, updated_at                      │  │ ┃
┃  │  │                                                  │  │ ┃
┃  │  │ • Message table                                 │  │ ┃
┃  │  │   - conversation_id (FK)                        │  │ ┃
┃  │  │   - role (user/assistant)                       │  │ ┃
┃  │  │   - content                                     │  │ ┃
┃  │  │   - created_at                                  │  │ ┃
┃  │  └──────────────────────────────────────────────────┘  │ ┃
┃  └─────────────────────────────────────────────────────────┘ ┃
┗━━━━━━━━━━━━━━━━━━━┬━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
                    │
                    │ LangChain ChatOpenAI
                    │
                    ▼
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                    OpenAI API                                 ┃
┃              https://api.openai.com/v1                        ┃
┃                                                               ┃
┃  POST /chat/completions                                      ┃
┃  {                                                           ┃
┃    "model": "gpt-4-turbo-preview",                           ┃
┃    "stream": true,                                           ┃
┃    "messages": [                                             ┃
┃      {"role": "system", "content": "You are Trika..."},      ┃
┃      {"role": "user", "content": "Hello!"}                   ┃
┃    ]                                                         ┃
┃  }                                                           ┃
┃                                                               ┃
┃  Response Stream:                                            ┃
┃  data: {"choices":[{"delta":{"content":"P"}}]}             ┃
┃  data: {"choices":[{"delta":{"content":"aris"}}]}          ┃
┃  data: {"choices":[{"delta":{"content":" is"}}]}           ┃
┃  ...                                                         ┃
┃  data: [DONE]                                                ┃
┃                                                               ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
                    │
                    │ Streamed chunks
                    │
                    ▼ (SSE - Server-Sent Events)
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                  Back to Frontend                             ┃
┃                                                               ┃
┃  data: {"type": "content", "content": "P"}                   ┃
┃  data: {"type": "content", "content": "aris is "}            ┃
┃  data: {"type": "content", "content": "the capital"}         ┃
┃  data: {"type": "content", "content": " of France."}         ┃
┃  data: {"type": "done", "conversation_id": "abc-123"}        ┃
┃                                                               ┃
┃  The frontend:                                               ┃
┃  1. Parses each SSE event                                    ┃
┃  2. Updates the assistant message in real-time              ┃
┃  3. User sees typing effect as text streams in              ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
```

## Data Flow

### Request Flow (1-4 seconds typically)

```
1. User types "Hello" and clicks Send
   ├─ Frontend creates Message object with UUID
   ├─ Displays message immediately (optimistic update)
   └─ Sends: POST /api/v1/chat/ {message: "Hello"}

2. Backend receives request
   ├─ Creates or retrieves Conversation
   ├─ Saves user Message to database
   ├─ Queries history from database
   └─ Calls AgentOrchestrator.stream_response()

3. AgentOrchestrator formats request to OpenAI
   ├─ System prompt: "You are Trika..."
   ├─ Conversation history (previous messages)
   ├─ Current message: "Hello"
   └─ Sends to OpenAI API with streaming=true

4. OpenAI starts streaming tokens
   ├─ First token arrives (~1-2 seconds)
   ├─ Subsequent tokens stream rapidly
   └─ [DONE] signal ends stream

5. Backend collects stream and sends to frontend
   ├─ Each chunk as SSE: data: {...}\n\n
   ├─ Frontend parses and updates UI
   └─ Full response saved to database

6. Chat appears complete to user
   ├─ Last token received
   ├─ Conversation saved
   └─ User can type next message
```

## Key Technologies

```
┌─────────────────────────────────────────────┐
│           Technology Stack                  │
├─────────────────────────────────────────────┤
│ Frontend:                                   │
│ • Next.js 14 (React framework)              │
│ • TypeScript                                │
│ • TailwindCSS                               │
│                                             │
│ Backend:                                    │
│ • FastAPI (Python web framework)            │
│ • SQLAlchemy (ORM)                          │
│ • Pydantic (validation)                     │
│                                             │
│ AI Integration:                             │
│ • LangChain (AI framework)                  │
│ • LangChain OpenAI (ChatOpenAI)             │
│ • OpenAI API (gpt-4-turbo-preview)          │
│                                             │
│ Optional Features:                          │
│ • ChromaDB (vector store for RAG)           │
│ • LangGraph (agent orchestration)           │
│ • Anthropic (Claude models)                 │
│                                             │
│ Database:                                   │
│ • SQLite (local development)                │
│ • PostgreSQL (production)                   │
└─────────────────────────────────────────────┘
```

## Configuration

```python
# app/core/config.py
Settings = {
    "app_name": "Trika AI",
    "debug": False,
    "api_prefix": "/api/v1",
    
    # OpenAI Configuration
    "openai_api_key": "${OPENAI_API_KEY}",
    "openai_model": "gpt-4-turbo-preview",
    
    # Anthropic Configuration (Optional)
    "anthropic_api_key": "${ANTHROPIC_API_KEY}",
    "anthropic_model": "claude-3-sonnet-20240229",
    
    # Vector Store (Optional)
    "vector_store_provider": "chroma",
    "chroma_host": "chromadb",
    "chroma_port": 8000,
    "chroma_collection": "trika_documents",
    
    # CORS
    "cors_origins": ["http://localhost:3000", "http://localhost:3001"],
}
```

## Streaming Protocol

### Server-Sent Events Format

```
# Content chunk
data: {"type": "content", "content": "The capital of France"}
data: {"type": "content", "content": " is Paris."}

# Sources (if RAG results exist)
data: {"type": "sources", "content": [...]}

# End of stream
data: {"type": "done", "conversation_id": "abc-123"}

# Error
data: {"type": "error", "content": "API rate limit exceeded"}
```

### Frontend Parsing

```typescript
const reader = response.body?.getReader();
const decoder = new TextDecoder();

while (reader) {
    const { done, value } = await reader.read();
    if (done) break;

    const chunk = decoder.decode(value);
    const lines = chunk.split('\n').filter(line => line.startsWith('data: '));
    
    for (const line of lines) {
        const data = JSON.parse(line.slice(6));
        
        if (data.type === 'content') {
            // Append to message
            setMessage(prev => prev + data.content);
        } else if (data.type === 'done') {
            // Save conversation ID
            setConversationId(data.conversation_id);
        }
    }
}
```

## Error Handling

```
User Input
    │
    ▼
  Validation ──Fail──> Return 422 (Unprocessable Entity)
    │
    ▼
  Save to DB ──Fail──> Return 500 (Internal Server Error)
    │
    ▼
  Call OpenAI ──Fail──> Yield error SSE, Log error
    │
    ▼
  Stream Response ──Fail──> Fallback to ainvoke() (non-streaming)
    │
    ▼
  Stream Chunks ──Fail──> Send error chunk, stop stream
    │
    ▼
  Save Response ──Fail──> User sees response but not saved (recoverable)
```

---

**This architecture enables:**
- ✅ Real-time streaming responses
- ✅ Conversation persistence
- ✅ Multi-turn conversations
- ✅ Scalable microservices
- ✅ Easy to add new models or features
- ✅ Robust error handling
