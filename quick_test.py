#!/usr/bin/env python3
"""Quick test to verify the complete setup is working"""

import os
from dotenv import load_dotenv
from google.adk import Runner
from google.adk.agents import LlmAgent
from google.adk.sessions import InMemorySessionService
from google.genai import types

# Load .env file
load_dotenv()

print("="*70)
print("🧪 QUICK INTEGRATION TEST")
print("="*70)

# Check API key
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key or api_key.startswith("MOCK"):
    print("\n❌ No valid GOOGLE_API_KEY found in .env")
    exit(1)
else:
    print(f"\n✅ GOOGLE_API_KEY loaded: {api_key[:20]}...")

# Create simple agent
agent = LlmAgent(
    name="TestAgent",
    model="gemini-2.0-flash-exp",
    description="A test agent",
    instruction="You are a helpful assistant. Answer briefly."
)

# Setup runner
session_service = InMemorySessionService()
session = session_service.create_session_sync(
    app_name="QuickTest",
    user_id="test_user",
    session_id="test_session_123"
)

runner = Runner(
    app_name="QuickTest",
    agent=agent,
    session_service=session_service
)

# Create message
message = types.Content(
    role="user",
    parts=[types.Part(text="What is 2+2? Answer in one sentence.")]
)

print("\n🚀 Sending request to Gemini...")

try:
    events = runner.run(
        user_id="test_user",
        session_id="test_session_123",
        new_message=message
    )
    
    print("\n📨 Received events:")
    response_text = None
    for event in events:
        if hasattr(event, 'content') and event.content:
            if hasattr(event.content, 'parts'):
                for part in event.content.parts:
                    if hasattr(part, 'text') and part.text:
                        response_text = part.text
    
    if response_text:
        print(f"\n✅ SUCCESS! Gemini responded:")
        print(f"   '{response_text}'")
        print("\n" + "="*70)
        print("🎉 ALL SYSTEMS WORKING!")
        print("="*70)
        print("\n✅ Compatibility issue SOLVED")
        print("✅ API key working")
        print("✅ google.genai.types integration successful")
        print("\n👉 You can now run: python runner.py")
        print("="*70)
    else:
        print("\n⚠️  No response text found")
        
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
