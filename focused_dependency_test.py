#!/usr/bin/env python3
"""
Focused Backend Dependency Test
Tests core backend functionality after dependency version changes
"""

import requests
import json
import sys
import os
from datetime import datetime, date
import random
import string
from dotenv import load_dotenv

def test_backend_dependencies():
    """Test backend with new dependency versions"""
    
    # Load environment variables
    load_dotenv('/app/frontend/.env')
    backend_url = os.environ.get('REACT_APP_BACKEND_URL')
    
    if not backend_url:
        print("❌ Error: REACT_APP_BACKEND_URL not found")
        return False
    
    print("🚀 Testing Backend with New Dependencies")
    print(f"🔗 Backend URL: {backend_url}")
    print("📦 Dependency versions:")
    print("   - annotated-types==0.6.0 (downgraded from 0.7.0)")
    print("   - pydantic==2.7.4 (downgraded)")
    print("   - fastapi==0.115.0 (maintained)")
    print("   - uvicorn==0.30.6 (maintained)")
    print("=" * 60)
    
    tests_passed = 0
    tests_total = 0
    
    def test_endpoint(name, method, endpoint, data=None, expected_status=200):
        nonlocal tests_passed, tests_total
        tests_total += 1
        
        url = f"{backend_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=10)
            else:
                print(f"❌ {name}: Unsupported method {method}")
                return False
                
            success = response.status_code == expected_status
            
            if success:
                tests_passed += 1
                print(f"✅ {name}: Status {response.status_code}")
                return True
            else:
                print(f"❌ {name}: Expected {expected_status}, got {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ {name}: Request failed - {str(e)}")
            return False
    
    # Test 1: FastAPI/Pydantic Model Validation
    print("\n🔍 Testing FastAPI/Pydantic Compatibility...")
    
    # Basic endpoint test
    test_endpoint("Notes Templates Endpoint", "GET", "api/notes-templates")
    test_endpoint("Clinical Templates Endpoint", "GET", "api/clinical-templates")
    
    # Test 2: Pydantic Model Creation and Validation
    print("\n🔍 Testing Pydantic Model Validation...")
    
    # Generate test data
    random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    admin_data = {
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
    }
    
    # Test admin registration (Pydantic model validation)
    success = test_endpoint("Admin Registration (Pydantic Model)", "POST", "api/admin-register", admin_data)
    
    # Test validation error handling
    invalid_data = admin_data.copy()
    invalid_data.pop("firstName")  # Remove required field
    test_endpoint("Pydantic Validation Error", "POST", "api/admin-register", invalid_data, 422)
    
    # Test 3: Database Operations
    print("\n🔍 Testing Database Operations...")
    
    test_endpoint("Admin Registrations Pending", "GET", "api/admin-registrations-pending")
    test_endpoint("Admin Registrations Submitted", "GET", "api/admin-registrations-submitted")
    
    # Test 4: Template Operations
    print("\n🔍 Testing Template Operations...")
    
    template_data = {
        "name": f"Test Template {random_suffix}",
        "content": f"Test content {random_suffix}",
        "is_default": False
    }
    
    test_endpoint("Create Notes Template", "POST", "api/notes-templates", template_data)
    test_endpoint("Create Clinical Template", "POST", "api/clinical-templates", template_data)
    
    # Test 5: Error Handling
    print("\n🔍 Testing Error Handling...")
    
    test_endpoint("404 Error Handling", "GET", "api/nonexistent-endpoint", expected_status=404)
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 DEPENDENCY COMPATIBILITY TEST RESULTS")
    print("=" * 60)
    print(f"Tests Passed: {tests_passed}/{tests_total}")
    print(f"Success Rate: {(tests_passed/tests_total*100):.1f}%")
    
    if tests_passed == tests_total:
        print("\n✅ ALL TESTS PASSED!")
        print("🎉 Backend is working correctly with new dependency versions!")
        print("\n📋 Key Findings:")
        print("   ✅ FastAPI 0.115.0 is working correctly")
        print("   ✅ Pydantic 2.7.4 model validation is working")
        print("   ✅ annotated-types 0.6.0 is compatible")
        print("   ✅ Database operations are functional")
        print("   ✅ Template operations are working")
        print("   ✅ Error handling is proper")
        return True
    else:
        print(f"\n❌ {tests_total - tests_passed} TESTS FAILED")
        print("⚠️  Some functionality may have issues with new dependency versions")
        return False

if __name__ == "__main__":
    success = test_backend_dependencies()
    sys.exit(0 if success else 1)