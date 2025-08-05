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

    def test_medication_crud(self):
        """Test basic CRUD operations for medications"""
        print("\n" + "=" * 50)
        print("🔍 Testing Medication CRUD Operations")
        print("=" * 50)
        
        if not self.registration_id:
            if not self.create_admin_registration():
                print("❌ Cannot proceed with medication tests without a registration")
                return False
        
        # Test 1: Create a medication
        medication_data = {
            "medication": "Ecplusa",
            "start_date": "2025-01-01",
            "end_date": "2025-02-01",
            "outcome": "Completed"
        }
        
        success, response = self.run_test(
            "Create Medication",
            "POST",
            f"api/admin-registration/{self.registration_id}/medication",
            200,
            data=medication_data
        )
        
        if not success or 'medication_id' not in response:
            print("❌ Failed to create medication")
            return False
        
        medication_id = response['medication_id']
        self.medication_ids.append(medication_id)
        print(f"✅ Created medication with ID: {medication_id}")
        
        # Test 2: Get all medications
        success, response = self.run_test(
            "Get All Medications",
            "GET",
            f"api/admin-registration/{self.registration_id}/medications",
            200
        )
        
        if not success or 'medications' not in response:
            print("❌ Failed to get medications")
            return False
        
        medications = response['medications']
        if len(medications) == 0:
            print("❌ No medications found")
            return False
        
        print(f"✅ Retrieved {len(medications)} medications")
        
        # Test 3: Update a medication
        update_data = {
            "medication": "Ecplusa",
            "outcome": "Side Effect",  # Changed outcome
            "end_date": "2025-01-15"   # Changed end date
        }
        
        success, response = self.run_test(
            "Update Medication",
            "PUT",
            f"api/admin-registration/{self.registration_id}/medication/{medication_id}",
            200,
            data=update_data
        )
        
        if not success:
            print("❌ Failed to update medication")
            return False
        
        print(f"✅ Updated medication with ID: {medication_id}")
        
        # Test 4: Verify the update
        success, response = self.run_test(
            "Get Medications After Update",
            "GET",
            f"api/admin-registration/{self.registration_id}/medications",
            200
        )
        
        if not success or 'medications' not in response:
            print("❌ Failed to get medications after update")
            return False
        
        medications = response['medications']
        updated_med = next((med for med in medications if med['id'] == medication_id), None)
        
        if not updated_med:
            print(f"❌ Could not find updated medication with ID: {medication_id}")
            return False
        
        update_verified = True
        for key, value in update_data.items():
            if updated_med.get(key) != value:
                print(f"❌ Update verification failed: {key} = {updated_med.get(key)}, expected {value}")
                update_verified = False
        
        if not update_verified:
            print("❌ Update verification failed")
            return False
        
        print("✅ Update verification successful")
        
        # Test 5: Delete a medication
        success, response = self.run_test(
            "Delete Medication",
            "DELETE",
            f"api/admin-registration/{self.registration_id}/medication/{medication_id}",
            200
        )
        
        if not success:
            print("❌ Failed to delete medication")
            return False
        
        print(f"✅ Deleted medication with ID: {medication_id}")
        
        # Test 6: Verify the deletion
        success, response = self.run_test(
            "Get Medications After Delete",
            "GET",
            f"api/admin-registration/{self.registration_id}/medications",
            200
        )
        
        if not success or 'medications' not in response:
            print("❌ Failed to get medications after delete")
            return False
        
        medications = response['medications']
        deleted_med = next((med for med in medications if med['id'] == medication_id), None)
        
        if deleted_med:
            print(f"❌ Medication with ID {medication_id} still exists after deletion")
            return False
        
        print(f"✅ Verified medication with ID {medication_id} was deleted")
        
        return True

    def test_medication_validation(self):
        """Test validation for medication endpoints"""
        print("\n" + "=" * 50)
        print("🔍 Testing Medication Validation")
        print("=" * 50)
        
        if not self.registration_id:
            if not self.create_admin_registration():
                print("❌ Cannot proceed with medication tests without a registration")
                return False
        
        # Test 1: Missing required fields
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
        
        # Test 2: Invalid registration ID
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
        
        # Test 3: Invalid medication ID for update
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
        
        # Test 4: Invalid medication ID for delete
        success, response = self.run_test(
            "Delete Medication - Invalid Medication ID",
            "DELETE",
            f"api/admin-registration/{self.registration_id}/medication/{invalid_med_id}",
            404  # Not found
        )
        
        return True

    def test_medication_options(self):
        """Test medication options (Ecplusa, Maviret, Vosevi) and outcome options"""
        print("\n" + "=" * 50)
        print("🔍 Testing Medication Options")
        print("=" * 50)
        
        if not self.registration_id:
            if not self.create_admin_registration():
                print("❌ Cannot proceed with medication tests without a registration")
                return False
        
        # Test each medication option
        medications = ["Ecplusa", "Maviret", "Vosevi"]
        outcomes = ["Completed", "Non Compliance", "Side Effect", "Did not start", "Death"]
        
        for medication in medications:
            for outcome in outcomes:
                medication_data = {
                    "medication": medication,
                    "start_date": "2025-01-01",
                    "end_date": "2025-02-01",
                    "outcome": outcome
                }
                
                success, response = self.run_test(
                    f"Create Medication - {medication} with outcome {outcome}",
                    "POST",
                    f"api/admin-registration/{self.registration_id}/medication",
                    200,
                    data=medication_data
                )
                
                if not success or 'medication_id' not in response:
                    print(f"❌ Failed to create medication {medication} with outcome {outcome}")
                    return False
                
                medication_id = response['medication_id']
                self.medication_ids.append(medication_id)
                print(f"✅ Created medication {medication} with outcome {outcome}, ID: {medication_id}")
        
        # Verify all medications were created
        success, response = self.run_test(
            "Get All Medications",
            "GET",
            f"api/admin-registration/{self.registration_id}/medications",
            200
        )
        
        if not success or 'medications' not in response:
            print("❌ Failed to get medications")
            return False
        
        medications = response['medications']
        print(f"✅ Retrieved {len(medications)} medications")
        
        # Verify that all created medications are in the list
        found_ids = [med['id'] for med in medications]
        all_found = True
        for med_id in self.medication_ids:
            if med_id in found_ids:
                print(f"✅ Found medication ID: {med_id}")
            else:
                print(f"❌ Medication ID not found: {med_id}")
                all_found = False
        
        if not all_found:
            print("❌ Not all medications were found")
            return False
        
        return True

    def test_complete_workflow(self):
        """Test the complete workflow from registration to medications"""
        print("\n" + "=" * 50)
        print("🔍 Testing Complete Workflow: Registration + Medications")
        print("=" * 50)
        
        # Step 1: Create a new admin registration
        admin_data = self.generate_test_data()
        
        success, response = self.run_test(
            "Step 1: Create Admin Registration",
            "POST",
            "api/admin-register",
            200,
            data=admin_data
        )
        
        if not success or 'registration_id' not in response:
            print("❌ Failed to create admin registration - cannot continue workflow test")
            return False
        
        self.registration_id = response['registration_id']
        print(f"✅ Created admin registration with ID: {self.registration_id}")
        
        # Step 2: Add multiple medications to the registration
        print("\n" + "=" * 50)
        print("Step 2: Adding Multiple Medications")
        print("=" * 50)
        
        medications = [
            {
                "medication": "Ecplusa",
                "start_date": "2025-01-01",
                "end_date": "2025-02-01",
                "outcome": "Completed"
            },
            {
                "medication": "Maviret",
                "start_date": "2025-03-01",
                "end_date": "2025-04-01",
                "outcome": "Non Compliance"
            },
            {
                "medication": "Vosevi",
                "start_date": "2025-05-01",
                "outcome": "Side Effect"
            }
        ]
        
        for i, med_data in enumerate(medications):
            success, response = self.run_test(
                f"Add Medication {i+1}: {med_data['medication']} - {med_data['outcome']}",
                "POST",
                f"api/admin-registration/{self.registration_id}/medication",
                200,
                data=med_data
            )
            
            if success and 'medication_id' in response:
                medication_id = response['medication_id']
                self.medication_ids.append(medication_id)
                print(f"✅ Added medication with ID: {medication_id}")
            else:
                print(f"❌ Failed to add medication {i+1}")
        
        # Step 3: Retrieve medications and verify sequential order
        print("\n" + "=" * 50)
        print("Step 3: Retrieving Medications and Verifying Order")
        print("=" * 50)
        
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
            all_found = True
            for med_id in self.medication_ids:
                if med_id in found_ids:
                    print(f"✅ Found medication ID: {med_id}")
                else:
                    print(f"❌ Medication ID not found: {med_id}")
                    all_found = False
            
            # Verify medications are sorted by created_at (newest first)
            if len(medications) > 1:
                is_sorted = all(medications[i]['created_at'] >= medications[i+1]['created_at'] 
                               for i in range(len(medications)-1))
                if is_sorted:
                    print("✅ Medications are correctly sorted by created_at (newest first)")
                else:
                    print("❌ Medications are not correctly sorted")
                    all_found = False
            
            if not all_found:
                print("❌ Not all medications were found or sorting is incorrect")
                return False
        else:
            print("❌ Failed to retrieve medications")
            return False
        
        # Step 4: Update medications
        print("\n" + "=" * 50)
        print("Step 4: Updating Medications")
        print("=" * 50)
        
        if len(self.medication_ids) >= 2:
            # Update the first medication
            update_data = {
                "medication": "Ecplusa",
                "outcome": "Side Effect",  # Changed outcome
                "end_date": "2025-01-15"   # Changed end date
            }
            
            success, response = self.run_test(
                f"Update Medication: {self.medication_ids[0]}",
                "PUT",
                f"api/admin-registration/{self.registration_id}/medication/{self.medication_ids[0]}",
                200,
                data=update_data
            )
            
            if not success:
                print("❌ Failed to update medication")
                return False
            
            # Verify the update was applied
            success, response = self.run_test(
                "Get Medications After Update",
                "GET",
                f"api/admin-registration/{self.registration_id}/medications",
                200
            )
            
            if success and 'medications' in response:
                medications = response['medications']
                updated_med = next((med for med in medications if med['id'] == self.medication_ids[0]), None)
                
                if updated_med:
                    update_verified = True
                    for key, value in update_data.items():
                        if updated_med.get(key) != value:
                            print(f"❌ Update verification failed: {key} = {updated_med.get(key)}, expected {value}")
                            update_verified = False
                    
                    if update_verified:
                        print("✅ Update verification successful")
                    else:
                        print("❌ Update verification failed")
                        return False
                else:
                    print(f"❌ Could not find updated medication with ID: {self.medication_ids[0]}")
                    return False
            else:
                print("❌ Failed to verify update")
                return False
        else:
            print("⚠️ Not enough medications to test updates")
        
        # Step 5: Delete medications
        print("\n" + "=" * 50)
        print("Step 5: Deleting Medications")
        print("=" * 50)
        
        if len(self.medication_ids) >= 3:
            # Delete the third medication
            success, response = self.run_test(
                f"Delete Medication: {self.medication_ids[2]}",
                "DELETE",
                f"api/admin-registration/{self.registration_id}/medication/{self.medication_ids[2]}",
                200
            )
            
            if not success:
                print("❌ Failed to delete medication")
                return False
            
            # Verify the deletion
            success, response = self.run_test(
                "Get Medications After Delete",
                "GET",
                f"api/admin-registration/{self.registration_id}/medications",
                200
            )
            
            if success and 'medications' in response:
                medications = response['medications']
                deleted_med = next((med for med in medications if med['id'] == self.medication_ids[2]), None)
                
                if deleted_med:
                    print(f"❌ Medication with ID {self.medication_ids[2]} still exists after deletion")
                    return False
                else:
                    print(f"✅ Verified medication with ID {self.medication_ids[2]} was deleted")
                    
                    # Remove from our list
                    self.medication_ids.remove(self.medication_ids[2])
            else:
                print("❌ Failed to verify deletion")
                return False
        else:
            print("⚠️ Not enough medications to test deletion")
        
        print("\n" + "=" * 50)
        print("✅ Complete Workflow Test Passed!")
        print("=" * 50)
        
        return True

    def run_all_tests(self):
        """Run all medication API tests"""
        print("🚀 Starting Medication API Tests")
        print(f"🔗 Base URL: {self.base_url}")
        
        # Run basic CRUD tests
        crud_success = self.test_medication_crud()
        
        # Run validation tests
        validation_success = self.test_medication_validation()
        
        # Run medication options tests
        options_success = self.test_medication_options()
        
        # Run complete workflow test
        workflow_success = self.test_complete_workflow()
        
        print("\n" + "=" * 50)
        print(f"📊 Tests passed: {self.tests_passed}/{self.tests_run}")
        print(f"📊 CRUD tests: {'✅ Passed' if crud_success else '❌ Failed'}")
        print(f"📊 Validation tests: {'✅ Passed' if validation_success else '❌ Failed'}")
        print(f"📊 Options tests: {'✅ Passed' if options_success else '❌ Failed'}")
        print(f"📊 Workflow test: {'✅ Passed' if workflow_success else '❌ Failed'}")
        
        return self.tests_passed == self.tests_run and crud_success and validation_success and options_success and workflow_success


def main():
    tester = MedicationAPITester(backend_url)
    success = tester.run_all_tests()
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())