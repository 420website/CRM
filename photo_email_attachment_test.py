import requests
import unittest
import json
from datetime import datetime, date
import random
import string
import sys
import os
import base64
from dotenv import load_dotenv
import time

class PhotoEmailAttachmentTester:
    def __init__(self, base_url):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.test_data = {}
        self.registration_ids = {}

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

    def generate_base64_image(self, size_kb=50):
        """Generate a base64 encoded image for testing with specified size in KB"""
        # Create a base64 string of approximately the requested size
        base64_prefix = "data:image/jpeg;base64,"
        # Generate random data to simulate an image of the requested size
        # Each base64 character represents 6 bits, so 4/3 characters per byte
        # We need size_kb * 1024 * 4/3 characters
        chars_needed = int(size_kb * 1024 * 4/3)
        random_data = ''.join(random.choices(string.ascii_letters + string.digits + '+/', k=chars_needed))
        return base64_prefix + random_data

    def generate_test_data(self, photo_size_kb=None, test_name=""):
        """Generate random test data for admin registration with optional photo size"""
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
        today = date.today()
        today_str = today.isoformat()
        dob_date = date(today.year - 40, today.month, today.day)
        dob_str = dob_date.isoformat()
        
        # Generate photo data if size is specified
        photo_data = None
        if photo_size_kb is not None:
            photo_data = self.generate_base64_image(photo_size_kb)
            photo_info = f" with {photo_size_kb}KB photo"
        else:
            photo_info = " without photo"
        
        test_data = {
            "firstName": f"{test_name}{random_suffix}",
            "lastName": f"Test{photo_info}",
            "dob": dob_str,
            "patientConsent": "Verbal",
            "gender": "Male",
            "province": "Ontario",
            "disposition": "POCT NEG",
            "aka": f"Test{random_suffix}",
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
            "email": f"test.{random_suffix}@example.com",
            "language": "English",
            "specialAttention": f"Test registration {test_name}{photo_info}",
            "physician": "Dr. David Fletcher",
            "summaryTemplate": f"Test registration {test_name}{photo_info}"
        }
        
        # Add photo if provided
        if photo_data:
            test_data["photo"] = photo_data
        
        return test_data

    def test_registration_with_photo(self, photo_size_kb, test_name):
        """Test creating and finalizing a registration with a photo of specified size"""
        # Generate test data with photo
        test_data = self.generate_test_data(photo_size_kb, test_name)
        
        # Step 1: Create registration
        success, response = self.run_test(
            f"Create Registration {test_name} with {photo_size_kb}KB Photo",
            "POST",
            "api/admin-register",
            200,
            data=test_data
        )
        
        if not success:
            return False, {}
        
        registration_id = response.get('registration_id')
        self.registration_ids[test_name] = registration_id
        print(f"✅ Registration created with ID: {registration_id}")
        
        # Step 2: Finalize registration
        success, response = self.run_test(
            f"Finalize Registration {test_name} with {photo_size_kb}KB Photo",
            "POST",
            f"api/admin-registration/{registration_id}/finalize",
            200
        )
        
        if success:
            # Verify email was sent
            if response.get('email_sent'):
                print(f"✅ Email with {photo_size_kb}KB photo was sent successfully")
            else:
                print(f"❌ Email with {photo_size_kb}KB photo failed to send: {response.get('email_error')}")
                success = False
        
        return success, response

    def test_registration_without_photo(self, test_name):
        """Test creating and finalizing a registration without a photo"""
        # Generate test data without photo
        test_data = self.generate_test_data(None, test_name)
        
        # Step 1: Create registration
        success, response = self.run_test(
            f"Create Registration {test_name} without Photo",
            "POST",
            "api/admin-register",
            200,
            data=test_data
        )
        
        if not success:
            return False, {}
        
        registration_id = response.get('registration_id')
        self.registration_ids[test_name] = registration_id
        print(f"✅ Registration created with ID: {registration_id}")
        
        # Step 2: Finalize registration
        success, response = self.run_test(
            f"Finalize Registration {test_name} without Photo",
            "POST",
            f"api/admin-registration/{registration_id}/finalize",
            200
        )
        
        if success:
            # Verify email was sent
            if response.get('email_sent'):
                print(f"✅ Email without photo was sent successfully")
            else:
                print(f"❌ Email without photo failed to send: {response.get('email_error')}")
                success = False
        
        return success, response

    def run_photo_email_tests(self):
        """Run tests for photo email attachments with various sizes"""
        print("🚀 Starting Photo Email Attachment Tests")
        print(f"🔗 Base URL: {self.base_url}")
        print("=" * 80)
        
        # Test 1: Registration without photo
        print("\n" + "=" * 80)
        print("🔍 TEST 1: Registration without Photo")
        print("=" * 80)
        success, _ = self.test_registration_without_photo("NoPhoto")
        if not success:
            print("❌ Registration without photo test failed")
        
        # Test 2: Registration with small photo (50KB)
        print("\n" + "=" * 80)
        print("🔍 TEST 2: Registration with Small Photo (50KB)")
        print("=" * 80)
        success, _ = self.test_registration_with_photo(50, "SmallPhoto")
        if not success:
            print("❌ Registration with small photo test failed")
        
        # Test 3: Registration with medium photo (500KB)
        print("\n" + "=" * 80)
        print("🔍 TEST 3: Registration with Medium Photo (500KB)")
        print("=" * 80)
        success, _ = self.test_registration_with_photo(500, "MediumPhoto")
        if not success:
            print("❌ Registration with medium photo test failed")
        
        # Test 4: Registration with large photo (1MB)
        print("\n" + "=" * 80)
        print("🔍 TEST 4: Registration with Large Photo (1MB)")
        print("=" * 80)
        success, _ = self.test_registration_with_photo(1000, "LargePhoto")
        if not success:
            print("❌ Registration with large photo test failed")
        
        # Test 5: Registration with very large photo (1.8MB - just under 2MB limit)
        print("\n" + "=" * 80)
        print("🔍 TEST 5: Registration with Very Large Photo (1.8MB)")
        print("=" * 80)
        success, _ = self.test_registration_with_photo(1800, "VeryLargePhoto")
        if not success:
            print("❌ Registration with very large photo test failed")
        
        # Summary
        print("\n" + "=" * 80)
        print(f"📊 Photo Email Tests passed: {self.tests_passed}/{self.tests_run}")
        print("=" * 80)
        
        if self.tests_passed == self.tests_run:
            print("✅ Photo Email Attachment Tests PASSED")
            return True
        else:
            print("❌ Photo Email Attachment Tests FAILED")
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
    
    # Run the photo email tests
    tester = PhotoEmailAttachmentTester(backend_url)
    success = tester.run_photo_email_tests()
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())