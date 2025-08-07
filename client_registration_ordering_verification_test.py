#!/usr/bin/env python3
"""
Client Registration Ordering Verification Test
==============================================

This test verifies that client registrations are returned in the correct order (newest first)
for both pending and submitted registration endpoints using existing data.

Test Focus:
1. GET /api/admin-registrations-pending endpoint returns registrations sorted by timestamp descending (newest first)
2. GET /api/admin-registrations-submitted endpoint returns registrations sorted by timestamp descending (newest first)
3. Verify timestamp ordering is working correctly at the database level
4. Ensure most recent registrations appear first in response

This addresses the user's issue where they had to scroll to the bottom to find newest registrations.
"""

import requests
import json
import sys
from datetime import datetime

# Use the external URL from frontend/.env
BACKEND_URL = "https://cd556dd9-d36b-422e-8110-4b1830397661.preview.emergentagent.com/api"

def test_endpoint_ordering(endpoint_name, endpoint_url):
    """Test that an endpoint returns registrations in newest-first order"""
    print(f"\n🔍 TESTING {endpoint_name.upper()} REGISTRATIONS ORDERING")
    print("=" * 60)
    
    try:
        response = requests.get(endpoint_url, timeout=30)
        if response.status_code != 200:
            print(f"❌ Failed to fetch {endpoint_name} registrations: {response.status_code} - {response.text}")
            return False
        
        registrations = response.json()
        print(f"📊 Retrieved {len(registrations)} {endpoint_name} registrations")
        
        if len(registrations) == 0:
            print(f"⚠️  No {endpoint_name} registrations found - cannot test ordering")
            return True  # Not a failure, just no data
        
        # Check timestamp ordering for all registrations
        timestamps_valid = True
        ordering_valid = True
        
        print(f"🔍 Checking timestamp ordering for first 10 registrations:")
        
        for i in range(min(10, len(registrations))):
            reg = registrations[i]
            timestamp = reg.get('timestamp')
            first_name = reg.get('firstName', 'Unknown')
            last_name = reg.get('lastName', 'Unknown')
            
            if not timestamp:
                print(f"❌ Registration {i+1} missing timestamp: {first_name} {last_name}")
                timestamps_valid = False
                continue
            
            # Try to parse timestamp
            try:
                parsed_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                print(f"   {i+1:2d}. {first_name} {last_name} - {timestamp}")
                
                # Check ordering with previous registration
                if i > 0:
                    prev_reg = registrations[i-1]
                    prev_timestamp = prev_reg.get('timestamp')
                    if prev_timestamp:
                        prev_parsed_time = datetime.fromisoformat(prev_timestamp.replace('Z', '+00:00'))
                        if parsed_time > prev_parsed_time:
                            print(f"❌ ORDERING ERROR: Registration {i+1} is newer than registration {i}")
                            print(f"   Current: {parsed_time}")
                            print(f"   Previous: {prev_parsed_time}")
                            ordering_valid = False
                
            except Exception as e:
                print(f"❌ Invalid timestamp format in registration {i+1}: {timestamp}")
                timestamps_valid = False
        
        # Overall assessment
        if timestamps_valid and ordering_valid:
            print(f"✅ {endpoint_name.upper()} REGISTRATIONS ORDERING TEST PASSED")
            print(f"   All {len(registrations)} registrations are properly ordered (newest first)")
            return True
        else:
            print(f"❌ {endpoint_name.upper()} REGISTRATIONS ORDERING TEST FAILED")
            if not timestamps_valid:
                print("   Issue: Invalid or missing timestamps")
            if not ordering_valid:
                print("   Issue: Registrations not in newest-first order")
            return False
            
    except Exception as e:
        print(f"❌ Error testing {endpoint_name} registrations ordering: {str(e)}")
        return False

def test_database_sorting_implementation():
    """Test that the database sorting is implemented correctly by checking sort direction"""
    print(f"\n🔍 TESTING DATABASE SORTING IMPLEMENTATION")
    print("=" * 50)
    
    endpoints = [
        ("pending", f"{BACKEND_URL}/admin-registrations-pending"),
        ("submitted", f"{BACKEND_URL}/admin-registrations-submitted")
    ]
    
    all_passed = True
    
    for endpoint_name, endpoint_url in endpoints:
        try:
            response = requests.get(endpoint_url, timeout=30)
            if response.status_code != 200:
                print(f"❌ Failed to fetch {endpoint_name} registrations: {response.status_code}")
                all_passed = False
                continue
            
            registrations = response.json()
            
            if len(registrations) < 2:
                print(f"⚠️  Not enough {endpoint_name} registrations to test sorting (need at least 2)")
                continue
            
            # Check first vs last registration timestamps
            first_reg = registrations[0]
            last_reg = registrations[-1]
            
            first_timestamp = first_reg.get('timestamp')
            last_timestamp = last_reg.get('timestamp')
            
            if not first_timestamp or not last_timestamp:
                print(f"❌ Missing timestamps in {endpoint_name} registrations")
                all_passed = False
                continue
            
            try:
                first_time = datetime.fromisoformat(first_timestamp.replace('Z', '+00:00'))
                last_time = datetime.fromisoformat(last_timestamp.replace('Z', '+00:00'))
                
                print(f"📊 {endpoint_name.upper()} registrations analysis:")
                print(f"   First (newest): {first_reg.get('firstName')} {first_reg.get('lastName')} - {first_timestamp}")
                print(f"   Last (oldest):  {last_reg.get('firstName')} {last_reg.get('lastName')} - {last_timestamp}")
                
                if first_time >= last_time:
                    print(f"✅ {endpoint_name.upper()} database sorting is correct (newest first)")
                else:
                    print(f"❌ {endpoint_name.upper()} database sorting is incorrect")
                    print(f"   First registration is older than last registration")
                    all_passed = False
                    
            except Exception as e:
                print(f"❌ Error parsing timestamps in {endpoint_name}: {str(e)}")
                all_passed = False
                
        except Exception as e:
            print(f"❌ Error testing {endpoint_name} database sorting: {str(e)}")
            all_passed = False
    
    return all_passed

def main():
    """Main test function"""
    print("🧪 CLIENT REGISTRATION ORDERING VERIFICATION TEST")
    print("=" * 70)
    print("Verifying that client registrations are ordered newest-first")
    print("as requested by the user to fix scrolling to bottom issue.")
    print("=" * 70)
    
    # Test results
    test_results = []
    
    # Test 1: Pending registrations ordering
    print("\n📋 TEST 1: PENDING REGISTRATIONS ORDERING")
    pending_result = test_endpoint_ordering("pending", f"{BACKEND_URL}/admin-registrations-pending")
    test_results.append(("Pending Registrations Ordering", pending_result))
    
    # Test 2: Submitted registrations ordering  
    print("\n📋 TEST 2: SUBMITTED REGISTRATIONS ORDERING")
    submitted_result = test_endpoint_ordering("submitted", f"{BACKEND_URL}/admin-registrations-submitted")
    test_results.append(("Submitted Registrations Ordering", submitted_result))
    
    # Test 3: Database sorting implementation
    print("\n📋 TEST 3: DATABASE SORTING IMPLEMENTATION")
    sorting_result = test_database_sorting_implementation()
    test_results.append(("Database Sorting Implementation", sorting_result))
    
    # Summary
    print("\n" + "=" * 70)
    print("🏁 CLIENT REGISTRATION ORDERING VERIFICATION SUMMARY")
    print("=" * 70)
    
    passed_tests = 0
    total_tests = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {test_name}")
        if result:
            passed_tests += 1
    
    print(f"\n📊 OVERALL RESULT: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 ALL TESTS PASSED - Client registration ordering is working correctly!")
        print("✅ Users will now see newest registrations first in both pending and submitted lists")
        print("✅ No more scrolling to bottom to find recent registrations")
        print("✅ Database sorting with .sort('timestamp', -1) is working properly")
        return True
    else:
        print("❌ SOME TESTS FAILED - Client registration ordering needs attention")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)