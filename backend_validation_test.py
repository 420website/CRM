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
backend_url = os.environ.get('REACT_APP_BACKEND_URL')

class ValidationTester:
    def __init__(self, base_url):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        
    def run_test(self, name, method, endpoint, data, expected_status, expected_error=None):
        """Run a validation test"""
        url = f"{self.base_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        
        try:
            if method == 'POST':
                response = requests.post(url, json=data, headers=headers)
            else:
                print(f"❌ Unsupported method: {method}")
                return False

            # For 422 validation errors, FastAPI returns a specific format
            if response.status_code == 422 and expected_status == 422:
                try:
                    response_json = response.json()
                    # FastAPI validation errors are in detail.loc + detail.msg format
                    if 'detail' in response_json and isinstance(response_json['detail'], list):
                        error_messages = [err.get('msg', '') for err in response_json['detail']]
                        if expected_error:
                            if any(expected_error in msg for msg in error_messages):
                                self.tests_passed += 1
                                print(f"✅ Passed - Status: 422, Error contains: '{expected_error}'")
                                return True
                            else:
                                print(f"❌ Failed - Status code correct (422), but error message doesn't contain '{expected_error}'")
                                print(f"Error messages: {error_messages}")
                                return False
                        else:
                            # If we're just checking for 422 without specific error
                            self.tests_passed += 1
                            print(f"✅ Passed - Status: 422 (Validation Error)")
                            return True
                except Exception as e:
                    print(f"❌ Failed - Could not parse validation error: {str(e)}")
                    print(f"Response: {response.text}")
                    return False
            
            # For other status codes
            elif response.status_code == expected_status:
                if expected_error and response.status_code != 200:
                    try:
                        response_json = response.json()
                        error_detail = response_json.get('detail', '')
                        if isinstance(error_detail, str) and expected_error in error_detail:
                            self.tests_passed += 1
                            print(f"✅ Passed - Status: {response.status_code}, Error contains: '{expected_error}'")
                            return True
                        else:
                            print(f"❌ Failed - Status code correct ({response.status_code}), but error message doesn't contain '{expected_error}'")
                            print(f"Response: {response_json}")
                            return False
                    except:
                        print(f"❌ Failed - Could not parse response JSON: {response.text}")
                        return False
                else:
                    self.tests_passed += 1
                    print(f"✅ Passed - Status: {response.status_code}")
                    return True
            else:
                print(f"❌ Failed - Expected status {expected_status}, got {response.status_code}")
                try:
                    print(f"Response: {response.json()}")
                except:
                    print(f"Response: {response.text}")
                return False

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False

    def generate_valid_data(self):
        """Generate valid test data"""
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
        today = date.today()
        
        return {
            "registration": {
                "full_name": f"Test User {random_suffix}",
                "date_of_birth": str(date(today.year - 30, today.month, today.day)),
                "health_card_number": ''.join(random.choices(string.digits, k=10)),
                "phone_number": ''.join(random.choices(string.digits, k=10)),
                "email": f"test.user.{random_suffix}@example.com",
                "consent_given": True
            },
            "contact": {
                "name": f"Contact User {random_suffix}",
                "email": f"contact.{random_suffix}@example.com",
                "phone": ''.join(random.choices(string.digits, k=10)),
                "message": f"This is a test message from the automated test suite. Random ID: {random_suffix}"
            }
        }

    def test_health_card_validation(self):
        """Test health card number validation"""
        data = self.generate_valid_data()["registration"]
        
        # Test 1: Invalid characters in health card
        test_data = data.copy()
        test_data["health_card_number"] = "123ABC4567"
        self.run_test(
            "Health Card Validation - Invalid Characters",
            "POST",
            "api/register",
            test_data,
            422,
            "Health card number must contain only digits"
        )
        
        # Test 2: Health card too short
        test_data = data.copy()
        test_data["health_card_number"] = "12345"
        self.run_test(
            "Health Card Validation - Too Short",
            "POST",
            "api/register",
            test_data,
            422,
            "String should have at least 10 characters"
        )
        
        # Test 3: Health card too long
        test_data = data.copy()
        test_data["health_card_number"] = "1234567890123456"
        self.run_test(
            "Health Card Validation - Too Long",
            "POST",
            "api/register",
            test_data,
            422,
            "String should have at most 12 characters"
        )
        
        # Test 4: Valid health card
        test_data = data.copy()
        test_data["health_card_number"] = "1234567890"
        self.run_test(
            "Health Card Validation - Valid",
            "POST",
            "api/register",
            test_data,
            200
        )

    def test_phone_validation(self):
        """Test phone number validation"""
        data = self.generate_valid_data()["registration"]
        
        # Test 1: Phone number too short
        test_data = data.copy()
        test_data["phone_number"] = "123456"
        test_data["email"] = None  # Remove email to test phone validation
        self.run_test(
            "Phone Validation - Too Short",
            "POST",
            "api/register",
            test_data,
            422,
            "String should have at least 10 characters"
        )
        
        # Test 2: Valid phone with formatting (should be accepted and normalized)
        test_data = data.copy()
        test_data["phone_number"] = "(123) 456-7890"
        test_data["email"] = None  # Remove email to test phone validation
        self.run_test(
            "Phone Validation - With Formatting",
            "POST",
            "api/register",
            test_data,
            200
        )

    def test_required_fields(self):
        """Test required fields validation"""
        data = self.generate_valid_data()["registration"]
        
        # Test 1: Missing full name
        test_data = data.copy()
        test_data.pop("full_name")
        self.run_test(
            "Required Fields - Missing Name",
            "POST",
            "api/register",
            test_data,
            422,
            "Field required"
        )
        
        # Test 2: Missing date of birth
        test_data = data.copy()
        test_data.pop("date_of_birth")
        self.run_test(
            "Required Fields - Missing DOB",
            "POST",
            "api/register",
            test_data,
            422,
            "Field required"
        )
        
        # Test 3: Missing consent
        test_data = data.copy()
        test_data.pop("consent_given")
        self.run_test(
            "Required Fields - Missing Consent",
            "POST",
            "api/register",
            test_data,
            422,
            "Field required"
        )

    def test_contact_form_validation(self):
        """Test contact form validation"""
        data = self.generate_valid_data()["contact"]
        
        # Test 1: Missing name
        test_data = data.copy()
        test_data.pop("name")
        self.run_test(
            "Contact Form - Missing Name",
            "POST",
            "api/contact",
            test_data,
            422,
            "Field required"
        )
        
        # Test 2: Missing email
        test_data = data.copy()
        test_data.pop("email")
        self.run_test(
            "Contact Form - Missing Email",
            "POST",
            "api/contact",
            test_data,
            422,
            "Field required"
        )
        
        # Test 3: Invalid email
        test_data = data.copy()
        test_data["email"] = "not-an-email"
        self.run_test(
            "Contact Form - Invalid Email",
            "POST",
            "api/contact",
            test_data,
            422,
            "value is not a valid email address"
        )
        
        # Test 4: Message too short
        test_data = data.copy()
        test_data["message"] = "Hi"
        self.run_test(
            "Contact Form - Message Too Short",
            "POST",
            "api/contact",
            test_data,
            422,
            "String should have at least 10 characters"
        )

    def test_contact_info_validation(self):
        """Test contact info validation (phone or email required)"""
        data = self.generate_valid_data()["registration"]
        
        # Test: Only phone provided (valid)
        test_data = data.copy()
        test_data.pop("email")
        self.run_test(
            "Contact Info - Only Phone Provided",
            "POST",
            "api/register",
            test_data,
            200
        )

    def run_all_validation_tests(self):
        """Run all validation tests"""
        print("🚀 Starting Validation Tests for my420.ca")
        print(f"🔗 Base URL: {self.base_url}")
        print("=" * 50)
        
        self.test_health_card_validation()
        self.test_phone_validation()
        self.test_required_fields()
        self.test_contact_info_validation()
        self.test_contact_form_validation()
        
        print("\n" + "=" * 50)
        print(f"📊 Validation Tests passed: {self.tests_passed}/{self.tests_run}")
        
        return self.tests_passed == self.tests_run

def main():
    if not backend_url:
        print("❌ Error: REACT_APP_BACKEND_URL not found in frontend .env file")
        return 1
    
    print(f"🔗 Using backend URL from .env: {backend_url}")
    
    # Run the validation tests
    tester = ValidationTester(backend_url)
    success = tester.run_all_validation_tests()
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())