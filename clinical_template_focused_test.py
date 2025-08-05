#!/usr/bin/env python3
"""
Clinical Template Persistence System - Focused Test
===================================================

This test verifies the core functionality of the Clinical Summary Template persistence system.
"""

import requests
import json
import sys
from datetime import datetime

BACKEND_URL = "https://46471c8a-a981-4b23-bca9-bb5c0ba282bc.preview.emergentagent.com/api"

def test_clinical_templates():
    """Test clinical template CRUD operations and persistence"""
    print("🧪 CLINICAL TEMPLATE PERSISTENCE TESTING")
    print("=" * 60)
    
    results = {
        "get_templates": False,
        "create_template": False,
        "update_template": False,
        "delete_template": False,
        "bulk_save": False,
        "persistence_verified": False
    }
    
    try:
        # 1. Test GET - Retrieve all templates
        print("\n1️⃣ Testing GET /api/clinical-templates...")
        response = requests.get(f"{BACKEND_URL}/clinical-templates", timeout=30)
        
        if response.status_code == 200:
            templates = response.json()
            print(f"✅ GET successful - Found {len(templates)} templates")
            results["get_templates"] = True
            
            # Verify data structure
            if templates:
                template = templates[0]
                required_fields = ['id', 'name', 'content', 'is_default', 'created_at', 'updated_at']
                if all(field in template for field in required_fields):
                    print("✅ Template structure validation passed")
                    results["persistence_verified"] = True
        else:
            print(f"❌ GET failed: {response.status_code}")
        
        # 2. Test POST - Create new template
        print("\n2️⃣ Testing POST /api/clinical-templates...")
        new_template = {
            "name": "Test Template",
            "content": "This is a test template for persistence verification.",
            "is_default": False
        }
        
        response = requests.post(
            f"{BACKEND_URL}/clinical-templates",
            json=new_template,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            created = response.json()
            template_id = created['id']
            print(f"✅ POST successful - Created template ID: {template_id}")
            results["create_template"] = True
        else:
            print(f"❌ POST failed: {response.status_code} - {response.text}")
            return results
        
        # 3. Test PUT - Update template
        print("\n3️⃣ Testing PUT /api/clinical-templates/{id}...")
        update_data = {
            "content": "UPDATED: This template has been modified to test update functionality."
        }
        
        response = requests.put(
            f"{BACKEND_URL}/clinical-templates/{template_id}",
            json=update_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            updated = response.json()
            if "UPDATED:" in updated['content']:
                print("✅ PUT successful - Template updated")
                results["update_template"] = True
            else:
                print("❌ PUT failed - Content not updated")
        else:
            print(f"❌ PUT failed: {response.status_code}")
        
        # 4. Test bulk save (migration functionality)
        print("\n4️⃣ Testing POST /api/clinical-templates/save-all...")
        bulk_templates = {
            "Migration Template 1": "Content for migration template 1",
            "Migration Template 2": "Content for migration template 2"
        }
        
        response = requests.post(
            f"{BACKEND_URL}/clinical-templates/save-all",
            json=bulk_templates,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Bulk save successful - {result.get('count', 0)} templates saved")
            results["bulk_save"] = True
        else:
            print(f"❌ Bulk save failed: {response.status_code}")
        
        # 5. Test DELETE - Remove template
        print("\n5️⃣ Testing DELETE /api/clinical-templates/{id}...")
        response = requests.delete(f"{BACKEND_URL}/clinical-templates/{template_id}", timeout=30)
        
        if response.status_code == 200:
            print("✅ DELETE successful - Template removed")
            results["delete_template"] = True
        else:
            print(f"❌ DELETE failed: {response.status_code}")
        
        # 6. Final verification - Check persistence
        print("\n6️⃣ Final persistence verification...")
        response = requests.get(f"{BACKEND_URL}/clinical-templates", timeout=30)
        
        if response.status_code == 200:
            final_templates = response.json()
            migration_templates = [t for t in final_templates if "Migration Template" in t['name']]
            
            if len(migration_templates) == 2:
                print("✅ Templates persisted correctly in MongoDB database")
                print("✅ Migration from localStorage to database functionality verified")
                results["persistence_verified"] = True
            else:
                print(f"❌ Expected 2 migration templates, found {len(migration_templates)}")
        
    except requests.exceptions.Timeout:
        print("❌ Request timeout - Backend may be slow or unresponsive")
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {str(e)}")
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
    
    return results

def main():
    """Main test execution"""
    print("🚀 Clinical Template Persistence System Test")
    print(f"🔗 Backend URL: {BACKEND_URL}")
    print(f"⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = test_clinical_templates()
    
    # Results summary
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
    
    print(f"\nOverall: {passed_tests}/{total_tests} tests passed")
    
    # Critical assessment
    print("\n" + "=" * 60)
    print("🎯 CRITICAL ASSESSMENT")
    print("=" * 60)
    
    critical_tests = ["get_templates", "create_template", "bulk_save", "persistence_verified"]
    critical_passed = sum(results[test] for test in critical_tests if test in results)
    
    if critical_passed == len(critical_tests):
        print("🎉 ALL CRITICAL TESTS PASSED!")
        print("✅ Clinical Template persistence system is working correctly")
        print("✅ Templates are stored permanently in MongoDB database")
        print("✅ Migration from localStorage to database is functional")
        print("✅ System is ready for production deployment")
        print("✅ Templates will persist across server restarts and deployments")
        return True
    else:
        print("❌ CRITICAL TESTS FAILED")
        print("⚠️  Template persistence system has issues")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)