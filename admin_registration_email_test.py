#!/usr/bin/env python3
"""
CRITICAL EMAIL VERIFICATION TEST
Test admin registration finalization email system to verify emails go to 420pharmacyprogram@gmail.com
This addresses a CRITICAL privacy issue where emails were going to the wrong address.
"""

import requests
import json
import time
import os
import subprocess
from datetime import datetime, date
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/backend/.env')

class AdminRegistrationEmailTester:
    def __init__(self):
        # Get backend URL from frontend .env
        self.base_url = 'http://localhost:8001/api'
        try:
            with open('/app/frontend/.env', 'r') as f:
                for line in f:
                    if line.startswith('REACT_APP_BACKEND_URL='):
                        self.base_url = line.split('=')[1].strip() + '/api'
                        break
        except Exception:
            pass
        
        print(f"🔗 Using backend URL: {self.base_url}")
        
        # Test tracking
        self.tests_run = 0
        self.tests_passed = 0
        self.registration_id = None
        
        # Expected email address
        self.expected_email = "420pharmacyprogram@gmail.com"
        
    def log_test(self, name, success, details=""):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name}")
        else:
            print(f"❌ {name}")
        
        if details:
            print(f"   {details}")
    
    def create_test_registration(self):
        """Create a new admin registration with realistic test data"""
        print("\n🔍 STEP 1: Creating test admin registration...")
        
        # Use realistic test data (not dummy data)
        test_data = {
            "firstName": "Sarah",
            "lastName": "Johnson",
            "dob": "1985-03-15",
            "patientConsent": "verbal",
            "gender": "Female",
            "province": "Ontario",
            "disposition": "Active",
            "age": "38",
            "regDate": str(date.today()),
            "healthCard": "1234567890AB",
            "healthCardVersion": "AB",
            "referralSite": "Downtown Clinic",
            "address": "123 Main Street",
            "unitNumber": "Apt 4B",
            "city": "Toronto",
            "postalCode": "M5V 3A8",
            "phone1": "416-555-0123",
            "phone2": "647-555-0456",
            "ext1": "",
            "ext2": "",
            "leaveMessage": True,
            "voicemail": True,
            "text": False,
            "preferredTime": "Morning",
            "email": "sarah.johnson@email.com",
            "language": "English",
            "specialAttention": "Test registration for email verification",
            "physician": "Dr. David Fletcher",
            "rnaAvailable": "No",
            "rnaSampleDate": "",
            "rnaResult": "Positive",
            "coverageType": "OHIP",
            "referralPerson": "Nurse Mary",
            "testType": "HCV"
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/admin-register",
                json=test_data,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            if response.status_code == 200:
                response_data = response.json()
                self.registration_id = response_data.get('registration_id')
                
                self.log_test(
                    "Create admin registration", 
                    True, 
                    f"Registration ID: {self.registration_id}"
                )
                return True
            else:
                self.log_test(
                    "Create admin registration", 
                    False, 
                    f"Status: {response.status_code}, Response: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Create admin registration", False, f"Error: {str(e)}")
            return False
    
    def verify_registration_pending(self):
        """Verify the registration is in pending_review status"""
        print("\n🔍 STEP 2: Verifying registration is pending...")
        
        if not self.registration_id:
            self.log_test("Verify pending status", False, "No registration ID available")
            return False
        
        try:
            response = requests.get(
                f"{self.base_url}/admin-registration/{self.registration_id}",
                timeout=30
            )
            
            if response.status_code == 200:
                registration_data = response.json()
                status = registration_data.get('status')
                
                if status == 'pending_review':
                    self.log_test(
                        "Verify pending status", 
                        True, 
                        f"Status: {status}"
                    )
                    return True
                else:
                    self.log_test(
                        "Verify pending status", 
                        False, 
                        f"Expected 'pending_review', got '{status}'"
                    )
                    return False
            else:
                self.log_test(
                    "Verify pending status", 
                    False, 
                    f"Status: {response.status_code}"
                )
                return False
                
        except Exception as e:
            self.log_test("Verify pending status", False, f"Error: {str(e)}")
            return False
    
    def check_environment_email_config(self):
        """Check the environment email configuration"""
        print("\n🔍 STEP 3: Checking email configuration...")
        
        support_email = os.environ.get('SUPPORT_EMAIL')
        
        if support_email == self.expected_email:
            self.log_test(
                "Environment email config", 
                True, 
                f"SUPPORT_EMAIL = {support_email}"
            )
            return True
        else:
            self.log_test(
                "Environment email config", 
                False, 
                f"SUPPORT_EMAIL = {support_email}, expected {self.expected_email}"
            )
            return False
    
    def finalize_registration(self):
        """Finalize the registration to trigger email sending"""
        print("\n🔍 STEP 4: Finalizing registration to trigger email...")
        
        if not self.registration_id:
            self.log_test("Finalize registration", False, "No registration ID available")
            return False
        
        try:
            # Clear any existing logs first
            self.clear_backend_logs()
            
            response = requests.post(
                f"{self.base_url}/admin-registration/{self.registration_id}/finalize",
                headers={'Content-Type': 'application/json'},
                timeout=60  # Longer timeout for email sending
            )
            
            if response.status_code == 200:
                response_data = response.json()
                email_sent = response_data.get('email_sent', False)
                finalized_at = response_data.get('finalized_at')
                
                self.log_test(
                    "Finalize registration", 
                    True, 
                    f"Email sent: {email_sent}, Finalized at: {finalized_at}"
                )
                
                # Give a moment for logs to be written
                time.sleep(2)
                return True
            else:
                self.log_test(
                    "Finalize registration", 
                    False, 
                    f"Status: {response.status_code}, Response: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Finalize registration", False, f"Error: {str(e)}")
            return False
    
    def clear_backend_logs(self):
        """Clear backend logs to get fresh log data"""
        try:
            # Clear supervisor logs
            subprocess.run(['sudo', 'truncate', '-s', '0', '/var/log/supervisor/backend.out.log'], 
                         capture_output=True, timeout=10)
            subprocess.run(['sudo', 'truncate', '-s', '0', '/var/log/supervisor/backend.err.log'], 
                         capture_output=True, timeout=10)
            print("   📝 Cleared backend logs for fresh capture")
        except Exception as e:
            print(f"   ⚠️  Could not clear logs: {str(e)}")
    
    def check_backend_logs_for_email(self):
        """Check backend logs to verify what email address was used"""
        print("\n🔍 STEP 5: Checking backend logs for email address...")
        
        try:
            # Check supervisor logs
            log_files = [
                '/var/log/supervisor/backend.out.log',
                '/var/log/supervisor/backend.err.log'
            ]
            
            email_found = False
            correct_email_used = False
            log_entries = []
            
            for log_file in log_files:
                try:
                    with open(log_file, 'r') as f:
                        content = f.read()
                        
                        # Look for email-related log entries
                        lines = content.split('\n')
                        for line in lines:
                            if any(keyword in line.lower() for keyword in [
                                'email debug', 'support_email', 'will send to', 
                                'sending to', 'email sent', 'force email'
                            ]):
                                log_entries.append(line.strip())
                                
                                # Check if the correct email address is mentioned
                                if self.expected_email in line:
                                    correct_email_used = True
                                    email_found = True
                                elif 'support@my420.ca' in line:
                                    email_found = True
                                    # This would be the wrong email
                
                except FileNotFoundError:
                    continue
                except Exception as e:
                    print(f"   ⚠️  Error reading {log_file}: {str(e)}")
            
            # Print relevant log entries
            if log_entries:
                print("   📝 Relevant log entries:")
                for entry in log_entries[-10:]:  # Show last 10 entries
                    print(f"      {entry}")
            
            if email_found and correct_email_used:
                self.log_test(
                    "Backend logs show correct email", 
                    True, 
                    f"Found {self.expected_email} in logs"
                )
                return True
            elif email_found and not correct_email_used:
                self.log_test(
                    "Backend logs show correct email", 
                    False, 
                    "Found email activity but wrong address (support@my420.ca)"
                )
                return False
            else:
                self.log_test(
                    "Backend logs show correct email", 
                    False, 
                    "No email activity found in logs"
                )
                return False
                
        except Exception as e:
            self.log_test("Backend logs check", False, f"Error: {str(e)}")
            return False
    
    def verify_final_status(self):
        """Verify the registration status is now completed"""
        print("\n🔍 STEP 6: Verifying final registration status...")
        
        if not self.registration_id:
            self.log_test("Verify final status", False, "No registration ID available")
            return False
        
        try:
            response = requests.get(
                f"{self.base_url}/admin-registration/{self.registration_id}",
                timeout=30
            )
            
            if response.status_code == 200:
                registration_data = response.json()
                status = registration_data.get('status')
                finalized_at = registration_data.get('finalized_at')
                
                if status == 'completed' and finalized_at:
                    self.log_test(
                        "Verify final status", 
                        True, 
                        f"Status: {status}, Finalized: {finalized_at}"
                    )
                    return True
                else:
                    self.log_test(
                        "Verify final status", 
                        False, 
                        f"Status: {status}, Finalized: {finalized_at}"
                    )
                    return False
            else:
                self.log_test(
                    "Verify final status", 
                    False, 
                    f"Status: {response.status_code}"
                )
                return False
                
        except Exception as e:
            self.log_test("Verify final status", False, f"Error: {str(e)}")
            return False
    
    def run_comprehensive_test(self):
        """Run the complete email verification test"""
        print("🚨 CRITICAL EMAIL VERIFICATION TEST")
        print("=" * 60)
        print(f"Testing that finalization emails go to: {self.expected_email}")
        print(f"NOT to the old address: support@my420.ca")
        print("=" * 60)
        
        # Run all test steps
        steps = [
            self.create_test_registration,
            self.verify_registration_pending,
            self.check_environment_email_config,
            self.finalize_registration,
            self.check_backend_logs_for_email,
            self.verify_final_status
        ]
        
        all_passed = True
        for step in steps:
            if not step():
                all_passed = False
                # Continue with remaining steps for complete diagnosis
        
        # Final summary
        print("\n" + "=" * 60)
        print("🏁 FINAL TEST RESULTS")
        print("=" * 60)
        print(f"Tests run: {self.tests_run}")
        print(f"Tests passed: {self.tests_passed}")
        print(f"Success rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        if all_passed:
            print("✅ ALL TESTS PASSED - Email system is working correctly!")
            print(f"✅ Emails are being sent to: {self.expected_email}")
        else:
            print("❌ SOME TESTS FAILED - Email system needs attention!")
            print("❌ This is a CRITICAL privacy issue that must be resolved!")
        
        if self.registration_id:
            print(f"📋 Test registration ID: {self.registration_id}")
        
        return all_passed

def main():
    """Main test execution"""
    tester = AdminRegistrationEmailTester()
    success = tester.run_comprehensive_test()
    
    if success:
        exit(0)
    else:
        exit(1)

if __name__ == "__main__":
    main()