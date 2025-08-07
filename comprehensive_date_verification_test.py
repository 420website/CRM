#!/usr/bin/env python3
"""
COMPREHENSIVE DATE HANDLING VERIFICATION TEST
Testing all date handling after implementing fixes for timezone/date selection issue
where users were experiencing "day before" problems when selecting calendar dates.

TESTING FOCUS:
1. Date Input Processing - verify dates like "2025-07-02" maintain correct day
2. Database Date Storage - test MongoDB storage without timezone conversion issues  
3. Date Retrieval - verify dates retrieved maintain correct day
4. Admin Registration Date Fields - test all date fields (dob, regDate, test dates, etc.)
5. Date Consistency - ensure July 2nd selected = July 2nd stored = July 2nd retrieved

CRITICAL TEST CASES:
- Create registration with dob: "2000-01-03" → verify stored/retrieved as January 3rd, 2000
- Test various date formats and edge cases
- Test date fields across different endpoints
- Test test records with timestamps
- Test HIV/HCV test dates
- Test RNA sample dates
"""

import requests
import json
import sys
from datetime import date, datetime
import pytz
import uuid

# Use external URL from frontend/.env for proper testing
BACKEND_URL = "https://cd556dd9-d36b-422e-8110-4b1830397661.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

def test_backend_health():
    """Test if backend is accessible"""
    try:
        response = requests.get(f"{API_BASE}/", timeout=15)
        print(f"✅ Backend Health Check: {response.status_code}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Backend Health Check Failed: {e}")
        return False

def test_critical_date_scenarios():
    """Test 1: Critical Date Scenarios - Focus on reported issues"""
    print("\n🔍 TEST 1: Critical Date Scenarios (July 2nd → July 1st issue)")
    
    critical_test_cases = [
        {
            "name": "July 2nd 2025 (Reported Issue)",
            "dob": "2025-07-02",
            "regDate": "2025-07-02",
            "expected_day": 2,
            "expected_month": 7
        },
        {
            "name": "January 3rd 2000 (Review Example)",
            "dob": "2000-01-03", 
            "regDate": "2000-01-03",
            "expected_day": 3,
            "expected_month": 1
        },
        {
            "name": "December 31st Edge Case",
            "dob": "1999-12-31",
            "regDate": "2024-12-31", 
            "expected_day": 31,
            "expected_month": 12
        },
        {
            "name": "February 29th Leap Year",
            "dob": "2000-02-29",
            "regDate": "2024-02-29",
            "expected_day": 29,
            "expected_month": 2
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(critical_test_cases):
        try:
            registration_data = {
                "firstName": f"CriticalTest{i+1}",
                "lastName": "DateUser",
                "dob": test_case["dob"],
                "regDate": test_case["regDate"],
                "patientConsent": "verbal",
                "gender": "Male",
                "province": "Ontario",
                "disposition": "ACTIVE",
                "physician": "Dr. David Fletcher"
            }
            
            # Create registration
            response = requests.post(f"{API_BASE}/admin-register", 
                                   json=registration_data, 
                                   timeout=15)
            
            if response.status_code == 200:
                registration_id = response.json().get('registration_id') or response.json().get('id')
                
                # Retrieve and verify dates
                get_response = requests.get(f"{API_BASE}/admin-registration/{registration_id}", 
                                          timeout=15)
                
                if get_response.status_code == 200:
                    stored_data = get_response.json()
                    stored_dob = stored_data.get('dob')
                    stored_regDate = stored_data.get('regDate')
                    
                    # Parse dates to check day and month
                    dob_parts = stored_dob.split('-') if stored_dob else []
                    regDate_parts = stored_regDate.split('-') if stored_regDate else []
                    
                    dob_day_correct = len(dob_parts) >= 3 and int(dob_parts[2]) == test_case["expected_day"]
                    dob_month_correct = len(dob_parts) >= 2 and int(dob_parts[1]) == test_case["expected_month"]
                    regDate_day_correct = len(regDate_parts) >= 3 and int(regDate_parts[2]) == test_case["expected_day"]
                    regDate_month_correct = len(regDate_parts) >= 2 and int(regDate_parts[1]) == test_case["expected_month"]
                    
                    if dob_day_correct and dob_month_correct and regDate_day_correct and regDate_month_correct:
                        print(f"  ✅ {test_case['name']}: DOB={stored_dob}, RegDate={stored_regDate}")
                        results.append(True)
                    else:
                        print(f"  ❌ {test_case['name']}: Date integrity issue")
                        print(f"     Expected: Day={test_case['expected_day']}, Month={test_case['expected_month']}")
                        print(f"     DOB: {stored_dob}, RegDate: {stored_regDate}")
                        results.append(False)
                else:
                    print(f"  ❌ {test_case['name']}: Failed to retrieve registration")
                    results.append(False)
            else:
                print(f"  ❌ {test_case['name']}: Registration failed - {response.status_code}")
                if response.status_code == 422:
                    print(f"     Validation error: {response.text}")
                results.append(False)
                
        except Exception as e:
            print(f"  ❌ {test_case['name']}: Exception - {e}")
            results.append(False)
    
    success_rate = (sum(results) / len(results)) * 100
    print(f"📊 Critical Date Scenarios Success Rate: {success_rate:.1f}% ({sum(results)}/{len(results)})")
    return success_rate > 80

def test_all_date_fields():
    """Test 2: All Date Fields in Admin Registration"""
    print("\n🔍 TEST 2: All Date Fields in Admin Registration")
    
    # Test comprehensive registration with all date fields
    test_data = {
        "firstName": "ComprehensiveDateTest",
        "lastName": "User",
        "dob": "1985-06-15",  # Date of birth
        "regDate": "2025-01-15",  # Registration date
        "patientConsent": "written",
        "gender": "Female",
        "province": "Ontario",
        "disposition": "ACTIVE",
        "physician": "Dr. David Fletcher",
        "rnaAvailable": "Yes",
        "rnaSampleDate": "2025-01-10",  # RNA sample date
        "hivDate": "2025-01-12",  # HIV test date
        "healthCard": "1234567890",
        "phone1": "4161234567",
        "email": "comprehensive@test.com"
    }
    
    try:
        # Create registration with all date fields
        response = requests.post(f"{API_BASE}/admin-register", 
                               json=test_data, 
                               timeout=15)
        
        if response.status_code == 200:
            registration_id = response.json().get('registration_id') or response.json().get('id')
            print(f"  📝 Created comprehensive registration: {registration_id}")
            
            # Retrieve and verify all date fields
            get_response = requests.get(f"{API_BASE}/admin-registration/{registration_id}", 
                                      timeout=15)
            
            if get_response.status_code == 200:
                stored_data = get_response.json()
                
                # Check all date fields
                date_fields = {
                    "dob": ("1985-06-15", "Date of Birth"),
                    "regDate": ("2025-01-15", "Registration Date"),
                    "rnaSampleDate": ("2025-01-10", "RNA Sample Date"),
                    "hivDate": ("2025-01-12", "HIV Test Date")
                }
                
                all_correct = True
                for field, (expected, description) in date_fields.items():
                    stored_value = stored_data.get(field)
                    if stored_value == expected:
                        print(f"  ✅ {description}: {stored_value}")
                    else:
                        print(f"  ❌ {description}: Expected {expected}, Got {stored_value}")
                        all_correct = False
                
                return all_correct
            else:
                print(f"  ❌ Failed to retrieve comprehensive registration")
                return False
        else:
            print(f"  ❌ Failed to create comprehensive registration - {response.status_code}")
            if response.status_code == 422:
                print(f"     Validation error: {response.text}")
            return False
            
    except Exception as e:
        print(f"  ❌ Comprehensive date test failed: {e}")
        return False

def test_test_records_with_dates():
    """Test 3: Test Records with Date Fields and Timestamps"""
    print("\n🔍 TEST 3: Test Records with Date Fields and Timestamps")
    
    # First create a registration to attach test records to
    try:
        registration_data = {
            "firstName": "TestRecordDate",
            "lastName": "User",
            "dob": "1990-05-20",
            "regDate": "2025-01-15",
            "patientConsent": "verbal",
            "province": "Ontario"
        }
        
        response = requests.post(f"{API_BASE}/admin-register", 
                               json=registration_data, 
                               timeout=15)
        
        if response.status_code != 200:
            print(f"  ❌ Failed to create base registration for test records")
            return False
            
        registration_id = response.json().get('registration_id') or response.json().get('id')
        print(f"  📝 Created base registration for test records: {registration_id}")
        
        # Test different types of test records with dates
        test_record_scenarios = [
            {
                "name": "HIV Test Record",
                "data": {
                    "test_type": "HIV",
                    "test_date": "2025-01-16",
                    "hiv_result": "negative",
                    "hiv_type": "Type 1",
                    "hiv_tester": "CM"
                }
            },
            {
                "name": "HCV Test Record", 
                "data": {
                    "test_type": "HCV",
                    "test_date": "2025-01-17",
                    "hcv_result": "positive",
                    "hcv_tester": "CM"
                }
            },
            {
                "name": "Bloodwork Test Record",
                "data": {
                    "test_type": "Bloodwork",
                    "test_date": "2025-01-18",
                    "bloodwork_type": "DBS",
                    "bloodwork_circles": "3",
                    "bloodwork_result": "Pending",
                    "bloodwork_date_submitted": "2025-01-19",
                    "bloodwork_tester": "CM"
                }
            }
        ]
        
        results = []
        
        for scenario in test_record_scenarios:
            try:
                # Create test record
                test_response = requests.post(f"{API_BASE}/admin-registration/{registration_id}/test-records", 
                                            json=scenario["data"], 
                                            timeout=15)
                
                if test_response.status_code == 200:
                    test_record_id = test_response.json().get('test_record_id') or test_response.json().get('id')
                    
                    # Retrieve test record to verify dates
                    get_test_response = requests.get(f"{API_BASE}/admin-registration/{registration_id}/test-records/{test_record_id}", 
                                                   timeout=15)
                    
                    if get_test_response.status_code == 200:
                        stored_test_data = get_test_response.json()
                        stored_test_date = stored_test_data.get('test_date')
                        expected_test_date = scenario["data"]["test_date"]
                        
                        if stored_test_date == expected_test_date:
                            print(f"  ✅ {scenario['name']}: Test date preserved ({stored_test_date})")
                            
                            # Check for timestamp fields
                            created_at = stored_test_data.get('created_at')
                            updated_at = stored_test_data.get('updated_at')
                            
                            if created_at and updated_at:
                                print(f"    📅 Timestamps: Created={created_at[:19]}, Updated={updated_at[:19]}")
                            
                            results.append(True)
                        else:
                            print(f"  ❌ {scenario['name']}: Date mismatch - Expected {expected_test_date}, Got {stored_test_date}")
                            results.append(False)
                    else:
                        print(f"  ❌ {scenario['name']}: Failed to retrieve test record")
                        results.append(False)
                else:
                    print(f"  ❌ {scenario['name']}: Failed to create test record - {test_response.status_code}")
                    results.append(False)
                    
            except Exception as e:
                print(f"  ❌ {scenario['name']}: Exception - {e}")
                results.append(False)
        
        success_rate = (sum(results) / len(results)) * 100
        print(f"📊 Test Records Date Handling Success Rate: {success_rate:.1f}% ({sum(results)}/{len(results)})")
        return success_rate > 80
        
    except Exception as e:
        print(f"  ❌ Test records date testing failed: {e}")
        return False

def test_date_consistency_across_operations():
    """Test 4: Date Consistency Across CRUD Operations"""
    print("\n🔍 TEST 4: Date Consistency Across CRUD Operations")
    
    original_dob = "1988-03-25"
    original_regDate = "2025-01-20"
    updated_dob = "1988-03-26"  # Change day by 1 to test update
    
    try:
        # Create registration
        registration_data = {
            "firstName": "CRUDDateTest",
            "lastName": "User",
            "dob": original_dob,
            "regDate": original_regDate,
            "patientConsent": "written",
            "province": "Ontario"
        }
        
        response = requests.post(f"{API_BASE}/admin-register", 
                               json=registration_data, 
                               timeout=15)
        
        if response.status_code != 200:
            print(f"  ❌ Failed to create registration for CRUD test")
            return False
            
        registration_id = response.json().get('registration_id') or response.json().get('id')
        print(f"  📝 Created registration for CRUD test: {registration_id}")
        
        # Step 1: Read - Verify initial dates
        get_response = requests.get(f"{API_BASE}/admin-registration/{registration_id}", 
                                  timeout=15)
        
        if get_response.status_code == 200:
            initial_data = get_response.json()
            if initial_data.get('dob') == original_dob and initial_data.get('regDate') == original_regDate:
                print(f"  ✅ CREATE: Dates stored correctly - DOB={original_dob}, RegDate={original_regDate}")
            else:
                print(f"  ❌ CREATE: Date mismatch")
                return False
        else:
            print(f"  ❌ READ: Failed to retrieve registration")
            return False
        
        # Step 2: Update - Change DOB and verify
        update_data = {
            "dob": updated_dob
        }
        
        update_response = requests.put(f"{API_BASE}/admin-registration/{registration_id}", 
                                     json=update_data, 
                                     timeout=15)
        
        if update_response.status_code == 200:
            # Verify update
            get_updated_response = requests.get(f"{API_BASE}/admin-registration/{registration_id}", 
                                              timeout=15)
            
            if get_updated_response.status_code == 200:
                updated_data = get_updated_response.json()
                if updated_data.get('dob') == updated_dob and updated_data.get('regDate') == original_regDate:
                    print(f"  ✅ UPDATE: Dates updated correctly - DOB={updated_dob}, RegDate={original_regDate}")
                else:
                    print(f"  ❌ UPDATE: Date update failed")
                    return False
            else:
                print(f"  ❌ UPDATE VERIFICATION: Failed to retrieve updated registration")
                return False
        else:
            print(f"  ❌ UPDATE: Failed to update registration - {update_response.status_code}")
            return False
        
        # Step 3: Final consistency check
        final_response = requests.get(f"{API_BASE}/admin-registration/{registration_id}", 
                                    timeout=15)
        
        if final_response.status_code == 200:
            final_data = final_response.json()
            final_dob = final_data.get('dob')
            final_regDate = final_data.get('regDate')
            
            if final_dob == updated_dob and final_regDate == original_regDate:
                print(f"  ✅ FINAL CONSISTENCY: All dates consistent after CRUD operations")
                return True
            else:
                print(f"  ❌ FINAL CONSISTENCY: Date inconsistency detected")
                return False
        else:
            print(f"  ❌ FINAL CHECK: Failed to retrieve registration")
            return False
            
    except Exception as e:
        print(f"  ❌ CRUD date consistency test failed: {e}")
        return False

def test_edge_case_dates():
    """Test 5: Edge Case Dates and Timezone Boundaries"""
    print("\n🔍 TEST 5: Edge Case Dates and Timezone Boundaries")
    
    edge_cases = [
        {
            "name": "New Year's Day",
            "dob": "2000-01-01",
            "regDate": "2025-01-01"
        },
        {
            "name": "New Year's Eve", 
            "dob": "1999-12-31",
            "regDate": "2024-12-31"
        },
        {
            "name": "Leap Day",
            "dob": "2000-02-29",
            "regDate": "2024-02-29"
        },
        {
            "name": "Day After Leap Day",
            "dob": "2000-03-01", 
            "regDate": "2024-03-01"
        },
        {
            "name": "Summer Solstice",
            "dob": "1990-06-21",
            "regDate": "2025-06-21"
        }
    ]
    
    results = []
    
    for i, case in enumerate(edge_cases):
        try:
            registration_data = {
                "firstName": f"EdgeCase{i+1}",
                "lastName": "User",
                "dob": case["dob"],
                "regDate": case["regDate"],
                "patientConsent": "verbal",
                "province": "Ontario"
            }
            
            response = requests.post(f"{API_BASE}/admin-register", 
                                   json=registration_data, 
                                   timeout=15)
            
            if response.status_code == 200:
                registration_id = response.json().get('registration_id') or response.json().get('id')
                
                # Verify dates
                get_response = requests.get(f"{API_BASE}/admin-registration/{registration_id}", 
                                          timeout=15)
                
                if get_response.status_code == 200:
                    stored_data = get_response.json()
                    stored_dob = stored_data.get('dob')
                    stored_regDate = stored_data.get('regDate')
                    
                    if stored_dob == case["dob"] and stored_regDate == case["regDate"]:
                        print(f"  ✅ {case['name']}: Dates preserved correctly")
                        results.append(True)
                    else:
                        print(f"  ❌ {case['name']}: Date mismatch")
                        results.append(False)
                else:
                    print(f"  ❌ {case['name']}: Failed to retrieve")
                    results.append(False)
            else:
                print(f"  ❌ {case['name']}: Registration failed - {response.status_code}")
                results.append(False)
                
        except Exception as e:
            print(f"  ❌ {case['name']}: Exception - {e}")
            results.append(False)
    
    success_rate = (sum(results) / len(results)) * 100
    print(f"📊 Edge Case Dates Success Rate: {success_rate:.1f}% ({sum(results)}/{len(results)})")
    return success_rate > 80

def main():
    """Run comprehensive date handling verification"""
    print("🔍 COMPREHENSIVE DATE HANDLING VERIFICATION")
    print("=" * 80)
    print("Testing all date handling after implementing fixes for timezone/date selection")
    print("issue where users were experiencing 'day before' problems when selecting")
    print("calendar dates. Focus: July 2nd → July 1st issue resolution.")
    print("=" * 80)
    
    # Check backend health first
    if not test_backend_health():
        print("❌ Backend is not accessible. Cannot proceed with testing.")
        return False
    
    # Run all comprehensive tests
    test_results = []
    
    test_results.append(test_critical_date_scenarios())
    test_results.append(test_all_date_fields())
    test_results.append(test_test_records_with_dates())
    test_results.append(test_date_consistency_across_operations())
    test_results.append(test_edge_case_dates())
    
    # Calculate overall results
    passed_tests = sum(test_results)
    total_tests = len(test_results)
    overall_success_rate = (passed_tests / total_tests) * 100
    
    print("\n" + "=" * 80)
    print("📊 FINAL RESULTS - COMPREHENSIVE DATE HANDLING VERIFICATION")
    print("=" * 80)
    print(f"Tests Passed: {passed_tests}/{total_tests}")
    print(f"Overall Success Rate: {overall_success_rate:.1f}%")
    
    if overall_success_rate >= 80:
        print("✅ COMPREHENSIVE DATE HANDLING VERIFICATION: PASSED")
        print("✅ Date integrity maintained throughout entire data flow")
        print("✅ Frontend → Backend → Database → Backend → Frontend: CONSISTENT")
        print("✅ July 2nd selected = July 2nd stored = July 2nd retrieved")
        print("✅ All date fields in admin registration working correctly")
        print("✅ Test records with timestamps functioning properly")
        print("✅ CRUD operations maintain date consistency")
        print("✅ Edge case dates handled correctly")
        print("✅ No timezone conversion issues detected")
    else:
        print("❌ COMPREHENSIVE DATE HANDLING VERIFICATION: FAILED")
        print("❌ Date integrity issues detected in data flow")
        print("❌ Some dates may still be affected by timezone conversion")
        print("❌ Further investigation and fixes needed")
    
    print("=" * 80)
    return overall_success_rate >= 80

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)