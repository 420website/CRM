#!/usr/bin/env python3
"""
Backend Verification Test for Labels Button PDF/Print Removal
=============================================================

This test verifies that all backend functionality remains intact after 
the frontend changes to remove PDF/print functionality from labels button.

Focus Areas:
1. All existing API endpoints working correctly
2. Database operations (registration CRUD, template operations) functional
3. Core backend services running properly
4. No backend errors after frontend changes

The labels functionality change only removed frontend PDF generation and 
print functionality, keeping only clipboard copy functionality. 
No backend changes were made.
"""

import requests
import json
import sys
import os
from datetime import datetime, date
import random
import string
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

class LabelsBackendVerificationTest:
    def __init__(self):
        # Get backend URL from frontend environment
        self.base_url = os.getenv('REACT_APP_BACKEND_URL', 'http://localhost:8001')
        if not self.base_url.endswith('/api'):
            self.base_url = f"{self.base_url}/api"
        
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []
        self.created_registration_id = None
        
        print(f"🔧 Backend URL: {self.base_url}")
        print("=" * 80)
        print("BACKEND VERIFICATION TEST - Labels Button PDF/Print Removal")
        print("=" * 80)

    def log_result(self, test_name, success, details=""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            status = "✅ PASS"
        else:
            status = "❌ FAIL"
        
        result = f"{status} - {test_name}"
        if details:
            result += f" | {details}"
        
        self.test_results.append(result)
        print(result)

    def make_request(self, method, endpoint, data=None, expected_status=200):
        """Make HTTP request and return response"""
        url = f"{self.base_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=30)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=30)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=30)
            
            success = response.status_code == expected_status
            return success, response
            
        except Exception as e:
            print(f"❌ Request failed: {str(e)}")
            return False, None

    def generate_test_registration_data(self):
        """Generate realistic test data for admin registration"""
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
        today = date.today()
        
        return {
            "firstName": f"Sarah",
            "lastName": f"Johnson{random_suffix}",
            "dob": "1985-03-15",
            "patientConsent": "Verbal",
            "gender": "Female",
            "province": "Ontario",
            "disposition": "Active Treatment",
            "aka": f"Sarah J",
            "age": "38",
            "regDate": today.isoformat(),
            "healthCard": f"123456789{random.randint(0,9)}AB",
            "healthCardVersion": "AB",
            "referralSite": "Downtown Health Clinic",
            "address": f"{random.randint(100, 999)} Queen Street West",
            "unitNumber": f"Apt {random.randint(1, 50)}",
            "city": "Toronto",
            "postalCode": "M5V 3A8",
            "phone1": "4165551234",
            "phone2": "4165555678",
            "ext1": "101",
            "ext2": "202",
            "leaveMessage": True,
            "voicemail": True,
            "text": True,
            "preferredTime": "Morning",
            "email": f"sarah.johnson{random_suffix}@email.com",
            "language": "English",
            "specialAttention": "Patient prefers morning appointments",
            "physician": "Dr. David Fletcher",
            "rnaAvailable": "No",
            "rnaSampleDate": None,
            "rnaResult": "Positive",
            "coverageType": "OHIP",
            "referralPerson": "Dr. Smith",
            "testType": "HCV Testing",
            "hivDate": today.isoformat(),
            "hivResult": "Negative",
            "hivType": "Type 1",
            "hivTester": "CM"
        }

    def test_1_core_api_endpoints(self):
        """Test 1: Verify core API endpoints are responding"""
        print("\n📋 TEST 1: Core API Endpoints")
        print("-" * 40)
        
        # Test basic API health
        success, response = self.make_request('GET', '', expected_status=200)
        if success:
            self.log_result("API Root Endpoint", True, "Backend is responding")
        else:
            self.log_result("API Root Endpoint", False, "Backend not responding")
            return False
        
        # Test admin registrations endpoints
        endpoints_to_test = [
            ('admin-registrations-pending', 'GET', 'Pending registrations endpoint'),
            ('admin-registrations-submitted', 'GET', 'Submitted registrations endpoint'),
            ('notes-templates', 'GET', 'Notes templates endpoint'),
            ('clinical-templates', 'GET', 'Clinical templates endpoint')
        ]
        
        all_passed = True
        for endpoint, method, description in endpoints_to_test:
            success, response = self.make_request(method, endpoint)
            if success and response:
                try:
                    data = response.json()
                    count = len(data) if isinstance(data, list) else 1
                    self.log_result(description, True, f"Returned {count} records")
                except:
                    self.log_result(description, True, "Valid response received")
            else:
                self.log_result(description, False, f"Status: {response.status_code if response else 'No response'}")
                all_passed = False
        
        return all_passed

    def test_2_registration_crud_operations(self):
        """Test 2: Registration CRUD Operations"""
        print("\n📝 TEST 2: Registration CRUD Operations")
        print("-" * 40)
        
        # CREATE - Test registration creation
        test_data = self.generate_test_registration_data()
        success, response = self.make_request('POST', 'admin-registrations', test_data, expected_status=201)
        
        if success and response:
            try:
                created_reg = response.json()
                self.created_registration_id = created_reg.get('id')
                self.log_result("CREATE Registration", True, f"ID: {self.created_registration_id}")
            except:
                self.log_result("CREATE Registration", False, "Invalid response format")
                return False
        else:
            self.log_result("CREATE Registration", False, f"Status: {response.status_code if response else 'No response'}")
            return False
        
        # READ - Test registration retrieval
        if self.created_registration_id:
            success, response = self.make_request('GET', f'admin-registrations/{self.created_registration_id}')
            if success and response:
                try:
                    reg_data = response.json()
                    if reg_data.get('firstName') == test_data['firstName']:
                        self.log_result("READ Registration", True, f"Retrieved: {reg_data.get('firstName')} {reg_data.get('lastName')}")
                    else:
                        self.log_result("READ Registration", False, "Data mismatch")
                except:
                    self.log_result("READ Registration", False, "Invalid response format")
            else:
                self.log_result("READ Registration", False, f"Status: {response.status_code if response else 'No response'}")
        
        # UPDATE - Test registration update
        if self.created_registration_id:
            update_data = {"specialAttention": "Updated via backend test - Labels functionality verification"}
            success, response = self.make_request('PUT', f'admin-registrations/{self.created_registration_id}', update_data)
            if success:
                self.log_result("UPDATE Registration", True, "Special attention field updated")
            else:
                self.log_result("UPDATE Registration", False, f"Status: {response.status_code if response else 'No response'}")
        
        return True

    def test_3_template_operations(self):
        """Test 3: Template Operations (Notes & Clinical)"""
        print("\n📄 TEST 3: Template Operations")
        print("-" * 40)
        
        # Test Notes Templates
        success, response = self.make_request('GET', 'notes-templates')
        if success and response:
            try:
                templates = response.json()
                template_count = len(templates)
                self.log_result("Notes Templates Retrieval", True, f"Found {template_count} templates")
                
                # Check for default templates
                template_names = [t.get('name', '') for t in templates]
                default_templates = ['Consultation', 'Lab', 'Prescription']
                found_defaults = [name for name in default_templates if name in template_names]
                self.log_result("Notes Default Templates", len(found_defaults) >= 2, f"Found: {', '.join(found_defaults)}")
                
            except:
                self.log_result("Notes Templates Retrieval", False, "Invalid response format")
        else:
            self.log_result("Notes Templates Retrieval", False, f"Status: {response.status_code if response else 'No response'}")
        
        # Test Clinical Templates
        success, response = self.make_request('GET', 'clinical-templates')
        if success and response:
            try:
                templates = response.json()
                template_count = len(templates)
                self.log_result("Clinical Templates Retrieval", True, f"Found {template_count} templates")
                
                # Check for default templates
                template_names = [t.get('name', '') for t in templates]
                expected_clinical = ['Positive', 'Negative']
                found_clinical = [name for name in expected_clinical if any(name in tn for tn in template_names)]
                self.log_result("Clinical Default Templates", len(found_clinical) >= 1, f"Found templates with: {', '.join(found_clinical)}")
                
            except:
                self.log_result("Clinical Templates Retrieval", False, "Invalid response format")
        else:
            self.log_result("Clinical Templates Retrieval", False, f"Status: {response.status_code if response else 'No response'}")
        
        return True

    def test_4_database_persistence(self):
        """Test 4: Database Persistence and Data Integrity"""
        print("\n💾 TEST 4: Database Persistence")
        print("-" * 40)
        
        # Test that our created registration persists
        if self.created_registration_id:
            success, response = self.make_request('GET', f'admin-registrations/{self.created_registration_id}')
            if success and response:
                try:
                    reg_data = response.json()
                    # Check if our update persisted
                    special_attention = reg_data.get('specialAttention', '')
                    if 'Labels functionality verification' in special_attention:
                        self.log_result("Data Persistence", True, "Updates persisted correctly")
                    else:
                        self.log_result("Data Persistence", False, "Update not persisted")
                except:
                    self.log_result("Data Persistence", False, "Invalid response format")
            else:
                self.log_result("Data Persistence", False, "Could not retrieve registration")
        
        # Test registration listing to ensure data is in collections
        success, response = self.make_request('GET', 'admin-registrations-pending')
        if success and response:
            try:
                pending_regs = response.json()
                # Look for our created registration
                found_our_reg = any(reg.get('id') == self.created_registration_id for reg in pending_regs)
                self.log_result("Registration in Pending List", found_our_reg, f"Total pending: {len(pending_regs)}")
            except:
                self.log_result("Registration in Pending List", False, "Invalid response format")
        
        return True

    def test_5_error_handling(self):
        """Test 5: Error Handling and Validation"""
        print("\n⚠️  TEST 5: Error Handling")
        print("-" * 40)
        
        # Test invalid registration ID
        success, response = self.make_request('GET', 'admin-registrations/invalid-id-12345', expected_status=404)
        if success:
            self.log_result("Invalid ID Error Handling", True, "Proper 404 response")
        else:
            self.log_result("Invalid ID Error Handling", False, f"Expected 404, got {response.status_code if response else 'No response'}")
        
        # Test invalid data submission
        invalid_data = {"firstName": "", "lastName": ""}  # Missing required fields
        success, response = self.make_request('POST', 'admin-registrations', invalid_data, expected_status=422)
        if success:
            self.log_result("Invalid Data Validation", True, "Proper 422 validation error")
        else:
            self.log_result("Invalid Data Validation", False, f"Expected 422, got {response.status_code if response else 'No response'}")
        
        return True

    def test_6_labels_related_data_access(self):
        """Test 6: Labels-Related Data Access (No Backend Changes Expected)"""
        print("\n🏷️  TEST 6: Labels-Related Data Access")
        print("-" * 40)
        
        # Since labels functionality was frontend-only, test that all registration data
        # needed for labels is still accessible
        if self.created_registration_id:
            success, response = self.make_request('GET', f'admin-registrations/{self.created_registration_id}')
            if success and response:
                try:
                    reg_data = response.json()
                    
                    # Check key fields that would be used in labels
                    label_fields = ['firstName', 'lastName', 'healthCard', 'dob', 'address', 'phone1']
                    available_fields = []
                    
                    for field in label_fields:
                        if field in reg_data and reg_data[field]:
                            available_fields.append(field)
                    
                    success_rate = len(available_fields) / len(label_fields)
                    self.log_result("Labels Data Fields Available", success_rate >= 0.8, f"Available: {', '.join(available_fields)}")
                    
                    # Test that registration data is complete and formatted correctly
                    required_fields = ['firstName', 'lastName', 'id', 'timestamp']
                    missing_fields = [field for field in required_fields if field not in reg_data]
                    
                    if not missing_fields:
                        self.log_result("Registration Data Completeness", True, "All required fields present")
                    else:
                        self.log_result("Registration Data Completeness", False, f"Missing: {', '.join(missing_fields)}")
                        
                except:
                    self.log_result("Labels Data Access", False, "Invalid response format")
            else:
                self.log_result("Labels Data Access", False, "Could not access registration data")
        
        return True

    def cleanup_test_data(self):
        """Clean up test data"""
        print("\n🧹 CLEANUP: Removing Test Data")
        print("-" * 40)
        
        if self.created_registration_id:
            success, response = self.make_request('DELETE', f'admin-registrations/{self.created_registration_id}', expected_status=200)
            if success:
                self.log_result("Test Data Cleanup", True, f"Removed registration {self.created_registration_id}")
            else:
                self.log_result("Test Data Cleanup", False, f"Could not remove test registration")

    def run_all_tests(self):
        """Run all backend verification tests"""
        print(f"🚀 Starting Backend Verification Tests")
        print(f"📅 Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🔗 Backend URL: {self.base_url}")
        
        # Run all tests
        test_methods = [
            self.test_1_core_api_endpoints,
            self.test_2_registration_crud_operations,
            self.test_3_template_operations,
            self.test_4_database_persistence,
            self.test_5_error_handling,
            self.test_6_labels_related_data_access
        ]
        
        all_tests_passed = True
        for test_method in test_methods:
            try:
                result = test_method()
                if not result:
                    all_tests_passed = False
            except Exception as e:
                print(f"❌ Test method {test_method.__name__} failed with error: {str(e)}")
                all_tests_passed = False
        
        # Cleanup
        self.cleanup_test_data()
        
        # Final results
        print("\n" + "=" * 80)
        print("BACKEND VERIFICATION TEST RESULTS")
        print("=" * 80)
        
        for result in self.test_results:
            print(result)
        
        print(f"\n📊 SUMMARY:")
        print(f"   Tests Run: {self.tests_run}")
        print(f"   Tests Passed: {self.tests_passed}")
        print(f"   Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        if all_tests_passed and self.tests_passed == self.tests_run:
            print(f"\n🎉 ALL TESTS PASSED - Backend functionality is intact after labels changes")
            return True
        else:
            print(f"\n⚠️  SOME TESTS FAILED - Backend issues detected")
            return False

if __name__ == "__main__":
    tester = LabelsBackendVerificationTest()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)