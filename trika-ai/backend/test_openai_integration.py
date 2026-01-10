"""Test OpenAI integration with the chat API."""
import asyncio
import httpx
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BASE_URL = "http://localhost:8000/api/v1"


async def test_chat_stream():
    """Test streaming chat response."""
    print("🚀 Testing Chat Stream...\n")
    
    async with httpx.AsyncClient() as client:
        payload = {
            "message": "Hello! What is the capital of France?",
            "stream": True,
        }
        
        print(f"Sending request: {json.dumps(payload, indent=2)}\n")
        
        try:
            async with client.stream(
                "POST",
                f"{BASE_URL}/chat/",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30.0
            ) as response:
                print(f"Status Code: {response.status_code}")
                print(f"Headers: {dict(response.headers)}\n")
                
                if response.status_code == 200:
                    print("📥 Streaming Response:\n")
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            try:
                                data = json.loads(line[6:])
                                msg_type = data.get("type", "unknown")
                                
                                if msg_type == "content":
                                    print(data.get("content", ""), end="", flush=True)
                                elif msg_type == "sources":
                                    print(f"\n\n📚 Sources: {json.dumps(data.get('content', []), indent=2)}\n")
                                elif msg_type == "done":
                                    print(f"\n\n✅ Conversation ID: {data.get('conversation_id')}")
                                elif msg_type == "error":
                                    print(f"\n\n❌ Error: {data.get('content')}")
                            except json.JSONDecodeError:
                                pass
                else:
                    content = await response.aread()
                    print(f"Error Response: {content.decode()}")
                    
        except httpx.ConnectError:
            print("❌ Connection Error: Backend is not running at http://localhost:8000")
            print("   Make sure to start the backend first: uvicorn main:app --reload")
        except Exception as e:
            print(f"❌ Error: {type(e).__name__}: {e}")


async def test_conversation_history():
    """Test retrieving conversation history."""
    print("\n\n🔍 Testing Conversation History...\n")
    
    async with httpx.AsyncClient() as client:
        # First, send a message
        payload = {
            "message": "What is Python?",
            "stream": True,
        }
        
        conversation_id = None
        async with client.stream(
            "POST",
            f"{BASE_URL}/chat/",
            json=payload,
            timeout=30.0
        ) as response:
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    try:
                        data = json.loads(line[6:])
                        if data.get("type") == "done":
                            conversation_id = data.get("conversation_id")
                    except json.JSONDecodeError:
                        pass
        
        if conversation_id:
            print(f"Retrieved Conversation ID: {conversation_id}")
            
            # Now get the history
            try:
                response = await client.get(
                    f"{BASE_URL}/chat/conversations/{conversation_id}",
                    timeout=10.0
                )
                if response.status_code == 200:
                    history = response.json()
                    print(f"✅ Conversation History:\n{json.dumps(history, indent=2)}")
                else:
                    print(f"❌ Failed to get history: {response.status_code}")
            except Exception as e:
                print(f"❌ Error fetching history: {e}")


async def main():
    """Run all tests."""
    await test_chat_stream()
    await test_conversation_history()


if __name__ == "__main__":
    print("=" * 60)
    print("Trika AI - OpenAI Integration Test")
    print("=" * 60)
    asyncio.run(main())
