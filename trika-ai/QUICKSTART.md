# 🚀 Quick Start Guide - OpenAI Integration

## 30 Second Setup

### 1️⃣ Backend
```bash
cd backend
pip install -r requirements.txt
# Edit .env and add your OpenAI API key
OPENAI_API_KEY=sk-your-key-here
# Start the server
uvicorn main:app --reload
```

### 2️⃣ Frontend
```bash
cd frontend
npm install
npm run dev
```

### 3️⃣ Chat!
- Open http://localhost:3000
- Go to Chat page
- Send a message
- ✅ You'll see streaming responses from OpenAI!

---

## What Just Happened?

You now have a full-stack AI chat application with:

```
┌─────────────────────────────────────────┐
│  Frontend (Next.js)                     │
│  • Real-time chat UI                    │
│  • Supports file upload                 │
│  • Conversation history                 │
└────────────┬────────────────────────────┘
             │
        REST API with Server-Sent Events
             │
┌────────────▼────────────────────────────┐
│  Backend (FastAPI)                      │
│  • OpenAI API integration                │
│  • Message persistence                  │
│  • RAG support (optional)                │
│  • Async streaming                      │
└────────────┬────────────────────────────┘
             │
┌────────────▼────────────────────────────┐
│  OpenAI gpt-4-turbo-preview             │
│  • Real-time text generation            │
│  • Token streaming                      │
│  • Memory of conversation                │
└─────────────────────────────────────────┘
```

## Core Changes

**File Modified**: `backend/app/engine/agents.py`
- Simplified `stream_response()` method
- Direct OpenAI API streaming via `ChatOpenAI.astream()`
- Better error handling

**Key Feature**: All messages are saved to database automatically

## Test It

```bash
# Run the integration test
cd backend
python test_openai_integration.py
```

Expected output:
```
🚀 Testing Chat Stream...
📥 Streaming Response:
Paris is the capital of France...
✅ Conversation ID: {conversation-id}
```

## Common Commands

```bash
# Start backend with auto-reload
uvicorn main:app --reload

# Start frontend with hot reload  
npm run dev

# Run tests
python test_openai_integration.py

# Format Python code
black app/

# Run type checking
mypy app/
```

## Environment Variables

Create `backend/.env`:
```env
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4-turbo-preview
DEBUG=false
```

## Example API Call

```bash
curl -X POST http://localhost:8000/api/v1/chat/ \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is the capital of France?",
    "stream": true
  }'
```

Response (Server-Sent Events):
```
data: {"type": "content", "content": "Paris"}
data: {"type": "content", "content": " is the capital"}
data: {"type": "content", "content": " of France."}
data: {"type": "done", "conversation_id": "abc-123"}
```

## What's Included

✅ OpenAI API integration with streaming
✅ Conversation history in database
✅ Multi-turn conversations
✅ Error handling with fallbacks
✅ Support for multiple models
✅ Real-time frontend updates
✅ Comprehensive test suite
✅ Full documentation

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Invalid API Key" | Check OPENAI_API_KEY in .env |
| Connection refused | Ensure backend runs on port 8000 |
| Slow responses | Normal first time, check API rate limits |
| No streaming | Verify your OpenAI account has API access |

## Next Features

- [ ] Upload documents for RAG context
- [ ] Web search integration
- [ ] Custom system prompts
- [ ] Conversation branching
- [ ] Export conversations
- [ ] Rate limiting
- [ ] API cost tracking

## Support

For detailed setup: See [OPENAI_SETUP.md](OPENAI_SETUP.md)
For technical details: See [INTEGRATION_SUMMARY.md](INTEGRATION_SUMMARY.md)

---

**Status**: ✅ Production Ready
**Last Updated**: January 9, 2026
