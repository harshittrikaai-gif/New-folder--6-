# OpenAI Integration Setup Guide

Your backend is now configured to respond to chat messages using the OpenAI API. Here's how to get everything running:

## 1. Backend Setup

### Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### Configure Environment Variables
Make sure your `.env` file contains:
```env
OPENAI_API_KEY=your-openai-api-key-here
OPENAI_MODEL=gpt-4-turbo-preview  # or gpt-3.5-turbo
```

The config.py already loads these from the `.env` file.

### Start the Backend Server
```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
🚀 Starting Trika AI
Uvicorn running on http://0.0.0.0:8000
```

## 2. Frontend Setup

In a new terminal:
```bash
cd frontend
npm install
npm run dev
```

The frontend will be available at `http://localhost:3000`

## 3. Test the Integration

### Test with the provided test script
```bash
cd backend
python test_openai_integration.py
```

This will test:
- ✅ Streaming chat responses
- ✅ Conversation history retrieval
- ✅ Error handling

### Or test manually via the frontend
1. Open http://localhost:3000 in your browser
2. Go to the Chat page
3. Type a message and send it
4. You should see a real-time streaming response from OpenAI

## How It Works

The chat flow is as follows:

```
Frontend (Next.js)
    ↓
POST /api/v1/chat/
    ↓
generate_stream() function
    ↓
AgentOrchestrator.stream_response()
    ↓
ChatOpenAI.astream() [OpenAI API]
    ↓
Server-Sent Events (SSE) back to frontend
    ↓
Frontend displays streaming response in real-time
```

### Key Components:

1. **ChatOpenAI** (`app/engine/agents.py`)
   - Initializes with your OpenAI API key
   - Handles streaming via `astream()` method
   - Falls back to `ainvoke()` if streaming fails

2. **AgentOrchestrator.stream_response()** 
   - Converts chat history to OpenAI message format
   - Adds system prompt with optional context
   - Yields chunks as they arrive from OpenAI

3. **Chat API** (`app/api/chat.py`)
   - Accepts chat requests with conversation history
   - Saves messages to database for persistence
   - Streams responses back via Server-Sent Events

4. **Frontend Hook** (`frontend/src/hooks/useChat.ts`)
   - Handles SSE stream parsing
   - Updates UI in real-time as chunks arrive
   - Manages conversation state

## Supported Models

By default, the system uses:
- **OpenAI**: `gpt-4-turbo-preview`
- **Anthropic**: `claude-3-sonnet-20240229`

You can override the model in requests:
```json
{
  "message": "Hello!",
  "model": "gpt-3.5-turbo",
  "stream": true
}
```

## Troubleshooting

### "Invalid API Key" Error
- Check your OPENAI_API_KEY in the `.env` file
- Make sure the key hasn't been rotated in your OpenAI account
- Keys should start with `sk-`

### Streaming Not Working
- Check that your OpenAI API account has API access enabled
- Ensure you have sufficient API credits
- Check the server logs for detailed error messages

### Connection Refused
- Ensure backend is running on port 8000
- Check if port 8000 is not blocked by a firewall
- Try: `netstat -ano | findstr :8000` (Windows) to see what's using the port

### Response is Slow
- This is normal for cold starts
- Once warmed up, streaming responses are typically < 1 second to first token
- Check your OpenAI API rate limits

## Environment Variables Summary

```env
# OpenAI Configuration
OPENAI_API_KEY=sk-...                    # Your OpenAI API key
OPENAI_MODEL=gpt-4-turbo-preview        # Model to use

# Anthropic Configuration (optional)
ANTHROPIC_API_KEY=sk-ant-...             # Optional: for Claude models
ANTHROPIC_MODEL=claude-3-sonnet-20240229

# Vector Store (for RAG features)
VECTOR_STORE_PROVIDER=chroma            # chroma or pinecone

# ChromaDB Settings
CHROMA_HOST=chromadb                    # ChromaDB server host
CHROMA_PORT=8000                        # ChromaDB server port
CHROMA_COLLECTION=trika_documents       # Collection name

# Application
DEBUG=false
APP_NAME=Trika AI
API_PREFIX=/api/v1
```

## Next Steps

1. **Add Conversation Context**: Messages are automatically saved to the database with conversation IDs
2. **Add File Upload & RAG**: Documents can be uploaded and used as context
3. **Add Tool Use**: Extend AgentOrchestrator to use function calling
4. **Add Memory**: Implement conversation summarization for long chats

Happy chatting! 🚀
