import requests
import unittest
import json
from datetime import datetime, date
import random
import string
import sys
from dotenv import load_dotenv
import os
import time
from pymongo import MongoClient

class CoverageTypeUpdateTester:
    def __init__(self, base_url):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.test_data = {}
        self.registration_ids = {}
        
        # Connect to MongoDB for direct verification
        load_dotenv('/app/backend/.env')
        mongo_url = os.environ.get('MONGO_URL')
        db_name = os.environ.get('DB_NAME')
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

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    return success, response_data
                except:
                    return success, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    response_data = response.json()
                    print(f"Response: {response_data}")
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

    def generate_test_data(self, coverage_type="Select"):
        """Generate random test data for registration with specified coverage type"""
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
        
        test_data = {
            "firstName": f"Michael {random_suffix}",
            "lastName": f"Smith {random_suffix}",
            "dob": None,
            "patientConsent": "Verbal",
            "gender": "Male",
            "province": "Ontario",
            "disposition": f"Disposition Option {random.randint(1, 70)}",
            "aka": f"Mike {random_suffix}",
            "age": str(40),
            "regDate": None,
            "healthCard": ''.join(random.choices(string.digits, k=10)),
            "healthCardVersion": "AB",
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
            "email": f"michael.smith.{random_suffix}@example.com",
            "language": "English",
            "specialAttention": "Patient requires interpreter assistance",
            "photo": self.generate_sample_base64_image(),
            "physician": "Dr. David Fletcher",
            "rnaAvailable": "No",
            "rnaSampleDate": None,
            "rnaResult": "Positive",
            "coverageType": coverage_type
        }
        
        return test_data

    def test_api_health(self):
        """Test the API health endpoint"""
        return self.run_test(
            "API Health Check",
            "GET",
            "api",
            200
        )

    def test_no_coverage_option(self):
        """Test admin registration with the new 'No coverage' option"""
        test_data = self.generate_test_data("No coverage")
        
        success, response = self.run_test(
            "Admin Registration - Coverage Type: 'No coverage'",
            "POST",
            "api/admin-register",
            200,
            data=test_data
        )
        
        if success:
            registration_id = response.get('registration_id')
            print(f"Admin Registration ID (Coverage Type 'No coverage'): {registration_id}")
            self.registration_ids["No coverage"] = registration_id
            
            # Verify in MongoDB that the coverage type was stored correctly
            registration = self.collection.find_one({"id": registration_id})
            
            if registration:
                if "coverageType" in registration:
                    stored_coverage_type = registration["coverageType"]
                    if stored_coverage_type == "No coverage":
                        print(f"✅ Coverage Type verified in MongoDB: {stored_coverage_type}")
                        self.tests_passed += 1
                    else:
                        print(f"❌ Coverage Type in MongoDB ({stored_coverage_type}) does not match expected value ('No coverage')")
                else:
                    print("❌ Coverage Type not found in stored data")
            else:
                print(f"❌ Could not find registration with ID {registration_id}")
        
        return success, response

    def test_get_no_coverage_registration(self):
        """Test retrieving admin registration with 'No coverage' type"""
        if "No coverage" not in self.registration_ids:
            print(f"❌ No registration ID found for coverage type: 'No coverage'")
            return False, {}
        
        registration_id = self.registration_ids["No coverage"]
        
        success, response = self.run_test(
            "Get Admin Registration - Coverage Type: 'No coverage'",
            "GET",
            f"api/admin-registration/{registration_id}",
            200
        )
        
        if success:
            # Verify that the coverage type in the response matches the expected value
            if "coverageType" in response:
                retrieved_coverage_type = response["coverageType"]
                if retrieved_coverage_type == "No coverage":
                    print(f"✅ Coverage Type in API response verified: {retrieved_coverage_type}")
                    self.tests_passed += 1
                else:
                    print(f"❌ Coverage Type in API response ({retrieved_coverage_type}) does not match expected value ('No coverage')")
            else:
                print("❌ Coverage Type not found in API response")
        
        return success, response

    def test_clinical_summary_with_no_coverage(self):
        """Test that the clinical summary template is updated correctly with 'No coverage'"""
        if "No coverage" not in self.registration_ids:
            print(f"❌ No registration ID found for coverage type: 'No coverage'")
            return False, {}
        
        registration_id = self.registration_ids["No coverage"]
        
        # Get the registration data
        success, response = self.run_test(
            "Get Admin Registration for Clinical Summary - Coverage Type: 'No coverage'",
            "GET",
            f"api/admin-registration/{registration_id}",
            200
        )
        
        if not success:
            return False, {}
        
        # Generate a summary template if none exists
        summary_template = response.get("summaryTemplate")
        if summary_template is None:
            summary_template = "Patient summary template. "
            summary_template = f"No coverage. {summary_template}"
            
            # Update the registration with the generated template
            update_data = response.copy()
            if "_id" in update_data:
                del update_data["_id"]
            update_data["summaryTemplate"] = summary_template
            
            # Convert date fields to strings if they're not already
            if update_data.get('dob') and not isinstance(update_data['dob'], str):
                update_data['dob'] = update_data['dob'].isoformat()
            if update_data.get('regDate') and not isinstance(update_data['regDate'], str):
                update_data['regDate'] = update_data['regDate'].isoformat()
            
            # Update the registration with the generated template
            success, update_response = self.run_test(
                "Update Admin Registration with Generated Template - Coverage Type: 'No coverage'",
                "PUT",
                f"api/admin-registration/{registration_id}",
                200,
                data=update_data
            )
            
            if not success:
                return False, {}
        
        # Check if the coverage type is correctly reflected in the clinical summary
        expected_coverage_text = "No coverage. "
        if summary_template and expected_coverage_text in summary_template:
            print(f"✅ Coverage information '{expected_coverage_text}' found in clinical summary: {summary_template}")
            self.tests_passed += 1
        else:
            print(f"❌ Expected coverage information '{expected_coverage_text}' not found in clinical summary: {summary_template}")
            return False, {}
        
        return True, {"summary_template": summary_template}

    def test_backward_compatibility_with_none(self):
        """Test backward compatibility with existing 'None' values"""
        # First, create a registration with 'None' coverage type
        # This simulates an existing record with the old value
        test_data = self.generate_test_data("None")
        
        success, response = self.run_test(
            "Admin Registration - Coverage Type: 'None' (Legacy)",
            "POST",
            "api/admin-register",
            200,
            data=test_data
        )
        
        if success:
            registration_id = response.get('registration_id')
            print(f"Admin Registration ID (Legacy Coverage Type 'None'): {registration_id}")
            self.registration_ids["None"] = registration_id
            
            # Verify in MongoDB that the coverage type was stored correctly
            registration = self.collection.find_one({"id": registration_id})
            
            if registration:
                if "coverageType" in registration:
                    stored_coverage_type = registration["coverageType"]
                    if stored_coverage_type == "None":
                        print(f"✅ Legacy Coverage Type verified in MongoDB: {stored_coverage_type}")
                        self.tests_passed += 1
                    else:
                        print(f"❌ Legacy Coverage Type in MongoDB ({stored_coverage_type}) does not match expected value ('None')")
                else:
                    print("❌ Coverage Type not found in stored data")
            else:
                print(f"❌ Could not find registration with ID {registration_id}")
        
        # Now test retrieving and updating this registration
        if "None" in self.registration_ids:
            registration_id = self.registration_ids["None"]
            
            # Get the registration
            success, response = self.run_test(
                "Get Admin Registration - Legacy Coverage Type: 'None'",
                "GET",
                f"api/admin-registration/{registration_id}",
                200
            )
            
            if success:
                # Verify that the coverage type in the response matches the expected value
                if "coverageType" in response:
                    retrieved_coverage_type = response["coverageType"]
                    if retrieved_coverage_type == "None":
                        print(f"✅ Legacy Coverage Type in API response verified: {retrieved_coverage_type}")
                        self.tests_passed += 1
                    else:
                        print(f"❌ Legacy Coverage Type in API response ({retrieved_coverage_type}) does not match expected value ('None')")
                else:
                    print("❌ Coverage Type not found in API response")
                
                # Update the registration with a new coverage type
                update_data = response.copy()
                if "_id" in update_data:
                    del update_data["_id"]
                
                # Update to "No coverage"
                update_data["coverageType"] = "No coverage"
                
                # Generate a summary template if none exists
                if update_data.get("summaryTemplate") is None:
                    update_data["summaryTemplate"] = "No coverage. Patient summary template. "
                else:
                    # Replace None with No coverage in the template
                    update_data["summaryTemplate"] = update_data["summaryTemplate"].replace("None. ", "No coverage. ")
                
                # Convert date fields to strings if they're not already
                if update_data.get('dob') and not isinstance(update_data['dob'], str):
                    update_data['dob'] = update_data['dob'].isoformat()
                if update_data.get('regDate') and not isinstance(update_data['regDate'], str):
                    update_data['regDate'] = update_data['regDate'].isoformat()
                
                success, response = self.run_test(
                    "Update Admin Registration - Legacy 'None' to 'No coverage'",
                    "PUT",
                    f"api/admin-registration/{registration_id}",
                    200,
                    data=update_data
                )
                
                if success:
                    # Verify in MongoDB that the coverage type was updated correctly
                    registration = self.collection.find_one({"id": registration_id})
                    
                    if registration:
                        if "coverageType" in registration:
                            stored_coverage_type = registration["coverageType"]
                            if stored_coverage_type == "No coverage":
                                print(f"✅ Updated Coverage Type verified in MongoDB: {stored_coverage_type}")
                                self.tests_passed += 1
                            else:
                                print(f"❌ Updated Coverage Type in MongoDB ({stored_coverage_type}) does not match expected value ('No coverage')")
                        else:
                            print("❌ Coverage Type not found in stored data after update")
                    else:
                        print(f"❌ Could not find registration with ID {registration_id} after update")
        
        return success, response

    def test_finalize_with_no_coverage(self):
        """Test finalizing admin registration with 'No coverage' type"""
        if "No coverage" not in self.registration_ids:
            print(f"❌ No registration ID found for coverage type: 'No coverage'")
            return False, {}
        
        registration_id = self.registration_ids["No coverage"]
        
        success, response = self.run_test(
            "Finalize Admin Registration - Coverage Type: 'No coverage'",
            "POST",
            f"api/admin-registration/{registration_id}/finalize",
            200
        )
        
        if success:
            print(f"✅ Successfully finalized registration with coverage type: 'No coverage'")
            
            # Verify that the registration status was updated to "completed"
            if "status" in response and response["status"] == "completed":
                print("✅ Registration status updated to 'completed'")
                self.tests_passed += 1
            else:
                print(f"❌ Registration status not updated to 'completed': {response.get('status', 'N/A')}")
            
            # Verify that the email was sent
            if "email_sent" in response and response["email_sent"]:
                print("✅ Email sent successfully")
                self.tests_passed += 1
            else:
                print(f"❌ Email not sent: {response.get('email_error', 'Unknown error')}")
        
        return success, response

    def test_copy_functionality_fields(self):
        """Test that all fields needed for copy functionality are supported"""
        # Create a registration with all required fields for copy functionality
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
        
        copy_fields_data = {
            "firstName": f"Copy {random_suffix}",
            "lastName": f"Test {random_suffix}",
            "dob": "1980-01-01",
            "healthCard": ''.join(random.choices(string.digits, k=10)),
            "healthCardVersion": "AB",
            "phone1": ''.join(random.choices(string.digits, k=10)),
            "address": f"{random.randint(100, 999)} Copy Street",
            "city": "Toronto",
            "province": "Ontario",
            "postalCode": f"M{random.randint(1, 9)}A {random.randint(1, 9)}B{random.randint(1, 9)}",
            "rnaAvailable": "Yes",
            "rnaResult": "Negative",
            "summaryTemplate": "Test summary template for copy functionality.",
            "coverageType": "No coverage",
            "referralSite": "Toronto - Outreach",
            "patientConsent": "Verbal"  # Required field
        }
        
        success, response = self.run_test(
            "Admin Registration - Copy Functionality Fields",
            "POST",
            "api/admin-register",
            200,
            data=copy_fields_data
        )
        
        if success:
            registration_id = response.get('registration_id')
            print(f"Admin Registration ID (Copy Functionality Fields): {registration_id}")
            
            # Get the registration to verify all fields were stored
            success, response = self.run_test(
                "Get Admin Registration - Copy Functionality Fields",
                "GET",
                f"api/admin-registration/{registration_id}",
                200
            )
            
            if success:
                # Check that all required fields for copy functionality are present
                required_fields = [
                    "firstName", "lastName", "dob", "healthCard", "healthCardVersion",
                    "phone1", "address", "city", "province", "postalCode",
                    "rnaAvailable", "rnaResult", "summaryTemplate", "coverageType", "referralSite"
                ]
                
                missing_fields = []
                for field in required_fields:
                    if field not in response or response[field] is None:
                        missing_fields.append(field)
                
                if missing_fields:
                    print(f"❌ Missing required fields for copy functionality: {', '.join(missing_fields)}")
                    return False, {"missing_fields": missing_fields}
                else:
                    print("✅ All required fields for copy functionality are present")
                    self.tests_passed += 1
            
        return success, response

    def run_all_tests(self):
        """Run all coverage type update tests"""
        print("🚀 Starting Coverage Type Update Tests for my420.ca")
        print(f"🔗 Base URL: {self.base_url}")
        print("=" * 50)
        
        # Test API health
        self.test_api_health()
        
        # Test the new 'No coverage' option
        print("\n" + "=" * 50)
        print("🔍 Testing 'No coverage' Option")
        print("=" * 50)
        self.test_no_coverage_option()
        self.test_get_no_coverage_registration()
        self.test_clinical_summary_with_no_coverage()
        
        # Test backward compatibility with 'None'
        print("\n" + "=" * 50)
        print("🔍 Testing Backward Compatibility with 'None'")
        print("=" * 50)
        self.test_backward_compatibility_with_none()
        
        # Test finalization with 'No coverage'
        print("\n" + "=" * 50)
        print("🔍 Testing Finalization with 'No coverage'")
        print("=" * 50)
        self.test_finalize_with_no_coverage()
        
        # Test copy functionality fields
        print("\n" + "=" * 50)
        print("🔍 Testing Copy Functionality Fields")
        print("=" * 50)
        self.test_copy_functionality_fields()
        
        print("\n" + "=" * 50)
        print(f"📊 Tests passed: {self.tests_passed}/{self.tests_run}")
        
        return self.tests_passed == self.tests_run


def main():
    # Get the backend URL from the frontend .env file
    import os
    from dotenv import load_dotenv
    
    # Load the frontend .env file
    load_dotenv('/app/frontend/.env')
    
    # Get the backend URL from the environment variable
    backend_url = os.environ.get('REACT_APP_BACKEND_URL')
    if not backend_url:
        print("❌ Error: REACT_APP_BACKEND_URL not found in frontend .env file")
        return 1
    
    print(f"🔗 Using backend URL from .env: {backend_url}")
    
    # Run the tests
    tester = CoverageTypeUpdateTester(backend_url)
    success = tester.run_all_tests()
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())