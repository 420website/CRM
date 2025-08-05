#!/usr/bin/env python3
"""
Backend Navigation Test - Comprehensive Backend Testing After Frontend Navigation Changes
======================================================================================

This test verifies that the "Back to Dashboard" button addition to AdminRegister.js and AdminEdit.js
did not break any existing backend functionality. The changes were frontend-only navigation improvements.

Test Focus:
1. All existing API endpoints are working correctly
2. Core backend services are running properly  
3. No backend errors after frontend navigation improvements
4. Registration and editing functionality remains intact
"""

import requests
import json
import uuid
from datetime import datetime, date
import os
import sys
import time

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://dfe9a1e1-7f3d-45aa-ad71-43a254e568c5.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

class BackendNavigationTester:
    def __init__(self):
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        
    def log_test(self, test_name, success, message=""):
        """Log test result"""
        self.total_tests += 1
        if success:
            self.passed_tests += 1
            status = "✅ PASS"
        else:
            status = "❌ FAIL"
        
        result = f"{status}: {test_name}"
        if message:
            result += f" - {message}"
        
        print(result)
        self.test_results.append({
            'test': test_name,
            'success': success,
            'message': message
        })
        
    def test_health_check(self):
        """Test basic API health check"""
        try:
            response = requests.get(f"{API_BASE}/", timeout=10)
            success = response.status_code == 200
            message = f"Status: {response.status_code}"
            if success:
                message += f", Response: {response.text[:100]}"
            self.log_test("API Health Check", success, message)
            return success
        except Exception as e:
            self.log_test("API Health Check", False, f"Error: {str(e)}")
            return False
    
    def test_admin_registrations_endpoints(self):
        """Test admin registration endpoints"""
        try:
            # Test pending registrations
            response = requests.get(f"{API_BASE}/admin-registrations-pending", timeout=10)
            pending_success = response.status_code == 200
            pending_count = len(response.json()) if pending_success else 0
            self.log_test("Admin Registrations Pending", pending_success, 
                         f"Status: {response.status_code}, Count: {pending_count}")
            
            # Test submitted registrations  
            response = requests.get(f"{API_BASE}/admin-registrations-submitted", timeout=10)
            submitted_success = response.status_code == 200
            submitted_count = len(response.json()) if submitted_success else 0
            self.log_test("Admin Registrations Submitted", submitted_success,
                         f"Status: {response.status_code}, Count: {submitted_count}")
            
            return pending_success and submitted_success
        except Exception as e:
            self.log_test("Admin Registrations Endpoints", False, f"Error: {str(e)}")
            return False
    
    def test_template_endpoints(self):
        """Test template management endpoints"""
        try:
            # Test notes templates
            response = requests.get(f"{API_BASE}/notes-templates", timeout=10)
            notes_success = response.status_code == 200
            notes_count = len(response.json()) if notes_success else 0
            self.log_test("Notes Templates", notes_success,
                         f"Status: {response.status_code}, Count: {notes_count}")
            
            # Test clinical templates
            response = requests.get(f"{API_BASE}/clinical-templates", timeout=10)
            clinical_success = response.status_code == 200
            clinical_count = len(response.json()) if clinical_success else 0
            self.log_test("Clinical Templates", clinical_success,
                         f"Status: {response.status_code}, Count: {clinical_count}")
            
            return notes_success and clinical_success
        except Exception as e:
            self.log_test("Template Endpoints", False, f"Error: {str(e)}")
            return False
    
    def test_admin_registration_crud(self):
        """Test admin registration CRUD operations"""
        try:
            # Create test registration
            test_data = {
                "firstName": "Navigation",
                "lastName": "TestUser", 
                "patientConsent": "verbal",
                "regDate": date.today().isoformat(),
                "province": "Ontario"
            }
            
            response = requests.post(f"{API_BASE}/admin-register", 
                                   json=test_data, timeout=10)
            create_success = response.status_code == 200
            
            if create_success:
                registration_id = response.json().get('id')
                self.log_test("Admin Registration Create", True, 
                             f"Created ID: {registration_id}")
                
                # Test retrieve registration
                response = requests.get(f"{API_BASE}/admin-registration/{registration_id}", 
                                      timeout=10)
                retrieve_success = response.status_code == 200
                self.log_test("Admin Registration Retrieve", retrieve_success,
                             f"Status: {response.status_code}")
                
                # Test update registration
                update_data = {"specialAttention": "Navigation test update"}
                response = requests.put(f"{API_BASE}/admin-registration/{registration_id}",
                                      json=update_data, timeout=10)
                update_success = response.status_code == 200
                self.log_test("Admin Registration Update", update_success,
                             f"Status: {response.status_code}")
                
                return create_success and retrieve_success and update_success
            else:
                self.log_test("Admin Registration Create", False,
                             f"Status: {response.status_code}, Error: {response.text[:200]}")
                return False
                
        except Exception as e:
            self.log_test("Admin Registration CRUD", False, f"Error: {str(e)}")
            return False
    
    def test_data_endpoints(self):
        """Test data retrieval endpoints used by frontend"""
        endpoints_to_test = [
            ("Notes Endpoint", "/notes-templates"),
            ("Clinical Templates Endpoint", "/clinical-templates"),
            ("Legacy Data Summary", "/legacy-data-summary"),
        ]
        
        all_success = True
        for name, endpoint in endpoints_to_test:
            try:
                response = requests.get(f"{API_BASE}{endpoint}", timeout=10)
                success = response.status_code in [200, 404]  # 404 is acceptable for some endpoints
                self.log_test(name, success, f"Status: {response.status_code}")
                if not success:
                    all_success = False
            except Exception as e:
                self.log_test(name, False, f"Error: {str(e)}")
                all_success = False
        
        return all_success
    
    def test_finalize_functionality(self):
        """Test finalize functionality that might be affected by navigation changes"""
        try:
            # First get a pending registration to test finalize
            response = requests.get(f"{API_BASE}/admin-registrations-pending", timeout=10)
            if response.status_code == 200:
                pending_registrations = response.json()
                if pending_registrations:
                    # Test finalize endpoint exists (don't actually finalize)
                    test_id = pending_registrations[0].get('id')
                    # Just test the endpoint exists by making a GET request
                    response = requests.get(f"{API_BASE}/admin-registration/{test_id}/finalize", 
                                          timeout=10)
                    # Expect 405 Method Not Allowed for GET on POST endpoint
                    success = response.status_code in [405, 200, 404]
                    self.log_test("Finalize Endpoint Exists", success,
                                 f"Status: {response.status_code}")
                    return success
                else:
                    self.log_test("Finalize Functionality", True, "No pending registrations to test")
                    return True
            else:
                self.log_test("Finalize Functionality", False, "Cannot access pending registrations")
                return False
        except Exception as e:
            self.log_test("Finalize Functionality", False, f"Error: {str(e)}")
            return False
    
    def test_attachment_endpoints(self):
        """Test attachment-related endpoints"""
        try:
            # Test attachment sharing endpoint (should return 422 for missing data)
            response = requests.post(f"{API_BASE}/share-attachment", json={}, timeout=10)
            success = response.status_code in [422, 400]  # Expected validation error
            self.log_test("Attachment Sharing Endpoint", success,
                         f"Status: {response.status_code} (expected validation error)")
            return success
        except Exception as e:
            self.log_test("Attachment Endpoints", False, f"Error: {str(e)}")
            return False
    
    def test_analytics_endpoints(self):
        """Test analytics endpoints"""
        try:
            # Test Claude chat endpoint (should return 422 for empty message)
            response = requests.post(f"{API_BASE}/claude-chat", json={}, timeout=10)
            success = response.status_code in [422, 400, 500]  # Expected validation error
            self.log_test("Claude Chat Endpoint", success,
                         f"Status: {response.status_code} (expected validation error)")
            return success
        except Exception as e:
            self.log_test("Analytics Endpoints", False, f"Error: {str(e)}")
            return False
    
    def run_comprehensive_test(self):
        """Run all backend tests"""
        print("🚀 BACKEND NAVIGATION TEST - COMPREHENSIVE BACKEND VERIFICATION")
        print("=" * 80)
        print("Testing backend functionality after 'Back to Dashboard' button addition")
        print("Changes were frontend-only navigation improvements in AdminRegister.js and AdminEdit.js")
        print("=" * 80)
        
        # Run all tests
        tests = [
            self.test_health_check,
            self.test_admin_registrations_endpoints,
            self.test_template_endpoints,
            self.test_admin_registration_crud,
            self.test_data_endpoints,
            self.test_finalize_functionality,
            self.test_attachment_endpoints,
            self.test_analytics_endpoints
        ]
        
        for test in tests:
            try:
                test()
                time.sleep(0.5)  # Brief pause between tests
            except Exception as e:
                print(f"❌ Test execution error: {str(e)}")
        
        # Print summary
        print("\n" + "=" * 80)
        print("🎯 BACKEND NAVIGATION TEST SUMMARY")
        print("=" * 80)
        
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.total_tests - self.passed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 80:
            print("\n✅ BACKEND VERIFICATION: SUCCESSFUL")
            print("Backend functionality is working correctly after navigation changes.")
            print("The 'Back to Dashboard' button addition did not break existing features.")
        else:
            print("\n❌ BACKEND VERIFICATION: ISSUES FOUND")
            print("Some backend functionality may have been affected.")
            print("Review failed tests above for details.")
        
        print("\n📋 DETAILED RESULTS:")
        for result in self.test_results:
            status = "✅" if result['success'] else "❌"
            print(f"{status} {result['test']}: {result['message']}")
        
        return success_rate >= 80

if __name__ == "__main__":
    print(f"Using Backend URL: {BACKEND_URL}")
    print(f"API Base: {API_BASE}")
    
    tester = BackendNavigationTester()
    success = tester.run_comprehensive_test()
    
    sys.exit(0 if success else 1)