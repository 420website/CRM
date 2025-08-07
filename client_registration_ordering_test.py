#!/usr/bin/env python3
"""
Client Registration Ordering Test
=================================

This test verifies that client registrations are returned in the correct order (newest first)
for both pending and submitted registration endpoints as requested by the user.

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
from datetime import datetime, timedelta
import pytz
import time

# Use the external URL from frontend/.env
BACKEND_URL = "https://cd556dd9-d36b-422e-8110-4b1830397661.preview.emergentagent.com/api"

def create_test_registration(first_name, last_name, timestamp_offset_hours=0):
    """Create a test registration with a specific timestamp offset"""
    
    # Calculate timestamp with offset
    toronto_tz = pytz.timezone('America/Toronto')
    base_time = datetime.now(toronto_tz)
    test_time = base_time - timedelta(hours=timestamp_offset_hours)
    
    registration_data = {
        "firstName": first_name,
        "lastName": last_name,
        "patientConsent": "verbal",
        "province": "Ontario",
        "regDate": test_time.strftime('%Y-%m-%d'),
        "timestamp": test_time.isoformat()
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/admin-register", json=registration_data, timeout=30)
        if response.status_code in [200, 201]:
            result = response.json()
            print(f"✅ Created test registration: {first_name} {last_name} (ID: {result.get('registration_id')}) at {test_time.strftime('%Y-%m-%d %H:%M:%S')}")
            return result.get('registration_id'), test_time
        else:
            print(f"❌ Failed to create registration for {first_name} {last_name}: {response.status_code} - {response.text}")
            return None, None
    except Exception as e:
        print(f"❌ Error creating registration for {first_name} {last_name}: {str(e)}")
        return None, None

def finalize_registration(registration_id):
    """Finalize a registration to move it to submitted status"""
    try:
        response = requests.post(f"{BACKEND_URL}/admin-registration/{registration_id}/finalize", timeout=30)
        if response.status_code == 200:
            print(f"✅ Finalized registration: {registration_id}")
            return True
        else:
            print(f"❌ Failed to finalize registration {registration_id}: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error finalizing registration {registration_id}: {str(e)}")
        return False

def test_pending_registrations_ordering():
    """Test that pending registrations are returned in newest-first order"""
    print("\n🔍 TESTING PENDING REGISTRATIONS ORDERING")
    print("=" * 50)
    
    # Create test registrations with different timestamps (hours ago)
    test_registrations = [
        ("Alice", "Oldest", 24),    # 24 hours ago (oldest)
        ("Bob", "Middle", 12),      # 12 hours ago (middle)
        ("Charlie", "Newest", 1)    # 1 hour ago (newest)
    ]
    
    created_registrations = []
    
    # Create test registrations
    for first_name, last_name, hours_ago in test_registrations:
        reg_id, timestamp = create_test_registration(first_name, last_name, hours_ago)
        if reg_id:
            created_registrations.append((reg_id, first_name, last_name, timestamp))
        time.sleep(1)  # Small delay between creations
    
    if len(created_registrations) < 3:
        print("❌ Failed to create enough test registrations for ordering test")
        return False
    
    # Wait a moment for database consistency
    time.sleep(2)
    
    # Test the pending registrations endpoint
    try:
        response = requests.get(f"{BACKEND_URL}/admin-registrations-pending", timeout=30)
        if response.status_code != 200:
            print(f"❌ Failed to fetch pending registrations: {response.status_code} - {response.text}")
            return False
        
        registrations = response.json()
        print(f"📊 Retrieved {len(registrations)} pending registrations")
        
        # Find our test registrations in the response
        test_reg_positions = {}
        for i, reg in enumerate(registrations):
            for reg_id, first_name, last_name, timestamp in created_registrations:
                if reg.get('id') == reg_id:
                    test_reg_positions[first_name] = {
                        'position': i,
                        'timestamp': reg.get('timestamp'),
                        'firstName': reg.get('firstName'),
                        'lastName': reg.get('lastName')
                    }
        
        print(f"🔍 Found {len(test_reg_positions)} test registrations in response:")
        for name, info in test_reg_positions.items():
            print(f"   {name}: Position {info['position']}, Timestamp: {info['timestamp']}")
        
        # Verify ordering (newest should come first)
        if len(test_reg_positions) >= 3:
            charlie_pos = test_reg_positions.get('Charlie', {}).get('position', 999)
            bob_pos = test_reg_positions.get('Bob', {}).get('position', 999)
            alice_pos = test_reg_positions.get('Alice', {}).get('position', 999)
            
            if charlie_pos < bob_pos < alice_pos:
                print("✅ PENDING REGISTRATIONS ORDERING TEST PASSED")
                print(f"   Charlie (newest) at position {charlie_pos}")
                print(f"   Bob (middle) at position {bob_pos}")
                print(f"   Alice (oldest) at position {alice_pos}")
                return True
            else:
                print("❌ PENDING REGISTRATIONS ORDERING TEST FAILED")
                print(f"   Expected: Charlie < Bob < Alice")
                print(f"   Actual: Charlie({charlie_pos}) Bob({bob_pos}) Alice({alice_pos})")
                return False
        else:
            print("❌ Could not find enough test registrations in response for ordering verification")
            return False
            
    except Exception as e:
        print(f"❌ Error testing pending registrations ordering: {str(e)}")
        return False

def test_submitted_registrations_ordering():
    """Test that submitted registrations are returned in newest-first order"""
    print("\n🔍 TESTING SUBMITTED REGISTRATIONS ORDERING")
    print("=" * 50)
    
    # Create test registrations with different timestamps (hours ago)
    test_registrations = [
        ("David", "OldSubmitted", 48),    # 48 hours ago (oldest)
        ("Eve", "MidSubmitted", 24),      # 24 hours ago (middle)
        ("Frank", "NewSubmitted", 2)      # 2 hours ago (newest)
    ]
    
    created_registrations = []
    
    # Create and finalize test registrations
    for first_name, last_name, hours_ago in test_registrations:
        reg_id, timestamp = create_test_registration(first_name, last_name, hours_ago)
        if reg_id:
            time.sleep(1)  # Small delay
            if finalize_registration(reg_id):
                created_registrations.append((reg_id, first_name, last_name, timestamp))
        time.sleep(1)  # Small delay between creations
    
    if len(created_registrations) < 3:
        print("❌ Failed to create enough finalized test registrations for ordering test")
        return False
    
    # Wait a moment for database consistency
    time.sleep(3)
    
    # Test the submitted registrations endpoint
    try:
        response = requests.get(f"{BACKEND_URL}/admin-registrations-submitted", timeout=30)
        if response.status_code != 200:
            print(f"❌ Failed to fetch submitted registrations: {response.status_code} - {response.text}")
            return False
        
        registrations = response.json()
        print(f"📊 Retrieved {len(registrations)} submitted registrations")
        
        # Find our test registrations in the response
        test_reg_positions = {}
        for i, reg in enumerate(registrations):
            for reg_id, first_name, last_name, timestamp in created_registrations:
                if reg.get('id') == reg_id:
                    test_reg_positions[first_name] = {
                        'position': i,
                        'timestamp': reg.get('timestamp'),
                        'firstName': reg.get('firstName'),
                        'lastName': reg.get('lastName')
                    }
        
        print(f"🔍 Found {len(test_reg_positions)} test registrations in response:")
        for name, info in test_reg_positions.items():
            print(f"   {name}: Position {info['position']}, Timestamp: {info['timestamp']}")
        
        # Verify ordering (newest should come first)
        if len(test_reg_positions) >= 3:
            frank_pos = test_reg_positions.get('Frank', {}).get('position', 999)
            eve_pos = test_reg_positions.get('Eve', {}).get('position', 999)
            david_pos = test_reg_positions.get('David', {}).get('position', 999)
            
            if frank_pos < eve_pos < david_pos:
                print("✅ SUBMITTED REGISTRATIONS ORDERING TEST PASSED")
                print(f"   Frank (newest) at position {frank_pos}")
                print(f"   Eve (middle) at position {eve_pos}")
                print(f"   David (oldest) at position {david_pos}")
                return True
            else:
                print("❌ SUBMITTED REGISTRATIONS ORDERING TEST FAILED")
                print(f"   Expected: Frank < Eve < David")
                print(f"   Actual: Frank({frank_pos}) Eve({eve_pos}) David({david_pos})")
                return False
        else:
            print("❌ Could not find enough test registrations in response for ordering verification")
            return False
            
    except Exception as e:
        print(f"❌ Error testing submitted registrations ordering: {str(e)}")
        return False

def test_timestamp_consistency():
    """Test that timestamps are consistent and properly formatted"""
    print("\n🔍 TESTING TIMESTAMP CONSISTENCY")
    print("=" * 40)
    
    # Test both endpoints for timestamp format consistency
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
            print(f"📊 Testing {len(registrations)} {endpoint_name} registrations for timestamp consistency")
            
            if len(registrations) == 0:
                print(f"⚠️  No {endpoint_name} registrations found for timestamp testing")
                continue
            
            # Check first few registrations for timestamp ordering
            timestamps_valid = True
            for i in range(min(5, len(registrations))):
                reg = registrations[i]
                timestamp = reg.get('timestamp')
                
                if not timestamp:
                    print(f"❌ Registration {i} missing timestamp in {endpoint_name}")
                    timestamps_valid = False
                    continue
                
                # Try to parse timestamp
                try:
                    parsed_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    print(f"   ✅ Registration {i}: {reg.get('firstName', 'Unknown')} {reg.get('lastName', 'Unknown')} - {timestamp}")
                except Exception as e:
                    print(f"❌ Invalid timestamp format in {endpoint_name} registration {i}: {timestamp}")
                    timestamps_valid = False
            
            # Check ordering of first few timestamps
            if len(registrations) >= 2:
                try:
                    first_time = datetime.fromisoformat(registrations[0].get('timestamp', '').replace('Z', '+00:00'))
                    second_time = datetime.fromisoformat(registrations[1].get('timestamp', '').replace('Z', '+00:00'))
                    
                    if first_time >= second_time:
                        print(f"✅ {endpoint_name.upper()} timestamps properly ordered (newest first)")
                    else:
                        print(f"❌ {endpoint_name.upper()} timestamps NOT properly ordered")
                        print(f"   First: {first_time}")
                        print(f"   Second: {second_time}")
                        timestamps_valid = False
                except Exception as e:
                    print(f"❌ Error comparing timestamps in {endpoint_name}: {str(e)}")
                    timestamps_valid = False
            
            if not timestamps_valid:
                all_passed = False
                
        except Exception as e:
            print(f"❌ Error testing {endpoint_name} timestamps: {str(e)}")
            all_passed = False
    
    return all_passed

def main():
    """Main test function"""
    print("🧪 CLIENT REGISTRATION ORDERING TEST")
    print("=" * 60)
    print("Testing that client registrations are ordered newest-first")
    print("as requested by the user to fix scrolling to bottom issue.")
    print("=" * 60)
    
    # Test results
    test_results = []
    
    # Test 1: Pending registrations ordering
    print("\n📋 TEST 1: PENDING REGISTRATIONS ORDERING")
    pending_result = test_pending_registrations_ordering()
    test_results.append(("Pending Registrations Ordering", pending_result))
    
    # Test 2: Submitted registrations ordering  
    print("\n📋 TEST 2: SUBMITTED REGISTRATIONS ORDERING")
    submitted_result = test_submitted_registrations_ordering()
    test_results.append(("Submitted Registrations Ordering", submitted_result))
    
    # Test 3: Timestamp consistency
    print("\n📋 TEST 3: TIMESTAMP CONSISTENCY")
    timestamp_result = test_timestamp_consistency()
    test_results.append(("Timestamp Consistency", timestamp_result))
    
    # Summary
    print("\n" + "=" * 60)
    print("🏁 CLIENT REGISTRATION ORDERING TEST SUMMARY")
    print("=" * 60)
    
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
        return True
    else:
        print("❌ SOME TESTS FAILED - Client registration ordering needs attention")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)