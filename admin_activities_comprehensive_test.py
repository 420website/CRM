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

class AdminActivitiesComprehensiveTest:
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
        last_week = today - timedelta(days=7)
        next_week = today + timedelta(days=7)
        
        self.test_data = {
            "admin_registrations": [
                {
                    "firstName": f"John{random_suffix}",
                    "lastName": f"Doe{random_suffix}",
                    "patientConsent": "Verbal",
                    "phone1": ''.join(random.choices(string.digits, k=10)),
                    "email": f"john.doe.{random_suffix}@example.com"
                },
                {
                    "firstName": f"Jane{random_suffix}",
                    "lastName": f"Smith{random_suffix}",
                    "patientConsent": "Written",
                    "phone1": ''.join(random.choices(string.digits, k=10)),
                    "email": f"jane.smith.{random_suffix}@example.com"
                }
            ],
            "activities": [
                # Past activities (completed)
                {
                    "registration_index": 0,  # For John Doe
                    "date": last_week.strftime('%Y-%m-%d'),
                    "time": "09:00",
                    "description": f"Past activity 1 {random_suffix}"
                },
                {
                    "registration_index": 0,  # For John Doe
                    "date": yesterday.strftime('%Y-%m-%d'),
                    "time": "14:30",
                    "description": f"Past activity 2 {random_suffix}"
                },
                # Today's activities (should be upcoming)
                {
                    "registration_index": 0,  # For John Doe
                    "date": today.strftime('%Y-%m-%d'),
                    "time": "18:00",
                    "description": f"Today's activity {random_suffix}"
                },
                # Future activities (upcoming)
                {
                    "registration_index": 1,  # For Jane Smith
                    "date": tomorrow.strftime('%Y-%m-%d'),
                    "time": "10:15",
                    "description": f"Future activity 1 {random_suffix}"
                },
                {
                    "registration_index": 1,  # For Jane Smith
                    "date": next_week.strftime('%Y-%m-%d'),
                    "time": "11:45",
                    "description": f"Future activity 2 {random_suffix}"
                }
            ]
        }
        
        return self.test_data

    def create_test_registrations(self):
        """Create test registrations for activities"""
        if not self.test_data:
            self.generate_test_data()
            
        registration_ids = []
        
        for i, registration_data in enumerate(self.test_data["admin_registrations"]):
            success, response = self.run_test(
                f"Create Test Registration {i+1}",
                "POST",
                "api/admin-register",
                200,
                data=registration_data
            )
            
            if success and 'registration_id' in response:
                registration_ids.append(response['registration_id'])
                print(f"✅ Created test registration {i+1} with ID: {response['registration_id']}")
            else:
                print(f"❌ Failed to create test registration {i+1}")
                return False
                
        self.test_data["registration_ids"] = registration_ids
        return True

    def create_test_activities(self):
        """Create test activities for the registrations"""
        if not self.test_data or 'registration_ids' not in self.test_data:
            if not self.create_test_registrations():
                return False
                
        activity_ids = []
        
        for i, activity_data in enumerate(self.test_data["activities"]):
            registration_index = activity_data.pop("registration_index")
            registration_id = self.test_data["registration_ids"][registration_index]
            
            success, response = self.run_test(
                f"Create Activity {i+1}: {activity_data['description']}",
                "POST",
                f"api/admin-registration/{registration_id}/activity",
                200,
                data=activity_data
            )
            
            if success and 'activity_id' in response:
                activity_ids.append({
                    "id": response['activity_id'],
                    "registration_id": registration_id,
                    "description": activity_data['description'],
                    "date": activity_data['date'],
                    "time": activity_data['time']
                })
                print(f"✅ Created activity {i+1} with ID: {response['activity_id']}")
            else:
                print(f"❌ Failed to create activity {i+1}: {activity_data['description']}")
                return False
                
        self.test_data["activity_ids"] = activity_ids
        return True

    def test_get_admin_activities_basic(self):
        """Test the basic functionality of GET /api/admin-activities endpoint"""
        success, response = self.run_test(
            "Get All Admin Activities - Basic Functionality",
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
                for test_activity in self.test_data["activity_ids"]:
                    for activity in activities:
                        if activity['id'] == test_activity['id']:
                            found_count += 1
                            break
                            
                if found_count == len(self.test_data["activity_ids"]):
                    print(f"✅ All {found_count} test activities found in the response")
                else:
                    print(f"❌ Only {found_count} of {len(self.test_data['activity_ids'])} test activities found in the response")
                    return False
            
            return True
        else:
            print("❌ Failed to retrieve admin activities")
            return False

    def test_data_enrichment(self):
        """Test that activities are enriched with client information"""
        success, response = self.run_test(
            "Get Admin Activities - Data Enrichment",
            "GET",
            "api/admin-activities",
            200
        )
        
        if success and 'activities' in response:
            activities = response['activities']
            
            # Check if our test activities are enriched with client information
            if hasattr(self, 'test_data') and 'activity_ids' in self.test_data:
                for test_activity in self.test_data["activity_ids"]:
                    found = False
                    for activity in activities:
                        if activity['id'] == test_activity['id']:
                            found = True
                            
                            # Get the registration data for this activity
                            registration_id = test_activity['registration_id']
                            registration_index = self.test_data["registration_ids"].index(registration_id)
                            registration_data = self.test_data["admin_registrations"][registration_index]
                            
                            # Verify client information is correctly joined
                            expected_name = f"{registration_data['firstName']} {registration_data['lastName']}"
                            if activity['client_name'] != expected_name:
                                print(f"❌ Client name mismatch: expected '{expected_name}', got '{activity['client_name']}'")
                                return False
                                
                            if activity['client_first_name'] != registration_data['firstName']:
                                print(f"❌ Client first name mismatch: expected '{registration_data['firstName']}', got '{activity['client_first_name']}'")
                                return False
                                
                            if activity['client_last_name'] != registration_data['lastName']:
                                print(f"❌ Client last name mismatch: expected '{registration_data['lastName']}', got '{activity['client_last_name']}'")
                                return False
                                
                            if activity['client_phone'] != registration_data['phone1']:
                                print(f"❌ Client phone mismatch: expected '{registration_data['phone1']}', got '{activity['client_phone']}'")
                                return False
                                
                            if activity['client_email'] != registration_data['email']:
                                print(f"❌ Client email mismatch: expected '{registration_data['email']}', got '{activity['client_email']}'")
                                return False
                                
                            print(f"✅ Activity {test_activity['id']} has correct client information")
                            break
                            
                    if not found:
                        print(f"❌ Could not find test activity {test_activity['id']} in the response")
                        return False
                
                print("✅ All test activities have correct client information")
                return True
            else:
                print("❌ No test activities to check for data enrichment")
                return False
        else:
            print("❌ Failed to retrieve admin activities for data enrichment check")
            return False

    def test_activity_status(self):
        """Test that activity status is correctly calculated"""
        success, response = self.run_test(
            "Get Admin Activities - Status Calculation",
            "GET",
            "api/admin-activities",
            200
        )
        
        if success and 'activities' in response:
            activities = response['activities']
            today = date.today().strftime('%Y-%m-%d')
            
            # Check if our test activities have the correct status
            if hasattr(self, 'test_data') and 'activity_ids' in self.test_data:
                for test_activity in self.test_data["activity_ids"]:
                    found = False
                    for activity in activities:
                        if activity['id'] == test_activity['id']:
                            found = True
                            
                            # Verify status is correctly calculated
                            expected_status = "completed" if test_activity['date'] < today else "upcoming"
                            if activity['status'] != expected_status:
                                print(f"❌ Activity status mismatch for {test_activity['description']}: expected '{expected_status}', got '{activity['status']}'")
                                print(f"   Activity date: {test_activity['date']}, Today: {today}")
                                return False
                                
                            print(f"✅ Activity {test_activity['id']} has correct status: {activity['status']}")
                            break
                            
                    if not found:
                        print(f"❌ Could not find test activity {test_activity['id']} in the response")
                        return False
                
                print("✅ All test activities have correct status")
                return True
            else:
                print("❌ No test activities to check for status calculation")
                return False
        else:
            print("❌ Failed to retrieve admin activities for status check")
            return False

    def test_sorting(self):
        """Test that activities are sorted by created_at timestamp (newest first)"""
        success, response = self.run_test(
            "Get Admin Activities - Sorting",
            "GET",
            "api/admin-activities",
            200
        )
        
        if success and 'activities' in response:
            activities = response['activities']
            
            # Verify activities are sorted by created_at (newest first)
            if len(activities) > 1:
                is_sorted = True
                for i in range(len(activities) - 1):
                    # Convert string timestamps to datetime objects for comparison
                    current_timestamp = datetime.fromisoformat(activities[i]['created_at'].replace('Z', '+00:00'))
                    next_timestamp = datetime.fromisoformat(activities[i+1]['created_at'].replace('Z', '+00:00'))
                    
                    if current_timestamp < next_timestamp:
                        is_sorted = False
                        print(f"❌ Activities not sorted correctly at index {i}:")
                        print(f"   Current: {activities[i]['created_at']}")
                        print(f"   Next: {activities[i+1]['created_at']}")
                        break
                        
                if is_sorted:
                    print("✅ Activities are correctly sorted by created_at (newest first)")
                    return True
                else:
                    print("❌ Activities are not correctly sorted by created_at (newest first)")
                    return False
            else:
                print("⚠️ Not enough activities to verify sorting")
                return True
        else:
            print("❌ Failed to retrieve admin activities for sorting check")
            return False

    def test_empty_result(self):
        """Test that the endpoint handles empty result sets gracefully"""
        # We can't easily delete all activities, so we'll just check the response format
        success, response = self.run_test(
            "Get Admin Activities - Empty Result Handling",
            "GET",
            "api/admin-activities",
            200
        )
        
        if success:
            if 'activities' in response:
                print("✅ Endpoint returns 'activities' array even if potentially empty")
                return True
            else:
                print("❌ Endpoint does not include 'activities' field in response")
                return False
        else:
            print("❌ Failed to test empty result handling")
            return False

    def run_all_tests(self):
        """Run all tests for the admin-activities endpoint"""
        print("🚀 Starting Comprehensive Admin Activities API Tests")
        print(f"🔗 Base URL: {self.base_url}")
        print("=" * 50)
        
        # Create test data first
        if self.create_test_activities():
            print("✅ Test setup completed successfully")
        else:
            print("❌ Test setup failed")
            return False
            
        # Run the tests
        print("\n" + "=" * 50)
        print("🔍 Testing Basic Functionality")
        print("=" * 50)
        self.test_get_admin_activities_basic()
        
        print("\n" + "=" * 50)
        print("🔍 Testing Data Enrichment")
        print("=" * 50)
        self.test_data_enrichment()
        
        print("\n" + "=" * 50)
        print("🔍 Testing Activity Status Calculation")
        print("=" * 50)
        self.test_activity_status()
        
        print("\n" + "=" * 50)
        print("🔍 Testing Sorting")
        print("=" * 50)
        self.test_sorting()
        
        print("\n" + "=" * 50)
        print("🔍 Testing Empty Result Handling")
        print("=" * 50)
        self.test_empty_result()
        
        print("\n" + "=" * 50)
        print(f"📊 Tests passed: {self.tests_passed}/{self.tests_run}")
        
        return self.tests_passed == self.tests_run

def main():
    tester = AdminActivitiesComprehensiveTest(BACKEND_URL)
    success = tester.run_all_tests()
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())