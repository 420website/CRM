#!/usr/bin/env python3
"""
Additional Notes CRUD Test - Testing UPDATE and DELETE operations specifically
"""

import requests
import json
import uuid
from datetime import datetime, date
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

def test_notes_update_delete():
    base_url = os.getenv('REACT_APP_BACKEND_URL', 'http://localhost:8001')
    if not base_url.endswith('/api'):
        base_url += '/api'
    
    print(f"🔧 Testing Notes UPDATE/DELETE at: {base_url}")
    print("=" * 60)
    
    # Create test registration
    registration_data = {
        "firstName": "UpdateDelete",
        "lastName": "TestUser",
        "patientConsent": "verbal",
        "province": "Ontario"
    }
    
    response = requests.post(f"{base_url}/admin-register", json=registration_data)
    if response.status_code != 200:
        print("❌ Failed to create test registration")
        return False
    
    registration_id = response.json().get('registration_id')
    print(f"✅ Created test registration: {registration_id}")
    
    # Create a test note
    note_data = {
        "noteDate": "2025-01-14",
        "noteText": "Original note content for testing UPDATE/DELETE",
        "templateType": "Consultation"
    }
    
    response = requests.post(f"{base_url}/admin-registration/{registration_id}/note", json=note_data)
    if response.status_code != 200:
        print("❌ Failed to create test note")
        return False
    
    result = response.json()
    note_id = result.get('note_id')
    print(f"✅ Created test note: {note_id}")
    
    # Test UPDATE operation
    update_data = {
        "noteText": "UPDATED note content - testing UPDATE operation",
        "templateType": "Lab"
    }
    
    response = requests.put(f"{base_url}/admin-registration/{registration_id}/note/{note_id}", json=update_data)
    if response.status_code == 200:
        print("✅ UPDATE operation successful")
        
        # Verify the update
        response = requests.get(f"{base_url}/admin-registration/{registration_id}/notes")
        if response.status_code == 200:
            notes = response.json().get('notes', [])
            updated_note = next((n for n in notes if n['id'] == note_id), None)
            
            if updated_note and updated_note['noteText'] == update_data['noteText']:
                print("✅ UPDATE verification successful - content updated correctly")
            else:
                print("❌ UPDATE verification failed - content not updated")
                return False
        else:
            print("❌ Failed to verify UPDATE")
            return False
    else:
        print(f"❌ UPDATE operation failed: {response.status_code}")
        return False
    
    # Test DELETE operation
    response = requests.delete(f"{base_url}/admin-registration/{registration_id}/note/{note_id}")
    if response.status_code == 200:
        print("✅ DELETE operation successful")
        
        # Verify the deletion
        response = requests.get(f"{base_url}/admin-registration/{registration_id}/notes")
        if response.status_code == 200:
            notes = response.json().get('notes', [])
            deleted_note = next((n for n in notes if n['id'] == note_id), None)
            
            if not deleted_note:
                print("✅ DELETE verification successful - note removed")
            else:
                print("❌ DELETE verification failed - note still exists")
                return False
        else:
            print("❌ Failed to verify DELETE")
            return False
    else:
        print(f"❌ DELETE operation failed: {response.status_code}")
        return False
    
    print("\n🎉 All UPDATE/DELETE operations working correctly!")
    return True

if __name__ == "__main__":
    success = test_notes_update_delete()
    if success:
        print("\n✅ Notes UPDATE/DELETE functionality verified")
        exit(0)
    else:
        print("\n❌ Notes UPDATE/DELETE functionality has issues")
        exit(1)