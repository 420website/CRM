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

class CoverageTypeComprehensiveTester:
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

    def test_coverage_type_default_value(self):
        """Test that coverageType defaults to 'Select' when not provided"""
        # Generate test data without coverageType
        test_data = self.generate_test_data()
        del test_data["coverageType"]
        
        success, response = self.run_test(
            "Admin Registration - Default Coverage Type",
            "POST",
            "api/admin-register",
            200,
            data=test_data
        )
        
        if success:
            registration_id = response.get('registration_id')
            print(f"Admin Registration ID (Default Coverage Type): {registration_id}")
            
            # Verify in MongoDB that the coverage type defaulted to "Select"
            registration = self.collection.find_one({"id": registration_id})
            
            if registration:
                if "coverageType" in registration:
                    stored_coverage_type = registration["coverageType"]
                    if stored_coverage_type == "Select":
                        print(f"✅ Default Coverage Type verified in MongoDB: {stored_coverage_type}")
                        self.tests_passed += 1
                    else:
                        print(f"❌ Coverage Type in MongoDB ({stored_coverage_type}) does not match expected default value ('Select')")
                else:
                    print("❌ Coverage Type not found in stored data")
            else:
                print(f"❌ Could not find registration with ID {registration_id}")
        
        return success, response

    def test_coverage_type_specific_values(self):
        """Test admin registration with each specific coverage type value"""
        coverage_types = ["Select", "OW", "ODSP", "None"]
        results = {}
        
        for coverage_type in coverage_types:
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
                registration = self.collection.find_one({"id": registration_id})
                
                if registration:
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
            
            results[coverage_type] = {"success": success, "registration_id": response.get('registration_id')}
        
        return results

    def test_clinical_summary_integration(self):
        """Test that the clinical summary template is updated correctly based on coverage type"""
        coverage_types = ["Select", "OW", "ODSP", "None"]
        results = {}
        
        for coverage_type in coverage_types:
            if coverage_type not in self.registration_ids:
                print(f"❌ No registration ID found for coverage type: {coverage_type}")
                continue
            
            registration_id = self.registration_ids[coverage_type]
            
            # Get the registration data
            success, response = self.run_test(
                f"Get Admin Registration for Clinical Summary - Coverage Type: {coverage_type}",
                "GET",
                f"api/admin-registration/{registration_id}",
                200
            )
            
            if not success:
                continue
            
            # Generate a summary template if none exists
            summary_template = response.get("summaryTemplate")
            if summary_template is None:
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
                    continue
            
            # Check if the coverage type is correctly reflected in the clinical summary
            if coverage_type == "Select":
                # For "Select", no coverage information should appear in the clinical summary
                if summary_template and ("OW. " in summary_template or "ODSP. " in summary_template or "None. " in summary_template):
                    print(f"❌ Coverage information found in clinical summary when coverageType is 'Select': {summary_template}")
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
            
            results[coverage_type] = {"success": success, "summary_template": summary_template}
        
        return results

    def test_complete_workflow(self):
        """Test the complete admin registration workflow with coverage type"""
        # 1. Create a new registration with coverage type "ODSP"
        test_data = self.generate_test_data("ODSP")
        
        success, response = self.run_test(
            "Complete Workflow - Create Registration with Coverage Type ODSP",
            "POST",
            "api/admin-register",
            200,
            data=test_data
        )
        
        if not success:
            return False, {}
        
        registration_id = response.get('registration_id')
        print(f"Admin Registration ID (Complete Workflow): {registration_id}")
        
        # 2. Get the registration details
        success, response = self.run_test(
            "Complete Workflow - Get Registration Details",
            "GET",
            f"api/admin-registration/{registration_id}",
            200
        )
        
        if not success:
            return False, {}
        
        # Verify coverage type in response
        if response.get("coverageType") != "ODSP":
            print(f"❌ Coverage Type in API response ({response.get('coverageType')}) does not match expected value (ODSP)")
            return False, {}
        else:
            print("✅ Coverage Type in API response verified: ODSP")
            self.tests_passed += 1
        
        # 3. Update the registration with a new coverage type
        update_data = response.copy()
        if "_id" in update_data:
            del update_data["_id"]
        
        # Update to "OW"
        update_data["coverageType"] = "OW"
        
        # Generate a summary template if none exists
        if update_data.get("summaryTemplate") is None:
            update_data["summaryTemplate"] = "OW. Patient summary template. "
        else:
            # Replace ODSP with OW in the template
            update_data["summaryTemplate"] = update_data["summaryTemplate"].replace("ODSP. ", "OW. ")
        
        # Convert date fields to strings if they're not already
        if update_data.get('dob') and not isinstance(update_data['dob'], str):
            update_data['dob'] = update_data['dob'].isoformat()
        if update_data.get('regDate') and not isinstance(update_data['regDate'], str):
            update_data['regDate'] = update_data['regDate'].isoformat()
        
        success, response = self.run_test(
            "Complete Workflow - Update Registration to OW",
            "PUT",
            f"api/admin-registration/{registration_id}",
            200,
            data=update_data
        )
        
        if not success:
            return False, {}
        
        # 4. Get the updated registration details
        success, response = self.run_test(
            "Complete Workflow - Get Updated Registration Details",
            "GET",
            f"api/admin-registration/{registration_id}",
            200
        )
        
        if not success:
            return False, {}
        
        # Verify updated coverage type in response
        if response.get("coverageType") != "OW":
            print(f"❌ Updated Coverage Type in API response ({response.get('coverageType')}) does not match expected value (OW)")
            return False, {}
        else:
            print("✅ Updated Coverage Type in API response verified: OW")
            self.tests_passed += 1
        
        # 5. Finalize the registration
        success, response = self.run_test(
            "Complete Workflow - Finalize Registration",
            "POST",
            f"api/admin-registration/{registration_id}/finalize",
            200
        )
        
        if not success:
            return False, {}
        
        # Verify that the registration was finalized
        if response.get("status") != "completed":
            print(f"❌ Registration status ({response.get('status')}) does not match expected value (completed)")
            return False, {}
        else:
            print("✅ Registration status verified: completed")
            self.tests_passed += 1
        
        # 6. Verify that the finalized registration is no longer in the pending list
        success, response = self.run_test(
            "Complete Workflow - Check Pending Registrations",
            "GET",
            "api/admin-registrations-pending",
            200
        )
        
        if not success:
            return False, {}
        
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
        
        return True, {"registration_id": registration_id, "status": "completed"}

    def run_all_tests(self):
        """Run all comprehensive coverage type tests"""
        print("🚀 Starting Comprehensive Coverage Type Tests for my420.ca")
        print(f"🔗 Base URL: {self.base_url}")
        print("=" * 50)
        
        # Test API health
        self.test_api_health()
        
        # Test coverage type default value
        print("\n" + "=" * 50)
        print("🔍 Testing Coverage Type Default Value")
        print("=" * 50)
        self.test_coverage_type_default_value()
        
        # Test coverage type specific values
        print("\n" + "=" * 50)
        print("🔍 Testing Coverage Type Specific Values")
        print("=" * 50)
        self.test_coverage_type_specific_values()
        
        # Test clinical summary integration
        print("\n" + "=" * 50)
        print("🔍 Testing Clinical Summary Integration")
        print("=" * 50)
        self.test_clinical_summary_integration()
        
        # Test complete workflow
        print("\n" + "=" * 50)
        print("🔍 Testing Complete Admin Registration Workflow")
        print("=" * 50)
        self.test_complete_workflow()
        
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
    tester = CoverageTypeComprehensiveTester(backend_url)
    success = tester.run_all_tests()
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())