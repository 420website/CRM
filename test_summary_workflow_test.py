#!/usr/bin/env python3
"""
Test Summary in Email Template Workflow Test
============================================

This test verifies the complete workflow for test summary functionality:
1. Create a new admin registration 
2. Add multiple test records (HIV, HCV, Bloodwork) with different data
3. Verify the tests are stored correctly in the backend
4. Test that the GET /api/admin-registration/{id}/tests endpoint returns the test data correctly
5. Confirm that all test fields are present and properly formatted

This validates that when the frontend calls loadTests() before copyFormData(), 
it will get the proper test data to include in the email template.
"""

import requests
import json
from datetime import datetime, date
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

class TestSummaryWorkflowTester:
    def __init__(self):
        self.base_url = os.getenv('REACT_APP_BACKEND_URL', 'https://cd556dd9-d36b-422e-8110-4b1830397661.preview.emergentagent.com')
        self.api_url = f"{self.base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.registration_id = None
        self.test_ids = []
        
    def log_test(self, test_name, success, details=""):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {test_name}: PASSED {details}")
        else:
            print(f"❌ {test_name}: FAILED {details}")
        return success
    
    def test_1_create_admin_registration(self):
        """Test 1: Create a new admin registration"""
        print("\n🧪 TEST 1: Creating Admin Registration")
        
        registration_data = {
            "firstName": "Michael",
            "lastName": "Johnson", 
            "patientConsent": "verbal",
            "dob": "1985-06-15",
            "gender": "Male",
            "province": "Ontario",
            "healthCard": "1234567890AB",
            "phone1": "416-555-0123",
            "email": "michael.johnson@email.com",
            "address": "123 Main Street",
            "city": "Toronto",
            "postalCode": "M5V 3A8"
        }
        
        try:
            response = requests.post(
                f"{self.api_url}/admin-register",
                json=registration_data,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'registration_id' in data:
                    self.registration_id = data['registration_id']
                    return self.log_test(
                        "Admin Registration Creation", 
                        True, 
                        f"- Registration ID: {self.registration_id}"
                    )
                else:
                    return self.log_test(
                        "Admin Registration Creation", 
                        False, 
                        "- Missing registration_id in response"
                    )
            else:
                return self.log_test(
                    "Admin Registration Creation", 
                    False, 
                    f"- Status: {response.status_code}, Response: {response.text}"
                )
                
        except Exception as e:
            return self.log_test(
                "Admin Registration Creation", 
                False, 
                f"- Exception: {str(e)}"
            )
    
    def test_2_create_hiv_test(self):
        """Test 2: Create HIV test record"""
        print("\n🧪 TEST 2: Creating HIV Test Record")
        
        if not self.registration_id:
            return self.log_test("HIV Test Creation", False, "- No registration ID available")
        
        hiv_test_data = {
            "test_type": "HIV",
            "test_date": "2025-01-15",
            "hiv_result": "negative",
            "hiv_type": "Type 1",
            "hiv_tester": "JY"
        }
        
        try:
            response = requests.post(
                f"{self.api_url}/admin-registration/{self.registration_id}/test",
                json=hiv_test_data,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'test_id' in data:
                    self.test_ids.append(data['test_id'])
                    return self.log_test(
                        "HIV Test Creation", 
                        True, 
                        f"- Test ID: {data['test_id']}, Result: {hiv_test_data['hiv_result']}"
                    )
                else:
                    return self.log_test(
                        "HIV Test Creation", 
                        False, 
                        "- Missing test_id in response"
                    )
            else:
                return self.log_test(
                    "HIV Test Creation", 
                    False, 
                    f"- Status: {response.status_code}, Response: {response.text}"
                )
                
        except Exception as e:
            return self.log_test(
                "HIV Test Creation", 
                False, 
                f"- Exception: {str(e)}"
            )
    
    def test_3_create_hcv_test(self):
        """Test 3: Create HCV test record"""
        print("\n🧪 TEST 3: Creating HCV Test Record")
        
        if not self.registration_id:
            return self.log_test("HCV Test Creation", False, "- No registration ID available")
        
        hcv_test_data = {
            "test_type": "HCV",
            "test_date": "2025-01-16",
            "hcv_result": "positive",
            "hcv_tester": "CM"
        }
        
        try:
            response = requests.post(
                f"{self.api_url}/admin-registration/{self.registration_id}/test",
                json=hcv_test_data,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'test_id' in data:
                    self.test_ids.append(data['test_id'])
                    return self.log_test(
                        "HCV Test Creation", 
                        True, 
                        f"- Test ID: {data['test_id']}, Result: {hcv_test_data['hcv_result']}"
                    )
                else:
                    return self.log_test(
                        "HCV Test Creation", 
                        False, 
                        "- Missing test_id in response"
                    )
            else:
                return self.log_test(
                    "HCV Test Creation", 
                    False, 
                    f"- Status: {response.status_code}, Response: {response.text}"
                )
                
        except Exception as e:
            return self.log_test(
                "HCV Test Creation", 
                False, 
                f"- Exception: {str(e)}"
            )
    
    def test_4_create_bloodwork_test(self):
        """Test 4: Create Bloodwork test record"""
        print("\n🧪 TEST 4: Creating Bloodwork Test Record")
        
        if not self.registration_id:
            return self.log_test("Bloodwork Test Creation", False, "- No registration ID available")
        
        bloodwork_test_data = {
            "test_type": "Bloodwork",
            "test_date": "2025-01-17",
            "bloodwork_type": "DBS",
            "bloodwork_circles": "3",
            "bloodwork_result": "Pending",
            "bloodwork_date_submitted": "2025-01-18",
            "bloodwork_tester": "JY"
        }
        
        try:
            response = requests.post(
                f"{self.api_url}/admin-registration/{self.registration_id}/test",
                json=bloodwork_test_data,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'test_id' in data:
                    self.test_ids.append(data['test_id'])
                    return self.log_test(
                        "Bloodwork Test Creation", 
                        True, 
                        f"- Test ID: {data['test_id']}, Type: {bloodwork_test_data['bloodwork_type']}"
                    )
                else:
                    return self.log_test(
                        "Bloodwork Test Creation", 
                        False, 
                        "- Missing test_id in response"
                    )
            else:
                return self.log_test(
                    "Bloodwork Test Creation", 
                    False, 
                    f"- Status: {response.status_code}, Response: {response.text}"
                )
                
        except Exception as e:
            return self.log_test(
                "Bloodwork Test Creation", 
                False, 
                f"- Exception: {str(e)}"
            )
    
    def test_5_retrieve_all_tests(self):
        """Test 5: Retrieve all tests for the registration"""
        print("\n🧪 TEST 5: Retrieving All Tests")
        
        if not self.registration_id:
            return self.log_test("Test Retrieval", False, "- No registration ID available")
        
        try:
            response = requests.get(
                f"{self.api_url}/admin-registration/{self.registration_id}/tests",
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check response format
                if 'tests' not in data:
                    return self.log_test(
                        "Test Retrieval", 
                        False, 
                        "- Response missing 'tests' key"
                    )
                
                tests = data['tests']
                
                # Check we have the expected number of tests
                if len(tests) != 3:
                    return self.log_test(
                        "Test Retrieval", 
                        False, 
                        f"- Expected 3 tests, got {len(tests)}"
                    )
                
                # Verify each test type is present
                test_types = [test.get('test_type') for test in tests]
                expected_types = ['HIV', 'HCV', 'Bloodwork']
                
                for expected_type in expected_types:
                    if expected_type not in test_types:
                        return self.log_test(
                            "Test Retrieval", 
                            False, 
                            f"- Missing test type: {expected_type}"
                        )
                
                return self.log_test(
                    "Test Retrieval", 
                    True, 
                    f"- Retrieved {len(tests)} tests with all expected types"
                )
                
            else:
                return self.log_test(
                    "Test Retrieval", 
                    False, 
                    f"- Status: {response.status_code}, Response: {response.text}"
                )
                
        except Exception as e:
            return self.log_test(
                "Test Retrieval", 
                False, 
                f"- Exception: {str(e)}"
            )
    
    def test_6_verify_test_data_structure(self):
        """Test 6: Verify test data structure and all required fields"""
        print("\n🧪 TEST 6: Verifying Test Data Structure")
        
        if not self.registration_id:
            return self.log_test("Test Data Structure", False, "- No registration ID available")
        
        try:
            response = requests.get(
                f"{self.api_url}/admin-registration/{self.registration_id}/tests",
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code != 200:
                return self.log_test(
                    "Test Data Structure", 
                    False, 
                    f"- Failed to retrieve tests: {response.status_code}"
                )
            
            data = response.json()
            tests = data.get('tests', [])
            
            # Verify each test has required fields
            required_base_fields = ['id', 'registration_id', 'test_type', 'test_date', 'created_at', 'updated_at']
            
            for i, test in enumerate(tests):
                test_type = test.get('test_type', 'Unknown')
                
                # Check base fields
                for field in required_base_fields:
                    if field not in test:
                        return self.log_test(
                            "Test Data Structure", 
                            False, 
                            f"- Test {i+1} ({test_type}) missing field: {field}"
                        )
                
                # Check type-specific fields
                if test_type == 'HIV':
                    hiv_fields = ['hiv_result', 'hiv_type', 'hiv_tester']
                    for field in hiv_fields:
                        if field not in test:
                            return self.log_test(
                                "Test Data Structure", 
                                False, 
                                f"- HIV test missing field: {field}"
                            )
                    
                    # Verify HIV data values
                    if test.get('hiv_result') != 'negative':
                        return self.log_test(
                            "Test Data Structure", 
                            False, 
                            f"- HIV result mismatch: expected 'negative', got '{test.get('hiv_result')}'"
                        )
                
                elif test_type == 'HCV':
                    hcv_fields = ['hcv_result', 'hcv_tester']
                    for field in hcv_fields:
                        if field not in test:
                            return self.log_test(
                                "Test Data Structure", 
                                False, 
                                f"- HCV test missing field: {field}"
                            )
                    
                    # Verify HCV data values
                    if test.get('hcv_result') != 'positive':
                        return self.log_test(
                            "Test Data Structure", 
                            False, 
                            f"- HCV result mismatch: expected 'positive', got '{test.get('hcv_result')}'"
                        )
                
                elif test_type == 'Bloodwork':
                    bloodwork_fields = ['bloodwork_type', 'bloodwork_circles', 'bloodwork_result', 'bloodwork_date_submitted', 'bloodwork_tester']
                    for field in bloodwork_fields:
                        if field not in test:
                            return self.log_test(
                                "Test Data Structure", 
                                False, 
                                f"- Bloodwork test missing field: {field}"
                            )
                    
                    # Verify Bloodwork data values
                    if test.get('bloodwork_type') != 'DBS':
                        return self.log_test(
                            "Test Data Structure", 
                            False, 
                            f"- Bloodwork type mismatch: expected 'DBS', got '{test.get('bloodwork_type')}'"
                        )
            
            return self.log_test(
                "Test Data Structure", 
                True, 
                f"- All {len(tests)} tests have proper structure and field values"
            )
            
        except Exception as e:
            return self.log_test(
                "Test Data Structure", 
                False, 
                f"- Exception: {str(e)}"
            )
    
    def test_7_verify_email_template_data_format(self):
        """Test 7: Verify data format matches what email template expects"""
        print("\n🧪 TEST 7: Verifying Email Template Data Format")
        
        if not self.registration_id:
            return self.log_test("Email Template Format", False, "- No registration ID available")
        
        try:
            response = requests.get(
                f"{self.api_url}/admin-registration/{self.registration_id}/tests",
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code != 200:
                return self.log_test(
                    "Email Template Format", 
                    False, 
                    f"- Failed to retrieve tests: {response.status_code}"
                )
            
            data = response.json()
            tests = data.get('tests', [])
            
            # Simulate what the frontend copyFormData function expects
            print("📋 Simulating Email Template Generation:")
            
            test_summary = ""
            for test in tests:
                test_type = test.get('test_type', 'Unknown')
                test_date = test.get('test_date', 'Not specified')
                
                test_summary += f"\n--- {test_type} Test ---\n"
                test_summary += f"Date: {test_date}\n"
                
                if test_type == 'HIV':
                    test_summary += f"Result: {test.get('hiv_result', 'Not specified')}\n"
                    test_summary += f"Type: {test.get('hiv_type', 'Not specified')}\n"
                    test_summary += f"Tester: {test.get('hiv_tester', 'Not specified')}\n"
                
                elif test_type == 'HCV':
                    test_summary += f"Result: {test.get('hcv_result', 'Not specified')}\n"
                    test_summary += f"Tester: {test.get('hcv_tester', 'Not specified')}\n"
                
                elif test_type == 'Bloodwork':
                    test_summary += f"Type: {test.get('bloodwork_type', 'Not specified')}\n"
                    test_summary += f"Circles: {test.get('bloodwork_circles', 'Not specified')}\n"
                    test_summary += f"Result: {test.get('bloodwork_result', 'Not specified')}\n"
                    test_summary += f"Date Submitted: {test.get('bloodwork_date_submitted', 'Not specified')}\n"
                    test_summary += f"Tester: {test.get('bloodwork_tester', 'Not specified')}\n"
                
                test_summary += "\n"
            
            print(f"Generated Test Summary:\n{test_summary}")
            
            # Verify the summary contains expected content
            expected_content = [
                "HIV Test", "HCV Test", "Bloodwork Test",
                "negative", "positive", "DBS", "Pending"
            ]
            
            for content in expected_content:
                if content not in test_summary:
                    return self.log_test(
                        "Email Template Format", 
                        False, 
                        f"- Missing expected content: {content}"
                    )
            
            return self.log_test(
                "Email Template Format", 
                True, 
                f"- Test summary generated successfully with all expected content"
            )
            
        except Exception as e:
            return self.log_test(
                "Email Template Format", 
                False, 
                f"- Exception: {str(e)}"
            )
    
    def run_all_tests(self):
        """Run all tests in sequence"""
        print("🚀 STARTING TEST SUMMARY WORKFLOW TESTING")
        print("=" * 60)
        
        # Run tests in sequence
        test_results = [
            self.test_1_create_admin_registration(),
            self.test_2_create_hiv_test(),
            self.test_3_create_hcv_test(),
            self.test_4_create_bloodwork_test(),
            self.test_5_retrieve_all_tests(),
            self.test_6_verify_test_data_structure(),
            self.test_7_verify_email_template_data_format()
        ]
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Tests Failed: {self.tests_run - self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        if self.registration_id:
            print(f"\n📋 Test Registration ID: {self.registration_id}")
            print(f"📋 Test IDs Created: {self.test_ids}")
        
        # Overall result
        all_passed = all(test_results)
        if all_passed:
            print("\n🎉 ALL TESTS PASSED - Backend is ready for frontend integration!")
            print("✅ Registration creation works")
            print("✅ Test creation works for all types (HIV, HCV, Bloodwork)")
            print("✅ Test retrieval returns proper format {'tests': [...]}")
            print("✅ All test fields are populated correctly")
            print("✅ Data format is compatible with email template generation")
        else:
            print("\n❌ SOME TESTS FAILED - Issues found in backend implementation")
        
        return all_passed

if __name__ == "__main__":
    tester = TestSummaryWorkflowTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🔍 DIAGNOSIS: Backend API is fully functional for test summary workflow")
        print("If test data is not appearing in email templates, the issue is in frontend:")
        print("- Check if loadTests() is being called before copyFormData()")
        print("- Verify savedTests array is populated correctly")
        print("- Ensure currentRegistrationId is set after registration creation")
        print("- Check API response format handling (expecting {'tests': [...]})")
    else:
        print("\n🔍 DIAGNOSIS: Backend issues found that need to be fixed")
    
    exit(0 if success else 1)