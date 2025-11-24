# tools/schemas.py

from pydantic import BaseModel, Field
from typing import List, Optional

## ✈️ Flight Schemas
class FlightOption(BaseModel):
    """A single flight search result option."""
    flight_id: str = Field(description="Unique identifier for the flight.")
    airline: str = Field(description="The name of the airline.")
    price: float = Field(description="The total price of the round-trip ticket in USD.")
    departure_time: str = Field(description="Local time of departure (e.g., '8:00 AM').")
    duration: str = Field(description="Total travel time including layovers (e.g., '10h 30m').")
    
class FlightSearchResult(BaseModel):
    """The structured list of the best flight options."""
    options: List[FlightOption] = Field(description="A list of the top 3-5 flight options found.")

## 🏨 Hotel Schemas
class HotelOption(BaseModel):
    """A single hotel search result option."""
    name: str = Field(description="The name of the hotel.")
    price_per_night: float = Field(description="The price per night in USD.")
    rating: float = Field(description="The user rating (e.g., 4.5 out of 5.0).")
    amenities_summary: str = Field(description="A brief summary of key amenities (e.g., 'Free Wi-Fi, Pool').")
    distance_to_center: Optional[float] = Field(None, description="Distance to the city center in kilometers.")

class HotelSearchResult(BaseModel):
    """The structured list of the best hotel options."""
    options: List[HotelOption] = Field(description="A list of the top 3-5 hotel options found.")

## 🗺️ Itinerary Schemas
class DailyActivity(BaseModel):
    """A single activity planned for a day."""
    time: str = Field(description="Suggested time for the activity (e.g., '10:00 AM').")
    description: str = Field(description="Detailed description of the attraction or activity.")
    estimated_cost: float = Field(description="Estimated cost of the activity or entry fee in USD.")

class DailyPlan(BaseModel):
    """The plan for a single day of the trip."""
    day_number: int = Field(description="The sequential day number of the trip (e.g., 1, 2, 3).")
    theme: str = Field(description="A short, descriptive theme for the day (e.g., 'Cultural Immersion' or 'Nature Day').")
    activities: List[DailyActivity] = Field(description="A list of planned activities for the day.")

class ItineraryPlanResult(BaseModel):
    """The complete structured itinerary for the entire trip."""
    city: str = Field(description="The destination city for the itinerary.")
    total_days: int = Field(description="The total number of days in the itinerary.")
    daily_plans: List[DailyPlan] = Field(description="A list of the planned days for the trip.")