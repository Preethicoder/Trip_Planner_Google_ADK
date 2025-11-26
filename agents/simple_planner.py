# agents/simple_planner.py
"""
Simplified single-agent trip planner with direct function wrappers.
"""

from google.adk.agents import LlmAgent
from google.adk.tools import google_search
from tools.travel_tools import FLIGHT_TOOL, HOTEL_TOOL, ITINERARY_TOOL

# Create simple wrapper functions that LLM can call directly
def flight_search(originLocationCode: str, destinationLocationCode: str, departureDate: str, adults: int):
    """Search for flight options using Amadeus API.
    
    Args:
        originLocationCode: 3-letter IATA code (e.g., MAA for Chennai)
        destinationLocationCode: 3-letter IATA code (e.g., BSL for Basel)
        departureDate: Date in YYYY-MM-DD format
        adults: Number of adult passengers
    """
    return FLIGHT_TOOL.run(originLocationCode, destinationLocationCode, departureDate, adults)

def hotel_search(cityCode: str, check_in: str, check_out: str, max_budget: float, adults: int = 2):
    """Search for hotel options using Amadeus API.
    
    Args:
        cityCode: 3-letter IATA city code
        check_in: Check-in date in YYYY-MM-DD format
        check_out: Check-out date in YYYY-MM-DD format
        max_budget: Maximum price per night in EUR
        adults: Number of adult guests (default: 2)
    """
    return HOTEL_TOOL.run(cityCode, check_in, check_out, max_budget, adults)

def itinerary_generator(city: str, trip_length_days: int):
    """Generate a structured itinerary for the trip.
    
    Args:
        city: Destination city name
        trip_length_days: Number of days for the trip
    """
    return ITINERARY_TOOL.run(city, trip_length_days)

# Single agent with direct function tools
SIMPLE_TRIP_PLANNER = LlmAgent(
    name="SimpleTripPlanner",
    model="gemini-2.5-pro",
    description="Trip planner with flight, hotel, and itinerary tools.",
    
    instruction="""# Trip Planner Agent

You are a professional trip planning assistant with access to real-time flight and hotel search APIs.

## Your Task
For every trip request, you MUST call these tools IN ORDER:

1. **flight_search** - Get real flight options
   - originLocationCode: 3-letter code (Chennai=MAA, Basel=BSL)
   - destinationLocationCode: 3-letter code  
   - departureDate: YYYY-MM-DD
   - adults: number

2. **hotel_search** - Get real hotel options
   - cityCode: 3-letter code
   - check_in: YYYY-MM-DD (use underscore!)
   - check_out: YYYY-MM-DD (use underscore!)
   - max_budget: 300.0
   - adults: number of adult guests (e.g., 2)

3. **itinerary_generator** - Signal for itinerary creation
   - city: destination name
   - trip_length_days: number of days

## Rules
- Call ALL three tools for EVERY trip request
- Use EXACT parameter names
- Never skip tools or make up data
- Present the flight and hotel results clearly
""",
    tools=[flight_search, hotel_search, itinerary_generator]
)
