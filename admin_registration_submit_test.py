#!/usr/bin/env python3
"""
Admin Registration Submit Functionality Test
Focus: Testing the POST /api/admin-register endpoint specifically for submit button issues
"""

import requests
import json
from datetime import datetime, date
import uuid
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

class AdminRegistrationSubmitTester:
    def __init__(self):
        # Use the same URL that frontend uses
        self.base_url = os.getenv('REACT_APP_BACKEND_URL', 'https://dfe9a1e1-7f3d-45aa-ad71-43a254e568c5.preview.emergentagent.com')
        self.api_url = f"{self.base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.registration_ids = []
        
    def log_test(self, test_name, success, details=""):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {test_name}: PASSED {details}")
        else:
            print(f"❌ {test_name}: FAILED {details}")
    
    def test_health_check(self):
        """Test if the backend is accessible"""
        try:
            # Try the root API endpoint
            response = requests.get(f"{self.api_url}/", timeout=10)
            success = response.status_code == 200
            self.log_test("Backend Health Check", success, f"Status: {response.status_code}")
            return success
        except Exception as e:
            self.log_test("Backend Health Check", False, f"Error: {str(e)}")
            return False
    
    def create_sample_registration_data(self, unique_suffix=""):
        """Create sample registration data that matches frontend structure"""
        return {
            "firstName": f"John{unique_suffix}",
            "lastName": f"Doe{unique_suffix}",
            "dob": "1990-05-15",
            "patientConsent": "verbal",
            "gender": "Male",
            "province": "Ontario",
            "disposition": "Active",
            "aka": "",
            "age": "33",
            "regDate": date.today().isoformat(),
            "healthCard": "1234567890AB",
            "healthCardVersion": "AB",
            "referralSite": "Walk-in",
            "address": "123 Main Street",
            "unitNumber": "Apt 1",
            "city": "Toronto",
            "postalCode": "M5V 3A8",
            "phone1": "4161234567",
            "phone2": "",
            "ext1": "",
            "ext2": "",
            "leaveMessage": True,
            "voicemail": False,
            "text": True,
            "preferredTime": "Morning",
            "email": f"john.doe{unique_suffix}@example.com",
            "language": "English",
            "specialAttention": "None",
            "photo": None,
            "summaryTemplate": "Standard template",
            "physician": "Dr. David Fletcher",
            "rnaAvailable": "No",
            "rnaSampleDate": None,
            "rnaResult": "Positive",
            "coverageType": "Select",
            "referralPerson": "Self-referral",
            "testType": "Tests",
            "hivDate": None,
            "hivResult": None,
            "hivType": None,
            "hivTester": "CM"
        }
    
    def test_admin_registration_submit(self):
        """Test the main admin registration submission endpoint"""
        print("\n🔍 Testing Admin Registration Submit Functionality...")
        
        # Test 1: Basic registration submission
        registration_data = self.create_sample_registration_data("_test1")
        
        try:
            response = requests.post(
                f"{self.api_url}/admin-register",
                json=registration_data,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            success = response.status_code == 200
            if success:
                response_data = response.json()
                
                # Check if response contains registration_id
                if 'registration_id' in response_data:
                    registration_id = response_data['registration_id']
                    self.registration_ids.append(registration_id)
                    self.log_test("Basic Registration Submit", True, f"Registration ID: {registration_id}")
                    
                    # Verify the registration_id is a valid UUID format
                    try:
                        uuid.UUID(registration_id)
                        self.log_test("Registration ID Format", True, "Valid UUID format")
                    except ValueError:
                        self.log_test("Registration ID Format", False, "Invalid UUID format")
                    
                    return True, response_data
                else:
                    self.log_test("Basic Registration Submit", False, "No registration_id in response")
                    print(f"Response data: {response_data}")
                    return False, response_data
            else:
                self.log_test("Basic Registration Submit", False, f"Status: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"Error response: {error_data}")
                except:
                    print(f"Raw response: {response.text}")
                return False, {}
                
        except Exception as e:
            self.log_test("Basic Registration Submit", False, f"Exception: {str(e)}")
            return False, {}
    
    def test_required_fields_validation(self):
        """Test validation of required fields"""
        print("\n🔍 Testing Required Fields Validation...")
        
        # Test with missing firstName
        incomplete_data = self.create_sample_registration_data("_validation")
        del incomplete_data['firstName']
        
        try:
            response = requests.post(
                f"{self.api_url}/admin-register",
                json=incomplete_data,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            # Should return 422 for validation error
            success = response.status_code == 422
            self.log_test("Missing firstName Validation", success, f"Status: {response.status_code}")
            
        except Exception as e:
            self.log_test("Missing firstName Validation", False, f"Exception: {str(e)}")
        
        # Test with missing lastName
        incomplete_data = self.create_sample_registration_data("_validation2")
        del incomplete_data['lastName']
        
        try:
            response = requests.post(
                f"{self.api_url}/admin-register",
                json=incomplete_data,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            success = response.status_code == 422
            self.log_test("Missing lastName Validation", success, f"Status: {response.status_code}")
            
        except Exception as e:
            self.log_test("Missing lastName Validation", False, f"Exception: {str(e)}")
        
        # Test with missing patientConsent
        incomplete_data = self.create_sample_registration_data("_validation3")
        del incomplete_data['patientConsent']
        
        try:
            response = requests.post(
                f"{self.api_url}/admin-register",
                json=incomplete_data,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            success = response.status_code == 422
            self.log_test("Missing patientConsent Validation", success, f"Status: {response.status_code}")
            
        except Exception as e:
            self.log_test("Missing patientConsent Validation", False, f"Exception: {str(e)}")
    
    def test_speech_to_text_data_structure(self):
        """Test with data structure that might come from speech-to-text"""
        print("\n🔍 Testing Speech-to-Text Data Structure...")
        
        # Create data that might come from speech-to-text (with some fields as strings)
        speech_data = {
            "firstName": "Jane",
            "lastName": "Smith",
            "dob": "1985-03-20",
            "patientConsent": "verbal",
            "gender": "Female",
            "province": "Ontario",
            "disposition": "Active",
            "aka": "",
            "age": "38",  # Age as string (common from speech)
            "regDate": date.today().isoformat(),
            "healthCard": "9876543210CD",
            "healthCardVersion": "CD",
            "referralSite": "Community Center",
            "address": "456 Oak Avenue",
            "unitNumber": "",
            "city": "Toronto",
            "postalCode": "M4B 1B3",
            "phone1": "4169876543",
            "phone2": "",
            "ext1": "",
            "ext2": "",
            "leaveMessage": "true",  # Boolean as string
            "voicemail": "false",    # Boolean as string
            "text": "true",          # Boolean as string
            "preferredTime": "Afternoon",
            "email": "jane.smith@example.com",
            "language": "English",
            "specialAttention": "Hearing impaired",
            "photo": None,
            "summaryTemplate": "Standard template",
            "physician": "Dr. David Fletcher",
            "rnaAvailable": "No",
            "rnaSampleDate": None,
            "rnaResult": "Positive",
            "coverageType": "ODSP",
            "referralPerson": "Social worker",
            "testType": "Tests",
            "hivDate": None,
            "hivResult": None,
            "hivType": None,
            "hivTester": "CM"
        }
        
        try:
            response = requests.post(
                f"{self.api_url}/admin-register",
                json=speech_data,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            success = response.status_code == 200
            if success:
                response_data = response.json()
                if 'registration_id' in response_data:
                    registration_id = response_data['registration_id']
                    self.registration_ids.append(registration_id)
                    self.log_test("Speech-to-Text Data Submit", True, f"Registration ID: {registration_id}")
                else:
                    self.log_test("Speech-to-Text Data Submit", False, "No registration_id in response")
            else:
                self.log_test("Speech-to-Text Data Submit", False, f"Status: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"Error response: {error_data}")
                except:
                    print(f"Raw response: {response.text}")
                    
        except Exception as e:
            self.log_test("Speech-to-Text Data Submit", False, f"Exception: {str(e)}")
    
    def test_response_format(self):
        """Test that response format matches frontend expectations"""
        print("\n🔍 Testing Response Format...")
        
        registration_data = self.create_sample_registration_data("_format_test")
        
        try:
            response = requests.post(
                f"{self.api_url}/admin-register",
                json=registration_data,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            if response.status_code == 200:
                response_data = response.json()
                
                # Check required response fields
                required_fields = ['registration_id', 'message']
                all_fields_present = True
                
                for field in required_fields:
                    if field not in response_data:
                        all_fields_present = False
                        print(f"Missing field in response: {field}")
                
                self.log_test("Response Format Check", all_fields_present, f"Fields: {list(response_data.keys())}")
                
                if 'registration_id' in response_data:
                    self.registration_ids.append(response_data['registration_id'])
                
            else:
                self.log_test("Response Format Check", False, f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_test("Response Format Check", False, f"Exception: {str(e)}")
    
    def test_duplicate_prevention(self):
        """Test duplicate prevention functionality"""
        print("\n🔍 Testing Duplicate Prevention...")
        
        # Create identical registration data
        duplicate_data = self.create_sample_registration_data("_duplicate")
        
        try:
            # Submit first registration
            response1 = requests.post(
                f"{self.api_url}/admin-register",
                json=duplicate_data,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            if response1.status_code == 200:
                response1_data = response1.json()
                if 'registration_id' in response1_data:
                    self.registration_ids.append(response1_data['registration_id'])
                
                # Submit identical registration (should be prevented)
                response2 = requests.post(
                    f"{self.api_url}/admin-register",
                    json=duplicate_data,
                    headers={'Content-Type': 'application/json'},
                    timeout=30
                )
                
                # Should return error for duplicate
                success = response2.status_code == 400
                self.log_test("Duplicate Prevention", success, f"Status: {response2.status_code}")
                
                if not success:
                    try:
                        response2_data = response2.json()
                        print(f"Unexpected duplicate response: {response2_data}")
                    except:
                        print(f"Raw duplicate response: {response2.text}")
            else:
                self.log_test("Duplicate Prevention", False, f"First registration failed: {response1.status_code}")
                
        except Exception as e:
            self.log_test("Duplicate Prevention", False, f"Exception: {str(e)}")
    
    def verify_registration_retrieval(self):
        """Verify that submitted registrations can be retrieved"""
        print("\n🔍 Verifying Registration Retrieval...")
        
        if not self.registration_ids:
            self.log_test("Registration Retrieval", False, "No registration IDs to verify")
            return
        
        for reg_id in self.registration_ids[:3]:  # Test first 3 registrations
            try:
                response = requests.get(
                    f"{self.api_url}/admin-registration/{reg_id}",
                    headers={'Content-Type': 'application/json'},
                    timeout=30
                )
                
                success = response.status_code == 200
                if success:
                    response_data = response.json()
                    # Check if the registration data is complete
                    has_required_fields = 'firstName' in response_data and 'lastName' in response_data
                    self.log_test(f"Retrieve Registration {reg_id[:8]}", has_required_fields, 
                                f"Status: {response.status_code}")
                else:
                    self.log_test(f"Retrieve Registration {reg_id[:8]}", False, 
                                f"Status: {response.status_code}")
                    
            except Exception as e:
                self.log_test(f"Retrieve Registration {reg_id[:8]}", False, f"Exception: {str(e)}")
    
    def run_all_tests(self):
        """Run all admin registration submit tests"""
        print("=" * 60)
        print("🧪 ADMIN REGISTRATION SUBMIT FUNCTIONALITY TESTS")
        print("=" * 60)
        print(f"Testing against: {self.api_url}")
        
        # Test backend connectivity first
        if not self.test_health_check():
            print("\n❌ Backend is not accessible. Cannot proceed with tests.")
            return
        
        # Run all tests
        self.test_admin_registration_submit()
        self.test_required_fields_validation()
        self.test_speech_to_text_data_structure()
        self.test_response_format()
        self.test_duplicate_prevention()
        self.verify_registration_retrieval()
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Tests Failed: {self.tests_run - self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        if self.registration_ids:
            print(f"\n📝 Created {len(self.registration_ids)} test registrations:")
            for reg_id in self.registration_ids:
                print(f"  - {reg_id}")
        
        # Overall assessment
        if self.tests_passed == self.tests_run:
            print("\n✅ ALL TESTS PASSED - Admin registration submit functionality is working correctly!")
        elif self.tests_passed >= self.tests_run * 0.8:
            print("\n⚠️  MOSTLY WORKING - Minor issues found but core functionality works")
        else:
            print("\n❌ SIGNIFICANT ISSUES - Admin registration submit functionality has problems")

if __name__ == "__main__":
    tester = AdminRegistrationSubmitTester()
    tester.run_all_tests()