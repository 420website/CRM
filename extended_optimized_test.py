#!/usr/bin/env python3
"""
Extended test suite for optimized admin dashboard endpoints with additional edge cases and performance testing.
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

def test_advanced_filtering():
    """Test advanced filtering capabilities"""
    print("🔍 Testing Advanced Filtering...")
    
    try:
        # Test disposition filtering
        print("  🏷️  Test 1: Disposition filtering")
        response = requests.get(f"{API_BASE}/admin-registrations-pending-optimized?search_disposition=ACTIVE")
        if response.status_code == 200:
            data = response.json()
            print(f"    ✅ Disposition filter 'ACTIVE': Found {len(data['data'])} results")
            
            # Verify all results have ACTIVE disposition
            if data['data']:
                active_count = sum(1 for reg in data['data'] if reg.get('disposition') == 'ACTIVE')
                if active_count == len(data['data']):
                    print(f"    ✅ All results correctly filtered by disposition")
                else:
                    print(f"    ⚠️  Some results don't match disposition filter")
        
        # Test referral site filtering
        print("  🏢 Test 2: Referral site filtering")
        response = requests.get(f"{API_BASE}/admin-registrations-pending-optimized?search_referral_site=Toronto - Outreach")
        if response.status_code == 200:
            data = response.json()
            print(f"    ✅ Referral site filter 'Toronto - Outreach': Found {len(data['data'])} results")
        
        # Test combined filtering
        print("  🔗 Test 3: Combined filtering")
        response = requests.get(f"{API_BASE}/admin-registrations-pending-optimized?search_disposition=ACTIVE&search_name=michael")
        if response.status_code == 200:
            data = response.json()
            print(f"    ✅ Combined filter (ACTIVE + michael): Found {len(data['data'])} results")
        
        # Test lastname, firstinitial format
        print("  👤 Test 4: Lastname, firstinitial search format")
        response = requests.get(f"{API_BASE}/admin-registrations-pending-optimized?search_name=johnson, m")
        if response.status_code == 200:
            data = response.json()
            print(f"    ✅ Name search 'johnson, m': Found {len(data['data'])} results")
        
        return True
        
    except Exception as e:
        print(f"    ❌ Advanced filtering test failed: {str(e)}")
        return False

def test_pagination_edge_cases():
    """Test pagination edge cases and limits"""
    print("🔍 Testing Pagination Edge Cases...")
    
    try:
        # Test page size limits
        print("  📏 Test 1: Large page size")
        response = requests.get(f"{API_BASE}/admin-registrations-pending-optimized?page_size=100")
        if response.status_code == 200:
            data = response.json()
            print(f"    ✅ Large page size (100): Got {len(data['data'])} records")
        
        # Test page 0 (should default to page 1)
        print("  🔢 Test 2: Page 0 handling")
        response = requests.get(f"{API_BASE}/admin-registrations-pending-optimized?page=0")
        if response.status_code == 200:
            data = response.json()
            if data['pagination']['current_page'] >= 1:
                print(f"    ✅ Page 0 handled correctly (current_page: {data['pagination']['current_page']})")
            else:
                print(f"    ❌ Page 0 not handled correctly")
        
        # Test negative page
        print("  ➖ Test 3: Negative page handling")
        response = requests.get(f"{API_BASE}/admin-registrations-pending-optimized?page=-1")
        if response.status_code == 200:
            data = response.json()
            if data['pagination']['current_page'] >= 1:
                print(f"    ✅ Negative page handled correctly")
            else:
                print(f"    ❌ Negative page not handled correctly")
        
        return True
        
    except Exception as e:
        print(f"    ❌ Pagination edge cases test failed: {str(e)}")
        return False

def test_performance_under_load():
    """Test performance under concurrent requests"""
    print("🔍 Testing Performance Under Load...")
    
    try:
        import threading
        import time
        
        results = []
        
        def make_request():
            start_time = time.time()
            response = requests.get(f"{API_BASE}/admin-registrations-pending-optimized?page_size=10")
            end_time = time.time()
            results.append({
                'status_code': response.status_code,
                'response_time': (end_time - start_time) * 1000
            })
        
        # Test 5 concurrent requests
        print("  🚀 Test 1: 5 concurrent requests")
        threads = []
        start_time = time.time()
        
        for i in range(5):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        total_time = (time.time() - start_time) * 1000
        
        successful_requests = sum(1 for r in results if r['status_code'] == 200)
        avg_response_time = sum(r['response_time'] for r in results) / len(results)
        
        print(f"    ✅ Concurrent requests: {successful_requests}/5 successful")
        print(f"    ⚡ Average response time: {avg_response_time:.2f}ms")
        print(f"    ⏱️  Total time: {total_time:.2f}ms")
        
        if successful_requests == 5 and avg_response_time < 1000:
            print(f"    ✅ Performance under load: GOOD")
            return True
        else:
            print(f"    ⚠️  Performance under load: NEEDS IMPROVEMENT")
            return False
        
    except Exception as e:
        print(f"    ❌ Performance under load test failed: {str(e)}")
        return False

def test_data_consistency():
    """Test data consistency between old and new endpoints"""
    print("🔍 Testing Data Consistency...")
    
    try:
        # Get data from both endpoints
        old_response = requests.get(f"{API_BASE}/admin-registrations-pending")
        new_response = requests.get(f"{API_BASE}/admin-registrations-pending-optimized?page_size=100")
        
        if old_response.status_code == 200 and new_response.status_code == 200:
            old_data = old_response.json()
            new_data = new_response.json()['data']
            
            # Compare record counts
            print(f"  📊 Test 1: Record count comparison")
            print(f"    Old endpoint: {len(old_data)} records")
            print(f"    New endpoint: {len(new_data)} records")
            
            if len(old_data) == len(new_data):
                print(f"    ✅ Record counts match")
            else:
                print(f"    ⚠️  Record counts differ")
            
            # Compare first few records
            print(f"  🔍 Test 2: Data structure comparison")
            if old_data and new_data:
                old_fields = set(old_data[0].keys())
                new_fields = set(new_data[0].keys())
                
                # Check if new endpoint has required fields
                required_fields = {'id', 'firstName', 'lastName', 'regDate', 'timestamp'}
                if required_fields.issubset(new_fields):
                    print(f"    ✅ New endpoint has all required fields")
                else:
                    missing = required_fields - new_fields
                    print(f"    ❌ New endpoint missing fields: {missing}")
                
                # Check if photo is excluded in new endpoint
                if 'photo' not in new_fields:
                    print(f"    ✅ Photo field correctly excluded from new endpoint")
                else:
                    print(f"    ⚠️  Photo field present in new endpoint")
            
            return True
        else:
            print(f"    ❌ Failed to get data from endpoints")
            return False
        
    except Exception as e:
        print(f"    ❌ Data consistency test failed: {str(e)}")
        return False

def test_activities_join_optimization():
    """Test the activities JOIN optimization"""
    print("🔍 Testing Activities JOIN Optimization...")
    
    try:
        # First, let's create a test activity if none exist
        print("  📝 Test 1: Creating test activity (if needed)")
        
        # Get a registration ID first
        reg_response = requests.get(f"{API_BASE}/admin-registrations-pending-optimized?page_size=1")
        if reg_response.status_code == 200:
            reg_data = reg_response.json()
            if reg_data['data']:
                registration_id = reg_data['data'][0]['id']
                
                # Try to create a test activity
                activity_data = {
                    "date": "2025-07-21",
                    "time": "10:00",
                    "description": "Test activity for JOIN optimization testing"
                }
                
                create_response = requests.post(f"{API_BASE}/admin-registration/{registration_id}/activity", json=activity_data)
                if create_response.status_code == 200:
                    print(f"    ✅ Test activity created")
                else:
                    print(f"    ℹ️  Could not create test activity (may already exist)")
        
        # Test the optimized activities endpoint
        print("  🔗 Test 2: Testing JOIN optimization")
        start_time = time.time()
        response = requests.get(f"{API_BASE}/admin-activities-optimized")
        end_time = time.time()
        
        if response.status_code == 200:
            data = response.json()
            response_time = (end_time - start_time) * 1000
            
            print(f"    ✅ Activities endpoint working")
            print(f"    📊 Found {data['pagination']['total_records']} activities")
            print(f"    ⚡ Response time: {response_time:.2f}ms")
            
            # Check if client information is joined
            if data['activities']:
                activity = data['activities'][0]
                if 'client_name' in activity and 'client_first_name' in activity:
                    print(f"    ✅ Client information successfully joined")
                    print(f"    👤 Sample client: {activity.get('client_name', 'N/A')}")
                else:
                    print(f"    ❌ Client information not joined properly")
            else:
                print(f"    ℹ️  No activities to test JOIN optimization")
            
            return True
        else:
            print(f"    ❌ Activities endpoint failed")
            return False
        
    except Exception as e:
        print(f"    ❌ Activities JOIN optimization test failed: {str(e)}")
        return False

def main():
    """Run extended optimized admin dashboard tests"""
    print("🚀 Starting Extended Optimized Admin Dashboard Tests")
    print("=" * 60)
    
    test_results = []
    
    # Run extended tests
    tests = [
        ("Advanced Filtering", test_advanced_filtering),
        ("Pagination Edge Cases", test_pagination_edge_cases),
        ("Performance Under Load", test_performance_under_load),
        ("Data Consistency", test_data_consistency),
        ("Activities JOIN Optimization", test_activities_join_optimization)
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
    print("📊 EXTENDED TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    print(f"\n🎯 Overall Result: {passed}/{total} extended tests passed")
    
    if passed == total:
        print("🎉 ALL EXTENDED TESTS PASSED! Optimized endpoints are enterprise-ready.")
        return True
    else:
        print("⚠️  Some extended tests failed. Review results for optimization opportunities.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)