import asyncio
import os
import sys

# Add current directory to path
sys.path.append(os.getcwd())

from app.engine.agents import AgentOrchestrator

async def main():
    orchestrator = AgentOrchestrator()
    
    # Test cases: (Input, Expected Intent)
    test_cases = [
        ("Hello!", "chat"),
        ("Search for AI agents", "research"),
        ("Write a python script", "code"),
    ]
    
    for msg, expected in test_cases:
        intent = orchestrator._determine_intent(msg)
        print(f"Message: {msg} -> Intent: {intent} (Expected: {expected})")
        if intent != expected:
            print(f"FAILED: Expected {expected} but got {intent}")
    
    # Test streaming (Fast Path)
    print("\nTesting Fast Path (Chat)...")
    async for chunk in orchestrator.stream_response("Say 'Fast Path'"):
        print(chunk, end="", flush=True)
    print("\n--- Done ---")

    # Test Smart Path (Code)
    print("\nTesting Smart Path (Code)...")
    async for chunk in orchestrator.stream_response("Write a simple hello world in python"):
        print(chunk, end="", flush=True)
    print("\n--- Done ---")

if __name__ == "__main__":
    asyncio.run(main())
