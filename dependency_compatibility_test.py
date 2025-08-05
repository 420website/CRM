#!/usr/bin/env python3
"""
Dependency Compatibility Test Suite
Tests backend functionality after dependency version changes:
- annotated-types==0.6.0 (downgraded from 0.7.0)
- pydantic==2.7.4 (downgraded)
- fastapi==0.115.0 (maintained)
- uvicorn==0.30.6 (maintained)
"""

import requests
import json
import sys
import os
from datetime import datetime, date
import random
import string
from dotenv import load_dotenv

class DependencyCompatibilityTester:
    def __init__(self, base_url):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []
        
    def log_test(self, name, success, details=""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name}")
        else:
            print(f"❌ {name}")
        
        if details:
            print(f"   {details}")
            
        self.test_results.append({
            "name": name,
            "success": success,
            "details": details
        })
        
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
            else:
                return False, None, f"Unsupported method: {method}"
                
            success = response.status_code == expected_status
            
            try:
                response_data = response.json()
            except:
                response_data = {"text": response.text}
                
            return success, response_data, f"Status: {response.status_code}"
            
        except requests.exceptions.RequestException as e:
            return False, None, f"Request failed: {str(e)}"
    
    def generate_test_data(self):
        """Generate test data for various endpoints"""
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
        
        return {
            "admin_registration": {
                "firstName": f"Test{random_suffix}",
                "lastName": f"User{random_suffix}",
                "patientConsent": "Verbal",
                "gender": "Male",
                "province": "Ontario",
                "age": "35",
                "healthCard": ''.join(random.choices(string.digits, k=10)),
                "phone1": ''.join(random.choices(string.digits, k=10)),
                "email": f"test{random_suffix}@example.com",
                "language": "English"
            },
            "test_record": {
                "test_type": "HIV",
                "test_date": "2024-01-15",
                "hiv_result": "negative",
                "hiv_type": "Type 1",
                "hiv_tester": "CM"
            },
            "notes_template": {
                "name": f"Test Template {random_suffix}",
                "content": f"This is a test template content {random_suffix}",
                "is_default": False
            },
            "clinical_template": {
                "name": f"Clinical Template {random_suffix}",
                "content": f"Clinical template content {random_suffix}",
                "is_default": False
            }
        }
    
    def test_fastapi_pydantic_compatibility(self):
        """Test FastAPI and Pydantic model compatibility"""
        print("\n🔍 Testing FastAPI/Pydantic Compatibility...")
        
        # Test 1: Basic API health check using notes-templates endpoint
        success, data, details = self.make_request('GET', 'api/notes-templates')
        self.log_test("FastAPI Basic Health Check", success, details)
        
        # Test 2: Pydantic model validation - Admin Registration
        test_data = self.generate_test_data()
        success, data, details = self.make_request(
            'POST', 'api/admin-register', 
            test_data["admin_registration"]
        )
        self.log_test("Pydantic Model Validation (Admin Registration)", success, details)
        
        if success and data and 'registration_id' in data:
            self.registration_id = data['registration_id']
            self.log_test("Registration ID Generation", True, f"ID: {self.registration_id}")
        else:
            self.log_test("Registration ID Generation", False, "No registration_id in response")
            return False
            
        # Test 3: Pydantic validation error handling
        invalid_data = test_data["admin_registration"].copy()
        invalid_data.pop("firstName")  # Remove required field
        success, data, details = self.make_request(
            'POST', 'api/admin-register', 
            invalid_data, expected_status=422
        )
        self.log_test("Pydantic Validation Error Handling", success, details)
        
        return True
    
    def test_database_operations(self):
        """Test database operations with new dependencies"""
        print("\n🔍 Testing Database Operations...")
        
        if not hasattr(self, 'registration_id'):
            self.log_test("Database Operations", False, "No registration_id available")
            return False
            
        # Test 1: Create test record
        test_data = self.generate_test_data()
        success, data, details = self.make_request(
            'POST', f'api/admin-registration/{self.registration_id}/test',
            test_data["test_record"]
        )
        self.log_test("Database Create Operation (Test Record)", success, details)
        
        if success and data and 'test_id' in data:
            self.test_id = data['test_id']
        else:
            self.log_test("Test Record Creation", False, "No test_id in response")
            return False
            
        # Test 2: Read test records
        success, data, details = self.make_request(
            'GET', f'api/admin-registration/{self.registration_id}/tests'
        )
        self.log_test("Database Read Operation (Test Records)", success, details)
        
        # Test 3: Update test record
        update_data = {
            "hiv_result": "positive",
            "hiv_type": "Type 2"
        }
        success, data, details = self.make_request(
            'PUT', f'api/admin-registration/{self.registration_id}/test/{self.test_id}',
            update_data
        )
        self.log_test("Database Update Operation (Test Record)", success, details)
        
        # Test 4: Delete test record
        success, data, details = self.make_request(
            'DELETE', f'api/admin-registration/{self.registration_id}/test/{self.test_id}'
        )
        self.log_test("Database Delete Operation (Test Record)", success, details)
        
        return True
    
    def test_template_operations(self):
        """Test template-related functionality"""
        print("\n🔍 Testing Template Operations...")
        
        # Test 1: Get notes templates
        success, data, details = self.make_request('GET', 'api/notes-templates')
        self.log_test("Get Notes Templates", success, details)
        
        # Test 2: Get clinical templates
        success, data, details = self.make_request('GET', 'api/clinical-templates')
        self.log_test("Get Clinical Templates", success, details)
        
        # Test 3: Create notes template
        test_data = self.generate_test_data()
        success, data, details = self.make_request(
            'POST', 'api/notes-templates',
            test_data["notes_template"]
        )
        self.log_test("Create Notes Template", success, details)
        
        # Test 4: Create clinical template
        success, data, details = self.make_request(
            'POST', 'api/clinical-templates',
            test_data["clinical_template"]
        )
        self.log_test("Create Clinical Template", success, details)
        
        return True
    
    def test_api_endpoints(self):
        """Test key API endpoints"""
        print("\n🔍 Testing Key API Endpoints...")
        
        # Test 1: Admin registrations pending
        success, data, details = self.make_request('GET', 'api/admin-registrations-pending')
        self.log_test("Admin Registrations Pending Endpoint", success, details)
        
        # Test 2: Admin registrations submitted
        success, data, details = self.make_request('GET', 'api/admin-registrations-submitted')
        self.log_test("Admin Registrations Submitted Endpoint", success, details)
        
        # Test 3: Admin activities
        success, data, details = self.make_request('GET', 'api/admin-activities')
        self.log_test("Admin Activities Endpoint", success, details)
        
        return True
    
    def test_error_handling(self):
        """Test error handling with new dependencies"""
        print("\n🔍 Testing Error Handling...")
        
        # Test 1: 404 error handling
        success, data, details = self.make_request(
            'GET', 'api/nonexistent-endpoint', 
            expected_status=404
        )
        self.log_test("404 Error Handling", success, details)
        
        # Test 2: Invalid JSON handling
        try:
            url = f"{self.base_url}/api/admin-register"
            headers = {'Content-Type': 'application/json'}
            response = requests.post(url, data="invalid json", headers=headers, timeout=30)
            success = response.status_code == 422
            self.log_test("Invalid JSON Handling", success, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Invalid JSON Handling", False, f"Error: {str(e)}")
        
        # Test 3: Missing required fields
        success, data, details = self.make_request(
            'POST', 'api/admin-register',
            {"invalid": "data"}, expected_status=422
        )
        self.log_test("Missing Required Fields Handling", success, details)
        
        return True
    
    def test_data_serialization(self):
        """Test data serialization with new Pydantic version"""
        print("\n🔍 Testing Data Serialization...")
        
        # Test 1: Date serialization
        test_data = self.generate_test_data()
        test_data["admin_registration"]["dob"] = "1990-05-15"
        test_data["admin_registration"]["regDate"] = "2024-01-15"
        
        success, data, details = self.make_request(
            'POST', 'api/admin-register',
            test_data["admin_registration"]
        )
        self.log_test("Date Serialization", success, details)
        
        # Test 2: Boolean serialization
        test_data["admin_registration"]["leaveMessage"] = True
        test_data["admin_registration"]["voicemail"] = False
        test_data["admin_registration"]["text"] = True
        
        success, data, details = self.make_request(
            'POST', 'api/admin-register',
            test_data["admin_registration"]
        )
        self.log_test("Boolean Serialization", success, details)
        
        # Test 3: Optional field handling
        minimal_data = {
            "firstName": "Test",
            "lastName": "User",
            "patientConsent": "Verbal"
        }
        
        success, data, details = self.make_request(
            'POST', 'api/admin-register',
            minimal_data
        )
        self.log_test("Optional Field Handling", success, details)
        
        return True
    
    def test_concurrent_requests(self):
        """Test concurrent request handling"""
        print("\n🔍 Testing Concurrent Request Handling...")
        
        import threading
        import time
        
        results = []
        
        def make_concurrent_request():
            success, data, details = self.make_request('GET', 'api/notes-templates')
            results.append(success)
        
        # Create 5 concurrent threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=make_concurrent_request)
            threads.append(thread)
        
        # Start all threads
        start_time = time.time()
        for thread in threads:
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        end_time = time.time()
        
        # Check results
        success_count = sum(results)
        total_requests = len(results)
        
        success = success_count == total_requests
        details = f"{success_count}/{total_requests} requests successful in {end_time - start_time:.2f}s"
        
        self.log_test("Concurrent Request Handling", success, details)
        
        return success
    
    def run_all_tests(self):
        """Run all dependency compatibility tests"""
        print("🚀 Starting Dependency Compatibility Tests")
        print(f"🔗 Backend URL: {self.base_url}")
        print("📦 Testing compatibility with:")
        print("   - annotated-types==0.6.0")
        print("   - pydantic==2.7.4") 
        print("   - fastapi==0.115.0")
        print("   - uvicorn==0.30.6")
        print("=" * 60)
        
        # Run all test suites
        test_suites = [
            self.test_fastapi_pydantic_compatibility,
            self.test_database_operations,
            self.test_template_operations,
            self.test_api_endpoints,
            self.test_error_handling,
            self.test_data_serialization,
            self.test_concurrent_requests
        ]
        
        all_passed = True
        for test_suite in test_suites:
            try:
                result = test_suite()
                if not result:
                    all_passed = False
            except Exception as e:
                print(f"❌ Test suite failed with exception: {str(e)}")
                all_passed = False
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 DEPENDENCY COMPATIBILITY TEST SUMMARY")
        print("=" * 60)
        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        
        if all_passed and self.tests_passed == self.tests_run:
            print("\n✅ ALL DEPENDENCY COMPATIBILITY TESTS PASSED")
            print("🎉 Backend is working correctly with new dependency versions!")
            return True
        else:
            print("\n❌ SOME TESTS FAILED")
            print("⚠️  Backend may have issues with new dependency versions")
            
            # Print failed tests
            failed_tests = [r for r in self.test_results if not r['success']]
            if failed_tests:
                print("\n❌ Failed Tests:")
                for test in failed_tests:
                    print(f"   - {test['name']}: {test['details']}")
            
            return False

def main():
    """Main test runner"""
    # Load environment variables
    load_dotenv('/app/frontend/.env')
    
    # Get backend URL
    backend_url = os.environ.get('REACT_APP_BACKEND_URL')
    if not backend_url:
        print("❌ Error: REACT_APP_BACKEND_URL not found in frontend .env file")
        return 1
    
    print(f"🔗 Using backend URL: {backend_url}")
    
    # Run tests
    tester = DependencyCompatibilityTester(backend_url)
    success = tester.run_all_tests()
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())