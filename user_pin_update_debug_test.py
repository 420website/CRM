#!/usr/bin/env python3
"""
User PIN Update Debug Test
Debug and test the user PIN update issue that the user reported.

This test will:
1. List Current Users: Get all active users and their current PINs to see what's in the database
2. Test PIN Update: Update a specific user's PIN and verify the update worked
3. Test PIN Verification: Immediately after updating the PIN, test the unified PIN verification to see if the new PIN is recognized
4. Check Database Consistency: Verify that the user record is properly updated in the database
5. Test Email Update: Also test updating a user's email address and verify it's reflected in authentication
"""

import requests
import json
import time
from datetime import datetime
import sys
import os
from dotenv import load_dotenv

class UserPINUpdateDebugTester:
    def __init__(self, base_url):
        self.base_url = base_url
        self.headers = {'Content-Type': 'application/json'}
        self.tests_run = 0
        self.tests_passed = 0
        
    def log_test(self, test_name, success, details=""):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {test_name}: PASSED {details}")
        else:
            print(f"❌ {test_name}: FAILED {details}")
        return success
        
    def make_request(self, method, endpoint, data=None, expected_status=200):
        """Make HTTP request and return response"""
        url = f"{self.base_url}/{endpoint}"
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=self.headers)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=self.headers)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=self.headers)
            elif method == 'DELETE':
                response = requests.delete(url, headers=self.headers)
            else:
                raise ValueError(f"Unsupported method: {method}")
                
            print(f"🔗 {method} {endpoint} -> {response.status_code}")
            
            if response.status_code != expected_status:
                print(f"⚠️ Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"📄 Response: {json.dumps(error_data, indent=2)}")
                except:
                    print(f"📄 Response: {response.text}")
                    
            return response
            
        except Exception as e:
            print(f"❌ Request failed: {str(e)}")
            return None
    
    def test_1_list_current_users(self):
        """Test 1: List Current Users - Get all active users and their current PINs"""
        print("\n" + "="*60)
        print("🔍 TEST 1: LIST CURRENT USERS")
        print("="*60)
        
        response = self.make_request('GET', 'api/users', expected_status=200)
        
        if not response or response.status_code != 200:
            return self.log_test("List Current Users", False, "- Failed to get users list")
        
        try:
            users = response.json()
            print(f"📊 Found {len(users)} active users in the database:")
            
            for i, user in enumerate(users, 1):
                print(f"  {i}. {user.get('firstName', 'N/A')} {user.get('lastName', 'N/A')}")
                print(f"     📧 Email: {user.get('email', 'N/A')}")
                print(f"     📱 Phone: {user.get('phone', 'N/A')}")
                print(f"     🔢 PIN: {user.get('pin', 'N/A')}")
                print(f"     🆔 ID: {user.get('id', 'N/A')}")
                print(f"     📅 Created: {user.get('created_at', 'N/A')}")
                print(f"     📅 Updated: {user.get('updated_at', 'N/A')}")
                print()
            
            # Store users for later tests
            self.users = users
            
            if len(users) == 0:
                return self.log_test("List Current Users", False, "- No users found in database")
            
            return self.log_test("List Current Users", True, f"- Found {len(users)} users")
            
        except Exception as e:
            return self.log_test("List Current Users", False, f"- Error parsing response: {str(e)}")
    
    def test_2_create_test_user_if_needed(self):
        """Test 2: Create a test user if we don't have enough users to test with"""
        print("\n" + "="*60)
        print("🔍 TEST 2: CREATE TEST USER IF NEEDED")
        print("="*60)
        
        if not hasattr(self, 'users') or len(self.users) == 0:
            print("📝 No existing users found. Creating a test user...")
            
            test_user_data = {
                "firstName": "Christian",
                "lastName": "Marcoux",
                "email": "christian.marcoux@testdomain.com",
                "phone": "4161234567",
                "pin": "1234",
                "permissions": {
                    "dashboard": True,
                    "registration": True,
                    "analytics": True
                }
            }
            
            response = self.make_request('POST', 'api/users', data=test_user_data, expected_status=200)
            
            if not response or response.status_code != 200:
                return self.log_test("Create Test User", False, "- Failed to create test user")
            
            try:
                result = response.json()
                print(f"✅ Created test user: {result.get('user', {}).get('firstName')} {result.get('user', {}).get('lastName')}")
                print(f"🔢 PIN: {result.get('user', {}).get('pin')}")
                print(f"📧 Email: {result.get('user', {}).get('email')}")
                
                # Add to our users list
                if not hasattr(self, 'users'):
                    self.users = []
                self.users.append(result.get('user', {}))
                
                return self.log_test("Create Test User", True, "- Test user created successfully")
                
            except Exception as e:
                return self.log_test("Create Test User", False, f"- Error parsing response: {str(e)}")
        else:
            print(f"📊 Found {len(self.users)} existing users. No need to create test user.")
            return self.log_test("Create Test User", True, "- Using existing users")
    
    def test_3_update_user_pin(self):
        """Test 3: Update a specific user's PIN and verify the update worked"""
        print("\n" + "="*60)
        print("🔍 TEST 3: UPDATE USER PIN")
        print("="*60)
        
        if not hasattr(self, 'users') or len(self.users) == 0:
            return self.log_test("Update User PIN", False, "- No users available for testing")
        
        # Use the first user for testing
        test_user = self.users[0]
        user_id = test_user.get('id')
        original_pin = test_user.get('pin')
        
        print(f"🎯 Testing with user: {test_user.get('firstName')} {test_user.get('lastName')}")
        print(f"🔢 Original PIN: {original_pin}")
        
        # Generate a new PIN (different from original and not used by other users)
        used_pins = [user.get('pin') for user in self.users if user.get('pin')]
        print(f"📋 Used PINs in system: {used_pins}")
        
        # Find a unique PIN
        new_pin = None
        for candidate in ["9999", "8888", "7777", "6666", "5555", "4444", "3333", "2222", "1111", "0000"]:
            if candidate != original_pin and candidate not in used_pins:
                new_pin = candidate
                break
        
        if not new_pin:
            # Generate a random 4-digit PIN
            import random
            while True:
                new_pin = f"{random.randint(0, 9999):04d}"
                if new_pin != original_pin and new_pin not in used_pins:
                    break
        
        print(f"🔢 New PIN: {new_pin}")
        
        # Update the user's PIN
        update_data = {
            "pin": new_pin
        }
        
        response = self.make_request('PUT', f'api/users/{user_id}', data=update_data, expected_status=200)
        
        if not response or response.status_code != 200:
            return self.log_test("Update User PIN", False, f"- Failed to update PIN (Status: {response.status_code if response else 'No response'})")
        
        try:
            result = response.json()
            updated_user = result.get('user', {})
            
            print(f"📄 Update response: {json.dumps(result, indent=2)}")
            
            # Verify the PIN was updated in the response
            if updated_user.get('pin') == new_pin:
                print(f"✅ PIN updated in response: {original_pin} -> {new_pin}")
                
                # Store the updated user info for next tests
                self.test_user_id = user_id
                self.test_user_original_pin = original_pin
                self.test_user_new_pin = new_pin
                self.test_user_email = updated_user.get('email')
                
                return self.log_test("Update User PIN", True, f"- PIN updated from {original_pin} to {new_pin}")
            else:
                return self.log_test("Update User PIN", False, f"- PIN not updated in response. Expected: {new_pin}, Got: {updated_user.get('pin')}")
                
        except Exception as e:
            return self.log_test("Update User PIN", False, f"- Error parsing response: {str(e)}")
    
    def test_4_verify_database_consistency(self):
        """Test 4: Check Database Consistency - Verify that the user record is properly updated in the database"""
        print("\n" + "="*60)
        print("🔍 TEST 4: VERIFY DATABASE CONSISTENCY")
        print("="*60)
        
        if not hasattr(self, 'test_user_id'):
            return self.log_test("Database Consistency", False, "- No test user ID available")
        
        # Get the user by ID to verify the update persisted
        response = self.make_request('GET', f'api/users/{self.test_user_id}', expected_status=200)
        
        if not response or response.status_code != 200:
            return self.log_test("Database Consistency", False, f"- Failed to get user by ID (Status: {response.status_code if response else 'No response'})")
        
        try:
            user = response.json()
            
            print(f"📄 User from database: {json.dumps(user, indent=2)}")
            
            # Check if the PIN matches what we updated it to
            db_pin = user.get('pin')
            expected_pin = self.test_user_new_pin
            
            if db_pin == expected_pin:
                print(f"✅ Database consistency verified: PIN is {db_pin}")
                return self.log_test("Database Consistency", True, f"- PIN correctly stored as {db_pin}")
            else:
                print(f"❌ Database inconsistency: Expected PIN {expected_pin}, but database has {db_pin}")
                return self.log_test("Database Consistency", False, f"- Expected PIN {expected_pin}, got {db_pin}")
                
        except Exception as e:
            return self.log_test("Database Consistency", False, f"- Error parsing response: {str(e)}")
    
    def test_5_verify_old_pin_rejected(self):
        """Test 5: Verify that the old PIN is no longer recognized"""
        print("\n" + "="*60)
        print("🔍 TEST 5: VERIFY OLD PIN REJECTED")
        print("="*60)
        
        if not hasattr(self, 'test_user_original_pin'):
            return self.log_test("Old PIN Rejection", False, "- No original PIN available")
        
        old_pin = self.test_user_original_pin
        print(f"🔢 Testing old PIN: {old_pin}")
        
        # Try to verify with the old PIN - should fail
        pin_data = {"pin": old_pin}
        
        response = self.make_request('POST', 'api/auth/pin-verify', data=pin_data, expected_status=401)
        
        if response and response.status_code == 401:
            print(f"✅ Old PIN {old_pin} correctly rejected")
            return self.log_test("Old PIN Rejection", True, f"- Old PIN {old_pin} properly rejected")
        else:
            print(f"❌ Old PIN {old_pin} was not rejected (Status: {response.status_code if response else 'No response'})")
            if response:
                try:
                    result = response.json()
                    print(f"📄 Unexpected response: {json.dumps(result, indent=2)}")
                except:
                    print(f"📄 Response text: {response.text}")
            return self.log_test("Old PIN Rejection", False, f"- Old PIN {old_pin} was not properly rejected")
    
    def test_6_verify_new_pin_accepted(self):
        """Test 6: Test PIN Verification - Immediately after updating the PIN, test the unified PIN verification to see if the new PIN is recognized"""
        print("\n" + "="*60)
        print("🔍 TEST 6: VERIFY NEW PIN ACCEPTED")
        print("="*60)
        
        if not hasattr(self, 'test_user_new_pin'):
            return self.log_test("New PIN Verification", False, "- No new PIN available")
        
        new_pin = self.test_user_new_pin
        print(f"🔢 Testing new PIN: {new_pin}")
        
        # Try to verify with the new PIN - should succeed
        pin_data = {"pin": new_pin}
        
        response = self.make_request('POST', 'api/auth/pin-verify', data=pin_data, expected_status=200)
        
        if not response or response.status_code != 200:
            print(f"❌ New PIN {new_pin} was rejected (Status: {response.status_code if response else 'No response'})")
            if response:
                try:
                    result = response.json()
                    print(f"📄 Error response: {json.dumps(result, indent=2)}")
                except:
                    print(f"📄 Response text: {response.text}")
            return self.log_test("New PIN Verification", False, f"- New PIN {new_pin} was rejected")
        
        try:
            result = response.json()
            print(f"📄 PIN verification response: {json.dumps(result, indent=2)}")
            
            # Check if the response indicates successful verification
            if result.get('pin_valid') == True:
                user_type = result.get('user_type')
                user_id = result.get('user_id')
                email = result.get('email')
                
                print(f"✅ New PIN {new_pin} correctly accepted")
                print(f"👤 User Type: {user_type}")
                print(f"🆔 User ID: {user_id}")
                print(f"📧 Email: {email}")
                
                # Verify this is the correct user
                if user_id == self.test_user_id:
                    print(f"✅ Correct user identified: {user_id}")
                    return self.log_test("New PIN Verification", True, f"- New PIN {new_pin} accepted and correct user identified")
                else:
                    print(f"❌ Wrong user identified. Expected: {self.test_user_id}, Got: {user_id}")
                    return self.log_test("New PIN Verification", False, f"- Wrong user identified")
            else:
                print(f"❌ PIN verification failed. pin_valid: {result.get('pin_valid')}")
                return self.log_test("New PIN Verification", False, f"- PIN verification returned pin_valid: {result.get('pin_valid')}")
                
        except Exception as e:
            return self.log_test("New PIN Verification", False, f"- Error parsing response: {str(e)}")
    
    def test_7_update_user_email(self):
        """Test 7: Test Email Update - Update a user's email address and verify it's reflected in authentication"""
        print("\n" + "="*60)
        print("🔍 TEST 7: UPDATE USER EMAIL")
        print("="*60)
        
        if not hasattr(self, 'test_user_id'):
            return self.log_test("Update User Email", False, "- No test user ID available")
        
        original_email = self.test_user_email
        new_email = "christian.marcoux.updated@testdomain.com"
        
        print(f"📧 Original Email: {original_email}")
        print(f"📧 New Email: {new_email}")
        
        # Update the user's email
        update_data = {
            "email": new_email
        }
        
        response = self.make_request('PUT', f'api/users/{self.test_user_id}', data=update_data, expected_status=200)
        
        if not response or response.status_code != 200:
            return self.log_test("Update User Email", False, f"- Failed to update email (Status: {response.status_code if response else 'No response'})")
        
        try:
            result = response.json()
            updated_user = result.get('user', {})
            
            print(f"📄 Update response: {json.dumps(result, indent=2)}")
            
            # Verify the email was updated in the response
            if updated_user.get('email') == new_email:
                print(f"✅ Email updated in response: {original_email} -> {new_email}")
                self.test_user_updated_email = new_email
                return self.log_test("Update User Email", True, f"- Email updated from {original_email} to {new_email}")
            else:
                return self.log_test("Update User Email", False, f"- Email not updated in response. Expected: {new_email}, Got: {updated_user.get('email')}")
                
        except Exception as e:
            return self.log_test("Update User Email", False, f"- Error parsing response: {str(e)}")
    
    def test_8_verify_email_in_authentication(self):
        """Test 8: Verify that the updated email is reflected in authentication"""
        print("\n" + "="*60)
        print("🔍 TEST 8: VERIFY EMAIL IN AUTHENTICATION")
        print("="*60)
        
        if not hasattr(self, 'test_user_new_pin') or not hasattr(self, 'test_user_updated_email'):
            return self.log_test("Email in Authentication", False, "- Missing test data")
        
        pin = self.test_user_new_pin
        expected_email = self.test_user_updated_email
        
        print(f"🔢 Using PIN: {pin}")
        print(f"📧 Expected Email: {expected_email}")
        
        # Verify PIN and check if the updated email is returned
        pin_data = {"pin": pin}
        
        response = self.make_request('POST', 'api/auth/pin-verify', data=pin_data, expected_status=200)
        
        if not response or response.status_code != 200:
            return self.log_test("Email in Authentication", False, f"- PIN verification failed (Status: {response.status_code if response else 'No response'})")
        
        try:
            result = response.json()
            returned_email = result.get('email')
            
            print(f"📄 Authentication response: {json.dumps(result, indent=2)}")
            print(f"📧 Returned Email: {returned_email}")
            
            if returned_email == expected_email:
                print(f"✅ Updated email correctly returned in authentication: {returned_email}")
                return self.log_test("Email in Authentication", True, f"- Updated email {returned_email} correctly returned")
            else:
                print(f"❌ Email mismatch. Expected: {expected_email}, Got: {returned_email}")
                return self.log_test("Email in Authentication", False, f"- Expected email {expected_email}, got {returned_email}")
                
        except Exception as e:
            return self.log_test("Email in Authentication", False, f"- Error parsing response: {str(e)}")
    
    def test_9_complete_flow_test(self):
        """Test 9: Complete Flow Test - Update User → Login with New PIN → 2FA with Updated Email"""
        print("\n" + "="*60)
        print("🔍 TEST 9: COMPLETE FLOW TEST")
        print("="*60)
        
        if not hasattr(self, 'test_user_new_pin') or not hasattr(self, 'test_user_updated_email'):
            return self.log_test("Complete Flow Test", False, "- Missing test data")
        
        pin = self.test_user_new_pin
        email = self.test_user_updated_email
        
        print(f"🔄 Testing complete authentication flow:")
        print(f"   1. PIN Verification: {pin}")
        print(f"   2. Email for 2FA: {email}")
        
        # Step 1: PIN Verification
        pin_data = {"pin": pin}
        response = self.make_request('POST', 'api/auth/pin-verify', data=pin_data, expected_status=200)
        
        if not response or response.status_code != 200:
            return self.log_test("Complete Flow Test", False, f"- Step 1 (PIN verification) failed")
        
        try:
            result = response.json()
            session_token = result.get('session_token')
            two_fa_email = result.get('two_fa_email')
            
            print(f"✅ Step 1 - PIN Verification successful")
            print(f"🎫 Session Token: {session_token}")
            print(f"📧 2FA Email: {two_fa_email}")
            
            if two_fa_email != email:
                print(f"⚠️ 2FA email mismatch. Expected: {email}, Got: {two_fa_email}")
                return self.log_test("Complete Flow Test", False, f"- 2FA email mismatch")
            
            # Step 2: 2FA Setup (if needed)
            if result.get('needs_email_verification', False):
                print(f"📧 User needs email verification - this is expected for new users")
                
                # Test 2FA setup endpoint
                setup_response = self.make_request('POST', 'api/admin/2fa/setup', expected_status=200)
                
                if setup_response and setup_response.status_code == 200:
                    print(f"✅ Step 2 - 2FA Setup endpoint accessible")
                else:
                    print(f"⚠️ Step 2 - 2FA Setup endpoint not accessible (this may be expected)")
            
            return self.log_test("Complete Flow Test", True, f"- Complete flow working: PIN → Session → 2FA Email")
            
        except Exception as e:
            return self.log_test("Complete Flow Test", False, f"- Error in flow test: {str(e)}")
    
    def run_all_tests(self):
        """Run all debug tests"""
        print("🚀 USER PIN UPDATE DEBUG TEST SUITE")
        print("=" * 80)
        print("Debug and test the user PIN update issue that the user reported.")
        print("This will test the complete flow: Update User → Login with New PIN → 2FA with Updated Email")
        print("=" * 80)
        
        # Run all tests in sequence
        self.test_1_list_current_users()
        self.test_2_create_test_user_if_needed()
        self.test_3_update_user_pin()
        self.test_4_verify_database_consistency()
        self.test_5_verify_old_pin_rejected()
        self.test_6_verify_new_pin_accepted()
        self.test_7_update_user_email()
        self.test_8_verify_email_in_authentication()
        self.test_9_complete_flow_test()
        
        # Summary
        print("\n" + "=" * 80)
        print("📊 TEST SUMMARY")
        print("=" * 80)
        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Tests Failed: {self.tests_run - self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed / self.tests_run * 100):.1f}%" if self.tests_run > 0 else "0%")
        
        if self.tests_passed == self.tests_run:
            print("🎉 ALL TESTS PASSED - User PIN update system is working correctly!")
        else:
            print("⚠️ SOME TESTS FAILED - There are issues with the user PIN update system")
            
        return self.tests_passed == self.tests_run

def main():
    # Load environment variables
    load_dotenv('/app/frontend/.env')
    
    # Get backend URL from environment
    backend_url = os.environ.get('REACT_APP_BACKEND_URL')
    if not backend_url:
        print("❌ REACT_APP_BACKEND_URL not found in environment")
        sys.exit(1)
    
    print(f"🔗 Backend URL: {backend_url}")
    
    # Create tester and run tests
    tester = UserPINUpdateDebugTester(backend_url)
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()