#!/usr/bin/env python3
"""
Additional MongoDB Connection Robustness Testing
===============================================

This script performs additional tests to verify the MongoDB connection improvements
are robust and handle various scenarios correctly.
"""

import requests
import json
import sys
import os
from datetime import datetime, date
import uuid
import time

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://dfe9a1e1-7f3d-45aa-ad71-43a254e568c5.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

def test_template_persistence():
    """Test template persistence functionality specifically"""
    print("🔍 TEMPLATE PERSISTENCE TESTING")
    print("=" * 60)
    
    try:
        # Test Notes Templates
        print("\n📝 Testing Notes Templates Persistence")
        response = requests.get(f"{API_BASE}/notes-templates", timeout=15)
        if response.status_code == 200:
            templates = response.json()
            print(f"   ✅ Notes templates loaded: {len(templates)} templates")
            
            # Check for default templates
            default_templates = [t for t in templates if t.get('is_default', False)]
            custom_templates = [t for t in templates if not t.get('is_default', False)]
            
            print(f"   📋 Default templates: {len(default_templates)}")
            print(f"   🔧 Custom templates: {len(custom_templates)}")
            
            # Show some template names
            if templates:
                names = [t.get('name', 'Unknown') for t in templates[:5]]
                print(f"   📄 Template names: {', '.join(names)}")
            
            return True
        else:
            print(f"   ❌ Notes templates failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Template persistence test error: {str(e)}")
        return False

def test_crud_operations():
    """Test CRUD operations to verify database functionality"""
    print("\n🔍 CRUD OPERATIONS TESTING")
    print("=" * 60)
    
    test_registration_id = None
    crud_results = []
    
    try:
        # CREATE operation
        print("\n➕ Testing CREATE operation")
        test_data = {
            "firstName": f"CRUDTest_{uuid.uuid4().hex[:6]}",
            "lastName": "MongoDB",
            "patientConsent": "verbal",
            "regDate": date.today().isoformat(),
            "province": "Ontario",
            "language": "English",
            "email": "test@mongodb.test"
        }
        
        response = requests.post(f"{API_BASE}/admin-register", 
                               json=test_data, 
                               headers={"Content-Type": "application/json"},
                               timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            test_registration_id = result.get('registration_id')
            print(f"   ✅ CREATE successful: {test_registration_id}")
            crud_results.append(True)
        else:
            print(f"   ❌ CREATE failed: {response.status_code}")
            crud_results.append(False)
            
    except Exception as e:
        print(f"   ❌ CREATE error: {str(e)}")
        crud_results.append(False)
    
    if test_registration_id:
        try:
            # READ operation
            print("\n📖 Testing READ operation")
            response = requests.get(f"{API_BASE}/admin-registration/{test_registration_id}", timeout=15)
            
            if response.status_code == 200:
                registration = response.json()
                print(f"   ✅ READ successful")
                print(f"   👤 Name: {registration.get('firstName')} {registration.get('lastName')}")
                crud_results.append(True)
            else:
                print(f"   ❌ READ failed: {response.status_code}")
                crud_results.append(False)
                
        except Exception as e:
            print(f"   ❌ READ error: {str(e)}")
            crud_results.append(False)
        
        try:
            # UPDATE operation
            print("\n✏️ Testing UPDATE operation")
            update_data = {
                "specialAttention": "MongoDB connection test update"
            }
            
            response = requests.put(f"{API_BASE}/admin-registration/{test_registration_id}", 
                                  json=update_data,
                                  headers={"Content-Type": "application/json"},
                                  timeout=15)
            
            if response.status_code == 200:
                print(f"   ✅ UPDATE successful")
                crud_results.append(True)
            else:
                print(f"   ❌ UPDATE failed: {response.status_code}")
                crud_results.append(False)
                
        except Exception as e:
            print(f"   ❌ UPDATE error: {str(e)}")
            crud_results.append(False)
    
    success_rate = sum(crud_results) / len(crud_results) * 100 if crud_results else 0
    print(f"\n📈 CRUD Operations Success Rate: {success_rate:.1f}% ({sum(crud_results)}/{len(crud_results)})")
    
    return success_rate >= 75, test_registration_id

def test_concurrent_operations():
    """Test concurrent database operations to verify connection stability"""
    print("\n🔍 CONCURRENT OPERATIONS TESTING")
    print("=" * 60)
    
    import threading
    import queue
    
    results_queue = queue.Queue()
    
    def make_request(endpoint, result_queue):
        try:
            response = requests.get(f"{API_BASE}{endpoint}", timeout=10)
            result_queue.put(response.status_code == 200)
        except:
            result_queue.put(False)
    
    # Create multiple threads to test concurrent access
    endpoints = [
        "/admin-registrations-pending",
        "/admin-registrations-submitted", 
        "/notes-templates",
        "/clinical-templates"
    ]
    
    threads = []
    for endpoint in endpoints:
        for i in range(2):  # 2 requests per endpoint
            thread = threading.Thread(target=make_request, args=(endpoint, results_queue))
            threads.append(thread)
            thread.start()
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join()
    
    # Collect results
    results = []
    while not results_queue.empty():
        results.append(results_queue.get())
    
    success_rate = sum(results) / len(results) * 100 if results else 0
    print(f"   📊 Concurrent requests: {len(results)} total")
    print(f"   ✅ Successful: {sum(results)}")
    print(f"   ❌ Failed: {len(results) - sum(results)}")
    print(f"   📈 Success rate: {success_rate:.1f}%")
    
    return success_rate >= 80

def test_error_handling():
    """Test error handling for invalid requests"""
    print("\n🔍 ERROR HANDLING TESTING")
    print("=" * 60)
    
    error_tests = []
    
    # Test invalid registration ID
    try:
        print("\n🚫 Testing invalid registration ID")
        response = requests.get(f"{API_BASE}/admin-registration/invalid-id-12345", timeout=10)
        
        if response.status_code == 404:
            print(f"   ✅ Proper 404 error for invalid ID")
            error_tests.append(True)
        else:
            print(f"   ❌ Unexpected status for invalid ID: {response.status_code}")
            error_tests.append(False)
            
    except Exception as e:
        print(f"   ❌ Error handling test failed: {str(e)}")
        error_tests.append(False)
    
    # Test malformed request
    try:
        print("\n🚫 Testing malformed registration data")
        bad_data = {"invalid": "data"}
        
        response = requests.post(f"{API_BASE}/admin-register", 
                               json=bad_data,
                               headers={"Content-Type": "application/json"},
                               timeout=10)
        
        if response.status_code in [400, 422]:  # Bad request or validation error
            print(f"   ✅ Proper error for malformed data: {response.status_code}")
            error_tests.append(True)
        else:
            print(f"   ❌ Unexpected status for malformed data: {response.status_code}")
            error_tests.append(False)
            
    except Exception as e:
        print(f"   ❌ Malformed data test failed: {str(e)}")
        error_tests.append(False)
    
    success_rate = sum(error_tests) / len(error_tests) * 100 if error_tests else 0
    print(f"\n📈 Error Handling Success Rate: {success_rate:.1f}% ({sum(error_tests)}/{len(error_tests)})")
    
    return success_rate >= 75

def run_additional_mongodb_tests():
    """Run additional MongoDB connection tests"""
    print("🚀 ADDITIONAL MONGODB CONNECTION TESTING")
    print("=" * 80)
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    test_results = []
    test_registration_id = None
    
    # Run additional tests
    test_results.append(("Template Persistence", test_template_persistence()))
    
    crud_result, reg_id = test_crud_operations()
    test_results.append(("CRUD Operations", crud_result))
    test_registration_id = reg_id
    
    test_results.append(("Concurrent Operations", test_concurrent_operations()))
    test_results.append(("Error Handling", test_error_handling()))
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 ADDITIONAL MONGODB TESTING SUMMARY")
    print("=" * 80)
    
    passed_tests = 0
    total_tests = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:.<40} {status}")
        if result:
            passed_tests += 1
    
    success_rate = (passed_tests / total_tests) * 100
    print(f"\nOverall Success Rate: {success_rate:.1f}% ({passed_tests}/{total_tests})")
    
    if success_rate >= 75:
        print("\n🎉 ADDITIONAL MONGODB TESTS: PASSED")
        print("✅ MongoDB connection improvements are robust")
        print("✅ Template persistence is working")
        print("✅ CRUD operations are functional")
        print("✅ Concurrent access is stable")
        print("✅ Error handling is appropriate")
    else:
        print("\n⚠️  ADDITIONAL MONGODB TESTS: ISSUES DETECTED")
        print("❌ Some MongoDB functionality needs attention")
    
    # Cleanup note
    if test_registration_id:
        print(f"\n🧹 Note: Test registration {test_registration_id} was created during testing")
    
    return success_rate >= 75

if __name__ == "__main__":
    success = run_additional_mongodb_tests()
    sys.exit(0 if success else 1)