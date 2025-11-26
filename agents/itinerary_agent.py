# agents/itinerary_agent.py
"""
Separate agent that uses Google Search to create detailed itineraries.
This is needed because gemini-2.5-pro doesn't support google_search + function calling together.
"""

from google.adk.agents import LlmAgent
from google.adk.tools import google_search

ITINERARY_SEARCH_AGENT = LlmAgent(
    name="ItinerarySearchAgent",
    model="gemini-2.5-pro",
    description="Agent that searches for and structures travel itineraries using Google Search.",
    
    instruction="""# Itinerary Search Agent

You are a travel itinerary specialist. Your job is to use Google Search to find comprehensive itinerary information for a destination.

## Your Task
When given a city and trip duration:
1. Use google_search to find detailed itinerary information for that destination
2. Search for popular attractions, restaurants, and activities
3. Structure the results into a detailed day-by-day plan

## Output Format
Structure your response as a clear day-by-day itinerary:

**Day 1: [Theme]**
- Morning: [Activity/Attraction]
- Afternoon: [Activity/Attraction]  
- Evening: [Activity/Attraction]

**Day 2: [Theme]**
...

Include specific attraction names, recommended times, and practical tips from your search results.
""",
    tools=[google_search]
)
