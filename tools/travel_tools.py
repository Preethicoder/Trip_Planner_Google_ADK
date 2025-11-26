# tools/travel_tools.py

from google.adk.tools import BaseTool
from .schemas import FlightSearchResult, HotelSearchResult, ItineraryPlanResult
from typing import List, Dict, Any, Optional
import requests
import os
import random
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- Amadeus API Configuration ---
# NOTE: These are loaded from environment variables (.env file)
API_KEY = os.getenv("AMADEUS_API_KEY", "YOUR_API_KEY_HERE")
API_SECRET = os.getenv("AMADEUS_API_SECRET", "YOUR_API_SECRET_HERE")

AUTH_URL = "https://test.api.amadeus.com/v1/security/oauth2/token"
FLIGHT_SEARCH_URL = "https://test.api.amadeus.com/v2/shopping/flight-offers"

HOTEL_LIST_URL = "https://test.api.amadeus.com/v1/reference-data/locations/hotels/by-city"
HOTEL_SEARCH_URL = "https://test.api.amadeus.com/v3/shopping/hotel-offers"

# --- Helper Function ---
def _get_access_token() -> str:
    """Handles the OAuth 2.0 client credentials flow to get a Bearer token."""
    print("✈️ Amadeus Auth: Requesting new access token...")
    
    # The Amadeus API expects the body to be x-www-form-urlencoded
    auth_data = {
        "grant_type": "client_credentials",
        "client_id": API_KEY,
        "client_secret": API_SECRET,
    }
    
    # The 'requests' library automatically sets the correct Content-Type 
    # header ('application/x-www-form-urlencoded') when using the 'data' parameter 
    # with a dictionary, as required by Amadeus.
    try:
        response = requests.post(AUTH_URL, data=auth_data)
        response.raise_for_status() # Raise exception for bad status codes (4xx or 5xx)
        
        token = response.json().get("access_token")
        if not token:
            raise ValueError("Access token not found in authentication response.")
        
        print("✈️ Amadeus Auth: Token retrieved successfully.")
        return token
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Amadeus Auth Error: Failed to get token. Details: {e}")
        raise

    
class FlightSearchTool(BaseTool):
    """
    Tool to search for the best available flight options using the Amadeus API.
    Handles token authentication internally.
    """
    
    
    def run(self, originLocationCode: str, destinationLocationCode: str, departureDate: str, adults: int = 1) -> FlightSearchResult:
        """
        Executes the flight offers search API call.

        Args:
            originLocationCode: The starting airport IATA code (e.g., 'NYC').
            destinationLocationCode: The target airport IATA code (e.g., 'LAX').
            departureDate: The travel date (YYYY-MM-DD).
            adults: The number of adult passengers.

        Returns:
            A structured FlightSearchResult object.
        """
        # 1. Get Access Token
        access_token = _get_access_token()
        
        # 2. Prepare API Headers and Parameters
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        
        params = {
            "originLocationCode": originLocationCode,
            "destinationLocationCode": destinationLocationCode,
            "departureDate": departureDate,
            "adults": adults
        }

        # 3. Make the Flight Search GET Request
        print(f"✈️ API Executing: Searching flights from {originLocationCode} to {destinationLocationCode}...")
        try:
            response = requests.get(FLIGHT_SEARCH_URL, headers=headers, params=params)
            response.raise_for_status()
            
            search_data = response.json()
            
            # --- 4. Process API Response to Match ADK Schema ---
            
            # This is the crucial step: map the complex Amadeus JSON response 
            # to your simple FlightSearchResult schema.
            processed_options = []
            
            # We'll just take the top 3 results from the 'data' array for demonstration
            for offer in search_data.get("data", [])[:3]:
                # Extract the total price
                price = float(offer["price"]["total"])
                
                # Get the first segment of the itinerary for departure details
                first_segment = offer["itineraries"][0]["segments"][0]
                departure_time = first_segment["departure"]["at"].split('T')[1][:5] # e.g., "2025-12-25T08:30:00" -> "08:30"
                
                # Get total duration (needs conversion from ISO 8601 duration string, 
                # but we'll simplify it here for the skeleton)
                duration = offer["itineraries"][0]["duration"].replace('PT', '').lower()
                
                processed_options.append({
                    "flight_id": f"AMADEUS-{random.randint(100, 999)}", # Assign a unique ID
                    "airline": first_segment["carrierCode"], # IATA airline code
                    "price": price,
                    "departure_time": departure_time,
                    "duration": duration,
                })

            if not processed_options:
                 print("⚠️ No flight offers found in the Amadeus response.")
            
            return FlightSearchResult(options=processed_options)
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Amadeus Search Error: Failed to search flights. Details: {e}")
            # Return an empty result if the search fails gracefully
            return FlightSearchResult(options=[])

# --- Placeholder Tools (Unmodified, but included for completeness) ---

class HotelSearchTool(BaseTool):
    """
    Tool to search for the best hotel options using a two-step Amadeus API process.
    """
    
    def _get_hotel_ids(self, cityCode: str) -> List[str]:
        """Step 1: Get a list of hotel IDs for the given city."""
        print(f"🏨 Step 1: Searching for hotel IDs in {cityCode}...")
        
        token = _get_access_token()
        headers = {"Authorization": f"Bearer {token}"}
        params = {"cityCode": cityCode}
        
        try:
            response = requests.get(HOTEL_LIST_URL, headers=headers, params=params)
            response.raise_for_status()
            
            data = response.json().get("data", [])
            # Extract the 'hotelId' from the list of hotel data objects
            hotel_ids = [item["hotelId"] for item in data if "hotelId" in item]
            
            print(f"🏨 Step 1 Result: Found {len(hotel_ids)} hotel IDs.")
            # Limit the number of IDs to search in the next step to prevent API quotas/complexity
            return hotel_ids[:5] 
        except requests.exceptions.RequestException as e:
            print(f"❌ Amadeus Hotel List Error: {e}")
            return []

    def _get_hotel_offers(self, hotel_ids: List[str], check_in: str, check_out: str, adults: int) -> HotelSearchResult:
        """Step 2: Get real-time offers for the found hotel IDs."""
        print(f"🏨 Step 2: Searching offers for {len(hotel_ids)} hotels...")
        
        if not hotel_ids:
            return HotelSearchResult(options=[])

        token = _get_access_token()
        headers = {"Authorization": f"Bearer {token}"}
        
        # Amadeus requires hotel IDs as a comma-separated string
        hotel_ids_str = ",".join(hotel_ids) 
        
        params = {
            "hotelIds": hotel_ids_str,
            "checkInDate": check_in,
            "checkOutDate": check_out,
            "adults": adults
        }
        
        try:
            response = requests.get(HOTEL_SEARCH_URL, headers=headers, params=params)
            response.raise_for_status()
            search_data = response.json()
            
            # --- Process API Response to Match ADK Schema ---
            processed_options = []
            
            # We iterate through the offers found
            for hotel_offer in search_data.get("data", [])[:5]:
                # Find the cheapest offer/room in the hotel
                cheapest_offer = hotel_offer["offers"][0] if hotel_offer.get("offers") else None
                
                if cheapest_offer:
                    # The total price for the stay
                    total_price = float(cheapest_offer["price"]["total"])
                    # Price per night (total / number of nights) - needs date calculation logic in a real app, 
                    # but for now, we'll simplify.
                    price_per_night = round(total_price / 3, 2) # Mock division by 3 nights
                    
                    # Extract general hotel info from the 'hotel' block
                    hotel_info = hotel_offer["hotel"]
                    
                    processed_options.append({
                        "name": hotel_info.get("name", "Unknown Hotel"),
                        "price_per_night": price_per_night,
                        "rating": random.uniform(3.0, 5.0), # Amadeus has separate rating API, using mock here
                        "amenities_summary": "Check for amenities in the offer details.",
                        "distance_to_center": None,
                    })

            return HotelSearchResult(options=processed_options)
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Amadeus Hotel Search Error: Failed to get offers. Details: {e}")
            return HotelSearchResult(options=[])

    def run(self, cityCode: str, check_in: str, check_out: str, max_budget: float, adults: int = 2) -> HotelSearchResult:
        """The main entry point for the Hotel Search Tool, orchestrating the two API calls."""
        
        # 1. Get Hotel IDs
        hotel_ids = self._get_hotel_ids(cityCode=cityCode)
        
        # 2. Search for Offers using the IDs
        results = self._get_hotel_offers(
            hotel_ids=hotel_ids, 
            check_in=check_in, 
            check_out=check_out,
            adults=adults
        )
        
        # 3. Filter results based on max_budget (optional cleanup/business logic)
        filtered_results = [
            option for option in results.options 
            if option.price_per_night <= max_budget
        ]
        
        return HotelSearchResult(options=filtered_results)


class ItineraryTool(BaseTool):
    """
    Tool to gather itinerary data from the internet (via Google Search)
    and structure it into a daily plan.
    """
    def run(self, city: str, trip_length_days: int) -> str:
        """
        Signals the LLM Agent to search for itinerary ideas for the specified city and duration.

        Args:
            city: The destination city.
            trip_length_days: The number of days for the trip.

        Returns:
            A message instructing the agent to search and structure the results.
        """
        print(f"🗺️ Tool Executing: Signaling Agent to search for a {trip_length_days}-day itinerary for {city} using Google Search.")
        # This function signals that the LLM should use google_search to find itinerary information
        # and then structure it according to the ItineraryPlanResult schema
        return f"Search Google for a comprehensive {trip_length_days}-day itinerary for {city}, including top attractions, activities, and dining recommendations. Structure the results as a day-by-day plan."

# Initialize the tool
ITINERARY_TOOL = ItineraryTool(name="itinerary_generator", description="Generate a day-by-day itinerary plan for a trip")

# ... (Rest of the file) ...

# Initialize the tools for use in the agent definitions
FLIGHT_TOOL = FlightSearchTool(name="flight_search", description="Search for flight options")
HOTEL_TOOL = HotelSearchTool(name="hotel_search", description="Search for hotel options")
