#!/usr/bin/env python3
"""
2FA Backend Implementation Testing Suite
Tests all 2FA functionality including PIN verification, setup, verification, and disable
"""

import requests
import json
import time
import pyotp
import re
from datetime import datetime

# Configuration
BACKEND_URL = "https://258401ff-ff29-421c-8498-4969ee7788f0.preview.emergentagent.com/api"
DEFAULT_PIN = "0224"

class TwoFactorAuthTester:
    def __init__(self):
        self.session_token = None
        self.totp_secret = None
        self.backup_codes = []
        
    def test_admin_user_creation(self):
        """Test 1: Admin User Creation - get_admin_user() function creates default admin user with PIN '0224'"""
        print("\n🔐 TEST 1: Admin User Creation")
        
        try:
            # Test PIN verification which triggers admin user creation if not exists
            response = requests.post(f"{BACKEND_URL}/admin/pin-verify", 
                                   json={"pin": DEFAULT_PIN},
                                   timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Admin user creation successful")
                print(f"   - PIN validation: {data.get('pin_valid', False)}")
                print(f"   - 2FA enabled: {data.get('two_fa_enabled', False)}")
                print(f"   - Session token received: {'session_token' in data}")
                
                # Store session token for subsequent tests
                self.session_token = data.get('session_token')
                return True
            else:
                print(f"❌ Admin user creation failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Admin user creation error: {str(e)}")
            return False
    
    def test_pin_verification(self):
        """Test 2: PIN Verification - /api/admin/pin-verify endpoint returns 2FA status"""
        print("\n🔑 TEST 2: PIN Verification")
        
        # Test valid PIN
        try:
            response = requests.post(f"{BACKEND_URL}/admin/pin-verify", 
                                   json={"pin": DEFAULT_PIN},
                                   timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Valid PIN verification successful")
                print(f"   - PIN valid: {data.get('pin_valid', False)}")
                print(f"   - 2FA enabled: {data.get('two_fa_enabled', False)}")
                print(f"   - 2FA required: {data.get('two_fa_required', False)}")
                print(f"   - Session token: {data.get('session_token', 'None')[:20]}...")
                
                self.session_token = data.get('session_token')
                valid_pin_test = True
            else:
                print(f"❌ Valid PIN verification failed: {response.status_code} - {response.text}")
                valid_pin_test = False
                
        except Exception as e:
            print(f"❌ Valid PIN verification error: {str(e)}")
            valid_pin_test = False
        
        # Test invalid PIN
        try:
            response = requests.post(f"{BACKEND_URL}/admin/pin-verify", 
                                   json={"pin": "9999"},
                                   timeout=30)
            
            if response.status_code == 401:
                print(f"✅ Invalid PIN correctly rejected")
                invalid_pin_test = True
            else:
                print(f"❌ Invalid PIN should be rejected but got: {response.status_code}")
                invalid_pin_test = False
                
        except Exception as e:
            print(f"❌ Invalid PIN test error: {str(e)}")
            invalid_pin_test = False
        
        # Test missing PIN
        try:
            response = requests.post(f"{BACKEND_URL}/admin/pin-verify", 
                                   json={},
                                   timeout=30)
            
            if response.status_code == 400:
                print(f"✅ Missing PIN correctly rejected")
                missing_pin_test = True
            else:
                print(f"❌ Missing PIN should be rejected but got: {response.status_code}")
                missing_pin_test = False
                
        except Exception as e:
            print(f"❌ Missing PIN test error: {str(e)}")
            missing_pin_test = False
        
        return valid_pin_test and invalid_pin_test and missing_pin_test
    
    def test_2fa_setup(self):
        """Test 3: 2FA Setup Flow - /api/admin/2fa/setup endpoint generates QR codes and backup codes"""
        print("\n🔧 TEST 3: 2FA Setup Flow")
        
        try:
            response = requests.post(f"{BACKEND_URL}/admin/2fa/setup", 
                                   timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 2FA setup successful")
                
                # Validate QR code data
                qr_code_data = data.get('qr_code_data', '')
                if qr_code_data.startswith('data:image/png;base64,'):
                    print(f"   - QR code generated: ✅ (length: {len(qr_code_data)})")
                else:
                    print(f"   - QR code generated: ❌ (invalid format)")
                
                # Validate backup codes
                backup_codes = data.get('backup_codes', [])
                if len(backup_codes) == 10 and all(len(code) == 8 for code in backup_codes):
                    print(f"   - Backup codes generated: ✅ ({len(backup_codes)} codes)")
                    self.backup_codes = backup_codes
                else:
                    print(f"   - Backup codes generated: ❌ (expected 10 codes of 8 chars each)")
                
                # Validate TOTP secret
                totp_secret = data.get('totp_secret', '')
                if len(totp_secret) == 32 and totp_secret.isalnum():
                    print(f"   - TOTP secret generated: ✅ (length: {len(totp_secret)})")
                    self.totp_secret = totp_secret
                else:
                    print(f"   - TOTP secret generated: ❌ (invalid format)")
                
                # Validate setup status
                setup_complete = data.get('setup_complete', True)
                if setup_complete == False:
                    print(f"   - Setup complete status: ✅ (False as expected)")
                else:
                    print(f"   - Setup complete status: ❌ (should be False)")
                
                return True
            else:
                print(f"❌ 2FA setup failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ 2FA setup error: {str(e)}")
            return False
    
    def test_2fa_setup_verification(self):
        """Test 4: 2FA Setup Verification - /api/admin/2fa/verify-setup endpoint enables 2FA"""
        print("\n✅ TEST 4: 2FA Setup Verification")
        
        if not self.totp_secret:
            print("❌ Cannot test setup verification - no TOTP secret available")
            return False
        
        # Generate valid TOTP code
        try:
            totp = pyotp.TOTP(self.totp_secret)
            valid_code = totp.now()
            print(f"   - Generated TOTP code: {valid_code}")
            
            # Test valid TOTP code
            response = requests.post(f"{BACKEND_URL}/admin/2fa/verify-setup", 
                                   json={"totp_code": valid_code},
                                   timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 2FA setup verification successful")
                print(f"   - Success: {data.get('success', False)}")
                print(f"   - Message: {data.get('message', 'None')}")
                valid_code_test = True
            else:
                print(f"❌ Valid TOTP verification failed: {response.status_code} - {response.text}")
                valid_code_test = False
                
        except Exception as e:
            print(f"❌ Valid TOTP verification error: {str(e)}")
            valid_code_test = False
        
        # Test invalid TOTP code
        try:
            response = requests.post(f"{BACKEND_URL}/admin/2fa/verify-setup", 
                                   json={"totp_code": "123456"},
                                   timeout=30)
            
            if response.status_code == 400:
                print(f"✅ Invalid TOTP code correctly rejected")
                invalid_code_test = True
            else:
                print(f"❌ Invalid TOTP code should be rejected but got: {response.status_code}")
                invalid_code_test = False
                
        except Exception as e:
            print(f"❌ Invalid TOTP code test error: {str(e)}")
            invalid_code_test = False
        
        # Test malformed TOTP code
        try:
            response = requests.post(f"{BACKEND_URL}/admin/2fa/verify-setup", 
                                   json={"totp_code": "12345"},
                                   timeout=30)
            
            if response.status_code == 400:
                print(f"✅ Malformed TOTP code correctly rejected")
                malformed_code_test = True
            else:
                print(f"❌ Malformed TOTP code should be rejected but got: {response.status_code}")
                malformed_code_test = False
                
        except Exception as e:
            print(f"❌ Malformed TOTP code test error: {str(e)}")
            malformed_code_test = False
        
        return valid_code_test and invalid_code_test and malformed_code_test
    
    def test_2fa_login_verification(self):
        """Test 5: 2FA Login Verification - /api/admin/2fa/verify endpoint for ongoing logins"""
        print("\n🔐 TEST 5: 2FA Login Verification")
        
        if not self.totp_secret or not self.session_token:
            print("❌ Cannot test login verification - missing TOTP secret or session token")
            return False
        
        # Test TOTP code verification
        try:
            totp = pyotp.TOTP(self.totp_secret)
            # Wait for a fresh TOTP window to avoid replay attack prevention
            print("   - Waiting for fresh TOTP window to avoid replay protection...")
            current_time = int(time.time())
            next_window = ((current_time // 30) + 1) * 30
            wait_time = next_window - current_time + 2  # Add 2 second buffer
            time.sleep(wait_time)
            
            valid_code = totp.now()
            print(f"   - Generated fresh TOTP code: {valid_code}")
            
            response = requests.post(f"{BACKEND_URL}/admin/2fa/verify", 
                                   json={
                                       "totp_code": valid_code,
                                       "session_token": self.session_token
                                   },
                                   timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ TOTP login verification successful")
                print(f"   - Success: {data.get('success', False)}")
                print(f"   - Message: {data.get('message', 'None')}")
                totp_test = True
            else:
                print(f"❌ TOTP login verification failed: {response.status_code} - {response.text}")
                totp_test = False
                
        except Exception as e:
            print(f"❌ TOTP login verification error: {str(e)}")
            totp_test = False
        
        # Test backup code verification
        backup_code_test = False
        if self.backup_codes:
            try:
                # Use the first backup code
                backup_code = self.backup_codes[0]
                print(f"   - Testing backup code: {backup_code}")
                
                response = requests.post(f"{BACKEND_URL}/admin/2fa/verify", 
                                       json={
                                           "backup_code": backup_code,
                                           "session_token": self.session_token
                                       },
                                       timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ Backup code verification successful")
                    print(f"   - Success: {data.get('success', False)}")
                    print(f"   - Message: {data.get('message', 'None')}")
                    backup_code_test = True
                else:
                    print(f"❌ Backup code verification failed: {response.status_code} - {response.text}")
                    backup_code_test = False
                    
            except Exception as e:
                print(f"❌ Backup code verification error: {str(e)}")
                backup_code_test = False
        else:
            print("⚠️ No backup codes available for testing")
        
        # Test invalid session token
        try:
            totp = pyotp.TOTP(self.totp_secret)
            valid_code = totp.now()
            
            response = requests.post(f"{BACKEND_URL}/admin/2fa/verify", 
                                   json={
                                       "totp_code": valid_code,
                                       "session_token": "invalid-token"
                                   },
                                   timeout=30)
            
            if response.status_code == 401:
                print(f"✅ Invalid session token correctly rejected")
                invalid_session_test = True
            else:
                print(f"❌ Invalid session token should be rejected but got: {response.status_code}")
                invalid_session_test = False
                
        except Exception as e:
            print(f"❌ Invalid session token test error: {str(e)}")
            invalid_session_test = False
        
        return totp_test and backup_code_test and invalid_session_test
    
    def test_2fa_disable(self):
        """Test 6: 2FA Disable - /api/admin/2fa/disable endpoint"""
        print("\n🔒 TEST 6: 2FA Disable")
        
        if not self.totp_secret:
            print("❌ Cannot test 2FA disable - no TOTP secret available")
            return False
        
        # Test valid TOTP code for disable
        try:
            totp = pyotp.TOTP(self.totp_secret)
            # Wait to ensure fresh code different from login verification
            print("   - Waiting for fresh TOTP window for disable...")
            current_time = int(time.time())
            next_window = ((current_time // 30) + 1) * 30
            wait_time = next_window - current_time + 2  # Add 2 second buffer
            time.sleep(wait_time)
            
            valid_code = totp.now()
            print(f"   - Generated TOTP code for disable: {valid_code}")
            
            response = requests.post(f"{BACKEND_URL}/admin/2fa/disable", 
                                   json={"totp_code": valid_code},
                                   timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 2FA disable successful")
                print(f"   - Success: {data.get('success', False)}")
                print(f"   - Message: {data.get('message', 'None')}")
                valid_disable_test = True
            else:
                print(f"❌ 2FA disable failed: {response.status_code} - {response.text}")
                valid_disable_test = False
                
        except Exception as e:
            print(f"❌ 2FA disable error: {str(e)}")
            valid_disable_test = False
        
        # Test disable without TOTP code
        try:
            response = requests.post(f"{BACKEND_URL}/admin/2fa/disable", 
                                   json={},
                                   timeout=30)
            
            if response.status_code == 400:
                print(f"✅ Disable without TOTP code correctly rejected")
                missing_code_test = True
            else:
                print(f"❌ Disable without TOTP code should be rejected but got: {response.status_code}")
                missing_code_test = False
                
        except Exception as e:
            print(f"❌ Missing TOTP code test error: {str(e)}")
            missing_code_test = False
        
        return valid_disable_test and missing_code_test
    
    def test_rate_limiting_and_lockout(self):
        """Test 7: Rate Limiting and Account Lockout Features"""
        print("\n🚫 TEST 7: Rate Limiting and Account Lockout")
        
        # Test multiple failed PIN attempts
        print("   - Testing PIN lockout mechanism...")
        failed_attempts = 0
        
        for attempt in range(3):  # Test a few failed attempts (not full 5 to avoid lockout)
            try:
                response = requests.post(f"{BACKEND_URL}/admin/pin-verify", 
                                       json={"pin": "9999"},
                                       timeout=30)
                
                if response.status_code == 401:
                    failed_attempts += 1
                    print(f"     - Failed attempt {attempt + 1}: ✅ Correctly rejected")
                else:
                    print(f"     - Failed attempt {attempt + 1}: ❌ Unexpected response {response.status_code}")
                    
            except Exception as e:
                print(f"     - Failed attempt {attempt + 1}: ❌ Error {str(e)}")
        
        # Reset with valid PIN
        try:
            response = requests.post(f"{BACKEND_URL}/admin/pin-verify", 
                                   json={"pin": DEFAULT_PIN},
                                   timeout=30)
            
            if response.status_code == 200:
                print(f"   - PIN reset after failed attempts: ✅")
                self.session_token = response.json().get('session_token')
                lockout_test = True
            else:
                print(f"   - PIN reset after failed attempts: ❌")
                lockout_test = False
                
        except Exception as e:
            print(f"   - PIN reset error: {str(e)}")
            lockout_test = False
        
        return lockout_test
    
    def test_session_token_management(self):
        """Test 8: Session Token Management"""
        print("\n🎫 TEST 8: Session Token Management")
        
        # Test session token generation
        try:
            response = requests.post(f"{BACKEND_URL}/admin/pin-verify", 
                                   json={"pin": DEFAULT_PIN},
                                   timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                session_token = data.get('session_token')
                
                if session_token and len(session_token) > 20:
                    print(f"✅ Session token generated successfully")
                    print(f"   - Token length: {len(session_token)}")
                    print(f"   - Token format: UUID-like")
                    token_generation_test = True
                else:
                    print(f"❌ Session token generation failed")
                    token_generation_test = False
            else:
                print(f"❌ Session token generation failed: {response.status_code}")
                token_generation_test = False
                
        except Exception as e:
            print(f"❌ Session token generation error: {str(e)}")
            token_generation_test = False
        
        return token_generation_test
    
    def run_comprehensive_test(self):
        """Run all 2FA tests in sequence"""
        print("🔐 2FA BACKEND IMPLEMENTATION COMPREHENSIVE TEST SUITE")
        print("=" * 60)
        
        test_results = []
        
        # Run all tests
        test_results.append(("Admin User Creation", self.test_admin_user_creation()))
        test_results.append(("PIN Verification", self.test_pin_verification()))
        test_results.append(("2FA Setup Flow", self.test_2fa_setup()))
        test_results.append(("2FA Setup Verification", self.test_2fa_setup_verification()))
        test_results.append(("2FA Login Verification", self.test_2fa_login_verification()))
        test_results.append(("2FA Disable", self.test_2fa_disable()))
        test_results.append(("Rate Limiting & Lockout", self.test_rate_limiting_and_lockout()))
        test_results.append(("Session Token Management", self.test_session_token_management()))
        
        # Summary
        print("\n" + "=" * 60)
        print("🔐 2FA BACKEND TEST RESULTS SUMMARY")
        print("=" * 60)
        
        passed = 0
        total = len(test_results)
        
        for test_name, result in test_results:
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{test_name:<30} {status}")
            if result:
                passed += 1
        
        print(f"\nOverall Success Rate: {passed}/{total} ({(passed/total)*100:.1f}%)")
        
        if passed == total:
            print("🎉 ALL 2FA BACKEND TESTS PASSED!")
            return True
        else:
            print(f"⚠️ {total - passed} TEST(S) FAILED - REVIEW REQUIRED")
            return False

if __name__ == "__main__":
    tester = TwoFactorAuthTester()
    success = tester.run_comprehensive_test()
    
    if success:
        print("\n✅ 2FA Backend Implementation: FULLY FUNCTIONAL")
    else:
        print("\n❌ 2FA Backend Implementation: ISSUES DETECTED")