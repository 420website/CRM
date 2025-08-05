#!/usr/bin/env python3

import requests
import json
import os
from dotenv import load_dotenv
import random
import string
from datetime import date

def test_backend_core_functionality():
    """Test core backend functionality after frontend copy button changes"""
    
    # Load environment variables
    load_dotenv('/app/frontend/.env')
    backend_url = os.environ.get('REACT_APP_BACKEND_URL')
    
    if not backend_url:
        print("❌ Error: REACT_APP_BACKEND_URL not found in frontend .env file")
        return False
    
    print(f"🔗 Testing backend at: {backend_url}")
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
    
    # Test 1: API Health Check
    success, _ = run_test("API Health Check", "GET", "api", 200)
    
    # Test 2: Admin Registration Endpoints
    success, pending_data = run_test("Admin Registrations Pending", "GET", "api/admin-registrations-pending", 200)
    if success:
        print(f"   Found {len(pending_data)} pending registrations")
    
    success, submitted_data = run_test("Admin Registrations Submitted", "GET", "api/admin-registrations-submitted", 200)
    if success:
        print(f"   Found {len(submitted_data)} submitted registrations")
    
    # Test 3: Template Endpoints
    success, notes_templates = run_test("Notes Templates", "GET", "api/notes-templates", 200)
    if success:
        print(f"   Found {len(notes_templates)} notes templates")
    
    success, clinical_templates = run_test("Clinical Templates", "GET", "api/clinical-templates", 200)
    if success:
        print(f"   Found {len(clinical_templates)} clinical templates")
    
    # Test 4: Create Admin Registration
    admin_registration_data = {
        "firstName": f"Test{random_suffix}",
        "lastName": f"User{random_suffix}",
        "patientConsent": "Verbal",
        "email": f"test.{random_suffix}@example.com",
        "phone1": "4161234567",
        "city": "Toronto",
        "province": "Ontario"
    }
    
    success, reg_response = run_test("Create Admin Registration", "POST", "api/admin-register", 200, admin_registration_data)
    registration_id = None
    if success and 'registration_id' in reg_response:
        registration_id = reg_response['registration_id']
        print(f"   Created registration with ID: {registration_id}")
    
    # Test 5: Registration Retrieval (if we created one)
    if registration_id:
        success, reg_data = run_test("Get Registration by ID", "GET", f"api/admin-registration/{registration_id}", 200)
        if success:
            print(f"   Retrieved registration for: {reg_data.get('firstName', 'N/A')} {reg_data.get('lastName', 'N/A')}")
    
    # Test 6: Contact Form
    contact_data = {
        "name": f"Contact Test {random_suffix}",
        "email": f"contact.{random_suffix}@example.com",
        "subject": "Backend Test Contact",
        "message": "This is a test message to verify contact form functionality after frontend copy button changes."
    }
    
    success, contact_response = run_test("Contact Form Submission", "POST", "api/contact", 200, contact_data)
    if success:
        print(f"   Contact message submitted successfully")
    
    # Test 7: User Registration (public endpoint)
    user_registration_data = {
        "full_name": f"Public User {random_suffix}",
        "date_of_birth": str(date(1990, 5, 15)),
        "phone_number": "4161234567",
        "email": f"public.{random_suffix}@example.com",
        "consent_given": True
    }
    
    success, user_response = run_test("Public User Registration", "POST", "api/register", 200, user_registration_data)
    if success:
        print(f"   Public registration created successfully")
    
    # Summary
    print("\n" + "=" * 60)
    print(f"📊 BACKEND TEST RESULTS")
    print(f"Tests Passed: {tests_passed}/{tests_total}")
    print(f"Success Rate: {(tests_passed/tests_total)*100:.1f}%")
    
    if tests_passed == tests_total:
        print("🎉 ALL BACKEND TESTS PASSED - No issues found after frontend copy button changes")
        return True
    else:
        print("⚠️  Some backend tests failed - Investigation needed")
        return False

if __name__ == "__main__":
    success = test_backend_core_functionality()
    exit(0 if success else 1)