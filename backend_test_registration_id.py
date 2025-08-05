import requests
import unittest
import json
from datetime import datetime, date
import random
import string
import sys
import os
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables
load_dotenv('/app/frontend/.env')
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL')

if not BACKEND_URL:
    logging.error("REACT_APP_BACKEND_URL not found in environment variables")
    sys.exit(1)

logging.info(f"Using backend URL: {BACKEND_URL}")

class TestsTabRegistrationIdTester:
    def __init__(self):
        self.backend_url = BACKEND_URL
        self.registration_id = None
        self.test_id = None
        self.test_data = {}
        
    def generate_test_data(self):
        """Generate random test data for registration"""
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
        
        self.test_data = {
            "admin_registration": {
                "firstName": f"Test{random_suffix}",
                "lastName": f"User{random_suffix}",
                "patientConsent": "Verbal",
                "gender": "Male",
                "province": "Ontario",
                "disposition": "POCT NEG",
                "healthCard": ''.join(random.choices(string.digits, k=10)),
                "email": f"test.user.{random_suffix}@example.com",
            },
            "hiv_test": {
                "test_type": "HIV",
                "test_date": date.today().isoformat(),
                "hiv_result": "negative",
                "hiv_tester": "CM"
            },
            "hcv_test": {
                "test_type": "HCV",
                "test_date": date.today().isoformat(),
                "hcv_result": "positive",
                "hcv_tester": "JY"
            }
        }
        
        return self.test_data
    
    def test_admin_registration_creation(self):
        """Test creating a new admin registration"""
        logging.info("Testing admin registration creation...")
        
        if not self.test_data:
            self.generate_test_data()
        
        url = f"{self.backend_url}/api/admin-register"
        headers = {'Content-Type': 'application/json'}
        
        try:
            response = requests.post(url, json=self.test_data["admin_registration"], headers=headers)
            
            if response.status_code == 200:
                response_data = response.json()
                self.registration_id = response_data.get("registration_id")
                status = response_data.get("status")
                
                logging.info(f"✅ Admin registration created successfully")
                logging.info(f"Registration ID: {self.registration_id}")
                logging.info(f"Status: {status}")
                
                if not self.registration_id:
                    logging.error("❌ Registration ID not returned in response")
                    return False
                
                if status != "pending_review":
                    logging.error(f"❌ Unexpected status: {status}, expected: pending_review")
                    return False
                
                return True
            else:
                logging.error(f"❌ Failed to create admin registration: {response.status_code}")
                try:
                    logging.error(f"Response: {response.json()}")
                except:
                    logging.error(f"Response: {response.text}")
                return False
                
        except Exception as e:
            logging.error(f"❌ Exception during admin registration creation: {str(e)}")
            return False
    
    def test_get_registration(self):
        """Test retrieving the created registration"""
        if not self.registration_id:
            logging.error("❌ No registration ID available for testing")
            return False
        
        logging.info(f"Testing retrieval of registration {self.registration_id}...")
        
        url = f"{self.backend_url}/api/admin-registration/{self.registration_id}"
        headers = {'Content-Type': 'application/json'}
        
        try:
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                registration_data = response.json()
                
                logging.info(f"✅ Registration retrieved successfully")
                
                # Verify registration data
                if registration_data.get("id") != self.registration_id:
                    logging.error(f"❌ Registration ID mismatch: {registration_data.get('id')} != {self.registration_id}")
                    return False
                
                if registration_data.get("firstName") != self.test_data["admin_registration"]["firstName"]:
                    logging.error(f"❌ First name mismatch: {registration_data.get('firstName')} != {self.test_data['admin_registration']['firstName']}")
                    return False
                
                if registration_data.get("lastName") != self.test_data["admin_registration"]["lastName"]:
                    logging.error(f"❌ Last name mismatch: {registration_data.get('lastName')} != {self.test_data['admin_registration']['lastName']}")
                    return False
                
                if registration_data.get("status") != "pending_review":
                    logging.error(f"❌ Status mismatch: {registration_data.get('status')} != pending_review")
                    return False
                
                logging.info(f"✅ Registration data verified")
                return True
            else:
                logging.error(f"❌ Failed to retrieve registration: {response.status_code}")
                try:
                    logging.error(f"Response: {response.json()}")
                except:
                    logging.error(f"Response: {response.text}")
                return False
                
        except Exception as e:
            logging.error(f"❌ Exception during registration retrieval: {str(e)}")
            return False
    
    def test_add_hiv_test(self):
        """Test adding an HIV test to the registration"""
        if not self.registration_id:
            logging.error("❌ No registration ID available for testing")
            return False
        
        logging.info(f"Testing adding HIV test to registration {self.registration_id}...")
        
        url = f"{self.backend_url}/api/admin-registration/{self.registration_id}/test"
        headers = {'Content-Type': 'application/json'}
        
        try:
            response = requests.post(url, json=self.test_data["hiv_test"], headers=headers)
            
            if response.status_code == 200:
                response_data = response.json()
                self.test_id = response_data.get("test_id")
                
                logging.info(f"✅ HIV test added successfully")
                logging.info(f"Test ID: {self.test_id}")
                
                if not self.test_id:
                    logging.error("❌ Test ID not returned in response")
                    return False
                
                return True
            else:
                logging.error(f"❌ Failed to add HIV test: {response.status_code}")
                try:
                    logging.error(f"Response: {response.json()}")
                except:
                    logging.error(f"Response: {response.text}")
                return False
                
        except Exception as e:
            logging.error(f"❌ Exception during HIV test addition: {str(e)}")
            return False
    
    def test_add_hcv_test(self):
        """Test adding an HCV test to the registration"""
        if not self.registration_id:
            logging.error("❌ No registration ID available for testing")
            return False
        
        logging.info(f"Testing adding HCV test to registration {self.registration_id}...")
        
        url = f"{self.backend_url}/api/admin-registration/{self.registration_id}/test"
        headers = {'Content-Type': 'application/json'}
        
        try:
            response = requests.post(url, json=self.test_data["hcv_test"], headers=headers)
            
            if response.status_code == 200:
                response_data = response.json()
                hcv_test_id = response_data.get("test_id")
                
                logging.info(f"✅ HCV test added successfully")
                logging.info(f"Test ID: {hcv_test_id}")
                
                if not hcv_test_id:
                    logging.error("❌ Test ID not returned in response")
                    return False
                
                return True
            else:
                logging.error(f"❌ Failed to add HCV test: {response.status_code}")
                try:
                    logging.error(f"Response: {response.json()}")
                except:
                    logging.error(f"Response: {response.text}")
                return False
                
        except Exception as e:
            logging.error(f"❌ Exception during HCV test addition: {str(e)}")
            return False
    
    def test_get_tests(self):
        """Test retrieving tests for the registration"""
        if not self.registration_id:
            logging.error("❌ No registration ID available for testing")
            return False
        
        logging.info(f"Testing retrieval of tests for registration {self.registration_id}...")
        
        url = f"{self.backend_url}/api/admin-registration/{self.registration_id}/tests"
        headers = {'Content-Type': 'application/json'}
        
        try:
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                response_data = response.json()
                tests = response_data.get("tests", [])
                
                logging.info(f"✅ Tests retrieved successfully")
                logging.info(f"Number of tests: {len(tests)}")
                
                if len(tests) < 2:
                    logging.error(f"❌ Expected at least 2 tests, got {len(tests)}")
                    return False
                
                # Verify test data
                hiv_test = None
                hcv_test = None
                
                for test in tests:
                    if test.get("test_type") == "HIV":
                        hiv_test = test
                    elif test.get("test_type") == "HCV":
                        hcv_test = test
                
                if not hiv_test:
                    logging.error("❌ HIV test not found in retrieved tests")
                    return False
                
                if not hcv_test:
                    logging.error("❌ HCV test not found in retrieved tests")
                    return False
                
                # Verify HIV test data
                if hiv_test.get("hiv_result") != self.test_data["hiv_test"]["hiv_result"]:
                    logging.error(f"❌ HIV result mismatch: {hiv_test.get('hiv_result')} != {self.test_data['hiv_test']['hiv_result']}")
                    return False
                
                if hiv_test.get("hiv_tester") != self.test_data["hiv_test"]["hiv_tester"]:
                    logging.error(f"❌ HIV tester mismatch: {hiv_test.get('hiv_tester')} != {self.test_data['hiv_test']['hiv_tester']}")
                    return False
                
                # Verify HCV test data
                if hcv_test.get("hcv_result") != self.test_data["hcv_test"]["hcv_result"]:
                    logging.error(f"❌ HCV result mismatch: {hcv_test.get('hcv_result')} != {self.test_data['hcv_test']['hcv_result']}")
                    return False
                
                if hcv_test.get("hcv_tester") != self.test_data["hcv_test"]["hcv_tester"]:
                    logging.error(f"❌ HCV tester mismatch: {hcv_test.get('hcv_tester')} != {self.test_data['hcv_test']['hcv_tester']}")
                    return False
                
                # Most importantly, verify registration_id is correctly set
                if hiv_test.get("registration_id") != self.registration_id:
                    logging.error(f"❌ HIV test registration_id mismatch: {hiv_test.get('registration_id')} != {self.registration_id}")
                    return False
                
                if hcv_test.get("registration_id") != self.registration_id:
                    logging.error(f"❌ HCV test registration_id mismatch: {hcv_test.get('registration_id')} != {self.registration_id}")
                    return False
                
                logging.info(f"✅ Test data verified")
                return True
            else:
                logging.error(f"❌ Failed to retrieve tests: {response.status_code}")
                try:
                    logging.error(f"Response: {response.json()}")
                except:
                    logging.error(f"Response: {response.text}")
                return False
                
        except Exception as e:
            logging.error(f"❌ Exception during tests retrieval: {str(e)}")
            return False
    
    def test_update_test(self):
        """Test updating a test"""
        if not self.registration_id or not self.test_id:
            logging.error("❌ No registration ID or test ID available for testing")
            return False
        
        logging.info(f"Testing updating test {self.test_id} for registration {self.registration_id}...")
        
        url = f"{self.backend_url}/api/admin-registration/{self.registration_id}/test/{self.test_id}"
        headers = {'Content-Type': 'application/json'}
        
        # Update HIV test to positive
        update_data = {
            "hiv_result": "positive",
            "hiv_type": "Type 1",
            "hiv_tester": "JD"
        }
        
        try:
            response = requests.put(url, json=update_data, headers=headers)
            
            if response.status_code == 200:
                logging.info(f"✅ Test updated successfully")
                
                # Verify the update by retrieving the tests again
                get_tests_url = f"{self.backend_url}/api/admin-registration/{self.registration_id}/tests"
                get_response = requests.get(get_tests_url, headers=headers)
                
                if get_response.status_code == 200:
                    tests = get_response.json().get("tests", [])
                    
                    # Find the updated test
                    updated_test = None
                    for test in tests:
                        if test.get("id") == self.test_id:
                            updated_test = test
                            break
                    
                    if not updated_test:
                        logging.error(f"❌ Updated test not found in retrieved tests")
                        return False
                    
                    # Verify updated fields
                    if updated_test.get("hiv_result") != update_data["hiv_result"]:
                        logging.error(f"❌ Updated HIV result mismatch: {updated_test.get('hiv_result')} != {update_data['hiv_result']}")
                        return False
                    
                    if updated_test.get("hiv_type") != update_data["hiv_type"]:
                        logging.error(f"❌ Updated HIV type mismatch: {updated_test.get('hiv_type')} != {update_data['hiv_type']}")
                        return False
                    
                    if updated_test.get("hiv_tester") != update_data["hiv_tester"]:
                        logging.error(f"❌ Updated HIV tester mismatch: {updated_test.get('hiv_tester')} != {update_data['hiv_tester']}")
                        return False
                    
                    logging.info(f"✅ Test update verified")
                    return True
                else:
                    logging.error(f"❌ Failed to verify test update: {get_response.status_code}")
                    return False
            else:
                logging.error(f"❌ Failed to update test: {response.status_code}")
                try:
                    logging.error(f"Response: {response.json()}")
                except:
                    logging.error(f"Response: {response.text}")
                return False
                
        except Exception as e:
            logging.error(f"❌ Exception during test update: {str(e)}")
            return False
    
    def test_delete_test(self):
        """Test deleting a test"""
        if not self.registration_id or not self.test_id:
            logging.error("❌ No registration ID or test ID available for testing")
            return False
        
        logging.info(f"Testing deleting test {self.test_id} for registration {self.registration_id}...")
        
        url = f"{self.backend_url}/api/admin-registration/{self.registration_id}/test/{self.test_id}"
        headers = {'Content-Type': 'application/json'}
        
        try:
            response = requests.delete(url, headers=headers)
            
            if response.status_code == 200:
                logging.info(f"✅ Test deleted successfully")
                
                # Verify the deletion by retrieving the tests again
                get_tests_url = f"{self.backend_url}/api/admin-registration/{self.registration_id}/tests"
                get_response = requests.get(get_tests_url, headers=headers)
                
                if get_response.status_code == 200:
                    tests = get_response.json().get("tests", [])
                    
                    # Check that the deleted test is not in the list
                    for test in tests:
                        if test.get("id") == self.test_id:
                            logging.error(f"❌ Deleted test still found in retrieved tests")
                            return False
                    
                    logging.info(f"✅ Test deletion verified")
                    return True
                else:
                    logging.error(f"❌ Failed to verify test deletion: {get_response.status_code}")
                    return False
            else:
                logging.error(f"❌ Failed to delete test: {response.status_code}")
                try:
                    logging.error(f"Response: {response.json()}")
                except:
                    logging.error(f"Response: {response.text}")
                return False
                
        except Exception as e:
            logging.error(f"❌ Exception during test deletion: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all tests in sequence"""
        logging.info("Starting Tests Tab Registration ID tests...")
        
        # Generate test data
        self.generate_test_data()
        
        # Run tests in sequence
        tests = [
            ("Admin Registration Creation", self.test_admin_registration_creation),
            ("Get Registration", self.test_get_registration),
            ("Add HIV Test", self.test_add_hiv_test),
            ("Add HCV Test", self.test_add_hcv_test),
            ("Get Tests", self.test_get_tests),
            ("Update Test", self.test_update_test),
            ("Delete Test", self.test_delete_test)
        ]
        
        results = {}
        all_passed = True
        
        for test_name, test_func in tests:
            logging.info(f"\n{'=' * 50}\nRunning test: {test_name}\n{'=' * 50}")
            result = test_func()
            results[test_name] = result
            
            if not result:
                all_passed = False
                logging.error(f"❌ Test '{test_name}' failed")
            else:
                logging.info(f"✅ Test '{test_name}' passed")
        
        # Print summary
        logging.info("\n\n" + "=" * 50)
        logging.info("TEST RESULTS SUMMARY")
        logging.info("=" * 50)
        
        for test_name, result in results.items():
            status = "✅ PASSED" if result else "❌ FAILED"
            logging.info(f"{test_name}: {status}")
        
        if all_passed:
            logging.info("\n✅ ALL TESTS PASSED")
            return 0
        else:
            logging.error("\n❌ SOME TESTS FAILED")
            return 1

if __name__ == "__main__":
    tester = TestsTabRegistrationIdTester()
    sys.exit(tester.run_all_tests())