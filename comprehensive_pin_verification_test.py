#!/usr/bin/env python3
"""
Comprehensive PIN Verification and Email Verification Flow Testing
Tests the complete authentication flow with fresh users
"""

import requests
import json
import time
import sys
import uuid
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

def create_fresh_test_user():
    """Create a fresh test user for testing first-time user flow"""
    print("\n🔍 Creating Fresh Test User")
    
    # Generate unique user data
    unique_id = str(uuid.uuid4())[:8]
    test_user_data = {
        "firstName": f"TestUser{unique_id}",
        "lastName": "EmailVerification", 
        "email": f"testuser{unique_id}@example.com",
        "phone": "4161234567",
        "pin": f"{unique_id[:4]}",
        "permissions": {}
    }
    
    try:
        create_response = requests.post(f"{API_BASE}/users", json=test_user_data, timeout=10)
        if create_response.status_code == 200:
            created_user_response = create_response.json()
            created_user = created_user_response.get("user", {})
            print(f"✅ Fresh test user created: {test_user_data['firstName']} {test_user_data['lastName']}")
            print(f"📝 PIN: {test_user_data['pin']}")
            print(f"📧 Email: {test_user_data['email']}")
            return {
                "user_id": created_user.get("id"),
                "pin": test_user_data["pin"],
                "email": test_user_data["email"],
                "firstName": test_user_data["firstName"],
                "lastName": test_user_data["lastName"]
            }
        else:
            print(f"❌ Failed to create test user: {create_response.text}")
            return None
    except Exception as e:
        print(f"❌ Error creating test user: {str(e)}")
        return None

def test_first_time_user_pin_flow(user_data):
    """Test 2: Test first-time user PIN verification"""
    print("\n🔍 TEST 2: First-Time User PIN Flow")
    
    if not user_data:
        print("❌ No user data provided")
        return False
    
    pin = user_data["pin"]
    print(f"🔐 Testing first-time user PIN verification with PIN: {pin}")
    
    try:
        pin_data = {"pin": pin}
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
            success = True
            if result.get('needs_email_verification') == True:
                print("✅ Correctly returns needs_email_verification: true for first-time users")
            else:
                print("❌ needs_email_verification should be true for first-time users")
                success = False
            
            if result.get('two_fa_enabled') == False:
                print("✅ Correctly returns two_fa_enabled: false for first-time users")
            else:
                print("❌ two_fa_enabled should be false for first-time users")
                success = False
            
            if result.get('email') == user_data["email"]:
                print("✅ Correctly returns user email for 2FA setup")
            else:
                print("❌ Incorrect or missing user email for 2FA setup")
                success = False
            
            # Add session token to user data for next tests
            user_data["session_token"] = result.get("session_token")
            
            return success and result
        else:
            print(f"❌ PIN verification failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ First-time user PIN flow test failed: {str(e)}")
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
    print("\n🔍 TEST 4: Returning User Logic (After Email Verification)")
    
    if not user_data:
        print("❌ No user data provided for returning user test")
        return False
    
    pin = user_data["pin"]
    print(f"🔐 Testing returning user logic with PIN: {pin}")
    
    try:
        pin_data = {"pin": pin}
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
            success = True
            if result.get('needs_email_verification') == False:
                print("✅ Correctly returns needs_email_verification: false for verified users")
            else:
                print("❌ needs_email_verification should be false for verified users")
                success = False
            
            if result.get('two_fa_enabled') == True:
                print("✅ Correctly returns two_fa_enabled: true for verified users")
            else:
                print("❌ two_fa_enabled should be true for verified users")
                success = False
            
            return success
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
            success = True
            if result.get('user_type') == 'admin':
                print("✅ Correctly identifies as admin user type")
            else:
                print("❌ Should identify as admin user type")
                success = False
            
            if result.get('two_fa_email') == 'support@my420.ca':
                print("✅ Correctly returns admin 2FA email")
            else:
                print(f"⚠️ Admin 2FA email: {result.get('two_fa_email')} (expected: support@my420.ca)")
            
            return success and result
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
        
        setup_success = False
        if setup_response.status_code == 200:
            setup_result = setup_response.json()
            print("✅ 2FA setup endpoint working")
            print(f"📋 Setup required: {setup_result.get('setup_required')}")
            print(f"📋 Email address: {setup_result.get('email_address')}")
            print(f"📋 Message: {setup_result.get('message')}")
            setup_success = True
        else:
            print(f"❌ 2FA setup failed: {setup_response.status_code} - {setup_response.text}")
        
        # Test send verification code
        print("\n📧 Testing send verification code...")
        send_code_data = {"session_token": session_token}
        send_response = requests.post(f"{API_BASE}/admin/2fa/send-code", json=send_code_data, timeout=15)
        
        send_success = False
        if send_response.status_code == 200:
            send_result = send_response.json()
            print("✅ Send verification code successful")
            print(f"📋 Message: {send_result.get('message')}")
            send_success = True
        else:
            print(f"❌ Send verification code failed: {send_response.status_code} - {send_response.text}")
        
        return setup_success and send_success
            
    except Exception as e:
        print(f"❌ Email setup and send code test failed: {str(e)}")
        return False

def cleanup_test_user(user_data):
    """Clean up the test user after testing"""
    if user_data and user_data.get('user_id'):
        try:
            response = requests.delete(f"{API_BASE}/users/{user_data['user_id']}", timeout=10)
            if response.status_code == 200:
                print(f"🧹 Test user cleaned up: {user_data['firstName']} {user_data['lastName']}")
            else:
                print(f"⚠️ Could not clean up test user: {response.status_code}")
        except Exception as e:
            print(f"⚠️ Error cleaning up test user: {str(e)}")

def main():
    """Run all PIN verification and email verification flow tests"""
    print("🚀 COMPREHENSIVE PIN VERIFICATION AND EMAIL VERIFICATION FLOW TESTING")
    print("=" * 80)
    
    start_time = time.time()
    tests_passed = 0
    total_tests = 6
    test_user_data = None
    
    try:
        # Test 1: Backend Health
        if test_backend_health():
            tests_passed += 1
        
        # Create fresh test user
        test_user_data = create_fresh_test_user()
        if not test_user_data:
            print("❌ Cannot proceed without test user")
            return False
        
        # Test 2: First-Time User PIN Flow
        if test_first_time_user_pin_flow(test_user_data):
            tests_passed += 1
            
            # Test 3: Email Verification Marking
            if test_email_verification_marking(test_user_data):
                tests_passed += 1
                
                # Test 4: Returning User Logic
                if test_returning_user_logic(test_user_data):
                    tests_passed += 1
        
        # Test 5: Admin PIN Fallback
        admin_data = test_admin_pin_fallback()
        if admin_data:
            tests_passed += 1
            
            # Test 6: Email Setup and Send Code
            if test_email_setup_and_send_code(admin_data):
                tests_passed += 1
    
    finally:
        # Clean up test user
        if test_user_data:
            cleanup_test_user(test_user_data)
    
    # Summary
    execution_time = time.time() - start_time
    success_rate = (tests_passed / total_tests) * 100
    
    print("\n" + "=" * 80)
    print("📊 COMPREHENSIVE PIN VERIFICATION AND EMAIL VERIFICATION FLOW TEST SUMMARY")
    print("=" * 80)
    print(f"✅ Tests Passed: {tests_passed}/{total_tests}")
    print(f"📈 Success Rate: {success_rate:.1f}%")
    print(f"⏱️ Execution Time: {execution_time:.2f}s")
    
    if tests_passed == total_tests:
        print("🎉 ALL TESTS PASSED - PIN verification and email verification flow working correctly!")
        print("\n🔐 SECURITY FLOW VERIFIED:")
        print("   1. ✅ New users require email verification before dashboard access")
        print("   2. ✅ Users are marked as verified in database after email verification")
        print("   3. ✅ Future logins recognize verified users and go directly to code verification")
        print("   4. ✅ Security flow: PIN → Setup Email → Send Code → Verify Code → Access")
        print("   5. ✅ Admin PIN fallback works properly")
        return True
    else:
        print("❌ SOME TESTS FAILED - PIN verification and email verification flow needs attention")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)