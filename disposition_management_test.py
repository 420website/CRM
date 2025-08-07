#!/usr/bin/env python3
"""
Comprehensive test suite for Disposition Management API endpoints
Tests all CRUD operations, seeding functionality, and business rules
"""

import requests
import json
import sys
import time
from datetime import datetime

# Backend URL from frontend .env
BACKEND_URL = "https://cd556dd9-d36b-422e-8110-4b1830397661.preview.emergentagent.com/api"

def test_server_health():
    """Test if the backend server is running"""
    print("🔍 Testing server health...")
    try:
        response = requests.get(f"{BACKEND_URL}/admin-registrations-pending", timeout=10)
        if response.status_code == 200:
            print("✅ Backend server is running and accessible")
            return True
        else:
            print(f"❌ Backend server returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend server is not accessible: {str(e)}")
        return False

def test_get_all_dispositions():
    """Test GET /api/dispositions endpoint"""
    print("\n🔍 Testing GET /api/dispositions...")
    try:
        response = requests.get(f"{BACKEND_URL}/dispositions", timeout=10)
        
        if response.status_code == 200:
            dispositions = response.json()
            print(f"✅ GET /api/dispositions successful - Found {len(dispositions)} dispositions")
            
            # Check if seeding worked - should have default dispositions
            if len(dispositions) > 0:
                print("✅ Database seeding appears to have worked - dispositions exist")
                
                # Check for frequent vs non-frequent categorization
                frequent_count = sum(1 for d in dispositions if d.get('is_frequent', False))
                non_frequent_count = len(dispositions) - frequent_count
                print(f"✅ Categorization working: {frequent_count} frequent, {non_frequent_count} non-frequent")
                
                # Check for default dispositions
                default_count = sum(1 for d in dispositions if d.get('is_default', False))
                print(f"✅ Default dispositions: {default_count} found")
                
                # Show some examples
                print("📋 Sample dispositions:")
                for i, disp in enumerate(dispositions[:5]):
                    freq_status = "frequent" if disp.get('is_frequent') else "non-frequent"
                    default_status = "default" if disp.get('is_default') else "custom"
                    print(f"   {i+1}. {disp['name']} ({freq_status}, {default_status})")
                
                return dispositions
            else:
                print("❌ No dispositions found - seeding may have failed")
                return []
        else:
            print(f"❌ GET /api/dispositions failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return []
            
    except Exception as e:
        print(f"❌ GET /api/dispositions error: {str(e)}")
        return []

def test_create_disposition():
    """Test POST /api/dispositions endpoint"""
    print("\n🔍 Testing POST /api/dispositions...")
    
    test_disposition = {
        "name": "TEST_DISPOSITION_" + str(int(time.time())),
        "is_frequent": True,
        "is_default": False
    }
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/dispositions",
            json=test_disposition,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            created_disposition = response.json()
            print(f"✅ POST /api/dispositions successful - Created: {created_disposition['name']}")
            print(f"   ID: {created_disposition['id']}")
            print(f"   Frequent: {created_disposition['is_frequent']}")
            print(f"   Default: {created_disposition['is_default']}")
            return created_disposition
        else:
            print(f"❌ POST /api/dispositions failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ POST /api/dispositions error: {str(e)}")
        return None

def test_update_disposition(disposition_id, original_name):
    """Test PUT /api/dispositions/{disposition_id} endpoint"""
    print(f"\n🔍 Testing PUT /api/dispositions/{disposition_id}...")
    
    update_data = {
        "name": original_name + "_UPDATED",
        "is_frequent": False,  # Change from True to False
        "is_default": False
    }
    
    try:
        response = requests.put(
            f"{BACKEND_URL}/dispositions/{disposition_id}",
            json=update_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            updated_disposition = response.json()
            print(f"✅ PUT /api/dispositions/{disposition_id} successful")
            print(f"   Updated name: {updated_disposition['name']}")
            print(f"   Updated frequent: {updated_disposition['is_frequent']}")
            return updated_disposition
        else:
            print(f"❌ PUT /api/dispositions/{disposition_id} failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ PUT /api/dispositions/{disposition_id} error: {str(e)}")
        return None

def test_delete_disposition(disposition_id, is_default=False):
    """Test DELETE /api/dispositions/{disposition_id} endpoint"""
    print(f"\n🔍 Testing DELETE /api/dispositions/{disposition_id}...")
    
    try:
        response = requests.delete(f"{BACKEND_URL}/dispositions/{disposition_id}", timeout=10)
        
        if is_default:
            # Should fail for default dispositions
            if response.status_code == 400:
                print("✅ DELETE correctly rejected for default disposition")
                return True
            else:
                print(f"❌ DELETE should have failed for default disposition but got status {response.status_code}")
                return False
        else:
            # Should succeed for non-default dispositions
            if response.status_code == 200:
                result = response.json()
                print(f"✅ DELETE /api/dispositions/{disposition_id} successful")
                print(f"   Message: {result.get('message', 'No message')}")
                return True
            else:
                print(f"❌ DELETE /api/dispositions/{disposition_id} failed with status {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ DELETE /api/dispositions/{disposition_id} error: {str(e)}")
        return False

def test_save_all_dispositions():
    """Test POST /api/dispositions/save-all endpoint"""
    print("\n🔍 Testing POST /api/dispositions/save-all...")
    
    test_dispositions = [
        {
            "name": "BULK_TEST_1_" + str(int(time.time())),
            "is_frequent": True,
            "is_default": False
        },
        {
            "name": "BULK_TEST_2_" + str(int(time.time())),
            "is_frequent": False,
            "is_default": False
        }
    ]
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/dispositions/save-all",
            json=test_dispositions,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ POST /api/dispositions/save-all successful")
            print(f"   Message: {result.get('message', 'No message')}")
            print(f"   Count: {result.get('count', 'No count')}")
            return True
        else:
            print(f"❌ POST /api/dispositions/save-all failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ POST /api/dispositions/save-all error: {str(e)}")
        return False

def test_default_disposition_protection():
    """Test that default dispositions cannot be deleted"""
    print("\n🔍 Testing default disposition protection...")
    
    # Get all dispositions to find a default one
    try:
        response = requests.get(f"{BACKEND_URL}/dispositions", timeout=10)
        if response.status_code == 200:
            dispositions = response.json()
            default_dispositions = [d for d in dispositions if d.get('is_default', False)]
            
            if default_dispositions:
                default_disp = default_dispositions[0]
                print(f"   Testing deletion of default disposition: {default_disp['name']}")
                return test_delete_disposition(default_disp['id'], is_default=True)
            else:
                print("❌ No default dispositions found to test protection")
                return False
        else:
            print("❌ Could not fetch dispositions to test default protection")
            return False
            
    except Exception as e:
        print(f"❌ Error testing default disposition protection: {str(e)}")
        return False

def test_duplicate_name_prevention():
    """Test that duplicate disposition names are prevented"""
    print("\n🔍 Testing duplicate name prevention...")
    
    # First, get existing dispositions to find a name that already exists
    try:
        response = requests.get(f"{BACKEND_URL}/dispositions", timeout=10)
        if response.status_code == 200:
            dispositions = response.json()
            if dispositions:
                existing_name = dispositions[0]['name']
                
                # Try to create a disposition with the same name
                duplicate_disposition = {
                    "name": existing_name,
                    "is_frequent": False,
                    "is_default": False
                }
                
                response = requests.post(
                    f"{BACKEND_URL}/dispositions",
                    json=duplicate_disposition,
                    headers={"Content-Type": "application/json"},
                    timeout=10
                )
                
                if response.status_code == 400:
                    print(f"✅ Duplicate name prevention working - rejected duplicate: {existing_name}")
                    return True
                else:
                    print(f"❌ Duplicate name prevention failed - should have rejected duplicate: {existing_name}")
                    return False
            else:
                print("❌ No existing dispositions to test duplicate prevention")
                return False
        else:
            print("❌ Could not fetch dispositions to test duplicate prevention")
            return False
            
    except Exception as e:
        print(f"❌ Error testing duplicate name prevention: {str(e)}")
        return False

def main():
    """Run all disposition management tests"""
    print("🚀 Starting Disposition Management API Tests")
    print("=" * 60)
    
    # Track test results
    test_results = {
        "server_health": False,
        "get_dispositions": False,
        "create_disposition": False,
        "update_disposition": False,
        "delete_disposition": False,
        "save_all_dispositions": False,
        "default_protection": False,
        "duplicate_prevention": False
    }
    
    # Test 1: Server Health
    test_results["server_health"] = test_server_health()
    if not test_results["server_health"]:
        print("\n❌ Server is not accessible. Cannot continue with tests.")
        return
    
    # Test 2: Get All Dispositions (includes seeding verification)
    dispositions = test_get_all_dispositions()
    test_results["get_dispositions"] = len(dispositions) > 0
    
    # Test 3: Create Disposition
    created_disposition = test_create_disposition()
    test_results["create_disposition"] = created_disposition is not None
    
    # Test 4: Update Disposition (if create succeeded)
    if created_disposition:
        updated_disposition = test_update_disposition(
            created_disposition['id'], 
            created_disposition['name']
        )
        test_results["update_disposition"] = updated_disposition is not None
        
        # Test 5: Delete Disposition (if create succeeded)
        test_results["delete_disposition"] = test_delete_disposition(created_disposition['id'])
    
    # Test 6: Save All Dispositions
    test_results["save_all_dispositions"] = test_save_all_dispositions()
    
    # Test 7: Default Disposition Protection
    test_results["default_protection"] = test_default_disposition_protection()
    
    # Test 8: Duplicate Name Prevention
    test_results["duplicate_prevention"] = test_duplicate_name_prevention()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    passed_tests = 0
    total_tests = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name.replace('_', ' ').title():<30} {status}")
        if result:
            passed_tests += 1
    
    print("-" * 60)
    print(f"OVERALL RESULT: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 ALL DISPOSITION MANAGEMENT TESTS PASSED!")
        return True
    else:
        print(f"⚠️  {total_tests - passed_tests} test(s) failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)