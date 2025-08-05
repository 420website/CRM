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
from PIL import Image
import io

class PhotoCompressionTester:
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
        """Generate a simple base64 encoded image for testing with specified size in KB"""
        # Create a small colored image
        width, height = 100, 100
        img = Image.new('RGB', (width, height), color=(73, 109, 137))
        
        # Save to bytes with quality to control size
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='JPEG', quality=95)
        
        # Get base64 string
        img_byte_arr.seek(0)
        base64_data = base64.b64encode(img_byte_arr.read()).decode('utf-8')
        
        # Add data URI prefix
        return f"data:image/jpeg;base64,{base64_data}"

    def generate_large_base64_image(self, target_size_kb=500):
        """Generate a larger base64 encoded image for testing (target size in KB)"""
        # Create a larger image to get closer to target size
        width, height = 800, 600
        img = Image.new('RGB', (width, height), color=(random.randint(0, 255), 
                                                      random.randint(0, 255), 
                                                      random.randint(0, 255)))
        
        # Draw some random content to make the image less compressible
        from PIL import ImageDraw
        draw = ImageDraw.Draw(img)
        for _ in range(100):
            x1, y1 = random.randint(0, width), random.randint(0, height)
            x2, y2 = random.randint(0, width), random.randint(0, height)
            color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            draw.line((x1, y1, x2, y2), fill=color, width=random.randint(1, 5))
        
        # Save to bytes with quality to control size
        img_byte_arr = io.BytesIO()
        
        # Start with high quality
        quality = 95
        img.save(img_byte_arr, format='JPEG', quality=quality)
        
        # Get current size in KB
        current_size_kb = len(img_byte_arr.getvalue()) / 1024
        
        # Adjust quality to get closer to target size
        attempts = 0
        while (abs(current_size_kb - target_size_kb) > target_size_kb * 0.1) and attempts < 10:
            attempts += 1
            img_byte_arr = io.BytesIO()
            
            if current_size_kb > target_size_kb:
                quality -= 5
            else:
                quality += 5
                
            quality = max(10, min(95, quality))  # Keep quality between 10 and 95
            
            img.save(img_byte_arr, format='JPEG', quality=quality)
            current_size_kb = len(img_byte_arr.getvalue()) / 1024
        
        # Get base64 string
        img_byte_arr.seek(0)
        base64_data = base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')
        
        print(f"Generated image with size: {current_size_kb:.2f}KB (target: {target_size_kb}KB) using quality: {quality}")
        
        # Add data URI prefix
        return f"data:image/jpeg;base64,{base64_data}"

    def generate_very_large_base64_image(self, target_size_kb=900):
        """Generate a very large base64 encoded image for testing (target size in KB)"""
        # Create a larger image to get closer to target size
        width, height = 1600, 1200
        img = Image.new('RGB', (width, height), color=(random.randint(0, 255), 
                                                      random.randint(0, 255), 
                                                      random.randint(0, 255)))
        
        # Draw some random content to make the image less compressible
        from PIL import ImageDraw
        draw = ImageDraw.Draw(img)
        for _ in range(500):
            x1, y1 = random.randint(0, width), random.randint(0, height)
            x2, y2 = random.randint(0, width), random.randint(0, height)
            color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            draw.line((x1, y1, x2, y2), fill=color, width=random.randint(1, 5))
        
        # Save to bytes with quality to control size
        img_byte_arr = io.BytesIO()
        
        # Start with high quality
        quality = 95
        img.save(img_byte_arr, format='JPEG', quality=quality)
        
        # Get current size in KB
        current_size_kb = len(img_byte_arr.getvalue()) / 1024
        
        # Adjust quality to get closer to target size
        attempts = 0
        while (abs(current_size_kb - target_size_kb) > target_size_kb * 0.1) and attempts < 10:
            attempts += 1
            img_byte_arr = io.BytesIO()
            
            if current_size_kb > target_size_kb:
                quality -= 5
            else:
                quality += 5
                
            quality = max(10, min(95, quality))  # Keep quality between 10 and 95
            
            img.save(img_byte_arr, format='JPEG', quality=quality)
            current_size_kb = len(img_byte_arr.getvalue()) / 1024
        
        # Get base64 string
        img_byte_arr.seek(0)
        base64_data = base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')
        
        print(f"Generated very large image with size: {current_size_kb:.2f}KB (target: {target_size_kb}KB) using quality: {quality}")
        
        # Add data URI prefix
        return f"data:image/jpeg;base64,{base64_data}"

    def generate_test_data(self):
        """Generate random test data for admin registration"""
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
        today = date.today()
        
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
        """Test admin registration with a small photo (under 100KB)"""
        if not self.test_data:
            self.generate_test_data()
        
        # Create data with a small photo
        data_with_small_photo = self.test_data["admin_registration"].copy()
        data_with_small_photo["photo"] = self.generate_sample_base64_image(size_kb=50)
        
        success, response = self.run_test(
            "Admin Registration - With Small Photo (50KB)",
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
                registration = collection.find_one({"id": self.test_data["admin_registration_with_small_photo_id"]})
                
                if registration:
                    # Check if photo is present and not empty
                    if "photo" in registration and registration["photo"]:
                        photo_size_kb = len(registration["photo"]) / 1024
                        print(f"✅ Small photo data verified in MongoDB (size: {photo_size_kb:.2f}KB)")
                        self.tests_passed += 1
                    else:
                        print("❌ Photo data not found or empty in stored data")
                else:
                    print(f"❌ Could not find registration with ID {self.test_data['admin_registration_with_small_photo_id']}")
            except Exception as e:
                print(f"❌ Error verifying small photo in MongoDB: {str(e)}")
        
        return success, response

    def test_admin_registration_with_medium_photo(self):
        """Test admin registration with a medium photo (around 500KB)"""
        if not self.test_data:
            self.generate_test_data()
        
        # Create data with a medium photo
        data_with_medium_photo = self.test_data["admin_registration"].copy()
        data_with_medium_photo["photo"] = self.generate_large_base64_image(target_size_kb=500)
        
        success, response = self.run_test(
            "Admin Registration - With Medium Photo (500KB)",
            "POST",
            "api/admin-register",
            200,
            data=data_with_medium_photo
        )
        
        if success:
            print(f"Admin Registration ID (with medium photo): {response.get('registration_id')}")
            self.test_data["admin_registration_with_medium_photo_id"] = response.get('registration_id')
            
            # Verify in MongoDB that the photo was stored
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
                registration = collection.find_one({"id": self.test_data["admin_registration_with_medium_photo_id"]})
                
                if registration:
                    # Check if photo is present and not empty
                    if "photo" in registration and registration["photo"]:
                        photo_size_kb = len(registration["photo"]) / 1024
                        print(f"✅ Medium photo data verified in MongoDB (size: {photo_size_kb:.2f}KB)")
                        self.tests_passed += 1
                    else:
                        print("❌ Photo data not found or empty in stored data")
                else:
                    print(f"❌ Could not find registration with ID {self.test_data['admin_registration_with_medium_photo_id']}")
            except Exception as e:
                print(f"❌ Error verifying medium photo in MongoDB: {str(e)}")
        
        return success, response

    def test_admin_registration_with_large_photo(self):
        """Test admin registration with a large photo (around 800KB)"""
        if not self.test_data:
            self.generate_test_data()
        
        # Create data with a large photo
        data_with_large_photo = self.test_data["admin_registration"].copy()
        data_with_large_photo["photo"] = self.generate_very_large_base64_image(target_size_kb=800)
        
        success, response = self.run_test(
            "Admin Registration - With Large Photo (800KB)",
            "POST",
            "api/admin-register",
            200,
            data=data_with_large_photo
        )
        
        if success:
            print(f"Admin Registration ID (with large photo): {response.get('registration_id')}")
            self.test_data["admin_registration_with_large_photo_id"] = response.get('registration_id')
            
            # Verify in MongoDB that the photo was stored
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
                registration = collection.find_one({"id": self.test_data["admin_registration_with_large_photo_id"]})
                
                if registration:
                    # Check if photo is present and not empty
                    if "photo" in registration and registration["photo"]:
                        photo_size_kb = len(registration["photo"]) / 1024
                        print(f"✅ Large photo data verified in MongoDB (size: {photo_size_kb:.2f}KB)")
                        self.tests_passed += 1
                    else:
                        print("❌ Photo data not found or empty in stored data")
                else:
                    print(f"❌ Could not find registration with ID {self.test_data['admin_registration_with_large_photo_id']}")
            except Exception as e:
                print(f"❌ Error verifying large photo in MongoDB: {str(e)}")
        
        return success, response

    def test_admin_registration_with_very_large_photo(self):
        """Test admin registration with a very large photo (over 1MB)"""
        if not self.test_data:
            self.generate_test_data()
        
        # Create data with a very large photo
        data_with_very_large_photo = self.test_data["admin_registration"].copy()
        data_with_very_large_photo["photo"] = self.generate_very_large_base64_image(target_size_kb=1200)
        
        success, response = self.run_test(
            "Admin Registration - With Very Large Photo (1.2MB)",
            "POST",
            "api/admin-register",
            200,  # We expect success even with large photos due to backend handling
            data=data_with_very_large_photo
        )
        
        if success:
            print(f"Admin Registration ID (with very large photo): {response.get('registration_id')}")
            self.test_data["admin_registration_with_very_large_photo_id"] = response.get('registration_id')
            
            # Verify in MongoDB that the photo was stored
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
                registration = collection.find_one({"id": self.test_data["admin_registration_with_very_large_photo_id"]})
                
                if registration:
                    # Check if photo is present and not empty
                    if "photo" in registration and registration["photo"]:
                        photo_size_kb = len(registration["photo"]) / 1024
                        print(f"✅ Very large photo data verified in MongoDB (size: {photo_size_kb:.2f}KB)")
                        self.tests_passed += 1
                    else:
                        print("❌ Photo data not found or empty in stored data")
                else:
                    print(f"❌ Could not find registration with ID {self.test_data['admin_registration_with_very_large_photo_id']}")
            except Exception as e:
                print(f"❌ Error verifying very large photo in MongoDB: {str(e)}")
        
        return success, response

    def test_network_reliability(self):
        """Test network reliability with multiple consecutive photo uploads"""
        if not self.test_data:
            self.generate_test_data()
        
        print("\n" + "=" * 50)
        print("🔍 Testing Network Reliability with Multiple Photo Uploads")
        print("=" * 50)
        
        # Number of consecutive uploads to test
        num_uploads = 5
        success_count = 0
        
        for i in range(num_uploads):
            # Create data with a medium-sized photo
            data_with_photo = self.test_data["admin_registration"].copy()
            data_with_photo["firstName"] = f"Network{i}"
            data_with_photo["lastName"] = f"Test{i}"
            data_with_photo["photo"] = self.generate_large_base64_image(target_size_kb=500)
            
            print(f"\n🔍 Network Reliability Test - Upload {i+1}/{num_uploads}")
            success, response = self.run_test(
                f"Network Reliability - Upload {i+1}",
                "POST",
                "api/admin-register",
                200,
                data=data_with_photo
            )
            
            if success:
                success_count += 1
                print(f"✅ Upload {i+1} successful - Registration ID: {response.get('registration_id')}")
            else:
                print(f"❌ Upload {i+1} failed")
            
            # Small delay between requests to avoid overwhelming the server
            time.sleep(1)
        
        reliability_percentage = (success_count / num_uploads) * 100
        print(f"\n✅ Network Reliability Test Results: {success_count}/{num_uploads} successful ({reliability_percentage:.1f}%)")
        
        if success_count == num_uploads:
            self.tests_passed += 1
            return True, {"reliability_percentage": reliability_percentage}
        else:
            return False, {"reliability_percentage": reliability_percentage}

    def run_all_tests(self):
        """Run all photo compression tests"""
        print("🚀 Starting Photo Compression Tests for Admin Registration System")
        print(f"🔗 Base URL: {self.base_url}")
        print("=" * 50)
        
        # Generate test data
        self.generate_test_data()
        
        # Test without photo
        self.test_admin_registration_without_photo()
        
        # Test with different photo sizes
        self.test_admin_registration_with_small_photo()
        self.test_admin_registration_with_medium_photo()
        self.test_admin_registration_with_large_photo()
        self.test_admin_registration_with_very_large_photo()
        
        # Test network reliability
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
    tester = PhotoCompressionTester(backend_url)
    success = tester.run_all_tests()
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())