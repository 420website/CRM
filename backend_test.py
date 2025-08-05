import requests
import unittest
import json
from datetime import datetime, date
import random
import string
import sys
from dotenv import load_dotenv

class My420APITester:
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
                "subject": f"Test Subject {random_suffix}",
                "message": f"This is a test message from the automated test suite. Random ID: {random_suffix}"
            },
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

    def test_api_health(self):
        """Test the API health endpoint"""
        return self.run_test(
            "API Health Check",
            "GET",
            "api",
            200
        )

    def test_registration(self):
        """Test user registration"""
        if not self.test_data:
            self.generate_test_data()
            
        success, response = self.run_test(
            "User Registration",
            "POST",
            "api/register",
            200,
            data=self.test_data["registration"]
        )
        
        if success:
            print(f"Registration ID: {response.get('registration_id')}")
            self.test_data["registration_id"] = response.get('registration_id')
            
        return success, response
        
    def test_phone_number_validation(self):
        """Test phone number validation in registration API"""
        if not self.test_data:
            self.generate_test_data()
        
        print("\n🔍 Testing Phone Number Validation...")
        
        # Test 1: Exactly 10 digits (should succeed)
        valid_data = self.test_data["registration"].copy()
        valid_data["phone_number"] = "1234567890"
        success, response = self.run_test(
            "Registration - Valid Phone (10 digits)",
            "POST",
            "api/register",
            200,
            data=valid_data
        )
        
        # Test 2: Less than 10 digits (should fail)
        invalid_data = self.test_data["registration"].copy()
        invalid_data["phone_number"] = "123456789"  # 9 digits
        success, response = self.run_test(
            "Registration - Invalid Phone (9 digits)",
            "POST",
            "api/register",
            422,  # Validation error status code
            data=invalid_data
        )
        
        # Test 3: More than 10 digits (should fail)
        invalid_data = self.test_data["registration"].copy()
        invalid_data["phone_number"] = "12345678901"  # 11 digits
        success, response = self.run_test(
            "Registration - Invalid Phone (11 digits)",
            "POST",
            "api/register",
            422,  # Validation error status code
            data=invalid_data
        )
        
        # Test 4: Formatted phone number with exactly 10 digits (should succeed)
        valid_data = self.test_data["registration"].copy()
        valid_data["phone_number"] = "(123) 456-7890"  # 10 digits with formatting
        success, response = self.run_test(
            "Registration - Valid Formatted Phone",
            "POST",
            "api/register",
            200,
            data=valid_data
        )
        
        # Test 5: Formatted phone number with less than 10 digits (should fail)
        invalid_data = self.test_data["registration"].copy()
        invalid_data["phone_number"] = "(123) 456-789"  # 9 digits with formatting
        success, response = self.run_test(
            "Registration - Invalid Formatted Phone (9 digits)",
            "POST",
            "api/register",
            422,  # Validation error status code
            data=invalid_data
        )
        
        # Test 6: Formatted phone number with more than 10 digits (should fail)
        invalid_data = self.test_data["registration"].copy()
        invalid_data["phone_number"] = "(123) 456-78901"  # 11 digits with formatting
        success, response = self.run_test(
            "Registration - Invalid Formatted Phone (11 digits)",
            "POST",
            "api/register",
            422,  # Validation error status code
            data=invalid_data
        )
        
        # Test 7: Phone with spaces (should succeed if 10 digits)
        valid_data = self.test_data["registration"].copy()
        valid_data["phone_number"] = "123 456 7890"  # 10 digits with spaces
        success, response = self.run_test(
            "Registration - Valid Phone with Spaces",
            "POST",
            "api/register",
            200,
            data=valid_data
        )
        
        # Test 8: Phone with dashes (should succeed if 10 digits)
        valid_data = self.test_data["registration"].copy()
        valid_data["phone_number"] = "123-456-7890"  # 10 digits with dashes
        success, response = self.run_test(
            "Registration - Valid Phone with Dashes",
            "POST",
            "api/register",
            200,
            data=valid_data
        )
        
        return True, {"message": "Phone number validation tests completed"}

    def test_duplicate_registration(self):
        """Test duplicate registration - note: backend currently allows duplicates"""
        if not self.test_data:
            self.generate_test_data()
            
        # First registration should succeed
        success, _ = self.test_registration()
        if not success:
            print("❌ Could not create initial registration for duplicate test")
            return False, {}
            
        # Second registration with same data should also succeed (no duplicate prevention)
        return self.run_test(
            "Duplicate Registration",
            "POST",
            "api/register",
            200,
            data=self.test_data["registration"]
        )

    def test_contact_form(self):
        """Test contact form submission"""
        if not self.test_data:
            self.generate_test_data()
            
        success, response = self.run_test(
            "Contact Form Submission",
            "POST",
            "api/contact",
            200,
            data=self.test_data["contact"]
        )
        
        if success:
            print(f"Message ID: {response.get('message_id')}")
            self.test_data["message_id"] = response.get('message_id')
            
        return success, response
    
    def test_contact_form_logger_fix(self):
        """Test contact form to verify logger error has been fixed"""
        if not self.test_data:
            self.generate_test_data()
            
        # Create a contact message with special characters to potentially trigger logger issues
        special_data = self.test_data["contact"].copy()
        special_data["message"] = """This message contains special characters that might trigger logger issues:
        * Quotes: "double" and 'single'
        * Brackets: [square], {curly}, (parentheses)
        * Special chars: !@#$%^&*()_+-=[]{}|;':",./<>?`~
        * Newlines and tabs: \n\t
        * Emoji: 😀🔥👍
        """
        
        success, response = self.run_test(
            "Contact Form - Special Characters (Logger Fix Test)",
            "POST",
            "api/contact",
            200,
            data=special_data
        )
        
        if success:
            print("✅ Logger error fix verified - contact form accepts special characters without errors")
            print(f"Message ID: {response.get('message_id')}")
            
        return success, response
        
    def test_contact_form_validation(self):
        """Test contact form validation for required fields"""
        if not self.test_data:
            self.generate_test_data()
        
        # Test missing name
        invalid_data = self.test_data["contact"].copy()
        invalid_data.pop("name")
        success, response = self.run_test(
            "Contact Form - Missing Name",
            "POST",
            "api/contact",
            422,  # Validation error status code
            data=invalid_data
        )
        
        # Test missing email
        invalid_data = self.test_data["contact"].copy()
        invalid_data.pop("email")
        success, response = self.run_test(
            "Contact Form - Missing Email",
            "POST",
            "api/contact",
            422,  # Validation error status code
            data=invalid_data
        )
        
        # Test missing subject
        invalid_data = self.test_data["contact"].copy()
        invalid_data.pop("subject")
        success, response = self.run_test(
            "Contact Form - Missing Subject",
            "POST",
            "api/contact",
            422,  # Validation error status code
            data=invalid_data
        )
        
        # Test missing message
        invalid_data = self.test_data["contact"].copy()
        invalid_data.pop("message")
        success, response = self.run_test(
            "Contact Form - Missing Message",
            "POST",
            "api/contact",
            422,  # Validation error status code
            data=invalid_data
        )
        
        # Test invalid email format
        invalid_data = self.test_data["contact"].copy()
        invalid_data["email"] = "invalid-email"
        success, response = self.run_test(
            "Contact Form - Invalid Email Format",
            "POST",
            "api/contact",
            422,  # Validation error status code
            data=invalid_data
        )
        
        # Test message too short
        invalid_data = self.test_data["contact"].copy()
        invalid_data["message"] = "short"
        success, response = self.run_test(
            "Contact Form - Message Too Short",
            "POST",
            "api/contact",
            422,  # Validation error status code
            data=invalid_data
        )
        
        return True, {"message": "Validation tests completed"}

    def test_get_registrations(self):
        """Test getting all registrations (admin endpoint)"""
        return self.run_test(
            "Get All Registrations",
            "GET",
            "api/registrations",
            200
        )

    def test_get_contact_messages(self):
        """Test getting all contact messages (admin endpoint)"""
        success, response = self.run_test(
            "Get All Contact Messages",
            "GET",
            "api/contact-messages",
            200
        )
        
        if success:
            # Verify that we have at least one contact message in the database
            if isinstance(response, list):
                print(f"✅ Found {len(response)} contact messages in the database")
                if len(response) > 0:
                    print(f"✅ Most recent contact message: {response[0]['name']} - {response[0]['subject']}")
            else:
                print("❌ Expected a list of contact messages but got a different response type")
                
        return success, response
        
    def test_admin_registration(self):
        """Test admin registration with all 28 fields"""
        if not self.test_data:
            self.generate_test_data()
            
        success, response = self.run_test(
            "Admin Registration - All Fields",
            "POST",
            "api/admin-register",
            200,
            data=self.test_data["admin_registration"]
        )
        
        if success:
            print(f"Admin Registration ID: {response.get('registration_id')}")
            self.test_data["admin_registration_id"] = response.get('registration_id')
            
        return success, response
        
    def test_admin_registration_required_fields(self):
        """Test admin registration with only required fields"""
        if not self.test_data:
            self.generate_test_data()
        
        # Create minimal data with only required fields
        minimal_data = {
            "firstName": self.test_data["admin_registration"]["firstName"],
            "lastName": self.test_data["admin_registration"]["lastName"],
            "patientConsent": self.test_data["admin_registration"]["patientConsent"]
        }
        
        success, response = self.run_test(
            "Admin Registration - Required Fields Only",
            "POST",
            "api/admin-register",
            200,
            data=minimal_data
        )
        
        if success:
            print(f"Admin Registration ID (minimal data): {response.get('registration_id')}")
            
        return success, response
        
    def test_admin_registration_validation(self):
        """Test admin registration validation for required fields"""
        if not self.test_data:
            self.generate_test_data()
        
        # Test missing firstName (required field)
        invalid_data = self.test_data["admin_registration"].copy()
        invalid_data.pop("firstName")
        success, response = self.run_test(
            "Admin Registration - Missing First Name",
            "POST",
            "api/admin-register",
            422,  # Validation error status code
            data=invalid_data
        )
        
        # Test missing lastName (required field)
        invalid_data = self.test_data["admin_registration"].copy()
        invalid_data.pop("lastName")
        success, response = self.run_test(
            "Admin Registration - Missing Last Name",
            "POST",
            "api/admin-register",
            422,  # Validation error status code
            data=invalid_data
        )
        
        # Test missing patientConsent (required field)
        invalid_data = self.test_data["admin_registration"].copy()
        invalid_data.pop("patientConsent")
        success, response = self.run_test(
            "Admin Registration - Missing Patient Consent",
            "POST",
            "api/admin-register",
            422,  # Validation error status code
            data=invalid_data
        )
        
        # Test invalid email format
        invalid_data = self.test_data["admin_registration"].copy()
        invalid_data["email"] = "invalid-email"
        success, response = self.run_test(
            "Admin Registration - Invalid Email Format",
            "POST",
            "api/admin-register",
            422,  # Validation error status code
            data=invalid_data
        )
        
        # Test firstName too short
        invalid_data = self.test_data["admin_registration"].copy()
        invalid_data["firstName"] = ""
        success, response = self.run_test(
            "Admin Registration - First Name Too Short",
            "POST",
            "api/admin-register",
            422,  # Validation error status code
            data=invalid_data
        )
        
        # Test lastName too short
        invalid_data = self.test_data["admin_registration"].copy()
        invalid_data["lastName"] = ""
        success, response = self.run_test(
            "Admin Registration - Last Name Too Short",
            "POST",
            "api/admin-register",
            422,  # Validation error status code
            data=invalid_data
        )
        
        return True, {"message": "Admin registration validation tests completed"}
        
    def test_admin_registration_edge_cases(self):
        """Test admin registration with edge cases"""
        if not self.test_data:
            self.generate_test_data()
        
        # Test with very long values for optional fields
        long_data = self.test_data["admin_registration"].copy()
        long_data["specialAttention"] = "A" * 1000  # Very long special attention notes
        success, response = self.run_test(
            "Admin Registration - Long Special Attention",
            "POST",
            "api/admin-register",
            200,
            data=long_data
        )
        
        # Test with different consent types
        consent_data = self.test_data["admin_registration"].copy()
        consent_data["patientConsent"] = "Written"
        success, response = self.run_test(
            "Admin Registration - Written Consent",
            "POST",
            "api/admin-register",
            200,
            data=consent_data
        )
        
        # Test with different language
        language_data = self.test_data["admin_registration"].copy()
        language_data["language"] = "French"
        success, response = self.run_test(
            "Admin Registration - French Language",
            "POST",
            "api/admin-register",
            200,
            data=language_data
        )
        
        # Test with all boolean fields set to true
        boolean_data = self.test_data["admin_registration"].copy()
        boolean_data["leaveMessage"] = True
        boolean_data["voicemail"] = True
        boolean_data["text"] = True
        success, response = self.run_test(
            "Admin Registration - All Contact Preferences True",
            "POST",
            "api/admin-register",
            200,
            data=boolean_data
        )
        
        # Test with all boolean fields set to false
        boolean_data = self.test_data["admin_registration"].copy()
        boolean_data["leaveMessage"] = False
        boolean_data["voicemail"] = False
        boolean_data["text"] = False
        success, response = self.run_test(
            "Admin Registration - All Contact Preferences False",
            "POST",
            "api/admin-register",
            200,
            data=boolean_data
        )
        
        return True, {"message": "Admin registration edge case tests completed"}
        
    def test_admin_registration_default_date(self):
        """Test admin registration with default registration date (current date)"""
        if not self.test_data:
            self.generate_test_data()
        
        # Create data without regDate field to test default value
        data_without_date = self.test_data["admin_registration"].copy()
        if "regDate" in data_without_date:
            data_without_date.pop("regDate")
        
        success, response = self.run_test(
            "Admin Registration - Default Registration Date",
            "POST",
            "api/admin-register",
            200,
            data=data_without_date
        )
        
        if success:
            print(f"Admin Registration ID (default date): {response.get('registration_id')}")
            self.test_data["admin_registration_default_date_id"] = response.get('registration_id')
            
            # Verify in MongoDB that the registration date was set to current date
            try:
                from pymongo import MongoClient
                import os
                from dotenv import load_dotenv
                from datetime import datetime, date
                
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
                registration = collection.find_one({"id": self.test_data["admin_registration_default_date_id"]})
                
                if registration:
                    # Check if regDate is present and is today's date
                    if "regDate" in registration:
                        reg_date = registration["regDate"]
                        today = date.today()
                        
                        # Handle different date formats
                        if isinstance(reg_date, str):
                            # If it's a string, try to parse it
                            try:
                                reg_date = datetime.strptime(reg_date, "%Y-%m-%d").date()
                            except:
                                print(f"❌ Registration date format unexpected: {reg_date}")
                                return success, response
                        elif isinstance(reg_date, datetime):
                            reg_date = reg_date.date()
                        
                        if reg_date == today:
                            print(f"✅ Default registration date verified: {reg_date} matches today's date {today}")
                            self.tests_passed += 1
                        else:
                            print(f"❌ Registration date {reg_date} does not match today's date {today}")
                    else:
                        print("❌ Registration date not found in stored data")
                else:
                    print(f"❌ Could not find registration with ID {self.test_data['admin_registration_default_date_id']}")
            except Exception as e:
                print(f"❌ Error verifying registration date in MongoDB: {str(e)}")
        
        return success, response
        
    def test_admin_registration_default_province(self):
        """Test admin registration with default province (Ontario)"""
        if not self.test_data:
            self.generate_test_data()
        
        # Create data without province field to test default value
        data_without_province = self.test_data["admin_registration"].copy()
        if "province" in data_without_province:
            data_without_province.pop("province")
        
        success, response = self.run_test(
            "Admin Registration - Default Province",
            "POST",
            "api/admin-register",
            200,
            data=data_without_province
        )
        
        if success:
            print(f"Admin Registration ID (default province): {response.get('registration_id')}")
            self.test_data["admin_registration_default_province_id"] = response.get('registration_id')
            
            # Verify in MongoDB that the province was set to "Ontario"
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
                registration = collection.find_one({"id": self.test_data["admin_registration_default_province_id"]})
                
                if registration:
                    # Check if province is present and is "Ontario"
                    if "province" in registration:
                        province = registration["province"]
                        if province == "Ontario":
                            print(f"✅ Default province verified: {province}")
                            self.tests_passed += 1
                        else:
                            print(f"❌ Province {province} does not match expected default 'Ontario'")
                    else:
                        print("❌ Province not found in stored data")
                else:
                    print(f"❌ Could not find registration with ID {self.test_data['admin_registration_default_province_id']}")
            except Exception as e:
                print(f"❌ Error verifying province in MongoDB: {str(e)}")
        
        return success, response
        
    def test_admin_registration_both_defaults(self):
        """Test admin registration with both default values (registration date and province)"""
        if not self.test_data:
            self.generate_test_data()
        
        # Create data without regDate and province fields to test both defaults
        data_without_defaults = self.test_data["admin_registration"].copy()
        if "regDate" in data_without_defaults:
            data_without_defaults.pop("regDate")
        if "province" in data_without_defaults:
            data_without_defaults.pop("province")
        
        success, response = self.run_test(
            "Admin Registration - Both Default Values",
            "POST",
            "api/admin-register",
            200,
            data=data_without_defaults
        )
        
        if success:
            print(f"Admin Registration ID (both defaults): {response.get('registration_id')}")
            self.test_data["admin_registration_both_defaults_id"] = response.get('registration_id')
            
            # Verify in MongoDB that both defaults were set correctly
            try:
                from pymongo import MongoClient
                import os
                from dotenv import load_dotenv
                from datetime import datetime, date
                
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
                registration = collection.find_one({"id": self.test_data["admin_registration_both_defaults_id"]})
                
                if registration:
                    defaults_correct = True
                    
                    # Check if regDate is present and is today's date
                    if "regDate" in registration:
                        reg_date = registration["regDate"]
                        today = date.today()
                        
                        # Handle different date formats
                        if isinstance(reg_date, str):
                            # If it's a string, try to parse it
                            try:
                                reg_date = datetime.strptime(reg_date, "%Y-%m-%d").date()
                            except:
                                print(f"❌ Registration date format unexpected: {reg_date}")
                                defaults_correct = False
                        elif isinstance(reg_date, datetime):
                            reg_date = reg_date.date()
                        
                        if reg_date == today:
                            print(f"✅ Default registration date verified: {reg_date} matches today's date {today}")
                        else:
                            print(f"❌ Registration date {reg_date} does not match today's date {today}")
                            defaults_correct = False
                    else:
                        print("❌ Registration date not found in stored data")
                        defaults_correct = False
                    
                    # Check if province is present and is "Ontario"
                    if "province" in registration:
                        province = registration["province"]
                        if province == "Ontario":
                            print(f"✅ Default province verified: {province}")
                        else:
                            print(f"❌ Province {province} does not match expected default 'Ontario'")
                            defaults_correct = False
                    else:
                        print("❌ Province not found in stored data")
                        defaults_correct = False
                    
                    if defaults_correct:
                        self.tests_passed += 1
                else:
                    print(f"❌ Could not find registration with ID {self.test_data['admin_registration_both_defaults_id']}")
            except Exception as e:
                print(f"❌ Error verifying defaults in MongoDB: {str(e)}")
        
        return success, response
        
    def test_get_admin_registrations(self):
        """Test getting admin registrations from MongoDB"""
        # First, create a new admin registration to ensure we have data
        self.test_admin_registration()
        
        # Now check if we can retrieve admin registrations from MongoDB
        # This is a custom test since there's no API endpoint for this yet
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
                return False, {}
                
            # Connect to MongoDB
            client = MongoClient(mongo_url)
            db = client[db_name]
            collection = db["admin_registrations"]
            
            # Find admin registrations
            admin_registrations = list(collection.find().limit(10))
            
            if admin_registrations:
                print(f"✅ Found {len(admin_registrations)} admin registrations in MongoDB")
                print(f"✅ Most recent admin registration: {admin_registrations[-1].get('firstName', 'N/A')} {admin_registrations[-1].get('lastName', 'N/A')}")
                
                # Verify all 28 fields are present in the stored data
                latest_registration = admin_registrations[-1]
                expected_fields = [
                    "firstName", "lastName", "dob", "patientConsent", "gender", "province", 
                    "fileNumber", "disposition", "aka", "age", "regDate", "healthCard", 
                    "referralSite", "address", "unitNumber", "city", "postalCode", 
                    "phone1", "phone2", "ext1", "ext2", "leaveMessage", "voicemail", 
                    "text", "preferredTime", "email", "language", "specialAttention"
                ]
                
                # Note: photo field is optional, so we don't check for it here
                
                missing_fields = [field for field in expected_fields if field not in latest_registration]
                
                if missing_fields:
                    print(f"❌ Missing fields in stored admin registration: {', '.join(missing_fields)}")
                    return False, {"missing_fields": missing_fields}
                else:
                    print("✅ All 28 expected fields are present in the stored admin registration")
                    # Check if photo field is present (optional)
                    if "photo" in latest_registration:
                        print("✅ Photo field is also present in the stored admin registration")
                    self.tests_passed += 1
                    return True, {"admin_registrations": len(admin_registrations)}
            else:
                print("❌ No admin registrations found in MongoDB")
                return False, {}
                
        except Exception as e:
            print(f"❌ Error checking MongoDB for admin registrations: {str(e)}")
            return False, {"error": str(e)}
    def test_admin_registration_with_photo(self):
        """Test admin registration with photo data"""
        if not self.test_data:
            self.generate_test_data()
            
        # Make sure the test data includes a photo
        self.test_data["admin_registration"]["photo"] = self.generate_sample_base64_image()
        
        success, response = self.run_test(
            "Admin Registration - With Photo",
            "POST",
            "api/admin-register",
            200,
            data=self.test_data["admin_registration"]
        )
        
        if success:
            print(f"Admin Registration ID (with photo): {response.get('registration_id')}")
            self.test_data["admin_registration_with_photo_id"] = response.get('registration_id')
            
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
                registration = collection.find_one({"id": self.test_data["admin_registration_with_photo_id"]})
                
                if registration:
                    # Check if photo is present and not empty
                    if "photo" in registration and registration["photo"]:
                        print(f"✅ Photo data verified in MongoDB (length: {len(registration['photo'])})")
                        self.tests_passed += 1
                    else:
                        print("❌ Photo data not found or empty in stored data")
                else:
                    print(f"❌ Could not find registration with ID {self.test_data['admin_registration_with_photo_id']}")
            except Exception as e:
                print(f"❌ Error verifying photo in MongoDB: {str(e)}")
        
        return success, response
        
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
        
    def test_admin_registration_photo_field(self):
        """Test that the photo field is properly included in the admin registration model"""
        # First, create a new admin registration with photo
        self.test_admin_registration_with_photo()
        
        # Now check if the photo field is included in the MongoDB document
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
                return False, {}
                
            # Connect to MongoDB
            client = MongoClient(mongo_url)
            db = client[db_name]
            collection = db["admin_registrations"]
            
            # Find admin registrations with photos
            admin_registrations_with_photos = list(collection.find({"photo": {"$ne": None}}))
            
            if admin_registrations_with_photos:
                print(f"✅ Found {len(admin_registrations_with_photos)} admin registrations with photos in MongoDB")
                
                # Verify photo field is present in the stored data
                latest_registration = admin_registrations_with_photos[-1]
                if "photo" in latest_registration and latest_registration["photo"]:
                    print("✅ Photo field is present and not empty in the stored admin registration")
                    self.tests_passed += 1
                    return True, {"admin_registrations_with_photos": len(admin_registrations_with_photos)}
                else:
                    print("❌ Photo field is missing or empty in the stored admin registration")
                    return False, {}
            else:
                print("❌ No admin registrations with photos found in MongoDB")
                return False, {}
                
        except Exception as e:
            print(f"❌ Error checking MongoDB for admin registrations with photos: {str(e)}")
            return False, {"error": str(e)}

    def test_dispensing_crud(self):
        """Test Dispensing CRUD operations"""
        if not hasattr(self, 'test_data') or not self.test_data:
            self.generate_test_data()
            
        # First, create a test registration if we don't have one
        if not hasattr(self, 'test_data') or 'admin_registration_id' not in self.test_data:
            success, response = self.test_admin_registration()
            if not success:
                print("❌ Could not create admin registration for dispensing tests")
                return False, {}
                
        registration_id = self.test_data['admin_registration_id']
        
        print("\n" + "=" * 50)
        print("🔍 Testing Dispensing CRUD Operations")
        print("=" * 50)
        
        # 1. Create a dispensing record
        dispensing_data = {
            "medication": "Ecplusa",
            "rx": "RX12345",
            "quantity": "28",
            "lot": "LOT123",
            "product_type": "Commercial",
            "expiry_date": "2025-12-31"
        }
        
        success, response = self.run_test(
            "Create Dispensing Record",
            "POST",
            f"api/admin-registration/{registration_id}/dispensing",
            200,
            data=dispensing_data
        )
        
        if success and 'dispensing_id' in response:
            dispensing_id = response['dispensing_id']
            print(f"✅ Created dispensing record with ID: {dispensing_id}")
            self.test_data['dispensing_id'] = dispensing_id
        else:
            print("❌ Failed to create dispensing record")
            return False, {}
            
        # 2. Get all dispensing records
        success, response = self.run_test(
            "Get Dispensing Records",
            "GET",
            f"api/admin-registration/{registration_id}/dispensing",
            200
        )
        
        if success and 'dispensing' in response:
            dispensing_records = response['dispensing']
            print(f"✅ Retrieved {len(dispensing_records)} dispensing records")
            
            # Verify the record we just created is in the list
            found = False
            for record in dispensing_records:
                if record['id'] == dispensing_id:
                    found = True
                    # Verify the data was saved correctly
                    for key, value in dispensing_data.items():
                        if record[key] != value:
                            print(f"❌ Field '{key}' mismatch: expected '{value}', got '{record[key]}'")
                            return False, {}
                    print("✅ All dispensing record fields match the data we sent")
                    break
                    
            if not found:
                print(f"❌ Could not find dispensing record with ID {dispensing_id} in the response")
                return False, {}
        else:
            print("❌ Failed to retrieve dispensing records")
            return False, {}
            
        # 3. Update the dispensing record
        update_data = {
            "medication": "Maviret",
            "rx": "RX67890",
            "quantity": "56",
            "lot": "LOT456",
            "product_type": "Compassionate",
            "expiry_date": "2026-06-30"
        }
        
        success, response = self.run_test(
            "Update Dispensing Record",
            "PUT",
            f"api/admin-registration/{registration_id}/dispensing/{dispensing_id}",
            200,
            data=update_data
        )
        
        if success:
            print(f"✅ Updated dispensing record with ID: {dispensing_id}")
            
            # Verify the update by getting the record again
            success, response = self.run_test(
                "Verify Dispensing Update",
                "GET",
                f"api/admin-registration/{registration_id}/dispensing",
                200
            )
            
            if success and 'dispensing' in response:
                dispensing_records = response['dispensing']
                found = False
                for record in dispensing_records:
                    if record['id'] == dispensing_id:
                        found = True
                        # Verify the data was updated correctly
                        for key, value in update_data.items():
                            if record[key] != value:
                                print(f"❌ Updated field '{key}' mismatch: expected '{value}', got '{record[key]}'")
                                return False, {}
                        print("✅ All updated dispensing record fields match the data we sent")
                        break
                        
                if not found:
                    print(f"❌ Could not find updated dispensing record with ID {dispensing_id} in the response")
                    return False, {}
            else:
                print("❌ Failed to retrieve updated dispensing records")
                return False, {}
        else:
            print("❌ Failed to update dispensing record")
            return False, {}
            
        # 4. Delete the dispensing record
        success, response = self.run_test(
            "Delete Dispensing Record",
            "DELETE",
            f"api/admin-registration/{registration_id}/dispensing/{dispensing_id}",
            200
        )
        
        if success:
            print(f"✅ Deleted dispensing record with ID: {dispensing_id}")
            
            # Verify the deletion by getting all records again
            success, response = self.run_test(
                "Verify Dispensing Deletion",
                "GET",
                f"api/admin-registration/{registration_id}/dispensing",
                200
            )
            
            if success and 'dispensing' in response:
                dispensing_records = response['dispensing']
                for record in dispensing_records:
                    if record['id'] == dispensing_id:
                        print(f"❌ Dispensing record with ID {dispensing_id} was not deleted")
                        return False, {}
                print("✅ Dispensing record was successfully deleted")
            else:
                print("❌ Failed to verify dispensing record deletion")
                return False, {}
        else:
            print("❌ Failed to delete dispensing record")
            return False, {}
            
        return True, {"message": "Dispensing CRUD tests completed successfully"}
        
    def test_dispensing_validation(self):
        """Test validation for dispensing records"""
        if not hasattr(self, 'test_data') or not self.test_data:
            self.generate_test_data()
            
        # First, create a test registration if we don't have one
        if not hasattr(self, 'test_data') or 'admin_registration_id' not in self.test_data:
            success, response = self.test_admin_registration()
            if not success:
                print("❌ Could not create admin registration for dispensing validation tests")
                return False, {}
                
        registration_id = self.test_data['admin_registration_id']
        
        print("\n" + "=" * 50)
        print("🔍 Testing Dispensing Validation")
        print("=" * 50)
        
        # Test 1: Missing required field (medication)
        invalid_data = {
            "rx": "RX12345",
            "quantity": "28",
            "lot": "LOT123",
            "product_type": "Commercial",
            "expiry_date": "2025-12-31"
        }
        
        success, response = self.run_test(
            "Dispensing - Missing Required Field (medication)",
            "POST",
            f"api/admin-registration/{registration_id}/dispensing",
            422,  # Validation error status code
            data=invalid_data
        )
        
        # Test 2: Invalid registration ID
        invalid_reg_id = "nonexistent-id"
        valid_data = {
            "medication": "Ecplusa",
            "rx": "RX12345",
            "quantity": "28",
            "lot": "LOT123",
            "product_type": "Commercial",
            "expiry_date": "2025-12-31"
        }
        
        success, response = self.run_test(
            "Dispensing - Invalid Registration ID",
            "POST",
            f"api/admin-registration/{invalid_reg_id}/dispensing",
            404,  # Not found status code
            data=valid_data
        )
        
        # Test 3: Test default values
        minimal_data = {
            "medication": "Ecplusa"
        }
        
        success, response = self.run_test(
            "Dispensing - Default Values",
            "POST",
            f"api/admin-registration/{registration_id}/dispensing",
            200,
            data=minimal_data
        )
        
        if success and 'dispensing_id' in response:
            dispensing_id = response['dispensing_id']
            print(f"✅ Created dispensing record with minimal data, ID: {dispensing_id}")
            
            # Verify default values by getting the record
            success, response = self.run_test(
                "Verify Dispensing Default Values",
                "GET",
                f"api/admin-registration/{registration_id}/dispensing",
                200
            )
            
            if success and 'dispensing' in response:
                dispensing_records = response['dispensing']
                found = False
                for record in dispensing_records:
                    if record['id'] == dispensing_id:
                        found = True
                        # Check default values
                        if record.get('quantity') == "28":
                            print("✅ Default quantity value '28' was correctly applied")
                        else:
                            print(f"❌ Default quantity value incorrect: expected '28', got '{record.get('quantity')}'")
                        
                        if record.get('product_type') == "Commercial":
                            print("✅ Default product_type value 'Commercial' was correctly applied")
                        else:
                            print(f"❌ Default product_type value incorrect: expected 'Commercial', got '{record.get('product_type')}'")
                        break
                        
                if not found:
                    print(f"❌ Could not find dispensing record with ID {dispensing_id} in the response")
            else:
                print("❌ Failed to retrieve dispensing records for default value verification")
        else:
            print("❌ Failed to create dispensing record with minimal data")
            
        return True, {"message": "Dispensing validation tests completed"}
        
    def run_all_tests(self):
        """Run all API tests"""
        print("🚀 Starting API Tests for my420.ca")
        print(f"🔗 Base URL: {self.base_url}")
        print("=" * 50)
        
        self.test_api_health()
        self.test_registration()
        self.test_phone_number_validation()  # Added phone number validation tests
        self.test_duplicate_registration()
        self.test_contact_form()
        self.test_contact_form_logger_fix()
        self.test_contact_form_validation()
        self.test_get_registrations()
        self.test_get_contact_messages()
        
        # Admin registration tests
        print("\n" + "=" * 50)
        print("🔍 Testing Admin Registration System")
        print("=" * 50)
        self.test_admin_registration()
        self.test_admin_registration_required_fields()
        self.test_admin_registration_validation()
        self.test_admin_registration_edge_cases()
        
        # Test new default values
        print("\n" + "=" * 50)
        print("🔍 Testing Admin Registration Default Values")
        print("=" * 50)
        self.test_admin_registration_default_date()
        self.test_admin_registration_default_province()
        self.test_admin_registration_both_defaults()
        
        # Test photo upload functionality
        print("\n" + "=" * 50)
        print("🔍 Testing Admin Registration Photo Upload")
        print("=" * 50)
        self.test_admin_registration_with_photo()
        self.test_admin_registration_without_photo()
        self.test_admin_registration_with_large_photo()
        self.test_admin_registration_photo_field()
        
        self.test_get_admin_registrations()  # Test MongoDB storage
        
        # Test dispensing functionality
        print("\n" + "=" * 50)
        print("🔍 Testing Dispensing Functionality")
        print("=" * 50)
        self.test_dispensing_crud()
        self.test_dispensing_validation()
        
        print("\n" + "=" * 50)
        print(f"📊 Tests passed: {self.tests_passed}/{self.tests_run}")
        
        return self.tests_passed == self.tests_run


def test_admin_activities(base_url):
    """Test the admin-activities endpoint"""
    print("\n" + "=" * 50)
    print("🔍 Testing Admin Activities Endpoint")
    print("=" * 50)
    
    # Import and run the admin activities test
    import admin_activities_test
    tester = admin_activities_test.AdminActivitiesTest(base_url)
    return tester.run_all_tests()

class DatabaseCleanupTester:
    def __init__(self, base_url):
        self.base_url = base_url
        self.headers = {'Content-Type': 'application/json'}
        
    def get_current_counts(self):
        """Get current counts of templates and dispositions"""
        print("\n🔍 Getting current database counts...")
        
        # Get clinical templates
        try:
            response = requests.get(f"{self.base_url}/api/clinical-templates", headers=self.headers)
            clinical_templates = response.json() if response.status_code == 200 else []
            print(f"📊 Clinical Templates: {len(clinical_templates)}")
        except Exception as e:
            print(f"❌ Error getting clinical templates: {e}")
            clinical_templates = []
            
        # Get notes templates
        try:
            response = requests.get(f"{self.base_url}/api/notes-templates", headers=self.headers)
            notes_templates = response.json() if response.status_code == 200 else []
            print(f"📊 Notes Templates: {len(notes_templates)}")
        except Exception as e:
            print(f"❌ Error getting notes templates: {e}")
            notes_templates = []
            
        # Get dispositions
        try:
            response = requests.get(f"{self.base_url}/api/dispositions", headers=self.headers)
            dispositions = response.json() if response.status_code == 200 else []
            print(f"📊 Dispositions: {len(dispositions)}")
        except Exception as e:
            print(f"❌ Error getting dispositions: {e}")
            dispositions = []
            
        return clinical_templates, notes_templates, dispositions
        
    def backup_data(self):
        """Create backup of current data"""
        print("\n💾 Creating backup of current data...")
        
        clinical_templates, notes_templates, dispositions = self.get_current_counts()
        
        backup_data = {
            "timestamp": datetime.now().isoformat(),
            "clinical_templates": clinical_templates,
            "notes_templates": notes_templates,
            "dispositions": dispositions
        }
        
        # Save backup to file
        backup_file = f"/app/database_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        try:
            with open(backup_file, 'w') as f:
                json.dump(backup_data, f, indent=2)
            print(f"✅ Backup saved to: {backup_file}")
            return True
        except Exception as e:
            print(f"❌ Error creating backup: {e}")
            return False
            
    def delete_all_clinical_templates(self):
        """Delete all clinical templates (all are test entries)"""
        print("\n🗑️ Deleting ALL clinical templates...")
        
        # Get all clinical templates
        try:
            response = requests.get(f"{self.base_url}/api/clinical-templates", headers=self.headers)
            if response.status_code != 200:
                print(f"❌ Error getting clinical templates: {response.status_code}")
                return False
                
            templates = response.json()
            print(f"📋 Found {len(templates)} clinical templates to delete")
            
            deleted_count = 0
            for template in templates:
                template_id = template.get('id')
                template_name = template.get('name', 'Unknown')
                
                try:
                    delete_response = requests.delete(
                        f"{self.base_url}/api/clinical-templates/{template_id}",
                        headers=self.headers
                    )
                    
                    if delete_response.status_code == 200:
                        print(f"✅ Deleted clinical template: {template_name} (ID: {template_id})")
                        deleted_count += 1
                    else:
                        print(f"❌ Failed to delete clinical template {template_name}: {delete_response.status_code}")
                        
                except Exception as e:
                    print(f"❌ Error deleting clinical template {template_name}: {e}")
                    
            print(f"🎯 Deleted {deleted_count}/{len(templates)} clinical templates")
            return deleted_count == len(templates)
            
        except Exception as e:
            print(f"❌ Error in delete_all_clinical_templates: {e}")
            return False
            
    def delete_all_notes_templates(self):
        """Delete all notes templates (all are test entries)"""
        print("\n🗑️ Deleting ALL notes templates...")
        
        # Get all notes templates
        try:
            response = requests.get(f"{self.base_url}/api/notes-templates", headers=self.headers)
            if response.status_code != 200:
                print(f"❌ Error getting notes templates: {response.status_code}")
                return False
                
            templates = response.json()
            print(f"📋 Found {len(templates)} notes templates to delete")
            
            deleted_count = 0
            for template in templates:
                template_id = template.get('id')
                template_name = template.get('name', 'Unknown')
                
                try:
                    delete_response = requests.delete(
                        f"{self.base_url}/api/notes-templates/{template_id}",
                        headers=self.headers
                    )
                    
                    if delete_response.status_code == 200:
                        print(f"✅ Deleted notes template: {template_name} (ID: {template_id})")
                        deleted_count += 1
                    else:
                        print(f"❌ Failed to delete notes template {template_name}: {delete_response.status_code}")
                        
                except Exception as e:
                    print(f"❌ Error deleting notes template {template_name}: {e}")
                    
            print(f"🎯 Deleted {deleted_count}/{len(templates)} notes templates")
            return deleted_count == len(templates)
            
        except Exception as e:
            print(f"❌ Error in delete_all_notes_templates: {e}")
            return False
            
    def delete_test_dispositions_only(self):
        """Delete only test dispositions, keep original medical dispositions"""
        print("\n🗑️ Deleting TEST dispositions only...")
        
        # Get all dispositions
        try:
            response = requests.get(f"{self.base_url}/api/dispositions", headers=self.headers)
            if response.status_code != 200:
                print(f"❌ Error getting dispositions: {response.status_code}")
                return False
                
            dispositions = response.json()
            print(f"📋 Found {len(dispositions)} total dispositions")
            
            # Identify test dispositions (those with TEST_, BULK_TEST_, UPDATE_TEST_ prefixes)
            test_dispositions = []
            original_dispositions = []
            
            for disposition in dispositions:
                name = disposition.get('name', '')
                if (name.startswith('TEST_DISPOSITION_') or 
                    name.startswith('BULK_TEST_') or 
                    name.startswith('UPDATE_TEST_')):
                    test_dispositions.append(disposition)
                else:
                    original_dispositions.append(disposition)
                    
            print(f"🎯 Identified {len(test_dispositions)} test dispositions to delete")
            print(f"✅ Will preserve {len(original_dispositions)} original medical dispositions")
            
            # List test dispositions to be deleted
            if test_dispositions:
                print("\n📋 Test dispositions to be deleted:")
                for disp in test_dispositions:
                    print(f"  - {disp.get('name', 'Unknown')} (ID: {disp.get('id')})")
                    
            deleted_count = 0
            for disposition in test_dispositions:
                disposition_id = disposition.get('id')
                disposition_name = disposition.get('name', 'Unknown')
                
                try:
                    delete_response = requests.delete(
                        f"{self.base_url}/api/dispositions/{disposition_id}",
                        headers=self.headers
                    )
                    
                    if delete_response.status_code == 200:
                        print(f"✅ Deleted test disposition: {disposition_name} (ID: {disposition_id})")
                        deleted_count += 1
                    else:
                        print(f"❌ Failed to delete test disposition {disposition_name}: {delete_response.status_code}")
                        
                except Exception as e:
                    print(f"❌ Error deleting test disposition {disposition_name}: {e}")
                    
            print(f"🎯 Deleted {deleted_count}/{len(test_dispositions)} test dispositions")
            return deleted_count == len(test_dispositions)
            
        except Exception as e:
            print(f"❌ Error in delete_test_dispositions_only: {e}")
            return False
            
    def verify_final_counts(self):
        """Verify final counts after cleanup"""
        print("\n✅ Verifying final counts after cleanup...")
        
        clinical_templates, notes_templates, dispositions = self.get_current_counts()
        
        # Expected final counts
        expected_clinical = 0  # All were test entries
        expected_notes = 0     # All were test entries  
        expected_dispositions = 61  # Original medical dispositions only
        
        success = True
        
        if len(clinical_templates) == expected_clinical:
            print(f"✅ Clinical templates: {len(clinical_templates)} (expected: {expected_clinical})")
        else:
            print(f"❌ Clinical templates: {len(clinical_templates)} (expected: {expected_clinical})")
            success = False
            
        if len(notes_templates) == expected_notes:
            print(f"✅ Notes templates: {len(notes_templates)} (expected: {expected_notes})")
        else:
            print(f"❌ Notes templates: {len(notes_templates)} (expected: {expected_notes})")
            success = False
            
        if len(dispositions) == expected_dispositions:
            print(f"✅ Dispositions: {len(dispositions)} (expected: {expected_dispositions})")
        else:
            print(f"❌ Dispositions: {len(dispositions)} (expected: {expected_dispositions})")
            success = False
            
        return success
        
    def run_cleanup(self):
        """Execute the complete cleanup process"""
        print("🧹 Starting Database Cleanup Process")
        print("=" * 60)
        
        # Step 1: Backup data
        if not self.backup_data():
            print("❌ Backup failed - aborting cleanup")
            return False
            
        # Step 2: Get initial counts
        print("\n📊 Initial counts:")
        self.get_current_counts()
        
        # Step 3: Delete all clinical templates
        if not self.delete_all_clinical_templates():
            print("❌ Clinical template deletion failed")
            return False
            
        # Step 4: Delete all notes templates
        if not self.delete_all_notes_templates():
            print("❌ Notes template deletion failed")
            return False
            
        # Step 5: Delete test dispositions only
        if not self.delete_test_dispositions_only():
            print("❌ Test disposition deletion failed")
            return False
            
        # Step 6: Verify final counts
        if not self.verify_final_counts():
            print("❌ Final count verification failed")
            return False
            
        print("\n🎉 Database cleanup completed successfully!")
        return True

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
    
    # Run database cleanup
    cleanup_tester = DatabaseCleanupTester(backend_url)
    cleanup_success = cleanup_tester.run_cleanup()
    
    return 0 if cleanup_success else 1


if __name__ == "__main__":
    sys.exit(main())