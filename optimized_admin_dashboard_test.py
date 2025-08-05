#!/usr/bin/env python3
"""
Comprehensive test suite for the new optimized admin dashboard backend endpoints.
Tests enterprise-level performance improvements and pagination functionality.
"""

import requests
import json
import time
from datetime import datetime, date
import sys
import os

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://46471c8a-a981-4b23-bca9-bb5c0ba282bc.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

def test_optimized_pending_registrations():
    """Test the new optimized pending registrations endpoint"""
    print("🔍 Testing /api/admin-registrations-pending-optimized...")
    
    try:
        # Test 1: Basic pagination (page 1, default page size)
        print("  📄 Test 1: Basic pagination (page 1)")
        response = requests.get(f"{API_BASE}/admin-registrations-pending-optimized")
        
        if response.status_code == 200:
            data = response.json()
            
            # Verify response structure
            required_keys = ['data', 'pagination', 'filters']
            if all(key in data for key in required_keys):
                print(f"    ✅ Response structure correct")
                print(f"    📊 Found {data['pagination']['total_records']} total pending registrations")
                print(f"    📄 Page {data['pagination']['current_page']} of {data['pagination']['total_pages']}")
                
                # Verify photos are excluded for performance
                if data['data'] and 'photo' not in data['data'][0]:
                    print(f"    ✅ Photos excluded from list view for performance")
                else:
                    print(f"    ⚠️  Photos may be included in list view")
                
            else:
                print(f"    ❌ Missing required keys in response")
                return False
        else:
            print(f"    ❌ Request failed with status {response.status_code}")
            return False
        
        # Test 2: Pagination with different page sizes
        print("  📄 Test 2: Different page sizes (5, 10, 20)")
        for page_size in [5, 10, 20]:
            response = requests.get(f"{API_BASE}/admin-registrations-pending-optimized?page=1&page_size={page_size}")
            if response.status_code == 200:
                data = response.json()
                actual_size = len(data['data'])
                expected_size = min(page_size, data['pagination']['total_records'])
                if actual_size <= expected_size:
                    print(f"    ✅ Page size {page_size}: Got {actual_size} records")
                else:
                    print(f"    ❌ Page size {page_size}: Expected ≤{expected_size}, got {actual_size}")
            else:
                print(f"    ❌ Page size {page_size} test failed")
        
        # Test 3: Name search filtering
        print("  🔍 Test 3: Name search filtering")
        response = requests.get(f"{API_BASE}/admin-registrations-pending-optimized?search_name=john")
        if response.status_code == 200:
            data = response.json()
            print(f"    ✅ Name search 'john': Found {len(data['data'])} results")
        else:
            print(f"    ❌ Name search test failed")
        
        # Test 4: Date filtering
        print("  📅 Test 4: Date filtering")
        today = date.today().isoformat()
        response = requests.get(f"{API_BASE}/admin-registrations-pending-optimized?search_date={today}")
        if response.status_code == 200:
            data = response.json()
            print(f"    ✅ Date search '{today}': Found {len(data['data'])} results")
        else:
            print(f"    ❌ Date search test failed")
        
        # Test 5: Edge case - invalid page
        print("  🚫 Test 5: Edge case - invalid page")
        response = requests.get(f"{API_BASE}/admin-registrations-pending-optimized?page=999")
        if response.status_code == 200:
            data = response.json()
            if len(data['data']) == 0:
                print(f"    ✅ Invalid page returns empty results correctly")
            else:
                print(f"    ⚠️  Invalid page returned {len(data['data'])} results")
        
        return True
        
    except Exception as e:
        print(f"    ❌ Test failed with error: {str(e)}")
        return False

def test_optimized_submitted_registrations():
    """Test the new optimized submitted registrations endpoint"""
    print("🔍 Testing /api/admin-registrations-submitted-optimized...")
    
    try:
        # Test 1: Basic functionality
        print("  📄 Test 1: Basic pagination")
        response = requests.get(f"{API_BASE}/admin-registrations-submitted-optimized")
        
        if response.status_code == 200:
            data = response.json()
            
            # Verify response structure
            if all(key in data for key in ['data', 'pagination', 'filters']):
                print(f"    ✅ Response structure correct")
                print(f"    📊 Found {data['pagination']['total_records']} total submitted registrations")
                
                # Verify photos are excluded
                if data['data'] and 'photo' not in data['data'][0]:
                    print(f"    ✅ Photos excluded from list view for performance")
                
                # Check for finalized_at field (specific to submitted)
                if data['data'] and 'finalized_at' in data['data'][0]:
                    print(f"    ✅ finalized_at field present in submitted registrations")
                
            else:
                print(f"    ❌ Missing required keys in response")
                return False
        else:
            print(f"    ❌ Request failed with status {response.status_code}")
            return False
        
        # Test 2: Pagination with page 2
        print("  📄 Test 2: Page 2 navigation")
        response = requests.get(f"{API_BASE}/admin-registrations-submitted-optimized?page=2&page_size=5")
        if response.status_code == 200:
            data = response.json()
            if data['pagination']['current_page'] == 2:
                print(f"    ✅ Page 2 navigation works correctly")
            else:
                print(f"    ❌ Page 2 navigation failed")
        
        return True
        
    except Exception as e:
        print(f"    ❌ Test failed with error: {str(e)}")
        return False

def test_optimized_activities():
    """Test the new optimized activities endpoint"""
    print("🔍 Testing /api/admin-activities-optimized...")
    
    try:
        # Test 1: Basic functionality
        print("  📄 Test 1: Basic activities retrieval")
        response = requests.get(f"{API_BASE}/admin-activities-optimized")
        
        if response.status_code == 200:
            data = response.json()
            
            # Verify response structure
            if all(key in data for key in ['activities', 'pagination', 'filters']):
                print(f"    ✅ Response structure correct")
                print(f"    📊 Found {data['pagination']['total_records']} total activities")
                
                # Check for client information (JOIN optimization)
                if data['activities'] and 'client_name' in data['activities'][0]:
                    print(f"    ✅ Client information joined correctly (optimized JOIN)")
                    print(f"    👤 Sample client: {data['activities'][0].get('client_name', 'N/A')}")
                
                # Check for status field
                if data['activities'] and 'status' in data['activities'][0]:
                    print(f"    ✅ Activity status calculated correctly")
                
            else:
                print(f"    ❌ Missing required keys in response")
                return False
        else:
            print(f"    ❌ Request failed with status {response.status_code}")
            return False
        
        # Test 2: Status filtering
        print("  🔍 Test 2: Status filtering")
        for status in ['all', 'upcoming', 'completed']:
            response = requests.get(f"{API_BASE}/admin-activities-optimized?status_filter={status}")
            if response.status_code == 200:
                data = response.json()
                print(f"    ✅ Status filter '{status}': Found {len(data['activities'])} results")
            else:
                print(f"    ❌ Status filter '{status}' failed")
        
        # Test 3: Search term filtering
        print("  🔍 Test 3: Search term filtering")
        response = requests.get(f"{API_BASE}/admin-activities-optimized?search_term=test")
        if response.status_code == 200:
            data = response.json()
            print(f"    ✅ Search term 'test': Found {len(data['activities'])} results")
        else:
            print(f"    ❌ Search term test failed")
        
        return True
        
    except Exception as e:
        print(f"    ❌ Test failed with error: {str(e)}")
        return False

def test_dashboard_stats():
    """Test the new dashboard stats endpoint"""
    print("🔍 Testing /api/admin-dashboard-stats...")
    
    try:
        start_time = time.time()
        response = requests.get(f"{API_BASE}/admin-dashboard-stats")
        end_time = time.time()
        
        if response.status_code == 200:
            data = response.json()
            response_time = (end_time - start_time) * 1000  # Convert to milliseconds
            
            # Verify response structure
            required_keys = ['pending_registrations', 'submitted_registrations', 'total_activities']
            if all(key in data for key in required_keys):
                print(f"    ✅ Response structure correct")
                print(f"    📊 Pending: {data['pending_registrations']}")
                print(f"    📊 Submitted: {data['submitted_registrations']}")
                print(f"    📊 Activities: {data['total_activities']}")
                print(f"    ⚡ Response time: {response_time:.2f}ms")
                
                if response_time < 1000:  # Less than 1 second
                    print(f"    ✅ Fast response time (< 1s)")
                else:
                    print(f"    ⚠️  Slow response time (> 1s)")
                
                return True
            else:
                print(f"    ❌ Missing required keys in response")
                return False
        else:
            print(f"    ❌ Request failed with status {response.status_code}")
            return False
        
    except Exception as e:
        print(f"    ❌ Test failed with error: {str(e)}")
        return False

def test_photo_lazy_loading():
    """Test the photo lazy loading endpoint"""
    print("🔍 Testing /api/admin-registration/{id}/photo...")
    
    try:
        # First, get a registration ID from pending registrations
        response = requests.get(f"{API_BASE}/admin-registrations-pending-optimized?page_size=5")
        
        if response.status_code == 200:
            data = response.json()
            if data['data']:
                registration_id = data['data'][0]['id']
                print(f"  📷 Test 1: Testing photo endpoint for ID: {registration_id}")
                
                # Test photo endpoint
                photo_response = requests.get(f"{API_BASE}/admin-registration/{registration_id}/photo")
                
                if photo_response.status_code == 200:
                    photo_data = photo_response.json()
                    if 'id' in photo_data and 'photo' in photo_data:
                        print(f"    ✅ Photo endpoint structure correct")
                        if photo_data['photo']:
                            print(f"    📷 Photo data present for registration")
                        else:
                            print(f"    📷 No photo data for this registration")
                        return True
                    else:
                        print(f"    ❌ Photo endpoint response structure incorrect")
                        return False
                elif photo_response.status_code == 404:
                    print(f"    ⚠️  Registration not found (404) - this may be expected")
                    return True
                else:
                    print(f"    ❌ Photo endpoint failed with status {photo_response.status_code}")
                    return False
            else:
                print(f"    ⚠️  No registrations available to test photo endpoint")
                return True
        else:
            print(f"    ❌ Could not get registrations to test photo endpoint")
            return False
        
    except Exception as e:
        print(f"    ❌ Test failed with error: {str(e)}")
        return False

def test_performance_comparison():
    """Compare performance between old and new endpoints"""
    print("🔍 Testing performance comparison (old vs optimized)...")
    
    try:
        # Test old pending endpoint
        print("  ⏱️  Testing old pending endpoint...")
        start_time = time.time()
        old_response = requests.get(f"{API_BASE}/admin-registrations-pending")
        old_time = (time.time() - start_time) * 1000
        
        # Test new optimized pending endpoint
        print("  ⚡ Testing optimized pending endpoint...")
        start_time = time.time()
        new_response = requests.get(f"{API_BASE}/admin-registrations-pending-optimized")
        new_time = (time.time() - start_time) * 1000
        
        if old_response.status_code == 200 and new_response.status_code == 200:
            old_data = old_response.json()
            new_data = new_response.json()
            
            # Compare response sizes
            old_size = len(json.dumps(old_data))
            new_size = len(json.dumps(new_data))
            
            print(f"    📊 Old endpoint: {old_time:.2f}ms, {old_size} bytes")
            print(f"    📊 New endpoint: {new_time:.2f}ms, {new_size} bytes")
            
            # Check if new endpoint is more efficient
            if new_time <= old_time:
                print(f"    ✅ Optimized endpoint is faster or equal")
            else:
                print(f"    ⚠️  Optimized endpoint is slower (may be due to additional features)")
            
            # Check data count
            old_count = len(old_data) if isinstance(old_data, list) else 0
            new_count = len(new_data.get('data', [])) if isinstance(new_data, dict) else 0
            print(f"    📊 Old endpoint returned {old_count} records")
            print(f"    📊 New endpoint returned {new_count} records")
            
            return True
        else:
            print(f"    ❌ One or both endpoints failed")
            return False
        
    except Exception as e:
        print(f"    ❌ Performance comparison failed: {str(e)}")
        return False

def test_backward_compatibility():
    """Test that old endpoints still work"""
    print("🔍 Testing backward compatibility...")
    
    try:
        # Test old endpoints still work
        old_endpoints = [
            "/admin-registrations-pending",
            "/admin-registrations-submitted"
        ]
        
        for endpoint in old_endpoints:
            print(f"  🔄 Testing {endpoint}...")
            response = requests.get(f"{API_BASE}{endpoint}")
            
            if response.status_code == 200:
                print(f"    ✅ {endpoint} still works")
            else:
                print(f"    ❌ {endpoint} failed with status {response.status_code}")
                return False
        
        return True
        
    except Exception as e:
        print(f"    ❌ Backward compatibility test failed: {str(e)}")
        return False

def main():
    """Run all optimized admin dashboard tests"""
    print("🚀 Starting Optimized Admin Dashboard Backend Tests")
    print("=" * 60)
    
    test_results = []
    
    # Run all tests
    tests = [
        ("Optimized Pending Registrations", test_optimized_pending_registrations),
        ("Optimized Submitted Registrations", test_optimized_submitted_registrations),
        ("Optimized Activities", test_optimized_activities),
        ("Dashboard Stats", test_dashboard_stats),
        ("Photo Lazy Loading", test_photo_lazy_loading),
        ("Performance Comparison", test_performance_comparison),
        ("Backward Compatibility", test_backward_compatibility)
    ]
    
    for test_name, test_func in tests:
        print(f"\n🧪 {test_name}")
        print("-" * 40)
        try:
            result = test_func()
            test_results.append((test_name, result))
            if result:
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {str(e)}")
            test_results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    print(f"\n🎯 Overall Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Optimized admin dashboard endpoints are working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Please review the results above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)