#!/usr/bin/env python3
"""
Support Email 2FA Backend Testing
=================================

Test that the admin email is now correctly set to support@my420.ca when setting up 2FA.
This test verifies the specific changes mentioned in the review request:

1. POST /api/admin/2fa/set-email with email: "support@my420.ca" 
2. POST /api/admin/2fa/send-code to ensure codes are sent to support@my420.ca
3. Verify that the database now stores "support@my420.ca" as the two_fa_email for the admin user
4. Complete flow: PIN entry → automatic 2FA setup → send code to support@my420.ca
"""

import requests
import json
import time
import os
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://dfe9a1e1-7f3d-45aa-ad71-43a254e568c5.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

def test_support_email_2fa_setup():
    """Test that 2FA is now correctly configured to use support@my420.ca"""
    
    print("🔐 SUPPORT EMAIL 2FA BACKEND TESTING")
    print("=" * 60)
    print(f"Backend URL: {BACKEND_URL}")
    print(f"API Base: {API_BASE}")
    print()
    
    test_results = []
    session_token = None
    
    try:
        # Test 1: PIN Verification to get session token
        print("1️⃣ Testing PIN verification with 2FA fields...")
        pin_response = requests.post(f"{API_BASE}/admin/pin-verify", 
                                   json={"pin": "0224"}, 
                                   timeout=30)
        
        if pin_response.status_code == 200:
            pin_data = pin_response.json()
            session_token = pin_data.get("session_token")
            two_fa_email = pin_data.get("two_fa_email")
            
            print(f"   ✅ PIN verification successful")
            print(f"   📧 Current 2FA email: {two_fa_email}")
            print(f"   🎫 Session token: {session_token[:20]}..." if session_token else "   ❌ No session token")
            test_results.append(("PIN Verification", True, f"Session token obtained, current email: {two_fa_email}"))
        else:
            print(f"   ❌ PIN verification failed: {pin_response.status_code}")
            test_results.append(("PIN Verification", False, f"HTTP {pin_response.status_code}"))
            return test_results
        
        print()
        
        # Test 2: Set 2FA Email to support@my420.ca
        print("2️⃣ Testing POST /api/admin/2fa/set-email with support@my420.ca...")
        set_email_response = requests.post(f"{API_BASE}/admin/2fa/set-email", 
                                         json={"email": "support@my420.ca"}, 
                                         timeout=30)
        
        if set_email_response.status_code == 200:
            set_email_data = set_email_response.json()
            print(f"   ✅ Email set successfully: {set_email_data.get('message')}")
            test_results.append(("Set 2FA Email", True, "support@my420.ca set successfully"))
        else:
            print(f"   ❌ Failed to set email: {set_email_response.status_code}")
            print(f"   Response: {set_email_response.text}")
            test_results.append(("Set 2FA Email", False, f"HTTP {set_email_response.status_code}"))
        
        print()
        
        # Test 3: Verify PIN again to check updated email
        print("3️⃣ Verifying PIN again to check updated 2FA email...")
        pin_verify_response = requests.post(f"{API_BASE}/admin/pin-verify", 
                                          json={"pin": "0224"}, 
                                          timeout=30)
        
        if pin_verify_response.status_code == 200:
            updated_pin_data = pin_verify_response.json()
            updated_email = updated_pin_data.get("two_fa_email")
            session_token = updated_pin_data.get("session_token")  # Get fresh session token
            
            if updated_email == "support@my420.ca":
                print(f"   ✅ Database correctly stores support@my420.ca as two_fa_email")
                test_results.append(("Database Email Verification", True, "support@my420.ca stored correctly"))
            else:
                print(f"   ❌ Database shows incorrect email: {updated_email}")
                test_results.append(("Database Email Verification", False, f"Expected support@my420.ca, got {updated_email}"))
        else:
            print(f"   ❌ PIN verification failed: {pin_verify_response.status_code}")
            test_results.append(("Database Email Verification", False, f"HTTP {pin_verify_response.status_code}"))
        
        print()
        
        # Test 4: Send verification code to support@my420.ca
        print("4️⃣ Testing POST /api/admin/2fa/send-code to support@my420.ca...")
        if session_token:
            send_code_response = requests.post(f"{API_BASE}/admin/2fa/send-code", 
                                             json={"session_token": session_token}, 
                                             timeout=30)
            
            if send_code_response.status_code == 200:
                send_code_data = send_code_response.json()
                message = send_code_data.get("message", "")
                
                if "support@my420.ca" in message:
                    print(f"   ✅ Verification code sent to support@my420.ca")
                    print(f"   📧 Message: {message}")
                    test_results.append(("Send Code to Support Email", True, "Code sent to support@my420.ca"))
                else:
                    print(f"   ❌ Code sent to wrong email: {message}")
                    test_results.append(("Send Code to Support Email", False, f"Wrong email in message: {message}"))
            else:
                print(f"   ❌ Failed to send code: {send_code_response.status_code}")
                print(f"   Response: {send_code_response.text}")
                test_results.append(("Send Code to Support Email", False, f"HTTP {send_code_response.status_code}"))
        else:
            print("   ❌ No session token available for send code test")
            test_results.append(("Send Code to Support Email", False, "No session token"))
        
        print()
        
        # Test 5: Complete Flow Verification
        print("5️⃣ Testing complete flow: PIN → 2FA Setup → Send Code...")
        
        # Fresh PIN verification
        fresh_pin_response = requests.post(f"{API_BASE}/admin/pin-verify", 
                                         json={"pin": "0224"}, 
                                         timeout=30)
        
        if fresh_pin_response.status_code == 200:
            fresh_data = fresh_pin_response.json()
            fresh_token = fresh_data.get("session_token")
            fresh_email = fresh_data.get("two_fa_email")
            
            print(f"   ✅ PIN verification: success")
            print(f"   📧 2FA email: {fresh_email}")
            
            # Send code with fresh token
            if fresh_token and fresh_email == "support@my420.ca":
                final_send_response = requests.post(f"{API_BASE}/admin/2fa/send-code", 
                                                   json={"session_token": fresh_token}, 
                                                   timeout=30)
                
                if final_send_response.status_code == 200:
                    final_data = final_send_response.json()
                    final_message = final_data.get("message", "")
                    
                    if "support@my420.ca" in final_message:
                        print(f"   ✅ Complete flow successful: Code sent to support@my420.ca")
                        test_results.append(("Complete Flow", True, "PIN → 2FA → Send Code to support@my420.ca"))
                    else:
                        print(f"   ❌ Complete flow failed: Wrong email {final_message}")
                        test_results.append(("Complete Flow", False, f"Wrong email: {final_message}"))
                else:
                    print(f"   ❌ Complete flow failed: Send code error {final_send_response.status_code}")
                    test_results.append(("Complete Flow", False, f"Send code failed: {final_send_response.status_code}"))
            else:
                print(f"   ❌ Complete flow failed: Token or email issue")
                test_results.append(("Complete Flow", False, f"Token: {bool(fresh_token)}, Email: {fresh_email}"))
        else:
            print(f"   ❌ Complete flow failed: PIN verification error")
            test_results.append(("Complete Flow", False, f"PIN verification failed: {fresh_pin_response.status_code}"))
        
    except Exception as e:
        print(f"❌ Test execution error: {str(e)}")
        test_results.append(("Test Execution", False, str(e)))
    
    return test_results

def main():
    """Run the support email 2FA tests"""
    start_time = time.time()
    
    # Run tests
    results = test_support_email_2fa_setup()
    
    # Calculate results
    total_tests = len(results)
    passed_tests = sum(1 for _, passed, _ in results if passed)
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    
    # Print summary
    print()
    print("📊 SUPPORT EMAIL 2FA TEST RESULTS")
    print("=" * 60)
    
    for test_name, passed, details in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {test_name}: {details}")
    
    print()
    print(f"📈 SUMMARY: {passed_tests}/{total_tests} tests passed ({success_rate:.1f}% success rate)")
    print(f"⏱️  Total execution time: {time.time() - start_time:.2f}s")
    
    # Key findings
    print()
    print("🔍 KEY FINDINGS:")
    
    # Check if support@my420.ca is properly configured
    email_tests = [r for r in results if "Email" in r[0] or "Database" in r[0]]
    email_success = all(r[1] for r in email_tests)
    
    if email_success:
        print("   ✅ Admin email correctly set to support@my420.ca")
        print("   ✅ Database properly stores support@my420.ca as two_fa_email")
        print("   ✅ Verification codes are sent to support@my420.ca")
    else:
        print("   ❌ Issues found with support@my420.ca configuration")
    
    # Check complete flow
    flow_test = next((r for r in results if "Complete Flow" in r[0]), None)
    if flow_test and flow_test[1]:
        print("   ✅ Complete PIN → 2FA → Send Code flow working with support@my420.ca")
    else:
        print("   ❌ Complete flow has issues")
    
    print()
    print("🎯 CONCLUSION:")
    if success_rate >= 80:
        print("   ✅ Support email 2FA configuration is working correctly")
        print("   ✅ Admin email successfully changed from admin@test420platform.com to support@my420.ca")
    else:
        print("   ❌ Support email 2FA configuration needs attention")
    
    return success_rate >= 80

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)