import asyncio
import pytest
from app.engine.agents import AgentOrchestrator
from langchain_core.messages import HumanMessage

@pytest.mark.asyncio
async def test_router_chat_intent():
    orchestrator = AgentOrchestrator()
    intent = orchestrator._determine_intent("Hello, how are you?")
    assert intent == "chat"

@pytest.mark.asyncio
async def test_router_research_intent():
    orchestrator = AgentOrchestrator()
    intent = orchestrator._determine_intent("Search for the latest news on AI")
    assert intent == "research"

@pytest.mark.asyncio
async def test_router_code_intent():
    orchestrator = AgentOrchestrator()
    intent = orchestrator._determine_intent("Write a python script to sort a list")
    assert intent == "code"

@pytest.mark.asyncio
async def test_stream_response_fast_path():
    orchestrator = AgentOrchestrator()
    # This should trigger the fast path (simple astream)
    chunks = []
    async for chunk in orchestrator.stream_response("Say 'Fast Path'"):
        chunks.append(chunk)
    
    assert len(chunks) > 0
    full_text = "".join(chunks)
    assert "Fast Path" in full_text or len(full_text) > 0

@pytest.mark.asyncio
async def test_graph_execution_code():
    orchestrator = AgentOrchestrator()
    # This should trigger the smart path (graph.ainvoke)
    # We mock the response if needed, but for now we'll just try to run it
    # Note: This requires a valid API key in .env
    chunks = []
    async for chunk in orchestrator.stream_response("Write a simple hello world in python"):
        chunks.append(chunk)
    
    assert len(chunks) > 0
    full_text = "".join(chunks)
    assert "print" in full_text.lower() or "hello" in full_text.lower()
