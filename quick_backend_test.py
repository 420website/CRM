#!/usr/bin/env python3
"""
Quick Backend Verification Test for Labels Button Changes
=========================================================

This test quickly verifies that all backend functionality remains intact 
after the frontend changes to remove PDF/print functionality from labels button.
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

class QuickBackendTest:
    def __init__(self):
        self.base_url = os.getenv('REACT_APP_BACKEND_URL', 'http://localhost:8001')
        if not self.base_url.endswith('/api'):
            self.base_url = f"{self.base_url}/api"
        
        self.tests_passed = 0
        self.tests_total = 0
        
        print("🔧 Quick Backend Verification Test")
        print(f"📡 Backend URL: {self.base_url}")
        print("=" * 60)

    def test_endpoint(self, name, endpoint, method='GET', data=None, expected_status=200, timeout=10):
        """Test a single endpoint"""
        self.tests_total += 1
        url = f"{self.base_url}/{endpoint}"
        
        try:
            if method == 'GET':
                response = requests.get(url, timeout=timeout)
            elif method == 'POST':
                response = requests.post(url, json=data, timeout=timeout)
            
            if response.status_code == expected_status:
                self.tests_passed += 1
                print(f"✅ {name} - Status: {response.status_code}")
                return True, response
            else:
                print(f"❌ {name} - Expected: {expected_status}, Got: {response.status_code}")
                return False, response
                
        except Exception as e:
            print(f"❌ {name} - Error: {str(e)}")
            return False, None

    def run_tests(self):
        """Run all backend tests"""
        print("🚀 Testing Core Backend Functionality...")
        print()
        
        # Test 1: API Health
        self.test_endpoint("API Health Check", "")
        
        # Test 2: Core Endpoints
        self.test_endpoint("Pending Registrations", "admin-registrations-pending")
        self.test_endpoint("Submitted Registrations", "admin-registrations-submitted")
        self.test_endpoint("Notes Templates", "notes-templates")
        self.test_endpoint("Clinical Templates", "clinical-templates")
        
        # Test 3: Create a test registration
        test_data = {
            "firstName": "TestUser",
            "lastName": f"Backend{random.randint(1000, 9999)}",
            "patientConsent": "Verbal",
            "province": "Ontario"
        }
        
        success, response = self.test_endpoint("Create Registration", "admin-registrations", 'POST', test_data, 201)
        
        registration_id = None
        if success and response:
            try:
                reg_data = response.json()
                registration_id = reg_data.get('id')
                print(f"   📝 Created registration ID: {registration_id}")
            except:
                pass
        
        # Test 4: Retrieve the created registration
        if registration_id:
            self.test_endpoint("Retrieve Registration", f"admin-registrations/{registration_id}")
        
        # Test 5: Test error handling
        self.test_endpoint("Invalid ID Error", "admin-registrations/invalid-id", expected_status=404)
        
        # Test 6: Template operations
        success, response = self.test_endpoint("Notes Templates Content", "notes-templates")
        if success and response:
            try:
                templates = response.json()
                template_count = len(templates)
                print(f"   📄 Found {template_count} notes templates")
            except:
                pass
        
        success, response = self.test_endpoint("Clinical Templates Content", "clinical-templates")
        if success and response:
            try:
                templates = response.json()
                template_count = len(templates)
                print(f"   📄 Found {template_count} clinical templates")
            except:
                pass
        
        # Cleanup - delete test registration
        if registration_id:
            self.test_endpoint("Delete Test Registration", f"admin-registrations/{registration_id}", 'DELETE', expected_status=200)
        
        # Final Results
        print()
        print("=" * 60)
        print("📊 BACKEND VERIFICATION RESULTS")
        print("=" * 60)
        print(f"Tests Passed: {self.tests_passed}/{self.tests_total}")
        print(f"Success Rate: {(self.tests_passed/self.tests_total)*100:.1f}%")
        
        if self.tests_passed == self.tests_total:
            print("🎉 ALL TESTS PASSED - Backend is fully functional")
            print("✅ Labels button changes did not affect backend functionality")
            return True
        else:
            print("⚠️  SOME TESTS FAILED - Backend issues detected")
            return False

if __name__ == "__main__":
    tester = QuickBackendTest()
    success = tester.run_tests()
    sys.exit(0 if success else 1)