# Simple test to verify ADK setup

import os
from google.adk import Runner, Agent
from google.adk.agents import LlmAgent
from google.adk.sessions import InMemorySessionService
from google.genai import types  # Use google.genai.types

# Set up Google AI API key (you need to provide your own)
# Get your API key from https://aistudio.google.com/app/apikey
API_KEY = os.getenv("GOOGLE_API_KEY", "YOUR_API_KEY_HERE")
os.environ["GOOGLE_API_KEY"] = API_KEY

# Create a simple agent
simple_agent = LlmAgent(
    name="TestAgent",
    model="gemini-2.0-flash-exp",
    description="A simple test agent",
    instruction="You are a helpful assistant. Answer the user's question briefly."
)

# Create session service
session_service = InMemorySessionService()

# Create runner
app_name = "SimpleTest"
user_id = "test_user"
session_id = "test_session"

# Create session
session = session_service.create_session_sync(
    app_name=app_name,
    user_id=user_id,
    session_id=session_id
)

runner = Runner(
    app_name=app_name,
    agent=simple_agent,
    session_service=session_service
)

# Create message - use google.genai.types
message = types.Content(
    role="user",
    parts=[types.Part(text="What is 2+2?")]
)

print("Running simple test...")

try:
    events = runner.run(
        user_id=user_id,
        session_id=session_id,
        new_message=message
    )
    
    for event in events:
        print(f"Event: {type(event).__name__}")
        if hasattr(event, 'content') and event.content:
            print(f"Content: {event.content}")
            
    print("✓ Test successful!")
    
except Exception as e:
    print(f"✗ Test failed: {e}")
    import traceback
    traceback.print_exc()
