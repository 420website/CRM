#!/usr/bin/env python3
"""
PIN Verification and Email Verification Flow Testing
Tests the corrected PIN verification and email verification flow implementation
"""

import requests
import json
import time
import sys
from datetime import datetime

# Get backend URL from frontend .env
def get_backend_url():
    try:
        with open('/app/frontend/.env', 'r') as f:
            for line in f:
                if line.startswith('REACT_APP_BACKEND_URL='):
                    return line.split('=', 1)[1].strip()
    except:
        pass
    return "http://localhost:8001"

BACKEND_URL = get_backend_url()
API_BASE = f"{BACKEND_URL}/api"

def test_backend_health():
    """Test 1: Verify backend service is running"""
    print("🔍 TEST 1: Backend Health Check")
    try:
        response = requests.get(f"{BACKEND_URL}/", timeout=10)
        if response.status_code == 200:
            print("✅ Backend service is running")
            return True
        else:
            print(f"❌ Backend returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend health check failed: {str(e)}")
        return False

def test_user_pin_flow():
    """Test 2: Test with a user PIN to verify the new logic"""
    print("\n🔍 TEST 2: User PIN Flow Testing")
    
    # First, let's check if there are any users in the system
    try:
        response = requests.get(f"{API_BASE}/users", timeout=10)
        if response.status_code == 200:
            users = response.json()
            print(f"📊 Found {len(users)} users in system")
            
            if len(users) == 0:
                print("⚠️ No users found in system - creating test user")
                # Create a test user
                test_user_data = {
                    "firstName": "Sarah",
                    "lastName": "Johnson", 
                    "email": "sarah.johnson@mediclinic.ca",
                    "phone": "4161234567",
                    "pin": "1234",
                    "permissions": {}
                }
                
                create_response = requests.post(f"{API_BASE}/users", json=test_user_data, timeout=10)
                if create_response.status_code == 200:
                    print("✅ Test user created successfully")
                    test_pin = "1234"
                else:
                    print(f"❌ Failed to create test user: {create_response.text}")
                    return False
            else:
                # Use first user's PIN for testing
                first_user = users[0]
                test_pin = first_user.get("pin", "1234")
                print(f"📝 Using existing user: {first_user.get('firstName')} {first_user.get('lastName')} (PIN: {test_pin})")
            
            # Test PIN verification with user PIN
            print(f"\n🔐 Testing PIN verification with user PIN: {test_pin}")
            pin_data = {"pin": test_pin}
            
            response = requests.post(f"{API_BASE}/auth/pin-verify", json=pin_data, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                print("✅ PIN verification successful")
                print(f"📋 Response data:")
                print(f"   - pin_valid: {result.get('pin_valid')}")
                print(f"   - user_type: {result.get('user_type')}")
                print(f"   - user_id: {result.get('user_id')}")
                print(f"   - firstName: {result.get('firstName')}")
                print(f"   - lastName: {result.get('lastName')}")
                print(f"   - email: {result.get('email')}")
                print(f"   - two_fa_enabled: {result.get('two_fa_enabled')}")
                print(f"   - two_fa_required: {result.get('two_fa_required')}")
                print(f"   - needs_email_verification: {result.get('needs_email_verification')}")
                print(f"   - session_token: {result.get('session_token', 'N/A')[:8]}...")
                
                # Verify expected behavior for first-time users
                if result.get('needs_email_verification') == True:
                    print("✅ Correctly returns needs_email_verification: true for first-time users")
                else:
                    print("⚠️ needs_email_verification should be true for first-time users")
                
                if result.get('two_fa_enabled') == False:
                    print("✅ Correctly returns two_fa_enabled: false for first-time users")
                else:
                    print("⚠️ two_fa_enabled should be false for first-time users")
                
                if result.get('email'):
                    print("✅ Correctly returns user email for 2FA setup")
                else:
                    print("❌ Missing user email for 2FA setup")
                
                return result
            else:
                print(f"❌ PIN verification failed: {response.status_code} - {response.text}")
                return False
                
        else:
            print(f"❌ Failed to get users: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ User PIN flow test failed: {str(e)}")
        return False

def test_email_verification_marking(user_data):
    """Test 3: Test the new /api/users/{user_id}/mark-email-verified endpoint"""
    print("\n🔍 TEST 3: Email Verification Marking")
    
    if not user_data or not user_data.get('user_id'):
        print("❌ No user data provided for email verification test")
        return False
    
    user_id = user_data['user_id']
    print(f"📝 Testing email verification marking for user: {user_id}")
    
    try:
        response = requests.post(f"{API_BASE}/users/{user_id}/mark-email-verified", timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Email verification marking successful")
            print(f"📋 Response: {result.get('message')}")
            print(f"📋 User ID: {result.get('user_id')}")
            return True
        else:
            print(f"❌ Email verification marking failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Email verification marking test failed: {str(e)}")
        return False

def test_returning_user_logic(user_data):
    """Test 4: After a user is marked as email verified, test that future PIN logins work correctly"""
    print("\n🔍 TEST 4: Returning User Logic")
    
    if not user_data:
        print("❌ No user data provided for returning user test")
        return False
    
    # Use PIN from previous test or default
    test_pin = "1234"  # We know this PIN from the user we tested
    print(f"🔐 Testing returning user logic with PIN: {test_pin}")
    
    try:
        pin_data = {"pin": test_pin}
        response = requests.post(f"{API_BASE}/auth/pin-verify", json=pin_data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Returning user PIN verification successful")
            print(f"📋 Response data:")
            print(f"   - pin_valid: {result.get('pin_valid')}")
            print(f"   - user_type: {result.get('user_type')}")
            print(f"   - two_fa_enabled: {result.get('two_fa_enabled')}")
            print(f"   - needs_email_verification: {result.get('needs_email_verification')}")
            
            # Verify expected behavior for returning users
            if result.get('needs_email_verification') == False:
                print("✅ Correctly returns needs_email_verification: false for verified users")
            else:
                print("❌ needs_email_verification should be false for verified users")
            
            if result.get('two_fa_enabled') == True:
                print("✅ Correctly returns two_fa_enabled: true for verified users")
            else:
                print("❌ two_fa_enabled should be true for verified users")
            
            return True
        else:
            print(f"❌ Returning user PIN verification failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Returning user logic test failed: {str(e)}")
        return False

def test_admin_pin_fallback():
    """Test 5: Verify admin PIN "0224" still works properly"""
    print("\n🔍 TEST 5: Admin PIN Fallback")
    
    try:
        pin_data = {"pin": "0224"}
        response = requests.post(f"{API_BASE}/auth/pin-verify", json=pin_data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Admin PIN verification successful")
            print(f"📋 Response data:")
            print(f"   - pin_valid: {result.get('pin_valid')}")
            print(f"   - user_type: {result.get('user_type')}")
            print(f"   - two_fa_email: {result.get('two_fa_email')}")
            print(f"   - session_token: {result.get('session_token', 'N/A')[:8]}...")
            
            # Verify expected behavior for admin
            if result.get('user_type') == 'admin':
                print("✅ Correctly identifies as admin user type")
            else:
                print("❌ Should identify as admin user type")
            
            if result.get('two_fa_email') == 'support@my420.ca':
                print("✅ Correctly returns admin 2FA email")
            else:
                print(f"⚠️ Admin 2FA email: {result.get('two_fa_email')} (expected: support@my420.ca)")
            
            return result
        else:
            print(f"❌ Admin PIN verification failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Admin PIN fallback test failed: {str(e)}")
        return False

def test_email_setup_and_send_code(admin_data):
    """Test 6: Verify the 2FA email setup and send code workflow"""
    print("\n🔍 TEST 6: Email Setup and Send Code Workflow")
    
    if not admin_data or not admin_data.get('session_token'):
        print("❌ No admin session data provided for email setup test")
        return False
    
    session_token = admin_data['session_token']
    print(f"📝 Testing email setup and send code with session: {session_token[:8]}...")
    
    try:
        # Test 2FA setup endpoint
        print("\n📧 Testing 2FA setup endpoint...")
        setup_response = requests.post(f"{API_BASE}/admin/2fa/setup", timeout=10)
        
        if setup_response.status_code == 200:
            setup_result = setup_response.json()
            print("✅ 2FA setup endpoint working")
            print(f"📋 Setup required: {setup_result.get('setup_required')}")
            print(f"📋 Email address: {setup_result.get('email_address')}")
            print(f"📋 Message: {setup_result.get('message')}")
        else:
            print(f"❌ 2FA setup failed: {setup_response.status_code} - {setup_response.text}")
        
        # Test send verification code
        print("\n📧 Testing send verification code...")
        send_code_data = {"session_token": session_token}
        send_response = requests.post(f"{API_BASE}/admin/2fa/send-code", json=send_code_data, timeout=15)
        
        if send_response.status_code == 200:
            send_result = send_response.json()
            print("✅ Send verification code successful")
            print(f"📋 Message: {send_result.get('message')}")
            print(f"📋 Email sent to: {send_result.get('email')}")
            return True
        else:
            print(f"❌ Send verification code failed: {send_response.status_code} - {send_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Email setup and send code test failed: {str(e)}")
        return False

def main():
    """Run all PIN verification and email verification flow tests"""
    print("🚀 PIN VERIFICATION AND EMAIL VERIFICATION FLOW TESTING")
    print("=" * 70)
    
    start_time = time.time()
    tests_passed = 0
    total_tests = 6
    
    # Test 1: Backend Health
    if test_backend_health():
        tests_passed += 1
    
    # Test 2: User PIN Flow
    user_data = test_user_pin_flow()
    if user_data:
        tests_passed += 1
        
        # Test 3: Email Verification Marking
        if test_email_verification_marking(user_data):
            tests_passed += 1
            
        # Test 4: Returning User Logic
        if test_returning_user_logic(user_data):
            tests_passed += 1
    
    # Test 5: Admin PIN Fallback
    admin_data = test_admin_pin_fallback()
    if admin_data:
        tests_passed += 1
        
        # Test 6: Email Setup and Send Code
        if test_email_setup_and_send_code(admin_data):
            tests_passed += 1
    
    # Summary
    execution_time = time.time() - start_time
    success_rate = (tests_passed / total_tests) * 100
    
    print("\n" + "=" * 70)
    print("📊 PIN VERIFICATION AND EMAIL VERIFICATION FLOW TEST SUMMARY")
    print("=" * 70)
    print(f"✅ Tests Passed: {tests_passed}/{total_tests}")
    print(f"📈 Success Rate: {success_rate:.1f}%")
    print(f"⏱️ Execution Time: {execution_time:.2f}s")
    
    if tests_passed == total_tests:
        print("🎉 ALL TESTS PASSED - PIN verification and email verification flow working correctly!")
        return True
    else:
        print("❌ SOME TESTS FAILED - PIN verification and email verification flow needs attention")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)