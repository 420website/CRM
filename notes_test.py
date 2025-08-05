import requests
import unittest
import json
from datetime import datetime, date
import random
import string
import sys
import os
from dotenv import load_dotenv
import time

# Load the frontend .env file to get the backend URL
load_dotenv('/app/frontend/.env')
backend_url = os.environ.get('REACT_APP_BACKEND_URL')

if not backend_url:
    print("❌ Error: REACT_APP_BACKEND_URL not found in frontend .env file")
    sys.exit(1)

print(f"🔗 Using backend URL: {backend_url}")

class NotesAPITester:
    def __init__(self, base_url):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.registration_id = None
        self.note_ids = []

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        if not headers:
            headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    # Check for proper error format if this is an error response
                    if expected_status >= 400 and 'detail' in response_data:
                        print(f"✅ Error message format correct: {response_data['detail']}")
                    return success, response_data
                except:
                    return success, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    response_data = response.json()
                    print(f"Response: {response_data}")
                    # Check if error response has proper format
                    if response.status_code >= 400 and 'detail' in response_data:
                        print(f"✅ Error message format correct: {response_data['detail']}")
                    elif response.status_code >= 400:
                        print("❌ Error response missing 'detail' field")
                    return False, response_data
                except:
                    print(f"Response: {response.text}")
                    return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def create_admin_registration(self):
        """Create a new admin registration for testing notes"""
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
        
        registration_data = {
            "firstName": f"Test{random_suffix}",
            "lastName": f"User{random_suffix}",
            "patientConsent": "Verbal",
            "gender": "Male",
            "province": "Ontario"
        }
        
        success, response = self.run_test(
            "Create Admin Registration",
            "POST",
            "api/admin-register",
            200,
            data=registration_data
        )
        
        if success and 'registration_id' in response:
            self.registration_id = response['registration_id']
            print(f"✅ Created admin registration with ID: {self.registration_id}")
            return True
        else:
            print("❌ Failed to create admin registration")
            return False

    def test_create_note(self, note_text="Test note", note_date=None):
        """Test creating a new note"""
        if not self.registration_id:
            print("❌ No registration ID available. Create a registration first.")
            return False, {}
            
        if not note_date:
            note_date = datetime.now().strftime('%Y-%m-%d')
            
        note_data = {
            "noteDate": note_date,
            "noteText": note_text
        }
        
        success, response = self.run_test(
            f"Create Note: '{note_text}'",
            "POST",
            f"api/admin-registration/{self.registration_id}/note",
            200,
            data=note_data
        )
        
        if success and 'note_id' in response:
            self.note_ids.append(response['note_id'])
            print(f"✅ Created note with ID: {response['note_id']}")
            return True, response
        else:
            print("❌ Failed to create note")
            return False, response

    def test_get_notes(self):
        """Test retrieving all notes for a registration"""
        if not self.registration_id:
            print("❌ No registration ID available. Create a registration first.")
            return False, {}
            
        success, response = self.run_test(
            "Get All Notes",
            "GET",
            f"api/admin-registration/{self.registration_id}/notes",
            200
        )
        
        if success and 'notes' in response:
            notes_count = len(response['notes'])
            print(f"✅ Retrieved {notes_count} notes")
            
            # Verify notes are in descending order by created_at
            if notes_count > 1:
                is_sorted = all(
                    response['notes'][i]['created_at'] >= response['notes'][i+1]['created_at'] 
                    for i in range(notes_count-1)
                )
                if is_sorted:
                    print("✅ Notes are correctly sorted by created_at (newest first)")
                else:
                    print("❌ Notes are NOT correctly sorted by created_at")
            
            return True, response
        else:
            print("❌ Failed to retrieve notes")
            return False, response

    def test_update_note(self, note_id=None, updated_text="Updated note text", updated_date=None):
        """Test updating an existing note"""
        if not self.registration_id:
            print("❌ No registration ID available. Create a registration first.")
            return False, {}
            
        if not note_id and self.note_ids:
            note_id = self.note_ids[0]
        
        if not note_id:
            print("❌ No note ID available. Create a note first.")
            return False, {}
            
        if not updated_date:
            updated_date = datetime.now().strftime('%Y-%m-%d')
            
        update_data = {
            "noteDate": updated_date,
            "noteText": updated_text
        }
        
        success, response = self.run_test(
            f"Update Note: {note_id}",
            "PUT",
            f"api/admin-registration/{self.registration_id}/note/{note_id}",
            200,
            data=update_data
        )
        
        if success:
            print(f"✅ Updated note with ID: {note_id}")
            
            # Verify the update by getting the note
            _, get_response = self.test_get_notes()
            if 'notes' in get_response:
                updated_note = next((note for note in get_response['notes'] if note['id'] == note_id), None)
                if updated_note:
                    if updated_note['noteText'] == updated_text and updated_note['noteDate'] == updated_date:
                        print(f"✅ Verified note update: text='{updated_text}', date='{updated_date}'")
                    else:
                        print(f"❌ Note update verification failed: {updated_note}")
                else:
                    print(f"❌ Could not find updated note with ID: {note_id}")
            
            return True, response
        else:
            print(f"❌ Failed to update note with ID: {note_id}")
            return False, response

    def test_delete_note(self, note_id=None):
        """Test deleting a note"""
        if not self.registration_id:
            print("❌ No registration ID available. Create a registration first.")
            return False, {}
            
        if not note_id and self.note_ids:
            note_id = self.note_ids[-1]  # Use the last created note
            self.note_ids.remove(note_id)  # Remove from our list
        
        if not note_id:
            print("❌ No note ID available. Create a note first.")
            return False, {}
            
        success, response = self.run_test(
            f"Delete Note: {note_id}",
            "DELETE",
            f"api/admin-registration/{self.registration_id}/note/{note_id}",
            200
        )
        
        if success:
            print(f"✅ Deleted note with ID: {note_id}")
            
            # Verify the deletion by getting all notes
            _, get_response = self.test_get_notes()
            if 'notes' in get_response:
                deleted_note = next((note for note in get_response['notes'] if note['id'] == note_id), None)
                if not deleted_note:
                    print(f"✅ Verified note deletion: Note {note_id} no longer exists")
                else:
                    print(f"❌ Note deletion verification failed: Note {note_id} still exists")
            
            return True, response
        else:
            print(f"❌ Failed to delete note with ID: {note_id}")
            return False, response

    def test_invalid_registration_id(self):
        """Test note operations with an invalid registration ID"""
        invalid_id = "invalid-registration-id"
        
        # Test creating a note with invalid registration ID
        success, response = self.run_test(
            "Create Note with Invalid Registration ID",
            "POST",
            f"api/admin-registration/{invalid_id}/note",
            404,
            data={"noteDate": datetime.now().strftime('%Y-%m-%d'), "noteText": "Test note"}
        )
        
        # Test getting notes with invalid registration ID
        success, response = self.run_test(
            "Get Notes with Invalid Registration ID",
            "GET",
            f"api/admin-registration/{invalid_id}/notes",
            404
        )
        
        # Test updating a note with invalid registration ID
        success, response = self.run_test(
            "Update Note with Invalid Registration ID",
            "PUT",
            f"api/admin-registration/{invalid_id}/note/some-note-id",
            404,
            data={"noteDate": datetime.now().strftime('%Y-%m-%d'), "noteText": "Updated note"}
        )
        
        # Test deleting a note with invalid registration ID
        success, response = self.run_test(
            "Delete Note with Invalid Registration ID",
            "DELETE",
            f"api/admin-registration/{invalid_id}/note/some-note-id",
            404
        )
        
        return True, {"message": "Invalid registration ID tests completed"}

    def test_invalid_note_id(self):
        """Test note operations with an invalid note ID"""
        if not self.registration_id:
            print("❌ No registration ID available. Create a registration first.")
            return False, {}
            
        invalid_id = "invalid-note-id"
        
        # Test updating a note with invalid note ID
        success, response = self.run_test(
            "Update Note with Invalid Note ID",
            "PUT",
            f"api/admin-registration/{self.registration_id}/note/{invalid_id}",
            404,
            data={"noteDate": datetime.now().strftime('%Y-%m-%d'), "noteText": "Updated note"}
        )
        
        # Test deleting a note with invalid note ID
        success, response = self.run_test(
            "Delete Note with Invalid Note ID",
            "DELETE",
            f"api/admin-registration/{self.registration_id}/note/{invalid_id}",
            404
        )
        
        return True, {"message": "Invalid note ID tests completed"}

    def test_invalid_note_data(self):
        """Test creating/updating notes with invalid data"""
        if not self.registration_id:
            print("❌ No registration ID available. Create a registration first.")
            return False, {}
            
        # Test creating a note with missing required fields
        success, response = self.run_test(
            "Create Note with Missing noteDate",
            "POST",
            f"api/admin-registration/{self.registration_id}/note",
            422,  # Validation error
            data={"noteText": "Test note without date"}
        )
        
        success, response = self.run_test(
            "Create Note with Missing noteText",
            "POST",
            f"api/admin-registration/{self.registration_id}/note",
            422,  # Validation error
            data={"noteDate": datetime.now().strftime('%Y-%m-%d')}
        )
        
        # Test creating a note with empty fields
        success, response = self.run_test(
            "Create Note with Empty noteText",
            "POST",
            f"api/admin-registration/{self.registration_id}/note",
            422,  # Validation error
            data={"noteDate": datetime.now().strftime('%Y-%m-%d'), "noteText": ""}
        )
        
        # If we have a note ID, test updating with invalid data
        if self.note_ids:
            note_id = self.note_ids[0]
            
            success, response = self.run_test(
                "Update Note with Empty Data",
                "PUT",
                f"api/admin-registration/{self.registration_id}/note/{note_id}",
                200,  # Should succeed with empty update (no changes)
                data={}
            )
        
        return True, {"message": "Invalid note data tests completed"}

    def test_complete_workflow(self):
        """Test the complete notes workflow"""
        print("\n" + "=" * 50)
        print("🔍 Testing Complete Notes Workflow")
        print("=" * 50)
        
        # 1. Create a new admin registration
        if not self.create_admin_registration():
            return False, {"message": "Failed to create admin registration"}
        
        # 2. Create multiple notes with different dates
        self.test_create_note("First test note", "2025-01-01")
        time.sleep(1)  # Small delay to ensure different created_at timestamps
        self.test_create_note("Second test note", "2025-01-02")
        time.sleep(1)
        self.test_create_note("Third test note", "2025-01-03")
        
        # 3. Get all notes and verify count
        success, get_response = self.test_get_notes()
        if not success or 'notes' not in get_response or len(get_response['notes']) != 3:
            print(f"❌ Expected 3 notes, got {len(get_response.get('notes', []))}")
            return False, {"message": "Failed to verify notes count"}
        
        # 4. Update a note
        if self.note_ids:
            self.test_update_note(self.note_ids[0], "Updated first note", "2025-01-10")
        
        # 5. Delete a note
        if len(self.note_ids) > 1:
            self.test_delete_note(self.note_ids[1])
        
        # 6. Get notes again and verify count
        success, get_response = self.test_get_notes()
        if not success or 'notes' not in get_response or len(get_response['notes']) != 2:
            print(f"❌ Expected 2 notes after deletion, got {len(get_response.get('notes', []))}")
            return False, {"message": "Failed to verify notes count after deletion"}
        
        print("\n✅ Complete notes workflow test passed!")
        return True, {"message": "Complete notes workflow test passed"}

    def run_all_tests(self):
        """Run all notes API tests"""
        print("🚀 Starting Notes API Tests")
        print(f"🔗 Base URL: {self.base_url}")
        print("=" * 50)
        
        # Test the complete workflow first
        self.test_complete_workflow()
        
        # Test error handling
        self.test_invalid_registration_id()
        self.test_invalid_note_id()
        self.test_invalid_note_data()
        
        print("\n" + "=" * 50)
        print(f"📊 Tests passed: {self.tests_passed}/{self.tests_run}")
        
        return self.tests_passed == self.tests_run


def main():
    tester = NotesAPITester(backend_url)
    success = tester.run_all_tests()
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())