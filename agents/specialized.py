from google.adk.agents import LlmAgent
from google.adk.tools import google_search
# Import the initialized tools from the travel_tools module
from tools.travel_tools import (
    FLIGHT_TOOL, 
    HOTEL_TOOL, 
    ITINERARY_TOOL 
)
# --- ✈️ 1. Flight Search Agent ---
FLIGHT_AGENT = LlmAgent(
    name="FlightAgent",
    model="gemini-2.5-flash", 
    description="An expert in finding and comparing flight options using the Amadeus Flight Search Tool.",
    instruction=(
        "You are a specialized Flight Search Agent. Your sole responsibility is to find flight options. "
        "You must accurately identify and extract the **origin city**, **destination city**, **departure date**, and **number of adults** from the user's request. "
        "Use the 'flight_search' tool with the extracted parameters. "
        "Once the tool returns the results, you must clearly and concisely summarize the top 2-3 flight options, ensuring the final output strictly adheres to the FlightSearchResult schema."
    ),
    # This agent uses the Amadeus-integrated tool
    tools=[FLIGHT_TOOL],
    # The output will be stored in the session state under this key
    output_key="flight_options" 
)

# --------------------------------------------------------------------------

# --- 🏨 2. Hotel Search Agent ---
HOTEL_AGENT = LlmAgent(
    name="HotelAgent",
    model="gemini-2.5-flash",
    description="An expert in finding and comparing hotel options using the Amadeus Hotel Search Tool.",
    instruction=(
        "You are a specialized Hotel Search Agent. Your sole responsibility is to find accommodation. "
        "You must accurately identify and extract the **city code**, **check-in date**, **check-out date**, and **maximum budget per night** from the user's request. "
        "Use the 'hotel_search' tool with these extracted parameters. "
        "Once the tool returns the offers, you must clearly and concisely summarize the best 2-3 hotel options. The output must strictly adhere to the HotelSearchResult schema."
    ),
    # This agent uses the Amadeus two-step API tool
    tools=[HOTEL_TOOL],
    # The output will be stored in the session state under this key
    output_key="hotel_options" 
)
# --- Specialized LLM Agent ---

ITINERARY_AGENT = LlmAgent(
    name="ItineraryAgent",
    model="gemini-2.5-flash",
    description="An expert in generating daily travel itineraries by using Google Search and structuring the results.",
    
    # **KEY STEP: Adding the google:search tool**
    instruction=(
        "You are an expert itinerary planner. Your task is to generate a comprehensive daily plan. "
        "First, use the `google_search` tool to find popular attractions and itineraries for the destination city. "
        "Second, combine the search results with the flight/hotel details from the session state (if available). "
        "Finally, call the `itinerary_generator` tool and provide a fully structured plan that adheres strictly to the ItineraryPlanResult schema. "
        "Ensure the plan covers the requested number of days and includes specific times, descriptions, and estimated costs."
    ),
    # The agent gets access to both the search capability AND the tool that defines the output structure.
    tools=[ITINERARY_TOOL, google_search], 
    output_key="itinerary_plan" # Store the result in session state under this key
)

# ... (Other agents like FLIGHT_AGENT and HOTEL_AGENT) ...