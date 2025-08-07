#!/usr/bin/env python3
"""
Final Backend API Verification Test
Confirming all critical endpoints are working correctly
"""

import requests
import json
import sys
from datetime import datetime

# Backend URL from frontend environment
BACKEND_URL = "https://cd556dd9-d36b-422e-8110-4b1830397661.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

def test_endpoint(name, endpoint):
    """Test a single endpoint"""
    try:
        response = requests.get(f"{BACKEND_URL}{endpoint}", timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            count = len(data) if isinstance(data, list) else 'N/A'
            
            # Check data structure for dropdown endpoints
            if isinstance(data, list) and data:
                sample = data[0]
                if 'id' in sample and 'name' in sample:
                    return True, count, sample.get('name', 'N/A')
                else:
                    return True, count, 'Valid but no name field'
            elif isinstance(data, list):
                return True, 0, 'Empty list (valid)'
            else:
                return True, 'N/A', 'Non-list response'
        else:
            return False, response.status_code, response.text[:100]
            
    except Exception as e:
        return False, 'Error', str(e)[:100]

def main():
    """Main test execution"""
    print("=" * 80)
    print("🚀 FINAL BACKEND API VERIFICATION TEST")
    print("=" * 80)
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # Critical endpoints for dropdown population
    endpoints = {
        'Dispositions': '/api/dispositions',
        'Referral Sites': '/api/referral-sites',
        'Clinical Templates': '/api/clinical-templates',
        'Notes Templates': '/api/notes-templates',
        'Admin Pending': '/api/admin-registrations-pending',
        'Admin Submitted': '/api/admin-registrations-submitted'
    }
    
    results = {}
    
    for name, endpoint in endpoints.items():
        print(f"\n🔍 Testing {name}...")
        success, count, sample = test_endpoint(name, endpoint)
        
        if success:
            print(f"✅ {name}: SUCCESS - {count} items")
            if sample != 'Empty list (valid)' and sample != 'Non-list response':
                print(f"   Sample: {sample}")
            results[name] = True
        else:
            print(f"❌ {name}: FAILED - {count}")
            print(f"   Error: {sample}")
            results[name] = False
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 FINAL TEST RESULTS")
    print("=" * 80)
    
    passed = sum(results.values())
    total = len(results)
    
    for name, result in results.items():
        status = "✅ WORKING" if result else "❌ FAILING"
        print(f"{name}: {status}")
    
    print(f"\nOverall Success Rate: {passed}/{total} ({(passed/total)*100:.1f}%)")
    
    # Dropdown analysis
    dropdown_endpoints = ['Dispositions', 'Referral Sites', 'Clinical Templates', 'Notes Templates']
    dropdown_working = sum(1 for name in dropdown_endpoints if results.get(name, False))
    
    print(f"\n🎯 DROPDOWN POPULATION ANALYSIS:")
    print(f"Working Dropdowns: {dropdown_working}/4 ({(dropdown_working/4)*100:.1f}%)")
    
    if dropdown_working == 4:
        print("✅ ALL DROPDOWN APIs ARE WORKING!")
        print("   • Frontend dropdowns should populate correctly")
        print("   • Users can select from all dropdown options")
        print("   • No connectivity issues preventing dropdown population")
    else:
        failing_dropdowns = [name for name in dropdown_endpoints if not results.get(name, False)]
        print(f"❌ FAILING DROPDOWNS: {', '.join(failing_dropdowns)}")
        print("   • These dropdowns will appear empty in the frontend")
        print("   • Users won't be able to select options for failing dropdowns")
    
    # Final verdict
    print(f"\n🏁 FINAL VERDICT:")
    if passed == total:
        print("🎉 ALL BACKEND APIs ARE WORKING CORRECTLY!")
        print("   • Backend service is fully operational")
        print("   • All dropdown APIs are functional")
        print("   • Frontend should be able to populate all dropdowns")
        print("   • No backend connectivity issues found")
    else:
        print("⚠️  SOME BACKEND APIs HAVE ISSUES")
        print("   • Check backend logs for specific errors")
        print("   • Verify database connectivity and seeding")
        print("   • Some frontend dropdowns may be empty")
    
    print("=" * 80)
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)