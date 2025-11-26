"""
Direct tool testing script to verify Amadeus API integration
Tests FlightSearchTool and HotelSearchTool independently
"""
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

print("=" * 80)
print("DIRECT TOOL TEST SCRIPT")
print("=" * 80)

# Check environment variables
print("\n📋 Environment Check:")
print(f"   GOOGLE_API_KEY: {'✓ Set' if os.getenv('GOOGLE_API_KEY') else '✗ Missing'}")
print(f"   AMADEUS_API_KEY: {os.getenv('AMADEUS_API_KEY', 'NOT SET')}")
print(f"   AMADEUS_API_SECRET: {os.getenv('AMADEUS_API_SECRET', 'NOT SET')[:20]}..." if os.getenv('AMADEUS_API_SECRET') else "   AMADEUS_API_SECRET: NOT SET")

# Import tools
print("\n📦 Importing tools...")
from tools.travel_tools import FLIGHT_TOOL, HOTEL_TOOL

print("   ✓ FlightSearchTool imported")
print("   ✓ HotelSearchTool imported")

# Test 1: Flight Search Tool
print("\n" + "=" * 80)
print("TEST 1: FLIGHT SEARCH TOOL")
print("=" * 80)
print("Parameters:")
print("   Origin: MAA (Chennai)")
print("   Destination: BSL (Basel)")
print("   Departure: 2025-12-15")
print("   Adults: 2")
print("\nExecuting flight search...")
print("-" * 80)

try:
    flight_result = FLIGHT_TOOL.run(
        originLocationCode="MAA",
        destinationLocationCode="BSL",
        departureDate="2025-12-15",
        adults=2
    )
    print("-" * 80)
    print("✅ FLIGHT TOOL EXECUTED SUCCESSFULLY")
    print(f"Result type: {type(flight_result)}")
    print(f"Result: {flight_result}")
except Exception as e:
    print("-" * 80)
    print(f"❌ FLIGHT TOOL FAILED")
    print(f"Error type: {type(e).__name__}")
    print(f"Error message: {str(e)}")

# Test 2: Hotel Search Tool
print("\n" + "=" * 80)
print("TEST 2: HOTEL SEARCH TOOL")
print("=" * 80)
print("Parameters:")
print("   City Code: BSL (Basel)")
print("   Check-in: 2025-12-15")
print("   Check-out: 2025-12-19")
print("   Max Budget: 200 EUR")
print("\nExecuting hotel search...")
print("-" * 80)

try:
    hotel_result = HOTEL_TOOL.run(
        cityCode="BSL",
        check_in="2025-12-15",
        check_out="2025-12-19",
        max_budget=200.0
    )
    print("-" * 80)
    print("✅ HOTEL TOOL EXECUTED SUCCESSFULLY")
    print(f"Result type: {type(hotel_result)}")
    print(f"Result: {hotel_result}")
except Exception as e:
    print("-" * 80)
    print(f"❌ HOTEL TOOL FAILED")
    print(f"Error type: {type(e).__name__}")
    print(f"Error message: {str(e)}")

print("\n" + "=" * 80)
print("DIRECT TOOL TEST COMPLETE")
print("=" * 80)
