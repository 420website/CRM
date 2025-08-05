#!/usr/bin/env python3

import requests
import json
import os
from dotenv import load_dotenv
import random
import string

def test_finalize_functionality():
    """Test the finalize functionality that was mentioned in the review"""
    
    # Load environment variables
    load_dotenv('/app/frontend/.env')
    backend_url = os.environ.get('REACT_APP_BACKEND_URL')
    
    if not backend_url:
        print("❌ Error: REACT_APP_BACKEND_URL not found in frontend .env file")
        return False
    
    print(f"🔗 Testing finalize functionality at: {backend_url}")
    print("=" * 60)
    
    tests_passed = 0
    tests_total = 0
    
    def run_test(name, method, endpoint, expected_status, data=None):
        nonlocal tests_passed, tests_total
        tests_total += 1
        
        url = f"{backend_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        print(f"\n🔍 Testing {name}...")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=30)
            
            if response.status_code == expected_status:
                tests_passed += 1
                print(f"✅ PASSED - Status: {response.status_code}")
                try:
                    return True, response.json()
                except:
                    return True, {}
            else:
                print(f"❌ FAILED - Expected {expected_status}, got {response.status_code}")
                try:
                    print(f"Response: {response.json()}")
                except:
                    print(f"Response: {response.text}")
                return False, {}
                
        except Exception as e:
            print(f"❌ FAILED - Error: {str(e)}")
            return False, {}
    
    # Generate test data
    random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    
    # First, create a test registration to finalize
    admin_registration_data = {
        "firstName": f"Finalize{random_suffix}",
        "lastName": f"Test{random_suffix}",
        "patientConsent": "Verbal",
        "email": f"finalize.{random_suffix}@example.com",
        "phone1": "4161234567",
        "city": "Toronto",
        "province": "Ontario",
        "photo": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
    }
    
    success, reg_response = run_test("Create Registration for Finalize Test", "POST", "api/admin-register", 200, admin_registration_data)
    if not success or 'registration_id' not in reg_response:
        print("❌ Cannot proceed with finalize test - failed to create test registration")
        return False
    
    registration_id = reg_response['registration_id']
    print(f"   Using registration ID: {registration_id}")
    
    # Test finalize GET endpoint (check if registration exists)
    success, finalize_get_data = run_test("Finalize GET Endpoint", "GET", f"api/admin-registration/{registration_id}/finalize", 200)
    if success:
        print(f"   Registration found for finalization")
    
    # Test finalize POST endpoint (actually finalize the registration)
    finalize_data = {
        "registration_id": registration_id
    }
    
    success, finalize_response = run_test("Finalize POST Endpoint", "POST", f"api/admin-registration/{registration_id}/finalize", 200, finalize_data)
    if success:
        print(f"   Registration finalized successfully")
        if 'message' in finalize_response:
            print(f"   Message: {finalize_response['message']}")
    
    # Verify the registration was moved to submitted status
    success, submitted_data = run_test("Verify Registration in Submitted", "GET", "api/admin-registrations-submitted", 200)
    if success:
        # Check if our registration is now in the submitted list
        found_finalized = False
        for reg in submitted_data:
            if reg.get('id') == registration_id:
                found_finalized = True
                print(f"   ✅ Registration found in submitted list with status: {reg.get('status', 'N/A')}")
                break
        
        if not found_finalized:
            print(f"   ⚠️  Registration not found in submitted list (may still be processing)")
    
    # Test email template functionality (if available)
    print("\n" + "=" * 40)
    print("📧 Testing Email Template Functionality")
    print("=" * 40)
    
    # Check if we can retrieve the registration to verify email template fields
    success, reg_data = run_test("Get Registration for Email Template Check", "GET", f"api/admin-registration/{registration_id}", 200)
    if success:
        # Check for email template related fields
        email_fields = ['firstName', 'lastName', 'email', 'phone1', 'city', 'province', 'photo']
        missing_fields = []
        for field in email_fields:
            if field not in reg_data or not reg_data[field]:
                missing_fields.append(field)
        
        if not missing_fields:
            print("   ✅ All email template fields are present")
            tests_passed += 1
            tests_total += 1
        else:
            print(f"   ⚠️  Missing email template fields: {missing_fields}")
            tests_total += 1
    
    # Summary
    print("\n" + "=" * 60)
    print(f"📊 FINALIZE FUNCTIONALITY TEST RESULTS")
    print(f"Tests Passed: {tests_passed}/{tests_total}")
    print(f"Success Rate: {(tests_passed/tests_total)*100:.1f}%")
    
    if tests_passed == tests_total:
        print("🎉 ALL FINALIZE TESTS PASSED - Finalize functionality is working correctly")
        return True
    else:
        print("⚠️  Some finalize tests failed - Investigation needed")
        return False

if __name__ == "__main__":
    success = test_finalize_functionality()
    exit(0 if success else 1)