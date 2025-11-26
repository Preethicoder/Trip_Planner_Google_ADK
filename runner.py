# runner.py

import os
from dotenv import load_dotenv
from google.adk import Runner
from google.adk.sessions import Session, InMemorySessionService
from google.genai import types  # Use google.genai.types, not google.generativeai.protos

# Load environment variables from .env file
load_dotenv()

# 1. Import the main agents
from agents.root_agent import ROOT_AGENT
from agents.itinerary_agent import ITINERARY_SEARCH_AGENT 

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
        "Plan a 4-day trip to Basel, Switzerland, arriving on 2026-06-10 and departing 2026-06-14. "
        "I will be traveling with husband and my kid who is 5 years old  (2 adults and 1 kid). My origin airport is Chennai. "
        "The maximum I want to spend on a hotel is 300 Euros per night."
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
        tool_calls_detected = []
        
        for event in events:
            event_type = type(event).__name__
            print(f"📨 Event: {event_type}")
            
            # Print event details for debugging
            if hasattr(event, 'content') and event.content:
                print(f"   Content received: {event.content}")
                
                if hasattr(event.content, 'parts'):
                    for part in event.content.parts:
                        # Check for text
                        if hasattr(part, 'text') and part.text:
                            final_text = part.text
                            print(f"   ✓ Text part found")
                        
                        # Check for function calls
                        if hasattr(part, 'function_call') and part.function_call:
                            func_call = part.function_call
                            tool_calls_detected.append(func_call.name)
                            print(f"   🔧 Function call: {func_call.name}")
                            print(f"      Args: {func_call.args}")
                        
                        # Check for function responses
                        if hasattr(part, 'function_response') and part.function_response:
                            func_resp = part.function_response
                            print(f"   ✅ Function response from: {func_resp.name}")
                            print(f"      Result: {func_resp.response}")
        
        # 🔍 VALIDATION: Check if specialized tools were called
        print("\n" + "=" * 80)
        print("🔍 TOOL EXECUTION VALIDATION")
        print("=" * 80)
        print(f"Tool calls detected: {tool_calls_detected}")
        
        flight_tool_used = any('flight' in name.lower() for name in tool_calls_detected)
        hotel_tool_used = any('hotel' in name.lower() for name in tool_calls_detected)
        
        print(f"✈️  Flight Search Tool: {'✅ CALLED' if flight_tool_used else '❌ NOT CALLED'}")
        print(f"🏨 Hotel Search Tool: {'✅ CALLED' if hotel_tool_used else '❌ NOT CALLED'}")
        
        if not flight_tool_used or not hotel_tool_used:
            print("\n⚠️  WARNING: Some specialized tools were not invoked!")
            print("   This means the LLM generated estimates instead of using real API data.")
            print("   The response may contain fabricated information.")
        print("=" * 80 + "\n")
        
        # 🧠 DEBUG: Print session state to see what data was stored
        print("\n" + "=" * 80)
        print("🧠 SESSION STATE DEBUG")
        print("=" * 80)
        
        # Get the session to inspect state
        current_session = session_service.get_session_sync(
            app_name=app_name,
            user_id=user_id,
            session_id=session_id
        )
        
        if current_session and hasattr(current_session, 'state'):
            # Session state is a dict, so we can access it directly
            print(f"Session state type: {type(current_session.state)}")
            print(f"Session state keys: {list(current_session.state.keys())}")
            print()
            
            # Access stored values using dict methods
            flight_data = current_session.state.get("flight_options")
            hotel_data = current_session.state.get("hotel_options")
            itinerary_data = current_session.state.get("itinerary_plan")
            
            # Display results
            if flight_data:
                print(f"✈️  flight_options: {flight_data}")
            else:
                print(f"✈️  flight_options: NOT SET (agents didn't store data)")
            
            if hotel_data:
                print(f"🏨 hotel_options: {hotel_data}")
            else:
                print(f"🏨 hotel_options: NOT SET (agents didn't store data)")
            
            if itinerary_data:
                print(f"📋 itinerary_plan: {itinerary_data}")
            else:
                print(f"📋 itinerary_plan: NOT SET (agents didn't store data)")
        else:
            print("⚠️  Cannot access session state")
        
        print("=" * 80 + "\n")
        
        # 🗺️ Now get the itinerary using the separate itinerary agent
        print("\n" + "=" * 80)
        print("🗺️ FETCHING ITINERARY WITH GOOGLE SEARCH")
        print("=" * 80)
        
        # Create a runner for the itinerary agent
        itinerary_runner = Runner(
            app_name="ItineraryPlanner",
            agent=ITINERARY_SEARCH_AGENT,
            session_service=session_service
        )
        
        # Create a new session for the itinerary agent
        itinerary_session = session_service.create_session_sync(
            app_name="ItineraryPlanner",
            user_id=user_id,
            session_id="itinerary_session"
        )
        
        # Extract city and duration from the user prompt
        itinerary_prompt = "Find a comprehensive 4-day itinerary for Basel, Switzerland"
        
        itinerary_message = types.Content(
            role="user",
            parts=[types.Part(text=itinerary_prompt)]
        )
        
        itinerary_events = itinerary_runner.run(
            user_id=user_id,
            session_id="itinerary_session",
            new_message=itinerary_message
        )
        
        itinerary_text = None
        for event in itinerary_events:
            if hasattr(event, 'content') and event.content:
                if hasattr(event.content, 'parts'):
                    for part in event.content.parts:
                        if hasattr(part, 'text') and part.text:
                            itinerary_text = part.text
        
        print("=" * 80 + "\n")
                            
        # Display the final synthesis from the ROOT_AGENT
        print("\n--- 🏆 Final Trip Plan Summary ---")
        if final_text:
            print(final_text)
        else:
            print("No response generated")
        
        # Add itinerary if we got it
        if itinerary_text:
            print("\n--- 🗺️ Detailed Itinerary ---")
            print(itinerary_text)
            print("-----------------------------")
        
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