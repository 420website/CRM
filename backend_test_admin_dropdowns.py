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

print(f"🔗 Using backend URL from .env: {backend_url}")

class AdminRegistrationDropdownTester:
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

    def generate_test_data(self):
        """Generate random test data for admin registration"""
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
                "province": "Ontario",
                "disposition": "POCT NEG",  # Testing the special disposition case
                "aka": f"Mike {random_suffix}",
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
                "email": f"michael.smith.{random_suffix}@example.com",
                "language": "English",
                "specialAttention": "Patient requires interpreter assistance",
                "physician": "None",  # Should be "None" when disposition is "POCT NEG"
                "photo": sample_image
            }
        }
        
        return self.test_data

    def test_referral_site_dropdown(self):
        """Test admin registration with various referral site values from the dropdown"""
        if not self.test_data:
            self.generate_test_data()
        
        # List of referral sites to test (from the 25 predefined options)
        referral_sites = [
            "Toronto - Outreach",
            "Barrie - City Centre Pharmacy",
            "Windsor - Downtown Mission",
            "Ottawa - Community Health Centre",
            "Hamilton - Urban Core"
        ]
        
        print("\n" + "=" * 50)
        print("🔍 Testing Referral Site Dropdown Values")
        print("=" * 50)
        
        all_passed = True
        
        for site in referral_sites:
            # Create data with this referral site
            data = self.test_data["admin_registration"].copy()
            data["referralSite"] = site
            
            success, response = self.run_test(
                f"Admin Registration - Referral Site: {site}",
                "POST",
                "api/admin-register",
                200,
                data=data
            )
            
            if success:
                print(f"✅ Successfully registered with referral site: {site}")
                
                # Verify in MongoDB that the referral site was stored correctly
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
                        all_passed = False
                        continue
                        
                    # Connect to MongoDB
                    client = MongoClient(mongo_url)
                    db = client[db_name]
                    collection = db["admin_registrations"]
                    
                    # Find the registration we just created
                    registration = collection.find_one({"id": response.get('registration_id')})
                    
                    if registration:
                        # Check if referralSite is present and matches what we sent
                        if "referralSite" in registration and registration["referralSite"] == site:
                            print(f"✅ Referral site verified in MongoDB: {registration['referralSite']}")
                        else:
                            print(f"❌ Referral site in MongoDB ({registration.get('referralSite', 'Not found')}) does not match expected value ({site})")
                            all_passed = False
                    else:
                        print(f"❌ Could not find registration with ID {response.get('registration_id')}")
                        all_passed = False
                except Exception as e:
                    print(f"❌ Error verifying referral site in MongoDB: {str(e)}")
                    all_passed = False
            else:
                all_passed = False
        
        return all_passed

    def test_health_card_version_code(self):
        """Test admin registration with health card version code field"""
        if not self.test_data:
            self.generate_test_data()
        
        # List of health card version codes to test
        version_codes = ["AB", "ON", "BC", "QC", "NS"]
        
        print("\n" + "=" * 50)
        print("🔍 Testing Health Card Version Code Field")
        print("=" * 50)
        
        all_passed = True
        
        for code in version_codes:
            # Create data with this health card version code
            data = self.test_data["admin_registration"].copy()
            data["healthCardVersion"] = code
            
            success, response = self.run_test(
                f"Admin Registration - Health Card Version Code: {code}",
                "POST",
                "api/admin-register",
                200,
                data=data
            )
            
            if success:
                print(f"✅ Successfully registered with health card version code: {code}")
                
                # Verify in MongoDB that the health card version code was stored correctly
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
                        all_passed = False
                        continue
                        
                    # Connect to MongoDB
                    client = MongoClient(mongo_url)
                    db = client[db_name]
                    collection = db["admin_registrations"]
                    
                    # Find the registration we just created
                    registration = collection.find_one({"id": response.get('registration_id')})
                    
                    if registration:
                        # Check if healthCardVersion is present and matches what we sent
                        if "healthCardVersion" in registration and registration["healthCardVersion"] == code:
                            print(f"✅ Health card version code verified in MongoDB: {registration['healthCardVersion']}")
                        else:
                            print(f"❌ Health card version code in MongoDB ({registration.get('healthCardVersion', 'Not found')}) does not match expected value ({code})")
                            all_passed = False
                    else:
                        print(f"❌ Could not find registration with ID {response.get('registration_id')}")
                        all_passed = False
                except Exception as e:
                    print(f"❌ Error verifying health card version code in MongoDB: {str(e)}")
                    all_passed = False
            else:
                all_passed = False
        
        return all_passed

    def test_physician_dropdown(self):
        """Test admin registration with physician dropdown values"""
        if not self.test_data:
            self.generate_test_data()
        
        print("\n" + "=" * 50)
        print("🔍 Testing Physician Dropdown Values")
        print("=" * 50)
        
        # Test 1: Default physician (Dr. David Fletcher) with non-POCT NEG disposition
        data_default_physician = self.test_data["admin_registration"].copy()
        data_default_physician["disposition"] = "Option 1"  # Not POCT NEG
        data_default_physician["physician"] = "Dr. David Fletcher"
        
        success1, response1 = self.run_test(
            "Admin Registration - Default Physician (Dr. David Fletcher)",
            "POST",
            "api/admin-register",
            200,
            data=data_default_physician
        )
        
        # Test 2: None physician with POCT NEG disposition
        data_none_physician = self.test_data["admin_registration"].copy()
        data_none_physician["disposition"] = "POCT NEG"
        data_none_physician["physician"] = "None"
        
        success2, response2 = self.run_test(
            "Admin Registration - None Physician with POCT NEG",
            "POST",
            "api/admin-register",
            200,
            data=data_none_physician
        )
        
        # Verify in MongoDB that the physician values were stored correctly
        all_passed = True
        
        if success1:
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
                    all_passed = False
                else:
                    # Connect to MongoDB
                    client = MongoClient(mongo_url)
                    db = client[db_name]
                    collection = db["admin_registrations"]
                    
                    # Find the first registration we created (default physician)
                    registration1 = collection.find_one({"id": response1.get('registration_id')})
                    
                    if registration1:
                        # Check if physician is present and matches what we sent
                        if "physician" in registration1 and registration1["physician"] == "Dr. David Fletcher":
                            print(f"✅ Default physician verified in MongoDB: {registration1['physician']}")
                        else:
                            print(f"❌ Physician in MongoDB ({registration1.get('physician', 'Not found')}) does not match expected value (Dr. David Fletcher)")
                            all_passed = False
                    else:
                        print(f"❌ Could not find registration with ID {response1.get('registration_id')}")
                        all_passed = False
            except Exception as e:
                print(f"❌ Error verifying default physician in MongoDB: {str(e)}")
                all_passed = False
        else:
            all_passed = False
        
        if success2:
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
                    all_passed = False
                else:
                    # Connect to MongoDB
                    client = MongoClient(mongo_url)
                    db = client[db_name]
                    collection = db["admin_registrations"]
                    
                    # Find the second registration we created (None physician)
                    registration2 = collection.find_one({"id": response2.get('registration_id')})
                    
                    if registration2:
                        # Check if physician is present and matches what we sent
                        if "physician" in registration2 and registration2["physician"] == "None":
                            print(f"✅ None physician verified in MongoDB: {registration2['physician']}")
                        else:
                            print(f"❌ Physician in MongoDB ({registration2.get('physician', 'Not found')}) does not match expected value (None)")
                            all_passed = False
                    else:
                        print(f"❌ Could not find registration with ID {response2.get('registration_id')}")
                        all_passed = False
            except Exception as e:
                print(f"❌ Error verifying None physician in MongoDB: {str(e)}")
                all_passed = False
        else:
            all_passed = False
        
        return all_passed

    def test_disposition_physician_logic(self):
        """Test the logic where disposition POCT NEG should have physician set to None"""
        if not self.test_data:
            self.generate_test_data()
        
        print("\n" + "=" * 50)
        print("🔍 Testing Disposition-Physician Logic")
        print("=" * 50)
        
        # Create data with POCT NEG disposition but try to set physician to Dr. David Fletcher
        # The backend should accept this (it's the frontend's responsibility to set the correct physician)
        data = self.test_data["admin_registration"].copy()
        data["disposition"] = "POCT NEG"
        data["physician"] = "Dr. David Fletcher"  # This should be accepted by the backend
        
        success, response = self.run_test(
            "Admin Registration - POCT NEG with Dr. David Fletcher",
            "POST",
            "api/admin-register",
            200,
            data=data
        )
        
        if success:
            print("✅ Backend correctly accepts POCT NEG disposition with any physician value")
            print("   (Frontend is responsible for setting physician to 'None' when disposition is 'POCT NEG')")
            
            # Verify in MongoDB that the values were stored as sent
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
                    return False
                    
                # Connect to MongoDB
                client = MongoClient(mongo_url)
                db = client[db_name]
                collection = db["admin_registrations"]
                
                # Find the registration we just created
                registration = collection.find_one({"id": response.get('registration_id')})
                
                if registration:
                    # Check if disposition and physician are present and match what we sent
                    disposition_correct = registration.get("disposition") == "POCT NEG"
                    physician_correct = registration.get("physician") == "Dr. David Fletcher"
                    
                    if disposition_correct and physician_correct:
                        print("✅ Disposition and physician values verified in MongoDB")
                        print(f"   Disposition: {registration['disposition']}")
                        print(f"   Physician: {registration['physician']}")
                        return True
                    else:
                        if not disposition_correct:
                            print(f"❌ Disposition in MongoDB ({registration.get('disposition', 'Not found')}) does not match expected value (POCT NEG)")
                        if not physician_correct:
                            print(f"❌ Physician in MongoDB ({registration.get('physician', 'Not found')}) does not match expected value (Dr. David Fletcher)")
                        return False
                else:
                    print(f"❌ Could not find registration with ID {response.get('registration_id')}")
                    return False
            except Exception as e:
                print(f"❌ Error verifying values in MongoDB: {str(e)}")
                return False
        else:
            return False

    def test_complete_form_submission(self):
        """Test a complete admin registration with all the new dropdown values"""
        if not self.test_data:
            self.generate_test_data()
        
        print("\n" + "=" * 50)
        print("🔍 Testing Complete Form Submission with New Fields")
        print("=" * 50)
        
        # Create complete data with all new fields
        complete_data = self.test_data["admin_registration"].copy()
        complete_data["referralSite"] = "Toronto - Outreach"
        complete_data["healthCardVersion"] = "ON"
        complete_data["disposition"] = "Option 2"  # Not POCT NEG
        complete_data["physician"] = "Dr. David Fletcher"
        
        success, response = self.run_test(
            "Admin Registration - Complete Form with New Fields",
            "POST",
            "api/admin-register",
            200,
            data=complete_data
        )
        
        if success:
            print("✅ Successfully submitted complete form with all new fields")
            print(f"   Registration ID: {response.get('registration_id')}")
            
            # Verify in MongoDB that all fields were stored correctly
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
                    return False
                    
                # Connect to MongoDB
                client = MongoClient(mongo_url)
                db = client[db_name]
                collection = db["admin_registrations"]
                
                # Find the registration we just created
                registration = collection.find_one({"id": response.get('registration_id')})
                
                if registration:
                    # Check if all new fields are present and match what we sent
                    referral_site_correct = registration.get("referralSite") == "Toronto - Outreach"
                    health_card_version_correct = registration.get("healthCardVersion") == "ON"
                    physician_correct = registration.get("physician") == "Dr. David Fletcher"
                    
                    if referral_site_correct and health_card_version_correct and physician_correct:
                        print("✅ All new fields verified in MongoDB:")
                        print(f"   Referral Site: {registration['referralSite']}")
                        print(f"   Health Card Version: {registration['healthCardVersion']}")
                        print(f"   Physician: {registration['physician']}")
                        return True
                    else:
                        if not referral_site_correct:
                            print(f"❌ Referral Site in MongoDB ({registration.get('referralSite', 'Not found')}) does not match expected value (Toronto - Outreach)")
                        if not health_card_version_correct:
                            print(f"❌ Health Card Version in MongoDB ({registration.get('healthCardVersion', 'Not found')}) does not match expected value (ON)")
                        if not physician_correct:
                            print(f"❌ Physician in MongoDB ({registration.get('physician', 'Not found')}) does not match expected value (Dr. David Fletcher)")
                        return False
                else:
                    print(f"❌ Could not find registration with ID {response.get('registration_id')}")
                    return False
            except Exception as e:
                print(f"❌ Error verifying fields in MongoDB: {str(e)}")
                return False
        else:
            return False

    def run_all_tests(self):
        """Run all tests for the admin registration dropdown fields"""
        print("🚀 Starting Admin Registration Dropdown Field Tests")
        print(f"🔗 Base URL: {self.base_url}")
        print("=" * 50)
        
        # Generate test data
        self.generate_test_data()
        
        # Run all tests
        referral_site_test = self.test_referral_site_dropdown()
        health_card_version_test = self.test_health_card_version_code()
        physician_test = self.test_physician_dropdown()
        disposition_logic_test = self.test_disposition_physician_logic()
        complete_form_test = self.test_complete_form_submission()
        
        # Print summary
        print("\n" + "=" * 50)
        print("📊 Test Summary:")
        print(f"✅ Referral Site Dropdown Test: {'Passed' if referral_site_test else 'Failed'}")
        print(f"✅ Health Card Version Code Test: {'Passed' if health_card_version_test else 'Failed'}")
        print(f"✅ Physician Dropdown Test: {'Passed' if physician_test else 'Failed'}")
        print(f"✅ Disposition-Physician Logic Test: {'Passed' if disposition_logic_test else 'Failed'}")
        print(f"✅ Complete Form Submission Test: {'Passed' if complete_form_test else 'Failed'}")
        print("=" * 50)
        print(f"📊 Tests passed: {self.tests_passed}/{self.tests_run}")
        
        return all([referral_site_test, health_card_version_test, physician_test, disposition_logic_test, complete_form_test])


def main():
    # Run the tests
    tester = AdminRegistrationDropdownTester(backend_url)
    success = tester.run_all_tests()
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())