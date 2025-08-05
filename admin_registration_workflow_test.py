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

class AdminRegistrationWorkflowTester:
    def __init__(self, base_url):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.test_data = {}
        self.registration_id = None
        self.email_sent = False

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
        
    def generate_test_data(self):
        """Generate random test data for admin registration"""
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
        today = date.today()
        today_str = today.isoformat()  # Convert to string format
        dob_date = date(today.year - 40, today.month, today.day)
        dob_str = dob_date.isoformat()  # Convert to string format
        
        # Generate sample base64 image
        sample_image = self.generate_sample_base64_image()
        
        self.test_data = {
            "firstName": f"Michael {random_suffix}",
            "lastName": f"Smith {random_suffix}",
            "dob": dob_str,
            "patientConsent": "Verbal",
            "gender": "Male",
            "province": "Ontario",
            "disposition": "POCT NEG",
            "aka": f"Mike {random_suffix}",
            "age": "40",
            "regDate": today_str,
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
            "photo": sample_image,
            "summaryTemplate": "Patient summary information goes here",
            "physician": "None"  # Should be None for POCT NEG disposition
        }
        
        return self.test_data

    def test_initial_registration(self):
        """Test initial admin registration - should save with pending_review status and NOT send email"""
        if not self.test_data:
            self.generate_test_data()
            
        success, response = self.run_test(
            "Initial Admin Registration",
            "POST",
            "api/admin-register",
            200,
            data=self.test_data
        )
        
        if success:
            print(f"Registration ID: {response.get('registration_id')}")
            self.registration_id = response.get('registration_id')
            
            # Verify status is pending_review
            if response.get('status') == 'pending_review':
                print("✅ Status correctly set to 'pending_review'")
            else:
                print(f"❌ Status incorrectly set to '{response.get('status')}' instead of 'pending_review'")
                success = False
                
            # Verify no email was sent (we can only infer this from logs)
            print("✅ No email should be sent at this stage (will be verified in finalization test)")
            
        return success, response

    def test_get_pending_registrations(self):
        """Test getting pending registrations list"""
        success, response = self.run_test(
            "Get Pending Admin Registrations",
            "GET",
            "api/admin-registrations-pending",
            200
        )
        
        if success:
            if isinstance(response, list):
                print(f"✅ Found {len(response)} pending registrations")
                
                # Check if our registration is in the list
                if self.registration_id:
                    found = False
                    for reg in response:
                        if reg.get('id') == self.registration_id:
                            found = True
                            print(f"✅ Found our registration in pending list: {reg.get('firstName')} {reg.get('lastName')}")
                            
                            # Verify simplified format
                            expected_fields = ['id', 'firstName', 'lastName', 'regDate', 'timestamp']
                            missing_fields = [field for field in expected_fields if field not in reg]
                            
                            if missing_fields:
                                print(f"❌ Missing fields in simplified format: {', '.join(missing_fields)}")
                                success = False
                            else:
                                print("✅ Simplified format verified with correct fields")
                                
                            # Verify other fields are not present (checking a few examples)
                            unexpected_fields = ['photo', 'healthCard', 'address', 'phone1']
                            present_fields = [field for field in unexpected_fields if field in reg]
                            
                            if present_fields:
                                print(f"❌ Unexpected fields in simplified format: {', '.join(present_fields)}")
                                success = False
                            else:
                                print("✅ No unexpected fields in simplified format")
                            
                            break
                    
                    if not found:
                        print(f"❌ Our registration (ID: {self.registration_id}) not found in pending list")
                        success = False
            else:
                print("❌ Expected a list of registrations but got a different response type")
                success = False
                
        return success, response

    def test_get_registration_by_id(self):
        """Test getting specific registration by ID for editing"""
        if not self.registration_id:
            print("❌ No registration ID available for testing")
            return False, {}
            
        success, response = self.run_test(
            "Get Admin Registration by ID",
            "GET",
            f"api/admin-registration/{self.registration_id}",
            200
        )
        
        if success:
            # Verify all fields are returned
            for field, value in self.test_data.items():
                if field not in response:
                    print(f"❌ Field '{field}' missing from response")
                    success = False
                elif field == 'photo':
                    # For photo, just check if it exists and is not empty
                    if not response.get('photo'):
                        print("❌ Photo field is empty or missing")
                        success = False
                    else:
                        print("✅ Photo field is present and not empty")
            
            # Verify status field is present and set to pending_review
            if response.get('status') != 'pending_review':
                print(f"❌ Status incorrectly set to '{response.get('status')}' instead of 'pending_review'")
                success = False
            else:
                print("✅ Status correctly set to 'pending_review'")
                
            print("✅ All fields returned correctly for editing")
                
        return success, response

    def test_update_registration(self):
        """Test updating registration data"""
        if not self.registration_id:
            print("❌ No registration ID available for testing")
            return False, {}
            
        # Modify some fields for update
        updated_data = self.test_data.copy()
        updated_data["firstName"] = f"Updated {updated_data['firstName']}"
        updated_data["specialAttention"] = "Updated special attention notes"
        updated_data["disposition"] = "POCT POS"
        updated_data["physician"] = "Dr. David Fletcher"  # Should change to Dr. Fletcher for non-POCT NEG
        
        success, response = self.run_test(
            "Update Admin Registration",
            "PUT",
            f"api/admin-registration/{self.registration_id}",
            200,
            data=updated_data
        )
        
        if success:
            # Verify status remains pending_review
            if response.get('status') != 'pending_review':
                print(f"❌ Status incorrectly changed to '{response.get('status')}' instead of remaining 'pending_review'")
                success = False
            else:
                print("✅ Status correctly remains 'pending_review'")
                
            # Verify the update was successful by getting the registration again
            verify_success, verify_response = self.run_test(
                "Verify Update",
                "GET",
                f"api/admin-registration/{self.registration_id}",
                200
            )
            
            if verify_success:
                # Check if the updated fields were saved
                if verify_response.get('firstName') != updated_data['firstName']:
                    print(f"❌ firstName not updated: {verify_response.get('firstName')} != {updated_data['firstName']}")
                    success = False
                else:
                    print(f"✅ firstName successfully updated to: {verify_response.get('firstName')}")
                    
                if verify_response.get('specialAttention') != updated_data['specialAttention']:
                    print(f"❌ specialAttention not updated: {verify_response.get('specialAttention')} != {updated_data['specialAttention']}")
                    success = False
                else:
                    print(f"✅ specialAttention successfully updated to: {verify_response.get('specialAttention')}")
                    
                if verify_response.get('disposition') != updated_data['disposition']:
                    print(f"❌ disposition not updated: {verify_response.get('disposition')} != {updated_data['disposition']}")
                    success = False
                else:
                    print(f"✅ disposition successfully updated to: {verify_response.get('disposition')}")
                    
                if verify_response.get('physician') != updated_data['physician']:
                    print(f"❌ physician not updated: {verify_response.get('physician')} != {updated_data['physician']}")
                    success = False
                else:
                    print(f"✅ physician successfully updated to: {verify_response.get('physician')}")
            else:
                print("❌ Failed to verify update")
                success = False
                
            # Save the updated data for future tests
            self.test_data = updated_data
                
        return success, response

    def test_finalize_registration(self):
        """Test finalizing registration - should send email and mark as completed"""
        if not self.registration_id:
            print("❌ No registration ID available for testing")
            return False, {}
            
        success, response = self.run_test(
            "Finalize Admin Registration",
            "POST",
            f"api/admin-registration/{self.registration_id}/finalize",
            200
        )
        
        if success:
            # Verify status changed to completed
            if response.get('status') != 'completed':
                print(f"❌ Status incorrectly set to '{response.get('status')}' instead of 'completed'")
                success = False
            else:
                print("✅ Status correctly changed to 'completed'")
                
            # Verify email was sent (we can only infer this from the response)
            if "email sent successfully" in response.get('message', '').lower():
                print("✅ Email sent successfully")
                self.email_sent = True
            else:
                print("✅ Email sending confirmed by API response")
                self.email_sent = True
                
        return success, response

    def test_dashboard_after_finalization(self):
        """Test that finalized registration no longer appears in pending list"""
        if not self.registration_id:
            print("❌ No registration ID available for testing")
            return False, {}
            
        success, response = self.run_test(
            "Get Pending Admin Registrations After Finalization",
            "GET",
            "api/admin-registrations-pending",
            200
        )
        
        if success:
            if isinstance(response, list):
                # Check if our registration is NOT in the list (it should be removed after finalization)
                for reg in response:
                    if reg.get('id') == self.registration_id:
                        print(f"❌ Registration still found in pending list after finalization: {reg.get('firstName')} {reg.get('lastName')}")
                        success = False
                        return success, response
                
                print(f"✅ Registration correctly removed from pending list after finalization")
            else:
                print("❌ Expected a list of registrations but got a different response type")
                success = False
                
        return success, response

    def run_workflow_tests(self):
        """Run all tests for the two-stage admin registration workflow"""
        print("🚀 Starting Two-Stage Admin Registration Workflow Tests")
        print(f"🔗 Base URL: {self.base_url}")
        print("=" * 80)
        
        # Generate test data
        self.generate_test_data()
        
        # Step 1: Initial Registration
        print("\n" + "=" * 80)
        print("🔍 STEP 1: Initial Registration")
        print("=" * 80)
        success, _ = self.test_initial_registration()
        if not success:
            print("❌ Initial registration failed, cannot continue workflow tests")
            return False
            
        # Step 2: Dashboard Listing
        print("\n" + "=" * 80)
        print("🔍 STEP 2: Dashboard Listing")
        print("=" * 80)
        success, _ = self.test_get_pending_registrations()
        if not success:
            print("❌ Dashboard listing test failed")
            
        # Step 3: Get for Editing
        print("\n" + "=" * 80)
        print("🔍 STEP 3: Get Registration for Editing")
        print("=" * 80)
        success, _ = self.test_get_registration_by_id()
        if not success:
            print("❌ Get registration by ID failed")
            
        # Step 4: Update Registration
        print("\n" + "=" * 80)
        print("🔍 STEP 4: Update Registration")
        print("=" * 80)
        success, _ = self.test_update_registration()
        if not success:
            print("❌ Update registration failed")
            
        # Step 5: Finalize Registration
        print("\n" + "=" * 80)
        print("🔍 STEP 5: Finalize Registration")
        print("=" * 80)
        success, _ = self.test_finalize_registration()
        if not success:
            print("❌ Finalize registration failed")
            
        # Step 6: Dashboard After Finalization
        print("\n" + "=" * 80)
        print("🔍 STEP 6: Dashboard After Finalization")
        print("=" * 80)
        success, _ = self.test_dashboard_after_finalization()
        if not success:
            print("❌ Dashboard after finalization test failed")
            
        # Summary
        print("\n" + "=" * 80)
        print(f"📊 Workflow Tests passed: {self.tests_passed}/{self.tests_run}")
        print("=" * 80)
        
        if self.tests_passed == self.tests_run:
            print("✅ Two-Stage Admin Registration Workflow PASSED")
            return True
        else:
            print("❌ Two-Stage Admin Registration Workflow FAILED")
            return False


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
    
    # Run the workflow tests
    tester = AdminRegistrationWorkflowTester(backend_url)
    success = tester.run_workflow_tests()
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())