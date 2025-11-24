# agents/root_agent.py

from google.adk.agents import LlmAgent
from google.adk.tools import AgentTool
# Import the full workflow pipeline
from .orchestrators import TRIP_PLANNER 

# The root agent uses the pipeline as one of its tools.
TRIP_PLANNER_TOOL = AgentTool(
    agent=TRIP_PLANNER
)

ROOT_AGENT = LlmAgent(
    name="TripPlannerRoot",
    model="gemini-2.5-pro", # Use a more powerful model for sophisticated final synthesis
    description="The primary travel assistant responsible for executing the full planning workflow and synthesizing results.",
    instruction=(
        "You are a professional and friendly Travel Planning Assistant. "
        "Your task is to take the user's request (e.g., 'Plan a 5-day trip to Rome in December') and immediately call the `trip_planner_pipeline` tool with the full original prompt. "
        "After the pipeline is complete, you will find the results in the session state under the keys: `flight_options`, `hotel_options`, and `itinerary_plan`. "
        "Your final output MUST be a single, cohesive, and beautifully formatted travel summary, combining the flight, hotel, and itinerary details into one clear response."
    ),
    # The only tool the root agent uses is the pipeline itself
    tools=[TRIP_PLANNER_TOOL]
)