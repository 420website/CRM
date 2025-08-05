#!/usr/bin/env python3

import requests
import json
import os
from dotenv import load_dotenv
import random
import string
from datetime import date

def test_backend_crud_operations():
    """Test CRUD operations for various backend entities"""
    
    # Load environment variables
    load_dotenv('/app/frontend/.env')
    backend_url = os.environ.get('REACT_APP_BACKEND_URL')
    
    if not backend_url:
        print("❌ Error: REACT_APP_BACKEND_URL not found in frontend .env file")
        return False
    
    print(f"🔗 Testing CRUD operations at: {backend_url}")
    print("=" * 60)
    
    tests_passed = 0
    tests_total = 0
    
    def run_test(name, method, endpoint, expected_status, data=None):
        nonlocal tests_passed, tests_total
        tests_total += 1
        
        url = f"{backend_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        print(f"\n🔍 Testing {name}...")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=30)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=30)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=30)
            
            if response.status_code == expected_status:
                tests_passed += 1
                print(f"✅ PASSED - Status: {response.status_code}")
                try:
                    return True, response.json()
                except:
                    return True, {}
            else:
                print(f"❌ FAILED - Expected {expected_status}, got {response.status_code}")
                try:
                    print(f"Response: {response.json()}")
                except:
                    print(f"Response: {response.text}")
                return False, {}
                
        except Exception as e:
            print(f"❌ FAILED - Error: {str(e)}")
            return False, {}
    
    # Generate test data
    random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    
    # First, create a test registration to use for CRUD operations
    admin_registration_data = {
        "firstName": f"CRUD{random_suffix}",
        "lastName": f"Test{random_suffix}",
        "patientConsent": "Verbal",
        "email": f"crud.{random_suffix}@example.com",
        "phone1": "4161234567",
        "city": "Toronto",
        "province": "Ontario"
    }
    
    success, reg_response = run_test("Create Test Registration for CRUD", "POST", "api/admin-register", 200, admin_registration_data)
    if not success or 'registration_id' not in reg_response:
        print("❌ Cannot proceed with CRUD tests - failed to create test registration")
        return False
    
    registration_id = reg_response['registration_id']
    print(f"   Using registration ID: {registration_id}")
    
    # Test Notes CRUD
    print("\n" + "=" * 40)
    print("📝 Testing Notes CRUD Operations")
    print("=" * 40)
    
    # Create Note
    note_data = {
        "noteDate": "2025-01-15",
        "noteText": f"Test note content {random_suffix}",
        "templateType": "Consultation"
    }
    
    success, note_response = run_test("Create Note", "POST", f"api/admin-registration/{registration_id}/note", 200, note_data)
    note_id = None
    if success and 'note_id' in note_response:
        note_id = note_response['note_id']
        print(f"   Created note with ID: {note_id}")
    
    # Get Notes
    success, notes_data = run_test("Get Notes", "GET", f"api/admin-registration/{registration_id}/notes", 200)
    if success:
        print(f"   Retrieved {len(notes_data.get('notes', []))} notes")
    
    # Update Note (if created successfully)
    if note_id:
        update_note_data = {
            "noteText": f"Updated note content {random_suffix}",
            "templateType": "Lab"
        }
        success, _ = run_test("Update Note", "PUT", f"api/admin-registration/{registration_id}/note/{note_id}", 200, update_note_data)
    
    # Test Test Records CRUD
    print("\n" + "=" * 40)
    print("🧪 Testing Test Records CRUD Operations")
    print("=" * 40)
    
    # Create Test Record
    test_record_data = {
        "test_type": "HIV",
        "test_date": "2025-01-15",
        "hiv_result": "negative",
        "hiv_type": "Type 1",
        "hiv_tester": "CM"
    }
    
    success, test_response = run_test("Create Test Record", "POST", f"api/admin-registration/{registration_id}/test", 200, test_record_data)
    test_id = None
    if success and 'test_id' in test_response:
        test_id = test_response['test_id']
        print(f"   Created test record with ID: {test_id}")
    
    # Get Test Records
    success, tests_data = run_test("Get Test Records", "GET", f"api/admin-registration/{registration_id}/tests", 200)
    if success:
        print(f"   Retrieved {len(tests_data.get('tests', []))} test records")
    
    # Update Test Record (if created successfully)
    if test_id:
        update_test_data = {
            "hiv_result": "positive",
            "hiv_type": "Type 2"
        }
        success, _ = run_test("Update Test Record", "PUT", f"api/admin-registration/{registration_id}/test/{test_id}", 200, update_test_data)
    
    # Test Interactions CRUD
    print("\n" + "=" * 40)
    print("🤝 Testing Interactions CRUD Operations")
    print("=" * 40)
    
    # Create Interaction
    interaction_data = {
        "date": "2025-01-15",
        "description": "Screening",
        "amount": "50.00",
        "payment_type": "Cash",
        "issued": "Yes"
    }
    
    success, interaction_response = run_test("Create Interaction", "POST", f"api/admin-registration/{registration_id}/interaction", 200, interaction_data)
    interaction_id = None
    if success and 'interaction_id' in interaction_response:
        interaction_id = interaction_response['interaction_id']
        print(f"   Created interaction with ID: {interaction_id}")
    
    # Get Interactions
    success, interactions_data = run_test("Get Interactions", "GET", f"api/admin-registration/{registration_id}/interactions", 200)
    if success:
        print(f"   Retrieved {len(interactions_data.get('interactions', []))} interactions")
    
    # Test Activities CRUD
    print("\n" + "=" * 40)
    print("📅 Testing Activities CRUD Operations")
    print("=" * 40)
    
    # Create Activity
    activity_data = {
        "date": "2025-01-15",
        "time": "14:30",
        "description": f"Test activity {random_suffix}"
    }
    
    success, activity_response = run_test("Create Activity", "POST", f"api/admin-registration/{registration_id}/activity", 200, activity_data)
    activity_id = None
    if success and 'activity_id' in activity_response:
        activity_id = activity_response['activity_id']
        print(f"   Created activity with ID: {activity_id}")
    
    # Get Activities
    success, activities_data = run_test("Get Activities", "GET", f"api/admin-registration/{registration_id}/activities", 200)
    if success:
        print(f"   Retrieved {len(activities_data.get('activities', []))} activities")
    
    # Test Template Management
    print("\n" + "=" * 40)
    print("📋 Testing Template Management")
    print("=" * 40)
    
    # Create Custom Notes Template
    notes_template_data = {
        "name": f"Test Template {random_suffix}",
        "content": f"Test template content {random_suffix}",
        "is_default": False
    }
    
    success, template_response = run_test("Create Notes Template", "POST", "api/notes-templates", 200, notes_template_data)
    template_id = None
    if success and 'template_id' in template_response:
        template_id = template_response['template_id']
        print(f"   Created notes template with ID: {template_id}")
    
    # Create Custom Clinical Template
    clinical_template_data = {
        "name": f"Test Clinical {random_suffix}",
        "content": f"Test clinical template content {random_suffix}",
        "is_default": False
    }
    
    success, clinical_response = run_test("Create Clinical Template", "POST", "api/clinical-templates", 200, clinical_template_data)
    clinical_id = None
    if success and 'template_id' in clinical_response:
        clinical_id = clinical_response['template_id']
        print(f"   Created clinical template with ID: {clinical_id}")
    
    # Clean up - Delete created templates
    if template_id:
        success, _ = run_test("Delete Notes Template", "DELETE", f"api/notes-templates/{template_id}", 200)
    
    if clinical_id:
        success, _ = run_test("Delete Clinical Template", "DELETE", f"api/clinical-templates/{clinical_id}", 200)
    
    # Summary
    print("\n" + "=" * 60)
    print(f"📊 CRUD OPERATIONS TEST RESULTS")
    print(f"Tests Passed: {tests_passed}/{tests_total}")
    print(f"Success Rate: {(tests_passed/tests_total)*100:.1f}%")
    
    if tests_passed == tests_total:
        print("🎉 ALL CRUD TESTS PASSED - Backend functionality is working correctly")
        return True
    else:
        print("⚠️  Some CRUD tests failed - Backend issues detected")
        return False

if __name__ == "__main__":
    success = test_backend_crud_operations()
    exit(0 if success else 1)