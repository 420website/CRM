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
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL')

if not BACKEND_URL:
    print("❌ Error: REACT_APP_BACKEND_URL not found in frontend .env file")
    sys.exit(1)

print(f"🔗 Using backend URL: {BACKEND_URL}")

class ActivityAPITester:
    def __init__(self, base_url):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.test_data = {}
        self.registration_id = None
        self.activity_ids = []

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
        """Generate random test data for registration"""
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
        today = date.today()
        today_str = today.isoformat()  # Convert to string format
        
        self.test_data = {
            "admin_registration": {
                "firstName": f"Test{random_suffix}",
                "lastName": f"User{random_suffix}",
                "patientConsent": "Verbal",
                "gender": "Male",
                "province": "Ontario",
                "disposition": f"Disposition Option {random.randint(1, 70)}",
                "healthCard": ''.join(random.choices(string.digits, k=10)),
                "email": f"test.user.{random_suffix}@example.com"
            },
            "activity_full": {
                "date": today_str,
                "time": "14:30",
                "description": f"Test activity with all fields - {random_suffix}"
            },
            "activity_required_only": {
                "date": today_str,
                "description": f"Test activity with required fields only - {random_suffix}"
            },
            "activity_update": {
                "date": today_str,
                "time": "16:45",
                "description": f"Updated test activity - {random_suffix}"
            }
        }
        
        return self.test_data

    def create_test_registration(self):
        """Create a test registration to use for activity tests"""
        if not self.test_data:
            self.generate_test_data()
            
        success, response = self.run_test(
            "Create Test Registration",
            "POST",
            "api/admin-register",
            200,
            data=self.test_data["admin_registration"]
        )
        
        if success and "registration_id" in response:
            self.registration_id = response["registration_id"]
            print(f"✅ Created test registration with ID: {self.registration_id}")
            return True
        else:
            print("❌ Failed to create test registration")
            return False

    def test_create_activity_with_all_fields(self):
        """Test creating an activity with all fields (date, time, description)"""
        if not self.registration_id:
            if not self.create_test_registration():
                return False, {}
        
        success, response = self.run_test(
            "Create Activity with All Fields",
            "POST",
            f"api/admin-registration/{self.registration_id}/activity",
            200,
            data=self.test_data["activity_full"]
        )
        
        if success and "activity_id" in response:
            activity_id = response["activity_id"]
            self.activity_ids.append(activity_id)
            print(f"✅ Created activity with ID: {activity_id}")
            return True, response
        else:
            print("❌ Failed to create activity with all fields")
            return False, response

    def test_create_activity_with_required_fields(self):
        """Test creating an activity with only required fields (date, description)"""
        if not self.registration_id:
            if not self.create_test_registration():
                return False, {}
        
        success, response = self.run_test(
            "Create Activity with Required Fields Only",
            "POST",
            f"api/admin-registration/{self.registration_id}/activity",
            200,
            data=self.test_data["activity_required_only"]
        )
        
        if success and "activity_id" in response:
            activity_id = response["activity_id"]
            self.activity_ids.append(activity_id)
            print(f"✅ Created activity with ID: {activity_id}")
            return True, response
        else:
            print("❌ Failed to create activity with required fields only")
            return False, response

    def test_get_activities(self):
        """Test retrieving all activities for a registration"""
        if not self.registration_id:
            if not self.create_test_registration():
                return False, {}
        
        # Create some activities if we don't have any
        if not self.activity_ids:
            self.test_create_activity_with_all_fields()
            self.test_create_activity_with_required_fields()
        
        success, response = self.run_test(
            "Get All Activities",
            "GET",
            f"api/admin-registration/{self.registration_id}/activities",
            200
        )
        
        if success and "activities" in response:
            activities = response["activities"]
            print(f"✅ Retrieved {len(activities)} activities")
            
            # Verify the activities we created are in the list
            found_count = 0
            for activity in activities:
                if activity["id"] in self.activity_ids:
                    found_count += 1
                    print(f"✅ Found activity with ID: {activity['id']}")
                    
                    # Verify the data was saved correctly
                    if activity["id"] == self.activity_ids[0]:  # First activity (with all fields)
                        if activity["date"] == self.test_data["activity_full"]["date"] and \
                           activity["time"] == self.test_data["activity_full"]["time"] and \
                           activity["description"] == self.test_data["activity_full"]["description"]:
                            print("✅ Activity with all fields data matches")
                        else:
                            print("❌ Activity with all fields data mismatch")
                            print(f"Expected: {self.test_data['activity_full']}")
                            print(f"Got: {activity}")
                    
                    elif len(self.activity_ids) > 1 and activity["id"] == self.activity_ids[1]:  # Second activity (required fields only)
                        if activity["date"] == self.test_data["activity_required_only"]["date"] and \
                           activity["description"] == self.test_data["activity_required_only"]["description"]:
                            print("✅ Activity with required fields data matches")
                        else:
                            print("❌ Activity with required fields data mismatch")
                            print(f"Expected: {self.test_data['activity_required_only']}")
                            print(f"Got: {activity}")
            
            if found_count == len(self.activity_ids):
                print(f"✅ All {found_count} created activities were found")
            else:
                print(f"❌ Only {found_count} of {len(self.activity_ids)} created activities were found")
            
            # Verify activities are sorted by created_at timestamp (newest first)
            if len(activities) > 1:
                is_sorted = all(activities[i]["created_at"] >= activities[i+1]["created_at"] for i in range(len(activities)-1))
                if is_sorted:
                    print("✅ Activities are correctly sorted by created_at timestamp (newest first)")
                else:
                    print("❌ Activities are not correctly sorted by created_at timestamp")
            
            return True, response
        else:
            print("❌ Failed to retrieve activities")
            return False, response

    def test_update_activity(self):
        """Test updating an existing activity"""
        if not self.registration_id:
            if not self.create_test_registration():
                return False, {}
        
        # Create an activity if we don't have any
        if not self.activity_ids:
            success, response = self.test_create_activity_with_all_fields()
            if not success:
                return False, {}
        
        activity_id = self.activity_ids[0]  # Use the first activity
        
        success, response = self.run_test(
            "Update Activity",
            "PUT",
            f"api/admin-registration/{self.registration_id}/activity/{activity_id}",
            200,
            data=self.test_data["activity_update"]
        )
        
        if success:
            print(f"✅ Updated activity with ID: {activity_id}")
            
            # Verify the update by getting the activities again
            success, response = self.run_test(
                "Verify Activity Update",
                "GET",
                f"api/admin-registration/{self.registration_id}/activities",
                200
            )
            
            if success and "activities" in response:
                activities = response["activities"]
                found = False
                for activity in activities:
                    if activity["id"] == activity_id:
                        found = True
                        # Verify the data was updated correctly
                        if activity["date"] == self.test_data["activity_update"]["date"] and \
                           activity["time"] == self.test_data["activity_update"]["time"] and \
                           activity["description"] == self.test_data["activity_update"]["description"]:
                            print("✅ Activity update verified - data matches")
                        else:
                            print("❌ Activity update verification failed - data mismatch")
                            print(f"Expected: {self.test_data['activity_update']}")
                            print(f"Got: {activity}")
                        break
                
                if not found:
                    print(f"❌ Could not find updated activity with ID {activity_id} in the response")
                    return False, {}
            else:
                print("❌ Failed to verify activity update")
                return False, {}
            
            return True, response
        else:
            print(f"❌ Failed to update activity with ID: {activity_id}")
            return False, response

    def test_delete_activity(self):
        """Test deleting an activity"""
        if not self.registration_id:
            if not self.create_test_registration():
                return False, {}
        
        # Create an activity if we don't have any
        if not self.activity_ids:
            success, response = self.test_create_activity_with_all_fields()
            if not success:
                return False, {}
        
        activity_id = self.activity_ids[0]  # Use the first activity
        
        success, response = self.run_test(
            "Delete Activity",
            "DELETE",
            f"api/admin-registration/{self.registration_id}/activity/{activity_id}",
            200
        )
        
        if success:
            print(f"✅ Deleted activity with ID: {activity_id}")
            
            # Verify the deletion by getting the activities again
            success, response = self.run_test(
                "Verify Activity Deletion",
                "GET",
                f"api/admin-registration/{self.registration_id}/activities",
                200
            )
            
            if success and "activities" in response:
                activities = response["activities"]
                for activity in activities:
                    if activity["id"] == activity_id:
                        print(f"❌ Activity with ID {activity_id} was not deleted")
                        return False, {}
                print("✅ Activity deletion verified - activity no longer exists")
            else:
                print("❌ Failed to verify activity deletion")
                return False, {}
            
            # Remove the deleted activity ID from our list
            self.activity_ids.remove(activity_id)
            
            return True, response
        else:
            print(f"❌ Failed to delete activity with ID: {activity_id}")
            return False, response

    def test_error_handling_invalid_registration_id(self):
        """Test error handling for invalid registration_id"""
        invalid_registration_id = "nonexistent-id"
        
        success, response = self.run_test(
            "Create Activity with Invalid Registration ID",
            "POST",
            f"api/admin-registration/{invalid_registration_id}/activity",
            404,
            data=self.test_data["activity_full"]
        )
        
        if success:
            print("✅ Proper error handling for invalid registration_id")
            return True, response
        else:
            print("❌ Failed to properly handle invalid registration_id")
            return False, response

    def test_error_handling_invalid_activity_id(self):
        """Test error handling for invalid activity_id"""
        if not self.registration_id:
            if not self.create_test_registration():
                return False, {}
        
        invalid_activity_id = "nonexistent-id"
        
        success, response = self.run_test(
            "Update Activity with Invalid Activity ID",
            "PUT",
            f"api/admin-registration/{self.registration_id}/activity/{invalid_activity_id}",
            404,
            data=self.test_data["activity_update"]
        )
        
        if success:
            print("✅ Proper error handling for invalid activity_id")
            return True, response
        else:
            print("❌ Failed to properly handle invalid activity_id")
            return False, response

    def test_validation_required_fields(self):
        """Test validation for required fields"""
        if not self.registration_id:
            if not self.create_test_registration():
                return False, {}
        
        # Test missing date (required field)
        invalid_data = {
            "description": "Test activity with missing date"
        }
        
        success, response = self.run_test(
            "Create Activity - Missing Date",
            "POST",
            f"api/admin-registration/{self.registration_id}/activity",
            422,  # Validation error status code
            data=invalid_data
        )
        
        # Test missing description (required field)
        invalid_data = {
            "date": date.today().isoformat()
        }
        
        success, response = self.run_test(
            "Create Activity - Missing Description",
            "POST",
            f"api/admin-registration/{self.registration_id}/activity",
            422,  # Validation error status code
            data=invalid_data
        )
        
        return True, {"message": "Validation tests completed"}

    def run_all_tests(self):
        """Run all Activity API tests"""
        print("🚀 Starting Activity API Tests for my420.ca")
        print(f"🔗 Base URL: {self.base_url}")
        print("=" * 50)
        
        self.generate_test_data()
        
        # Create a test registration
        self.create_test_registration()
        
        # Test creating activities
        self.test_create_activity_with_all_fields()
        self.test_create_activity_with_required_fields()
        
        # Test retrieving activities
        self.test_get_activities()
        
        # Test updating an activity
        self.test_update_activity()
        
        # Test deleting an activity
        self.test_delete_activity()
        
        # Test error handling
        self.test_error_handling_invalid_registration_id()
        self.test_error_handling_invalid_activity_id()
        
        # Test validation
        self.test_validation_required_fields()
        
        print("\n" + "=" * 50)
        print(f"📊 Tests passed: {self.tests_passed}/{self.tests_run}")
        
        return self.tests_passed == self.tests_run


def main():
    # Run the tests
    tester = ActivityAPITester(BACKEND_URL)
    success = tester.run_all_tests()
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())