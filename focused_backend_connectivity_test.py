#!/usr/bin/env python3
"""
Focused Backend API Test with Retry Logic
Testing critical API endpoints with improved error handling
"""

import requests
import json
import sys
import time
from datetime import datetime

# Backend URL from frontend environment
BACKEND_URL = "https://46471c8a-a981-4b23-bca9-bb5c0ba282bc.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

def make_request_with_retry(url, method='GET', data=None, max_retries=3, timeout=15):
    """Make HTTP request with retry logic"""
    for attempt in range(max_retries):
        try:
            if method == 'GET':
                response = requests.get(url, timeout=timeout)
            elif method == 'POST':
                response = requests.post(url, json=data, timeout=timeout)
            elif method == 'DELETE':
                response = requests.delete(url, timeout=timeout)
            
            return response
        except requests.exceptions.Timeout:
            print(f"   Timeout on attempt {attempt + 1}/{max_retries}")
            if attempt < max_retries - 1:
                time.sleep(2)  # Wait before retry
            continue
        except Exception as e:
            print(f"   Error on attempt {attempt + 1}: {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(2)
            continue
    
    return None

def test_critical_endpoints():
    """Test all critical endpoints for dropdown population"""
    print("🔍 Testing Critical API Endpoints for Dropdown Population...")
    
    endpoints = {
        'dispositions': '/api/dispositions',
        'referral_sites': '/api/referral-sites',
        'clinical_templates': '/api/clinical-templates',
        'notes_templates': '/api/notes-templates',
        'admin_pending': '/api/admin-registrations-pending',
        'admin_submitted': '/api/admin-registrations-submitted'
    }
    
    results = {}
    
    for name, endpoint in endpoints.items():
        print(f"\n📋 Testing {name.replace('_', ' ').title()}...")
        
        response = make_request_with_retry(f"{BACKEND_URL}{endpoint}")
        
        if response is None:
            print(f"❌ {name} - Failed after all retries")
            results[name] = {'success': False, 'error': 'Timeout/Connection error'}
            continue
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                count = len(data) if isinstance(data, list) else 'N/A'
                print(f"✅ {name} - Success ({count} items)")
                
                # Check data structure for dropdown endpoints
                if isinstance(data, list) and data:
                    sample = data[0]
                    if 'id' in sample and 'name' in sample:
                        print(f"   ✅ Valid structure - Sample: {sample.get('name', 'N/A')}")
                        results[name] = {'success': True, 'count': len(data), 'sample': sample.get('name')}
                    else:
                        print(f"   ⚠️  Missing required fields (id/name)")
                        results[name] = {'success': True, 'count': len(data), 'warning': 'Missing fields'}
                elif isinstance(data, list):
                    print(f"   ✅ Empty list (valid for registrations)")
                    results[name] = {'success': True, 'count': 0}
                else:
                    print(f"   ⚠️  Unexpected data format")
                    results[name] = {'success': True, 'warning': 'Unexpected format'}
                    
            except Exception as e:
                print(f"❌ {name} - JSON parsing error: {str(e)}")
                results[name] = {'success': False, 'error': f'JSON error: {str(e)}'}
        else:
            print(f"❌ {name} - HTTP {response.status_code}")
            try:
                error_data = response.text
                print(f"   Error: {error_data[:200]}...")
            except:
                pass
            results[name] = {'success': False, 'error': f'HTTP {response.status_code}'}
    
    return results

def test_mongodb_basic():
    """Test basic MongoDB connectivity"""
    print("\n🔍 Testing MongoDB Basic Connectivity...")
    
    # Try to create a simple test registration
    test_data = {
        "firstName": "ConnectivityTest",
        "lastName": "MongoDB",
        "patientConsent": "verbal"
    }
    
    print("   Creating test registration...")
    response = make_request_with_retry(f"{API_BASE}/admin-register", method='POST', data=test_data)
    
    if response is None:
        print("❌ MongoDB test failed - Connection timeout")
        return False
    
    if response.status_code == 200:
        try:
            data = response.json()
            reg_id = data.get('id')
            print(f"✅ MongoDB write successful - ID: {reg_id}")
            
            # Try to read it back
            if reg_id:
                print("   Reading back test registration...")
                read_response = make_request_with_retry(f"{API_BASE}/admin-registration/{reg_id}")
                
                if read_response and read_response.status_code == 200:
                    read_data = read_response.json()
                    if read_data.get('firstName') == 'ConnectivityTest':
                        print("✅ MongoDB read successful - Data persistence verified")
                        
                        # Clean up
                        print("   Cleaning up test data...")
                        delete_response = make_request_with_retry(f"{API_BASE}/admin-registration/{reg_id}", method='DELETE')
                        if delete_response and delete_response.status_code == 200:
                            print("✅ MongoDB delete successful - Cleanup completed")
                        
                        return True
                    else:
                        print("❌ Data mismatch in read operation")
                        return False
                else:
                    print("❌ Failed to read back test registration")
                    return False
            else:
                print("❌ No ID returned from registration creation")
                return False
                
        except Exception as e:
            print(f"❌ MongoDB test error: {str(e)}")
            return False
    else:
        print(f"❌ MongoDB write failed - HTTP {response.status_code}")
        try:
            print(f"   Error: {response.text[:200]}...")
        except:
            pass
        return False

def analyze_dropdown_issues(results):
    """Analyze which dropdowns will have issues"""
    print("\n🔍 Analyzing Dropdown Population Issues...")
    
    dropdown_endpoints = ['dispositions', 'referral_sites', 'clinical_templates', 'notes_templates']
    
    working_dropdowns = []
    failing_dropdowns = []
    
    for endpoint in dropdown_endpoints:
        if endpoint in results and results[endpoint]['success']:
            count = results[endpoint].get('count', 0)
            sample = results[endpoint].get('sample', 'N/A')
            working_dropdowns.append(f"{endpoint.replace('_', ' ').title()} ({count} items, e.g., '{sample}')")
        else:
            error = results[endpoint].get('error', 'Unknown error') if endpoint in results else 'Not tested'
            failing_dropdowns.append(f"{endpoint.replace('_', ' ').title()} - {error}")
    
    print(f"\n✅ Working Dropdowns ({len(working_dropdowns)}/4):")
    for dropdown in working_dropdowns:
        print(f"   • {dropdown}")
    
    if failing_dropdowns:
        print(f"\n❌ Failing Dropdowns ({len(failing_dropdowns)}/4):")
        for dropdown in failing_dropdowns:
            print(f"   • {dropdown}")
    
    return len(working_dropdowns), len(failing_dropdowns)

def main():
    """Main test execution"""
    print("=" * 80)
    print("🚀 FOCUSED BACKEND API CONNECTIVITY TEST")
    print("=" * 80)
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # Test critical endpoints
    endpoint_results = test_critical_endpoints()
    
    # Test MongoDB
    mongodb_working = test_mongodb_basic()
    
    # Analyze dropdown issues
    working_count, failing_count = analyze_dropdown_issues(endpoint_results)
    
    # Final summary
    print("\n" + "=" * 80)
    print("📊 FINAL SUMMARY")
    print("=" * 80)
    
    total_endpoints = len(endpoint_results)
    working_endpoints = sum(1 for r in endpoint_results.values() if r['success'])
    
    print(f"API Endpoints: {working_endpoints}/{total_endpoints} working ({(working_endpoints/total_endpoints)*100:.1f}%)")
    print(f"Dropdown APIs: {working_count}/4 working ({(working_count/4)*100:.1f}%)")
    print(f"MongoDB: {'✅ Working' if mongodb_working else '❌ Failing'}")
    
    # Root cause analysis
    print(f"\n🔍 ROOT CAUSE ANALYSIS:")
    
    if failing_count > 0:
        print(f"   • {failing_count} dropdown API(s) are failing")
        print(f"   • This will cause empty dropdowns in the frontend")
        print(f"   • Users won't be able to select options for failing dropdowns")
    
    if not mongodb_working:
        print(f"   • MongoDB connectivity issues detected")
        print(f"   • Data persistence may be unreliable")
    
    if working_count == 4 and mongodb_working:
        print(f"   • All systems are working correctly!")
        print(f"   • Frontend dropdowns should populate properly")
        print(f"   • No connectivity issues found")
    
    # Recommendations
    print(f"\n💡 RECOMMENDATIONS:")
    
    if failing_count > 0:
        print(f"   • Check backend logs for specific API endpoint errors")
        print(f"   • Verify database seeding for failing endpoints")
        print(f"   • Test individual API endpoints manually")
    
    if not mongodb_working:
        print(f"   • Check MongoDB connection string and database availability")
        print(f"   • Verify backend can connect to database")
    
    print("=" * 80)
    
    # Return success if most critical systems are working
    success = working_count >= 3 and mongodb_working
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)