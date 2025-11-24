# runner.py

import os
from dotenv import load_dotenv
from google.adk import Runner
from google.adk.sessions import Session, InMemorySessionService
from google.genai import types  # Use google.genai.types, not google.generativeai.protos

# Load environment variables from .env file
load_dotenv()

# 1. Import the main agent
from agents.root_agent import ROOT_AGENT 

# 2. Setup API Keys and Environment
def setup_environment():
    """Sets placeholder API keys if they are not already set."""
    print("--- Environment Setup ---")
    
    # Google AI API Key (required for Gemini models)
    if not os.getenv("GOOGLE_API_KEY"):
        print("⚠️  WARNING: GOOGLE_API_KEY not set!")
        print("   Get your API key from: https://aistudio.google.com/app/apikey")
        print("   Set it with: export GOOGLE_API_KEY='your-key-here'")
        os.environ["GOOGLE_API_KEY"] = "MOCK_GOOGLE_KEY_FOR_TESTING"
    else:
        print("✓ GOOGLE_API_KEY is set")
    
    # Amadeus API credentials (for travel tools)
    # WARNING: Replace these placeholders with your actual Amadeus keys 
    # and ensure they are loaded securely (e.g., from a .env file).
    if not os.getenv("AMADEUS_API_KEY"):
        os.environ["AMADEUS_API_KEY"] = "MOCK_AMADEUS_KEY_FOR_TESTING"
    if not os.getenv("AMADEUS_API_SECRET"):
        os.environ["AMADEUS_API_SECRET"] = "MOCK_AMADEUS_SECRET_FOR_TESTING"
    print("✓ Amadeus environment variables set (using mock/test values).")
    print("-------------------------")

# 3. Define the main execution function
def run_trip_planner():
    """Initializes the runner and executes the trip planner agent."""
    
    # Ensure environment variables are set before tools are initialized
    setup_environment()
    
    # The user's request. This must contain all parameters the specialized 
    # agents need (cities, dates, budget, duration).
    user_prompt = (
        "Plan a 4-day trip to Paris, France, arriving on 2026-06-10 and departing 2026-06-14. "
        "I will be traveling alone (1 adult). My origin airport is JFK. "
        "The maximum I want to spend on a hotel is $250 per night."
    )

    print(f"\n✅ Starting Trip Planner for request:\n> {user_prompt}\n")
    
    # Initialize the ADK Runner with an in-memory session service
    session_service = InMemorySessionService()
    
    # Create a session first
    app_name = "TripPlanner"
    user_id = "user123"
    session_id = "session123"
    
    session = session_service.create_session_sync(
        app_name=app_name,
        user_id=user_id,
        session_id=session_id
    )
    
    runner = Runner(
        app_name=app_name,
        agent=ROOT_AGENT,
        session_service=session_service
    )
    
    # Run the session with the user's prompt
    print("🚀 Executing Multi-Agent Pipeline...")
    
    # The Runner manages the entire workflow: 
    # ROOT_AGENT calls TRIP_PLANNER_TOOL 
    # which executes PARALLEL_PLANNER and then ITINERARY_AGENT.
    try:
        # Create a proper Content message using google.genai.types
        message = types.Content(
            role="user",
            parts=[types.Part(text=user_prompt)]
        )
        
        # Run the agent with user_id and session_id
        events = runner.run(
            user_id=user_id,
            session_id=session_id,
            new_message=message
        )
        
        # Process events and collect the final response
        final_text = None
        for event in events:
            print(f"Event: {type(event).__name__}")
            if hasattr(event, 'content') and event.content:
                if hasattr(event.content, 'parts'):
                    for part in event.content.parts:
                        if hasattr(part, 'text'):
                            final_text = part.text
                            
        # Display the final synthesis from the ROOT_AGENT
        print("\n--- 🏆 Final Trip Plan Summary ---")
        if final_text:
            print(final_text)
        else:
            print("No response generated")
        print("---------------------------------")
        
        # Optional: Print the final state to see all collected data
        # print("\n--- 🧠 Final Session State (Data Collected) ---")
        # print(session.state.get_value("flight_options"))
        # print(session.state.get_value("hotel_options"))
        # print(session.state.get_value("itinerary_plan"))
        # print("----------------------------------------------")
        
    except Exception as e:
        print(f"\n❌ An error occurred during the execution: {e}")
        # This often happens if the API keys are invalid or the model 
        # cannot correctly extract parameters for the tool call.

if __name__ == "__main__":
    run_trip_planner()