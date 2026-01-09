# Trika AI - Development Roadmap

This document outlines the systematic plan to evolve Trika AI into a robust, enterprise-grade platform.

## 🚀 Phase 1: Robust Foundation & Intelligence (Current Focus)

### 1. True Multi-Agent Swarm
- **Current State:** Basic LLM orchestration.
- **Goal:** Implement a fully functional LangGraph-based swarm where agents dynamically collaborate.
- **Tasks:**
    - [ ] Refactor `AgentOrchestrator` to execute the actual StateGraph.
    - [ ] Implement real "Researcher" capability using tool-calling (Mock or Real Web Search).
    - [ ] Add "Coder" agent specialized in generating code blocks.

### 2. Workflow Automation Engine
- **Current State:** UI exists; Backend Logic exists but uses in-memory storage.
- **Goal:** A persistent, visual workflow builder.
- **Tasks:**
    - [ ] Connect Frontend `WorkflowCanvas` to Backend API.
    - [ ] Migrate Workflow storage from In-Memory to SQLite Database.
    - [ ] Add real execution nodes (e.g., HTTP Request, LLM Chain).

### 3. Data Persistence & Management
- **Current State:** Chat history persists in SQLite.
- **Goal:** Complete data sovereignty.
- **Tasks:**
    - [ ] Create a "Knowledge Base" UI to manage (view/delete) uploaded RAG documents.
    - [ ] Persist Vector Store configuration (Switch between Collections).

## 🔮 Phase 2: Enhanced User Experience

### 1. Authentication & Profiles
- Add simple user accounts to segregate chat history and workflows.

### 2. Voice & Multi-Modal Inputs
- Add Voice-to-Text (Whisper) support for the Chat Interface.

### 3. Analytics Dashboard
- Visualize token usage, workflow success rates, and agent performance.

## 🛠️ Phase 3: Enterprise Readiness

- **Containerization:** Optimize Docker setup for production (Nginx reverse proxy).
- **Security:** API Key management and rate limiting.
- **Testing:** Comprehensive Unit and Integration tests.
