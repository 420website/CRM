import requests
import unittest
import json
from datetime import datetime, date, timedelta
import random
import string
import sys
import os
from dotenv import load_dotenv

# Load the frontend .env file to get the backend URL
load_dotenv('/app/frontend/.env')
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL')

if not BACKEND_URL:
    print("❌ Error: REACT_APP_BACKEND_URL not found in frontend .env file")
    sys.exit(1)

print(f"🔗 Using backend URL: {BACKEND_URL}")

class AdminActivitiesTest:
    def __init__(self, base_url):
        self.base_url = base_url
        self.test_data = {}
        self.tests_run = 0
        self.tests_passed = 0

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
        """Generate random test data for registration and activities"""
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
        today = date.today()
        tomorrow = today + timedelta(days=1)
        yesterday = today - timedelta(days=1)
        
        self.test_data = {
            "admin_registration": {
                "firstName": f"Test{random_suffix}",
                "lastName": f"User{random_suffix}",
                "patientConsent": "Verbal",
                "phone1": ''.join(random.choices(string.digits, k=10)),
                "email": f"test.user.{random_suffix}@example.com"
            },
            "activities": [
                {
                    "date": yesterday.strftime('%Y-%m-%d'),  # Past activity (completed)
                    "time": "10:00",
                    "description": f"Past activity {random_suffix}"
                },
                {
                    "date": today.strftime('%Y-%m-%d'),  # Today's activity (upcoming)
                    "time": "14:30",
                    "description": f"Today's activity {random_suffix}"
                },
                {
                    "date": tomorrow.strftime('%Y-%m-%d'),  # Future activity (upcoming)
                    "time": "09:15",
                    "description": f"Future activity {random_suffix}"
                }
            ]
        }
        
        return self.test_data

    def create_test_registration(self):
        """Create a test registration for activities"""
        if not self.test_data:
            self.generate_test_data()
            
        success, response = self.run_test(
            "Create Test Registration",
            "POST",
            "api/admin-register",
            200,
            data=self.test_data["admin_registration"]
        )
        
        if success and 'registration_id' in response:
            self.test_data["registration_id"] = response['registration_id']
            print(f"✅ Created test registration with ID: {self.test_data['registration_id']}")
            return True
        else:
            print("❌ Failed to create test registration")
            return False

    def create_test_activities(self):
        """Create test activities for the registration"""
        if not self.test_data or 'registration_id' not in self.test_data:
            if not self.create_test_registration():
                return False
                
        registration_id = self.test_data["registration_id"]
        activity_ids = []
        
        for activity_data in self.test_data["activities"]:
            success, response = self.run_test(
                f"Create Activity: {activity_data['description']}",
                "POST",
                f"api/admin-registration/{registration_id}/activity",
                200,
                data=activity_data
            )
            
            if success and 'activity_id' in response:
                activity_ids.append(response['activity_id'])
                print(f"✅ Created activity with ID: {response['activity_id']}")
            else:
                print(f"❌ Failed to create activity: {activity_data['description']}")
                return False
                
        self.test_data["activity_ids"] = activity_ids
        return True

    def test_get_admin_activities(self):
        """Test the GET /api/admin-activities endpoint"""
        success, response = self.run_test(
            "Get All Admin Activities",
            "GET",
            "api/admin-activities",
            200
        )
        
        if success and 'activities' in response:
            activities = response['activities']
            print(f"✅ Retrieved {len(activities)} activities")
            
            # Check if our test activities are in the response
            if hasattr(self, 'test_data') and 'activity_ids' in self.test_data:
                found_count = 0
                for activity_id in self.test_data["activity_ids"]:
                    for activity in activities:
                        if activity['id'] == activity_id:
                            found_count += 1
                            
                            # Verify the activity has all required fields
                            required_fields = [
                                'id', 'registration_id', 'date', 'time', 'description', 
                                'created_at', 'client_name', 'client_first_name', 
                                'client_last_name', 'client_phone', 'client_email', 'status'
                            ]
                            
                            missing_fields = [field for field in required_fields if field not in activity]
                            
                            if missing_fields:
                                print(f"❌ Activity {activity_id} is missing required fields: {', '.join(missing_fields)}")
                                return False
                            
                            # Verify client information is correctly joined
                            if activity['registration_id'] == self.test_data["registration_id"]:
                                expected_name = f"{self.test_data['admin_registration']['firstName']} {self.test_data['admin_registration']['lastName']}"
                                if activity['client_name'] != expected_name:
                                    print(f"❌ Client name mismatch: expected '{expected_name}', got '{activity['client_name']}'")
                                    return False
                                    
                                if activity['client_phone'] != self.test_data['admin_registration']['phone1']:
                                    print(f"❌ Client phone mismatch: expected '{self.test_data['admin_registration']['phone1']}', got '{activity['client_phone']}'")
                                    return False
                                    
                                if activity['client_email'] != self.test_data['admin_registration']['email']:
                                    print(f"❌ Client email mismatch: expected '{self.test_data['admin_registration']['email']}', got '{activity['client_email']}'")
                                    return False
                                    
                                # Verify status is correctly calculated
                                today = date.today().strftime('%Y-%m-%d')
                                expected_status = "completed" if activity['date'] < today else "upcoming"
                                if activity['status'] != expected_status:
                                    print(f"❌ Activity status mismatch: expected '{expected_status}', got '{activity['status']}'")
                                    return False
                                    
                                print(f"✅ Activity {activity_id} has correct client information and status")
                            
                if found_count == len(self.test_data["activity_ids"]):
                    print(f"✅ All {found_count} test activities found in the response")
                else:
                    print(f"❌ Only {found_count} of {len(self.test_data['activity_ids'])} test activities found in the response")
                    return False
            
            # Verify activities are sorted by created_at (newest first)
            if len(activities) > 1:
                is_sorted = True
                for i in range(len(activities) - 1):
                    if activities[i]['created_at'] < activities[i+1]['created_at']:
                        is_sorted = False
                        break
                        
                if is_sorted:
                    print("✅ Activities are correctly sorted by created_at (newest first)")
                else:
                    print("❌ Activities are not correctly sorted by created_at (newest first)")
                    return False
            
            return True
        else:
            print("❌ Failed to retrieve admin activities")
            return False

    def test_empty_activities(self):
        """Test the GET /api/admin-activities endpoint with no activities"""
        # This test is more of a verification that the endpoint handles empty result sets gracefully
        # We can't easily delete all activities, so we'll just check the response format
        success, response = self.run_test(
            "Get Admin Activities (Empty Check)",
            "GET",
            "api/admin-activities",
            200
        )
        
        if success and 'activities' in response:
            print("✅ Endpoint returns 'activities' array even if empty")
            return True
        else:
            print("❌ Endpoint does not handle empty result sets correctly")
            return False

    def run_all_tests(self):
        """Run all tests for the admin-activities endpoint"""
        print("🚀 Starting Admin Activities API Tests")
        print(f"🔗 Base URL: {self.base_url}")
        print("=" * 50)
        
        # Create test data first
        if self.create_test_activities():
            print("✅ Test setup completed successfully")
        else:
            print("❌ Test setup failed")
            return False
            
        # Run the tests
        self.test_get_admin_activities()
        self.test_empty_activities()
        
        print("\n" + "=" * 50)
        print(f"📊 Tests passed: {self.tests_passed}/{self.tests_run}")
        
        return self.tests_passed == self.tests_run

def main():
    tester = AdminActivitiesTest(BACKEND_URL)
    success = tester.run_all_tests()
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())