# agents/orchestrators.py

from google.adk.agents import SequentialAgent, ParallelAgent
# Import the specialized agents defined in the previous step
from .specialized import FLIGHT_AGENT, HOTEL_AGENT, ITINERARY_AGENT 

# --- A. Parallel Execution Step ---
# Since finding flights and finding hotels are independent tasks,
# we run them concurrently to minimize the user's wait time.
PARALLEL_PLANNER = ParallelAgent(
    name="ParallelTripSearch",
    # Agents will run at the same time
    sub_agents=[FLIGHT_AGENT, HOTEL_AGENT],
    description="Runs flight and hotel searches concurrently.",
    # The output of both agents (flight_options and hotel_options) 
    # will be automatically stored in the session state.
)

# --- B. Sequential Pipeline ---
# The Itinerary Agent *depends* on the results of the Parallel Search, 
# so the parallel step MUST finish before the itinerary step begins.
TRIP_PLANNER_PIPELINE = SequentialAgent(
    name="TripPlannerPipeline",
    # Agents will execute in this fixed order
    sub_agents=[
        PARALLEL_PLANNER,  # Step 1: Execute flight and hotel search (in parallel)
        ITINERARY_AGENT    # Step 2: Generate itinerary (using results from Step 1)
    ],
    description="The main workflow that coordinates all trip planning steps sequentially.",
)

# Export the final pipeline for the Root Agent
TRIP_PLANNER = TRIP_PLANNER_PIPELINE