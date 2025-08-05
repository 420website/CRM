#!/usr/bin/env python3

import requests
import json
import sys
import os
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://dfe9a1e1-7f3d-45aa-ad71-43a254e568c5.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

def test_notes_templates_functionality():
    """
    Comprehensive test of Notes Template functionality as requested in review:
    1. GET /api/notes-templates endpoint
    2. POST /api/notes-templates/save-all endpoint  
    3. Verify default templates (Consultation, Lab, Prescription) are available
    4. Test template save/load cycle
    5. Ensure Notes template backend functionality is working as expected
    """
    
    print("🧪 NOTES TEMPLATE FUNCTIONALITY TESTING")
    print("=" * 60)
    
    test_results = {
        'get_templates': False,
        'default_templates_exist': False,
        'save_all_endpoint': False,
        'save_load_cycle': False,
        'backend_functionality': False
    }
    
    try:
        # Test 1: GET /api/notes-templates endpoint
        print("\n1️⃣ Testing GET /api/notes-templates endpoint...")
        response = requests.get(f"{API_BASE}/notes-templates", timeout=30)
        
        if response.status_code == 200:
            templates = response.json()
            print(f"✅ GET endpoint working - Found {len(templates)} templates")
            test_results['get_templates'] = True
            
            # Test 3: Verify default templates exist
            print("\n3️⃣ Verifying default templates (Consultation, Lab, Prescription)...")
            template_names = [t['name'] for t in templates]
            required_defaults = ['Consultation', 'Lab', 'Prescription']
            
            all_defaults_exist = True
            for default_name in required_defaults:
                if default_name in template_names:
                    print(f"✅ Default template '{default_name}' exists")
                else:
                    print(f"❌ Default template '{default_name}' missing")
                    all_defaults_exist = False
            
            if all_defaults_exist:
                test_results['default_templates_exist'] = True
                print("✅ All required default templates are available")
            else:
                print("❌ Some default templates are missing")
                
        else:
            print(f"❌ GET endpoint failed with status {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing GET endpoint: {str(e)}")
    
    try:
        # Test 2: POST /api/notes-templates/save-all endpoint
        print("\n2️⃣ Testing POST /api/notes-templates/save-all endpoint...")
        
        test_templates = {
            'Consultation': 'Test consultation template content for backend testing',
            'Lab': 'Test lab template content for backend testing',
            'Custom Test Template': 'This is a custom test template for save/load cycle testing'
        }
        
        response = requests.post(
            f"{API_BASE}/notes-templates/save-all",
            json=test_templates,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Save-all endpoint working - {result.get('message', 'Success')}")
            test_results['save_all_endpoint'] = True
        else:
            print(f"❌ Save-all endpoint failed with status {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing save-all endpoint: {str(e)}")
    
    try:
        # Test 4: Template save/load cycle
        print("\n4️⃣ Testing template save/load cycle...")
        
        # First, save a unique test template
        unique_template_name = f"Test Template {datetime.now().strftime('%Y%m%d_%H%M%S')}"
        unique_content = f"Unique test content created at {datetime.now().isoformat()}"
        
        save_payload = {unique_template_name: unique_content}
        
        save_response = requests.post(
            f"{API_BASE}/notes-templates/save-all",
            json=save_payload,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        if save_response.status_code == 200:
            print(f"✅ Template saved successfully: {unique_template_name}")
            
            # Now load all templates and verify our test template exists
            load_response = requests.get(f"{API_BASE}/notes-templates", timeout=30)
            
            if load_response.status_code == 200:
                all_templates = load_response.json()
                
                # Find our test template
                test_template_found = None
                for template in all_templates:
                    if template['name'] == unique_template_name:
                        test_template_found = template
                        break
                
                if test_template_found and test_template_found['content'] == unique_content:
                    print(f"✅ Save/load cycle successful - Template content matches")
                    test_results['save_load_cycle'] = True
                else:
                    print(f"❌ Save/load cycle failed - Template not found or content mismatch")
            else:
                print(f"❌ Failed to load templates after save: {load_response.status_code}")
        else:
            print(f"❌ Failed to save test template: {save_response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing save/load cycle: {str(e)}")
    
    # Test 5: Overall backend functionality assessment
    print("\n5️⃣ Assessing overall Notes template backend functionality...")
    
    functionality_checks = [
        test_results['get_templates'],
        test_results['default_templates_exist'], 
        test_results['save_all_endpoint'],
        test_results['save_load_cycle']
    ]
    
    if all(functionality_checks):
        test_results['backend_functionality'] = True
        print("✅ All Notes template backend functionality is working correctly")
    else:
        print("❌ Some Notes template backend functionality issues detected")
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 NOTES TEMPLATE TESTING SUMMARY")
    print("=" * 60)
    
    total_tests = len(test_results)
    passed_tests = sum(test_results.values())
    
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
    
    print(f"\nOverall Result: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 ALL NOTES TEMPLATE TESTS PASSED - Backend functionality is working correctly!")
        return True
    else:
        print("⚠️  Some tests failed - Notes template backend needs attention")
        return False

def test_additional_notes_template_endpoints():
    """Test additional CRUD endpoints for completeness"""
    
    print("\n🔧 TESTING ADDITIONAL NOTES TEMPLATE ENDPOINTS")
    print("=" * 60)
    
    try:
        # Test individual template creation
        print("\n📝 Testing individual template creation (POST /api/notes-templates)...")
        
        test_template = {
            "name": f"Individual Test Template {datetime.now().strftime('%H%M%S')}",
            "content": "This template was created via individual POST endpoint",
            "is_default": False
        }
        
        response = requests.post(
            f"{API_BASE}/notes-templates",
            json=test_template,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        if response.status_code == 200:
            created_template = response.json()
            template_id = created_template['id']
            print(f"✅ Individual template creation successful - ID: {template_id}")
            
            # Test template update
            print(f"\n✏️  Testing template update (PUT /api/notes-templates/{template_id})...")
            
            update_data = {
                "content": "Updated content for testing purposes",
                "name": created_template['name'] + " (Updated)"
            }
            
            update_response = requests.put(
                f"{API_BASE}/notes-templates/{template_id}",
                json=update_data,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            if update_response.status_code == 200:
                updated_template = update_response.json()
                print(f"✅ Template update successful - New content: {updated_template['content'][:50]}...")
                
                # Test template deletion
                print(f"\n🗑️  Testing template deletion (DELETE /api/notes-templates/{template_id})...")
                
                delete_response = requests.delete(f"{API_BASE}/notes-templates/{template_id}", timeout=30)
                
                if delete_response.status_code == 200:
                    print("✅ Template deletion successful")
                else:
                    print(f"❌ Template deletion failed: {delete_response.status_code}")
            else:
                print(f"❌ Template update failed: {update_response.status_code}")
        else:
            print(f"❌ Individual template creation failed: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing additional endpoints: {str(e)}")

if __name__ == "__main__":
    print("🚀 Starting Notes Template Backend Testing")
    print(f"🔗 Backend URL: {BACKEND_URL}")
    print(f"🔗 API Base: {API_BASE}")
    
    # Run main functionality tests
    main_tests_passed = test_notes_templates_functionality()
    
    # Run additional endpoint tests
    test_additional_notes_template_endpoints()
    
    print("\n" + "=" * 60)
    print("🏁 NOTES TEMPLATE BACKEND TESTING COMPLETED")
    print("=" * 60)
    
    if main_tests_passed:
        print("✅ Notes Template backend functionality is working correctly for frontend integration")
        sys.exit(0)
    else:
        print("❌ Notes Template backend has issues that need to be addressed")
        sys.exit(1)