#!/usr/bin/env python3
"""
Final Test Management API Timestamp Verification
Focused test to verify timestamp enhancement is working correctly
"""

import requests
import json
import time
from datetime import datetime, timedelta
import pytz

# Get backend URL from environment
BACKEND_URL = "https://dfe9a1e1-7f3d-45aa-ad71-43a254e568c5.preview.emergentagent.com/api"

def test_timestamp_enhancement():
    """Comprehensive test of timestamp enhancement for test records"""
    print("🧪 FINAL TIMESTAMP ENHANCEMENT VERIFICATION")
    print("=" * 60)
    
    # Create a unique registration for this test
    timestamp_suffix = int(time.time())
    registration_data = {
        "firstName": f"Timestamp",
        "lastName": f"Test{timestamp_suffix}",
        "patientConsent": "verbal",
        "dob": "1990-05-15",
        "gender": "Male",
        "province": "Ontario"
    }
    
    print("\n1️⃣ Creating test registration...")
    try:
        response = requests.post(f"{BACKEND_URL}/admin-register", json=registration_data)
        if response.status_code in [200, 201]:
            registration = response.json()
            registration_id = registration.get('registration_id')
            print(f"✅ Registration created: {registration_id}")
        else:
            print(f"❌ Failed to create registration: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error creating registration: {str(e)}")
        return False
    
    # Test 1: Create test and verify created_at timestamp
    print("\n2️⃣ Testing created_at timestamp...")
    before_create = datetime.now(pytz.timezone('America/Toronto'))
    
    test_data = {
        "test_type": "HIV",
        "test_date": "2025-01-15",
        "hiv_result": "negative",
        "hiv_type": "Type 1",
        "hiv_tester": "TS"
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/admin-registration/{registration_id}/test", json=test_data)
        if response.status_code in [200, 201]:
            test_response = response.json()
            test_id = test_response.get('test_id')
            print(f"✅ Test created with ID: {test_id}")
            
            # Retrieve test to check timestamps
            get_response = requests.get(f"{BACKEND_URL}/admin-registration/{registration_id}/tests")
            if get_response.status_code == 200:
                tests_data = get_response.json()
                tests = tests_data.get('tests', [])
                
                # Find our test
                our_test = None
                for test in tests:
                    if test.get('id') == test_id:
                        our_test = test
                        break
                
                if our_test:
                    # Verify created_at timestamp
                    if 'created_at' in our_test:
                        created_at_str = our_test['created_at']
                        print(f"✅ created_at timestamp: {created_at_str}")
                        
                        # Verify format
                        try:
                            created_at = datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))
                            print(f"✅ created_at format is valid ISO")
                        except Exception as e:
                            print(f"❌ Invalid created_at format: {str(e)}")
                            return False
                    else:
                        print(f"❌ created_at timestamp missing")
                        return False
                    
                    # Verify updated_at timestamp
                    if 'updated_at' in our_test:
                        updated_at_str = our_test['updated_at']
                        print(f"✅ updated_at timestamp: {updated_at_str}")
                        
                        # Verify format
                        try:
                            updated_at = datetime.fromisoformat(updated_at_str.replace('Z', '+00:00'))
                            print(f"✅ updated_at format is valid ISO")
                        except Exception as e:
                            print(f"❌ Invalid updated_at format: {str(e)}")
                            return False
                    else:
                        print(f"❌ updated_at timestamp missing")
                        return False
                    
                    # Verify initially they are the same
                    if created_at_str == updated_at_str:
                        print(f"✅ created_at and updated_at initially identical")
                    else:
                        print(f"⚠️ created_at and updated_at differ initially")
                        
                else:
                    print(f"❌ Could not find our test in response")
                    return False
            else:
                print(f"❌ Failed to retrieve tests: {get_response.status_code}")
                return False
        else:
            print(f"❌ Failed to create test: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error in test creation: {str(e)}")
        return False
    
    # Test 2: Update test and verify updated_at changes
    print("\n3️⃣ Testing updated_at timestamp update...")
    
    # Wait to ensure timestamp difference
    time.sleep(2)
    
    original_created_at = our_test['created_at']
    original_updated_at = our_test['updated_at']
    
    update_data = {
        "hiv_result": "positive",
        "hiv_type": "Type 2"
    }
    
    try:
        response = requests.put(f"{BACKEND_URL}/admin-registration/{registration_id}/test/{test_id}", json=update_data)
        if response.status_code == 200:
            print(f"✅ Test updated successfully")
            
            # Retrieve updated test
            get_response = requests.get(f"{BACKEND_URL}/admin-registration/{registration_id}/tests")
            if get_response.status_code == 200:
                tests_data = get_response.json()
                tests = tests_data.get('tests', [])
                
                # Find our updated test
                updated_test = None
                for test in tests:
                    if test.get('id') == test_id:
                        updated_test = test
                        break
                
                if updated_test:
                    new_created_at = updated_test['created_at']
                    new_updated_at = updated_test['updated_at']
                    
                    # Verify created_at unchanged
                    if new_created_at == original_created_at:
                        print(f"✅ created_at remained unchanged: {new_created_at}")
                    else:
                        print(f"❌ created_at changed unexpectedly: {original_created_at} -> {new_created_at}")
                        return False
                    
                    # Verify updated_at changed
                    if new_updated_at != original_updated_at:
                        print(f"✅ updated_at changed: {original_updated_at} -> {new_updated_at}")
                        
                        # Verify updated_at is later
                        try:
                            original_dt = datetime.fromisoformat(original_updated_at.replace('Z', '+00:00'))
                            new_dt = datetime.fromisoformat(new_updated_at.replace('Z', '+00:00'))
                            
                            if new_dt > original_dt:
                                print(f"✅ updated_at is later than original")
                            else:
                                print(f"❌ updated_at is not later than original")
                                return False
                        except Exception as e:
                            print(f"❌ Error comparing timestamps: {str(e)}")
                            return False
                    else:
                        print(f"❌ updated_at did not change after update")
                        return False
                else:
                    print(f"❌ Could not find updated test")
                    return False
            else:
                print(f"❌ Failed to retrieve updated tests: {get_response.status_code}")
                return False
        else:
            print(f"❌ Failed to update test: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error updating test: {str(e)}")
        return False
    
    # Test 3: Verify frontend display format
    print("\n4️⃣ Testing frontend display format...")
    
    try:
        # Parse timestamps for display
        created_at = datetime.fromisoformat(new_created_at.replace('Z', '+00:00'))
        updated_at = datetime.fromisoformat(new_updated_at.replace('Z', '+00:00'))
        
        # Convert to Toronto timezone
        toronto_tz = pytz.timezone('America/Toronto')
        created_display = created_at.astimezone(toronto_tz).strftime('%Y-%m-%d %H:%M:%S %Z')
        updated_display = updated_at.astimezone(toronto_tz).strftime('%Y-%m-%d %H:%M:%S %Z')
        
        print(f"✅ Frontend display format:")
        print(f"   Created:  {created_display}")
        print(f"   Updated:  {updated_display}")
        
        # Verify they can be parsed for sorting/comparison
        if updated_at > created_at:
            print(f"✅ Timestamps can be compared for sorting")
        else:
            print(f"⚠️ Timestamp comparison issue")
            
    except Exception as e:
        print(f"❌ Error formatting for frontend: {str(e)}")
        return False
    
    # Test 4: Test different test types have timestamps
    print("\n5️⃣ Testing timestamps for different test types...")
    
    test_types_to_test = [
        {
            "name": "HCV",
            "data": {
                "test_type": "HCV",
                "test_date": "2025-01-16",
                "hcv_result": "positive",
                "hcv_tester": "TS"
            }
        },
        {
            "name": "Bloodwork",
            "data": {
                "test_type": "Bloodwork",
                "test_date": "2025-01-17",
                "bloodwork_type": "DBS",
                "bloodwork_circles": "3",
                "bloodwork_result": "Pending",
                "bloodwork_tester": "TS"
            }
        }
    ]
    
    for test_type in test_types_to_test:
        try:
            response = requests.post(f"{BACKEND_URL}/admin-registration/{registration_id}/test", json=test_type['data'])
            if response.status_code in [200, 201]:
                print(f"✅ {test_type['name']} test created successfully")
            else:
                print(f"❌ Failed to create {test_type['name']} test: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error creating {test_type['name']} test: {str(e)}")
            return False
    
    # Verify all tests have timestamps
    try:
        response = requests.get(f"{BACKEND_URL}/admin-registration/{registration_id}/tests")
        if response.status_code == 200:
            tests_data = response.json()
            tests = tests_data.get('tests', [])
            
            timestamp_count = 0
            for test in tests:
                if 'created_at' in test and 'updated_at' in test:
                    timestamp_count += 1
            
            print(f"✅ {timestamp_count} tests have both timestamps")
            
            if timestamp_count >= 3:  # We created at least 3 tests
                print(f"✅ All test types support timestamps")
            else:
                print(f"❌ Not all tests have timestamps")
                return False
                
        else:
            print(f"❌ Failed to retrieve final tests: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error verifying final tests: {str(e)}")
        return False
    
    print("\n" + "=" * 60)
    print("🎉 TIMESTAMP ENHANCEMENT VERIFICATION COMPLETE!")
    print("✅ Test registration creation works")
    print("✅ Test record creation includes created_at timestamp")
    print("✅ Test retrieval returns both created_at and updated_at timestamps")
    print("✅ Test update properly updates updated_at while preserving created_at")
    print("✅ Timestamps are in correct ISO format")
    print("✅ Timestamps can be formatted for frontend display")
    print("✅ All test types (HIV, HCV, Bloodwork) support timestamps")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    print("🚀 STARTING FINAL TIMESTAMP ENHANCEMENT VERIFICATION")
    
    if test_timestamp_enhancement():
        print("\n🎉 ALL TIMESTAMP ENHANCEMENT TESTS PASSED!")
        print("The timestamp enhancement for test records is working correctly.")
    else:
        print("\n❌ TIMESTAMP ENHANCEMENT TESTS FAILED!")
        print("Please check the error messages above for details.")