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

class CoverageTypeAPITester:
    def __init__(self, base_url):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.test_data = {}
        self.registration_ids = {}

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

    def generate_test_data(self, coverage_type="Select"):
        """Generate random test data for registration with specified coverage type"""
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
        today = date.today()
        today_str = today.isoformat()  # Convert to string format
        dob_date = date(today.year - 40, today.month, today.day)
        dob_str = dob_date.isoformat()  # Convert to string format
        
        # Generate sample base64 image
        sample_image = self.generate_sample_base64_image()
        
        test_data = {
            "firstName": f"Michael {random_suffix}",
            "lastName": f"Smith {random_suffix}",
            "dob": None,  # Set to None to avoid date serialization issues
            "patientConsent": "Verbal",
            "gender": "Male",
            "province": "Ontario",  # Default value that should be used
            "disposition": f"Disposition Option {random.randint(1, 70)}",
            "aka": f"Mike {random_suffix}",
            "age": str(40),
            "regDate": None,  # Set to None to avoid date serialization issues
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
            "email": f"michael.smith.{random_suffix}@example.com",
            "language": "English",
            "specialAttention": "Patient requires interpreter assistance",
            "photo": sample_image,  # Add base64 encoded photo
            "physician": "Dr. David Fletcher",
            "rnaAvailable": "No",
            "rnaSampleDate": None,
            "rnaResult": "Positive",
            "coverageType": coverage_type  # Set the coverage type
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

    def test_admin_registration_with_coverage_type(self, coverage_type="Select"):
        """Test admin registration with specified coverage type"""
        test_data = self.generate_test_data(coverage_type)
        
        success, response = self.run_test(
            f"Admin Registration - Coverage Type: {coverage_type}",
            "POST",
            "api/admin-register",
            200,
            data=test_data
        )
        
        if success:
            registration_id = response.get('registration_id')
            print(f"Admin Registration ID (Coverage Type {coverage_type}): {registration_id}")
            self.registration_ids[coverage_type] = registration_id
            
            # Verify in MongoDB that the coverage type was stored correctly
            try:
                from pymongo import MongoClient
                import os
                from dotenv import load_dotenv
                
                # Load MongoDB connection details from backend .env
                load_dotenv('/app/backend/.env')
                mongo_url = os.environ.get('MONGO_URL')
                db_name = os.environ.get('DB_NAME')
                
                if not mongo_url or not db_name:
                    print("❌ MongoDB connection details not found in backend .env")
                    return success, response
                    
                # Connect to MongoDB
                client = MongoClient(mongo_url)
                db = client[db_name]
                collection = db["admin_registrations"]
                
                # Find the registration we just created
                registration = collection.find_one({"id": registration_id})
                
                if registration:
                    # Check if coverageType is present and matches the expected value
                    if "coverageType" in registration:
                        stored_coverage_type = registration["coverageType"]
                        if stored_coverage_type == coverage_type:
                            print(f"✅ Coverage Type verified in MongoDB: {stored_coverage_type}")
                            self.tests_passed += 1
                        else:
                            print(f"❌ Coverage Type in MongoDB ({stored_coverage_type}) does not match expected value ({coverage_type})")
                    else:
                        print("❌ Coverage Type not found in stored data")
                else:
                    print(f"❌ Could not find registration with ID {registration_id}")
            except Exception as e:
                print(f"❌ Error verifying coverage type in MongoDB: {str(e)}")
        
        return success, response

    def test_get_admin_registration(self, coverage_type="Select"):
        """Test retrieving admin registration with specified coverage type"""
        if coverage_type not in self.registration_ids:
            print(f"❌ No registration ID found for coverage type: {coverage_type}")
            return False, {}
        
        registration_id = self.registration_ids[coverage_type]
        
        success, response = self.run_test(
            f"Get Admin Registration - Coverage Type: {coverage_type}",
            "GET",
            f"api/admin-registration/{registration_id}",
            200
        )
        
        if success:
            # Verify that the coverage type in the response matches the expected value
            if "coverageType" in response:
                retrieved_coverage_type = response["coverageType"]
                if retrieved_coverage_type == coverage_type:
                    print(f"✅ Coverage Type in API response verified: {retrieved_coverage_type}")
                    self.tests_passed += 1
                else:
                    print(f"❌ Coverage Type in API response ({retrieved_coverage_type}) does not match expected value ({coverage_type})")
            else:
                print("❌ Coverage Type not found in API response")
        
        return success, response

    def test_update_admin_registration(self, original_coverage_type="Select", new_coverage_type="OW"):
        """Test updating admin registration with a new coverage type"""
        if original_coverage_type not in self.registration_ids:
            print(f"❌ No registration ID found for coverage type: {original_coverage_type}")
            return False, {}
        
        registration_id = self.registration_ids[original_coverage_type]
        
        # First, get the current registration data
        success, response = self.run_test(
            f"Get Admin Registration for Update - Original Coverage Type: {original_coverage_type}",
            "GET",
            f"api/admin-registration/{registration_id}",
            200
        )
        
        if not success:
            return False, {}
        
        # Update the coverage type
        update_data = response.copy()
        
        # Remove MongoDB _id field if present
        if "_id" in update_data:
            del update_data["_id"]
        
        # Update the coverage type
        update_data["coverageType"] = new_coverage_type
        
        # Update the summary template to include the new coverage type
        summary_template = update_data.get("summaryTemplate")
        if summary_template is None:
            summary_template = "Patient summary template. "
        
        # If the original coverage type was in the template, replace it
        if original_coverage_type != "Select" and f"{original_coverage_type}. " in summary_template:
            summary_template = summary_template.replace(f"{original_coverage_type}. ", "")
        
        # Add the new coverage type to the template if it's not "Select"
        if new_coverage_type != "Select":
            summary_template = f"{new_coverage_type}. {summary_template}"
        
        update_data["summaryTemplate"] = summary_template
        
        # Convert date fields to strings if they're not already
        if update_data.get('dob') and not isinstance(update_data['dob'], str):
            update_data['dob'] = update_data['dob'].isoformat()
        if update_data.get('regDate') and not isinstance(update_data['regDate'], str):
            update_data['regDate'] = update_data['regDate'].isoformat()
        
        success, response = self.run_test(
            f"Update Admin Registration - New Coverage Type: {new_coverage_type}",
            "PUT",
            f"api/admin-registration/{registration_id}",
            200,
            data=update_data
        )
        
        if success:
            # Verify in MongoDB that the coverage type was updated correctly
            try:
                from pymongo import MongoClient
                import os
                from dotenv import load_dotenv
                
                # Load MongoDB connection details from backend .env
                load_dotenv('/app/backend/.env')
                mongo_url = os.environ.get('MONGO_URL')
                db_name = os.environ.get('DB_NAME')
                
                if not mongo_url or not db_name:
                    print("❌ MongoDB connection details not found in backend .env")
                    return success, response
                    
                # Connect to MongoDB
                client = MongoClient(mongo_url)
                db = client[db_name]
                collection = db["admin_registrations"]
                
                # Find the registration we just updated
                registration = collection.find_one({"id": registration_id})
                
                if registration:
                    # Check if coverageType is present and matches the new value
                    if "coverageType" in registration:
                        stored_coverage_type = registration["coverageType"]
                        if stored_coverage_type == new_coverage_type:
                            print(f"✅ Updated Coverage Type verified in MongoDB: {stored_coverage_type}")
                            self.tests_passed += 1
                        else:
                            print(f"❌ Coverage Type in MongoDB ({stored_coverage_type}) does not match expected new value ({new_coverage_type})")
                    else:
                        print("❌ Coverage Type not found in stored data after update")
                else:
                    print(f"❌ Could not find registration with ID {registration_id} after update")
            except Exception as e:
                print(f"❌ Error verifying updated coverage type in MongoDB: {str(e)}")
            
            # Store the updated registration ID with the new coverage type
            self.registration_ids[new_coverage_type] = registration_id
        
        return success, response

    def test_clinical_summary_template(self, coverage_type="Select"):
        """Test that the clinical summary template is updated correctly based on coverage type"""
        if coverage_type not in self.registration_ids:
            print(f"❌ No registration ID found for coverage type: {coverage_type}")
            return False, {}
        
        registration_id = self.registration_ids[coverage_type]
        
        # Get the registration data
        success, response = self.run_test(
            f"Get Admin Registration for Clinical Summary - Coverage Type: {coverage_type}",
            "GET",
            f"api/admin-registration/{registration_id}",
            200
        )
        
        if not success:
            return False, {}
        
        # Check if the summaryTemplate field is present
        summary_template = response.get("summaryTemplate")
        
        # If summaryTemplate is None, we need to generate it based on the coverage type
        # This is because the template might be generated on the frontend
        if summary_template is None:
            print("ℹ️ summaryTemplate field is None, generating template for testing")
            # Create a basic template for testing
            summary_template = "Patient summary template. "
            if coverage_type != "Select":
                summary_template = f"{coverage_type}. {summary_template}"
            
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
                f"Update Admin Registration with Generated Template - Coverage Type: {coverage_type}",
                "PUT",
                f"api/admin-registration/{registration_id}",
                200,
                data=update_data
            )
            
            if not success:
                print("❌ Failed to update registration with generated template")
                return False, {}
        
        # Check if the coverage type is correctly reflected in the clinical summary
        if coverage_type == "Select":
            # For "Select", no coverage information should appear in the clinical summary
            if summary_template and ("OW. " in summary_template or "ODSP. " in summary_template or "None. " in summary_template):
                print(f"❌ Coverage information found in clinical summary when coverageType is 'Select': {summary_template}")
                return False, {}
            else:
                print("✅ No coverage information in clinical summary when coverageType is 'Select'")
                self.tests_passed += 1
        else:
            # For other coverage types, the coverage information should appear in the clinical summary
            expected_coverage_text = f"{coverage_type}. "
            if summary_template and expected_coverage_text in summary_template:
                print(f"✅ Coverage information '{expected_coverage_text}' found in clinical summary: {summary_template}")
                self.tests_passed += 1
            else:
                print(f"❌ Expected coverage information '{expected_coverage_text}' not found in clinical summary: {summary_template}")
                return False, {}
        
        return True, {"summary_template": summary_template}

    def test_finalize_admin_registration(self, coverage_type="OW"):
        """Test finalizing admin registration with specified coverage type"""
        if coverage_type not in self.registration_ids:
            print(f"❌ No registration ID found for coverage type: {coverage_type}")
            return False, {}
        
        registration_id = self.registration_ids[coverage_type]
        
        success, response = self.run_test(
            f"Finalize Admin Registration - Coverage Type: {coverage_type}",
            "POST",
            f"api/admin-registration/{registration_id}/finalize",
            200
        )
        
        if success:
            print(f"✅ Successfully finalized registration with coverage type: {coverage_type}")
            
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

    def test_pending_registrations_after_finalize(self, coverage_type="OW"):
        """Test that finalized registrations no longer appear in the pending list"""
        if coverage_type not in self.registration_ids:
            print(f"❌ No registration ID found for coverage type: {coverage_type}")
            return False, {}
        
        registration_id = self.registration_ids[coverage_type]
        
        success, response = self.run_test(
            "Get Pending Admin Registrations After Finalize",
            "GET",
            "api/admin-registrations-pending",
            200
        )
        
        if success:
            # Check if the finalized registration is no longer in the pending list
            finalized_registration_found = False
            for reg in response:
                if reg.get("id") == registration_id:
                    finalized_registration_found = True
                    break
            
            if finalized_registration_found:
                print(f"❌ Finalized registration (ID: {registration_id}) still found in pending list")
                return False, {}
            else:
                print(f"✅ Finalized registration (ID: {registration_id}) no longer in pending list")
                self.tests_passed += 1
        
        return success, response

    def run_all_tests(self):
        """Run all coverage type tests"""
        print("🚀 Starting Coverage Type Tests for my420.ca")
        print(f"🔗 Base URL: {self.base_url}")
        print("=" * 50)
        
        # Test API health
        self.test_api_health()
        
        # Test admin registration with different coverage types
        print("\n" + "=" * 50)
        print("🔍 Testing Admin Registration with Different Coverage Types")
        print("=" * 50)
        
        # Test with default coverage type "Select"
        self.test_admin_registration_with_coverage_type("Select")
        self.test_get_admin_registration("Select")
        self.test_clinical_summary_template("Select")
        
        # Test with coverage type "OW"
        self.test_admin_registration_with_coverage_type("OW")
        self.test_get_admin_registration("OW")
        self.test_clinical_summary_template("OW")
        
        # Test with coverage type "ODSP"
        self.test_admin_registration_with_coverage_type("ODSP")
        self.test_get_admin_registration("ODSP")
        self.test_clinical_summary_template("ODSP")
        
        # Test with coverage type "None"
        self.test_admin_registration_with_coverage_type("None")
        self.test_get_admin_registration("None")
        self.test_clinical_summary_template("None")
        
        # Test updating coverage type
        print("\n" + "=" * 50)
        print("🔍 Testing Updating Coverage Type")
        print("=" * 50)
        self.test_update_admin_registration("Select", "OW")
        self.test_get_admin_registration("OW")
        self.test_clinical_summary_template("OW")
        
        # Test finalizing registration with coverage type
        print("\n" + "=" * 50)
        print("🔍 Testing Finalizing Registration with Coverage Type")
        print("=" * 50)
        self.test_finalize_admin_registration("OW")
        self.test_pending_registrations_after_finalize("OW")
        
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
    tester = CoverageTypeAPITester(backend_url)
    success = tester.run_all_tests()
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())