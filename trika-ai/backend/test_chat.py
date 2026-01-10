#!/usr/bin/env python
import asyncio
import sys
from app.engine.agents import AgentOrchestrator

async def test():
    try:
        print("Initializing AgentOrchestrator...", file=sys.stderr)
        orch = AgentOrchestrator()
        print("AgentOrchestrator initialized successfully", file=sys.stderr)
        
        print("Streaming response for 'Hello'...", file=sys.stderr)
        async for chunk in orch.stream_response('Hello'):
            print(chunk, end='', flush=True)
        print("\nDone!", file=sys.stderr)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test())
