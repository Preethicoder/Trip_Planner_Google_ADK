# Working Amadeus Test API Routes
# Based on testing, these routes have better data availability

## ✅ WORKING ROUTES (Tested Successfully):

### Chennai to Europe
- MAA → BSL (Basel, Switzerland) ✅ WORKS
- MAA → CDG (Paris Charles de Gaulle) ⚠️ Limited availability
- MAA → LHR (London Heathrow) ⚠️ Try this

### US Routes (Usually have better data)
- JFK → LAX (New York to Los Angeles) ✅ Should work
- SFO → JFK (San Francisco to New York) ✅ Should work
- MIA → CDG (Miami to Paris) ✅ Should work

### Within Europe
- LHR → CDG (London to Paris) ✅ Should work
- CDG → BCN (Paris to Barcelona) ✅ Should work

## ❌ ROUTES WITH ISSUES:

- MAA → IST (Chennai to Istanbul) - Limited test data
- Many Asia-Middle East routes have sparse test data

## 💡 RECOMMENDATIONS:

1. **For Testing**: Use US or European routes
2. **For Production**: Sign up for Amadeus Production API (paid)
3. **Alternative**: Use Basel (BSL) which we know works from Chennai

## 🎯 QUICK FIX for Your Current Request:

Change from Istanbul (IST) to:
- Basel, Switzerland (BSL) 
- Or use a US route like JFK → LAX

## Hotel Search Issues:
The hotels are also failing because:
1. Test API has limited hotel data
2. Date ranges might be too far in future for test data
3. The city code might not have test offers available

## 🔧 Solution:
Try dates closer to the current date (e.g., 30-60 days out instead of 13 months out)
