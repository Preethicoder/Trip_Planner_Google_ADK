# app.py
"""
Simple and attractive UI for the Trip Planner using Streamlit.
Run with: streamlit run app.py
"""

import streamlit as st
from datetime import date, timedelta
import os
from dotenv import load_dotenv
from google.adk import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

# Load environment variables
load_dotenv()

# Import agents
from agents.root_agent import ROOT_AGENT
from agents.itinerary_agent import ITINERARY_SEARCH_AGENT

# Page configuration
st.set_page_config(
    page_title="AI Trip Planner",
    page_icon="✈️",
    layout="centered"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #FF4B4B;
        color: white;
        font-size: 18px;
        font-weight: bold;
        padding: 0.75rem;
        border-radius: 10px;
        border: none;
        margin-top: 1rem;
    }
    .stButton>button:hover {
        background-color: #FF3333;
    }
    h1 {
        color: #FF4B4B;
        text-align: center;
    }
    .result-box {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        margin-top: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# Title
st.title("✈️ AI Trip Planner")
st.markdown("### Plan your perfect trip with real-time flight & hotel data!")
st.markdown("---")

# Input form
st.info("💡 **Tip**: Amadeus Test API has limited data. Known working routes: MAA→BSL (Basel), JFK→LAX, LHR→CDG")

col1, col2 = st.columns(2)

with col1:
    destination = st.text_input("🌍 Destination City", placeholder="e.g., Basel, Switzerland")
    origin = st.text_input("🛫 Origin Airport", placeholder="e.g., Chennai")
    arrival_date = st.date_input("📅 Arrival Date", value=date.today() + timedelta(days=30))

with col2:
    destination_code = st.text_input("📍 Destination IATA Code", placeholder="e.g., BSL")
    origin_code = st.text_input("📍 Origin IATA Code", placeholder="e.g., MAA")
    departure_date = st.date_input("📅 Departure Date", value=date.today() + timedelta(days=34))

# Calculate trip duration
if arrival_date and departure_date:
    trip_days = (departure_date - arrival_date).days
    st.info(f"🗓️ Trip Duration: **{trip_days} days**")

# Travelers and budget
col3, col4 = st.columns(2)

with col3:
    adults = st.number_input("👥 Number of Adults", min_value=1, max_value=10, value=2)
    children = st.number_input("👶 Number of Children", min_value=0, max_value=10, value=0)

with col4:
    hotel_budget = st.number_input("💰 Max Hotel Budget (EUR/night)", min_value=50, max_value=1000, value=300, step=50)

st.markdown("---")

# Plan Trip Button
if st.button("🚀 Plan My Trip!"):
    # Validation
    if not destination or not origin or not destination_code or not origin_code:
        st.error("⚠️ Please fill in all required fields!")
    elif arrival_date >= departure_date:
        st.error("⚠️ Departure date must be after arrival date!")
    else:
        # Create the prompt
        travelers_text = f"{adults} adult{'s' if adults > 1 else ''}"
        if children > 0:
            travelers_text += f" and {children} child{'ren' if children > 1 else ''}"
        
        user_prompt = (
            f"Plan a {trip_days}-day trip to {destination}, arriving on {arrival_date} and departing {departure_date}. "
            f"I will be traveling with {travelers_text}. My origin airport is {origin}. "
            f"The maximum I want to spend on a hotel is {hotel_budget} Euros per night."
        )
        
        # Setup environment
        if not os.getenv("GOOGLE_API_KEY"):
            st.error("⚠️ GOOGLE_API_KEY not set! Please configure your API keys.")
            st.stop()
        
        # Show loading spinner
        with st.spinner("🔍 Searching for flights and hotels... This may take a minute."):
            try:
                # Initialize session service
                session_service = InMemorySessionService()
                
                # Create session
                app_name = "TripPlanner"
                user_id = "streamlit_user"
                session_id = f"session_{arrival_date}_{departure_date}"
                
                session = session_service.create_session_sync(
                    app_name=app_name,
                    user_id=user_id,
                    session_id=session_id
                )
                
                # Create runner
                runner = Runner(
                    app_name=app_name,
                    agent=ROOT_AGENT,
                    session_service=session_service
                )
                
                # Create message
                message = types.Content(
                    role="user",
                    parts=[types.Part(text=user_prompt)]
                )
                
                # Run agent
                events = runner.run(
                    user_id=user_id,
                    session_id=session_id,
                    new_message=message
                )
                
                # Process results
                final_text = None
                for event in events:
                    if hasattr(event, 'content') and event.content:
                        if hasattr(event.content, 'parts'):
                            for part in event.content.parts:
                                if hasattr(part, 'text') and part.text:
                                    final_text = part.text
                
                # Get itinerary
                itinerary_runner = Runner(
                    app_name="ItineraryPlanner",
                    agent=ITINERARY_SEARCH_AGENT,
                    session_service=session_service
                )
                
                itinerary_session = session_service.create_session_sync(
                    app_name="ItineraryPlanner",
                    user_id=user_id,
                    session_id="itinerary_session"
                )
                
                itinerary_prompt = f"Find a comprehensive {trip_days}-day itinerary for {destination}"
                
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
                
                # Display results
                st.success("✅ Trip plan generated successfully!")
                
                # Show trip summary
                if final_text:
                    st.markdown("## 🏆 Your Trip Plan")
                    st.markdown(final_text)
                
                # Show itinerary
                if itinerary_text:
                    st.markdown("---")
                    st.markdown("## 🗺️ Detailed Itinerary")
                    st.markdown(itinerary_text)
                
            except Exception as e:
                st.error(f"❌ An error occurred: {str(e)}")
                st.info("💡 Tip: Make sure your API keys are configured correctly in the .env file")

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #666;'>
        <p>Powered by Google ADK & Amadeus API | Real-time flight & hotel data</p>
    </div>
""", unsafe_allow_html=True)
