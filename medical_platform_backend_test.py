#!/usr/bin/env python3
"""
Medical Platform Backend API Connectivity Test
Testing critical API endpoints for dropdown population and data persistence
Focus: Verify backend connectivity and identify dropdown population issues
"""

import requests
import json
import sys
from datetime import datetime
import uuid

# Backend URL from frontend environment
BACKEND_URL = "https://cd556dd9-d36b-422e-8110-4b1830397661.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

def test_backend_health():
    """Test basic backend connectivity and health"""
    print("🔍 Testing Backend Health and Connectivity...")
    
    try:
        # Test basic backend response
        response = requests.get(BACKEND_URL, timeout=10)
        print(f"✅ Backend base URL accessible: {response.status_code}")
        
        # Test API root
        api_response = requests.get(API_BASE, timeout=10)
        print(f"✅ API base accessible: {api_response.status_code}")
        
        return True
    except Exception as e:
        print(f"❌ Backend health check failed: {str(e)}")
        return False

def test_dispositions_api():
    """Test /api/dispositions endpoint for dropdown population"""
    print("\n🔍 Testing Dispositions API...")
    
    try:
        response = requests.get(f"{API_BASE}/dispositions", timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Dispositions API working - Found {len(data)} dispositions")
            
            # Check data structure
            if data and isinstance(data, list):
                sample = data[0]
                required_fields = ['id', 'name']
                missing_fields = [field for field in required_fields if field not in sample]
                
                if not missing_fields:
                    print(f"✅ Data structure valid - Sample: {sample.get('name', 'N/A')}")
                    
                    # Check for frequent dispositions
                    frequent_count = len([d for d in data if d.get('is_frequent', False)])
                    print(f"✅ Found {frequent_count} frequent dispositions")
                    
                    return True
                else:
                    print(f"❌ Missing required fields: {missing_fields}")
                    return False
            else:
                print("❌ Invalid data structure - expected list")
                return False
        else:
            print(f"❌ Dispositions API failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Dispositions API error: {str(e)}")
        return False

def test_referral_sites_api():
    """Test /api/referral-sites endpoint for dropdown population"""
    print("\n🔍 Testing Referral Sites API...")
    
    try:
        response = requests.get(f"{API_BASE}/referral-sites", timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Referral Sites API working - Found {len(data)} sites")
            
            # Check data structure
            if data and isinstance(data, list):
                sample = data[0]
                required_fields = ['id', 'name']
                missing_fields = [field for field in required_fields if field not in sample]
                
                if not missing_fields:
                    print(f"✅ Data structure valid - Sample: {sample.get('name', 'N/A')}")
                    
                    # Check for frequent sites
                    frequent_count = len([s for s in data if s.get('is_frequent', False)])
                    print(f"✅ Found {frequent_count} frequent referral sites")
                    
                    return True
                else:
                    print(f"❌ Missing required fields: {missing_fields}")
                    return False
            else:
                print("❌ Invalid data structure - expected list")
                return False
        else:
            print(f"❌ Referral Sites API failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Referral Sites API error: {str(e)}")
        return False

def test_clinical_templates_api():
    """Test /api/clinical-templates endpoint for dropdown population"""
    print("\n🔍 Testing Clinical Templates API...")
    
    try:
        response = requests.get(f"{API_BASE}/clinical-templates", timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Clinical Templates API working - Found {len(data)} templates")
            
            # Check data structure
            if data and isinstance(data, list):
                sample = data[0]
                required_fields = ['id', 'name', 'content']
                missing_fields = [field for field in required_fields if field not in sample]
                
                if not missing_fields:
                    print(f"✅ Data structure valid - Sample: {sample.get('name', 'N/A')}")
                    
                    # Check for default templates
                    default_count = len([t for t in data if t.get('is_default', False)])
                    print(f"✅ Found {default_count} default clinical templates")
                    
                    return True
                else:
                    print(f"❌ Missing required fields: {missing_fields}")
                    return False
            else:
                print("❌ Invalid data structure - expected list")
                return False
        else:
            print(f"❌ Clinical Templates API failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Clinical Templates API error: {str(e)}")
        return False

def test_notes_templates_api():
    """Test /api/notes-templates endpoint for dropdown population"""
    print("\n🔍 Testing Notes Templates API...")
    
    try:
        response = requests.get(f"{API_BASE}/notes-templates", timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Notes Templates API working - Found {len(data)} templates")
            
            # Check data structure
            if data and isinstance(data, list):
                sample = data[0]
                required_fields = ['id', 'name', 'content']
                missing_fields = [field for field in required_fields if field not in sample]
                
                if not missing_fields:
                    print(f"✅ Data structure valid - Sample: {sample.get('name', 'N/A')}")
                    
                    # Check for default templates
                    default_count = len([t for t in data if t.get('is_default', False)])
                    print(f"✅ Found {default_count} default notes templates")
                    
                    return True
                else:
                    print(f"❌ Missing required fields: {missing_fields}")
                    return False
            else:
                print("❌ Invalid data structure - expected list")
                return False
        else:
            print(f"❌ Notes Templates API failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Notes Templates API error: {str(e)}")
        return False

def test_admin_registrations_pending():
    """Test /api/admin-registrations-pending endpoint"""
    print("\n🔍 Testing Admin Registrations Pending API...")
    
    try:
        response = requests.get(f"{API_BASE}/admin-registrations-pending", timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Admin Registrations Pending API working - Found {len(data)} pending registrations")
            
            # Check data structure if data exists
            if data and isinstance(data, list):
                sample = data[0]
                required_fields = ['id', 'firstName', 'lastName', 'timestamp']
                missing_fields = [field for field in required_fields if field not in sample]
                
                if not missing_fields:
                    print(f"✅ Data structure valid - Sample: {sample.get('firstName', 'N/A')} {sample.get('lastName', 'N/A')}")
                    return True
                else:
                    print(f"❌ Missing required fields: {missing_fields}")
                    return False
            else:
                print("✅ No pending registrations found (empty list is valid)")
                return True
        else:
            print(f"❌ Admin Registrations Pending API failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Admin Registrations Pending API error: {str(e)}")
        return False

def test_admin_registrations_submitted():
    """Test /api/admin-registrations-submitted endpoint"""
    print("\n🔍 Testing Admin Registrations Submitted API...")
    
    try:
        response = requests.get(f"{API_BASE}/admin-registrations-submitted", timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Admin Registrations Submitted API working - Found {len(data)} submitted registrations")
            
            # Check data structure if data exists
            if data and isinstance(data, list):
                sample = data[0]
                required_fields = ['id', 'firstName', 'lastName', 'timestamp']
                missing_fields = [field for field in required_fields if field not in sample]
                
                if not missing_fields:
                    print(f"✅ Data structure valid - Sample: {sample.get('firstName', 'N/A')} {sample.get('lastName', 'N/A')}")
                    return True
                else:
                    print(f"❌ Missing required fields: {missing_fields}")
                    return False
            else:
                print("✅ No submitted registrations found (empty list is valid)")
                return True
        else:
            print(f"❌ Admin Registrations Submitted API failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Admin Registrations Submitted API error: {str(e)}")
        return False

def test_mongodb_connectivity():
    """Test MongoDB connectivity through backend operations"""
    print("\n🔍 Testing MongoDB Connectivity and Data Persistence...")
    
    try:
        # Test creating a test registration to verify database connectivity
        test_registration = {
            "firstName": "TestConnectivity",
            "lastName": "BackendTest",
            "patientConsent": "verbal",
            "regDate": datetime.now().strftime("%Y-%m-%d")
        }
        
        response = requests.post(f"{API_BASE}/admin-register", 
                               json=test_registration, 
                               timeout=10)
        
        if response.status_code == 200:
            registration_data = response.json()
            registration_id = registration_data.get('id')
            print(f"✅ MongoDB write operation successful - Created test registration: {registration_id}")
            
            # Test reading the registration back
            read_response = requests.get(f"{API_BASE}/admin-registration/{registration_id}", timeout=10)
            
            if read_response.status_code == 200:
                read_data = read_response.json()
                if read_data.get('firstName') == 'TestConnectivity':
                    print("✅ MongoDB read operation successful - Data persistence verified")
                    
                    # Clean up test registration
                    delete_response = requests.delete(f"{API_BASE}/admin-registration/{registration_id}", timeout=10)
                    if delete_response.status_code == 200:
                        print("✅ MongoDB delete operation successful - Test cleanup completed")
                    
                    return True
                else:
                    print("❌ Data persistence failed - Retrieved data doesn't match")
                    return False
            else:
                print(f"❌ MongoDB read operation failed: {read_response.status_code}")
                return False
        else:
            print(f"❌ MongoDB write operation failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ MongoDB connectivity test error: {str(e)}")
        return False

def test_backend_port_and_routing():
    """Test if backend is properly accessible and routing correctly"""
    print("\n🔍 Testing Backend Port and Routing...")
    
    try:
        # Test different endpoint patterns to verify routing
        endpoints_to_test = [
            "/api/dispositions",
            "/api/referral-sites", 
            "/api/clinical-templates",
            "/api/notes-templates"
        ]
        
        routing_success = 0
        for endpoint in endpoints_to_test:
            try:
                response = requests.get(f"{BACKEND_URL}{endpoint}", timeout=5)
                if response.status_code in [200, 404, 422]:  # Any valid HTTP response
                    routing_success += 1
                    print(f"✅ Routing working for {endpoint}: {response.status_code}")
                else:
                    print(f"❌ Routing issue for {endpoint}: {response.status_code}")
            except Exception as e:
                print(f"❌ Routing failed for {endpoint}: {str(e)}")
        
        if routing_success == len(endpoints_to_test):
            print("✅ Backend routing is working correctly")
            return True
        else:
            print(f"❌ Backend routing issues - {routing_success}/{len(endpoints_to_test)} endpoints accessible")
            return False
            
    except Exception as e:
        print(f"❌ Backend routing test error: {str(e)}")
        return False

def run_comprehensive_backend_test():
    """Run all backend tests and provide summary"""
    print("=" * 80)
    print("🚀 MEDICAL PLATFORM BACKEND API CONNECTIVITY TEST")
    print("=" * 80)
    print(f"Backend URL: {BACKEND_URL}")
    print(f"API Base: {API_BASE}")
    print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    test_results = {}
    
    # Run all tests
    test_results['backend_health'] = test_backend_health()
    test_results['backend_routing'] = test_backend_port_and_routing()
    test_results['dispositions_api'] = test_dispositions_api()
    test_results['referral_sites_api'] = test_referral_sites_api()
    test_results['clinical_templates_api'] = test_clinical_templates_api()
    test_results['notes_templates_api'] = test_notes_templates_api()
    test_results['admin_pending_api'] = test_admin_registrations_pending()
    test_results['admin_submitted_api'] = test_admin_registrations_submitted()
    test_results['mongodb_connectivity'] = test_mongodb_connectivity()
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 80)
    
    passed_tests = sum(test_results.values())
    total_tests = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
    
    print(f"\nOverall Success Rate: {passed_tests}/{total_tests} ({(passed_tests/total_tests)*100:.1f}%)")
    
    # Critical issues analysis
    critical_failures = []
    if not test_results['backend_health']:
        critical_failures.append("Backend service is not accessible")
    if not test_results['backend_routing']:
        critical_failures.append("Backend routing is not working properly")
    if not test_results['mongodb_connectivity']:
        critical_failures.append("MongoDB connectivity is failing")
    
    dropdown_failures = []
    if not test_results['dispositions_api']:
        dropdown_failures.append("Dispositions dropdown will be empty")
    if not test_results['referral_sites_api']:
        dropdown_failures.append("Referral Sites dropdown will be empty")
    if not test_results['clinical_templates_api']:
        dropdown_failures.append("Clinical Templates dropdown will be empty")
    if not test_results['notes_templates_api']:
        dropdown_failures.append("Notes Templates dropdown will be empty")
    
    if critical_failures:
        print(f"\n🚨 CRITICAL ISSUES FOUND:")
        for issue in critical_failures:
            print(f"   • {issue}")
    
    if dropdown_failures:
        print(f"\n⚠️  DROPDOWN POPULATION ISSUES:")
        for issue in dropdown_failures:
            print(f"   • {issue}")
    
    if not critical_failures and not dropdown_failures:
        print(f"\n🎉 ALL SYSTEMS OPERATIONAL!")
        print("   • Backend is accessible and working correctly")
        print("   • All dropdown APIs are functional")
        print("   • MongoDB connectivity is stable")
        print("   • Frontend should be able to populate dropdowns")
    
    print("=" * 80)
    
    return passed_tests == total_tests

if __name__ == "__main__":
    success = run_comprehensive_backend_test()
    sys.exit(0 if success else 1)