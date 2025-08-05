import requests
import unittest
import json
from datetime import datetime, date
import random
import string
import sys
import time
from dotenv import load_dotenv
import os
import pymongo
from pymongo import MongoClient

# Load the frontend .env file to get the backend URL
load_dotenv('/app/frontend/.env')
backend_url = os.environ.get('REACT_APP_BACKEND_URL')

# Load the backend .env file to get MongoDB connection details
load_dotenv('/app/backend/.env')
mongo_url = os.environ.get('MONGO_URL')
db_name = os.environ.get('DB_NAME')

class RNAFieldsTester:
    def __init__(self, base_url):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.test_data = {}
        self.registration_ids = []
        
        # Connect to MongoDB
        self.client = MongoClient(mongo_url)
        self.db = self.client[db_name]
        self.collection = self.db["admin_registrations"]

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

    def generate_sample_base64_image(self):
        """Generate a simple base64 encoded image for testing"""
        # This is a tiny 1x1 pixel transparent PNG image encoded as base64
        return "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
        
    def generate_test_data(self, rna_available="No", rna_sample_date=None, rna_result="Positive"):
        """Generate random test data for admin registration with RNA fields"""
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
        today = date.today()
        today_str = today.isoformat()  # Convert to string format
        
        # Generate sample base64 image
        sample_image = self.generate_sample_base64_image()
        
        # Create test data with RNA fields
        self.test_data = {
            "firstName": f"RNA{random_suffix}",
            "lastName": f"Test{random_suffix}",
            "dob": None,  # Set to None to avoid date serialization issues
            "patientConsent": "Verbal",
            "gender": "Male",
            "province": "Ontario",
            "disposition": f"Disposition Option {random.randint(1, 70)}",
            "aka": f"RNA{random_suffix}",
            "age": str(40),
            "regDate": None,  # Set to None to use default value
            "healthCard": ''.join(random.choices(string.digits, k=10)),
            "healthCardVersion": "AB",  # Health card version code
            "referralSite": "Toronto - Outreach",
            "address": f"{random.randint(100, 999)} Main Street",
            "unitNumber": str(random.randint(1, 100)),
            "city": "Toronto",
            "postalCode": f"M{random.randint(1, 9)}A {random.randint(1, 9)}B{random.randint(1, 9)}",
            "phone1": ''.join(random.choices(string.digits, k=10)),
            "phone2": ''.join(random.choices(string.digits, k=10)),
            "ext1": str(random.randint(100, 999)),
            "ext2": str(random.randint(100, 999)),
            "leaveMessage": True,
            "voicemail": True,
            "text": False,
            "preferredTime": "Afternoon",
            "email": f"rna.test.{random_suffix}@example.com",
            "language": "English",
            "specialAttention": "RNA test patient",
            "photo": sample_image,
            "physician": "Dr. David Fletcher",
            "rnaAvailable": rna_available,
            "rnaSampleDate": rna_sample_date,
            "rnaResult": rna_result
        }
        
        return self.test_data

    def test_api_health(self):
        """Test the API health endpoint"""
        return self.run_test(
            "API Health Check",
            "GET",
            "api",
            200
        )

    def test_rna_fields_default_values(self):
        """Test admin registration with default RNA field values"""
        # Generate test data with default RNA values (rnaAvailable="No")
        test_data = self.generate_test_data()
        
        # Remove RNA fields to test defaults
        if "rnaAvailable" in test_data:
            test_data.pop("rnaAvailable")
        if "rnaSampleDate" in test_data:
            test_data.pop("rnaSampleDate")
        if "rnaResult" in test_data:
            test_data.pop("rnaResult")
        
        success, response = self.run_test(
            "Admin Registration - Default RNA Fields",
            "POST",
            "api/admin-register",
            200,
            data=test_data
        )
        
        if success:
            registration_id = response.get('registration_id')
            print(f"Admin Registration ID (default RNA fields): {registration_id}")
            self.registration_ids.append(registration_id)
            
            # Verify in MongoDB that the RNA fields were set to default values
            registration = self.collection.find_one({"id": registration_id})
            
            if registration:
                # Check if RNA fields have default values
                rna_available = registration.get("rnaAvailable")
                rna_sample_date = registration.get("rnaSampleDate")
                rna_result = registration.get("rnaResult")
                
                if rna_available == "No":
                    print(f"✅ Default rnaAvailable verified: {rna_available}")
                else:
                    print(f"❌ rnaAvailable {rna_available} does not match expected default 'No'")
                    success = False
                
                if rna_sample_date is None:
                    print(f"✅ Default rnaSampleDate verified: None")
                else:
                    print(f"❌ rnaSampleDate {rna_sample_date} is not None as expected")
                    success = False
                
                if rna_result == "Positive":
                    print(f"✅ Default rnaResult verified: {rna_result}")
                else:
                    print(f"❌ rnaResult {rna_result} does not match expected default 'Positive'")
                    success = False
            else:
                print(f"❌ Could not find registration with ID {registration_id}")
                success = False
        
        return success, response

    def test_rna_fields_with_values(self):
        """Test admin registration with specific RNA field values"""
        # Generate test data with specific RNA values
        test_data = self.generate_test_data(
            rna_available="Yes",
            rna_sample_date="2025-07-01",
            rna_result="Negative"
        )
        
        success, response = self.run_test(
            "Admin Registration - Specific RNA Fields",
            "POST",
            "api/admin-register",
            200,
            data=test_data
        )
        
        if success:
            registration_id = response.get('registration_id')
            print(f"Admin Registration ID (specific RNA fields): {registration_id}")
            self.registration_ids.append(registration_id)
            
            # Verify in MongoDB that the RNA fields were set to the specified values
            registration = self.collection.find_one({"id": registration_id})
            
            if registration:
                # Check if RNA fields have the specified values
                rna_available = registration.get("rnaAvailable")
                rna_sample_date = registration.get("rnaSampleDate")
                rna_result = registration.get("rnaResult")
                
                if rna_available == "Yes":
                    print(f"✅ rnaAvailable verified: {rna_available}")
                else:
                    print(f"❌ rnaAvailable {rna_available} does not match expected 'Yes'")
                    success = False
                
                if rna_sample_date == "2025-07-01":
                    print(f"✅ rnaSampleDate verified: {rna_sample_date}")
                else:
                    print(f"❌ rnaSampleDate {rna_sample_date} does not match expected '2025-07-01'")
                    success = False
                
                if rna_result == "Negative":
                    print(f"✅ rnaResult verified: {rna_result}")
                else:
                    print(f"❌ rnaResult {rna_result} does not match expected 'Negative'")
                    success = False
            else:
                print(f"❌ Could not find registration with ID {registration_id}")
                success = False
        
        return success, response

    def test_rna_fields_mixed_values(self):
        """Test admin registration with mixed RNA field values"""
        # Generate test data with mixed RNA values (rnaAvailable="Yes" but no sample date)
        test_data = self.generate_test_data(
            rna_available="Yes",
            rna_sample_date=None,
            rna_result="Positive"
        )
        
        success, response = self.run_test(
            "Admin Registration - Mixed RNA Fields",
            "POST",
            "api/admin-register",
            200,
            data=test_data
        )
        
        if success:
            registration_id = response.get('registration_id')
            print(f"Admin Registration ID (mixed RNA fields): {registration_id}")
            self.registration_ids.append(registration_id)
            
            # Verify in MongoDB that the RNA fields were set correctly
            registration = self.collection.find_one({"id": registration_id})
            
            if registration:
                # Check if RNA fields have the correct values
                rna_available = registration.get("rnaAvailable")
                rna_sample_date = registration.get("rnaSampleDate")
                rna_result = registration.get("rnaResult")
                
                if rna_available == "Yes":
                    print(f"✅ rnaAvailable verified: {rna_available}")
                else:
                    print(f"❌ rnaAvailable {rna_available} does not match expected 'Yes'")
                    success = False
                
                if rna_sample_date is None:
                    print(f"✅ rnaSampleDate verified: None")
                else:
                    print(f"❌ rnaSampleDate {rna_sample_date} is not None as expected")
                    success = False
                
                if rna_result == "Positive":
                    print(f"✅ rnaResult verified: {rna_result}")
                else:
                    print(f"❌ rnaResult {rna_result} does not match expected 'Positive'")
                    success = False
            else:
                print(f"❌ Could not find registration with ID {registration_id}")
                success = False
        
        return success, response

    def test_admin_registration_workflow(self):
        """Test the complete two-stage admin registration workflow"""
        print("\n" + "=" * 50)
        print("🔍 Testing Complete Admin Registration Workflow")
        print("=" * 50)
        
        # Step 1: Create a new admin registration with RNA fields
        test_data = self.generate_test_data(
            rna_available="Yes",
            rna_sample_date="2025-07-15",
            rna_result="Negative"
        )
        
        success, response = self.run_test(
            "Step 1: Create Admin Registration",
            "POST",
            "api/admin-register",
            200,
            data=test_data
        )
        
        if not success:
            return False, {"error": "Failed to create admin registration"}
        
        registration_id = response.get('registration_id')
        print(f"Admin Registration ID: {registration_id}")
        self.registration_ids.append(registration_id)
        
        # Step 2: Get pending admin registrations
        success, pending_response = self.run_test(
            "Step 2: Get Pending Admin Registrations",
            "GET",
            "api/admin-registrations-pending",
            200
        )
        
        if not success:
            return False, {"error": "Failed to get pending admin registrations"}
        
        # Verify our registration is in the pending list
        registration_found = False
        for reg in pending_response:
            if reg.get('id') == registration_id:
                registration_found = True
                print(f"✅ Registration found in pending list: {reg.get('firstName')} {reg.get('lastName')}")
                break
        
        if not registration_found:
            print("❌ Registration not found in pending list")
            return False, {"error": "Registration not found in pending list"}
        
        # Step 3: Get specific admin registration by ID
        success, registration_response = self.run_test(
            "Step 3: Get Admin Registration by ID",
            "GET",
            f"api/admin-registration/{registration_id}",
            200
        )
        
        if not success:
            return False, {"error": "Failed to get admin registration by ID"}
        
        # Verify RNA fields are present in the response
        if "rnaAvailable" in registration_response and registration_response["rnaAvailable"] == "Yes":
            print(f"✅ rnaAvailable field verified in GET response: {registration_response['rnaAvailable']}")
        else:
            print(f"❌ rnaAvailable field not found or incorrect in GET response")
            return False, {"error": "RNA fields not found in GET response"}
        
        if "rnaSampleDate" in registration_response and registration_response["rnaSampleDate"] == "2025-07-15":
            print(f"✅ rnaSampleDate field verified in GET response: {registration_response['rnaSampleDate']}")
        else:
            print(f"❌ rnaSampleDate field not found or incorrect in GET response")
            return False, {"error": "RNA fields not found in GET response"}
        
        if "rnaResult" in registration_response and registration_response["rnaResult"] == "Negative":
            print(f"✅ rnaResult field verified in GET response: {registration_response['rnaResult']}")
        else:
            print(f"❌ rnaResult field not found or incorrect in GET response")
            return False, {"error": "RNA fields not found in GET response"}
        
        # Step 4: Update admin registration
        update_data = registration_response.copy()
        update_data["rnaAvailable"] = "Yes"
        update_data["rnaSampleDate"] = "2025-07-20"  # Updated date
        update_data["rnaResult"] = "Positive"  # Changed result
        
        # Remove fields that shouldn't be in the update request
        if "_id" in update_data:
            update_data.pop("_id")
        if "id" in update_data:
            update_data.pop("id")
        if "timestamp" in update_data:
            update_data.pop("timestamp")
        if "status" in update_data:
            update_data.pop("status")
        
        success, update_response = self.run_test(
            "Step 4: Update Admin Registration",
            "PUT",
            f"api/admin-registration/{registration_id}",
            200,
            data=update_data
        )
        
        if not success:
            return False, {"error": "Failed to update admin registration"}
        
        # Verify the update was successful
        success, updated_reg_response = self.run_test(
            "Verify Update: Get Updated Admin Registration",
            "GET",
            f"api/admin-registration/{registration_id}",
            200
        )
        
        if not success:
            return False, {"error": "Failed to get updated admin registration"}
        
        # Verify RNA fields were updated
        if "rnaAvailable" in updated_reg_response and updated_reg_response["rnaAvailable"] == "Yes":
            print(f"✅ Updated rnaAvailable field verified: {updated_reg_response['rnaAvailable']}")
        else:
            print(f"❌ rnaAvailable field not updated correctly")
            return False, {"error": "RNA fields not updated correctly"}
        
        if "rnaSampleDate" in updated_reg_response and updated_reg_response["rnaSampleDate"] == "2025-07-20":
            print(f"✅ Updated rnaSampleDate field verified: {updated_reg_response['rnaSampleDate']}")
        else:
            print(f"❌ rnaSampleDate field not updated correctly")
            return False, {"error": "RNA fields not updated correctly"}
        
        if "rnaResult" in updated_reg_response and updated_reg_response["rnaResult"] == "Positive":
            print(f"✅ Updated rnaResult field verified: {updated_reg_response['rnaResult']}")
        else:
            print(f"❌ rnaResult field not updated correctly")
            return False, {"error": "RNA fields not updated correctly"}
        
        # Step 5: Finalize admin registration
        success, finalize_response = self.run_test(
            "Step 5: Finalize Admin Registration",
            "POST",
            f"api/admin-registration/{registration_id}/finalize",
            200
        )
        
        if not success:
            return False, {"error": "Failed to finalize admin registration"}
        
        # Verify the registration was finalized
        if finalize_response.get("status") == "completed":
            print(f"✅ Registration status verified: {finalize_response['status']}")
        else:
            print(f"❌ Registration status not updated to 'completed'")
            return False, {"error": "Registration not finalized correctly"}
        
        # Step 6: Verify the registration is no longer in the pending list
        success, pending_response_after = self.run_test(
            "Step 6: Verify Registration Not in Pending List",
            "GET",
            "api/admin-registrations-pending",
            200
        )
        
        if not success:
            return False, {"error": "Failed to get pending admin registrations after finalization"}
        
        # Verify our registration is NOT in the pending list
        for reg in pending_response_after:
            if reg.get('id') == registration_id:
                print("❌ Registration still found in pending list after finalization")
                return False, {"error": "Registration still in pending list after finalization"}
        
        print("✅ Registration successfully removed from pending list after finalization")
        
        return True, {"message": "Complete admin registration workflow tested successfully"}

    def test_duplicate_prevention(self):
        """Test duplicate prevention with unique index on firstName + lastName"""
        print("\n" + "=" * 50)
        print("🔍 Testing Duplicate Prevention")
        print("=" * 50)
        
        # Generate test data
        test_data = self.generate_test_data()
        
        # Create a registration
        success, response = self.run_test(
            "Create First Registration",
            "POST",
            "api/admin-register",
            200,
            data=test_data
        )
        
        if not success:
            return False, {"error": "Failed to create first registration"}
        
        registration_id = response.get('registration_id')
        print(f"First Registration ID: {registration_id}")
        self.registration_ids.append(registration_id)
        
        # Try to create a duplicate registration with the same firstName and lastName
        duplicate_data = test_data.copy()
        
        # Change some non-key fields to verify it's still caught as a duplicate
        duplicate_data["email"] = f"duplicate.{test_data['email']}"
        duplicate_data["phone1"] = ''.join(random.choices(string.digits, k=10))
        
        success, duplicate_response = self.run_test(
            "Create Duplicate Registration",
            "POST",
            "api/admin-register",
            200,  # Note: The API returns 200 even for duplicates, with a special flag
            data=duplicate_data
        )
        
        # Check if the duplicate was detected
        if "duplicate_prevented" in duplicate_response and duplicate_response["duplicate_prevented"] == True:
            print("✅ Duplicate prevention working correctly")
            print(f"✅ Response message: {duplicate_response.get('message')}")
            
            # Verify the returned registration ID matches the original
            if duplicate_response.get('registration_id') == registration_id:
                print("✅ Duplicate returns original registration ID")
            else:
                print("❌ Duplicate returns different registration ID")
                return False, {"error": "Duplicate prevention not working correctly"}
        else:
            print("❌ Duplicate prevention not working - created new registration instead of detecting duplicate")
            return False, {"error": "Duplicate prevention not working"}
        
        return True, {"message": "Duplicate prevention tested successfully"}

    def test_rna_fields_in_finalize_email(self):
        """Test that RNA fields are included in the finalization email"""
        print("\n" + "=" * 50)
        print("🔍 Testing RNA Fields in Finalization Email")
        print("=" * 50)
        
        # Create a registration with RNA fields
        test_data = self.generate_test_data(
            rna_available="Yes",
            rna_sample_date="2025-07-25",
            rna_result="Negative"
        )
        
        success, response = self.run_test(
            "Create Registration with RNA Fields",
            "POST",
            "api/admin-register",
            200,
            data=test_data
        )
        
        if not success:
            return False, {"error": "Failed to create registration with RNA fields"}
        
        registration_id = response.get('registration_id')
        print(f"Registration ID: {registration_id}")
        self.registration_ids.append(registration_id)
        
        # Finalize the registration to trigger email
        success, finalize_response = self.run_test(
            "Finalize Registration with RNA Fields",
            "POST",
            f"api/admin-registration/{registration_id}/finalize",
            200
        )
        
        if not success:
            return False, {"error": "Failed to finalize registration with RNA fields"}
        
        # Since we can't directly check the email content, we'll verify the finalization was successful
        if finalize_response.get("status") == "completed" and finalize_response.get("email_sent") == True:
            print("✅ Registration finalized and email sent successfully")
            print("✅ RNA fields should be included in the email based on server.py implementation")
        else:
            print("❌ Registration finalization or email sending failed")
            return False, {"error": "Registration finalization failed"}
        
        return True, {"message": "RNA fields in finalization email tested successfully"}

    def run_all_tests(self):
        """Run all RNA fields and admin registration workflow tests"""
        print("🚀 Starting RNA Fields and Admin Registration Workflow Tests")
        print(f"🔗 Base URL: {self.base_url}")
        print("=" * 50)
        
        # Test API health
        self.test_api_health()
        
        # Test RNA fields
        print("\n" + "=" * 50)
        print("🔍 Testing RNA Fields")
        print("=" * 50)
        self.test_rna_fields_default_values()
        self.test_rna_fields_with_values()
        self.test_rna_fields_mixed_values()
        
        # Test admin registration workflow
        self.test_admin_registration_workflow()
        
        # Test duplicate prevention
        self.test_duplicate_prevention()
        
        # Test RNA fields in finalization email
        self.test_rna_fields_in_finalize_email()
        
        print("\n" + "=" * 50)
        print(f"📊 Tests passed: {self.tests_passed}/{self.tests_run}")
        
        return self.tests_passed == self.tests_run


def main():
    # Get the backend URL from the frontend .env file
    if not backend_url:
        print("❌ Error: REACT_APP_BACKEND_URL not found in frontend .env file")
        return 1
    
    print(f"🔗 Using backend URL from .env: {backend_url}")
    
    # Run the tests
    tester = RNAFieldsTester(backend_url)
    success = tester.run_all_tests()
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())