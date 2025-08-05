import requests
import unittest
import json
from datetime import datetime, date
import random
import string
import sys
from dotenv import load_dotenv
import os

# Load the frontend .env file to get the backend URL
load_dotenv('/app/frontend/.env')
backend_url = os.environ.get('REACT_APP_BACKEND_URL')

if not backend_url:
    print("❌ Error: REACT_APP_BACKEND_URL not found in frontend .env file")
    sys.exit(1)

print(f"🔗 Using backend URL: {backend_url}")

class AdminRegistrationDeleteTester:
    def __init__(self, base_url):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.registration_id = None

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
        
        return {
            "firstName": f"DeleteTest{random_suffix}",
            "lastName": f"User{random_suffix}",
            "patientConsent": "Verbal",
            "gender": "Male",
            "province": "Ontario",
            "disposition": f"Disposition Option {random.randint(1, 70)}",
            "healthCard": ''.join(random.choices(string.digits, k=10)),
            "referralSite": "Toronto - Outreach",
            "email": f"delete.test.{random_suffix}@example.com",
            "language": "English"
        }

    def test_create_registration(self):
        """Create a test registration to be deleted later"""
        test_data = self.generate_test_data()
        
        success, response = self.run_test(
            "Create Admin Registration for Delete Test",
            "POST",
            "api/admin-register",
            200,
            data=test_data
        )
        
        if success and 'registration_id' in response:
            self.registration_id = response['registration_id']
            print(f"✅ Created test registration with ID: {self.registration_id}")
            return True, self.registration_id
        else:
            print("❌ Failed to create test registration")
            return False, None

    def test_get_registration(self):
        """Verify the registration exists before deletion"""
        if not self.registration_id:
            print("❌ No registration ID available for testing")
            return False, None
            
        success, response = self.run_test(
            "Get Admin Registration Before Delete",
            "GET",
            f"api/admin-registration/{self.registration_id}",
            200
        )
        
        if success:
            print(f"✅ Retrieved registration: {response.get('firstName')} {response.get('lastName')}")
            return True, response
        else:
            print("❌ Failed to retrieve registration")
            return False, None

    def test_delete_registration(self):
        """Test deleting the registration"""
        if not self.registration_id:
            print("❌ No registration ID available for testing")
            return False, None
            
        success, response = self.run_test(
            "Delete Admin Registration",
            "DELETE",
            f"api/admin-registration/{self.registration_id}",
            200
        )
        
        if success:
            print(f"✅ Successfully deleted registration with ID: {self.registration_id}")
            return True, response
        else:
            print(f"❌ Failed to delete registration with ID: {self.registration_id}")
            return False, response

    def test_get_after_delete(self):
        """Verify the registration no longer exists after deletion"""
        if not self.registration_id:
            print("❌ No registration ID available for testing")
            return False, None
            
        success, response = self.run_test(
            "Get Admin Registration After Delete",
            "GET",
            f"api/admin-registration/{self.registration_id}",
            404  # Expecting a 404 Not Found
        )
        
        # In this case, we expect a 404, so success means we got a 404
        if success:
            print(f"✅ Confirmed registration no longer exists (404 Not Found)")
            return True, response
        else:
            print(f"❌ Registration still exists or unexpected error")
            return False, response

    def test_delete_nonexistent(self):
        """Test deleting a non-existent registration"""
        fake_id = "nonexistent-" + ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
        
        success, response = self.run_test(
            "Delete Non-existent Registration",
            "DELETE",
            f"api/admin-registration/{fake_id}",
            404  # Expecting a 404 Not Found
        )
        
        # In this case, we expect a 404, so success means we got a 404
        if success:
            print(f"✅ Correctly received 404 for non-existent registration")
            return True, response
        else:
            print(f"❌ Unexpected response for non-existent registration")
            return False, response

    def run_all_tests(self):
        """Run all delete functionality tests"""
        print("🚀 Starting Admin Registration Delete Tests")
        print(f"🔗 Base URL: {self.base_url}")
        print("=" * 50)
        
        # Create a registration to delete
        create_success, _ = self.test_create_registration()
        if not create_success:
            print("❌ Cannot proceed with delete tests - failed to create test registration")
            return False
            
        # Verify the registration exists
        self.test_get_registration()
        
        # Test deleting the registration
        delete_success, _ = self.test_delete_registration()
        
        # Verify the registration no longer exists
        self.test_get_after_delete()
        
        # Test deleting a non-existent registration
        self.test_delete_nonexistent()
        
        print("\n" + "=" * 50)
        print(f"📊 Tests passed: {self.tests_passed}/{self.tests_run}")
        
        return self.tests_passed == self.tests_run

def main():
    tester = AdminRegistrationDeleteTester(backend_url)
    success = tester.run_all_tests()
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())