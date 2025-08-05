#!/usr/bin/env python3
"""
Activity Backend API Testing Suite
Focus: Test Activity CRUD operations as requested in review
"""

import requests
import json
import sys
import os
from datetime import datetime, date
import random
import string
from dotenv import load_dotenv

class ActivityBackendTester:
    def __init__(self, base_url):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.test_data = {}
        self.registration_id = None
        
    def log_test(self, name, success, details=""):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name}")
            if details:
                print(f"   {details}")
        else:
            print(f"❌ {name}")
            if details:
                print(f"   {details}")
    
    def make_request(self, method, endpoint, data=None, expected_status=200):
        """Make HTTP request and return success status and response"""
        url = f"{self.base_url}/api/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers)
            else:
                return False, {"error": f"Unsupported method: {method}"}
            
            success = response.status_code == expected_status
            
            try:
                response_data = response.json()
            except:
                response_data = {"text": response.text, "status_code": response.status_code}
            
            if not success:
                print(f"   Expected status {expected_status}, got {response.status_code}")
                if response_data:
                    print(f"   Response: {response_data}")
            
            return success, response_data
            
        except Exception as e:
            print(f"   Request failed: {str(e)}")
            return False, {"error": str(e)}
    
    def setup_test_registration(self):
        """Create a test admin registration for activity testing"""
        print("\n🔧 Setting up test registration for activity tests...")
        
        # Generate unique test data
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
        
        registration_data = {
            "firstName": f"Activity Test {random_suffix}",
            "lastName": f"User {random_suffix}",
            "patientConsent": "Verbal",
            "email": f"activity.test.{random_suffix}@example.com"
        }
        
        success, response = self.make_request(
            'POST', 
            'admin-register', 
            registration_data, 
            200
        )
        
        if success and 'registration_id' in response:
            self.registration_id = response['registration_id']
            print(f"✅ Created test registration: {self.registration_id}")
            return True
        else:
            print(f"❌ Failed to create test registration: {response}")
            return False
    
    def test_health_check(self):
        """Test basic health check endpoint"""
        print("\n🏥 Testing Health Check Endpoint...")
        
        success, response = self.make_request('GET', '', expected_status=200)
        self.log_test(
            "Health Check Endpoint", 
            success,
            f"Response: {response}" if success else f"Failed: {response}"
        )
        return success
    
    def test_activity_create(self):
        """Test creating activity records"""
        print("\n📝 Testing Activity Creation...")
        
        if not self.registration_id:
            print("❌ No registration ID available for activity tests")
            return False
        
        # Test 1: Create activity with all fields
        activity_data = {
            "date": date.today().isoformat(),
            "time": "14:30",
            "description": "Initial consultation and assessment"
        }
        
        success, response = self.make_request(
            'POST',
            f'admin-registration/{self.registration_id}/activity',
            activity_data,
            200
        )
        
        if success and 'activity_id' in response:
            self.test_data['activity_id'] = response['activity_id']
            self.log_test(
                "Create Activity - All Fields",
                True,
                f"Activity ID: {response['activity_id']}"
            )
        else:
            self.log_test("Create Activity - All Fields", False, f"Response: {response}")
            return False
        
        # Test 2: Create activity with minimal fields (only required)
        minimal_activity = {
            "date": date.today().isoformat(),
            "description": "Follow-up appointment"
        }
        
        success, response = self.make_request(
            'POST',
            f'admin-registration/{self.registration_id}/activity',
            minimal_activity,
            200
        )
        
        if success and 'activity_id' in response:
            self.test_data['minimal_activity_id'] = response['activity_id']
            self.log_test(
                "Create Activity - Minimal Fields",
                True,
                f"Activity ID: {response['activity_id']}"
            )
        else:
            self.log_test("Create Activity - Minimal Fields", False, f"Response: {response}")
        
        # Test 3: Create activity with missing required field (should fail)
        invalid_activity = {
            "time": "15:00"
            # Missing date and description
        }
        
        success, response = self.make_request(
            'POST',
            f'admin-registration/{self.registration_id}/activity',
            invalid_activity,
            422  # Validation error
        )
        
        self.log_test(
            "Create Activity - Missing Required Fields",
            success,
            "Correctly rejected invalid data" if success else f"Unexpected response: {response}"
        )
        
        return True
    
    def test_activity_read(self):
        """Test reading activity records"""
        print("\n📖 Testing Activity Retrieval...")
        
        if not self.registration_id:
            print("❌ No registration ID available for activity tests")
            return False
        
        # Test: Get all activities for registration
        success, response = self.make_request(
            'GET',
            f'admin-registration/{self.registration_id}/activities',
            expected_status=200
        )
        
        if success and 'activities' in response:
            activities = response['activities']
            self.log_test(
                "Get All Activities",
                True,
                f"Retrieved {len(activities)} activities"
            )
            
            # Verify our created activities are in the response
            if self.test_data.get('activity_id'):
                found = any(activity['id'] == self.test_data['activity_id'] for activity in activities)
                self.log_test(
                    "Verify Created Activity in List",
                    found,
                    "Activity found in list" if found else "Activity not found in list"
                )
            
            # Verify activity structure
            if activities:
                activity = activities[0]
                required_fields = ['id', 'date', 'description', 'created_at', 'updated_at']
                has_all_fields = all(field in activity for field in required_fields)
                self.log_test(
                    "Activity Response Structure",
                    has_all_fields,
                    "All required fields present" if has_all_fields else f"Missing fields in: {activity}"
                )
        else:
            self.log_test("Get All Activities", False, f"Response: {response}")
            return False
        
        return True
    
    def test_activity_update(self):
        """Test updating activity records"""
        print("\n✏️ Testing Activity Updates...")
        
        if not self.registration_id or not self.test_data.get('activity_id'):
            print("❌ No registration ID or activity ID available for update tests")
            return False
        
        activity_id = self.test_data['activity_id']
        
        # Test: Update activity
        update_data = {
            "date": date.today().isoformat(),
            "time": "16:00",
            "description": "Updated consultation notes - patient responded well to treatment"
        }
        
        success, response = self.make_request(
            'PUT',
            f'admin-registration/{self.registration_id}/activity/{activity_id}',
            update_data,
            200
        )
        
        self.log_test(
            "Update Activity",
            success,
            "Activity updated successfully" if success else f"Update failed: {response}"
        )
        
        if success:
            # Verify the update by retrieving the activity
            success, response = self.make_request(
                'GET',
                f'admin-registration/{self.registration_id}/activities',
                expected_status=200
            )
            
            if success and 'activities' in response:
                activities = response['activities']
                updated_activity = next((a for a in activities if a['id'] == activity_id), None)
                
                if updated_activity:
                    # Check if the description was updated
                    if updated_activity['description'] == update_data['description']:
                        self.log_test(
                            "Verify Activity Update",
                            True,
                            "Activity description updated correctly"
                        )
                    else:
                        self.log_test(
                            "Verify Activity Update",
                            False,
                            f"Description not updated. Expected: {update_data['description']}, Got: {updated_activity['description']}"
                        )
                else:
                    self.log_test("Verify Activity Update", False, "Updated activity not found")
            else:
                self.log_test("Verify Activity Update", False, "Failed to retrieve activities for verification")
        
        # Test: Update with invalid activity ID (should fail)
        success, response = self.make_request(
            'PUT',
            f'admin-registration/{self.registration_id}/activity/invalid-id',
            update_data,
            404  # Not found
        )
        
        self.log_test(
            "Update Activity - Invalid ID",
            success,
            "Correctly rejected invalid activity ID" if success else f"Unexpected response: {response}"
        )
        
        return True
    
    def test_activity_delete(self):
        """Test deleting activity records"""
        print("\n🗑️ Testing Activity Deletion...")
        
        if not self.registration_id or not self.test_data.get('minimal_activity_id'):
            print("❌ No registration ID or activity ID available for delete tests")
            return False
        
        activity_id = self.test_data['minimal_activity_id']
        
        # First, verify the activity exists
        success, response = self.make_request(
            'GET',
            f'admin-registration/{self.registration_id}/activities',
            expected_status=200
        )
        
        if success and 'activities' in response:
            activities = response['activities']
            activity_exists = any(a['id'] == activity_id for a in activities)
            
            if not activity_exists:
                print(f"❌ Activity {activity_id} not found before deletion test")
                return False
        
        # Test: Delete activity
        success, response = self.make_request(
            'DELETE',
            f'admin-registration/{self.registration_id}/activity/{activity_id}',
            expected_status=200
        )
        
        self.log_test(
            "Delete Activity",
            success,
            "Activity deleted successfully" if success else f"Delete failed: {response}"
        )
        
        if success:
            # Verify the deletion by checking if activity is gone
            success, response = self.make_request(
                'GET',
                f'admin-registration/{self.registration_id}/activities',
                expected_status=200
            )
            
            if success and 'activities' in response:
                activities = response['activities']
                activity_still_exists = any(a['id'] == activity_id for a in activities)
                
                self.log_test(
                    "Verify Activity Deletion",
                    not activity_still_exists,
                    "Activity successfully removed from list" if not activity_still_exists else "Activity still exists after deletion"
                )
            else:
                self.log_test("Verify Activity Deletion", False, "Failed to retrieve activities for verification")
        
        # Test: Delete with invalid activity ID (should fail)
        success, response = self.make_request(
            'DELETE',
            f'admin-registration/{self.registration_id}/activity/invalid-id',
            expected_status=404  # Not found
        )
        
        self.log_test(
            "Delete Activity - Invalid ID",
            success,
            "Correctly rejected invalid activity ID" if success else f"Unexpected response: {response}"
        )
        
        return True
    
    def test_activity_validation(self):
        """Test activity validation rules"""
        print("\n🔍 Testing Activity Validation...")
        
        if not self.registration_id:
            print("❌ No registration ID available for validation tests")
            return False
        
        # Test 1: Missing date (required field)
        invalid_data = {
            "time": "10:00",
            "description": "Test activity"
        }
        
        success, response = self.make_request(
            'POST',
            f'admin-registration/{self.registration_id}/activity',
            invalid_data,
            422  # Validation error
        )
        
        self.log_test(
            "Validation - Missing Date",
            success,
            "Correctly rejected missing date" if success else f"Unexpected response: {response}"
        )
        
        # Test 2: Missing description (required field)
        invalid_data = {
            "date": date.today().isoformat(),
            "time": "10:00"
        }
        
        success, response = self.make_request(
            'POST',
            f'admin-registration/{self.registration_id}/activity',
            invalid_data,
            422  # Validation error
        )
        
        self.log_test(
            "Validation - Missing Description",
            success,
            "Correctly rejected missing description" if success else f"Unexpected response: {response}"
        )
        
        # Test 3: Invalid registration ID
        valid_data = {
            "date": date.today().isoformat(),
            "description": "Test activity"
        }
        
        success, response = self.make_request(
            'POST',
            'admin-registration/invalid-id/activity',
            valid_data,
            404  # Not found
        )
        
        self.log_test(
            "Validation - Invalid Registration ID",
            success,
            "Correctly rejected invalid registration ID" if success else f"Unexpected response: {response}"
        )
        
        return True
    
    def test_admin_registration_crud(self):
        """Test basic admin registration CRUD operations"""
        print("\n👤 Testing Admin Registration CRUD...")
        
        # Test: Create admin registration
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
        registration_data = {
            "firstName": f"CRUD Test {random_suffix}",
            "lastName": f"User {random_suffix}",
            "patientConsent": "Written",
            "email": f"crud.test.{random_suffix}@example.com",
            "phone1": "4161234567",
            "province": "Ontario"
        }
        
        success, response = self.make_request(
            'POST',
            'admin-register',
            registration_data,
            200
        )
        
        if success and 'registration_id' in response:
            crud_registration_id = response['registration_id']
            self.log_test(
                "Create Admin Registration",
                True,
                f"Registration ID: {crud_registration_id}"
            )
        else:
            self.log_test("Create Admin Registration", False, f"Response: {response}")
            return False
        
        # Test: Read admin registration (via activities endpoint to verify it exists)
        success, response = self.make_request(
            'GET',
            f'admin-registration/{crud_registration_id}/activities',
            expected_status=200
        )
        
        self.log_test(
            "Read Admin Registration (via activities)",
            success,
            "Registration accessible" if success else f"Response: {response}"
        )
        
        return True
    
    def run_all_tests(self):
        """Run all activity backend tests"""
        print("🚀 Starting Activity Backend API Tests")
        print(f"🔗 Base URL: {self.base_url}")
        print("=" * 60)
        
        # Test 1: Health check
        health_success = self.test_health_check()
        
        # Test 2: Setup test registration
        setup_success = self.setup_test_registration()
        if not setup_success:
            print("❌ Cannot continue without test registration")
            return False
        
        # Test 3: Admin registration CRUD
        admin_crud_success = self.test_admin_registration_crud()
        
        # Test 4: Activity CRUD operations
        create_success = self.test_activity_create()
        read_success = self.test_activity_read()
        update_success = self.test_activity_update()
        delete_success = self.test_activity_delete()
        
        # Test 5: Activity validation
        validation_success = self.test_activity_validation()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        if self.tests_passed == self.tests_run:
            print("🎉 ALL TESTS PASSED!")
            return True
        else:
            print(f"❌ {self.tests_run - self.tests_passed} tests failed")
            return False

def main():
    """Main test execution"""
    # Get the backend URL from the frontend .env file
    load_dotenv('/app/frontend/.env')
    
    backend_url = os.environ.get('REACT_APP_BACKEND_URL')
    if not backend_url:
        print("❌ Error: REACT_APP_BACKEND_URL not found in frontend .env file")
        return 1
    
    print(f"🔗 Using backend URL from .env: {backend_url}")
    
    # Run tests
    tester = ActivityBackendTester(backend_url)
    success = tester.run_all_tests()
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())