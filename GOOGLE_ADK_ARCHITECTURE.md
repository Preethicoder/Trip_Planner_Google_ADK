# Google ADK Implementation Guide - TripPlanner Architecture

## Overview

This document explains how we used **Google ADK (Agent Development Kit)** to build an intelligent trip planning system that integrates real-time APIs with AI agents.

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [The Challenge We Solved](#the-challenge-we-solved)
3. [Solution: Wrapper Functions](#solution-wrapper-functions)
4. [Solution: Separate Agent for Google Search](#solution-separate-agent-for-google-search)
5. [Code Implementation Details](#code-implementation-details)
6. [How It All Works Together](#how-it-all-works-together)

---

## Architecture Overview

### Final Working Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER REQUEST                             │
│      "Plan a 4-day trip to Basel from Chennai..."               │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                   RUNNER (app.py / runner.py)                    │
│  • Creates sessions                                              │
│  • Manages agent execution                                       │
│  • Processes events and responses                                │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              MAIN AGENT: SimpleTripPlanner                       │
│              (agents/simple_planner.py)                          │
│  • Model: gemini-2.5-pro                                         │
│  • Tools: flight_search, hotel_search, itinerary_generator      │
│  • Wrapper functions (NOT BaseTool classes!)                    │
└────────────┬───────────────┬────────────────────────────────────┘
             │               │
             ▼               ▼
    ┌────────────┐   ┌────────────┐   ┌──────────────────┐
    │  Flight    │   │   Hotel    │   │   Itinerary      │
    │  Wrapper   │   │  Wrapper   │   │   Wrapper        │
    │  Function  │   │  Function  │   │   Function       │
    └─────┬──────┘   └─────┬──────┘   └────────┬─────────┘
          │                │                     │
          ▼                ▼                     ▼
    ┌────────────┐   ┌────────────┐   ┌──────────────────┐
    │ FLIGHT_    │   │ HOTEL_     │   │ ITINERARY_       │
    │ TOOL       │   │ TOOL       │   │ TOOL             │
    │ (BaseTool) │   │ (BaseTool) │   │ (BaseTool)       │
    └─────┬──────┘   └─────┬──────┘   └────────┬─────────┘
          │                │                     │
          ▼                ▼                     ▼
    ┌────────────┐   ┌────────────┐   ┌──────────────────┐
    │  Amadeus   │   │  Amadeus   │   │   Returns        │
    │  Flight    │   │  Hotel     │   │   Message        │
    │  API       │   │  API       │   │                  │
    └────────────┘   └────────────┘   └──────────────────┘

                         │ (After main agent completes)
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│         SEPARATE AGENT: ItinerarySearchAgent                     │
│         (agents/itinerary_agent.py)                              │
│  • Model: gemini-2.5-pro                                         │
│  • Tools: google_search ONLY                                     │
│  • Runs in separate runner instance                              │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
                  ┌─────────────┐
                  │   Google    │
                  │   Search    │
                  │   Tool      │
                  └─────────────┘
```

---

## The Challenge We Solved

### Initial Problem

When we first built the system, we encountered **two critical issues**:

#### Problem 1: Tools Were Invisible to the LLM

```python
# ❌ DIDN'T WORK: Direct BaseTool instances
tools=[FLIGHT_TOOL, HOTEL_TOOL, ITINERARY_TOOL]

# Result when agent registered tools:
# 1. function (Type: function, Description: N/A)  ← No name!
# 2. function (Type: function, Description: N/A)  ← No name!
# 3. function (Type: function, Description: N/A)  ← No name!
```

**Why?** BaseTool instances have a `.run()` method but aren't callable objects themselves. When ADK tried to register them, it lost all metadata (name, description).

**Result:** LLM couldn't see the tool names and kept saying "tool is undefined" 🚫

#### Problem 2: Google Search Incompatibility

```python
# ❌ DIDN'T WORK: Mixing google_search with function calling
tools=[flight_search, hotel_search, itinerary_generator, google_search]

# Error: 400 INVALID_ARGUMENT
# "Tool use with function calling is unsupported"
```

**Why?** In Gemini 2.5 models, `google_search` tool cannot be used alongside regular function calling tools. It's an API limitation.

---

## Solution: Wrapper Functions

### What We Did

We created **simple Python functions** that wrap the BaseTool classes:

```python
# agents/simple_planner.py

# ✅ WRAPPER FUNCTION (Callable with metadata)
def flight_search(originLocationCode: str, 
                  destinationLocationCode: str, 
                  departureDate: str, 
                  adults: int):
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
```

### Why This Works

**Wrapper functions are:**
- ✅ **Callable objects** - Can be called directly like `flight_search(...)`
- ✅ **Have `__name__` attribute** - ADK can extract the function name
- ✅ **Have docstrings** - ADK can extract descriptions and parameter info
- ✅ **Type hints** - ADK can infer parameter types and requirements
- ✅ **Compatible with gemini-2.5-pro** - Work perfectly with function calling

**Result:**
```python
# Now when agent registers tools:
1. flight_search (Type: function, Callable: True) ✅
2. hotel_search (Type: function, Callable: True) ✅
3. itinerary_generator (Type: function, Callable: True) ✅
```

The LLM can now **see and call** all the tools! 🎉

---

## Solution: Separate Agent for Google Search

### The Architectural Decision

Since `google_search` cannot coexist with function calling tools, we created **TWO separate agents**:

### Agent 1: Main Trip Planner (WITHOUT google_search)

```python
# agents/simple_planner.py

SIMPLE_TRIP_PLANNER = LlmAgent(
    name="SimpleTripPlanner",
    model="gemini-2.5-pro",
    description="Trip planner with flight, hotel, and itinerary tools.",
    instruction="""# Trip Planner Agent
    
    You are a professional trip planning assistant with access to real-time 
    flight and hotel search APIs.
    
    ## Your Task
    For every trip request, you MUST call these tools IN ORDER:
    
    1. **flight_search** - Get real flight options
    2. **hotel_search** - Get real hotel options  
    3. **itinerary_generator** - Signal for itinerary creation
    
    ## Rules
    - Call ALL three tools for EVERY trip request
    - Use EXACT parameter names
    - Never skip tools or make up data
    """,
    tools=[flight_search, hotel_search, itinerary_generator]  # No google_search!
)
```

### Agent 2: Itinerary Search Agent (ONLY google_search)

```python
# agents/itinerary_agent.py

ITINERARY_SEARCH_AGENT = LlmAgent(
    name="ItinerarySearchAgent",
    model="gemini-2.5-pro",
    description="Agent that searches for and structures travel itineraries using Google Search.",
    
    instruction="""# Itinerary Search Agent

    You are a travel itinerary specialist. Your job is to use Google Search 
    to find comprehensive itinerary information for a destination.
    
    ## Your Task
    When given a city and trip duration:
    1. Use google_search to find detailed itinerary information
    2. Search for popular attractions, restaurants, and activities
    3. Structure the results into a detailed day-by-day plan
    
    ## Output Format
    Structure your response as a clear day-by-day itinerary:
    
    **Day 1: [Theme]**
    - Morning: [Activity/Attraction]
    - Afternoon: [Activity/Attraction]  
    - Evening: [Activity/Attraction]
    """,
    tools=[google_search]  # ONLY google_search, no other tools!
)
```

### Sequential Execution in Runner

```python
# runner.py (simplified)

# Step 1: Run main planner (flights + hotels)
runner = Runner(
    app_name="TripPlanner",
    agent=ROOT_AGENT,  # Points to SIMPLE_TRIP_PLANNER
    session_service=session_service
)

events = runner.run(user_id=user_id, session_id=session_id, new_message=message)
# ... process flight and hotel results ...

# Step 2: Run itinerary agent (google search)
itinerary_runner = Runner(
    app_name="ItineraryPlanner",
    agent=ITINERARY_SEARCH_AGENT,
    session_service=session_service
)

itinerary_events = itinerary_runner.run(
    user_id=user_id, 
    session_id="itinerary_session",
    new_message=itinerary_message
)
# ... process itinerary results ...
```

### Why This Works

By separating into two agents:

1. **Main agent** can use function calling (wrapper functions) without issues
2. **Itinerary agent** can use `google_search` without conflicts
3. **Sequential execution** ensures proper workflow
4. **Each agent** has its own specialized instructions
5. **No API conflicts** - each agent uses compatible tool combinations

---

## Code Implementation Details

### 1. Tool Definition (BaseTool Classes)

```python
# tools/travel_tools.py

class FlightSearchTool(BaseTool):
    """Tool to search for flight options using Amadeus API."""
    
    def run(self, originLocationCode: str, destinationLocationCode: str, 
            departureDate: str, adults: int = 1) -> FlightSearchResult:
        """Executes the flight search API call."""
        
        # 1. Get OAuth token
        access_token = _get_access_token()
        
        # 2. Call Amadeus API
        response = requests.get(FLIGHT_SEARCH_URL, 
                               headers={"Authorization": f"Bearer {access_token}"},
                               params={...})
        
        # 3. Process and return structured results
        return FlightSearchResult(options=[...])

# Initialize tool instances
FLIGHT_TOOL = FlightSearchTool(
    name="flight_search", 
    description="Search for flight options"
)
```

### 2. Wrapper Functions

```python
# agents/simple_planner.py

def flight_search(originLocationCode: str, destinationLocationCode: str, 
                  departureDate: str, adults: int):
    """Search for flight options using Amadeus API."""
    # Simply delegate to the BaseTool's run method
    return FLIGHT_TOOL.run(originLocationCode, destinationLocationCode, 
                          departureDate, adults)
```

**Key Pattern:**
- Wrapper accepts same parameters as tool
- Has proper docstring for ADK
- Delegates execution to `TOOL.run(...)`
- Returns the result unchanged

### 3. Agent Configuration

```python
# agents/simple_planner.py

SIMPLE_TRIP_PLANNER = LlmAgent(
    name="SimpleTripPlanner",
    model="gemini-2.5-pro",  # Important: 2.5-pro supports function calling better
    description="Trip planner with flight, hotel, and itinerary tools.",
    instruction="...",  # Detailed markdown instructions
    tools=[flight_search, hotel_search, itinerary_generator]  # Wrapper functions!
)
```

**Important Details:**
- Use `gemini-2.5-pro` not `gemini-2.5-flash` (flash has issues with tools)
- Pass wrapper **functions**, not BaseTool instances
- Instructions should be clear, detailed, and use markdown
- Include parameter examples and rules

### 4. Runner Setup

```python
# runner.py or app.py

from google.adk import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

# Create session service
session_service = InMemorySessionService()

# Create session
session = session_service.create_session_sync(
    app_name="TripPlanner",
    user_id=user_id,
    session_id=session_id
)

# Create runner
runner = Runner(
    app_name="TripPlanner",
    agent=SIMPLE_TRIP_PLANNER,  # Your agent
    session_service=session_service
)

# Create message
message = types.Content(
    role="user",
    parts=[types.Part(text=user_prompt)]
)

# Execute
events = runner.run(
    user_id=user_id,
    session_id=session_id,
    new_message=message
)
```

---

## How It All Works Together

### Complete Flow Example

**User Input:**
> "Plan a 4-day trip to Basel, arriving June 10, 2026"

### Step 1: Main Agent Execution

```
User → Runner → SIMPLE_TRIP_PLANNER
                    ↓
        LLM analyzes request and decides to call:
                    ↓
        1. flight_search(MAA, BSL, 2026-06-10, 2)
           → FLIGHT_TOOL.run()
           → Amadeus API
           → Returns: [Flight options with real prices]
                    ↓
        2. hotel_search(BSL, 2026-06-10, 2026-06-14, 300, 2)
           → HOTEL_TOOL.run()
           → Amadeus API
           → Returns: [Hotel options with real prices]
                    ↓
        3. itinerary_generator(Basel, 4)
           → ITINERARY_TOOL.run()
           → Returns: "Search Google for Basel itinerary"
                    ↓
        LLM synthesizes results into text response
```

### Step 2: Itinerary Agent Execution

```
Runner creates new instance → ITINERARY_SEARCH_AGENT
                    ↓
        Request: "Find 4-day itinerary for Basel"
                    ↓
        LLM uses google_search tool
                    ↓
        Searches: "Basel 4-day itinerary attractions"
                    ↓
        Processes search results
                    ↓
        Returns: Detailed day-by-day itinerary with:
        - Day 1: Old Town exploration
        - Day 2: Museums (Kunstmuseum, etc.)
        - Day 3: Day trip to Alsace
        - Day 4: Rhine activities
```

### Step 3: Final Output

```
Combined Response:
├── Flights: Real Amadeus data (€985-€1104)
├── Hotels: Real Amadeus data (filtered by budget)
└── Itinerary: Google Search results (structured by AI)
```

---

## Key Learnings and Best Practices

### ✅ DO's

1. **Use wrapper functions** for BaseTool classes to preserve metadata
2. **Separate agents** when tools are incompatible (like google_search)
3. **Use gemini-2.5-pro** for better function calling support
4. **Write detailed instructions** with examples and parameter formats
5. **Use sequential execution** when agents need to work in order
6. **Test with working data** (e.g., Basel route for Amadeus Test API)

### ❌ DON'Ts

1. **Don't pass BaseTool instances directly** to agent tools list
2. **Don't mix google_search with other tools** in gemini-2.5
3. **Don't use gemini-2.5-flash** if you need reliable function calling
4. **Don't use past dates** with Amadeus Test API
5. **Don't expect all routes** to work with Amadeus Test API (limited data)

---

## Conclusion

This architecture demonstrates:

1. **How to properly integrate custom tools** with Google ADK using wrapper functions
2. **How to handle API limitations** by using separate specialized agents
3. **How to orchestrate multi-agent workflows** with sequential execution
4. **How to combine real-time APIs** (Amadeus) with AI search (Google) seamlessly

The result is a **fully functional AI trip planner** that:
- ✅ Calls real flight and hotel APIs
- ✅ Uses AI to generate detailed itineraries
- ✅ Works around API limitations elegantly
- ✅ Provides a clean user interface (Streamlit)

**Total tokens used to solve this:** ~90,000+ tokens of debugging and iteration! 🎉

---

## Files Reference

- `agents/simple_planner.py` - Main agent with wrapper functions
- `agents/itinerary_agent.py` - Separate agent for Google Search
- `tools/travel_tools.py` - BaseTool implementations
- `runner.py` - CLI execution with both agents
- `app.py` - Streamlit UI with both agents
- `WHY_400_ERRORS.md` - Troubleshooting guide
- `AMADEUS_TEST_ROUTES.md` - Working routes reference

---

*Built with ❤️ using Google ADK, Amadeus API, and lots of debugging!*
