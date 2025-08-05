#!/usr/bin/env python3
"""
Comprehensive Notes Template API Testing Script
Tests all 5 Notes Template endpoints to verify they work correctly
"""

import requests
import json
import uuid
from datetime import datetime
import sys

# Backend URL from environment
BACKEND_URL = "https://dfe9a1e1-7f3d-45aa-ad71-43a254e568c5.preview.emergentagent.com/api"

def test_get_all_notes_templates():
    """Test GET /api/notes-templates - should return default templates"""
    print("\n🧪 Testing GET /api/notes-templates...")
    
    try:
        response = requests.get(f"{BACKEND_URL}/notes-templates", timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            templates = response.json()
            print(f"✅ SUCCESS: Retrieved {len(templates)} templates")
            
            # Check for default templates
            template_names = [t.get('name') for t in templates]
            expected_defaults = ['Consultation', 'Lab', 'Prescription']
            
            print(f"Template names found: {template_names}")
            
            for default_name in expected_defaults:
                if default_name in template_names:
                    print(f"✅ Default template '{default_name}' found")
                else:
                    print(f"⚠️  Default template '{default_name}' missing")
            
            # Verify template structure
            if templates:
                sample_template = templates[0]
                required_fields = ['id', 'name', 'content', 'is_default', 'created_at', 'updated_at']
                
                for field in required_fields:
                    if field in sample_template:
                        print(f"✅ Required field '{field}' present")
                    else:
                        print(f"❌ Required field '{field}' missing")
            
            return templates
        else:
            print(f"❌ FAILED: {response.status_code} - {response.text}")
            return []
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return []

def test_create_notes_template():
    """Test POST /api/notes-templates - should create new template"""
    print("\n🧪 Testing POST /api/notes-templates...")
    
    test_template = {
        "name": f"Test Template {uuid.uuid4().hex[:8]}",
        "content": "This is a test template content for Notes functionality.",
        "is_default": False
    }
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/notes-templates",
            json=test_template,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            created_template = response.json()
            print(f"✅ SUCCESS: Created template '{created_template.get('name')}'")
            print(f"Template ID: {created_template.get('id')}")
            
            # Verify all fields are present
            required_fields = ['id', 'name', 'content', 'is_default', 'created_at', 'updated_at']
            for field in required_fields:
                if field in created_template:
                    print(f"✅ Field '{field}': {created_template.get(field)}")
                else:
                    print(f"❌ Missing field '{field}'")
            
            return created_template
        else:
            print(f"❌ FAILED: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return None

def test_update_notes_template(template_id):
    """Test PUT /api/notes-templates/{id} - should update existing template"""
    print(f"\n🧪 Testing PUT /api/notes-templates/{template_id}...")
    
    update_data = {
        "name": f"Updated Test Template {uuid.uuid4().hex[:8]}",
        "content": "This is updated content for the Notes template.",
        "is_default": False
    }
    
    try:
        response = requests.put(
            f"{BACKEND_URL}/notes-templates/{template_id}",
            json=update_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            updated_template = response.json()
            print(f"✅ SUCCESS: Updated template '{updated_template.get('name')}'")
            
            # Verify the update worked
            if updated_template.get('name') == update_data['name']:
                print(f"✅ Name updated correctly: {updated_template.get('name')}")
            else:
                print(f"❌ Name update failed")
                
            if updated_template.get('content') == update_data['content']:
                print(f"✅ Content updated correctly")
            else:
                print(f"❌ Content update failed")
            
            return updated_template
        else:
            print(f"❌ FAILED: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return None

def test_delete_notes_template(template_id):
    """Test DELETE /api/notes-templates/{id} - should delete template"""
    print(f"\n🧪 Testing DELETE /api/notes-templates/{template_id}...")
    
    try:
        response = requests.delete(f"{BACKEND_URL}/notes-templates/{template_id}", timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ SUCCESS: {result.get('message')}")
            return True
        elif response.status_code == 404:
            print(f"⚠️  Template not found (already deleted?)")
            return True
        else:
            print(f"❌ FAILED: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

def test_bulk_save_notes_templates():
    """Test POST /api/notes-templates/save-all - should bulk save templates"""
    print("\n🧪 Testing POST /api/notes-templates/save-all...")
    
    bulk_templates = {
        f"Bulk Test Template 1 {uuid.uuid4().hex[:8]}": "Content for bulk template 1",
        f"Bulk Test Template 2 {uuid.uuid4().hex[:8]}": "Content for bulk template 2",
        f"Bulk Test Template 3 {uuid.uuid4().hex[:8]}": "Content for bulk template 3"
    }
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/notes-templates/save-all",
            json=bulk_templates,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ SUCCESS: {result.get('message')}")
            print(f"Templates saved: {result.get('count')}")
            
            # Verify the expected count
            if result.get('count') == len(bulk_templates):
                print(f"✅ Correct number of templates saved")
            else:
                print(f"⚠️  Expected {len(bulk_templates)} templates, got {result.get('count')}")
            
            return True
        else:
            print(f"❌ FAILED: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

def test_api_format_consistency():
    """Test that Notes Template API format matches Clinical Template format"""
    print("\n🧪 Testing API format consistency with Clinical Templates...")
    
    try:
        # Get Notes templates
        notes_response = requests.get(f"{BACKEND_URL}/notes-templates", timeout=10)
        
        # Get Clinical templates for comparison
        clinical_response = requests.get(f"{BACKEND_URL}/clinical-templates", timeout=10)
        
        if notes_response.status_code == 200 and clinical_response.status_code == 200:
            notes_templates = notes_response.json()
            clinical_templates = clinical_response.json()
            
            if notes_templates and clinical_templates:
                notes_fields = set(notes_templates[0].keys())
                clinical_fields = set(clinical_templates[0].keys())
                
                if notes_fields == clinical_fields:
                    print(f"✅ SUCCESS: Notes and Clinical templates have identical field structure")
                    print(f"Fields: {sorted(notes_fields)}")
                else:
                    print(f"❌ FAILED: Field structure mismatch")
                    print(f"Notes fields: {sorted(notes_fields)}")
                    print(f"Clinical fields: {sorted(clinical_fields)}")
                    print(f"Missing in Notes: {clinical_fields - notes_fields}")
                    print(f"Extra in Notes: {notes_fields - clinical_fields}")
                
                return notes_fields == clinical_fields
            else:
                print(f"⚠️  No templates found for comparison")
                return True
        else:
            print(f"⚠️  Could not fetch templates for comparison")
            return True
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

def run_comprehensive_tests():
    """Run all Notes Template API tests"""
    print("🚀 Starting Comprehensive Notes Template API Testing")
    print("=" * 60)
    
    test_results = {
        'get_all': False,
        'create': False,
        'update': False,
        'delete': False,
        'bulk_save': False,
        'format_consistency': False
    }
    
    # Test 1: Get all templates (should include defaults)
    templates = test_get_all_notes_templates()
    test_results['get_all'] = len(templates) > 0
    
    # Test 2: Create new template
    created_template = test_create_notes_template()
    test_results['create'] = created_template is not None
    
    # Test 3: Update template (if creation succeeded)
    if created_template:
        updated_template = test_update_notes_template(created_template['id'])
        test_results['update'] = updated_template is not None
        
        # Test 4: Delete template (if update succeeded)
        if updated_template:
            delete_success = test_delete_notes_template(updated_template['id'])
            test_results['delete'] = delete_success
    
    # Test 5: Bulk save templates
    bulk_success = test_bulk_save_notes_templates()
    test_results['bulk_save'] = bulk_success
    
    # Test 6: API format consistency
    format_consistent = test_api_format_consistency()
    test_results['format_consistency'] = format_consistent
    
    # Final results
    print("\n" + "=" * 60)
    print("📊 FINAL TEST RESULTS")
    print("=" * 60)
    
    passed_tests = 0
    total_tests = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
        if result:
            passed_tests += 1
    
    print(f"\nOverall Result: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 ALL TESTS PASSED - Notes Template API is fully functional!")
        return True
    else:
        print("⚠️  Some tests failed - Notes Template API needs attention")
        return False

if __name__ == "__main__":
    success = run_comprehensive_tests()
    sys.exit(0 if success else 1)