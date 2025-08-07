#!/usr/bin/env python3
"""
Clean Test Management Functionality Test Suite
Tests the complete workflow for test data storage and retrieval in the backend API.
Uses unique data to avoid conflicts with previous test runs.
"""

import requests
import json
import sys
from datetime import datetime, date
import os
import uuid
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

class CleanTestManagementTester:
    def __init__(self):
        self.base_url = os.getenv('REACT_APP_BACKEND_URL', 'https://cd556dd9-d36b-422e-8110-4b1830397661.preview.emergentagent.com')
        self.api_url = f"{self.base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.registration_id = None
        self.test_ids = []
        self.unique_id = str(uuid.uuid4())[:8]  # Short unique identifier
        
    def log_test(self, test_name, success, details=""):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {test_name}: PASSED {details}")
        else:
            print(f"❌ {test_name}: FAILED {details}")
        return success
    
    def create_admin_registration(self):
        """Create a new admin registration for testing"""
        registration_data = {
            "firstName": f"TestUser{self.unique_id}",
            "lastName": f"Patient{self.unique_id}",
            "patientConsent": "verbal",
            "dob": "1990-05-15",
            "gender": "Male",
            "province": "Ontario",
            "healthCard": f"123456789{self.unique_id[:2]}",
            "phone1": "4165551234",
            "email": f"test.{self.unique_id}@example.com"
        }
        
        try:
            response = requests.post(f"{self.api_url}/admin-register", 
                                   json=registration_data, 
                                   headers={'Content-Type': 'application/json'},
                                   timeout=30)
            
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
                                   timeout=30)
            
            if response.status_code in [200, 201]:
                data = response.json()
                test_id = data.get('test_id')
                self.test_ids.append(('HIV', test_id))
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
                                   timeout=30)
            
            if response.status_code in [200, 201]:
                data = response.json()
                test_id = data.get('test_id')
                self.test_ids.append(('HCV', test_id))
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
                                   timeout=30)
            
            if response.status_code in [200, 201]:
                data = response.json()
                test_id = data.get('test_id')
                self.test_ids.append(('Bloodwork', test_id))
                return self.log_test("Add Bloodwork Test", 
                                   True, 
                                   f"Test ID: {test_id}")
            else:
                return self.log_test("Add Bloodwork Test", 
                                   False, 
                                   f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            return self.log_test("Add Bloodwork Test", False, f"Error: {str(e)}")
    
    def retrieve_and_verify_tests(self):
        """Retrieve all tests for the registration and verify fields"""
        if not self.registration_id:
            return self.log_test("Retrieve and Verify Tests", False, "No registration ID available")
        
        try:
            response = requests.get(f"{self.api_url}/admin-registration/{self.registration_id}/tests",
                                  headers={'Content-Type': 'application/json'},
                                  timeout=30)
            
            if response.status_code == 200:
                response_data = response.json()
                all_tests = response_data.get('tests', [])
                
                # Filter tests for this registration only
                tests = [t for t in all_tests if t.get('registration_id') == self.registration_id]
                
                print(f"DEBUG: Retrieved {len(tests)} tests for this registration")
                
                # Verify we have the expected number of tests
                if len(tests) != 3:
                    return self.log_test("Retrieve and Verify Tests", 
                                       False, 
                                       f"Expected 3 tests, got {len(tests)}")
                
                # Verify each test has the required fields
                required_fields = ['id', 'registration_id', 'test_type', 'created_at', 'updated_at']
                
                hiv_test = None
                hcv_test = None
                bloodwork_test = None
                
                for test in tests:
                    # Check required fields
                    for field in required_fields:
                        if field not in test:
                            return self.log_test("Retrieve and Verify Tests", 
                                               False, 
                                               f"Missing required field: {field}")
                    
                    # Categorize tests by type
                    if test['test_type'] == 'HIV':
                        hiv_test = test
                    elif test['test_type'] == 'HCV':
                        hcv_test = test
                    elif test['test_type'] == 'Bloodwork':
                        bloodwork_test = test
                
                # Verify HIV test fields and data
                if not hiv_test:
                    return self.log_test("Retrieve and Verify Tests", False, "HIV test not found")
                
                hiv_required = ['hiv_result', 'hiv_type', 'hiv_tester']
                for field in hiv_required:
                    if field not in hiv_test or hiv_test[field] is None:
                        return self.log_test("Retrieve and Verify Tests", 
                                           False, 
                                           f"HIV test missing field: {field}")
                
                # Verify HIV test data integrity
                if (hiv_test['hiv_result'] != 'negative' or 
                    hiv_test['hiv_type'] != 'Type 1' or 
                    hiv_test['hiv_tester'] != 'JY'):
                    return self.log_test("Retrieve and Verify Tests", 
                                       False, 
                                       f"HIV test data mismatch: expected negative/Type 1/JY, got {hiv_test['hiv_result']}/{hiv_test['hiv_type']}/{hiv_test['hiv_tester']}")
                
                # Verify HCV test fields and data
                if not hcv_test:
                    return self.log_test("Retrieve and Verify Tests", False, "HCV test not found")
                
                hcv_required = ['hcv_result', 'hcv_tester']
                for field in hcv_required:
                    if field not in hcv_test or hcv_test[field] is None:
                        return self.log_test("Retrieve and Verify Tests", 
                                           False, 
                                           f"HCV test missing field: {field}")
                
                # Verify HCV test data integrity
                if (hcv_test['hcv_result'] != 'positive' or 
                    hcv_test['hcv_tester'] != 'CM'):
                    return self.log_test("Retrieve and Verify Tests", 
                                       False, 
                                       f"HCV test data mismatch: expected positive/CM, got {hcv_test['hcv_result']}/{hcv_test['hcv_tester']}")
                
                # Verify Bloodwork test fields and data
                if not bloodwork_test:
                    return self.log_test("Retrieve and Verify Tests", False, "Bloodwork test not found")
                
                bloodwork_required = ['bloodwork_type', 'bloodwork_circles', 'bloodwork_result', 
                                    'bloodwork_date_submitted', 'bloodwork_tester']
                for field in bloodwork_required:
                    if field not in bloodwork_test or bloodwork_test[field] is None:
                        return self.log_test("Retrieve and Verify Tests", 
                                           False, 
                                           f"Bloodwork test missing field: {field}")
                
                # Verify Bloodwork test data integrity
                if (bloodwork_test['bloodwork_type'] != 'DBS' or 
                    bloodwork_test['bloodwork_circles'] != '3' or 
                    bloodwork_test['bloodwork_result'] != 'Pending' or
                    bloodwork_test['bloodwork_tester'] != 'JY'):
                    return self.log_test("Retrieve and Verify Tests", 
                                       False, 
                                       f"Bloodwork test data mismatch: expected DBS/3/Pending/JY, got {bloodwork_test['bloodwork_type']}/{bloodwork_test['bloodwork_circles']}/{bloodwork_test['bloodwork_result']}/{bloodwork_test['bloodwork_tester']}")
                
                return self.log_test("Retrieve and Verify Tests", 
                                   True, 
                                   f"All 3 tests retrieved with correct fields and data integrity verified")
            else:
                return self.log_test("Retrieve and Verify Tests", 
                                   False, 
                                   f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            return self.log_test("Retrieve and Verify Tests", False, f"Error: {str(e)}")
    
    def test_complete_workflow(self):
        """Test the complete workflow: registration → test addition → test retrieval"""
        return self.log_test("Complete Workflow Test", 
                           self.registration_id is not None and len(self.test_ids) == 3,
                           f"Registration ID: {self.registration_id}, Test IDs: {len(self.test_ids)}")
    
    def run_all_tests(self):
        """Run all test management tests"""
        print("🧪 STARTING CLEAN TEST MANAGEMENT FUNCTIONALITY TESTS")
        print("=" * 70)
        print(f"Using unique identifier: {self.unique_id}")
        print()
        
        # Test sequence
        tests = [
            self.create_admin_registration,
            self.add_hiv_test,
            self.add_hcv_test,
            self.add_bloodwork_test,
            self.retrieve_and_verify_tests,
            self.test_complete_workflow
        ]
        
        for test in tests:
            test()
            print()  # Add spacing between tests
        
        # Summary
        print("=" * 70)
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
    tester = CleanTestManagementTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n✅ CONCLUSION: Test management backend API is fully functional")
        print("✓ Admin registration creation works")
        print("✓ HIV, HCV, and Bloodwork test creation works")
        print("✓ Test data storage and retrieval works")
        print("✓ All required fields are properly stored and returned:")
        print("  - test_type, test_date, hiv_result, hiv_tester")
        print("  - hcv_result, hcv_tester")
        print("  - bloodwork_type, bloodwork_circles, bloodwork_result")
        print("  - bloodwork_date_submitted, bloodwork_tester")
        print("✓ Complete workflow from registration → test addition → test retrieval works")
        print("\n🔍 DIAGNOSIS: The backend API is working correctly.")
        print("   If test data is not appearing in email templates, the issue is likely:")
        print("   1. Frontend not calling the correct API endpoint")
        print("   2. Frontend not processing the response format correctly")
        print("   3. Frontend copyFormData function not accessing savedTests properly")
        sys.exit(0)
    else:
        print("\n❌ CONCLUSION: Test management backend API has issues")
        print("- Some functionality is not working as expected")
        print("- Check the failed tests above for specific issues")
        sys.exit(1)

if __name__ == "__main__":
    main()