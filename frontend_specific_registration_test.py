#!/usr/bin/env python3
"""
Frontend-Specific Admin Registration Test
Focus: Testing the exact data structure and scenarios that the frontend sends
"""

import requests
import json
from datetime import datetime, date
import uuid
import os
import base64
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

class FrontendSpecificTester:
    def __init__(self):
        self.base_url = os.getenv('REACT_APP_BACKEND_URL', 'https://46471c8a-a981-4b23-bca9-bb5c0ba282bc.preview.emergentagent.com')
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
    
    def create_sample_photo_data(self):
        """Create a small base64 encoded image for testing"""
        # Create a minimal 1x1 pixel PNG image in base64
        # This is a valid PNG image data
        return "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
    
    def test_frontend_exact_structure(self):
        """Test with the exact structure that frontend sends"""
        print("\n🔍 Testing Frontend Exact Structure...")
        
        frontend_data = {
            "firstName": "Emma",
            "lastName": "Watson",
            "dob": "1990-04-15",
            "patientConsent": "verbal",
            "gender": "Female",
            "province": "Ontario",
            "disposition": "Active",
            "aka": "",
            "age": "33",
            "regDate": date.today().isoformat(),
            "healthCard": "4444555566EE",
            "healthCardVersion": "EE",
            "referralSite": "Community Center",
            "address": "789 Broadway Ave",
            "unitNumber": "Suite 200",
            "city": "Toronto",
            "postalCode": "M4K 1N1",
            "phone1": "4165554444",
            "phone2": "4165555555",
            "ext1": "123",
            "ext2": "456",
            "leaveMessage": True,
            "voicemail": True,
            "text": False,
            "preferredTime": "Afternoon",
            "email": "emma.watson@example.com",
            "language": "English",
            "specialAttention": "Patient prefers female healthcare providers",
            "photo": self.create_sample_photo_data(),  # Include photo data
            "summaryTemplate": "Patient requires standard HCV screening and follow-up care",
            "physician": "Dr. David Fletcher",
            "rnaAvailable": "Yes",
            "rnaSampleDate": "2024-01-15",
            "rnaResult": "Negative",
            "coverageType": "ODSP",
            "referralPerson": "Jane Smith, Social Worker",
            "testType": "HCV",
            "hivDate": "2024-01-10",
            "hivResult": "negative",
            "hivType": "Type 1",
            "hivTester": "JY"
        }
        
        try:
            response = requests.post(
                f"{self.api_url}/admin-register",
                json=frontend_data,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            success = response.status_code == 200
            if success:
                response_data = response.json()
                if 'registration_id' in response_data:
                    registration_id = response_data['registration_id']
                    self.registration_ids.append(registration_id)
                    self.log_test("Frontend Exact Structure", True, f"ID: {registration_id[:8]}")
                    
                    # Verify response structure matches frontend expectations
                    expected_fields = ['registration_id', 'message', 'status']
                    has_all_fields = all(field in response_data for field in expected_fields)
                    self.log_test("Frontend Response Structure", has_all_fields, 
                                f"Fields: {list(response_data.keys())}")
                    
                    return True, response_data
                else:
                    self.log_test("Frontend Exact Structure", False, "No registration_id in response")
                    return False, response_data
            else:
                self.log_test("Frontend Exact Structure", False, f"Status: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"Error response: {error_data}")
                except:
                    print(f"Raw response: {response.text}")
                return False, {}
                
        except Exception as e:
            self.log_test("Frontend Exact Structure", False, f"Exception: {str(e)}")
            return False, {}
    
    def test_speech_to_text_workflow(self):
        """Test the complete speech-to-text workflow scenario"""
        print("\n🔍 Testing Speech-to-Text Workflow...")
        
        # Simulate data that might come from speech-to-text after user speaks
        speech_workflow_data = {
            "firstName": "Michael",
            "lastName": "Johnson",
            "dob": "1985-07-22",
            "patientConsent": "written",  # User said "written consent"
            "gender": "Male",
            "province": "Ontario",
            "disposition": "Active",
            "aka": "Mike",  # User said "also known as Mike"
            "age": "38",
            "regDate": date.today().isoformat(),
            "healthCard": "6666777788FF",
            "healthCardVersion": "FF",
            "referralSite": "Downtown Clinic",  # User said "downtown clinic"
            "address": "One hundred twenty three Main Street",  # Speech might convert numbers to words
            "unitNumber": "Apartment two B",  # Speech conversion
            "city": "Toronto",
            "postalCode": "M five V three A eight",  # Speech might separate postal code
            "phone1": "four one six five five five one two three four",  # Speech format
            "phone2": "",
            "ext1": "",
            "ext2": "",
            "leaveMessage": True,
            "voicemail": False,
            "text": True,
            "preferredTime": "Morning between nine and eleven",  # Natural speech
            "email": "michael dot johnson at gmail dot com",  # Speech format
            "language": "English",
            "specialAttention": "Patient has difficulty hearing please speak loudly",  # Natural speech
            "photo": None,
            "summaryTemplate": "Patient needs hepatitis C testing and counseling",
            "physician": "Doctor David Fletcher",  # Speech might add "Doctor"
            "rnaAvailable": "No",
            "rnaSampleDate": None,
            "rnaResult": "Positive",
            "coverageType": "Ontario Works",  # Full name instead of abbreviation
            "referralPerson": "Community health worker",
            "testType": "Tests",
            "hivDate": None,
            "hivResult": None,
            "hivType": None,
            "hivTester": "CM"
        }
        
        try:
            response = requests.post(
                f"{self.api_url}/admin-register",
                json=speech_workflow_data,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            success = response.status_code == 200
            if success:
                response_data = response.json()
                if 'registration_id' in response_data:
                    registration_id = response_data['registration_id']
                    self.registration_ids.append(registration_id)
                    self.log_test("Speech-to-Text Workflow", True, f"ID: {registration_id[:8]}")
                else:
                    self.log_test("Speech-to-Text Workflow", False, "No registration_id in response")
            else:
                self.log_test("Speech-to-Text Workflow", False, f"Status: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"Speech workflow error: {error_data}")
                except:
                    print(f"Raw speech workflow response: {response.text}")
                
        except Exception as e:
            self.log_test("Speech-to-Text Workflow", False, f"Exception: {str(e)}")
    
    def test_form_state_after_speech(self):
        """Test form submission after speech-to-text has populated fields"""
        print("\n🔍 Testing Form State After Speech...")
        
        # This simulates the state where speech-to-text has populated some fields
        # and user manually filled others
        mixed_input_data = {
            "firstName": "Lisa",  # Manually typed
            "lastName": "Anderson",  # Manually typed
            "dob": "1992-11-08",  # Date picker
            "patientConsent": "verbal",  # Dropdown selection
            "gender": "Female",  # Dropdown selection
            "province": "Ontario",  # Default value
            "disposition": "Active",  # Dropdown selection
            "aka": "Liz",  # Speech-to-text
            "age": "31",  # Calculated or speech
            "regDate": date.today().isoformat(),  # Auto-generated
            "healthCard": "8888999900GG",  # Manually typed
            "healthCardVersion": "GG",  # Manually typed
            "referralSite": "Family doctor referred me here",  # Speech-to-text (long form)
            "address": "Four fifty six Oak Street",  # Speech-to-text
            "unitNumber": "Unit three",  # Speech-to-text
            "city": "Toronto",  # Dropdown or manual
            "postalCode": "M6K 2L5",  # Manually typed
            "phone1": "4165556789",  # Manually typed
            "phone2": "",  # Empty
            "ext1": "",  # Empty
            "ext2": "",  # Empty
            "leaveMessage": True,  # Checkbox
            "voicemail": False,  # Checkbox
            "text": True,  # Checkbox
            "preferredTime": "I prefer morning appointments",  # Speech-to-text (long form)
            "email": "lisa.anderson@hotmail.com",  # Manually typed
            "language": "English",  # Dropdown
            "specialAttention": "I am allergic to latex gloves please use non latex alternatives",  # Speech-to-text
            "photo": None,  # No photo
            "summaryTemplate": "Patient requires comprehensive testing and follow up care",  # Speech-to-text
            "physician": "Dr. David Fletcher",  # Default
            "rnaAvailable": "No",  # Dropdown
            "rnaSampleDate": None,  # Empty
            "rnaResult": "Positive",  # Default
            "coverageType": "None",  # Dropdown selection
            "referralPerson": "My family doctor Doctor Smith",  # Speech-to-text
            "testType": "Tests",  # Default
            "hivDate": None,
            "hivResult": None,
            "hivType": None,
            "hivTester": "CM"  # Default
        }
        
        try:
            response = requests.post(
                f"{self.api_url}/admin-register",
                json=mixed_input_data,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            success = response.status_code == 200
            if success:
                response_data = response.json()
                if 'registration_id' in response_data:
                    registration_id = response_data['registration_id']
                    self.registration_ids.append(registration_id)
                    self.log_test("Form State After Speech", True, f"ID: {registration_id[:8]}")
                else:
                    self.log_test("Form State After Speech", False, "No registration_id in response")
            else:
                self.log_test("Form State After Speech", False, f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_test("Form State After Speech", False, f"Exception: {str(e)}")
    
    def test_submit_button_scenarios(self):
        """Test specific scenarios that might cause submit button issues"""
        print("\n🔍 Testing Submit Button Scenarios...")
        
        # Scenario 1: Minimal required data (what happens if user clicks submit early)
        minimal_data = {
            "firstName": "Test",
            "lastName": "User",
            "patientConsent": "verbal"  # Only required fields
        }
        
        try:
            response = requests.post(
                f"{self.api_url}/admin-register",
                json=minimal_data,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            # This should either succeed with defaults or fail with validation
            if response.status_code == 200:
                response_data = response.json()
                if 'registration_id' in response_data:
                    self.registration_ids.append(response_data['registration_id'])
                    self.log_test("Minimal Data Submit", True, "Accepted with defaults")
                else:
                    self.log_test("Minimal Data Submit", False, "No registration_id")
            elif response.status_code == 422:
                self.log_test("Minimal Data Submit", True, "Properly rejected with validation")
            else:
                self.log_test("Minimal Data Submit", False, f"Unexpected status: {response.status_code}")
                
        except Exception as e:
            self.log_test("Minimal Data Submit", False, f"Exception: {str(e)}")
        
        # Scenario 2: Complete data (normal successful submission)
        complete_data = {
            "firstName": "Complete",
            "lastName": "Test",
            "dob": "1990-01-01",
            "patientConsent": "verbal",
            "gender": "Other",
            "province": "Ontario",
            "disposition": "Active",
            "aka": "",
            "age": "34",
            "regDate": date.today().isoformat(),
            "healthCard": "1111222233HH",
            "healthCardVersion": "HH",
            "referralSite": "Test Site",
            "address": "Test Address",
            "unitNumber": "",
            "city": "Toronto",
            "postalCode": "M1M 1M1",
            "phone1": "4165551111",
            "phone2": "",
            "ext1": "",
            "ext2": "",
            "leaveMessage": True,
            "voicemail": False,
            "text": True,
            "preferredTime": "Anytime",
            "email": "complete.test@example.com",
            "language": "English",
            "specialAttention": "",
            "photo": None,
            "summaryTemplate": "",
            "physician": "Dr. David Fletcher",
            "rnaAvailable": "No",
            "rnaSampleDate": None,
            "rnaResult": "Positive",
            "coverageType": "Select",
            "referralPerson": "",
            "testType": "Tests",
            "hivDate": None,
            "hivResult": None,
            "hivType": None,
            "hivTester": "CM"
        }
        
        try:
            response = requests.post(
                f"{self.api_url}/admin-register",
                json=complete_data,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            success = response.status_code == 200
            if success:
                response_data = response.json()
                if 'registration_id' in response_data:
                    registration_id = response_data['registration_id']
                    self.registration_ids.append(registration_id)
                    self.log_test("Complete Data Submit", True, f"ID: {registration_id[:8]}")
                else:
                    self.log_test("Complete Data Submit", False, "No registration_id")
            else:
                self.log_test("Complete Data Submit", False, f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_test("Complete Data Submit", False, f"Exception: {str(e)}")
    
    def verify_data_persistence(self):
        """Verify that submitted data is properly stored and retrievable"""
        print("\n🔍 Verifying Data Persistence...")
        
        if not self.registration_ids:
            self.log_test("Data Persistence", False, "No registration IDs to verify")
            return
        
        # Test the first registration
        reg_id = self.registration_ids[0]
        
        try:
            response = requests.get(
                f"{self.api_url}/admin-registration/{reg_id}",
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            if response.status_code == 200:
                response_data = response.json()
                
                # Check that key fields are preserved
                required_fields = ['firstName', 'lastName', 'patientConsent']
                has_required = all(field in response_data for field in required_fields)
                
                # Check that the ID matches
                id_matches = response_data.get('id') == reg_id
                
                success = has_required and id_matches
                self.log_test("Data Persistence", success, 
                            f"Required fields: {has_required}, ID matches: {id_matches}")
                
                if success:
                    # Check specific data integrity
                    if 'photo' in response_data and response_data['photo']:
                        self.log_test("Photo Data Persistence", True, "Photo data preserved")
                    
            else:
                self.log_test("Data Persistence", False, f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_test("Data Persistence", False, f"Exception: {str(e)}")
    
    def run_frontend_tests(self):
        """Run all frontend-specific tests"""
        print("=" * 70)
        print("🧪 FRONTEND-SPECIFIC ADMIN REGISTRATION TESTS")
        print("=" * 70)
        print(f"Testing against: {self.api_url}")
        
        # Run all frontend-specific tests
        self.test_frontend_exact_structure()
        self.test_speech_to_text_workflow()
        self.test_form_state_after_speech()
        self.test_submit_button_scenarios()
        self.verify_data_persistence()
        
        # Print summary
        print("\n" + "=" * 70)
        print("📊 FRONTEND-SPECIFIC TEST SUMMARY")
        print("=" * 70)
        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Tests Failed: {self.tests_run - self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        if self.registration_ids:
            print(f"\n📝 Created {len(self.registration_ids)} test registrations")
        
        # Assessment
        if self.tests_passed == self.tests_run:
            print("\n✅ ALL FRONTEND TESTS PASSED")
            print("The admin registration submit functionality works perfectly with frontend!")
            print("The submit button issue is likely NOT in the backend API.")
        elif self.tests_passed >= self.tests_run * 0.8:
            print("\n⚠️  MOSTLY WORKING")
            print("Minor issues found but backend API is solid")
        else:
            print("\n❌ BACKEND ISSUES FOUND")
            print("The submit button problems may be related to backend API issues")

if __name__ == "__main__":
    tester = FrontendSpecificTester()
    tester.run_frontend_tests()