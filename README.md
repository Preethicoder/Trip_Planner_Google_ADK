# TripPlanner - Multi-Agent Travel Planning System

A sophisticated multi-agent system built with Google ADK (Agent Development Kit) that helps plan complete trips including flights, hotels, and daily itineraries.

## ⚠️ IMPORTANT: Date Requirements

**The Amadeus Test API only accepts FUTURE dates!**

- Current date: November 26, 2025
- ✅ Valid dates: 2026-01-01 and later
- ❌ Invalid dates: Any date before November 26, 2025

**Common Error**: If you see `400 Bad Request` errors for flights or hotels, it usually means:
1. The date is in the past
2. The IATA code is invalid
3. No availability for that route/destination

## 🚀 Quick Start with UI

```bash
# Activate virtual environment
source venv/bin/activate

# Run the Streamlit UI
venv/bin/python -m streamlit run app.py
```

Then open `http://localhost:8501` and fill in your trip details with **future dates**!

## Features

- **Multi-Agent Architecture**: Specialized agents for flights, hotels, and itinerary planning
- **Parallel Processing**: Flight and hotel searches run concurrently for efficiency
- **Real-time Travel Data**: Integration with Amadeus Travel API (configurable)
- **Intelligent Itinerary**: Google Search integration for destination recommendations

## Prerequisites

- Python 3.11+
- Google AI API Key (for Gemini models)
- Amadeus API credentials (optional, for real travel data)

## Setup

### 1. Clone and Navigate to Project
```bash
cd /Users/preethisivakumar/Documents/TripPlanner
```

### 2. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate  # On Windows
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Up API Keys

#### Google AI API Key (Required)
1. Get your API key from: https://aistudio.google.com/app/apikey
2. Set the environment variable:
```bash
export GOOGLE_API_KEY='your-google-api-key-here'
```

#### Amadeus API Credentials (Optional)
For real flight and hotel data:
1. Sign up at: https://developers.amadeus.com/
2. Get your API key and secret
3. Set environment variables:
```bash
export AMADEUS_API_KEY='your-amadeus-api-key'
export AMADEUS_API_SECRET='your-amadeus-api-secret'
```

## Usage

### Run the Trip Planner
```bash
python runner.py
```

### Run Simple Test
To test the basic setup:
```bash
python simple_test.py
```

### Customize Your Trip
Edit the `user_prompt` in `runner.py` to customize your trip:

```python
user_prompt = (
    "Plan a 4-day trip to Paris, France, arriving on 2026-06-10 and departing 2026-06-14. "
    "I will be traveling alone (1 adult). My origin airport is JFK. "
    "The maximum I want to spend on a hotel is $250 per night."
)
```

## Project Structure

```
TripPlanner/
├── agents/
│   ├── __init__.py
│   ├── root_agent.py          # Main orchestrator agent
│   ├── specialized.py         # Flight, Hotel, Itinerary agents
│   └── orchestrators.py       # Parallel and Sequential agents
├── tools/
│   ├── __init__.py
│   ├── schemas.py             # Pydantic models for data structures
│   └── travel_tools.py        # Flight, Hotel, Itinerary tools
├── runner.py                  # Main execution script
├── simple_test.py            # Basic test script
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## Architecture

### Agent Hierarchy
```
ROOT_AGENT (Gemini 2.5 Pro)
  └── TRIP_PLANNER_TOOL
      └── PARALLEL_PLANNER
          ├── FLIGHT_AGENT (Gemini 2.5 Flash)
          │   └── FlightSearchTool → Amadeus API
          └── HOTEL_AGENT (Gemini 2.5 Flash)
              └── HotelSearchTool → Amadeus API
      └── ITINERARY_AGENT (Gemini 2.5 Flash)
          ├── ItineraryTool
          └── Google Search
```

### Key Components

1. **ROOT_AGENT**: Coordinates the entire planning workflow
2. **PARALLEL_PLANNER**: Runs flight and hotel searches concurrently
3. **FLIGHT_AGENT**: Searches and analyzes flight options
4. **HOTEL_AGENT**: Searches and analyzes hotel options
5. **ITINERARY_AGENT**: Creates day-by-day travel itineraries

## Troubleshooting

### Compatibility Issue Fixed
✅ **Issue**: Enum validation errors with Content messages  
✅ **Solution**: Use `google.genai.types` instead of `google.generativeai.protos`

### Common Issues

1. **Missing API Key Error**
   ```
   ValueError: Missing key inputs argument!
   ```
   **Solution**: Set `GOOGLE_API_KEY` environment variable

2. **Amadeus API Errors**
   - The system works with mock data if Amadeus credentials are not provided
   - For real data, ensure valid API credentials are set

3. **Import Errors**
   - Ensure virtual environment is activated
   - Reinstall dependencies: `pip install -r requirements.txt`

## Development

### Protected Methods
Methods prefixed with `_` (single underscore) are protected methods in Python:
- `_get_access_token()` - For internal OAuth handling
- Convention indicates internal/subclass use
- Not enforced by Python (just a naming convention)

### Adding New Agents
1. Define agent in `agents/specialized.py`
2. Create corresponding tool in `tools/travel_tools.py`
3. Add schema in `tools/schemas.py`
4. Integrate into orchestrator in `agents/orchestrators.py`

## Dependencies

- `google-adk`: Google Agent Development Kit
- `google-genai`: Google Generative AI client
- `pydantic`: Data validation
- `requests`: HTTP client for API calls

## License

This is a sample project for educational purposes.

## Notes

- The system uses mock data when API credentials are not provided
- Real Amadeus API calls may incur costs based on usage
- Google AI API has rate limits based on your tier
