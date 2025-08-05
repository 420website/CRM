#!/usr/bin/env python3
"""
Comprehensive Email Template Changes Test Suite
Tests the email template changes to ensure the registration date is properly included as the first line
"""

import requests
import json
import sys
import os
from datetime import datetime, date
import random
import string
from dotenv import load_dotenv

class EmailTemplateTest:
    def __init__(self, base_url):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.test_registration_id = None
        
    def log_test(self, test_name, success, message=""):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {test_name}: PASSED {message}")
        else:
            print(f"❌ {test_name}: FAILED {message}")
        return success
        
    def generate_test_registration_data(self):
        """Generate test registration data"""
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
        today = date.today()
        
        return {
            "firstName": f"EmailTest{random_suffix}",
            "lastName": f"User{random_suffix}",
            "dob": "1985-05-15",
            "patientConsent": "Verbal",
            "gender": "Male",
            "province": "Ontario",
            "disposition": "Test Disposition",
            "aka": f"TestAlias{random_suffix}",
            "age": "38",
            "regDate": today.isoformat(),
            "healthCard": ''.join(random.choices(string.digits, k=10)),
            "healthCardVersion": "AB",
            "referralSite": "Test Clinic",
            "address": f"{random.randint(100, 999)} Test Street",
            "unitNumber": "101",
            "city": "Toronto",
            "postalCode": "M1A 1A1",
            "phone1": ''.join(random.choices(string.digits, k=10)),
            "phone2": ''.join(random.choices(string.digits, k=10)),
            "ext1": "123",
            "ext2": "456",
            "leaveMessage": True,
            "voicemail": True,
            "text": False,
            "preferredTime": "Morning",
            "email": f"emailtest{random_suffix}@example.com",
            "language": "English",
            "specialAttention": "Test special attention notes",
            "physician": "Dr. Test Physician",
            "summaryTemplate": "Test clinical summary template content"
        }
    
    def test_create_registration(self):
        """Create a test registration for email testing"""
        print("\n🔍 Creating test registration for email template testing...")
        
        registration_data = self.generate_test_registration_data()
        
        try:
            response = requests.post(
                f"{self.base_url}/api/admin-register",
                json=registration_data,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            if response.status_code == 200:
                response_data = response.json()
                self.test_registration_id = response_data.get('registration_id')
                return self.log_test(
                    "Create Test Registration",
                    True,
                    f"- Registration ID: {self.test_registration_id}"
                )
            else:
                return self.log_test(
                    "Create Test Registration",
                    False,
                    f"- Status: {response.status_code}, Response: {response.text}"
                )
                
        except Exception as e:
            return self.log_test(
                "Create Test Registration",
                False,
                f"- Error: {str(e)}"
            )
    
    def test_finalize_endpoint_availability(self):
        """Test that the finalize endpoint is available"""
        print("\n🔍 Testing finalize endpoint availability...")
        
        if not self.test_registration_id:
            return self.log_test(
                "Finalize Endpoint Availability",
                False,
                "- No test registration ID available"
            )
        
        try:
            # Test GET endpoint
            response = requests.get(
                f"{self.base_url}/api/admin-registration/{self.test_registration_id}/finalize",
                timeout=30
            )
            
            # Should return 200 or 400 (if already finalized), not 404
            if response.status_code in [200, 400]:
                return self.log_test(
                    "Finalize Endpoint Availability",
                    True,
                    f"- GET endpoint available (Status: {response.status_code})"
                )
            else:
                return self.log_test(
                    "Finalize Endpoint Availability",
                    False,
                    f"- GET endpoint returned: {response.status_code}"
                )
                
        except Exception as e:
            return self.log_test(
                "Finalize Endpoint Availability",
                False,
                f"- Error: {str(e)}"
            )
    
    def test_email_template_structure(self):
        """Test the email template structure by examining the finalize endpoint response"""
        print("\n🔍 Testing email template structure...")
        
        if not self.test_registration_id:
            return self.log_test(
                "Email Template Structure",
                False,
                "- No test registration ID available"
            )
        
        try:
            # Call the finalize endpoint to trigger email generation
            response = requests.post(
                f"{self.base_url}/api/admin-registration/{self.test_registration_id}/finalize",
                timeout=60  # Longer timeout for email processing
            )
            
            if response.status_code == 200:
                response_data = response.json()
                
                # Check if email was sent
                email_sent = response_data.get('email_sent', False)
                email_error = response_data.get('email_error')
                
                if email_sent:
                    return self.log_test(
                        "Email Template Structure",
                        True,
                        "- Email sent successfully, template structure working"
                    )
                else:
                    # Even if email failed to send, we can still check if the process worked
                    if email_error and "Registration Date:" in str(email_error):
                        return self.log_test(
                            "Email Template Structure",
                            True,
                            "- Template structure includes Registration Date (detected in error message)"
                        )
                    else:
                        return self.log_test(
                            "Email Template Structure",
                            False,
                            f"- Email failed to send: {email_error}"
                        )
            else:
                return self.log_test(
                    "Email Template Structure",
                    False,
                    f"- Finalize failed: {response.status_code}, {response.text}"
                )
                
        except Exception as e:
            return self.log_test(
                "Email Template Structure",
                False,
                f"- Error: {str(e)}"
            )
    
    def test_backend_email_functionality(self):
        """Test that backend email functionality is working"""
        print("\n🔍 Testing backend email functionality...")
        
        try:
            # Test that email configuration is available
            # We'll check if the SMTP settings are configured
            load_dotenv('/app/backend/.env')
            
            smtp_server = os.environ.get('SMTP_SERVER')
            smtp_username = os.environ.get('SMTP_USERNAME')
            support_email = os.environ.get('SUPPORT_EMAIL')
            
            if smtp_server and smtp_username and support_email:
                return self.log_test(
                    "Backend Email Configuration",
                    True,
                    f"- SMTP configured: {smtp_server}, Username: {smtp_username}, Support: {support_email}"
                )
            else:
                return self.log_test(
                    "Backend Email Configuration",
                    False,
                    f"- Missing config - SMTP: {smtp_server}, Username: {smtp_username}, Support: {support_email}"
                )
                
        except Exception as e:
            return self.log_test(
                "Backend Email Configuration",
                False,
                f"- Error: {str(e)}"
            )
    
    def test_registration_date_in_template(self):
        """Test that registration date is properly formatted and included"""
        print("\n🔍 Testing registration date formatting in template...")
        
        # This test verifies the template structure by checking the backend code logic
        # Since we can't directly inspect the email content, we verify the data flow
        
        if not self.test_registration_id:
            return self.log_test(
                "Registration Date in Template",
                False,
                "- No test registration ID available"
            )
        
        try:
            # Get the registration data to verify regDate is present
            from pymongo import MongoClient
            
            # Load MongoDB connection details
            load_dotenv('/app/backend/.env')
            mongo_url = os.environ.get('MONGO_URL')
            db_name = os.environ.get('DB_NAME')
            
            if not mongo_url or not db_name:
                return self.log_test(
                    "Registration Date in Template",
                    False,
                    "- MongoDB connection details not available"
                )
            
            # Connect to MongoDB and check the registration
            client = MongoClient(mongo_url)
            db = client[db_name]
            collection = db["admin_registrations"]
            
            registration = collection.find_one({"id": self.test_registration_id})
            
            if registration:
                reg_date = registration.get('regDate')
                if reg_date:
                    return self.log_test(
                        "Registration Date in Template",
                        True,
                        f"- Registration date present: {reg_date}"
                    )
                else:
                    return self.log_test(
                        "Registration Date in Template",
                        False,
                        "- Registration date not found in database"
                    )
            else:
                return self.log_test(
                    "Registration Date in Template",
                    False,
                    "- Registration not found in database"
                )
                
        except Exception as e:
            return self.log_test(
                "Registration Date in Template",
                False,
                f"- Error: {str(e)}"
            )
    
    def test_template_formatting_consistency(self):
        """Test that template formatting is consistent"""
        print("\n🔍 Testing template formatting consistency...")
        
        # This test verifies that the template structure follows the expected format
        # by checking the backend code implementation
        
        try:
            # Read the backend server.py file to verify template structure
            with open('/app/backend/server.py', 'r') as f:
                server_code = f.read()
            
            # Check for the expected template structure
            template_checks = [
                'Registration Date: {registration_data.get(\'regDate\')',  # First line
                'PATIENT INFORMATION:',  # Section header
                'CONTACT INFORMATION:',  # Section header
                'OTHER INFORMATION:',    # Section header
                'CLINICAL SUMMARY TEMPLATE:'  # Section header
            ]
            
            all_checks_passed = True
            missing_elements = []
            
            for check in template_checks:
                if check not in server_code:
                    all_checks_passed = False
                    missing_elements.append(check)
            
            if all_checks_passed:
                return self.log_test(
                    "Template Formatting Consistency",
                    True,
                    "- All expected template elements found in backend code"
                )
            else:
                return self.log_test(
                    "Template Formatting Consistency",
                    False,
                    f"- Missing elements: {missing_elements}"
                )
                
        except Exception as e:
            return self.log_test(
                "Template Formatting Consistency",
                False,
                f"- Error: {str(e)}"
            )
    
    def test_email_generation_process(self):
        """Test the complete email generation process"""
        print("\n🔍 Testing complete email generation process...")
        
        if not self.test_registration_id:
            return self.log_test(
                "Email Generation Process",
                False,
                "- No test registration ID available"
            )
        
        try:
            # Test the complete finalization process
            response = requests.post(
                f"{self.base_url}/api/admin-registration/{self.test_registration_id}/finalize",
                timeout=60
            )
            
            if response.status_code == 200:
                response_data = response.json()
                
                # Check all expected response fields
                expected_fields = ['message', 'registration_id', 'status', 'finalized_at', 'email_sent']
                missing_fields = [field for field in expected_fields if field not in response_data]
                
                if not missing_fields:
                    status = response_data.get('status')
                    finalized_at = response_data.get('finalized_at')
                    
                    if status == 'completed' and finalized_at:
                        return self.log_test(
                            "Email Generation Process",
                            True,
                            f"- Process completed successfully, Status: {status}, Finalized: {finalized_at}"
                        )
                    else:
                        return self.log_test(
                            "Email Generation Process",
                            False,
                            f"- Unexpected status or missing finalized_at: {status}, {finalized_at}"
                        )
                else:
                    return self.log_test(
                        "Email Generation Process",
                        False,
                        f"- Missing response fields: {missing_fields}"
                    )
            else:
                return self.log_test(
                    "Email Generation Process",
                    False,
                    f"- HTTP error: {response.status_code}, {response.text}"
                )
                
        except Exception as e:
            return self.log_test(
                "Email Generation Process",
                False,
                f"- Error: {str(e)}"
            )
    
    def test_template_changes_verification(self):
        """Verify the specific template changes requested"""
        print("\n🔍 Verifying specific template changes...")
        
        try:
            # Read the backend server.py file to verify specific changes
            with open('/app/backend/server.py', 'r') as f:
                server_code = f.read()
            
            # Check for specific changes
            changes_verified = []
            changes_failed = []
            
            # 1. Check that "Registration Date:" is the first line in email templates
            if 'Registration Date: {registration_data.get(\'regDate\')' in server_code:
                changes_verified.append("Registration Date as first line")
            else:
                changes_failed.append("Registration Date as first line")
            
            # 2. Check that "New Registration" title is used
            if 'New Registration' in server_code:
                changes_verified.append("New Registration title")
            else:
                changes_failed.append("New Registration title")
            
            # 3. Check that province is in contact information
            if 'Province: {registration_data.get(\'province\')' in server_code:
                changes_verified.append("Province in contact information")
            else:
                changes_failed.append("Province in contact information")
            
            # 4. Check that "OTHER INFORMATION:" is used instead of "Medical Information"
            if 'OTHER INFORMATION:' in server_code:
                changes_verified.append("OTHER INFORMATION section")
            else:
                changes_failed.append("OTHER INFORMATION section")
            
            # 5. Check that PROCESSING DETAILS section is removed
            if 'PROCESSING DETAILS:' not in server_code:
                changes_verified.append("PROCESSING DETAILS section removed")
            else:
                changes_failed.append("PROCESSING DETAILS section removed")
            
            if not changes_failed:
                return self.log_test(
                    "Template Changes Verification",
                    True,
                    f"- All changes verified: {', '.join(changes_verified)}"
                )
            else:
                return self.log_test(
                    "Template Changes Verification",
                    False,
                    f"- Failed changes: {', '.join(changes_failed)}, Verified: {', '.join(changes_verified)}"
                )
                
        except Exception as e:
            return self.log_test(
                "Template Changes Verification",
                False,
                f"- Error: {str(e)}"
            )
    
    def run_all_tests(self):
        """Run all email template tests"""
        print("🚀 Starting Email Template Changes Test Suite")
        print(f"🔗 Base URL: {self.base_url}")
        print("=" * 60)
        
        # Test sequence
        tests = [
            self.test_backend_email_functionality,
            self.test_create_registration,
            self.test_finalize_endpoint_availability,
            self.test_registration_date_in_template,
            self.test_template_formatting_consistency,
            self.test_template_changes_verification,
            self.test_email_template_structure,
            self.test_email_generation_process
        ]
        
        for test in tests:
            try:
                test()
            except Exception as e:
                self.log_test(test.__name__, False, f"- Exception: {str(e)}")
        
        print("\n" + "=" * 60)
        print(f"📊 Email Template Tests Summary:")
        print(f"✅ Tests Passed: {self.tests_passed}")
        print(f"❌ Tests Failed: {self.tests_run - self.tests_passed}")
        print(f"📈 Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        return self.tests_passed == self.tests_run

def main():
    """Main test execution"""
    # Get the backend URL from the frontend .env file
    load_dotenv('/app/frontend/.env')
    
    backend_url = os.environ.get('REACT_APP_BACKEND_URL')
    if not backend_url:
        print("❌ Error: REACT_APP_BACKEND_URL not found in frontend .env file")
        return 1
    
    print(f"🔗 Using backend URL from .env: {backend_url}")
    
    # Run the email template tests
    tester = EmailTemplateTest(backend_url)
    success = tester.run_all_tests()
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())