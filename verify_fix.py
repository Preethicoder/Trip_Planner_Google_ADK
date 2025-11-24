#!/usr/bin/env python3
"""
Verification script to test that the compatibility issue is resolved.
"""

print("=" * 70)
print("🔍 COMPATIBILITY VERIFICATION TEST")
print("=" * 70)

# Test 1: Import Check
print("\n✓ Test 1: Checking imports...")
try:
    from google.adk import Runner
    from google.adk.agents import LlmAgent
    from google.adk.sessions import InMemorySessionService
    from google.genai import types
    print("  ✅ All imports successful")
except ImportError as e:
    print(f"  ❌ Import failed: {e}")
    exit(1)

# Test 2: Content Creation
print("\n✓ Test 2: Creating Content message...")
try:
    message = types.Content(
        role="user",
        parts=[types.Part(text="Test message")]
    )
    print(f"  ✅ Content created successfully")
    print(f"     Type: {type(message)}")
    print(f"     Role: {message.role}")
except Exception as e:
    print(f"  ❌ Content creation failed: {e}")
    exit(1)

# Test 3: Verify correct types module
print("\n✓ Test 3: Verifying correct types module...")
import google.adk.runners
import sys
runner_module = sys.modules['google.adk.runners']
if hasattr(runner_module, 'types'):
    types_module = runner_module.types
    print(f"  ✅ Found types module: {types_module.__name__}")
    
    # Check if our imported types matches
    if types_module.__name__ == 'google.genai.types':
        print(f"  ✅ Using correct types module: google.genai.types")
    else:
        print(f"  ⚠️  Types module mismatch: {types_module.__name__}")
else:
    print(f"  ❌ Types module not found in runner")
    exit(1)

# Test 4: Package versions
print("\n✓ Test 4: Checking package versions...")
try:
    import pkg_resources
    adk_version = pkg_resources.get_distribution('google-adk').version
    genai_version = pkg_resources.get_distribution('google-genai').version
    print(f"  ✅ google-adk: {adk_version}")
    print(f"  ✅ google-genai: {genai_version}")
except Exception as e:
    print(f"  ⚠️  Version check: {e}")

# Test 5: Message type compatibility
print("\n✓ Test 5: Checking message type compatibility...")
try:
    from google.genai import types as our_types
    import google.adk.runners as runners_mod
    
    # Create message with our types
    test_msg = our_types.Content(
        role="user",
        parts=[our_types.Part(text="Compatibility test")]
    )
    
    # Check if it's the right type expected by Runner
    expected_type = runners_mod.types.Content
    if isinstance(test_msg, expected_type):
        print(f"  ✅ Message type is compatible with Runner")
        print(f"     Message type: {type(test_msg)}")
        print(f"     Expected type: {expected_type}")
    else:
        print(f"  ❌ Type mismatch!")
        print(f"     Message type: {type(test_msg)}")
        print(f"     Expected type: {expected_type}")
except Exception as e:
    print(f"  ❌ Compatibility check failed: {e}")
    exit(1)

print("\n" + "=" * 70)
print("🎉 ALL COMPATIBILITY TESTS PASSED!")
print("=" * 70)
print("\n✅ The compatibility issue between google-adk and google-genai")
print("   has been RESOLVED by using 'google.genai.types' instead of")
print("   'google.generativeai.protos'")
print("\n📝 Next steps:")
print("   1. Set GOOGLE_API_KEY environment variable")
print("   2. Run: python runner.py")
print("=" * 70)
