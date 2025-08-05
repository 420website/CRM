import requests
import json
import sys
from dotenv import load_dotenv
import os
from datetime import datetime, date
import random
import string

# Load the frontend .env file to get the backend URL
load_dotenv('/app/frontend/.env')
backend_url = os.environ.get('REACT_APP_BACKEND_URL')

if not backend_url:
    print("❌ Error: REACT_APP_BACKEND_URL not found in frontend .env file")
    sys.exit(1)

print(f"🔗 Using backend URL from .env: {backend_url}")

class AdminRegistrationTester:
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

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    return success, response_data
                except:
                    return success, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    response_data = response.json()
                    print(f"Response: {response_data}")
                    return False, response_data
                except:
                    print(f"Response: {response.text}")
                    return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def generate_test_data(self):
        """Generate random test data for admin registration"""
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
        today = date.today()
        today_str = today.isoformat()
        dob_date = date(today.year - 40, today.month, today.day)
        dob_str = dob_date.isoformat()
        
        # Base64 encoded small image
        sample_image = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
        
        self.test_data = {
            "firstName": f"Test {random_suffix}",
            "lastName": f"User {random_suffix}",
            "dob": dob_str,
            "patientConsent": "Verbal",
            "gender": "Male",
            "province": "Ontario",
            "disposition": "Option 1",
            "aka": f"TU {random_suffix}",
            "age": "40",
            "regDate": today_str,
            "healthCard": ''.join(random.choices(string.digits, k=10)),
            "healthCardVersion": "AB",  # New field for health card version code
            "referralSite": "Toronto - Outreach",  # One of the predefined referral sites
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
            "email": f"test.user.{random_suffix}@example.com",
            "language": "English",
            "specialAttention": "Test notes",
            "physician": "Dr. David Fletcher",
            "photo": sample_image
        }
        
        return self.test_data

    def test_referral_site_values(self):
        """Test various referral site values from the dropdown"""
        print("\n" + "=" * 50)
        print("🔍 Testing Referral Site Field")
        print("=" * 50)
        
        # List of referral sites to test
        referral_sites = [
            "Toronto - Outreach",
            "Barrie - City Centre Pharmacy",
            "Windsor - Downtown Mission"
        ]
        
        for site in referral_sites:
            # Create test data with this referral site
            data = self.generate_test_data()
            data["referralSite"] = site
            
            success, response = self.run_test(
                f"Referral Site: {site}",
                "POST",
                "api/admin-register",
                200,
                data=data
            )
            
            if success:
                reg_id = response.get('registration_id')
                self.registration_ids.append(reg_id)
                print(f"✅ Successfully registered with referral site: {site}")
                print(f"   Registration ID: {reg_id}")
                
                # Verify in MongoDB
                self.verify_in_mongodb(reg_id, "referralSite", site)
            
        return True

    def test_health_card_version_code(self):
        """Test health card version code field"""
        print("\n" + "=" * 50)
        print("🔍 Testing Health Card Version Code Field")
        print("=" * 50)
        
        # Test with various 2-character values
        version_codes = ["AB", "ON", "BC"]
        
        for code in version_codes:
            # Create test data with this health card version code
            data = self.generate_test_data()
            data["healthCardVersion"] = code
            
            success, response = self.run_test(
                f"Health Card Version Code: {code}",
                "POST",
                "api/admin-register",
                200,
                data=data
            )
            
            if success:
                reg_id = response.get('registration_id')
                self.registration_ids.append(reg_id)
                print(f"✅ Successfully registered with health card version code: {code}")
                print(f"   Registration ID: {reg_id}")
                
                # Verify in MongoDB
                self.verify_in_mongodb(reg_id, "healthCardVersion", code)
        
        return True

    def test_physician_field(self):
        """Test physician field with both options"""
        print("\n" + "=" * 50)
        print("🔍 Testing Physician Field")
        print("=" * 50)
        
        # Test with Dr. David Fletcher (default)
        data1 = self.generate_test_data()
        data1["disposition"] = "Option 1"  # Not POCT NEG
        data1["physician"] = "Dr. David Fletcher"
        
        success1, response1 = self.run_test(
            "Physician: Dr. David Fletcher",
            "POST",
            "api/admin-register",
            200,
            data=data1
        )
        
        if success1:
            reg_id1 = response1.get('registration_id')
            self.registration_ids.append(reg_id1)
            print(f"✅ Successfully registered with physician: Dr. David Fletcher")
            print(f"   Registration ID: {reg_id1}")
            
            # Verify in MongoDB
            self.verify_in_mongodb(reg_id1, "physician", "Dr. David Fletcher")
        
        # Test with None (when disposition is POCT NEG)
        data2 = self.generate_test_data()
        data2["disposition"] = "POCT NEG"
        data2["physician"] = "None"
        
        success2, response2 = self.run_test(
            "Physician: None (with POCT NEG)",
            "POST",
            "api/admin-register",
            200,
            data=data2
        )
        
        if success2:
            reg_id2 = response2.get('registration_id')
            self.registration_ids.append(reg_id2)
            print(f"✅ Successfully registered with physician: None")
            print(f"   Registration ID: {reg_id2}")
            
            # Verify in MongoDB
            self.verify_in_mongodb(reg_id2, "physician", "None")
        
        return success1 and success2

    def test_disposition_logic(self):
        """Test disposition logic with POCT NEG"""
        print("\n" + "=" * 50)
        print("🔍 Testing Disposition Logic")
        print("=" * 50)
        
        # Test with POCT NEG disposition and None physician
        data = self.generate_test_data()
        data["disposition"] = "POCT NEG"
        data["physician"] = "None"
        
        success, response = self.run_test(
            "Disposition POCT NEG with Physician None",
            "POST",
            "api/admin-register",
            200,
            data=data
        )
        
        if success:
            reg_id = response.get('registration_id')
            self.registration_ids.append(reg_id)
            print(f"✅ Successfully registered with POCT NEG disposition and None physician")
            print(f"   Registration ID: {reg_id}")
            
            # Verify in MongoDB
            success1 = self.verify_in_mongodb(reg_id, "disposition", "POCT NEG")
            success2 = self.verify_in_mongodb(reg_id, "physician", "None")
            
            return success1 and success2
        
        return False

    def test_complete_form_submission(self):
        """Test complete form submission with all new fields"""
        print("\n" + "=" * 50)
        print("🔍 Testing Complete Form Submission")
        print("=" * 50)
        
        # Create complete test data
        data = self.generate_test_data()
        data["referralSite"] = "Toronto - Outreach"
        data["healthCardVersion"] = "ON"
        data["disposition"] = "Option 2"
        data["physician"] = "Dr. David Fletcher"
        
        success, response = self.run_test(
            "Complete Form Submission",
            "POST",
            "api/admin-register",
            200,
            data=data
        )
        
        if success:
            reg_id = response.get('registration_id')
            self.registration_ids.append(reg_id)
            print(f"✅ Successfully submitted complete form")
            print(f"   Registration ID: {reg_id}")
            
            # Verify all fields in MongoDB
            success1 = self.verify_in_mongodb(reg_id, "referralSite", "Toronto - Outreach")
            success2 = self.verify_in_mongodb(reg_id, "healthCardVersion", "ON")
            success3 = self.verify_in_mongodb(reg_id, "disposition", "Option 2")
            success4 = self.verify_in_mongodb(reg_id, "physician", "Dr. David Fletcher")
            
            return success1 and success2 and success3 and success4
        
        return False

    def verify_in_mongodb(self, registration_id, field_name, expected_value):
        """Verify a field value in MongoDB"""
        try:
            from pymongo import MongoClient
            import os
            from dotenv import load_dotenv
            
            # Load MongoDB connection details from backend .env
            load_dotenv('/app/backend/.env')
            mongo_url = os.environ.get('MONGO_URL')
            db_name = os.environ.get('DB_NAME')
            
            if not mongo_url or not db_name:
                print(f"❌ MongoDB connection details not found in backend .env")
                return False
                
            # Connect to MongoDB
            client = MongoClient(mongo_url)
            db = client[db_name]
            collection = db["admin_registrations"]
            
            # Find the registration
            registration = collection.find_one({"id": registration_id})
            
            if registration:
                # Check if field is present and matches expected value
                if field_name in registration and registration[field_name] == expected_value:
                    print(f"✅ Verified in MongoDB: {field_name} = {expected_value}")
                    return True
                else:
                    actual_value = registration.get(field_name, "Not found")
                    print(f"❌ MongoDB verification failed: {field_name} = {actual_value}, expected {expected_value}")
                    return False
            else:
                print(f"❌ Could not find registration with ID {registration_id}")
                return False
        except Exception as e:
            print(f"❌ Error verifying in MongoDB: {str(e)}")
            return False

    def run_all_tests(self):
        """Run all tests for the admin registration API"""
        print("🚀 Starting Admin Registration API Tests")
        print(f"🔗 Base URL: {self.base_url}")
        print("=" * 50)
        
        # Run all tests
        referral_site_test = self.test_referral_site_values()
        health_card_version_test = self.test_health_card_version_code()
        physician_test = self.test_physician_field()
        disposition_test = self.test_disposition_logic()
        complete_form_test = self.test_complete_form_submission()
        
        # Print summary
        print("\n" + "=" * 50)
        print("📊 Test Summary:")
        print(f"✅ Referral Site Field Test: {'Passed' if referral_site_test else 'Failed'}")
        print(f"✅ Health Card Version Code Test: {'Passed' if health_card_version_test else 'Failed'}")
        print(f"✅ Physician Field Test: {'Passed' if physician_test else 'Failed'}")
        print(f"✅ Disposition Logic Test: {'Passed' if disposition_test else 'Failed'}")
        print(f"✅ Complete Form Submission Test: {'Passed' if complete_form_test else 'Failed'}")
        print("=" * 50)
        print(f"📊 Tests passed: {self.tests_passed}/{self.tests_run}")
        
        all_passed = all([
            referral_site_test,
            health_card_version_test,
            physician_test,
            disposition_test,
            complete_form_test
        ])
        
        return all_passed


def main():
    # Run the tests
    tester = AdminRegistrationTester(backend_url)
    success = tester.run_all_tests()
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())