#!/usr/bin/env python3
"""
Comprehensive Admin Registration Submit Test
Focus: Testing edge cases and speech-to-text scenarios that might cause submit button issues
"""

import requests
import json
from datetime import datetime, date
import uuid
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

class ComprehensiveAdminRegistrationTester:
    def __init__(self):
        self.base_url = os.getenv('REACT_APP_BACKEND_URL', 'https://cd556dd9-d36b-422e-8110-4b1830397661.preview.emergentagent.com')
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
    
    def test_speech_to_text_edge_cases(self):
        """Test various edge cases that might occur with speech-to-text input"""
        print("\n🔍 Testing Speech-to-Text Edge Cases...")
        
        # Test Case 1: Mixed case and extra spaces (common with speech recognition)
        speech_case_1 = {
            "firstName": "  MARY  ",  # Extra spaces and caps
            "lastName": "  johnson  ",  # Mixed case
            "dob": "1992-08-25",
            "patientConsent": "VERBAL",  # Caps
            "gender": "female",  # Lowercase
            "province": "ontario",  # Lowercase
            "disposition": "Active",
            "aka": "",
            "age": "31",
            "regDate": date.today().isoformat(),
            "healthCard": "5555666677AA",
            "healthCardVersion": "AA",
            "referralSite": "community health center",  # Lowercase
            "address": "789 elm street",  # Lowercase
            "unitNumber": "unit 5",
            "city": "TORONTO",  # Caps
            "postalCode": "m6h 3s4",  # Lowercase with space
            "phone1": "416 555 1234",  # With spaces
            "phone2": "",
            "ext1": "",
            "ext2": "",
            "leaveMessage": True,
            "voicemail": False,
            "text": True,
            "preferredTime": "evening",  # Lowercase
            "email": "MARY.JOHNSON@GMAIL.COM",  # Caps
            "language": "english",  # Lowercase
            "specialAttention": "needs interpreter",
            "photo": None,
            "summaryTemplate": "Standard template",
            "physician": "dr. david fletcher",  # Lowercase
            "rnaAvailable": "no",  # Lowercase
            "rnaSampleDate": None,
            "rnaResult": "positive",  # Lowercase
            "coverageType": "odsp",  # Lowercase
            "referralPerson": "social worker",
            "testType": "tests",  # Lowercase
            "hivDate": None,
            "hivResult": None,
            "hivType": None,
            "hivTester": "cm"  # Lowercase
        }
        
        try:
            response = requests.post(
                f"{self.api_url}/admin-register",
                json=speech_case_1,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            success = response.status_code == 200
            if success:
                response_data = response.json()
                if 'registration_id' in response_data:
                    self.registration_ids.append(response_data['registration_id'])
                    self.log_test("Speech Case 1 (Mixed Case/Spaces)", True, f"ID: {response_data['registration_id'][:8]}")
                else:
                    self.log_test("Speech Case 1 (Mixed Case/Spaces)", False, "No registration_id")
            else:
                self.log_test("Speech Case 1 (Mixed Case/Spaces)", False, f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_test("Speech Case 1 (Mixed Case/Spaces)", False, f"Exception: {str(e)}")
    
    def test_boolean_string_conversion(self):
        """Test boolean fields as strings (common issue with speech-to-text)"""
        print("\n🔍 Testing Boolean String Conversion...")
        
        boolean_string_data = {
            "firstName": "Robert",
            "lastName": "Wilson",
            "dob": "1988-12-10",
            "patientConsent": "written",
            "gender": "Male",
            "province": "Ontario",
            "disposition": "Active",
            "aka": "",
            "age": "35",
            "regDate": date.today().isoformat(),
            "healthCard": "9999888877BB",
            "healthCardVersion": "BB",
            "referralSite": "Hospital",
            "address": "321 Pine Road",
            "unitNumber": "",
            "city": "Ottawa",
            "postalCode": "K1A 0A6",
            "phone1": "6135551234",
            "phone2": "",
            "ext1": "",
            "ext2": "",
            "leaveMessage": "true",    # String instead of boolean
            "voicemail": "false",      # String instead of boolean
            "text": "yes",             # Different string representation
            "preferredTime": "Morning",
            "email": "robert.wilson@example.com",
            "language": "English",
            "specialAttention": "",
            "photo": None,
            "summaryTemplate": "Standard template",
            "physician": "Dr. David Fletcher",
            "rnaAvailable": "No",
            "rnaSampleDate": None,
            "rnaResult": "Positive",
            "coverageType": "OW",
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
                json=boolean_string_data,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            success = response.status_code == 200
            if success:
                response_data = response.json()
                if 'registration_id' in response_data:
                    self.registration_ids.append(response_data['registration_id'])
                    self.log_test("Boolean String Conversion", True, f"ID: {response_data['registration_id'][:8]}")
                else:
                    self.log_test("Boolean String Conversion", False, "No registration_id")
            else:
                self.log_test("Boolean String Conversion", False, f"Status: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"Error details: {error_data}")
                except:
                    print(f"Raw error: {response.text}")
                    
        except Exception as e:
            self.log_test("Boolean String Conversion", False, f"Exception: {str(e)}")
    
    def test_empty_and_null_fields(self):
        """Test handling of empty strings and null values"""
        print("\n🔍 Testing Empty and Null Fields...")
        
        empty_fields_data = {
            "firstName": "Sarah",
            "lastName": "Davis",
            "dob": "1995-06-30",
            "patientConsent": "verbal",
            "gender": "Female",
            "province": "Ontario",
            "disposition": "Active",
            "aka": "",           # Empty string
            "age": "28",
            "regDate": date.today().isoformat(),
            "healthCard": "",    # Empty health card
            "healthCardVersion": "",  # Empty version
            "referralSite": "Walk-in",
            "address": "123 Main St",
            "unitNumber": None,  # Null value
            "city": "Toronto",
            "postalCode": "M5V 1A1",
            "phone1": "4165551234",
            "phone2": "",        # Empty string
            "ext1": None,        # Null value
            "ext2": "",          # Empty string
            "leaveMessage": True,
            "voicemail": False,
            "text": True,
            "preferredTime": "",  # Empty string
            "email": "sarah.davis@example.com",
            "language": "English",
            "specialAttention": None,  # Null value
            "photo": None,
            "summaryTemplate": "",     # Empty string
            "physician": "Dr. David Fletcher",
            "rnaAvailable": "No",
            "rnaSampleDate": None,
            "rnaResult": "Positive",
            "coverageType": "Select",
            "referralPerson": "",      # Empty string
            "testType": "Tests",
            "hivDate": None,
            "hivResult": None,
            "hivType": None,
            "hivTester": "CM"
        }
        
        try:
            response = requests.post(
                f"{self.api_url}/admin-register",
                json=empty_fields_data,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            success = response.status_code == 200
            if success:
                response_data = response.json()
                if 'registration_id' in response_data:
                    self.registration_ids.append(response_data['registration_id'])
                    self.log_test("Empty and Null Fields", True, f"ID: {response_data['registration_id'][:8]}")
                else:
                    self.log_test("Empty and Null Fields", False, "No registration_id")
            else:
                self.log_test("Empty and Null Fields", False, f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_test("Empty and Null Fields", False, f"Exception: {str(e)}")
    
    def test_special_characters(self):
        """Test handling of special characters that might come from speech-to-text"""
        print("\n🔍 Testing Special Characters...")
        
        special_chars_data = {
            "firstName": "José",      # Accented character
            "lastName": "O'Connor",   # Apostrophe
            "dob": "1990-03-15",
            "patientConsent": "verbal",
            "gender": "Male",
            "province": "Ontario",
            "disposition": "Active",
            "aka": "Joe",
            "age": "33",
            "regDate": date.today().isoformat(),
            "healthCard": "1234567890AB",
            "healthCardVersion": "AB",
            "referralSite": "St. Mary's Hospital",  # Apostrophe and period
            "address": "123 Queen St. E., Apt #5",  # Multiple special chars
            "unitNumber": "#5",       # Hash symbol
            "city": "Toronto",
            "postalCode": "M5H-2N2",  # Dash instead of space
            "phone1": "(416) 555-1234",  # Formatted phone
            "phone2": "416.555.5678",    # Dot formatted phone
            "ext1": "x123",           # Extension with x
            "ext2": "ext. 456",       # Extension with period
            "leaveMessage": True,
            "voicemail": False,
            "text": True,
            "preferredTime": "9:00 AM - 5:00 PM",  # Time range
            "email": "jose.oconnor+test@gmail.com",  # Plus sign in email
            "language": "English/Spanish",  # Multiple languages
            "specialAttention": "Needs wheelchair access & interpreter",  # Ampersand
            "photo": None,
            "summaryTemplate": "Patient requires special care - see notes",  # Dash
            "physician": "Dr. David Fletcher",
            "rnaAvailable": "No",
            "rnaSampleDate": None,
            "rnaResult": "Positive",
            "coverageType": "ODSP",
            "referralPerson": "Maria González",  # Accented character
            "testType": "Tests",
            "hivDate": None,
            "hivResult": None,
            "hivType": None,
            "hivTester": "CM"
        }
        
        try:
            response = requests.post(
                f"{self.api_url}/admin-register",
                json=special_chars_data,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            success = response.status_code == 200
            if success:
                response_data = response.json()
                if 'registration_id' in response_data:
                    self.registration_ids.append(response_data['registration_id'])
                    self.log_test("Special Characters", True, f"ID: {response_data['registration_id'][:8]}")
                else:
                    self.log_test("Special Characters", False, "No registration_id")
            else:
                self.log_test("Special Characters", False, f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_test("Special Characters", False, f"Exception: {str(e)}")
    
    def test_large_payload(self):
        """Test with large text fields (speech-to-text might generate long text)"""
        print("\n🔍 Testing Large Payload...")
        
        large_text = "This is a very long text that might be generated by speech-to-text recognition software when a user speaks for an extended period of time. " * 10
        
        large_payload_data = {
            "firstName": "Alexander",
            "lastName": "Thompson",
            "dob": "1987-09-22",
            "patientConsent": "verbal",
            "gender": "Male",
            "province": "Ontario",
            "disposition": "Active",
            "aka": "Alex",
            "age": "36",
            "regDate": date.today().isoformat(),
            "healthCard": "7777888899CC",
            "healthCardVersion": "CC",
            "referralSite": "Community Health Center",
            "address": "456 Long Street Name That Goes On And On",
            "unitNumber": "Apartment 123B",
            "city": "Toronto",
            "postalCode": "M4B 2C3",
            "phone1": "4165551234",
            "phone2": "",
            "ext1": "",
            "ext2": "",
            "leaveMessage": True,
            "voicemail": False,
            "text": True,
            "preferredTime": "Morning",
            "email": "alexander.thompson@example.com",
            "language": "English",
            "specialAttention": large_text,  # Very long text
            "photo": None,
            "summaryTemplate": large_text,   # Very long text
            "physician": "Dr. David Fletcher",
            "rnaAvailable": "No",
            "rnaSampleDate": None,
            "rnaResult": "Positive",
            "coverageType": "None",
            "referralPerson": "Community outreach worker with a very long title and description",
            "testType": "Tests",
            "hivDate": None,
            "hivResult": None,
            "hivType": None,
            "hivTester": "CM"
        }
        
        try:
            response = requests.post(
                f"{self.api_url}/admin-register",
                json=large_payload_data,
                headers={'Content-Type': 'application/json'},
                timeout=60  # Longer timeout for large payload
            )
            
            success = response.status_code == 200
            if success:
                response_data = response.json()
                if 'registration_id' in response_data:
                    self.registration_ids.append(response_data['registration_id'])
                    self.log_test("Large Payload", True, f"ID: {response_data['registration_id'][:8]}")
                else:
                    self.log_test("Large Payload", False, "No registration_id")
            else:
                self.log_test("Large Payload", False, f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_test("Large Payload", False, f"Exception: {str(e)}")
    
    def test_response_consistency(self):
        """Test that responses are consistent across multiple submissions"""
        print("\n🔍 Testing Response Consistency...")
        
        base_data = {
            "firstName": "TestUser",
            "lastName": "Consistency",
            "dob": "1990-01-01",
            "patientConsent": "verbal",
            "gender": "Other",
            "province": "Ontario",
            "disposition": "Active",
            "aka": "",
            "age": "34",
            "regDate": date.today().isoformat(),
            "healthCard": "1111222233DD",
            "healthCardVersion": "DD",
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
            "email": "test.consistency@example.com",
            "language": "English",
            "specialAttention": "",
            "photo": None,
            "summaryTemplate": "Test template",
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
        
        responses = []
        for i in range(3):
            test_data = base_data.copy()
            test_data["firstName"] = f"TestUser{i+1}"
            test_data["email"] = f"test.consistency{i+1}@example.com"
            
            try:
                response = requests.post(
                    f"{self.api_url}/admin-register",
                    json=test_data,
                    headers={'Content-Type': 'application/json'},
                    timeout=30
                )
                
                if response.status_code == 200:
                    response_data = response.json()
                    responses.append(response_data)
                    if 'registration_id' in response_data:
                        self.registration_ids.append(response_data['registration_id'])
                        
            except Exception as e:
                self.log_test(f"Response Consistency {i+1}", False, f"Exception: {str(e)}")
                return
        
        # Check consistency
        if len(responses) == 3:
            # Check that all responses have the same structure
            keys_consistent = all(set(resp.keys()) == set(responses[0].keys()) for resp in responses)
            # Check that all have registration_id
            all_have_id = all('registration_id' in resp for resp in responses)
            # Check that all IDs are different (unique)
            ids = [resp.get('registration_id') for resp in responses]
            ids_unique = len(set(ids)) == len(ids)
            
            overall_success = keys_consistent and all_have_id and ids_unique
            details = f"Keys consistent: {keys_consistent}, All have ID: {all_have_id}, IDs unique: {ids_unique}"
            self.log_test("Response Consistency", overall_success, details)
        else:
            self.log_test("Response Consistency", False, f"Only {len(responses)}/3 requests succeeded")
    
    def run_comprehensive_tests(self):
        """Run all comprehensive tests"""
        print("=" * 70)
        print("🧪 COMPREHENSIVE ADMIN REGISTRATION SUBMIT TESTS")
        print("=" * 70)
        print(f"Testing against: {self.api_url}")
        
        # Run all edge case tests
        self.test_speech_to_text_edge_cases()
        self.test_boolean_string_conversion()
        self.test_empty_and_null_fields()
        self.test_special_characters()
        self.test_large_payload()
        self.test_response_consistency()
        
        # Print summary
        print("\n" + "=" * 70)
        print("📊 COMPREHENSIVE TEST SUMMARY")
        print("=" * 70)
        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Tests Failed: {self.tests_run - self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        if self.registration_ids:
            print(f"\n📝 Created {len(self.registration_ids)} test registrations")
        
        # Detailed assessment
        if self.tests_passed == self.tests_run:
            print("\n✅ ALL COMPREHENSIVE TESTS PASSED")
            print("The admin registration submit functionality handles all edge cases correctly!")
        elif self.tests_passed >= self.tests_run * 0.9:
            print("\n⚠️  EXCELLENT PERFORMANCE")
            print("Minor issues found but the system handles edge cases very well")
        elif self.tests_passed >= self.tests_run * 0.7:
            print("\n⚠️  GOOD PERFORMANCE")
            print("Some edge cases need attention but core functionality is solid")
        else:
            print("\n❌ SIGNIFICANT ISSUES FOUND")
            print("Multiple edge cases are failing - needs investigation")

if __name__ == "__main__":
    tester = ComprehensiveAdminRegistrationTester()
    tester.run_comprehensive_tests()