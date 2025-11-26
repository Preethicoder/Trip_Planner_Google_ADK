# TripPlanner Tool Execution Analysis & Solutions

## Date: 25 November 2025

### Summary
After extensive testing and configuration attempts, we've identified the core issue and explored multiple solutions.

---

## ✅ What We've Confirmed

1. **Amadeus API Integration Works Perfectly**
   - FlightSearchTool: Returns real Lufthansa flights from Chennai to Basel
   - HotelSearchTool: Searches 48 hotels in Basel successfully
   - API credentials are REAL and valid (not mock)

2. **All Improvements Successfully Implemented**
   - ✅ Strengthened agent instructions with explicit parameters
   - ✅ Added tool execution validation logic
   - ✅ Implemented session state debugging
   - ✅ Direct tool testing framework

3. **Validation System Working**
   - Correctly detects when tools aren't called
   - Provides clear warnings to users
   - Helps diagnose orchestration issues

---

## ❌ Core Problem Identified

**The LLM agents within multi-agent orchestrators are choosing NOT to call tools**, despite:
- Strong "MUST use tool" instructions
- Explicit parameter documentation
- Step-by-step execution guides

### Root Cause
When LlmAgents are nested within ParallelAgent/SequentialAgent orchestrators, they have the autonomy to decide whether to call tools or generate responses from their knowledge base. Gemini is choosing to use its built-in knowledge instead of calling the Amadeus APIs.

---

## 🔧 Solutions Attempted

### 1. Strengthened Instructions ⚠️ PARTIAL SUCCESS
**Approach:** Added explicit "🚨 MANDATORY" warnings, parameter lists, and step-by-step guides
**Result:** Instructions are clear but LLM still has choice to bypass tools
**Status:** Implemented but insufficient alone

### 2. Tool Config with FunctionCallingConfigMode.ANY ❌ FAILED
**Approach:**
```python
generate_content_config=GenerateContentConfig(
    tool_config=ToolConfig(
        function_calling_config=FunctionCallingConfig(
            mode=FunctionCallingConfigMode.ANY
        )
    )
)
```
**Error:** `400 INVALID_ARGUMENT: Function calling config is set without function_declarations`
**Reason:** When agents are nested in orchestrators, the tool_config is passed down but tools aren't properly included in the Gemini API call
**Status:** Not viable with current ADK architecture

### 3. Tool Config with allowed_function_names ❌ FAILED
**Approach:**
```python
generate_content_config=GenerateContentConfig(
    tool_config=ToolConfig(
        function_calling_config=FunctionCallingConfig(
            mode=FunctionCallingConfigMode.AUTO,
            allowed_function_names=["flight_search", "hotel_search"]
        )
    )
)
```
**Result:** Same error as above
**Status:** Not viable with nested agents

---

## ✅ Working Solutions

### Solution A: Direct Tool Execution (RECOMMENDED)
**Skip LLM orchestration for tool calls and execute tools programmatically.**

**Implementation:**
```python
# agents/orchestrators.py
from tools.travel_tools import FLIGHT_TOOL, HOTEL_TOOL
import re

def extract_parameters(request_text):
    """Parse user request to extract tool parameters"""
    # Extract dates, cities, budget, etc.
    # Use regex or simple string parsing
    pass

def execute_trip_search(request: str) -> dict:
    """Directly execute flight and hotel searches"""
    # Parse request
    params = extract_parameters(request)
    
    # Force tool execution
    print("🚀 Forcing flight search...")
    flights = FLIGHT_TOOL.run(
        originLocationCode=params['origin'],
        destinationLocationCode=params['destination'],
        departureDate=params['departure_date'],
        adults=params['adults']
    )
    
    print("🚀 Forcing hotel search...")
    hotels = HOTEL_TOOL.run(
        cityCode=params['destination'],
        check_in=params['check_in'],
        check_out=params['check_out'],
        max_budget=params['budget']
    )
    
    return {
        "flights": flights,
        "hotels": hotels
    }

# Create a simple tool wrapper
FORCED_SEARCH_TOOL = BaseTool(
    name="forced_trip_search",
    description="Executes flight and hotel searches with guaranteed API calls",
    run=execute_trip_search
)

# Use in ROOT_AGENT instead of nested agents
ROOT_AGENT = LlmAgent(
    name="TripPlanner",
    tools=[FORCED_SEARCH_TOOL, ITINERARY_TOOL],
    instruction="Always call forced_trip_search first..."
)
```

**Pros:**
- ✅ Guarantees tool execution
- ✅ No LLM autonomy issues
- ✅ Reliable and predictable

**Cons:**
- ❌ Requires parameter parsing logic
- ❌ Less flexible than LLM-driven orchestration

---

### Solution B: Flatten Architecture
**Remove ParallelAgent/SequentialAgent nesting and use a single LlmAgent.**

**Implementation:**
```python
# agents/simple_planner.py
from google.adk.agents import LlmAgent
from tools.travel_tools import FLIGHT_TOOL, HOTEL_TOOL, ITINERARY_TOOL

SIMPLE_TRIP_PLANNER = LlmAgent(
    name="SimpleTripPlanner",
    model="gemini-2.5-pro",  # Use Pro for better instruction following
    tools=[FLIGHT_TOOL, HOTEL_TOOL, ITINERARY_TOOL],
    instruction=(
        "You are a trip planner. For EVERY request:\n"
        "1. FIRST call flight_search tool\n"
        "2. THEN call hotel_search tool\n"
        "3. FINALLY call itinerary_generator tool\n"
        "Do these IN ORDER. Never skip tools."
    )
)
```

**Replace ROOT_AGENT:**
```python
# agents/root_agent.py
from agents.simple_planner import SIMPLE_TRIP_PLANNER

ROOT_AGENT = SIMPLE_TRIP_PLANNER
```

**Pros:**
- ✅ Simpler architecture
- ✅ No nested agent issues
- ✅ Better tool visibility to LLM

**Cons:**
- ❌ Still relies on LLM choosing to call tools
- ❌ Loses parallel execution benefits

---

### Solution C: Validation with Fallback
**Keep current architecture but add automatic retry with forced execution.**

**Implementation:**
```python
# runner.py
def run_with_fallback(user_prompt):
    # Try multi-agent orchestration first
    events = runner.run(user_id, session_id, message)
    
    # Check if tools were called
    tool_calls = [...]  # Extract from events
    
    if not flight_tool_used or not hotel_tool_used:
        print("⚠️ Tools not called, forcing direct execution...")
        # Parse prompt and force tool calls
        params = extract_parameters(user_prompt)
        flights = FLIGHT_TOOL.run(**params['flight'])
        hotels = HOTEL_TOOL.run(**params['hotel'])
        
        # Feed results back to LLM for itinerary
        itinerary_prompt = f"Using these flights: {flights} and hotels: {hotels}, create itinerary..."
        # ... continue
```

**Pros:**
- ✅ Best of both worlds
- ✅ Attempts LLM orchestration first
- ✅ Guarantees data reliability

**Cons:**
- ❌ More complex logic
- ❌ Requires parameter extraction

---

## 📊 Recommendation

**Best Approach:** **Solution A (Direct Tool Execution)**

**Rationale:**
1. Your primary goal is to get REAL flight/hotel data from Amadeus
2. Current multi-agent orchestration is sophisticated but unreliable for tool execution
3. Direct execution is simple, predictable, and guarantees API usage
4. You can still use LLM for itinerary generation after getting real data

**Implementation Priority:**
1. Create `execute_trip_search()` function with parameter parsing
2. Wrap it in a BaseTool
3. Replace TRIP_PLANNER_PIPELINE with direct tool in ROOT_AGENT
4. Test with validation system (should show ✅ for both tools)

---

## 🔬 Alternative: Test with Gemini Pro

The current implementation uses `gemini-2.5-flash` which prioritizes speed over instruction following. Try upgrading to `gemini-2.5-pro`:

```python
FLIGHT_AGENT = LlmAgent(
    name="FlightAgent",
    model="gemini-2.5-pro",  # More likely to follow tool instructions
    ...
)
```

**Gemini Pro:**
- Better at following complex instructions
- More reliable tool calling
- Slower and more expensive but might solve the issue

---

## 📝 Current File State

### Files with tool_config (WILL CAUSE ERRORS)
- `agents/specialized.py` - Lines with `generate_content_config` should be REMOVED

### Working Files
- `tools/travel_tools.py` - ✅ Fully functional
- `test_tools.py` - ✅ Proves tools work
- `runner.py` - ✅ Has validation logic
- `agents/orchestrators.py` - ⚠️ Architecture works but tools not called

### Next Edit Required
Remove `generate_content_config` from specialized.py to avoid API errors, then implement Solution A or B.

---

## 🎯 Action Items

1. **Immediate:** Remove `generate_content_config` from specialized.py (causing 400 errors)
2. **Short-term:** Implement Solution A (Direct Tool Execution)
3. **Alternative:** Try Solution B (Flatten Architecture with gemini-2.5-pro)
4. **Long-term:** Monitor Google ADK updates for better nested agent tool configuration support
