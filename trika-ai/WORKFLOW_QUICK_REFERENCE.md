# Workflow System - Quick Reference

## 🚀 Quick Start

### Run the System
```bash
# Terminal 1: Backend
cd backend
uvicorn main:app --reload

# Terminal 2: Frontend  
cd frontend
npm run dev
```

### Access Workflow Builder
Open: http://localhost:3000/workflow

---

## 📋 API Endpoints

### List Workflows
```bash
GET /api/v1/workflows/
```

### Create Workflow
```bash
POST /api/v1/workflows/
{
  "name": "My Workflow",
  "description": "Optional description"
}
```

### Get Workflow
```bash
GET /api/v1/workflows/{workflow_id}
```

### Update Workflow
```bash
PUT /api/v1/workflows/{workflow_id}
{
  "name": "Updated Name",
  "nodes": [...],
  "edges": [...],
  "variables": {}
}
```

### Execute Workflow
```bash
POST /api/v1/workflows/{workflow_id}/execute
{
  "topic": "AI",
  "count": 5
}
```

### Get Execution Status
```bash
GET /api/v1/workflows/executions/{execution_id}
```

### List Executions
```bash
GET /api/v1/workflows/{workflow_id}/executions
```

### WebSocket Monitoring
```
ws://localhost:8000/ws/workflows/{execution_id}
```

---

## 🔧 Node Types & Parameters

### Input Node
```json
{
  "type": "input",
  "label": "Input",
  "params": {}
}
```

### LLM Node
```json
{
  "type": "llm",
  "label": "Generate Content",
  "params": {
    "prompt": "Write about {topic}",
    "model": "gpt-4-turbo-preview",
    "temperature": 0.7,
    "max_tokens": 1000
  }
}
```

### HTTP Node
```json
{
  "type": "http",
  "label": "Call API",
  "params": {
    "method": "POST",
    "url": "https://api.example.com/endpoint",
    "headers": {"Authorization": "Bearer token"},
    "body": {"data": "{input}"}
  }
}
```

### Code Node
```json
{
  "type": "code",
  "label": "Process",
  "params": {
    "code": "output = len(input.get('text', ''))"
  }
}
```

### Transform Node
```json
{
  "type": "transform",
  "label": "Extract",
  "params": {
    "type": "extract",
    "key": "result"
  }
}
```

**Transform Types**:
- `passthrough` - Return as-is
- `extract` - Get single field
- `merge` - Combine objects
- `template` - Format string
- `map` - Rename fields
- `filter` - Keep specific keys

### Condition Node
```json
{
  "type": "condition",
  "label": "Check",
  "params": {
    "condition": "len(input.get('text', '')) > 100"
  }
}
```

### RAG Node
```json
{
  "type": "rag",
  "label": "Search Docs",
  "params": {
    "query": "What is {topic}?",
    "k": 5
  }
}
```

### Search Node
```json
{
  "type": "search",
  "label": "Web Search",
  "params": {
    "query": "Search for {term}",
    "num_results": 5
  }
}
```

### Output Node
```json
{
  "type": "output",
  "label": "Result",
  "params": {
    "output_key": "final_result"
  }
}
```

---

## 📊 Node Output Format

All nodes return:
```json
{
  "success": true/false,
  "output": "any value",
  "error": "error message if failed",
  ...
}
```

---

## 🔌 WebSocket Events

### Start Event
```json
{
  "type": "start",
  "timestamp": "2026-01-09T...",
  "workflow_id": "...",
  "workflow_name": "My Workflow"
}
```

### Node Completed Event
```json
{
  "type": "node_completed",
  "timestamp": "2026-01-09T...",
  "node_id": "n1",
  "output": {
    "success": true,
    "output": "Generated text"
  }
}
```

### Completed Event
```json
{
  "type": "completed",
  "timestamp": "2026-01-09T...",
  "output": {...},
  "node_outputs": {
    "n1": {...},
    "n2": {...}
  }
}
```

### Failed Event
```json
{
  "type": "failed",
  "timestamp": "2026-01-09T...",
  "error": "API timeout"
}
```

---

## 💡 Template Variables

Use `{variable}` syntax in any text field:

```
Prompt: "Write about {topic} in {tone}"
URL: "https://api.example.com?q={query}"
Code: "for item in {items}: process(item)"

Executes with: {"topic": "AI", "tone": "casual", ...}
```

---

## 🧪 Example Workflows

### Simple Q&A
```
Input → LLM → Output
```

### Multi-step Processing
```
Input → Code → Transform → LLM → Output
```

### Conditional Logic
```
Input → Condition → LLM (branch A)
                 → HTTP (branch B)
```

### API Integration
```
Input → HTTP (fetch data) → Transform → Output
```

### Content + Search
```
Input → RAG (search docs) → LLM (with context) → Output
```

---

## 🐛 Debugging

### Check Backend Logs
```
Watch console where uvicorn is running
Look for: [ERROR] or [EXCEPTION]
```

### Monitor WebSocket
```
Open Browser DevTools > Network > WS
Watch messages in real-time
```

### Query Database
```
SQLite: Open .db file with SQLite Browser
Check: workflows table for saved workflows
Check: workflow_executions table for history
```

### Test Node Individually
```bash
curl -X POST http://localhost:8000/api/v1/workflows/{id}/execute \
  -H "Content-Type: application/json" \
  -d '{"test_var": "value"}'
```

---

## 📈 Common Patterns

### Fan-out Pattern
```
Input
  ├─ Process 1
  ├─ Process 2
  └─ Process 3
     └─ Merge Results → Output
```

### Sequential Processing
```
Input → Step1 → Step2 → Step3 → Output
```

### Try-Catch Pattern
```
Input → Operation
         ├─ Success → Output
         └─ Error → Fallback
```

### Data Transformation Pipeline
```
Input → Extract → Clean → Validate → Output
```

---

## ⚙️ Configuration

### Set Default Model
Edit `backend/app/core/config.py`:
```python
openai_model: str = "gpt-4-turbo-preview"
```

### Set API Keys
Edit `backend/.env`:
```env
OPENAI_API_KEY=sk-...
```

### Change DB
Edit `backend/app/db/database.py`:
```python
# SQLite (default)
SQLALCHEMY_DATABASE_URL = "sqlite:///./workflows.db"

# PostgreSQL
SQLALCHEMY_DATABASE_URL = "postgresql://user:pass@localhost/db"
```

---

## 🚨 Troubleshooting

| Problem | Solution |
|---------|----------|
| "Workflow not found" | Check workflow ID is correct |
| WebSocket won't connect | Ensure backend is running |
| LLM node fails | Check OpenAI API key in .env |
| HTTP node fails | Verify URL and headers |
| Code node syntax error | Check Python syntax carefully |
| Condition always false | Use correct variable names |

---

## 📚 Full Documentation

- **WORKFLOW_GUIDE.md** - Complete guide
- **WORKFLOW_IMPLEMENTATION.md** - Implementation details
- **API Docs** - http://localhost:8000/docs

---

## 🎯 Quick Workflow Example

### Step 1: Create
```bash
curl -X POST http://localhost:8000/api/v1/workflows/ \
  -H "Content-Type: application/json" \
  -d '{"name":"Article Generator"}'
# Returns: {"id": "workflow-123", ...}
```

### Step 2: Configure
```bash
curl -X PUT http://localhost:8000/api/v1/workflows/workflow-123 \
  -H "Content-Type: application/json" \
  -d '{
    "nodes": [
      {"id":"1","config":{"type":"input","label":"Input","params":{},"position":{"x":0,"y":0}}},
      {"id":"2","config":{"type":"llm","label":"Generate","params":{"prompt":"Write about {topic}","model":"gpt-4"},"position":{"x":300,"y":0}}},
      {"id":"3","config":{"type":"output","label":"Output","params":{},"position":{"x":600,"y":0}}}
    ],
    "edges": [
      {"id":"e1-2","source":"1","target":"2"},
      {"id":"e2-3","source":"2","target":"3"}
    ]
  }'
```

### Step 3: Execute
```bash
curl -X POST http://localhost:8000/api/v1/workflows/workflow-123/execute \
  -H "Content-Type: application/json" \
  -d '{"topic":"Artificial Intelligence"}'
# Returns: {"id": "execution-456", "status": "running", ...}
```

### Step 4: Monitor
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/workflows/execution-456');
ws.onmessage = (e) => {
  const update = JSON.parse(e.data);
  console.log(`Event: ${update.type}`, update);
};
```

---

**Everything is ready to use! 🚀**
