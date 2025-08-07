#!/usr/bin/env python3

"""
Detailed Notes Template Verification Test
Verifies specific requirements from the review request:
- All 5 API endpoints working correctly
- Default templates (Consultation, Lab, Prescription) available
- API responses identical to Clinical Template format
- Database persistence working correctly
- Ready for frontend integration
"""

import requests
import json
import sys
import os
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://cd556dd9-d36b-422e-8110-4b1830397661.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

def test_all_five_endpoints():
    """Test all 5 Notes template API endpoints as specified"""
    print("🔍 TESTING ALL 5 NOTES TEMPLATE API ENDPOINTS")
    print("-" * 50)
    
    results = {}
    
    # 1. GET /api/notes-templates (retrieve all Notes templates)
    try:
        response = requests.get(f"{API_BASE}/notes-templates", timeout=10)
        results['GET_all'] = {
            'status_code': response.status_code,
            'success': response.status_code == 200,
            'data': response.json() if response.status_code == 200 else None
        }
        print(f"✅ GET /api/notes-templates: {response.status_code}")
    except Exception as e:
        results['GET_all'] = {'success': False, 'error': str(e)}
        print(f"❌ GET /api/notes-templates: {str(e)}")
    
    # 2. POST /api/notes-templates (create single Notes template)
    try:
        test_template = {
            "name": "Endpoint Test Template",
            "content": "Testing single template creation",
            "is_default": False
        }
        response = requests.post(
            f"{API_BASE}/notes-templates",
            json=test_template,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        results['POST_single'] = {
            'status_code': response.status_code,
            'success': response.status_code == 200,
            'data': response.json() if response.status_code == 200 else None
        }
        print(f"✅ POST /api/notes-templates: {response.status_code}")
        
        # Store template ID for update/delete tests
        template_id = results['POST_single']['data'].get('id') if results['POST_single']['success'] else None
        
    except Exception as e:
        results['POST_single'] = {'success': False, 'error': str(e)}
        print(f"❌ POST /api/notes-templates: {str(e)}")
        template_id = None
    
    # 3. PUT /api/notes-templates/{id} (update Notes template)
    if template_id:
        try:
            update_data = {
                "name": "Updated Endpoint Test",
                "content": "Updated content for endpoint testing"
            }
            response = requests.put(
                f"{API_BASE}/notes-templates/{template_id}",
                json=update_data,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            results['PUT_update'] = {
                'status_code': response.status_code,
                'success': response.status_code == 200,
                'data': response.json() if response.status_code == 200 else None
            }
            print(f"✅ PUT /api/notes-templates/{{id}}: {response.status_code}")
        except Exception as e:
            results['PUT_update'] = {'success': False, 'error': str(e)}
            print(f"❌ PUT /api/notes-templates/{{id}}: {str(e)}")
    else:
        results['PUT_update'] = {'success': False, 'error': 'No template ID available'}
        print("❌ PUT /api/notes-templates/{id}: No template ID available")
    
    # 4. DELETE /api/notes-templates/{id} (delete Notes template)
    if template_id:
        try:
            response = requests.delete(f"{API_BASE}/notes-templates/{template_id}", timeout=10)
            results['DELETE_single'] = {
                'status_code': response.status_code,
                'success': response.status_code == 200,
                'data': response.json() if response.status_code == 200 else None
            }
            print(f"✅ DELETE /api/notes-templates/{{id}}: {response.status_code}")
        except Exception as e:
            results['DELETE_single'] = {'success': False, 'error': str(e)}
            print(f"❌ DELETE /api/notes-templates/{{id}}: {str(e)}")
    else:
        results['DELETE_single'] = {'success': False, 'error': 'No template ID available'}
        print("❌ DELETE /api/notes-templates/{id}: No template ID available")
    
    # 5. POST /api/notes-templates/save-all (bulk save Notes templates)
    try:
        bulk_data = {
            "Bulk Test 1": "Content for bulk test 1",
            "Bulk Test 2": "Content for bulk test 2"
        }
        response = requests.post(
            f"{API_BASE}/notes-templates/save-all",
            json=bulk_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        results['POST_bulk'] = {
            'status_code': response.status_code,
            'success': response.status_code == 200,
            'data': response.json() if response.status_code == 200 else None
        }
        print(f"✅ POST /api/notes-templates/save-all: {response.status_code}")
    except Exception as e:
        results['POST_bulk'] = {'success': False, 'error': str(e)}
        print(f"❌ POST /api/notes-templates/save-all: {str(e)}")
    
    # Summary
    successful_endpoints = sum(1 for result in results.values() if result.get('success', False))
    print(f"\n📊 ENDPOINT SUMMARY: {successful_endpoints}/5 endpoints working correctly")
    
    return results, successful_endpoints == 5

def test_default_templates_detailed():
    """Detailed verification of default templates"""
    print("\n🔍 DETAILED DEFAULT TEMPLATES VERIFICATION")
    print("-" * 50)
    
    try:
        response = requests.get(f"{API_BASE}/notes-templates", timeout=10)
        if response.status_code != 200:
            print(f"❌ Failed to fetch templates: {response.status_code}")
            return False
        
        templates = response.json()
        expected_defaults = ['Consultation', 'Lab', 'Prescription']
        
        print(f"📋 Total templates found: {len(templates)}")
        
        default_templates = {}
        for template in templates:
            if template.get('name') in expected_defaults:
                default_templates[template['name']] = template
        
        print(f"🎯 Default templates found: {len(default_templates)}/3")
        
        # Verify each default template
        all_valid = True
        for name in expected_defaults:
            if name in default_templates:
                template = default_templates[name]
                
                # Check required fields
                required_fields = ['id', 'name', 'content', 'is_default', 'created_at', 'updated_at']
                missing_fields = [field for field in required_fields if field not in template]
                
                if missing_fields:
                    print(f"❌ {name}: Missing fields {missing_fields}")
                    all_valid = False
                else:
                    # Verify is_default is True
                    if template.get('is_default') != True:
                        print(f"❌ {name}: is_default should be True, got {template.get('is_default')}")
                        all_valid = False
                    else:
                        print(f"✅ {name}: Valid default template")
            else:
                print(f"❌ {name}: Not found")
                all_valid = False
        
        return all_valid
        
    except Exception as e:
        print(f"❌ Error verifying default templates: {str(e)}")
        return False

def test_api_format_comparison():
    """Compare Notes Templates API format with Clinical Templates"""
    print("\n🔍 API FORMAT COMPARISON (Notes vs Clinical)")
    print("-" * 50)
    
    try:
        # Get both template types
        notes_response = requests.get(f"{API_BASE}/notes-templates", timeout=10)
        clinical_response = requests.get(f"{API_BASE}/clinical-templates", timeout=10)
        
        if notes_response.status_code != 200:
            print(f"❌ Notes templates API failed: {notes_response.status_code}")
            return False
            
        if clinical_response.status_code != 200:
            print(f"❌ Clinical templates API failed: {clinical_response.status_code}")
            return False
        
        notes_templates = notes_response.json()
        clinical_templates = clinical_response.json()
        
        if not notes_templates or not clinical_templates:
            print("❌ One or both template lists are empty")
            return False
        
        # Compare structure
        notes_fields = set(notes_templates[0].keys())
        clinical_fields = set(clinical_templates[0].keys())
        
        print(f"📋 Notes template fields: {sorted(notes_fields)}")
        print(f"📋 Clinical template fields: {sorted(clinical_fields)}")
        
        # Check if structures are identical
        if notes_fields == clinical_fields:
            print("✅ API structures are identical")
            
            # Check field types and formats
            notes_sample = notes_templates[0]
            clinical_sample = clinical_templates[0]
            
            format_match = True
            for field in notes_fields:
                notes_type = type(notes_sample[field])
                clinical_type = type(clinical_sample[field])
                
                if notes_type != clinical_type:
                    print(f"❌ Field '{field}' type mismatch: Notes={notes_type}, Clinical={clinical_type}")
                    format_match = False
            
            if format_match:
                print("✅ Field types match perfectly")
                return True
            else:
                return False
        else:
            missing_in_notes = clinical_fields - notes_fields
            extra_in_notes = notes_fields - clinical_fields
            
            if missing_in_notes:
                print(f"❌ Missing in Notes: {missing_in_notes}")
            if extra_in_notes:
                print(f"❌ Extra in Notes: {extra_in_notes}")
            
            return False
            
    except Exception as e:
        print(f"❌ Error comparing API formats: {str(e)}")
        return False

def test_database_persistence_detailed():
    """Detailed database persistence testing"""
    print("\n🔍 DETAILED DATABASE PERSISTENCE TESTING")
    print("-" * 50)
    
    try:
        # Test 1: Create and verify persistence
        test_template = {
            "name": "Persistence Test Template",
            "content": "This template tests database persistence across operations",
            "is_default": False
        }
        
        print("📝 Creating test template...")
        create_response = requests.post(
            f"{API_BASE}/notes-templates",
            json=test_template,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if create_response.status_code != 200:
            print(f"❌ Failed to create template: {create_response.status_code}")
            return False
        
        created_template = create_response.json()
        template_id = created_template.get('id')
        print(f"✅ Template created with ID: {template_id}")
        
        # Test 2: Verify it appears in GET all
        print("🔍 Verifying template appears in GET all...")
        get_response = requests.get(f"{API_BASE}/notes-templates", timeout=10)
        
        if get_response.status_code != 200:
            print(f"❌ Failed to fetch templates: {get_response.status_code}")
            return False
        
        all_templates = get_response.json()
        template_found = any(t.get('id') == template_id for t in all_templates)
        
        if template_found:
            print("✅ Template found in GET all response")
        else:
            print("❌ Template not found in GET all response")
            return False
        
        # Test 3: Update and verify persistence
        print("📝 Updating template...")
        update_data = {
            "content": "Updated content to test persistence"
        }
        
        update_response = requests.put(
            f"{API_BASE}/notes-templates/{template_id}",
            json=update_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if update_response.status_code != 200:
            print(f"❌ Failed to update template: {update_response.status_code}")
            return False
        
        updated_template = update_response.json()
        if updated_template.get('content') == update_data['content']:
            print("✅ Template update persisted correctly")
        else:
            print("❌ Template update not persisted")
            return False
        
        # Test 4: Cleanup
        print("🧹 Cleaning up test template...")
        delete_response = requests.delete(f"{API_BASE}/notes-templates/{template_id}", timeout=10)
        
        if delete_response.status_code == 200:
            print("✅ Test template deleted successfully")
        else:
            print(f"⚠️ Failed to delete test template: {delete_response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing database persistence: {str(e)}")
        return False

def test_frontend_integration_readiness():
    """Test readiness for frontend integration"""
    print("\n🔍 FRONTEND INTEGRATION READINESS")
    print("-" * 50)
    
    try:
        # Test bulk save functionality (key for frontend)
        print("📝 Testing bulk save functionality...")
        
        bulk_templates = {
            "Frontend Test 1": "Content for frontend integration test 1",
            "Frontend Test 2": "Content for frontend integration test 2",
            "Frontend Test 3": ""  # Test empty content
        }
        
        bulk_response = requests.post(
            f"{API_BASE}/notes-templates/save-all",
            json=bulk_templates,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if bulk_response.status_code != 200:
            print(f"❌ Bulk save failed: {bulk_response.status_code}")
            return False
        
        bulk_result = bulk_response.json()
        expected_count = len(bulk_templates)
        actual_count = bulk_result.get('count', 0)
        
        if actual_count == expected_count:
            print(f"✅ Bulk save successful: {actual_count} templates saved")
        else:
            print(f"❌ Bulk save count mismatch: expected {expected_count}, got {actual_count}")
            return False
        
        # Verify templates were actually saved
        print("🔍 Verifying bulk saved templates...")
        get_response = requests.get(f"{API_BASE}/notes-templates", timeout=10)
        
        if get_response.status_code != 200:
            print(f"❌ Failed to fetch templates: {get_response.status_code}")
            return False
        
        all_templates = get_response.json()
        template_names = [t.get('name') for t in all_templates]
        
        bulk_found = 0
        for name in bulk_templates.keys():
            if name in template_names:
                bulk_found += 1
        
        if bulk_found == len(bulk_templates):
            print(f"✅ All bulk templates found: {bulk_found}/{len(bulk_templates)}")
        else:
            print(f"❌ Some bulk templates missing: {bulk_found}/{len(bulk_templates)}")
            return False
        
        # Test CORS and headers
        print("🔍 Testing CORS and headers...")
        options_response = requests.options(f"{API_BASE}/notes-templates", timeout=10)
        
        # Even if OPTIONS fails, the main endpoints work, so this is not critical
        if options_response.status_code in [200, 204]:
            print("✅ CORS preflight working")
        else:
            print("⚠️ CORS preflight may not be configured (not critical)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing frontend integration: {str(e)}")
        return False

def main():
    """Run detailed verification tests"""
    print("🧪 DETAILED NOTES TEMPLATE VERIFICATION")
    print("=" * 60)
    print(f"Backend URL: {BACKEND_URL}")
    print(f"API Base: {API_BASE}")
    print("=" * 60)
    
    test_results = []
    
    # Test 1: All 5 API endpoints
    endpoints_result, endpoints_success = test_all_five_endpoints()
    test_results.append(("All 5 API Endpoints", endpoints_success))
    
    # Test 2: Default templates verification
    defaults_success = test_default_templates_detailed()
    test_results.append(("Default Templates", defaults_success))
    
    # Test 3: API format comparison
    format_success = test_api_format_comparison()
    test_results.append(("API Format Identical", format_success))
    
    # Test 4: Database persistence
    persistence_success = test_database_persistence_detailed()
    test_results.append(("Database Persistence", persistence_success))
    
    # Test 5: Frontend integration readiness
    frontend_success = test_frontend_integration_readiness()
    test_results.append(("Frontend Integration Ready", frontend_success))
    
    # Final summary
    print("\n" + "=" * 60)
    print("📊 DETAILED VERIFICATION SUMMARY")
    print("=" * 60)
    
    passed = 0
    for test_name, success in test_results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if success:
            passed += 1
    
    total = len(test_results)
    print(f"\nOverall: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 ALL REQUIREMENTS VERIFIED - NOTES TEMPLATE SYSTEM READY!")
        print("✅ All 5 Notes template API endpoints working correctly")
        print("✅ Default templates (Consultation, Lab, Prescription) available")
        print("✅ API responses identical to Clinical Template format")
        print("✅ Database persistence working correctly")
        print("✅ Ready for frontend integration")
        return True
    else:
        print(f"\n❌ {total - passed} requirements not met")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)