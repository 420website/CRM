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

class HCVTestTester:
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

    def generate_sample_base64_image(self):
        """Generate a simple base64 encoded image for testing"""
        # This is a tiny 1x1 pixel transparent PNG image encoded as base64
        return "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
        
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
                "dob": dob_str,
                "patientConsent": "Verbal",
                "gender": "Male",
                "province": "Ontario",  # Default value that should be used
                "disposition": f"Disposition Option {random.randint(1, 70)}",
                "aka": f"Mike {random_suffix}",
                "age": str(40),
                "regDate": today_str,
                "healthCard": ''.join(random.choices(string.digits, k=10)),
                "healthCardVersion": "AB",
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
            },
            "hcv_test": {
                "test_type": "HCV",
                "test_date": today_str,
                "hcv_result": "positive",
                "hcv_tester": "JY"
            },
            "hcv_test_update": {
                "hcv_result": "negative",
                "hcv_tester": "CM"
            },
            "hiv_test": {
                "test_type": "HIV",
                "test_date": today_str,
                "hiv_result": "negative",
                "hiv_tester": "CM",
                "hiv_type": None
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

    def test_create_registration(self):
        """Create a new registration for testing"""
        if not self.test_data:
            self.generate_test_data()
            
        success, response = self.run_test(
            "Create Admin Registration",
            "POST",
            "api/admin-register",
            200,
            data=self.test_data["admin_registration"]
        )
        
        if success:
            print(f"Registration ID: {response.get('registration_id')}")
            self.test_data["registration_id"] = response.get('registration_id')
            
        return success, response

    def test_add_hcv_test(self):
        """Test adding an HCV test to a registration"""
        if not self.test_data or "registration_id" not in self.test_data:
            success, response = self.test_create_registration()
            if not success:
                return False, {}
        
        registration_id = self.test_data["registration_id"]
        
        success, response = self.run_test(
            "Add HCV Test",
            "POST",
            f"api/admin-registration/{registration_id}/test",
            200,
            data=self.test_data["hcv_test"]
        )
        
        if success:
            print(f"HCV Test ID: {response.get('test_id')}")
            self.test_data["hcv_test_id"] = response.get('test_id')
            
        return success, response

    def test_get_tests(self):
        """Test retrieving all tests for a registration"""
        if not self.test_data or "registration_id" not in self.test_data:
            success, response = self.test_create_registration()
            if not success:
                return False, {}
                
        registration_id = self.test_data["registration_id"]
        
        success, response = self.run_test(
            "Get All Tests",
            "GET",
            f"api/admin-registration/{registration_id}/tests",
            200
        )
        
        if success:
            print(f"Found {len(response)} tests")
            
            # Verify HCV test data if we have added one
            if "hcv_test_id" in self.test_data:
                hcv_test = next((test for test in response if test.get("id") == self.test_data["hcv_test_id"]), None)
                if hcv_test:
                    print("✅ Found HCV test in response")
                    # Verify HCV test fields
                    if hcv_test.get("test_type") == "HCV":
                        print("✅ HCV test_type is correct")
                    else:
                        print(f"❌ HCV test_type is incorrect: {hcv_test.get('test_type')}")
                        
                    if hcv_test.get("hcv_result") == self.test_data["hcv_test"]["hcv_result"]:
                        print("✅ HCV result is correct")
                    else:
                        print(f"❌ HCV result is incorrect: {hcv_test.get('hcv_result')}")
                        
                    if hcv_test.get("hcv_tester") == self.test_data["hcv_test"]["hcv_tester"]:
                        print("✅ HCV tester is correct")
                    else:
                        print(f"❌ HCV tester is incorrect: {hcv_test.get('hcv_tester')}")
                else:
                    print("❌ Could not find HCV test in response")
            
            # Verify HIV test data if we have added one
            if "hiv_test_id" in self.test_data:
                hiv_test = next((test for test in response if test.get("id") == self.test_data["hiv_test_id"]), None)
                if hiv_test:
                    print("✅ Found HIV test in response")
                    # Verify HIV test fields
                    if hiv_test.get("test_type") == "HIV":
                        print("✅ HIV test_type is correct")
                    else:
                        print(f"❌ HIV test_type is incorrect: {hiv_test.get('test_type')}")
                        
                    if hiv_test.get("hiv_result") == self.test_data["hiv_test"]["hiv_result"]:
                        print("✅ HIV result is correct")
                    else:
                        print(f"❌ HIV result is incorrect: {hiv_test.get('hiv_result')}")
                        
                    if hiv_test.get("hiv_tester") == self.test_data["hiv_test"]["hiv_tester"]:
                        print("✅ HIV tester is correct")
                    else:
                        print(f"❌ HIV tester is incorrect: {hiv_test.get('hiv_tester')}")
                else:
                    print("❌ Could not find HIV test in response")
            
        return success, response

    def test_update_hcv_test(self):
        """Test updating an HCV test"""
        if not self.test_data or "hcv_test_id" not in self.test_data:
            success, response = self.test_add_hcv_test()
            if not success:
                return False, {}
                
        registration_id = self.test_data["registration_id"]
        test_id = self.test_data["hcv_test_id"]
        
        success, response = self.run_test(
            "Update HCV Test",
            "PUT",
            f"api/admin-registration/{registration_id}/test/{test_id}",
            200,
            data=self.test_data["hcv_test_update"]
        )
        
        if success:
            print(f"Updated HCV Test ID: {test_id}")
            
            # Verify the update by getting the test again
            get_success, get_response = self.run_test(
                "Get Tests After Update",
                "GET",
                f"api/admin-registration/{registration_id}/tests",
                200
            )
            
            if get_success:
                hcv_test = next((test for test in get_response if test.get("id") == test_id), None)
                if hcv_test:
                    print("✅ Found updated HCV test in response")
                    
                    # Verify updated fields
                    if hcv_test.get("hcv_result") == self.test_data["hcv_test_update"]["hcv_result"]:
                        print("✅ Updated HCV result is correct")
                    else:
                        print(f"❌ Updated HCV result is incorrect: {hcv_test.get('hcv_result')}")
                        
                    if hcv_test.get("hcv_tester") == self.test_data["hcv_test_update"]["hcv_tester"]:
                        print("✅ Updated HCV tester is correct")
                    else:
                        print(f"❌ Updated HCV tester is incorrect: {hcv_test.get('hcv_tester')}")
                else:
                    print("❌ Could not find updated HCV test in response")
            
        return success, response

    def test_add_hiv_test(self):
        """Test adding an HIV test to a registration with existing HCV test"""
        if not self.test_data or "registration_id" not in self.test_data:
            success, response = self.test_create_registration()
            if not success:
                return False, {}
                
        # Make sure we have an HCV test first
        if "hcv_test_id" not in self.test_data:
            success, response = self.test_add_hcv_test()
            if not success:
                return False, {}
        
        registration_id = self.test_data["registration_id"]
        
        success, response = self.run_test(
            "Add HIV Test",
            "POST",
            f"api/admin-registration/{registration_id}/test",
            200,
            data=self.test_data["hiv_test"]
        )
        
        if success:
            print(f"HIV Test ID: {response.get('test_id')}")
            self.test_data["hiv_test_id"] = response.get('test_id')
            
        return success, response

    def test_mixed_test_types(self):
        """Test that HCV and HIV tests work together"""
        # Make sure we have both HCV and HIV tests
        if "hcv_test_id" not in self.test_data:
            success, response = self.test_add_hcv_test()
            if not success:
                return False, {}
                
        if "hiv_test_id" not in self.test_data:
            success, response = self.test_add_hiv_test()
            if not success:
                return False, {}
        
        registration_id = self.test_data["registration_id"]
        
        success, response = self.run_test(
            "Get Mixed Test Types",
            "GET",
            f"api/admin-registration/{registration_id}/tests",
            200
        )
        
        if success:
            print(f"Found {len(response)} tests")
            
            # Verify we have both HCV and HIV tests
            hcv_tests = [test for test in response if test.get("test_type") == "HCV"]
            hiv_tests = [test for test in response if test.get("test_type") == "HIV"]
            
            if hcv_tests:
                print(f"✅ Found {len(hcv_tests)} HCV tests")
            else:
                print("❌ No HCV tests found")
                
            if hiv_tests:
                print(f"✅ Found {len(hiv_tests)} HIV tests")
            else:
                print("❌ No HIV tests found")
                
            if hcv_tests and hiv_tests:
                print("✅ Both HCV and HIV tests are working together")
                self.tests_passed += 1
            else:
                print("❌ Failed to find both HCV and HIV tests")
            
        return success, response

    def test_hcv_functionality(self):
        """Run all HCV test functionality tests"""
        print("\n" + "=" * 50)
        print("🔍 Testing HCV Test Functionality")
        print("=" * 50)
        
        # Generate test data
        self.generate_test_data()
        
        # Step 1: Create a new registration
        success, response = self.test_create_registration()
        if not success:
            print("❌ Failed to create registration")
            return False
            
        # Step 2: Add an HCV test
        success, response = self.test_add_hcv_test()
        if not success:
            print("❌ Failed to add HCV test")
            return False
            
        # Step 3: Verify HCV test data
        success, response = self.test_get_tests()
        if not success:
            print("❌ Failed to get tests")
            return False
            
        # Step 4: Update the HCV test
        success, response = self.test_update_hcv_test()
        if not success:
            print("❌ Failed to update HCV test")
            return False
            
        # Step 5: Add an HIV test to test mixed types
        success, response = self.test_add_hiv_test()
        if not success:
            print("❌ Failed to add HIV test")
            return False
            
        # Step 6: Verify mixed test types
        success, response = self.test_mixed_test_types()
        if not success:
            print("❌ Failed to verify mixed test types")
            return False
            
        print("\n✅ All HCV test functionality tests passed!")
        return True

def main():
    # Use the external backend URL for testing
    backend_url = "https://46471c8a-a981-4b23-bca9-bb5c0ba282bc.preview.emergentagent.com"
    print(f"🔗 Using external backend URL: {backend_url}")
    
    # Run the tests
    tester = HCVTestTester(backend_url)
    tester.test_api_health()
    success = tester.test_hcv_functionality()
    
    print("\n" + "=" * 50)
    print(f"📊 Tests passed: {tester.tests_passed}/{tester.tests_run}")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())