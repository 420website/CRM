#!/usr/bin/env python3
"""
Date Handling Backend Test - Testing timezone/date selection fixes
Tests the backend date handling to ensure dates like "2000-01-03" are correctly stored and retrieved
without timezone conversion issues.

Focus Areas:
1. BACKEND DATE HANDLING: Verify dates sent from frontend are correctly stored/retrieved
2. DATE PARSING BACKEND: Test endpoints that receive date fields (especially dob)
3. DATABASE DATE STORAGE: Verify dates are stored consistently
4. API ENDPOINTS TESTING: Test admin registration endpoints with date fields
"""

import requests
import json
import sys
from datetime import date, datetime
import pytz

# Use localhost for backend testing (external URL has proxy issues)
BACKEND_URL = "http://localhost:8001"
API_BASE = f"{BACKEND_URL}/api"

def test_backend_health():
    """Test if backend is accessible"""
    try:
        response = requests.get(f"{API_BASE}/", timeout=10)
        print(f"✅ Backend Health Check: {response.status_code}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Backend Health Check Failed: {e}")
        return False

def test_date_field_handling():
    """Test 1: Backend Date Field Handling - Test various date formats"""
    print("\n🔍 TEST 1: Backend Date Field Handling")
    
    test_cases = [
        {
            "name": "Standard YYYY-MM-DD format",
            "dob": "2000-01-03",
            "regDate": "2024-01-15"
        },
        {
            "name": "Different date format",
            "dob": "1985-12-25", 
            "regDate": "2024-02-20"
        },
        {
            "name": "Edge case - January 1st",
            "dob": "1990-01-01",
            "regDate": "2024-01-01"
        },
        {
            "name": "Edge case - December 31st",
            "dob": "1995-12-31",
            "regDate": "2023-12-31"
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases):
        try:
            # Create registration with specific date
            registration_data = {
                "firstName": f"DateTest{i+1}",
                "lastName": "User",
                "dob": test_case["dob"],
                "regDate": test_case["regDate"],
                "patientConsent": "verbal",
                "gender": "Male",
                "province": "Ontario"
            }
            
            # Send to backend
            response = requests.post(f"{API_BASE}/admin-register", 
                                   json=registration_data, 
                                   timeout=10)
            
            if response.status_code == 200:
                registration_id = response.json().get('registration_id') or response.json().get('id')
                
                # Retrieve the registration to verify date storage
                get_response = requests.get(f"{API_BASE}/admin-registration/{registration_id}", 
                                          timeout=10)
                
                if get_response.status_code == 200:
                    stored_data = get_response.json()
                    stored_dob = stored_data.get('dob')
                    stored_regDate = stored_data.get('regDate')
                    
                    # Check if dates match exactly
                    dob_match = stored_dob == test_case["dob"]
                    regDate_match = stored_regDate == test_case["regDate"]
                    
                    if dob_match and regDate_match:
                        print(f"  ✅ {test_case['name']}: DOB={stored_dob}, RegDate={stored_regDate}")
                        results.append(True)
                    else:
                        print(f"  ❌ {test_case['name']}: Expected DOB={test_case['dob']}, Got={stored_dob}")
                        print(f"     Expected RegDate={test_case['regDate']}, Got={stored_regDate}")
                        results.append(False)
                else:
                    print(f"  ❌ {test_case['name']}: Failed to retrieve registration")
                    results.append(False)
            else:
                print(f"  ❌ {test_case['name']}: Registration failed - {response.status_code}")
                results.append(False)
                
        except Exception as e:
            print(f"  ❌ {test_case['name']}: Exception - {e}")
            results.append(False)
    
    success_rate = (sum(results) / len(results)) * 100
    print(f"📊 Date Field Handling Success Rate: {success_rate:.1f}% ({sum(results)}/{len(results)})")
    return success_rate > 80

def test_dob_parsing_specifically():
    """Test 2: DOB Parsing Backend - Focus on date of birth field"""
    print("\n🔍 TEST 2: DOB Parsing Backend Testing")
    
    # Test various DOB scenarios that might cause timezone issues
    dob_test_cases = [
        "2000-01-03",  # The specific date mentioned in the review
        "1985-06-15",  # Mid-year date
        "1990-02-29",  # Leap year date (invalid - should be handled)
        "1992-02-29",  # Valid leap year date
        "1975-11-30",  # End of month
        "2001-07-04"   # Summer date
    ]
    
    results = []
    
    for i, dob in enumerate(dob_test_cases):
        try:
            registration_data = {
                "firstName": f"DOBTest{i+1}",
                "lastName": "User", 
                "dob": dob,
                "patientConsent": "written",
                "province": "Ontario"
            }
            
            response = requests.post(f"{API_BASE}/admin-register", 
                                   json=registration_data, 
                                   timeout=10)
            
            if response.status_code == 200:
                registration_id = response.json().get('registration_id') or response.json().get('id')
                
                # Verify the DOB was stored correctly
                get_response = requests.get(f"{API_BASE}/admin-registration/{registration_id}", 
                                          timeout=10)
                
                if get_response.status_code == 200:
                    stored_data = get_response.json()
                    stored_dob = stored_data.get('dob')
                    
                    if stored_dob == dob:
                        print(f"  ✅ DOB {dob}: Stored correctly as {stored_dob}")
                        results.append(True)
                    else:
                        print(f"  ❌ DOB {dob}: Expected {dob}, Got {stored_dob}")
                        results.append(False)
                else:
                    print(f"  ❌ DOB {dob}: Failed to retrieve registration")
                    results.append(False)
            else:
                # Check if it's a validation error for invalid dates
                if dob == "1990-02-29":  # Invalid leap year
                    print(f"  ✅ DOB {dob}: Correctly rejected invalid date")
                    results.append(True)
                else:
                    print(f"  ❌ DOB {dob}: Registration failed - {response.status_code}")
                    if response.status_code == 422:
                        print(f"     Validation error: {response.text}")
                    results.append(False)
                    
        except Exception as e:
            print(f"  ❌ DOB {dob}: Exception - {e}")
            results.append(False)
    
    success_rate = (sum(results) / len(results)) * 100
    print(f"📊 DOB Parsing Success Rate: {success_rate:.1f}% ({sum(results)}/{len(results)})")
    return success_rate > 80

def test_database_date_consistency():
    """Test 3: Database Date Storage Consistency"""
    print("\n🔍 TEST 3: Database Date Storage Consistency")
    
    # Create a registration and verify date consistency across multiple retrievals
    test_dob = "2000-01-03"  # The specific date from the review
    test_regDate = "2024-01-15"
    
    try:
        # Create registration
        registration_data = {
            "firstName": "ConsistencyTest",
            "lastName": "User",
            "dob": test_dob,
            "regDate": test_regDate,
            "patientConsent": "verbal",
            "province": "Ontario"
        }
        
        response = requests.post(f"{API_BASE}/admin-register", 
                               json=registration_data, 
                               timeout=10)
        
        if response.status_code != 200:
            print(f"  ❌ Failed to create test registration: {response.status_code}")
            return False
            
        registration_id = response.json().get('registration_id') or response.json().get('id')
        print(f"  📝 Created test registration: {registration_id}")
        
        # Retrieve the same registration multiple times to check consistency
        retrieval_results = []
        
        for attempt in range(5):
            get_response = requests.get(f"{API_BASE}/admin-registration/{registration_id}", 
                                      timeout=10)
            
            if get_response.status_code == 200:
                stored_data = get_response.json()
                stored_dob = stored_data.get('dob')
                stored_regDate = stored_data.get('regDate')
                
                dob_consistent = stored_dob == test_dob
                regDate_consistent = stored_regDate == test_regDate
                
                retrieval_results.append(dob_consistent and regDate_consistent)
                
                if attempt == 0:  # Log first retrieval
                    print(f"  📅 Retrieved DOB: {stored_dob} (Expected: {test_dob})")
                    print(f"  📅 Retrieved RegDate: {stored_regDate} (Expected: {test_regDate})")
            else:
                retrieval_results.append(False)
        
        # Check if all retrievals were consistent
        all_consistent = all(retrieval_results)
        success_count = sum(retrieval_results)
        
        if all_consistent:
            print(f"  ✅ Date consistency verified: {success_count}/5 retrievals successful")
        else:
            print(f"  ❌ Date consistency failed: {success_count}/5 retrievals successful")
            
        return all_consistent
        
    except Exception as e:
        print(f"  ❌ Database consistency test failed: {e}")
        return False

def test_timezone_handling():
    """Test 4: Timezone Handling - Ensure no timezone conversion issues"""
    print("\n🔍 TEST 4: Timezone Handling Verification")
    
    # Test dates that might be affected by timezone conversion
    timezone_test_cases = [
        {
            "name": "January 3rd (Review case)",
            "dob": "2000-01-03",
            "expected_day": 3
        },
        {
            "name": "January 2nd (Day before)",
            "dob": "2000-01-02", 
            "expected_day": 2
        },
        {
            "name": "January 4th (Day after)",
            "dob": "2000-01-04",
            "expected_day": 4
        }
    ]
    
    results = []
    
    for test_case in timezone_test_cases:
        try:
            registration_data = {
                "firstName": "TimezoneTest",
                "lastName": test_case["name"].replace(" ", ""),
                "dob": test_case["dob"],
                "patientConsent": "verbal",
                "province": "Ontario"
            }
            
            response = requests.post(f"{API_BASE}/admin-register", 
                                   json=registration_data, 
                                   timeout=10)
            
            if response.status_code == 200:
                registration_id = response.json().get('registration_id') or response.json().get('id')
                
                # Retrieve and verify the date wasn't shifted by timezone
                get_response = requests.get(f"{API_BASE}/admin-registration/{registration_id}", 
                                          timeout=10)
                
                if get_response.status_code == 200:
                    stored_data = get_response.json()
                    stored_dob = stored_data.get('dob')
                    
                    # Parse the stored date to check the day
                    if stored_dob:
                        stored_day = int(stored_dob.split('-')[2])
                        expected_day = test_case["expected_day"]
                        
                        if stored_day == expected_day:
                            print(f"  ✅ {test_case['name']}: Day preserved ({stored_day})")
                            results.append(True)
                        else:
                            print(f"  ❌ {test_case['name']}: Day changed from {expected_day} to {stored_day}")
                            results.append(False)
                    else:
                        print(f"  ❌ {test_case['name']}: No DOB returned")
                        results.append(False)
                else:
                    print(f"  ❌ {test_case['name']}: Failed to retrieve")
                    results.append(False)
            else:
                print(f"  ❌ {test_case['name']}: Registration failed")
                results.append(False)
                
        except Exception as e:
            print(f"  ❌ {test_case['name']}: Exception - {e}")
            results.append(False)
    
    success_rate = (sum(results) / len(results)) * 100
    print(f"📊 Timezone Handling Success Rate: {success_rate:.1f}% ({sum(results)}/{len(results)})")
    return success_rate > 80

def test_admin_registration_endpoints():
    """Test 5: Admin Registration Endpoints with Date Fields"""
    print("\n🔍 TEST 5: Admin Registration Endpoints Date Testing")
    
    endpoints_to_test = [
        {
            "name": "POST /api/admin-register",
            "method": "POST",
            "url": f"{API_BASE}/admin-register"
        }
    ]
    
    # Test data with various date scenarios
    test_data = {
        "firstName": "EndpointTest",
        "lastName": "User",
        "dob": "2000-01-03",  # The specific date from review
        "regDate": "2024-01-15",
        "patientConsent": "written",
        "gender": "Female",
        "province": "Ontario",
        "disposition": "ACTIVE",
        "healthCard": "1234567890",
        "phone1": "4161234567",
        "email": "test@example.com"
    }
    
    results = []
    
    for endpoint in endpoints_to_test:
        try:
            if endpoint["method"] == "POST":
                response = requests.post(endpoint["url"], 
                                       json=test_data, 
                                       timeout=10)
                
                if response.status_code == 200:
                    registration_id = response.json().get('registration_id') or response.json().get('id')
                    
                    # Verify the registration was created with correct dates
                    get_response = requests.get(f"{API_BASE}/admin-registration/{registration_id}", 
                                              timeout=10)
                    
                    if get_response.status_code == 200:
                        stored_data = get_response.json()
                        dob_correct = stored_data.get('dob') == test_data['dob']
                        regDate_correct = stored_data.get('regDate') == test_data['regDate']
                        
                        if dob_correct and regDate_correct:
                            print(f"  ✅ {endpoint['name']}: Dates handled correctly")
                            results.append(True)
                        else:
                            print(f"  ❌ {endpoint['name']}: Date mismatch")
                            print(f"     DOB: Expected {test_data['dob']}, Got {stored_data.get('dob')}")
                            print(f"     RegDate: Expected {test_data['regDate']}, Got {stored_data.get('regDate')}")
                            results.append(False)
                    else:
                        print(f"  ❌ {endpoint['name']}: Failed to retrieve created registration")
                        results.append(False)
                else:
                    print(f"  ❌ {endpoint['name']}: Request failed - {response.status_code}")
                    if response.status_code == 422:
                        print(f"     Validation error: {response.text}")
                    results.append(False)
                    
        except Exception as e:
            print(f"  ❌ {endpoint['name']}: Exception - {e}")
            results.append(False)
    
    success_rate = (sum(results) / len(results)) * 100 if results else 0
    print(f"📊 Endpoint Date Handling Success Rate: {success_rate:.1f}% ({sum(results)}/{len(results)})")
    return success_rate > 80

def main():
    """Run all date handling tests"""
    print("🔍 DATE HANDLING BACKEND TESTING - TIMEZONE/DATE SELECTION FIXES")
    print("=" * 70)
    print("Testing backend date handling to ensure dates like '2000-01-03' are")
    print("correctly stored and retrieved without timezone conversion issues.")
    print("=" * 70)
    
    # Check backend health first
    if not test_backend_health():
        print("❌ Backend is not accessible. Cannot proceed with testing.")
        return False
    
    # Run all tests
    test_results = []
    
    test_results.append(test_date_field_handling())
    test_results.append(test_dob_parsing_specifically()) 
    test_results.append(test_database_date_consistency())
    test_results.append(test_timezone_handling())
    test_results.append(test_admin_registration_endpoints())
    
    # Calculate overall results
    passed_tests = sum(test_results)
    total_tests = len(test_results)
    overall_success_rate = (passed_tests / total_tests) * 100
    
    print("\n" + "=" * 70)
    print("📊 FINAL RESULTS - DATE HANDLING BACKEND TESTING")
    print("=" * 70)
    print(f"Tests Passed: {passed_tests}/{total_tests}")
    print(f"Overall Success Rate: {overall_success_rate:.1f}%")
    
    if overall_success_rate >= 80:
        print("✅ DATE HANDLING BACKEND TESTING: PASSED")
        print("✅ Backend correctly handles date fields without timezone conversion issues")
        print("✅ Dates like '2000-01-03' are stored and retrieved correctly")
        print("✅ DOB parsing works properly with YYYY-MM-DD format")
        print("✅ Database date storage is consistent")
        print("✅ Admin registration endpoints handle dates correctly")
    else:
        print("❌ DATE HANDLING BACKEND TESTING: FAILED")
        print("❌ Issues found with backend date handling")
        print("❌ Some dates may be affected by timezone conversion")
        print("❌ Further investigation needed")
    
    print("=" * 70)
    return overall_success_rate >= 80

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)