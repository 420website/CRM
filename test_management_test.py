#!/usr/bin/env python3
"""
Test Management Functionality Test Suite
Tests the complete workflow for test data storage and retrieval in the backend API.

Focus areas:
1. Create a new admin registration
2. Add test data to the registration (including HIV, HCV, and Bloodwork tests)
3. Verify that tests are properly stored in the database
4. Retrieve tests for the registration and verify all fields are returned
5. Test the complete workflow: registration creation → test addition → test retrieval
"""

import requests
import json
import sys
from datetime import datetime, date
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

class TestManagementTester:
    def __init__(self):
        self.base_url = os.getenv('REACT_APP_BACKEND_URL', 'https://258401ff-ff29-421c-8498-4969ee7788f0.preview.emergentagent.com')
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
    
    def test_health_check(self):
        """Test if the backend is accessible"""
        try:
            # Try a simple endpoint that should exist
            response = requests.get(f"{self.api_url}/admin-registrations", timeout=10)
            return self.log_test("Backend Health Check", 
                               response.status_code in [200, 404], 
                               f"Status: {response.status_code}")
        except Exception as e:
            return self.log_test("Backend Health Check", False, f"Error: {str(e)}")
    
    def create_admin_registration(self):
        """Create a new admin registration for testing"""
        registration_data = {
            "firstName": "Test",
            "lastName": "Patient",
            "patientConsent": "verbal",
            "dob": "1990-05-15",
            "gender": "Male",
            "province": "Ontario",
            "healthCard": "1234567890AB",
            "phone1": "4165551234",
            "email": "test.patient@example.com",
            "address": "123 Test Street",
            "city": "Toronto",
            "postalCode": "M5V 3A8"
        }
        
        try:
            response = requests.post(f"{self.api_url}/admin-register", 
                                   json=registration_data, 
                                   headers={'Content-Type': 'application/json'},
                                   timeout=10)
            
            if response.status_code in [200, 201]:
                data = response.json()
                self.registration_id = data.get('registration_id')
                return self.log_test("Create Admin Registration", 
                                   True, 
                                   f"Registration ID: {self.registration_id}")
            else:
                return self.log_test("Create Admin Registration", 
                                   False, 
                                   f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            return self.log_test("Create Admin Registration", False, f"Error: {str(e)}")
    
    def add_hiv_test(self):
        """Add an HIV test to the registration"""
        if not self.registration_id:
            return self.log_test("Add HIV Test", False, "No registration ID available")
        
        hiv_test_data = {
            "test_type": "HIV",
            "test_date": "2024-01-15",
            "hiv_result": "negative",
            "hiv_type": "Type 1",
            "hiv_tester": "JY"
        }
        
        try:
            response = requests.post(f"{self.api_url}/admin-registration/{self.registration_id}/test",
                                   json=hiv_test_data,
                                   headers={'Content-Type': 'application/json'},
                                   timeout=10)
            
            if response.status_code in [200, 201]:
                data = response.json()
                test_id = data.get('test_id')
                self.test_ids.append(test_id)
                return self.log_test("Add HIV Test", 
                                   True, 
                                   f"Test ID: {test_id}")
            else:
                return self.log_test("Add HIV Test", 
                                   False, 
                                   f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            return self.log_test("Add HIV Test", False, f"Error: {str(e)}")
    
    def add_hcv_test(self):
        """Add an HCV test to the registration"""
        if not self.registration_id:
            return self.log_test("Add HCV Test", False, "No registration ID available")
        
        hcv_test_data = {
            "test_type": "HCV",
            "test_date": "2024-01-16",
            "hcv_result": "positive",
            "hcv_tester": "CM"
        }
        
        try:
            response = requests.post(f"{self.api_url}/admin-registration/{self.registration_id}/test",
                                   json=hcv_test_data,
                                   headers={'Content-Type': 'application/json'},
                                   timeout=10)
            
            if response.status_code in [200, 201]:
                data = response.json()
                test_id = data.get('test_id')
                self.test_ids.append(test_id)
                return self.log_test("Add HCV Test", 
                                   True, 
                                   f"Test ID: {test_id}")
            else:
                return self.log_test("Add HCV Test", 
                                   False, 
                                   f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            return self.log_test("Add HCV Test", False, f"Error: {str(e)}")
    
    def add_bloodwork_test(self):
        """Add a Bloodwork test to the registration"""
        if not self.registration_id:
            return self.log_test("Add Bloodwork Test", False, "No registration ID available")
        
        bloodwork_test_data = {
            "test_type": "Bloodwork",
            "test_date": "2024-01-17",
            "bloodwork_type": "DBS",
            "bloodwork_circles": "3",
            "bloodwork_result": "Pending",
            "bloodwork_date_submitted": "2024-01-18",
            "bloodwork_tester": "JY"
        }
        
        try:
            response = requests.post(f"{self.api_url}/admin-registration/{self.registration_id}/test",
                                   json=bloodwork_test_data,
                                   headers={'Content-Type': 'application/json'},
                                   timeout=10)
            
            if response.status_code in [200, 201]:
                data = response.json()
                test_id = data.get('test_id')
                self.test_ids.append(test_id)
                return self.log_test("Add Bloodwork Test", 
                                   True, 
                                   f"Test ID: {test_id}")
            else:
                return self.log_test("Add Bloodwork Test", 
                                   False, 
                                   f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            return self.log_test("Add Bloodwork Test", False, f"Error: {str(e)}")
    
    def retrieve_all_tests(self):
        """Retrieve all tests for the registration and verify fields"""
        if not self.registration_id:
            return self.log_test("Retrieve All Tests", False, "No registration ID available")
        
        try:
            response = requests.get(f"{self.api_url}/admin-registration/{self.registration_id}/tests",
                                  headers={'Content-Type': 'application/json'},
                                  timeout=30)
            
            if response.status_code == 200:
                response_data = response.json()
                tests = response_data.get('tests', [])
                
                print(f"DEBUG: Retrieved {len(tests)} tests")
                for i, test in enumerate(tests):
                    print(f"DEBUG: Test {i+1}: {test.get('test_type', 'Unknown')} - ID: {test.get('id', 'No ID')}")
                
                # Verify we have at least some tests (may not be 3 if there were issues)
                if len(tests) == 0:
                    return self.log_test("Retrieve All Tests", 
                                       False, 
                                       f"No tests found")
                
                # Verify each test has the required fields
                required_fields = ['id', 'registration_id', 'test_type', 'created_at', 'updated_at']
                
                hiv_test = None
                hcv_test = None
                bloodwork_test = None
                
                for test in tests:
                    # Check required fields
                    for field in required_fields:
                        if field not in test:
                            return self.log_test("Retrieve All Tests", 
                                               False, 
                                               f"Missing required field: {field}")
                    
                    # Categorize tests by type
                    if test['test_type'] == 'HIV':
                        hiv_test = test
                    elif test['test_type'] == 'HCV':
                        hcv_test = test
                    elif test['test_type'] == 'Bloodwork':
                        bloodwork_test = test
                
                # Verify HIV test fields
                if not hiv_test:
                    return self.log_test("Retrieve All Tests", False, "HIV test not found")
                
                hiv_required = ['hiv_result', 'hiv_type', 'hiv_tester']
                for field in hiv_required:
                    if field not in hiv_test or hiv_test[field] is None:
                        return self.log_test("Retrieve All Tests", 
                                           False, 
                                           f"HIV test missing field: {field}")
                
                # Verify HCV test fields
                if not hcv_test:
                    return self.log_test("Retrieve All Tests", False, "HCV test not found")
                
                hcv_required = ['hcv_result', 'hcv_tester']
                for field in hcv_required:
                    if field not in hcv_test or hcv_test[field] is None:
                        return self.log_test("Retrieve All Tests", 
                                           False, 
                                           f"HCV test missing field: {field}")
                
                # Verify Bloodwork test fields
                if not bloodwork_test:
                    return self.log_test("Retrieve All Tests", False, "Bloodwork test not found")
                
                bloodwork_required = ['bloodwork_type', 'bloodwork_circles', 'bloodwork_result', 
                                    'bloodwork_date_submitted', 'bloodwork_tester']
                for field in bloodwork_required:
                    if field not in bloodwork_test or bloodwork_test[field] is None:
                        return self.log_test("Retrieve All Tests", 
                                           False, 
                                           f"Bloodwork test missing field: {field}")
                
                return self.log_test("Retrieve All Tests", 
                                   True, 
                                   f"Retrieved {len(tests)} tests with correct fields")
            else:
                return self.log_test("Retrieve All Tests", 
                                   False, 
                                   f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            return self.log_test("Retrieve All Tests", False, f"Error: {str(e)}")
    
    def verify_test_data_integrity(self):
        """Verify that test data matches what was submitted"""
        if not self.registration_id:
            return self.log_test("Verify Test Data Integrity", False, "No registration ID available")
        
        try:
            response = requests.get(f"{self.api_url}/admin-registration/{self.registration_id}/tests",
                                  headers={'Content-Type': 'application/json'},
                                  timeout=30)
            
            if response.status_code == 200:
                response_data = response.json()
                tests = response_data.get('tests', [])
                
                # Find each test type and verify data
                for test in tests:
                    if test['test_type'] == 'HIV':
                        if (test['hiv_result'] != 'negative' or 
                            test['hiv_type'] != 'Type 1' or 
                            test['hiv_tester'] != 'JY'):
                            return self.log_test("Verify Test Data Integrity", 
                                               False, 
                                               f"HIV test data mismatch: {test}")
                    
                    elif test['test_type'] == 'HCV':
                        if (test['hcv_result'] != 'positive' or 
                            test['hcv_tester'] != 'CM'):
                            return self.log_test("Verify Test Data Integrity", 
                                               False, 
                                               f"HCV test data mismatch: {test}")
                    
                    elif test['test_type'] == 'Bloodwork':
                        if (test['bloodwork_type'] != 'DBS' or 
                            test['bloodwork_circles'] != '3' or 
                            test['bloodwork_result'] != 'Pending' or
                            test['bloodwork_tester'] != 'JY'):
                            return self.log_test("Verify Test Data Integrity", 
                                               False, 
                                               f"Bloodwork test data mismatch: {test}")
                
                return self.log_test("Verify Test Data Integrity", 
                                   True, 
                                   "All test data matches submitted values")
            else:
                return self.log_test("Verify Test Data Integrity", 
                                   False, 
                                   f"Status: {response.status_code}")
        except Exception as e:
            return self.log_test("Verify Test Data Integrity", False, f"Error: {str(e)}")
    
    def test_update_test(self):
        """Test updating a test record"""
        if not self.test_ids:
            return self.log_test("Test Update Test", False, "No test IDs available")
        
        # Update the HIV test
        hiv_test_id = self.test_ids[0]  # First test should be HIV
        
        update_data = {
            "hiv_result": "positive",
            "hiv_type": "Type 2",
            "hiv_tester": "CM"
        }
        
        try:
            response = requests.put(f"{self.api_url}/admin-registration/{self.registration_id}/test/{hiv_test_id}",
                                  json=update_data,
                                  headers={'Content-Type': 'application/json'},
                                  timeout=10)
            
            if response.status_code == 200:
                # Verify the update worked
                get_response = requests.get(f"{self.api_url}/admin-registration/{self.registration_id}/tests",
                                          headers={'Content-Type': 'application/json'},
                                          timeout=10)
                
                if get_response.status_code == 200:
                    response_data = get_response.json()
                    tests = response_data.get('tests', [])
                    hiv_test = next((t for t in tests if t['test_type'] == 'HIV'), None)
                    
                    if (hiv_test and 
                        hiv_test['hiv_result'] == 'positive' and 
                        hiv_test['hiv_type'] == 'Type 2' and 
                        hiv_test['hiv_tester'] == 'CM'):
                        return self.log_test("Test Update Test", 
                                           True, 
                                           "HIV test updated successfully")
                    else:
                        return self.log_test("Test Update Test", 
                                           False, 
                                           f"Update not reflected: {hiv_test}")
                else:
                    return self.log_test("Test Update Test", 
                                       False, 
                                       f"Failed to retrieve updated test: {get_response.status_code}")
            else:
                return self.log_test("Test Update Test", 
                                   False, 
                                   f"Update failed: {response.status_code}, {response.text}")
        except Exception as e:
            return self.log_test("Test Update Test", False, f"Error: {str(e)}")
    
    def test_delete_test(self):
        """Test deleting a test record"""
        if not self.test_ids or len(self.test_ids) < 2:
            return self.log_test("Test Delete Test", False, "Not enough test IDs available")
        
        # Delete the HCV test (second test)
        hcv_test_id = self.test_ids[1]
        
        try:
            response = requests.delete(f"{self.api_url}/admin-registration/{self.registration_id}/test/{hcv_test_id}",
                                     headers={'Content-Type': 'application/json'},
                                     timeout=10)
            
            if response.status_code == 200:
                # Verify the test was deleted
                get_response = requests.get(f"{self.api_url}/admin-registration/{self.registration_id}/tests",
                                          headers={'Content-Type': 'application/json'},
                                          timeout=10)
                
                if get_response.status_code == 200:
                    response_data = get_response.json()
                    tests = response_data.get('tests', [])
                    hcv_test = next((t for t in tests if t['test_type'] == 'HCV'), None)
                    
                    if hcv_test is None:
                        return self.log_test("Test Delete Test", 
                                           True, 
                                           "HCV test deleted successfully")
                    else:
                        return self.log_test("Test Delete Test", 
                                           False, 
                                           "HCV test still exists after deletion")
                else:
                    return self.log_test("Test Delete Test", 
                                       False, 
                                       f"Failed to retrieve tests after deletion: {get_response.status_code}")
            else:
                return self.log_test("Test Delete Test", 
                                   False, 
                                   f"Delete failed: {response.status_code}, {response.text}")
        except Exception as e:
            return self.log_test("Test Delete Test", False, f"Error: {str(e)}")
    
    def run_all_tests(self):
        """Run all test management tests"""
        print("🧪 STARTING TEST MANAGEMENT FUNCTIONALITY TESTS")
        print("=" * 60)
        
        # Test sequence
        tests = [
            self.test_health_check,
            self.create_admin_registration,
            self.add_hiv_test,
            self.add_hcv_test,
            self.add_bloodwork_test,
            self.retrieve_all_tests,
            self.verify_test_data_integrity,
            self.test_update_test,
            self.test_delete_test
        ]
        
        for test in tests:
            test()
            print()  # Add spacing between tests
        
        # Summary
        print("=" * 60)
        print(f"📊 TEST SUMMARY")
        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Tests Failed: {self.tests_run - self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        if self.tests_passed == self.tests_run:
            print("🎉 ALL TESTS PASSED - Test management functionality is working correctly!")
            return True
        else:
            print("⚠️  SOME TESTS FAILED - Test management functionality has issues")
            return False

def main():
    """Main function to run the test suite"""
    tester = TestManagementTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n✅ CONCLUSION: Test management backend API is fully functional")
        print("- Admin registration creation works")
        print("- HIV, HCV, and Bloodwork test creation works")
        print("- Test data storage and retrieval works")
        print("- All required fields are properly stored and returned")
        print("- Test update and delete operations work")
        print("- Complete workflow from registration → test addition → test retrieval works")
        sys.exit(0)
    else:
        print("\n❌ CONCLUSION: Test management backend API has issues")
        print("- Some functionality is not working as expected")
        print("- Check the failed tests above for specific issues")
        sys.exit(1)

if __name__ == "__main__":
    main()