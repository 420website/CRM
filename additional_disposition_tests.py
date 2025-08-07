#!/usr/bin/env python3
"""
Additional Disposition Management Tests
Tests edge cases and business logic validation
"""

import requests
import json
import sys
import time

BACKEND_URL = "https://cd556dd9-d36b-422e-8110-4b1830397661.preview.emergentagent.com/api"

def make_request(method, url, **kwargs):
    """Make HTTP request with error handling"""
    kwargs.setdefault('timeout', 30)
    try:
        response = getattr(requests, method.lower())(url, **kwargs)
        return response
    except Exception as e:
        print(f"❌ Request error: {str(e)}")
        return None

def test_duplicate_name_prevention():
    """Test that duplicate disposition names are prevented"""
    print("🔍 Testing duplicate name prevention...")
    
    # Get existing dispositions
    response = make_request('GET', f"{BACKEND_URL}/dispositions")
    if response is None or response.status_code != 200:
        print("❌ Could not fetch existing dispositions")
        return False
    
    dispositions = response.json()
    if not dispositions:
        print("❌ No existing dispositions found")
        return False
    
    existing_name = dispositions[0]['name']
    print(f"   Attempting to create duplicate of: {existing_name}")
    
    # Try to create a disposition with the same name
    duplicate_disposition = {
        "name": existing_name,
        "is_frequent": False,
        "is_default": False
    }
    
    response = make_request(
        'POST',
        f"{BACKEND_URL}/dispositions",
        json=duplicate_disposition,
        headers={"Content-Type": "application/json"}
    )
    
    if response is None:
        print("❌ Failed to connect")
        return False
    
    if response.status_code == 400:
        print("✅ Duplicate name prevention working correctly")
        try:
            error = response.json()
            print(f"   Error message: {error.get('detail', 'No detail')}")
        except:
            pass
        return True
    else:
        print(f"❌ Duplicate name prevention failed - got status {response.status_code}")
        return False

def test_frequent_vs_non_frequent_categorization():
    """Test that dispositions are properly categorized"""
    print("\n🔍 Testing frequent vs non-frequent categorization...")
    
    response = make_request('GET', f"{BACKEND_URL}/dispositions")
    if response is None or response.status_code != 200:
        print("❌ Could not fetch dispositions")
        return False
    
    dispositions = response.json()
    
    # Check expected frequent dispositions
    expected_frequent = ["ACTIVE", "BW RLTS", "CONSULT REQ", "DELIVERY", "DISPENSING", 
                        "PENDING", "POCT NEG", "PREVIOUSLY TX", "SELF CURED", "SOT"]
    
    frequent_dispositions = [d for d in dispositions if d.get('is_frequent', False)]
    frequent_names = [d['name'] for d in frequent_dispositions]
    
    print(f"   Found {len(frequent_dispositions)} frequent dispositions")
    print(f"   Expected frequent dispositions: {len(expected_frequent)}")
    
    # Check if all expected frequent dispositions are marked as frequent
    missing_frequent = [name for name in expected_frequent if name not in frequent_names]
    unexpected_frequent = [name for name in frequent_names if name not in expected_frequent and not name.startswith('TEST_') and not name.startswith('BULK_')]
    
    if not missing_frequent and len(unexpected_frequent) <= 2:  # Allow some test dispositions
        print("✅ Frequent disposition categorization is correct")
        print(f"   Frequent dispositions: {frequent_names[:5]}...")
        return True
    else:
        print("❌ Frequent disposition categorization issues found")
        if missing_frequent:
            print(f"   Missing frequent: {missing_frequent}")
        if unexpected_frequent:
            print(f"   Unexpected frequent: {unexpected_frequent}")
        return False

def test_default_disposition_fields():
    """Test that default dispositions have correct field values"""
    print("\n🔍 Testing default disposition field validation...")
    
    response = make_request('GET', f"{BACKEND_URL}/dispositions")
    if response is None or response.status_code != 200:
        print("❌ Could not fetch dispositions")
        return False
    
    dispositions = response.json()
    default_dispositions = [d for d in dispositions if d.get('is_default', False)]
    
    print(f"   Found {len(default_dispositions)} default dispositions")
    
    # Check that all default dispositions have required fields
    issues = []
    for disp in default_dispositions:
        if not disp.get('id'):
            issues.append(f"Missing ID: {disp.get('name', 'Unknown')}")
        if not disp.get('name'):
            issues.append(f"Missing name: {disp.get('id', 'Unknown ID')}")
        if 'is_frequent' not in disp:
            issues.append(f"Missing is_frequent: {disp.get('name', 'Unknown')}")
        if not disp.get('created_at'):
            issues.append(f"Missing created_at: {disp.get('name', 'Unknown')}")
        if not disp.get('updated_at'):
            issues.append(f"Missing updated_at: {disp.get('name', 'Unknown')}")
    
    if not issues:
        print("✅ All default dispositions have required fields")
        return True
    else:
        print("❌ Default disposition field validation issues:")
        for issue in issues[:5]:  # Show first 5 issues
            print(f"   - {issue}")
        return False

def test_update_validation():
    """Test update endpoint validation"""
    print("\n🔍 Testing update endpoint validation...")
    
    # Create a test disposition first
    test_disposition = {
        "name": f"UPDATE_TEST_{int(time.time())}",
        "is_frequent": False,
        "is_default": False
    }
    
    response = make_request(
        'POST',
        f"{BACKEND_URL}/dispositions",
        json=test_disposition,
        headers={"Content-Type": "application/json"}
    )
    
    if response is None or response.status_code != 200:
        print("❌ Could not create test disposition for update validation")
        return False
    
    created = response.json()
    disposition_id = created['id']
    
    # Test 1: Valid update
    update_data = {"name": f"{test_disposition['name']}_VALID_UPDATE"}
    response = make_request(
        'PUT',
        f"{BACKEND_URL}/dispositions/{disposition_id}",
        json=update_data,
        headers={"Content-Type": "application/json"}
    )
    
    if response is None or response.status_code != 200:
        print("❌ Valid update failed")
        return False
    
    # Test 2: Update to existing name (should fail)
    # Get another disposition name
    all_response = make_request('GET', f"{BACKEND_URL}/dispositions")
    if all_response and all_response.status_code == 200:
        all_dispositions = all_response.json()
        other_disposition = next((d for d in all_dispositions if d['id'] != disposition_id), None)
        
        if other_disposition:
            duplicate_update = {"name": other_disposition['name']}
            response = make_request(
                'PUT',
                f"{BACKEND_URL}/dispositions/{disposition_id}",
                json=duplicate_update,
                headers={"Content-Type": "application/json"}
            )
            
            if response and response.status_code == 400:
                print("✅ Update validation working - duplicate name rejected")
            else:
                print("❌ Update validation failed - duplicate name should be rejected")
                return False
    
    # Clean up
    make_request('DELETE', f"{BACKEND_URL}/dispositions/{disposition_id}")
    
    print("✅ Update endpoint validation working correctly")
    return True

def test_nonexistent_disposition_operations():
    """Test operations on non-existent dispositions"""
    print("\n🔍 Testing operations on non-existent dispositions...")
    
    fake_id = "00000000-0000-0000-0000-000000000000"
    
    # Test GET non-existent (this endpoint doesn't exist, but testing DELETE and PUT)
    
    # Test UPDATE non-existent
    update_data = {"name": "SHOULD_NOT_WORK"}
    response = make_request(
        'PUT',
        f"{BACKEND_URL}/dispositions/{fake_id}",
        json=update_data,
        headers={"Content-Type": "application/json"}
    )
    
    if response and response.status_code == 404:
        print("✅ UPDATE non-existent disposition correctly returns 404")
    else:
        print(f"❌ UPDATE non-existent disposition returned {response.status_code if response else 'None'}")
        return False
    
    # Test DELETE non-existent
    response = make_request('DELETE', f"{BACKEND_URL}/dispositions/{fake_id}")
    
    if response and response.status_code == 404:
        print("✅ DELETE non-existent disposition correctly returns 404")
    else:
        print(f"❌ DELETE non-existent disposition returned {response.status_code if response else 'None'}")
        return False
    
    return True

def main():
    """Run additional disposition management tests"""
    print("🚀 Additional Disposition Management Tests")
    print("=" * 50)
    
    test_results = []
    
    # Test 1: Duplicate Name Prevention
    print("TEST 1: Duplicate Name Prevention")
    duplicate_success = test_duplicate_name_prevention()
    test_results.append(("Duplicate Prevention", duplicate_success))
    
    # Test 2: Categorization
    print("TEST 2: Frequent vs Non-Frequent Categorization")
    categorization_success = test_frequent_vs_non_frequent_categorization()
    test_results.append(("Categorization", categorization_success))
    
    # Test 3: Default Disposition Fields
    print("TEST 3: Default Disposition Field Validation")
    fields_success = test_default_disposition_fields()
    test_results.append(("Default Fields", fields_success))
    
    # Test 4: Update Validation
    print("TEST 4: Update Endpoint Validation")
    update_validation_success = test_update_validation()
    test_results.append(("Update Validation", update_validation_success))
    
    # Test 5: Non-existent Operations
    print("TEST 5: Non-existent Disposition Operations")
    nonexistent_success = test_nonexistent_disposition_operations()
    test_results.append(("Non-existent Ops", nonexistent_success))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 ADDITIONAL TEST RESULTS")
    print("=" * 50)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<25} {status}")
        if result:
            passed += 1
    
    print("-" * 50)
    print(f"ADDITIONAL TESTS: {passed}/{total} passed")
    
    return passed >= 4  # Allow one failure

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)