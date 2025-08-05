import requests
import unittest
import json
from datetime import datetime, date
import random
import string
import sys
import base64
import os
from dotenv import load_dotenv
import time

class AdminRegistrationFinalTester:
    def __init__(self, base_url):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.test_data = {}

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

    def generate_sample_base64_image(self, size_kb=1):
        """Generate a base64 encoded image for testing with specified size in KB"""
        # This is a tiny 1x1 pixel transparent PNG image encoded as base64
        base64_prefix = "data:image/png;base64,"
        # Repeat the base64 data to create a string of the specified size
        base_data = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
        # Calculate how many times to repeat to get approximately the desired size
        # Each character in base64 is approximately 0.75 bytes
        repeat_count = int((size_kb * 1024) / (len(base_data) * 0.75))
        base64_data = base_data * max(1, repeat_count)
        
        # Trim to approximate size
        target_length = int(size_kb * 1024 * 4/3)  # base64 is ~4/3 the size of binary
        if len(base64_data) > target_length:
            base64_data = base64_data[:target_length]
            
        return base64_prefix + base64_data

    def generate_test_data(self):
        """Generate random test data for admin registration"""
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
        today = date.today()
        today_str = today.isoformat()  # Convert to string format
        dob_date = date(today.year - 40, today.month, today.day)
        dob_str = dob_date.isoformat()  # Convert to string format
        
        self.test_data = {
            "admin_registration": {
                "firstName": f"Michael {random_suffix}",
                "lastName": f"Smith {random_suffix}",
                "dob": dob_str,
                "patientConsent": "Verbal",
                "gender": "Male",
                "province": "Ontario",
                "fileNumber": f"FILE-{random.randint(10000, 99999)}",
                "disposition": f"Disposition Option {random.randint(1, 70)}",
                "aka": f"Mike {random_suffix}",
                "age": "40",
                "regDate": today_str,
                "healthCard": ''.join(random.choices(string.digits, k=10)),
                "referralSite": "Community Clinic",
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
                "specialAttention": "Patient requires interpreter assistance"
            }
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

    def test_complete_admin_registration(self):
        """Test admin registration with all fields filled"""
        if not self.test_data:
            self.generate_test_data()
            
        # Add a small photo to the registration data
        self.test_data["admin_registration"]["photo"] = self.generate_sample_base64_image(50)
            
        success, response = self.run_test(
            "Complete Admin Registration Form Submission",
            "POST",
            "api/admin-register",
            200,
            data=self.test_data["admin_registration"]
        )
        
        if success:
            print(f"✅ Complete form submission successful")
            print(f"Registration ID: {response.get('registration_id')}")
            self.test_data["admin_registration_id"] = response.get('registration_id')
            
        return success, response

    def test_photo_upload_integration(self):
        """Test admin registration with photo upload and verify email attachment"""
        if not self.test_data:
            self.generate_test_data()
            
        # Add a compressed photo to the registration data (500KB)
        self.test_data["admin_registration"]["photo"] = self.generate_sample_base64_image(500)
        
        # Make the registration data unique
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
        self.test_data["admin_registration"]["firstName"] = f"Photo {random_suffix}"
        self.test_data["admin_registration"]["lastName"] = f"Test {random_suffix}"
            
        success, response = self.run_test(
            "Admin Registration with Photo Upload",
            "POST",
            "api/admin-register",
            200,
            data=self.test_data["admin_registration"]
        )
        
        if success:
            print(f"✅ Photo upload integration successful")
            print(f"Registration ID: {response.get('registration_id')}")
            self.test_data["photo_registration_id"] = response.get('registration_id')
            
            # Verify in MongoDB that the photo was stored
            try:
                from pymongo import MongoClient
                
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
                registration = collection.find_one({"id": self.test_data["photo_registration_id"]})
                
                if registration:
                    # Check if photo is present and not empty
                    if "photo" in registration and registration["photo"]:
                        photo_length = len(registration["photo"])
                        print(f"✅ Photo data verified in MongoDB (length: {photo_length} characters)")
                        self.tests_passed += 1
                    else:
                        print("❌ Photo data not found or empty in stored data")
                else:
                    print(f"❌ Could not find registration with ID {self.test_data['photo_registration_id']}")
            except Exception as e:
                print(f"❌ Error verifying photo in MongoDB: {str(e)}")
            
        return success, response

    def test_error_handling(self):
        """Test various error scenarios for admin registration"""
        if not self.test_data:
            self.generate_test_data()
        
        print("\n🔍 Testing Error Handling Scenarios...")
        
        # Test 1: Missing required field - firstName
        invalid_data = self.test_data["admin_registration"].copy()
        invalid_data.pop("firstName")
        success1, response1 = self.run_test(
            "Error Handling - Missing First Name",
            "POST",
            "api/admin-register",
            422,  # Validation error status code
            data=invalid_data
        )
        
        # Test 2: Missing required field - lastName
        invalid_data = self.test_data["admin_registration"].copy()
        invalid_data.pop("lastName")
        success2, response2 = self.run_test(
            "Error Handling - Missing Last Name",
            "POST",
            "api/admin-register",
            422,  # Validation error status code
            data=invalid_data
        )
        
        # Test 3: Missing required field - patientConsent
        invalid_data = self.test_data["admin_registration"].copy()
        invalid_data.pop("patientConsent")
        success3, response3 = self.run_test(
            "Error Handling - Missing Patient Consent",
            "POST",
            "api/admin-register",
            422,  # Validation error status code
            data=invalid_data
        )
        
        # Test 4: Invalid email format
        invalid_data = self.test_data["admin_registration"].copy()
        invalid_data["email"] = "invalid-email"
        success4, response4 = self.run_test(
            "Error Handling - Invalid Email Format",
            "POST",
            "api/admin-register",
            422,  # Validation error status code
            data=invalid_data
        )
        
        # Test 5: Very large photo (1.2MB)
        large_photo_data = self.test_data["admin_registration"].copy()
        large_photo_data["photo"] = self.generate_sample_base64_image(1200)  # 1.2MB
        success5, response5 = self.run_test(
            "Error Handling - Very Large Photo (1.2MB)",
            "POST",
            "api/admin-register",
            200,  # Should still succeed with large photo
            data=large_photo_data
        )
        
        # Check if all error handling tests passed
        error_handling_success = all([
            success1 == False,  # Should fail with 422
            success2 == False,  # Should fail with 422
            success3 == False,  # Should fail with 422
            success4 == False,  # Should fail with 422
            success5 == True    # Should succeed with large photo
        ])
        
        if error_handling_success:
            print("✅ Error handling tests completed successfully")
            self.tests_passed += 1
        else:
            print("❌ Some error handling tests failed")
            
        return error_handling_success, {
            "missing_firstName": success1,
            "missing_lastName": success2,
            "missing_patientConsent": success3,
            "invalid_email": success4,
            "large_photo": success5
        }

    def test_network_reliability(self):
        """Test network reliability with multiple consecutive submissions"""
        if not self.test_data:
            self.generate_test_data()
            
        print("\n🔍 Testing Network Reliability with Multiple Submissions...")
        
        # Number of consecutive submissions to test
        num_tests = 5
        successes = 0
        
        for i in range(num_tests):
            # Create unique data for each submission
            random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
            test_data = self.test_data["admin_registration"].copy()
            test_data["firstName"] = f"Network{i} {random_suffix}"
            test_data["lastName"] = f"Test{i} {random_suffix}"
            
            # Add a medium-sized photo (300KB)
            test_data["photo"] = self.generate_sample_base64_image(300)
            
            print(f"\n🔄 Network Reliability Test {i+1}/{num_tests}")
            success, response = self.run_test(
                f"Network Reliability - Submission {i+1}",
                "POST",
                "api/admin-register",
                200,
                data=test_data
            )
            
            if success:
                successes += 1
                print(f"✅ Submission {i+1} successful - Registration ID: {response.get('registration_id')}")
            else:
                print(f"❌ Submission {i+1} failed")
                
            # Add a small delay between requests to avoid overwhelming the server
            time.sleep(1)
        
        reliability_percentage = (successes / num_tests) * 100
        print(f"\n📊 Network Reliability: {reliability_percentage}% ({successes}/{num_tests} successful)")
        
        if reliability_percentage == 100:
            print("✅ Network reliability test passed with 100% success rate")
            self.tests_passed += 1
        else:
            print(f"❌ Network reliability test failed with {reliability_percentage}% success rate")
            
        return reliability_percentage == 100, {
            "success_rate": reliability_percentage,
            "successes": successes,
            "total_tests": num_tests
        }

    def run_all_tests(self):
        """Run all final validation tests for admin registration system"""
        print("🚀 Starting Final Validation Tests for Admin Registration System")
        print(f"🔗 Base URL: {self.base_url}")
        print("=" * 80)
        
        # Generate test data
        self.generate_test_data()
        
        # Test API health
        self.test_api_health()
        
        # Test complete form submission
        print("\n" + "=" * 80)
        print("🔍 Testing Complete Form Submission")
        print("=" * 80)
        self.test_complete_admin_registration()
        
        # Test photo upload integration
        print("\n" + "=" * 80)
        print("🔍 Testing Photo Upload Integration")
        print("=" * 80)
        self.test_photo_upload_integration()
        
        # Test error handling
        print("\n" + "=" * 80)
        print("🔍 Testing Error Handling")
        print("=" * 80)
        self.test_error_handling()
        
        # Test network reliability
        print("\n" + "=" * 80)
        print("🔍 Testing Network Reliability")
        print("=" * 80)
        self.test_network_reliability()
        
        # Print summary
        print("\n" + "=" * 80)
        print(f"📊 Final Validation Tests Summary: {self.tests_passed}/{self.tests_run} tests passed")
        print("=" * 80)
        
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
    tester = AdminRegistrationFinalTester(backend_url)
    success = tester.run_all_tests()
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())