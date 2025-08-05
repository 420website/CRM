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

class AdminPhotoTester:
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

    def generate_sample_base64_image(self):
        """Generate a simple base64 encoded image for testing"""
        # This is a tiny 1x1 pixel transparent PNG image encoded as base64
        return "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
        
    def generate_large_base64_image(self):
        """Generate a larger base64 encoded image for testing"""
        # Create a larger base64 string (approximately 10KB)
        base64_prefix = "data:image/png;base64,"
        # Repeat the base64 data to create a larger string
        base64_data = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==" * 100
        return base64_prefix + base64_data

    def generate_test_data(self):
        """Generate random test data for registration"""
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
        today = date.today()
        today_str = today.isoformat()  # Convert to string format
        dob_date = date(today.year - 40, today.month, today.day)
        dob_str = dob_date.isoformat()  # Convert to string format
        
        # Generate sample base64 image
        sample_image = self.generate_sample_base64_image()
        
        self.test_data = {
            "admin_registration": {
                "firstName": f"Michael {random_suffix}",
                "lastName": f"Smith {random_suffix}",
                "dob": None,  # Set to None to avoid date serialization issues
                "patientConsent": "Verbal",
                "gender": "Male",
                "province": "Ontario",  # Default value that should be used
                "fileNumber": f"FILE-{random.randint(10000, 99999)}",
                "disposition": f"Disposition Option {random.randint(1, 70)}",
                "aka": f"Mike {random_suffix}",
                "age": str(40),
                "regDate": None,  # Set to None to avoid date serialization issues
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
                "specialAttention": "Patient requires interpreter assistance",
                "photo": sample_image  # Add base64 encoded photo
            }
        }
        
        return self.test_data

    def test_admin_registration_without_photo(self):
        """Test admin registration without photo data"""
        if not self.test_data:
            self.generate_test_data()
        
        # Create data without photo field
        data_without_photo = self.test_data["admin_registration"].copy()
        if "photo" in data_without_photo:
            data_without_photo.pop("photo")
        
        success, response = self.run_test(
            "Admin Registration - Without Photo",
            "POST",
            "api/admin-register",
            200,
            data=data_without_photo
        )
        
        if success:
            print(f"Admin Registration ID (without photo): {response.get('registration_id')}")
            self.test_data["admin_registration_without_photo_id"] = response.get('registration_id')
            
            # Verify in MongoDB that the photo field is null or not present
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
                registration = collection.find_one({"id": self.test_data["admin_registration_without_photo_id"]})
                
                if registration:
                    # Check if photo is not present or null
                    if "photo" not in registration or registration["photo"] is None:
                        print("✅ Photo field correctly null or not present in MongoDB")
                        self.tests_passed += 1
                    else:
                        print(f"❌ Photo field unexpectedly present in MongoDB: {registration['photo']}")
                else:
                    print(f"❌ Could not find registration with ID {self.test_data['admin_registration_without_photo_id']}")
            except Exception as e:
                print(f"❌ Error verifying photo absence in MongoDB: {str(e)}")
        
        return success, response
        
    def test_admin_registration_with_small_photo(self):
        """Test admin registration with a small photo"""
        if not self.test_data:
            self.generate_test_data()
        
        # Create data with a small photo
        data_with_small_photo = self.test_data["admin_registration"].copy()
        data_with_small_photo["photo"] = self.generate_sample_base64_image()
        
        success, response = self.run_test(
            "Admin Registration - With Small Photo",
            "POST",
            "api/admin-register",
            200,
            data=data_with_small_photo
        )
        
        if success:
            print(f"Admin Registration ID (with small photo): {response.get('registration_id')}")
            self.test_data["admin_registration_with_small_photo_id"] = response.get('registration_id')
            
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
                registration = collection.find_one({"id": self.test_data["admin_registration_with_small_photo_id"]})
                
                if registration:
                    # Check if photo is present and not empty
                    if "photo" in registration and registration["photo"]:
                        print(f"✅ Small photo data verified in MongoDB (length: {len(registration['photo'])})")
                        self.tests_passed += 1
                    else:
                        print("❌ Photo data not found or empty in stored data")
                else:
                    print(f"❌ Could not find registration with ID {self.test_data['admin_registration_with_small_photo_id']}")
            except Exception as e:
                print(f"❌ Error verifying photo in MongoDB: {str(e)}")
        
        return success, response
        
    def test_admin_registration_with_large_photo(self):
        """Test admin registration with a large photo"""
        if not self.test_data:
            self.generate_test_data()
        
        # Create data with a large photo
        data_with_large_photo = self.test_data["admin_registration"].copy()
        data_with_large_photo["photo"] = self.generate_large_base64_image()
        
        success, response = self.run_test(
            "Admin Registration - With Large Photo",
            "POST",
            "api/admin-register",
            200,
            data=data_with_large_photo
        )
        
        if success:
            print(f"Admin Registration ID (with large photo): {response.get('registration_id')}")
            self.test_data["admin_registration_with_large_photo_id"] = response.get('registration_id')
            
            # Verify in MongoDB that the large photo was stored
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
                registration = collection.find_one({"id": self.test_data["admin_registration_with_large_photo_id"]})
                
                if registration:
                    # Check if photo is present and has the expected large size
                    if "photo" in registration and registration["photo"]:
                        photo_length = len(registration["photo"])
                        if photo_length > 5000:  # Expecting a large photo (>5KB)
                            print(f"✅ Large photo data verified in MongoDB (length: {photo_length})")
                            self.tests_passed += 1
                        else:
                            print(f"❌ Photo data smaller than expected: {photo_length} bytes")
                    else:
                        print("❌ Photo data not found or empty in stored data")
                else:
                    print(f"❌ Could not find registration with ID {self.test_data['admin_registration_with_large_photo_id']}")
            except Exception as e:
                print(f"❌ Error verifying large photo in MongoDB: {str(e)}")
        
        return success, response

    def test_network_reliability(self):
        """Test network reliability with photo uploads"""
        if not self.test_data:
            self.generate_test_data()
        
        print("\n🔍 Testing Network Reliability with Photo Uploads...")
        
        # Test 1: Multiple consecutive requests with photos
        success_count = 0
        total_tests = 3
        
        for i in range(total_tests):
            # Create a new random data set for each test
            self.generate_test_data()
            data = self.test_data["admin_registration"].copy()
            
            # Add a large photo to test network reliability
            data["photo"] = self.generate_large_base64_image()
            
            print(f"\n🔍 Network Reliability Test {i+1}/{total_tests}...")
            success, response = self.run_test(
                f"Network Reliability - Large Photo Upload {i+1}",
                "POST",
                "api/admin-register",
                200,
                data=data
            )
            
            if success:
                success_count += 1
                print(f"✅ Registration ID: {response.get('registration_id')}")
            
            # Add a small delay between requests to simulate real-world conditions
            time.sleep(1)
        
        print(f"\n✅ Network Reliability Test Results: {success_count}/{total_tests} successful uploads")
        
        if success_count == total_tests:
            self.tests_passed += 1
            return True, {"success_rate": f"{success_count}/{total_tests}"}
        else:
            return False, {"success_rate": f"{success_count}/{total_tests}"}

    def run_photo_tests(self):
        """Run all photo-related tests"""
        print("🚀 Starting Admin Registration Photo Tests")
        print(f"🔗 Base URL: {self.base_url}")
        print("=" * 50)
        
        # Generate test data
        self.generate_test_data()
        
        # Test 1: Admin registration without photo
        self.test_admin_registration_without_photo()
        
        # Test 2: Admin registration with small photo
        self.test_admin_registration_with_small_photo()
        
        # Test 3: Admin registration with large photo
        self.test_admin_registration_with_large_photo()
        
        # Test 4: Network reliability
        self.test_network_reliability()
        
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
    tester = AdminPhotoTester(backend_url)
    success = tester.run_photo_tests()
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())