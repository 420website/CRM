#!/usr/bin/env python3

import requests
import json
import sys
from datetime import datetime
import uuid

# Configuration
BACKEND_URL = "https://46471c8a-a981-4b23-bca9-bb5c0ba282bc.preview.emergentagent.com/api"

def test_referral_sites_api():
    """
    Comprehensive test of the new referral site management API endpoints
    Tests all CRUD operations and seeding functionality
    """
    
    print("🧪 REFERRAL SITES API TESTING STARTED")
    print("=" * 60)
    
    results = {
        "server_startup": False,
        "seeding_function": False,
        "get_all_referral_sites": False,
        "create_referral_site": False,
        "update_referral_site": False,
        "delete_referral_site": False,
        "save_all_referral_sites": False,
        "frequent_categorization": False,
        "default_protection": False
    }
    
    # Test 1: Server startup and basic connectivity
    print("\n1️⃣ TESTING SERVER STARTUP AND CONNECTIVITY")
    try:
        response = requests.get(f"{BACKEND_URL}/referral-sites", timeout=10)
        if response.status_code == 200:
            print("✅ Server is running and responding")
            results["server_startup"] = True
        else:
            print(f"❌ Server responded with status {response.status_code}")
            return results
    except Exception as e:
        print(f"❌ Server connection failed: {str(e)}")
        return results
    
    # Test 2: Seeding function verification
    print("\n2️⃣ TESTING SEEDING FUNCTION AND DEFAULT REFERRAL SITES")
    try:
        response = requests.get(f"{BACKEND_URL}/referral-sites")
        if response.status_code == 200:
            referral_sites = response.json()
            print(f"📊 Found {len(referral_sites)} referral sites in database")
            
            # Check if we have the expected 25 default referral sites
            default_sites = [site for site in referral_sites if site.get('is_default', False)]
            frequent_sites = [site for site in referral_sites if site.get('is_frequent', False)]
            non_frequent_sites = [site for site in referral_sites if not site.get('is_frequent', False)]
            
            print(f"📈 Default referral sites: {len(default_sites)}")
            print(f"🔥 Frequent referral sites: {len(frequent_sites)}")
            print(f"📋 Non-frequent referral sites: {len(non_frequent_sites)}")
            
            # Verify expected seeding (5 frequent + 20 non-frequent = 25 total)
            if len(default_sites) >= 20:  # Should have at least 20 default sites
                print("✅ Seeding function populated referral sites successfully")
                results["seeding_function"] = True
                
                # Check frequent vs non-frequent categorization
                if len(frequent_sites) >= 3 and len(non_frequent_sites) >= 15:
                    print("✅ Referral sites properly categorized as frequent vs non-frequent")
                    results["frequent_categorization"] = True
                else:
                    print(f"⚠️ Categorization issue: {len(frequent_sites)} frequent, {len(non_frequent_sites)} non-frequent")
            else:
                print(f"❌ Expected at least 20 default referral sites, found {len(default_sites)}")
            
            # Display some sample referral sites
            print("\n📋 Sample referral sites:")
            for i, site in enumerate(referral_sites[:5]):
                freq_status = "🔥 Frequent" if site.get('is_frequent') else "📋 Regular"
                default_status = "🔒 Default" if site.get('is_default') else "✏️ Custom"
                print(f"   {i+1}. {site['name']} - {freq_status} - {default_status}")
                
            results["get_all_referral_sites"] = True
        else:
            print(f"❌ Failed to fetch referral sites: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing seeding: {str(e)}")
    
    # Test 3: Create new referral site
    print("\n3️⃣ TESTING CREATE REFERRAL SITE")
    test_site_name = f"Test Site - {datetime.now().strftime('%H%M%S')}"
    try:
        new_site_data = {
            "name": test_site_name,
            "is_frequent": True,
            "is_default": False
        }
        
        response = requests.post(f"{BACKEND_URL}/referral-sites", 
                               json=new_site_data, 
                               headers={"Content-Type": "application/json"})
        
        if response.status_code == 200:
            created_site = response.json()
            print(f"✅ Successfully created referral site: {created_site['name']}")
            print(f"   ID: {created_site['id']}")
            print(f"   Frequent: {created_site['is_frequent']}")
            print(f"   Default: {created_site['is_default']}")
            results["create_referral_site"] = True
            
            # Store the ID for update and delete tests
            test_site_id = created_site['id']
        else:
            print(f"❌ Failed to create referral site: {response.status_code}")
            print(f"   Response: {response.text}")
            test_site_id = None
    except Exception as e:
        print(f"❌ Error creating referral site: {str(e)}")
        test_site_id = None
    
    # Test 4: Update referral site
    print("\n4️⃣ TESTING UPDATE REFERRAL SITE")
    if test_site_id:
        try:
            update_data = {
                "name": f"Updated {test_site_name}",
                "is_frequent": False,
                "is_default": False
            }
            
            response = requests.put(f"{BACKEND_URL}/referral-sites/{test_site_id}", 
                                  json=update_data,
                                  headers={"Content-Type": "application/json"})
            
            if response.status_code == 200:
                updated_site = response.json()
                print(f"✅ Successfully updated referral site: {updated_site['name']}")
                print(f"   Frequent changed to: {updated_site['is_frequent']}")
                results["update_referral_site"] = True
            else:
                print(f"❌ Failed to update referral site: {response.status_code}")
                print(f"   Response: {response.text}")
        except Exception as e:
            print(f"❌ Error updating referral site: {str(e)}")
    else:
        print("⏭️ Skipping update test (no test site created)")
    
    # Test 5: Test default referral site protection
    print("\n5️⃣ TESTING DEFAULT REFERRAL SITE DELETION PROTECTION")
    try:
        # Get a default referral site
        response = requests.get(f"{BACKEND_URL}/referral-sites")
        if response.status_code == 200:
            referral_sites = response.json()
            default_site = next((site for site in referral_sites if site.get('is_default', False)), None)
            
            if default_site:
                # Try to delete a default referral site (should fail)
                response = requests.delete(f"{BACKEND_URL}/referral-sites/{default_site['id']}")
                
                if response.status_code == 400:
                    print(f"✅ Default referral site protection working: {default_site['name']}")
                    print("   Cannot delete default referral sites as expected")
                    results["default_protection"] = True
                else:
                    print(f"❌ Default referral site protection failed: {response.status_code}")
                    print(f"   Should have returned 400, got {response.status_code}")
            else:
                print("⚠️ No default referral sites found to test protection")
    except Exception as e:
        print(f"❌ Error testing default protection: {str(e)}")
    
    # Test 6: Delete custom referral site
    print("\n6️⃣ TESTING DELETE CUSTOM REFERRAL SITE")
    if test_site_id:
        try:
            response = requests.delete(f"{BACKEND_URL}/referral-sites/{test_site_id}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Successfully deleted custom referral site")
                print(f"   Message: {result.get('message', 'Deleted')}")
                results["delete_referral_site"] = True
            else:
                print(f"❌ Failed to delete referral site: {response.status_code}")
                print(f"   Response: {response.text}")
        except Exception as e:
            print(f"❌ Error deleting referral site: {str(e)}")
    else:
        print("⏭️ Skipping delete test (no test site created)")
    
    # Test 7: Save all referral sites
    print("\n7️⃣ TESTING SAVE ALL REFERRAL SITES")
    try:
        # Create test data for save-all endpoint
        test_sites_data = [
            {
                "name": f"Bulk Test Site 1 - {datetime.now().strftime('%H%M%S')}",
                "is_frequent": True,
                "is_default": False
            },
            {
                "name": f"Bulk Test Site 2 - {datetime.now().strftime('%H%M%S')}",
                "is_frequent": False,
                "is_default": False
            }
        ]
        
        response = requests.post(f"{BACKEND_URL}/referral-sites/save-all", 
                               json=test_sites_data,
                               headers={"Content-Type": "application/json"})
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Successfully saved referral sites in bulk")
            print(f"   Message: {result.get('message', 'Saved')}")
            print(f"   Count: {result.get('count', 'Unknown')}")
            results["save_all_referral_sites"] = True
        else:
            print(f"❌ Failed to save all referral sites: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Error testing save all: {str(e)}")
    
    # Final verification - check total count after all operations
    print("\n8️⃣ FINAL VERIFICATION")
    try:
        response = requests.get(f"{BACKEND_URL}/referral-sites")
        if response.status_code == 200:
            final_sites = response.json()
            print(f"📊 Final referral site count: {len(final_sites)}")
            
            # Count by categories
            default_count = len([s for s in final_sites if s.get('is_default', False)])
            frequent_count = len([s for s in final_sites if s.get('is_frequent', False)])
            custom_count = len([s for s in final_sites if not s.get('is_default', False)])
            
            print(f"   🔒 Default sites: {default_count}")
            print(f"   🔥 Frequent sites: {frequent_count}")
            print(f"   ✏️ Custom sites: {custom_count}")
        else:
            print(f"❌ Failed final verification: {response.status_code}")
    except Exception as e:
        print(f"❌ Error in final verification: {str(e)}")
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    passed_tests = sum(results.values())
    total_tests = len(results)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name.replace('_', ' ').title()}")
    
    print(f"\n🎯 OVERALL RESULT: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 ALL REFERRAL SITE TESTS PASSED! The new API is working correctly.")
    elif passed_tests >= total_tests * 0.8:
        print("⚠️ Most tests passed, but some issues need attention.")
    else:
        print("❌ Multiple critical issues found. API needs fixes.")
    
    return results

if __name__ == "__main__":
    test_referral_sites_api()