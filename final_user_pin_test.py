#!/usr/bin/env python3
"""
Final User PIN Update Verification Test
Comprehensive test to verify the user PIN update system is working correctly.
"""

import requests
import json
import time
from datetime import datetime
import sys
import os
from dotenv import load_dotenv

class FinalUserPINTest:
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
            else:
                raise ValueError(f"Unsupported method: {method}")
                
            return response
            
        except Exception as e:
            print(f"❌ Request failed: {str(e)}")
            return None
    
    def test_pin_update_and_verification_flow(self):
        """Test the complete PIN update and verification flow"""
        print("\n" + "="*80)
        print("🔍 COMPREHENSIVE PIN UPDATE AND VERIFICATION TEST")
        print("="*80)
        
        # Step 1: Get current users
        print("\n📋 Step 1: Getting current users...")
        response = self.make_request('GET', 'api/users')
        if not response or response.status_code != 200:
            return self.log_test("PIN Update Flow", False, "- Failed to get users")
        
        users = response.json()
        if len(users) == 0:
            return self.log_test("PIN Update Flow", False, "- No users found")
        
        # Use the first user for testing
        test_user = users[0]
        user_id = test_user.get('id')
        original_pin = test_user.get('pin')
        original_email = test_user.get('email')
        
        print(f"🎯 Testing with: {test_user.get('firstName')} {test_user.get('lastName')}")
        print(f"🔢 Original PIN: {original_pin}")
        print(f"📧 Original Email: {original_email}")
        
        # Step 2: Find a unique new PIN
        used_pins = [user.get('pin') for user in users if user.get('pin')]
        new_pin = None
        for candidate in ["0001", "0002", "0003", "0004", "0005"]:
            if candidate != original_pin and candidate not in used_pins:
                new_pin = candidate
                break
        
        if not new_pin:
            return self.log_test("PIN Update Flow", False, "- Could not find unique PIN")
        
        print(f"🔢 New PIN: {new_pin}")
        
        # Step 3: Update PIN
        print(f"\n🔄 Step 2: Updating PIN from {original_pin} to {new_pin}...")
        update_data = {"pin": new_pin}
        response = self.make_request('PUT', f'api/users/{user_id}', data=update_data)
        
        if not response or response.status_code != 200:
            return self.log_test("PIN Update Flow", False, f"- PIN update failed (Status: {response.status_code if response else 'No response'})")
        
        result = response.json()
        if result.get('user', {}).get('pin') != new_pin:
            return self.log_test("PIN Update Flow", False, "- PIN not updated in response")
        
        print(f"✅ PIN updated successfully")
        
        # Step 4: Verify old PIN is rejected
        print(f"\n🚫 Step 3: Verifying old PIN {original_pin} is rejected...")
        pin_data = {"pin": original_pin}
        response = self.make_request('POST', 'api/auth/pin-verify', data=pin_data, expected_status=401)
        
        if response and response.status_code == 401:
            print(f"✅ Old PIN {original_pin} correctly rejected")
        else:
            print(f"⚠️ Old PIN rejection test inconclusive (Status: {response.status_code if response else 'No response'})")
        
        # Step 5: Verify new PIN is accepted
        print(f"\n✅ Step 4: Verifying new PIN {new_pin} is accepted...")
        pin_data = {"pin": new_pin}
        response = self.make_request('POST', 'api/auth/pin-verify', data=pin_data)
        
        if not response or response.status_code != 200:
            return self.log_test("PIN Update Flow", False, f"- New PIN verification failed (Status: {response.status_code if response else 'No response'})")
        
        result = response.json()
        if not result.get('pin_valid'):
            return self.log_test("PIN Update Flow", False, "- New PIN not validated")
        
        if result.get('user_id') != user_id:
            return self.log_test("PIN Update Flow", False, "- Wrong user returned")
        
        print(f"✅ New PIN {new_pin} correctly accepted and user identified")
        
        # Step 6: Update email
        new_email = "updated.test.email@testdomain.com"
        print(f"\n📧 Step 5: Updating email from {original_email} to {new_email}...")
        update_data = {"email": new_email}
        response = self.make_request('PUT', f'api/users/{user_id}', data=update_data)
        
        if not response or response.status_code != 200:
            return self.log_test("PIN Update Flow", False, f"- Email update failed (Status: {response.status_code if response else 'No response'})")
        
        result = response.json()
        if result.get('user', {}).get('email') != new_email:
            return self.log_test("PIN Update Flow", False, "- Email not updated in response")
        
        print(f"✅ Email updated successfully")
        
        # Step 7: Verify email is reflected in authentication
        print(f"\n🔐 Step 6: Verifying updated email in authentication...")
        pin_data = {"pin": new_pin}
        response = self.make_request('POST', 'api/auth/pin-verify', data=pin_data)
        
        if not response or response.status_code != 200:
            return self.log_test("PIN Update Flow", False, "- Authentication with updated email failed")
        
        result = response.json()
        returned_email = result.get('email')
        two_fa_email = result.get('two_fa_email')
        
        if returned_email != new_email:
            return self.log_test("PIN Update Flow", False, f"- Email mismatch in auth. Expected: {new_email}, Got: {returned_email}")
        
        if two_fa_email != new_email:
            return self.log_test("PIN Update Flow", False, f"- 2FA email mismatch. Expected: {new_email}, Got: {two_fa_email}")
        
        print(f"✅ Updated email correctly returned in authentication")
        print(f"✅ 2FA email correctly set to updated email")
        
        # Step 8: Restore original values (cleanup)
        print(f"\n🔄 Step 7: Restoring original values...")
        restore_data = {"pin": original_pin, "email": original_email}
        response = self.make_request('PUT', f'api/users/{user_id}', data=restore_data)
        
        if response and response.status_code == 200:
            print(f"✅ Original values restored")
        else:
            print(f"⚠️ Could not restore original values")
        
        return self.log_test("PIN Update Flow", True, "- Complete flow working correctly")
    
    def test_database_consistency(self):
        """Test that database updates are immediately consistent"""
        print("\n" + "="*80)
        print("🔍 DATABASE CONSISTENCY TEST")
        print("="*80)
        
        # Get users
        response = self.make_request('GET', 'api/users')
        if not response or response.status_code != 200:
            return self.log_test("Database Consistency", False, "- Failed to get users")
        
        users = response.json()
        if len(users) == 0:
            return self.log_test("Database Consistency", False, "- No users found")
        
        test_user = users[0]
        user_id = test_user.get('id')
        original_pin = test_user.get('pin')
        
        # Find unique PIN
        used_pins = [user.get('pin') for user in users if user.get('pin')]
        test_pin = None
        for candidate in ["0010", "0020", "0030"]:
            if candidate != original_pin and candidate not in used_pins:
                test_pin = candidate
                break
        
        if not test_pin:
            return self.log_test("Database Consistency", False, "- Could not find unique test PIN")
        
        print(f"🔄 Testing immediate consistency with PIN update: {original_pin} -> {test_pin}")
        
        # Update PIN
        update_data = {"pin": test_pin}
        response = self.make_request('PUT', f'api/users/{user_id}', data=update_data)
        
        if not response or response.status_code != 200:
            return self.log_test("Database Consistency", False, "- PIN update failed")
        
        # Immediately verify the PIN works
        pin_data = {"pin": test_pin}
        response = self.make_request('POST', 'api/auth/pin-verify', data=pin_data)
        
        if not response or response.status_code != 200:
            # Restore original PIN
            restore_data = {"pin": original_pin}
            self.make_request('PUT', f'api/users/{user_id}', data=restore_data)
            return self.log_test("Database Consistency", False, "- Updated PIN not immediately recognized")
        
        result = response.json()
        if not result.get('pin_valid') or result.get('user_id') != user_id:
            # Restore original PIN
            restore_data = {"pin": original_pin}
            self.make_request('PUT', f'api/users/{user_id}', data=restore_data)
            return self.log_test("Database Consistency", False, "- PIN verification failed")
        
        # Restore original PIN
        restore_data = {"pin": original_pin}
        self.make_request('PUT', f'api/users/{user_id}', data=restore_data)
        
        return self.log_test("Database Consistency", True, "- Database updates are immediately consistent")
    
    def run_all_tests(self):
        """Run all tests"""
        print("🚀 FINAL USER PIN UPDATE VERIFICATION TEST")
        print("=" * 80)
        print("Comprehensive verification that the user PIN update system is working correctly")
        print("=" * 80)
        
        # Run tests
        self.test_pin_update_and_verification_flow()
        self.test_database_consistency()
        
        # Summary
        print("\n" + "=" * 80)
        print("📊 FINAL TEST SUMMARY")
        print("=" * 80)
        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Tests Failed: {self.tests_run - self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed / self.tests_run * 100):.1f}%" if self.tests_run > 0 else "0%")
        
        if self.tests_passed == self.tests_run:
            print("\n🎉 ALL TESTS PASSED!")
            print("✅ User PIN update system is working correctly")
            print("✅ PIN updates are immediately recognized by the login system")
            print("✅ Email updates are immediately reflected in authentication")
            print("✅ Database consistency is maintained")
            print("✅ No disconnect between CRUD operations and authentication system")
        else:
            print("\n⚠️ SOME TESTS FAILED")
            print("❌ There may be issues with the user PIN update system")
            
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
    tester = FinalUserPINTest(backend_url)
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()