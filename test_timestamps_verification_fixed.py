#!/usr/bin/env python3
"""
Test Management API Timestamp Verification
Testing that timestamps (created_at and updated_at) are properly saved and returned
"""

import requests
import json
import time
from datetime import datetime, timedelta
import pytz

# Get backend URL from environment
BACKEND_URL = "https://258401ff-ff29-421c-8498-4969ee7788f0.preview.emergentagent.com/api"

def test_timestamp_functionality():
    """Test complete timestamp functionality for test management"""
    print("🧪 TESTING TEST MANAGEMENT API TIMESTAMP FUNCTIONALITY")
    print("=" * 60)
    
    # Step 1: Create a test registration
    print("\n1️⃣ Creating test registration...")
    registration_data = {
        "firstName": "Timothy",
        "lastName": "TestUser",
        "patientConsent": "verbal",
        "dob": "1990-05-15",
        "gender": "Male",
        "province": "Ontario"
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/admin-register", json=registration_data)
        if response.status_code in [200, 201]:
            registration = response.json()
            registration_id = registration.get('registration_id')
            print(f"✅ Registration created successfully: {registration_id}")
        else:
            print(f"❌ Failed to create registration: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error creating registration: {str(e)}")
        return False
    
    # Step 2: Add a new test record and verify created_at timestamp
    print("\n2️⃣ Adding new test record and verifying created_at timestamp...")
    
    # Record time before creating test
    before_create_time = datetime.now(pytz.timezone('America/Toronto'))
    
    test_data = {
        "test_type": "HIV",
        "test_date": "2025-01-15",
        "hiv_result": "negative",
        "hiv_type": "Type 1",
        "hiv_tester": "TT"
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/admin-registration/{registration_id}/test", json=test_data)
        if response.status_code in [200, 201]:
            test_response = response.json()
            print(f"✅ Test record created successfully")
            print(f"📋 Response: {test_response}")
            
            # Get test_id from response
            test_id = test_response.get('test_id')
            if not test_id:
                print(f"❌ test_id missing from response")
                return False
            
            # Retrieve the full test record to check timestamps
            print(f"📋 Retrieving full test record to verify timestamps...")
            get_response = requests.get(f"{BACKEND_URL}/admin-registration/{registration_id}/tests")
            if get_response.status_code == 200:
                tests_data = get_response.json()
                tests = tests_data.get('tests', [])
                
                if len(tests) > 0:
                    test_record = tests[0]  # Get the first (and should be only) test
                    print(f"✅ Retrieved test record with timestamps")
                    
                    # Verify created_at timestamp is present
                    if 'created_at' in test_record:
                        created_at_str = test_record['created_at']
                        print(f"✅ created_at timestamp present: {created_at_str}")
                        
                        # Parse and verify timestamp format
                        try:
                            created_at = datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))
                            print(f"✅ Timestamp format is valid ISO format")
                            
                            # Verify timestamp is recent (within last minute)
                            time_diff = abs((created_at.replace(tzinfo=pytz.UTC) - before_create_time.astimezone(pytz.UTC)).total_seconds())
                            if time_diff < 60:
                                print(f"✅ Timestamp is recent (within {time_diff:.1f} seconds)")
                            else:
                                print(f"⚠️ Timestamp seems old: {time_diff:.1f} seconds ago")
                                
                        except Exception as e:
                            print(f"❌ Error parsing created_at timestamp: {str(e)}")
                            return False
                    else:
                        print(f"❌ created_at timestamp missing from test record")
                        return False
                        
                    # Store test_id for later update test
                    test_id = test_record.get('id')
                    
                else:
                    print(f"❌ No test records found after creation")
                    return False
            else:
                print(f"❌ Failed to retrieve test records: {get_response.status_code}")
                return False
                
        else:
            print(f"❌ Failed to create test: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error creating test: {str(e)}")
        return False
    
    # Step 3: Retrieve test records and verify timestamps are returned
    print("\n3️⃣ Retrieving test records and verifying timestamps...")
    
    try:
        response = requests.get(f"{BACKEND_URL}/admin-registration/{registration_id}/tests")
        if response.status_code == 200:
            tests_response = response.json()
            print(f"✅ Tests retrieved successfully")
            
            # Check response format
            if 'tests' in tests_response and isinstance(tests_response['tests'], list):
                tests = tests_response['tests']
                print(f"✅ Response format correct: {{'tests': [...]}}")
                
                if len(tests) > 0:
                    test = tests[0]
                    print(f"✅ Found {len(tests)} test record(s)")
                    
                    # Verify both timestamps are present
                    required_timestamps = ['created_at', 'updated_at']
                    for timestamp_field in required_timestamps:
                        if timestamp_field in test:
                            timestamp_value = test[timestamp_field]
                            print(f"✅ {timestamp_field} present: {timestamp_value}")
                            
                            # Verify timestamp format
                            try:
                                parsed_timestamp = datetime.fromisoformat(timestamp_value.replace('Z', '+00:00'))
                                print(f"✅ {timestamp_field} format is valid")
                            except Exception as e:
                                print(f"❌ Invalid {timestamp_field} format: {str(e)}")
                                return False
                        else:
                            print(f"❌ {timestamp_field} missing from test record")
                            return False
                            
                    # Verify created_at and updated_at are initially the same
                    if test['created_at'] == test['updated_at']:
                        print(f"✅ created_at and updated_at are initially identical (as expected)")
                    else:
                        print(f"⚠️ created_at and updated_at differ initially: {test['created_at']} vs {test['updated_at']}")
                        
                else:
                    print(f"❌ No test records found")
                    return False
            else:
                print(f"❌ Invalid response format: {tests_response}")
                return False
        else:
            print(f"❌ Failed to retrieve tests: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error retrieving tests: {str(e)}")
        return False
    
    # Step 4: Update test record and verify updated_at timestamp is properly updated
    print("\n4️⃣ Updating test record and verifying updated_at timestamp...")
    
    # Wait a moment to ensure timestamp difference
    time.sleep(2)
    
    # Record time before update
    before_update_time = datetime.now(pytz.timezone('America/Toronto'))
    original_created_at = test['created_at']
    original_updated_at = test['updated_at']
    
    update_data = {
        "hiv_result": "positive",
        "hiv_type": "Type 2",
        "hiv_tester": "CM"
    }
    
    try:
        response = requests.put(f"{BACKEND_URL}/admin-registration/{registration_id}/test/{test_id}", json=update_data)
        if response.status_code == 200:
            print(f"✅ Test record updated successfully")
            
            # Retrieve updated test to check timestamps
            get_response = requests.get(f"{BACKEND_URL}/admin-registration/{registration_id}/tests")
            if get_response.status_code == 200:
                tests_data = get_response.json()
                updated_test = tests_data['tests'][0]
                
                # Verify updated_at timestamp changed
                if 'updated_at' in updated_test:
                    new_updated_at = updated_test['updated_at']
                    print(f"✅ New updated_at timestamp: {new_updated_at}")
                    
                    # Verify updated_at changed
                    if new_updated_at != original_updated_at:
                        print(f"✅ updated_at timestamp properly updated")
                        
                        # Verify created_at remained the same
                        if 'created_at' in updated_test:
                            new_created_at = updated_test['created_at']
                            if new_created_at == original_created_at:
                                print(f"✅ created_at timestamp remained unchanged: {new_created_at}")
                            else:
                                print(f"❌ created_at timestamp unexpectedly changed: {original_created_at} -> {new_created_at}")
                                return False
                        else:
                            print(f"❌ created_at missing from updated test record")
                            return False
                            
                        # Verify new updated_at is recent
                        try:
                            updated_at_parsed = datetime.fromisoformat(new_updated_at.replace('Z', '+00:00'))
                            time_diff = abs((updated_at_parsed.replace(tzinfo=pytz.UTC) - before_update_time.astimezone(pytz.UTC)).total_seconds())
                            if time_diff < 60:
                                print(f"✅ New updated_at timestamp is recent (within {time_diff:.1f} seconds)")
                            else:
                                print(f"⚠️ New updated_at timestamp seems old: {time_diff:.1f} seconds ago")
                        except Exception as e:
                            print(f"❌ Error parsing new updated_at timestamp: {str(e)}")
                            return False
                            
                    else:
                        print(f"❌ updated_at timestamp did not change after update")
                        return False
                else:
                    print(f"❌ updated_at timestamp missing from updated test record")
                    return False
            else:
                print(f"❌ Failed to retrieve updated test: {get_response.status_code}")
                return False
                
        else:
            print(f"❌ Failed to update test: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error updating test: {str(e)}")
        return False
    
    # Step 5: Confirm timestamps are in correct format for frontend display
    print("\n5️⃣ Verifying timestamp format for frontend display...")
    
    # Retrieve final test to verify final state
    try:
        response = requests.get(f"{BACKEND_URL}/admin-registration/{registration_id}/tests")
        if response.status_code == 200:
            tests_response = response.json()
            final_test = tests_response['tests'][0]
            
            print(f"✅ Final test record retrieved")
            
            # Test timestamp parsing for frontend display
            created_at_str = final_test['created_at']
            updated_at_str = final_test['updated_at']
            
            try:
                # Parse timestamps
                created_at = datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))
                updated_at = datetime.fromisoformat(updated_at_str.replace('Z', '+00:00'))
                
                # Convert to Toronto timezone for display
                toronto_tz = pytz.timezone('America/Toronto')
                created_at_toronto = created_at.astimezone(toronto_tz)
                updated_at_toronto = updated_at.astimezone(toronto_tz)
                
                # Format for frontend display
                created_display = created_at_toronto.strftime('%Y-%m-%d %H:%M:%S %Z')
                updated_display = updated_at_toronto.strftime('%Y-%m-%d %H:%M:%S %Z')
                
                print(f"✅ Frontend display format:")
                print(f"   Created: {created_display}")
                print(f"   Updated: {updated_display}")
                
                # Verify timestamps are different (updated should be later)
                if updated_at > created_at:
                    print(f"✅ updated_at is later than created_at (as expected)")
                else:
                    print(f"⚠️ Timestamp relationship unexpected: updated_at should be later than created_at")
                    
            except Exception as e:
                print(f"❌ Error formatting timestamps for frontend: {str(e)}")
                return False
                
        else:
            print(f"❌ Failed to retrieve final test state: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error retrieving final test state: {str(e)}")
        return False
    
    print("\n" + "=" * 60)
    print("🎉 ALL TIMESTAMP TESTS PASSED SUCCESSFULLY!")
    print("✅ Test registration creation works")
    print("✅ Test record creation includes created_at timestamp")
    print("✅ Test retrieval returns both created_at and updated_at timestamps")
    print("✅ Test update properly updates updated_at while preserving created_at")
    print("✅ Timestamps are in correct format for frontend display")
    print("=" * 60)
    
    return True

def test_multiple_test_types_timestamps():
    """Test timestamps work correctly for different test types"""
    print("\n🧪 TESTING TIMESTAMPS FOR DIFFERENT TEST TYPES")
    print("=" * 60)
    
    # Create registration for multiple test types
    registration_data = {
        "firstName": "Multi",
        "lastName": "TestTypes",
        "patientConsent": "written",
        "dob": "1985-03-20",
        "gender": "Female"
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/admin-register", json=registration_data)
        if response.status_code in [200, 201]:
            registration = response.json()
            registration_id = registration.get('registration_id')
            print(f"✅ Registration created for multiple test types: {registration_id}")
        else:
            print(f"❌ Failed to create registration: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error creating registration: {str(e)}")
        return False
    
    # Test different test types
    test_types = [
        {
            "name": "HIV Test",
            "data": {
                "test_type": "HIV",
                "test_date": "2025-01-15",
                "hiv_result": "negative",
                "hiv_type": "Type 1",
                "hiv_tester": "MT"
            }
        },
        {
            "name": "HCV Test", 
            "data": {
                "test_type": "HCV",
                "test_date": "2025-01-16",
                "hcv_result": "positive",
                "hcv_tester": "MT"
            }
        },
        {
            "name": "Bloodwork Test",
            "data": {
                "test_type": "Bloodwork",
                "test_date": "2025-01-17",
                "bloodwork_type": "DBS",
                "bloodwork_circles": "3",
                "bloodwork_result": "Pending",
                "bloodwork_date_submitted": "2025-01-17",
                "bloodwork_tester": "MT"
            }
        }
    ]
    
    created_tests = []
    
    for test_type_info in test_types:
        print(f"\n📋 Testing {test_type_info['name']} timestamps...")
        
        try:
            response = requests.post(f"{BACKEND_URL}/admin-registration/{registration_id}/test", json=test_type_info['data'])
            if response.status_code in [200, 201]:
                test_response = response.json()
                print(f"✅ {test_type_info['name']} created successfully")
                
                # Get test_id from response
                test_id = test_response.get('test_id')
                if test_id:
                    created_tests.append({
                        'id': test_id,
                        'type': test_type_info['name']
                    })
                    print(f"✅ {test_type_info['name']} test_id: {test_id}")
                else:
                    print(f"❌ Missing test_id for {test_type_info['name']}")
                    return False
            else:
                print(f"❌ Failed to create {test_type_info['name']}: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error creating {test_type_info['name']}: {str(e)}")
            return False
    
    # Retrieve all tests and verify timestamps
    print(f"\n📋 Retrieving all tests and verifying timestamps...")
    
    try:
        response = requests.get(f"{BACKEND_URL}/admin-registration/{registration_id}/tests")
        if response.status_code == 200:
            tests_response = response.json()
            tests = tests_response.get('tests', [])
            
            print(f"✅ Retrieved {len(tests)} tests")
            
            if len(tests) == len(test_types):
                print(f"✅ All test types retrieved successfully")
                
                # Verify each test has proper timestamps
                for test in tests:
                    test_type = test.get('test_type', 'Unknown')
                    if 'created_at' in test and 'updated_at' in test:
                        print(f"✅ {test_type} test has both timestamps")
                        
                        # Verify timestamp format
                        try:
                            created_at = datetime.fromisoformat(test['created_at'].replace('Z', '+00:00'))
                            updated_at = datetime.fromisoformat(test['updated_at'].replace('Z', '+00:00'))
                            print(f"✅ {test_type} timestamps are valid ISO format")
                        except Exception as e:
                            print(f"❌ {test_type} timestamp format error: {str(e)}")
                            return False
                    else:
                        print(f"❌ {test_type} test missing timestamps")
                        return False
            else:
                print(f"❌ Expected {len(test_types)} tests, got {len(tests)}")
                return False
                
        else:
            print(f"❌ Failed to retrieve tests: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error retrieving tests: {str(e)}")
        return False
    
    print(f"\n✅ All test types have proper timestamp functionality")
    return True

if __name__ == "__main__":
    print("🚀 STARTING TEST MANAGEMENT API TIMESTAMP VERIFICATION")
    print("Testing timestamp enhancement for test records...")
    
    success = True
    
    # Test main timestamp functionality
    if not test_timestamp_functionality():
        success = False
    
    # Test timestamps for different test types
    if not test_multiple_test_types_timestamps():
        success = False
    
    if success:
        print("\n🎉 ALL TIMESTAMP VERIFICATION TESTS PASSED!")
        print("✅ Timestamps are properly saved and returned")
        print("✅ created_at timestamp is included in responses")
        print("✅ updated_at timestamp is properly updated")
        print("✅ Timestamps are in correct format for frontend display")
        print("✅ All test types support timestamp functionality")
    else:
        print("\n❌ SOME TIMESTAMP TESTS FAILED!")
        print("Please check the error messages above for details.")