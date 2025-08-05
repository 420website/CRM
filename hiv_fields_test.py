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

class HIVFieldsTester:
    def __init__(self, base_url):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.test_data = {}
        self.registration_ids = []

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

    def generate_test_data(self, test_type="HIV", hiv_result="positive", hiv_type="Type 1"):
        """Generate random test data for registration with HIV fields"""
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
        
        self.test_data = {
            "firstName": f"Michael {random_suffix}",
            "lastName": f"Smith {random_suffix}",
            "dob": None,  # Set to None to avoid date serialization issues
            "patientConsent": "Verbal",
            "gender": "Male",
            "province": "Ontario",
            "disposition": f"Disposition Option {random.randint(1, 70)}",
            "aka": f"Mike {random_suffix}",
            "age": str(40),
            "regDate": None,  # Set to None to avoid date serialization issues
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
            "testType": test_type,
            "hivDate": "2025-07-08",
            "hivResult": hiv_result,
            "hivType": hiv_type if hiv_result == "positive" else None
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

    def test_hiv_positive_registration(self):
        """Test registration with HIV positive fields"""
        test_data = self.generate_test_data(test_type="HIV", hiv_result="positive", hiv_type="Type 1")
            
        success, response = self.run_test(
            "HIV Positive Registration",
            "POST",
            "api/admin-register",
            200,
            data=test_data
        )
        
        if success:
            registration_id = response.get('registration_id')
            print(f"Registration ID: {registration_id}")
            self.registration_ids.append(registration_id)
            
            # Now retrieve the registration to verify HIV fields were saved
            success, get_response = self.run_test(
                "Get HIV Positive Registration",
                "GET",
                f"api/admin-registration/{registration_id}",
                200
            )
            
            if success:
                # Verify HIV fields
                if get_response.get('testType') == "HIV":
                    print("✅ testType field correctly saved as 'HIV'")
                else:
                    print(f"❌ testType field incorrect: {get_response.get('testType')}")
                    success = False
                    
                if get_response.get('hivDate') == "2025-07-08":
                    print("✅ hivDate field correctly saved")
                else:
                    print(f"❌ hivDate field incorrect: {get_response.get('hivDate')}")
                    success = False
                    
                if get_response.get('hivResult') == "positive":
                    print("✅ hivResult field correctly saved as 'positive'")
                else:
                    print(f"❌ hivResult field incorrect: {get_response.get('hivResult')}")
                    success = False
                    
                if get_response.get('hivType') == "Type 1":
                    print("✅ hivType field correctly saved as 'Type 1'")
                else:
                    print(f"❌ hivType field incorrect: {get_response.get('hivType')}")
                    success = False
            
        return success, response

    def test_hiv_negative_registration(self):
        """Test registration with HIV negative fields (hivType should be empty)"""
        test_data = self.generate_test_data(test_type="HIV", hiv_result="negative", hiv_type=None)
            
        success, response = self.run_test(
            "HIV Negative Registration",
            "POST",
            "api/admin-register",
            200,
            data=test_data
        )
        
        if success:
            registration_id = response.get('registration_id')
            print(f"Registration ID: {registration_id}")
            self.registration_ids.append(registration_id)
            
            # Now retrieve the registration to verify HIV fields were saved
            success, get_response = self.run_test(
                "Get HIV Negative Registration",
                "GET",
                f"api/admin-registration/{registration_id}",
                200
            )
            
            if success:
                # Verify HIV fields
                if get_response.get('testType') == "HIV":
                    print("✅ testType field correctly saved as 'HIV'")
                else:
                    print(f"❌ testType field incorrect: {get_response.get('testType')}")
                    success = False
                    
                if get_response.get('hivDate') == "2025-07-08":
                    print("✅ hivDate field correctly saved")
                else:
                    print(f"❌ hivDate field incorrect: {get_response.get('hivDate')}")
                    success = False
                    
                if get_response.get('hivResult') == "negative":
                    print("✅ hivResult field correctly saved as 'negative'")
                else:
                    print(f"❌ hivResult field incorrect: {get_response.get('hivResult')}")
                    success = False
                    
                # For negative results, hivType should be empty or null
                if get_response.get('hivType') is None or get_response.get('hivType') == "":
                    print("✅ hivType field correctly empty for negative result")
                else:
                    print(f"❌ hivType field should be empty for negative result but got: {get_response.get('hivType')}")
                    success = False
            
        return success, response

    def test_non_hiv_registration(self):
        """Test registration with non-HIV test type (HIV fields should not be saved)"""
        test_data = self.generate_test_data(test_type="HCV", hiv_result="positive", hiv_type="Type 1")
            
        success, response = self.run_test(
            "Non-HIV Registration",
            "POST",
            "api/admin-register",
            200,
            data=test_data
        )
        
        if success:
            registration_id = response.get('registration_id')
            print(f"Registration ID: {registration_id}")
            self.registration_ids.append(registration_id)
            
            # Now retrieve the registration to verify HIV fields were not saved
            success, get_response = self.run_test(
                "Get Non-HIV Registration",
                "GET",
                f"api/admin-registration/{registration_id}",
                200
            )
            
            if success:
                # Verify test type
                if get_response.get('testType') == "HCV":
                    print("✅ testType field correctly saved as 'HCV'")
                else:
                    print(f"❌ testType field incorrect: {get_response.get('testType')}")
                    success = False
                    
                # HIV fields should be empty or have default values
                if get_response.get('hivDate') is None or get_response.get('hivDate') == "":
                    print("✅ hivDate field correctly empty for non-HIV test")
                else:
                    print(f"❌ hivDate field should be empty for non-HIV test but got: {get_response.get('hivDate')}")
                    success = False
                    
                if get_response.get('hivResult') is None or get_response.get('hivResult') == "":
                    print("✅ hivResult field correctly empty for non-HIV test")
                else:
                    print(f"❌ hivResult field should be empty for non-HIV test but got: {get_response.get('hivResult')}")
                    success = False
                    
                if get_response.get('hivType') is None or get_response.get('hivType') == "":
                    print("✅ hivType field correctly empty for non-HIV test")
                else:
                    print(f"❌ hivType field should be empty for non-HIV test but got: {get_response.get('hivType')}")
                    success = False
            
        return success, response

    def run_all_tests(self):
        """Run all HIV fields tests"""
        print("🚀 Starting HIV Fields Tests for my420.ca")
        print(f"🔗 Base URL: {self.base_url}")
        print("=" * 50)
        
        self.test_api_health()
        
        print("\n" + "=" * 50)
        print("🔍 Testing HIV Fields Functionality")
        print("=" * 50)
        
        self.test_hiv_positive_registration()
        self.test_hiv_negative_registration()
        self.test_non_hiv_registration()
        
        print("\n" + "=" * 50)
        print(f"📊 Tests passed: {self.tests_passed}/{self.tests_run}")
        
        return self.tests_passed == self.tests_run

def main():
    # Run the tests
    tester = HIVFieldsTester(backend_url)
    success = tester.run_all_tests()
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())