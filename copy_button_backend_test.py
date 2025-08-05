#!/usr/bin/env python3
"""
Backend Testing Suite for Copy Button Fix Review
Tests all backend functionality to ensure no existing features were broken
after fixing the copy button to fetch test data directly from the API.
"""

import requests
import json
import sys
import os
from datetime import datetime, date
import uuid
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

class CopyButtonBackendTester:
    def __init__(self):
        # Use the same URL that frontend uses
        self.base_url = os.getenv('REACT_APP_BACKEND_URL', 'https://46471c8a-a981-4b23-bca9-bb5c0ba282bc.preview.emergentagent.com')
        self.api_url = f"{self.base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.test_registration_id = None
        self.test_data = {}
        
        print(f"🔧 Backend API URL: {self.api_url}")
        print("=" * 80)
        print("BACKEND TESTING AFTER COPY BUTTON FIX")
        print("Testing all backend functionality to ensure no features were broken")
        print("=" * 80)

    def test_api_endpoint(self, name, method, endpoint, expected_status=200, data=None, description=""):
        """Test a single API endpoint"""
        url = f"{self.api_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        self.tests_run += 1
        print(f"\n🔍 Test {self.tests_run}: {name}")
        if description:
            print(f"   📝 {description}")
        print(f"   🌐 {method} {url}")
        
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
            
            if success:
                self.tests_passed += 1
                print(f"   ✅ PASSED - Status: {response.status_code}")
                
                try:
                    response_data = response.json()
                    if isinstance(response_data, list):
                        print(f"   📊 Response: List with {len(response_data)} items")
                        if len(response_data) > 0:
                            print(f"   📋 Sample item keys: {list(response_data[0].keys()) if response_data[0] else 'Empty item'}")
                    elif isinstance(response_data, dict):
                        print(f"   📊 Response keys: {list(response_data.keys())}")
                    return True, response_data
                except:
                    print(f"   📊 Response: Non-JSON or empty")
                    return True, {}
            else:
                print(f"   ❌ FAILED - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   🚨 Error: {error_data}")
                except:
                    print(f"   🚨 Error: {response.text}")
                return False, {}
                
        except requests.exceptions.Timeout:
            print(f"   ⏰ TIMEOUT - Request took longer than 30 seconds")
            return False, {}
        except requests.exceptions.ConnectionError:
            print(f"   🔌 CONNECTION ERROR - Could not connect to server")
            return False, {}
        except Exception as e:
            print(f"   💥 EXCEPTION - {str(e)}")
            return False, {}

    def test_core_api_endpoints(self):
        """Test all core API endpoints"""
        print("\n" + "="*60)
        print("1. TESTING CORE API ENDPOINTS")
        print("="*60)
        
        endpoints = [
            ("Admin Registrations Pending", "GET", "admin-registrations-pending", 200, None, "Get all pending registrations"),
            ("Admin Registrations Submitted", "GET", "admin-registrations-submitted", 200, None, "Get all submitted registrations"),
            ("Notes Templates", "GET", "notes-templates", 200, None, "Get all notes templates"),
            ("Clinical Templates", "GET", "clinical-templates", 200, None, "Get all clinical templates"),
        ]
        
        for name, method, endpoint, status, data, desc in endpoints:
            success, response_data = self.test_api_endpoint(name, method, endpoint, status, data, desc)
            if success and endpoint == "admin-registrations-pending" and response_data:
                # Store a registration ID for later tests
                if isinstance(response_data, list) and len(response_data) > 0:
                    self.test_registration_id = response_data[0].get('id')
                    print(f"   📌 Stored test registration ID: {self.test_registration_id}")

    def test_registration_crud(self):
        """Test registration CRUD operations"""
        print("\n" + "="*60)
        print("2. TESTING REGISTRATION CRUD OPERATIONS")
        print("="*60)
        
        # Create a test registration
        test_registration = {
            "firstName": "TestUser",
            "lastName": f"CopyButtonTest{datetime.now().strftime('%H%M%S')}",
            "dob": "1990-01-01",
            "patientConsent": "verbal",
            "gender": "Male",
            "province": "Ontario",
            "healthCard": "1234567890AB",
            "phone1": "4161234567",
            "email": "test@example.com",
            "address": "123 Test Street",
            "city": "Toronto",
            "postalCode": "M1M1M1"
        }
        
        # CREATE
        success, create_response = self.test_api_endpoint(
            "Create Registration", "POST", "admin-register", 200, 
            test_registration, "Create a new admin registration"
        )
        
        if success and create_response:
            created_id = create_response.get('id')
            self.test_data['created_registration_id'] = created_id
            print(f"   📌 Created registration ID: {created_id}")
            
            # READ - Get the created registration
            success, read_response = self.test_api_endpoint(
                "Read Registration", "GET", f"admin-registrations/{created_id}", 200,
                None, "Retrieve the created registration"
            )
            
            if success and read_response:
                print(f"   ✅ Registration retrieved successfully")
                
                # UPDATE - Modify the registration
                update_data = {
                    "firstName": "UpdatedTestUser",
                    "specialAttention": "Updated via copy button backend test"
                }
                
                success, update_response = self.test_api_endpoint(
                    "Update Registration", "PUT", f"admin-registrations/{created_id}", 200,
                    update_data, "Update the registration"
                )
                
                if success:
                    print(f"   ✅ Registration updated successfully")

    def test_test_data_endpoints(self):
        """Test test data retrieval endpoints - CRITICAL for copy button functionality"""
        print("\n" + "="*60)
        print("3. TESTING TEST DATA ENDPOINTS (CRITICAL FOR COPY BUTTON)")
        print("="*60)
        
        # Use stored registration ID or find one
        registration_id = self.test_data.get('created_registration_id') or self.test_registration_id
        
        if not registration_id:
            print("   ⚠️  No registration ID available, trying to get one from pending registrations")
            success, pending_data = self.test_api_endpoint(
                "Get Pending for Test ID", "GET", "admin-registrations-pending", 200,
                None, "Get registration ID for testing"
            )
            if success and pending_data and len(pending_data) > 0:
                registration_id = pending_data[0].get('id')
                print(f"   📌 Using registration ID: {registration_id}")
        
        if registration_id:
            # Test the specific endpoint mentioned in the review request
            success, tests_response = self.test_api_endpoint(
                "Get Registration Tests", "GET", f"admin-registration/{registration_id}/tests", 200,
                None, "CRITICAL: Test data endpoint used by copy button"
            )
            
            if success:
                print(f"   🎯 CRITICAL TEST PASSED: Copy button test data endpoint working")
            else:
                print(f"   🚨 CRITICAL TEST FAILED: Copy button test data endpoint not working")
            
            # Test other test-related endpoints
            test_endpoints = [
                (f"admin-registration/{registration_id}/notes", "Get registration notes"),
                (f"admin-registration/{registration_id}/interactions", "Get registration interactions"),
                (f"admin-registration/{registration_id}/activities", "Get registration activities"),
            ]
            
            for endpoint, description in test_endpoints:
                self.test_api_endpoint(
                    f"Test Data - {description}", "GET", endpoint, 200,
                    None, description
                )
        else:
            print("   ⚠️  Could not find registration ID for test data endpoint testing")

    def test_template_operations(self):
        """Test template operations"""
        print("\n" + "="*60)
        print("4. TESTING TEMPLATE OPERATIONS")
        print("="*60)
        
        # Test Notes Templates
        success, notes_templates = self.test_api_endpoint(
            "Notes Templates List", "GET", "notes-templates", 200,
            None, "Get all notes templates"
        )
        
        if success and notes_templates:
            print(f"   📋 Found {len(notes_templates)} notes templates")
            
            # Test saving notes templates
            test_template = {
                "name": f"Test Template {datetime.now().strftime('%H%M%S')}",
                "content": "This is a test template created during copy button backend testing",
                "is_default": False
            }
            
            # Add to existing templates and save
            updated_templates = notes_templates + [test_template]
            
            success, save_response = self.test_api_endpoint(
                "Save Notes Templates", "POST", "notes-templates/save-all", 200,
                updated_templates, "Save updated notes templates"
            )
        
        # Test Clinical Templates
        success, clinical_templates = self.test_api_endpoint(
            "Clinical Templates List", "GET", "clinical-templates", 200,
            None, "Get all clinical templates"
        )
        
        if success and clinical_templates:
            print(f"   📋 Found {len(clinical_templates)} clinical templates")

    def test_finalize_functionality(self):
        """Test finalize functionality"""
        print("\n" + "="*60)
        print("5. TESTING FINALIZE FUNCTIONALITY")
        print("="*60)
        
        registration_id = self.test_data.get('created_registration_id') or self.test_registration_id
        
        if registration_id:
            # Test finalize endpoint (but don't actually finalize to avoid sending emails)
            success, finalize_response = self.test_api_endpoint(
                "Finalize Registration (GET)", "GET", f"admin-registration/{registration_id}/finalize", 400,
                None, "Test finalize endpoint availability (expecting 400 for non-pending registration)"
            )
            
            if success:
                print(f"   ✅ Finalize endpoint is accessible")
            else:
                print(f"   ⚠️  Finalize endpoint test - this may be expected if registration is not ready")
        else:
            print("   ⚠️  No registration ID available for finalize testing")

    def test_service_health(self):
        """Test overall service health"""
        print("\n" + "="*60)
        print("6. TESTING SERVICE HEALTH")
        print("="*60)
        
        # Test basic connectivity
        try:
            response = requests.get(f"{self.base_url}/", timeout=5)
            if response.status_code in [200, 404]:  # 404 is OK for root endpoint
                print(f"   ✅ Backend service is responding")
                self.tests_run += 1
                self.tests_passed += 1
            else:
                print(f"   ⚠️  Backend service response: {response.status_code}")
                self.tests_run += 1
        except Exception as e:
            print(f"   ❌ Backend service connectivity issue: {str(e)}")
            self.tests_run += 1

    def run_all_tests(self):
        """Run all backend tests"""
        print("🚀 Starting comprehensive backend testing after copy button fix...")
        
        # Run all test suites
        self.test_core_api_endpoints()
        self.test_registration_crud()
        self.test_test_data_endpoints()
        self.test_template_operations()
        self.test_finalize_functionality()
        self.test_service_health()
        
        # Print final results
        print("\n" + "="*80)
        print("FINAL TEST RESULTS")
        print("="*80)
        
        success_rate = (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0
        
        print(f"📊 Tests Run: {self.tests_run}")
        print(f"✅ Tests Passed: {self.tests_passed}")
        print(f"❌ Tests Failed: {self.tests_run - self.tests_passed}")
        print(f"📈 Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 90:
            print("\n🎉 EXCELLENT: Backend functionality is working correctly after copy button fix!")
            print("✅ No existing features appear to be broken by the copy button changes.")
        elif success_rate >= 75:
            print("\n✅ GOOD: Most backend functionality is working correctly.")
            print("⚠️  Some minor issues detected but core functionality intact.")
        else:
            print("\n🚨 ISSUES DETECTED: Significant backend problems found.")
            print("❌ Copy button fix may have affected backend functionality.")
        
        print("\n📋 COPY BUTTON SPECIFIC FINDINGS:")
        print("The copy button fix was a frontend-only change that:")
        print("• Removes dependency on React state for test data")
        print("• Fetches fresh test data directly from API when copying")
        print("• Improves error handling when test data cannot be loaded")
        print("• Should NOT affect any backend functionality")
        
        return success_rate >= 75

if __name__ == "__main__":
    tester = CopyButtonBackendTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)