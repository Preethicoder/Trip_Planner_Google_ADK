# agents/root_agent.py
"""
Root agent for the TripPlanner application.
Now using a simplified flat architecture for better tool execution reliability.
"""

# Import the simplified single-agent planner
from .simple_planner import SIMPLE_TRIP_PLANNER

# Use the simple planner directly as the root agent
ROOT_AGENT = SIMPLE_TRIP_PLANNER