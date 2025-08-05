import requests
import unittest
import json
from datetime import datetime, date
import random
import string
import sys
import os
from dotenv import load_dotenv

# Load the frontend .env file to get the backend URL
load_dotenv('/app/frontend/.env')
backend_url = os.environ.get('REACT_APP_BACKEND_URL')

if not backend_url:
    print("❌ Error: REACT_APP_BACKEND_URL not found in frontend .env file")
    sys.exit(1)

print(f"🔗 Using backend URL: {backend_url}")

class MedicationAPITester:
    def __init__(self, base_url):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.registration_id = None
        self.medication_ids = []

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

    def generate_test_data(self):
        """Generate random test data for admin registration"""
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
        
        admin_registration = {
            "firstName": f"Test{random_suffix}",
            "lastName": f"User{random_suffix}",
            "patientConsent": "Verbal",
            "gender": "Male",
            "province": "Ontario",
            "disposition": "POCT NEG",
            "healthCard": ''.join(random.choices(string.digits, k=10)),
            "email": f"test.user.{random_suffix}@example.com"
        }
        
        return admin_registration

    def create_admin_registration(self):
        """Create a new admin registration for testing medications"""
        admin_data = self.generate_test_data()
        
        success, response = self.run_test(
            "Create Admin Registration",
            "POST",
            "api/admin-register",
            200,
            data=admin_data
        )
        
        if success and 'registration_id' in response:
            self.registration_id = response['registration_id']
            print(f"✅ Created admin registration with ID: {self.registration_id}")
            return True
        else:
            print("❌ Failed to create admin registration")
            return False

    def test_create_medication(self, medication_data):
        """Test creating a new medication"""
        if not self.registration_id:
            print("❌ No registration ID available. Create a registration first.")
            return False, {}
        
        success, response = self.run_test(
            f"Create Medication ({medication_data['medication']})",
            "POST",
            f"api/admin-registration/{self.registration_id}/medication",
            200,
            data=medication_data
        )
        
        if success and 'medication_id' in response:
            medication_id = response['medication_id']
            self.medication_ids.append(medication_id)
            print(f"✅ Created medication with ID: {medication_id}")
            return True, medication_id
        else:
            print("❌ Failed to create medication")
            return False, None

    def test_get_medications(self):
        """Test getting all medications for a registration"""
        if not self.registration_id:
            print("❌ No registration ID available. Create a registration first.")
            return False, {}
        
        success, response = self.run_test(
            "Get All Medications",
            "GET",
            f"api/admin-registration/{self.registration_id}/medications",
            200
        )
        
        if success and 'medications' in response:
            medications = response['medications']
            print(f"✅ Retrieved {len(medications)} medications")
            
            # Verify that all created medications are in the list
            found_ids = [med['id'] for med in medications]
            for med_id in self.medication_ids:
                if med_id in found_ids:
                    print(f"✅ Found medication ID: {med_id}")
                else:
                    print(f"❌ Medication ID not found: {med_id}")
                    success = False
            
            # Verify medications are sorted by created_at (newest first)
            if len(medications) > 1:
                is_sorted = all(medications[i]['created_at'] >= medications[i+1]['created_at'] 
                               for i in range(len(medications)-1))
                if is_sorted:
                    print("✅ Medications are correctly sorted by created_at (newest first)")
                else:
                    print("❌ Medications are not correctly sorted")
                    success = False
            
            return success, medications
        else:
            print("❌ Failed to retrieve medications")
            return False, []

    def test_update_medication(self, medication_id, update_data):
        """Test updating an existing medication"""
        if not self.registration_id:
            print("❌ No registration ID available. Create a registration first.")
            return False, {}
        
        success, response = self.run_test(
            f"Update Medication ({medication_id})",
            "PUT",
            f"api/admin-registration/{self.registration_id}/medication/{medication_id}",
            200,
            data=update_data
        )
        
        if success:
            print(f"✅ Updated medication with ID: {medication_id}")
            
            # Verify the update was applied by getting the medication
            get_success, get_response = self.run_test(
                "Get Medications After Update",
                "GET",
                f"api/admin-registration/{self.registration_id}/medications",
                200
            )
            
            if get_success and 'medications' in get_response:
                medications = get_response['medications']
                updated_med = next((med for med in medications if med['id'] == medication_id), None)
                
                if updated_med:
                    update_verified = True
                    for key, value in update_data.items():
                        if updated_med.get(key) != value:
                            print(f"❌ Update verification failed: {key} = {updated_med.get(key)}, expected {value}")
                            update_verified = False
                    
                    if update_verified:
                        print("✅ Update verification successful")
                    else:
                        success = False
                else:
                    print(f"❌ Could not find updated medication with ID: {medication_id}")
                    success = False
            else:
                print("❌ Failed to verify update")
                success = False
            
            return success, response
        else:
            print(f"❌ Failed to update medication with ID: {medication_id}")
            return False, {}

    def test_delete_medication(self, medication_id):
        """Test deleting a medication"""
        if not self.registration_id:
            print("❌ No registration ID available. Create a registration first.")
            return False, {}
        
        success, response = self.run_test(
            f"Delete Medication ({medication_id})",
            "DELETE",
            f"api/admin-registration/{self.registration_id}/medication/{medication_id}",
            200
        )
        
        if success:
            print(f"✅ Deleted medication with ID: {medication_id}")
            
            # Remove from our list of medication IDs
            if medication_id in self.medication_ids:
                self.medication_ids.remove(medication_id)
            
            # Verify the deletion by getting all medications
            get_success, get_response = self.run_test(
                "Get Medications After Delete",
                "GET",
                f"api/admin-registration/{self.registration_id}/medications",
                200
            )
            
            if get_success and 'medications' in get_response:
                medications = get_response['medications']
                deleted_med = next((med for med in medications if med['id'] == medication_id), None)
                
                if deleted_med:
                    print(f"❌ Medication with ID {medication_id} still exists after deletion")
                    success = False
                else:
                    print(f"✅ Verified medication with ID {medication_id} was deleted")
            else:
                print("❌ Failed to verify deletion")
                success = False
            
            return success, response
        else:
            print(f"❌ Failed to delete medication with ID: {medication_id}")
            return False, {}

    def test_validation_errors(self):
        """Test validation errors for medication endpoints"""
        if not self.registration_id:
            print("❌ No registration ID available. Create a registration first.")
            return False
        
        # Test missing required fields
        missing_medication = {
            "start_date": "2025-01-01",
            "end_date": "2025-02-01",
            "outcome": "Completed"
        }
        
        success, response = self.run_test(
            "Create Medication - Missing Required Field (medication)",
            "POST",
            f"api/admin-registration/{self.registration_id}/medication",
            422,  # Validation error
            data=missing_medication
        )
        
        missing_outcome = {
            "medication": "Ecplusa",
            "start_date": "2025-01-01",
            "end_date": "2025-02-01"
        }
        
        success, response = self.run_test(
            "Create Medication - Missing Required Field (outcome)",
            "POST",
            f"api/admin-registration/{self.registration_id}/medication",
            422,  # Validation error
            data=missing_outcome
        )
        
        # Test invalid registration ID
        invalid_reg_id = "invalid-registration-id"
        
        success, response = self.run_test(
            "Create Medication - Invalid Registration ID",
            "POST",
            f"api/admin-registration/{invalid_reg_id}/medication",
            404,  # Not found
            data={
                "medication": "Ecplusa",
                "start_date": "2025-01-01",
                "end_date": "2025-02-01",
                "outcome": "Completed"
            }
        )
        
        # Test invalid medication ID for update
        invalid_med_id = "invalid-medication-id"
        
        success, response = self.run_test(
            "Update Medication - Invalid Medication ID",
            "PUT",
            f"api/admin-registration/{self.registration_id}/medication/{invalid_med_id}",
            404,  # Not found
            data={
                "medication": "Maviret",
                "outcome": "Completed"
            }
        )
        
        # Test invalid medication ID for delete
        success, response = self.run_test(
            "Delete Medication - Invalid Medication ID",
            "DELETE",
            f"api/admin-registration/{self.registration_id}/medication/{invalid_med_id}",
            404  # Not found
        )
        
        return True

    def run_all_tests(self):
        """Run all medication API tests"""
        print("🚀 Starting Medication API Tests")
        print(f"🔗 Base URL: {self.base_url}")
        print("=" * 50)
        
        # Create a registration for testing
        if not self.create_admin_registration():
            print("❌ Cannot proceed with medication tests without a registration")
            return False
        
        # Test creating medications with different data
        medication1 = {
            "medication": "Ecplusa",
            "start_date": "2025-01-01",
            "end_date": "2025-02-01",
            "outcome": "Completed"
        }
        
        medication2 = {
            "medication": "Maviret",
            "start_date": "2025-03-01",
            "end_date": "2025-04-01",
            "outcome": "Non Compliance"
        }
        
        medication3 = {
            "medication": "Vosevi",
            "start_date": "2025-05-01",
            "outcome": "Side Effect"  # No end_date (optional field)
        }
        
        # Create medications
        success1, med_id1 = self.test_create_medication(medication1)
        success2, med_id2 = self.test_create_medication(medication2)
        success3, med_id3 = self.test_create_medication(medication3)
        
        # Get all medications
        self.test_get_medications()
        
        # Update a medication
        if success2 and med_id2:
            update_data = {
                "medication": "Maviret",
                "outcome": "Completed",
                "end_date": "2025-04-15"  # Changed end date
            }
            self.test_update_medication(med_id2, update_data)
        
        # Delete a medication
        if success3 and med_id3:
            self.test_delete_medication(med_id3)
        
        # Test validation errors
        self.test_validation_errors()
        
        # Final get to verify state
        self.test_get_medications()
        
        print("\n" + "=" * 50)
        print(f"📊 Tests passed: {self.tests_passed}/{self.tests_run}")
        
        return self.tests_passed == self.tests_run


def main():
    tester = MedicationAPITester(backend_url)
    success = tester.run_all_tests()
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())