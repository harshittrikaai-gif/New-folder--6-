import asyncio
import os
import sys

# Add current directory to path
sys.path.append(os.getcwd())

from app.engine.agents import AgentOrchestrator

async def demo_intent(orchestrator, message, label):
    intent = orchestrator._determine_intent(message)
    print(f"\n--- {label} ---")
    print(f"Query: '{message}'")
    print(f"Detected Intent: {intent}")
    
    print("Response: ", end="", flush=True)
    try:
        async for chunk in orchestrator.stream_response(message):
            print(chunk, end="", flush=True)
    except Exception as e:
        if "401" in str(e) or "Authentication" in str(e):
            print(f"\n[API Error]: Authentication failed (401). Please check your OPENAI_API_KEY.")
        else:
            print(f"\n[Error]: {e}")
    print("\n" + "="*40)

async def main():
    print("🚀 Starting Trika AI Swarm Demonstration")
    orchestrator = AgentOrchestrator()
    
    # 1. Fast Path (Chat)
    await demo_intent(orchestrator, "Hi Trika, explain who you are in one sentence.", "FAST PATH (CHAT)")
    
    # 2. Smart Path (Coder)
    await demo_intent(orchestrator, "Write a Python function to check for prime numbers.", "SMART PATH (CODER)")
    
    # 3. Smart Path (Research)
    await demo_intent(orchestrator, "Search for the latest breakthroughs in agentic AI from Jan 2026.", "SMART PATH (RESEARCH)")

if __name__ == "__main__":
    asyncio.run(main())
