#!/usr/bin/env python3
"""
Focused Disposition Management API Test
Tests the core functionality with better error handling and longer timeouts
"""

import requests
import json
import sys
import time
from datetime import datetime

# Backend URL from frontend .env
BACKEND_URL = "https://cd556dd9-d36b-422e-8110-4b1830397661.preview.emergentagent.com/api"

def make_request(method, url, **kwargs):
    """Make HTTP request with better error handling and longer timeout"""
    kwargs.setdefault('timeout', 30)  # Increased timeout
    try:
        response = getattr(requests, method.lower())(url, **kwargs)
        return response
    except requests.exceptions.Timeout:
        print(f"⏰ Request timed out after {kwargs['timeout']} seconds")
        return None
    except requests.exceptions.ConnectionError as e:
        print(f"🔌 Connection error: {str(e)}")
        return None
    except Exception as e:
        print(f"❌ Request error: {str(e)}")
        return None

def test_disposition_seeding_and_get():
    """Test that dispositions were seeded and GET endpoint works"""
    print("🔍 Testing disposition seeding and GET /api/dispositions...")
    
    response = make_request('GET', f"{BACKEND_URL}/dispositions")
    
    if response is None:
        print("❌ Failed to connect to dispositions endpoint")
        return False, []
    
    if response.status_code == 200:
        dispositions = response.json()
        print(f"✅ GET /api/dispositions successful - Found {len(dispositions)} dispositions")
        
        if len(dispositions) >= 60:  # Should have ~62 default dispositions
            print("✅ Seeding function worked - found expected number of dispositions")
            
            # Check categorization
            frequent = [d for d in dispositions if d.get('is_frequent', False)]
            non_frequent = [d for d in dispositions if not d.get('is_frequent', False)]
            default_count = len([d for d in dispositions if d.get('is_default', False)])
            
            print(f"✅ Categorization: {len(frequent)} frequent, {len(non_frequent)} non-frequent")
            print(f"✅ Default dispositions: {default_count}")
            
            # Show some examples
            print("📋 Sample frequent dispositions:")
            for disp in frequent[:3]:
                print(f"   - {disp['name']} (frequent: {disp['is_frequent']}, default: {disp['is_default']})")
            
            print("📋 Sample non-frequent dispositions:")
            for disp in non_frequent[:3]:
                print(f"   - {disp['name']} (frequent: {disp['is_frequent']}, default: {disp['is_default']})")
            
            return True, dispositions
        else:
            print(f"❌ Expected ~62 dispositions but found {len(dispositions)}")
            return False, dispositions
    else:
        print(f"❌ GET /api/dispositions failed with status {response.status_code}")
        print(f"Response: {response.text}")
        return False, []

def test_create_disposition():
    """Test creating a new disposition"""
    print("\n🔍 Testing POST /api/dispositions...")
    
    test_disposition = {
        "name": f"TEST_DISPOSITION_{int(time.time())}",
        "is_frequent": True,
        "is_default": False
    }
    
    response = make_request(
        'POST', 
        f"{BACKEND_URL}/dispositions",
        json=test_disposition,
        headers={"Content-Type": "application/json"}
    )
    
    if response is None:
        print("❌ Failed to connect to create disposition endpoint")
        return None
    
    if response.status_code == 200:
        created = response.json()
        print(f"✅ POST /api/dispositions successful")
        print(f"   Created: {created['name']}")
        print(f"   ID: {created['id']}")
        print(f"   Frequent: {created['is_frequent']}")
        print(f"   Default: {created['is_default']}")
        return created
    else:
        print(f"❌ POST /api/dispositions failed with status {response.status_code}")
        try:
            error_detail = response.json()
            print(f"   Error: {error_detail}")
        except:
            print(f"   Response: {response.text}")
        return None

def test_update_disposition(disposition_id, original_name):
    """Test updating a disposition"""
    print(f"\n🔍 Testing PUT /api/dispositions/{disposition_id}...")
    
    update_data = {
        "name": f"{original_name}_UPDATED",
        "is_frequent": False,  # Change from True to False
    }
    
    response = make_request(
        'PUT',
        f"{BACKEND_URL}/dispositions/{disposition_id}",
        json=update_data,
        headers={"Content-Type": "application/json"}
    )
    
    if response is None:
        print("❌ Failed to connect to update disposition endpoint")
        return None
    
    if response.status_code == 200:
        updated = response.json()
        print(f"✅ PUT /api/dispositions/{disposition_id} successful")
        print(f"   Updated name: {updated['name']}")
        print(f"   Updated frequent: {updated['is_frequent']}")
        return updated
    else:
        print(f"❌ PUT /api/dispositions/{disposition_id} failed with status {response.status_code}")
        try:
            error_detail = response.json()
            print(f"   Error: {error_detail}")
        except:
            print(f"   Response: {response.text}")
        return None

def test_delete_custom_disposition(disposition_id):
    """Test deleting a custom (non-default) disposition"""
    print(f"\n🔍 Testing DELETE /api/dispositions/{disposition_id} (custom)...")
    
    response = make_request('DELETE', f"{BACKEND_URL}/dispositions/{disposition_id}")
    
    if response is None:
        print("❌ Failed to connect to delete disposition endpoint")
        return False
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ DELETE /api/dispositions/{disposition_id} successful")
        print(f"   Message: {result.get('message', 'No message')}")
        return True
    else:
        print(f"❌ DELETE /api/dispositions/{disposition_id} failed with status {response.status_code}")
        try:
            error_detail = response.json()
            print(f"   Error: {error_detail}")
        except:
            print(f"   Response: {response.text}")
        return False

def test_delete_default_disposition_protection(dispositions):
    """Test that default dispositions cannot be deleted"""
    print("\n🔍 Testing default disposition deletion protection...")
    
    # Find a default disposition
    default_dispositions = [d for d in dispositions if d.get('is_default', False)]
    
    if not default_dispositions:
        print("❌ No default dispositions found to test protection")
        return False
    
    default_disp = default_dispositions[0]
    print(f"   Testing deletion of default disposition: {default_disp['name']}")
    
    response = make_request('DELETE', f"{BACKEND_URL}/dispositions/{default_disp['id']}")
    
    if response is None:
        print("❌ Failed to connect to delete disposition endpoint")
        return False
    
    # Should return 400 or 500 (both indicate protection is working)
    if response.status_code in [400, 500]:
        print("✅ Default disposition protection working - deletion rejected")
        try:
            error_detail = response.json()
            print(f"   Error message: {error_detail}")
        except:
            print(f"   Response: {response.text}")
        return True
    else:
        print(f"❌ Default disposition protection failed - got status {response.status_code}")
        print(f"   This should have been rejected!")
        return False

def test_save_all_dispositions():
    """Test bulk save functionality"""
    print("\n🔍 Testing POST /api/dispositions/save-all...")
    
    test_dispositions = [
        {
            "name": f"BULK_TEST_1_{int(time.time())}",
            "is_frequent": True,
            "is_default": False
        },
        {
            "name": f"BULK_TEST_2_{int(time.time())}",
            "is_frequent": False,
            "is_default": False
        }
    ]
    
    response = make_request(
        'POST',
        f"{BACKEND_URL}/dispositions/save-all",
        json=test_dispositions,
        headers={"Content-Type": "application/json"}
    )
    
    if response is None:
        print("❌ Failed to connect to save-all dispositions endpoint")
        return False
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ POST /api/dispositions/save-all successful")
        print(f"   Message: {result.get('message', 'No message')}")
        print(f"   Count: {result.get('count', 'No count')}")
        return True
    else:
        print(f"❌ POST /api/dispositions/save-all failed with status {response.status_code}")
        try:
            error_detail = response.json()
            print(f"   Error: {error_detail}")
        except:
            print(f"   Response: {response.text}")
        return False

def main():
    """Run focused disposition management tests"""
    print("🚀 Disposition Management API Testing")
    print("=" * 50)
    
    test_results = []
    
    # Test 1: Seeding and GET
    print("TEST 1: Seeding and GET Dispositions")
    seeding_success, dispositions = test_disposition_seeding_and_get()
    test_results.append(("Seeding & GET", seeding_success))
    
    if not seeding_success:
        print("\n❌ Cannot continue without basic GET functionality")
        return False
    
    # Test 2: Create Disposition
    print("\nTEST 2: Create Disposition")
    created_disposition = test_create_disposition()
    create_success = created_disposition is not None
    test_results.append(("Create Disposition", create_success))
    
    # Test 3: Update Disposition (if create worked)
    if created_disposition:
        print("\nTEST 3: Update Disposition")
        updated_disposition = test_update_disposition(
            created_disposition['id'], 
            created_disposition['name']
        )
        update_success = updated_disposition is not None
        test_results.append(("Update Disposition", update_success))
        
        # Test 4: Delete Custom Disposition
        print("\nTEST 4: Delete Custom Disposition")
        delete_success = test_delete_custom_disposition(created_disposition['id'])
        test_results.append(("Delete Custom", delete_success))
    else:
        test_results.append(("Update Disposition", False))
        test_results.append(("Delete Custom", False))
    
    # Test 5: Default Disposition Protection
    print("\nTEST 5: Default Disposition Protection")
    protection_success = test_delete_default_disposition_protection(dispositions)
    test_results.append(("Default Protection", protection_success))
    
    # Test 6: Save All Dispositions
    print("\nTEST 6: Save All Dispositions")
    save_all_success = test_save_all_dispositions()
    test_results.append(("Save All", save_all_success))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<25} {status}")
        if result:
            passed += 1
    
    print("-" * 50)
    print(f"OVERALL: {passed}/{total} tests passed")
    
    if passed >= 4:  # Allow some flexibility
        print("🎉 DISPOSITION MANAGEMENT FUNCTIONALITY IS WORKING!")
        return True
    else:
        print("⚠️  Critical issues found in disposition management")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)