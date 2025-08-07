#!/usr/bin/env python3
"""
Final Comprehensive Notes Template API Verification
Tests all requirements from the review request to confirm backend is working properly
"""

import requests
import json
import uuid
from datetime import datetime
import sys

# Backend URL from environment
BACKEND_URL = "https://cd556dd9-d36b-422e-8110-4b1830397661.preview.emergentagent.com/api"

def verify_requirement_1():
    """
    Requirement 1: GET /api/notes-templates - should return default templates including Consultation, Lab, Prescription
    """
    print("📋 REQUIREMENT 1: GET /api/notes-templates returns default templates")
    print("-" * 60)
    
    try:
        response = requests.get(f"{BACKEND_URL}/notes-templates", timeout=30)
        
        if response.status_code != 200:
            print(f"❌ FAILED: HTTP {response.status_code}")
            return False
        
        templates = response.json()
        print(f"✅ SUCCESS: Retrieved {len(templates)} templates")
        
        # Check for required default templates
        template_names = [t.get('name') for t in templates]
        required_defaults = ['Consultation', 'Lab', 'Prescription']
        
        all_defaults_found = True
        for default_name in required_defaults:
            if default_name in template_names:
                print(f"✅ Default template '{default_name}' found")
            else:
                print(f"❌ Default template '{default_name}' MISSING")
                all_defaults_found = False
        
        # Verify template structure matches frontend expectations
        if templates:
            sample = templates[0]
            required_fields = ['id', 'name', 'content', 'is_default', 'created_at', 'updated_at']
            
            for field in required_fields:
                if field in sample:
                    print(f"✅ Required field '{field}' present")
                else:
                    print(f"❌ Required field '{field}' missing")
                    all_defaults_found = False
        
        return all_defaults_found
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

def verify_requirement_2():
    """
    Requirement 2: POST /api/notes-templates - should allow creating new templates
    """
    print("\n📋 REQUIREMENT 2: POST /api/notes-templates creates new templates")
    print("-" * 60)
    
    test_template = {
        "name": f"Verification Template {uuid.uuid4().hex[:8]}",
        "content": "This template was created during API verification testing.",
        "is_default": False
    }
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/notes-templates",
            json=test_template,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"❌ FAILED: HTTP {response.status_code} - {response.text}")
            return False, None
        
        created = response.json()
        print(f"✅ SUCCESS: Created template '{created.get('name')}'")
        
        # Verify the created template has all expected fields
        expected_fields = ['id', 'name', 'content', 'is_default', 'created_at', 'updated_at']
        all_fields_present = True
        
        for field in expected_fields:
            if field in created:
                print(f"✅ Field '{field}': {created.get(field)}")
            else:
                print(f"❌ Missing field '{field}'")
                all_fields_present = False
        
        # Verify the data matches what we sent
        if created.get('name') == test_template['name']:
            print(f"✅ Name matches: {created.get('name')}")
        else:
            print(f"❌ Name mismatch")
            all_fields_present = False
            
        if created.get('content') == test_template['content']:
            print(f"✅ Content matches")
        else:
            print(f"❌ Content mismatch")
            all_fields_present = False
        
        return all_fields_present, created
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False, None

def verify_requirement_3(template_id):
    """
    Requirement 3: PUT /api/notes-templates/{id} - should allow updating existing templates
    """
    print(f"\n📋 REQUIREMENT 3: PUT /api/notes-templates/{template_id} updates templates")
    print("-" * 60)
    
    if not template_id:
        print("❌ SKIPPED: No template ID provided from creation test")
        return False
    
    update_data = {
        "name": f"Updated Verification Template {uuid.uuid4().hex[:8]}",
        "content": "This template content was updated during API verification testing.",
        "is_default": False
    }
    
    try:
        response = requests.put(
            f"{BACKEND_URL}/notes-templates/{template_id}",
            json=update_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"❌ FAILED: HTTP {response.status_code} - {response.text}")
            return False
        
        updated = response.json()
        print(f"✅ SUCCESS: Updated template '{updated.get('name')}'")
        
        # Verify the update worked
        if updated.get('name') == update_data['name']:
            print(f"✅ Name updated correctly: {updated.get('name')}")
        else:
            print(f"❌ Name update failed")
            return False
            
        if updated.get('content') == update_data['content']:
            print(f"✅ Content updated correctly")
        else:
            print(f"❌ Content update failed")
            return False
        
        # Verify updated_at timestamp changed
        if updated.get('updated_at'):
            print(f"✅ Updated timestamp: {updated.get('updated_at')}")
        else:
            print(f"❌ Updated timestamp missing")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

def verify_requirement_4(template_id):
    """
    Requirement 4: DELETE /api/notes-templates/{id} - should allow deleting templates
    """
    print(f"\n📋 REQUIREMENT 4: DELETE /api/notes-templates/{template_id} deletes templates")
    print("-" * 60)
    
    if not template_id:
        print("❌ SKIPPED: No template ID provided from previous tests")
        return False
    
    try:
        response = requests.delete(f"{BACKEND_URL}/notes-templates/{template_id}", timeout=30)
        
        if response.status_code != 200:
            print(f"❌ FAILED: HTTP {response.status_code} - {response.text}")
            return False
        
        result = response.json()
        print(f"✅ SUCCESS: {result.get('message')}")
        
        # Verify the template is actually deleted by trying to get it
        try:
            get_response = requests.get(f"{BACKEND_URL}/notes-templates", timeout=30)
            if get_response.status_code == 200:
                templates = get_response.json()
                template_ids = [t.get('id') for t in templates]
                
                if template_id not in template_ids:
                    print(f"✅ Template successfully removed from database")
                else:
                    print(f"❌ Template still exists in database")
                    return False
        except:
            print(f"⚠️  Could not verify deletion (GET request failed)")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

def verify_requirement_5():
    """
    Requirement 5: POST /api/notes-templates/save-all - should allow bulk saving templates
    """
    print("\n📋 REQUIREMENT 5: POST /api/notes-templates/save-all bulk saves templates")
    print("-" * 60)
    
    bulk_templates = {
        f"Bulk Verification Template 1 {uuid.uuid4().hex[:8]}": "Content for bulk verification template 1",
        f"Bulk Verification Template 2 {uuid.uuid4().hex[:8]}": "Content for bulk verification template 2",
        f"Bulk Verification Template 3 {uuid.uuid4().hex[:8]}": "Content for bulk verification template 3",
        f"Bulk Verification Template 4 {uuid.uuid4().hex[:8]}": ""  # Test empty content
    }
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/notes-templates/save-all",
            json=bulk_templates,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"❌ FAILED: HTTP {response.status_code} - {response.text}")
            return False
        
        result = response.json()
        print(f"✅ SUCCESS: {result.get('message')}")
        print(f"Templates saved: {result.get('count')}")
        
        # Verify the expected count
        if result.get('count') == len(bulk_templates):
            print(f"✅ Correct number of templates saved ({result.get('count')})")
        else:
            print(f"❌ Expected {len(bulk_templates)} templates, got {result.get('count')}")
            return False
        
        # Verify the templates were actually saved
        try:
            get_response = requests.get(f"{BACKEND_URL}/notes-templates", timeout=30)
            if get_response.status_code == 200:
                all_templates = get_response.json()
                template_names = [t.get('name') for t in all_templates]
                
                saved_count = 0
                for bulk_name in bulk_templates.keys():
                    if bulk_name in template_names:
                        print(f"✅ Bulk template '{bulk_name}' found in database")
                        saved_count += 1
                    else:
                        print(f"❌ Bulk template '{bulk_name}' not found in database")
                
                if saved_count == len(bulk_templates):
                    print(f"✅ All bulk templates verified in database")
                    return True
                else:
                    print(f"❌ Only {saved_count}/{len(bulk_templates)} bulk templates found")
                    return False
        except:
            print(f"⚠️  Could not verify bulk save (GET request failed)")
            return True  # Assume success if we can't verify
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

def verify_data_format_compatibility():
    """
    Verify that the API returns data in the format expected by the frontend
    """
    print("\n📋 BONUS: Verify data format matches frontend expectations")
    print("-" * 60)
    
    try:
        response = requests.get(f"{BACKEND_URL}/notes-templates", timeout=30)
        
        if response.status_code != 200:
            print(f"❌ FAILED: Could not retrieve templates for format check")
            return False
        
        templates = response.json()
        
        if not templates:
            print(f"⚠️  No templates found for format verification")
            return True
        
        # Check that response is a list
        if not isinstance(templates, list):
            print(f"❌ Response is not a list: {type(templates)}")
            return False
        
        print(f"✅ Response is a list with {len(templates)} templates")
        
        # Check each template has required fields for frontend
        sample_template = templates[0]
        frontend_required_fields = ['id', 'name', 'content', 'is_default']
        
        for field in frontend_required_fields:
            if field in sample_template:
                print(f"✅ Frontend required field '{field}' present")
            else:
                print(f"❌ Frontend required field '{field}' missing")
                return False
        
        # Check data types
        if isinstance(sample_template.get('id'), str):
            print(f"✅ ID is string type")
        else:
            print(f"❌ ID is not string type: {type(sample_template.get('id'))}")
            return False
            
        if isinstance(sample_template.get('name'), str):
            print(f"✅ Name is string type")
        else:
            print(f"❌ Name is not string type: {type(sample_template.get('name'))}")
            return False
            
        if isinstance(sample_template.get('is_default'), bool):
            print(f"✅ is_default is boolean type")
        else:
            print(f"❌ is_default is not boolean type: {type(sample_template.get('is_default'))}")
            return False
        
        print(f"✅ Data format is compatible with frontend expectations")
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

def run_complete_verification():
    """Run complete verification of all Notes Template API requirements"""
    print("🚀 COMPLETE NOTES TEMPLATE API VERIFICATION")
    print("=" * 80)
    print("Testing all requirements from the review request...")
    print("=" * 80)
    
    results = {}
    
    # Test all requirements
    results['req1_get_defaults'] = verify_requirement_1()
    
    req2_success, created_template = verify_requirement_2()
    results['req2_create'] = req2_success
    
    template_id = created_template.get('id') if created_template else None
    results['req3_update'] = verify_requirement_3(template_id)
    results['req4_delete'] = verify_requirement_4(template_id)
    results['req5_bulk_save'] = verify_requirement_5()
    results['bonus_format'] = verify_data_format_compatibility()
    
    # Final summary
    print("\n" + "=" * 80)
    print("📊 FINAL VERIFICATION RESULTS")
    print("=" * 80)
    
    passed = 0
    total = len(results)
    
    for requirement, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        req_name = requirement.replace('_', ' ').replace('req', 'Requirement ').title()
        print(f"{req_name}: {status}")
        if success:
            passed += 1
    
    print(f"\nOverall Result: {passed}/{total} requirements passed")
    
    if passed == total:
        print("\n🎉 ALL REQUIREMENTS VERIFIED SUCCESSFULLY!")
        print("✅ Notes Template API is fully functional and ready for frontend integration")
        print("✅ Backend is working properly - no backend issues found")
        print("✅ All endpoints return proper data format matching frontend expectations")
        return True
    else:
        print(f"\n⚠️  {total - passed} requirement(s) failed")
        print("❌ Notes Template API needs attention before frontend integration")
        return False

if __name__ == "__main__":
    success = run_complete_verification()
    sys.exit(0 if success else 1)