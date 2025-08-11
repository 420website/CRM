#!/usr/bin/env python3
"""
Email-Based 2FA Backend Testing Suite
=====================================

Comprehensive testing of the newly implemented email-based 2FA system backend endpoints.
Tests the complete flow: PIN entry → Email setup → Code sending → Code verification

Test Coverage:
1. POST /api/admin/pin-verify - Returns two_fa_email field in response
2. POST /api/admin/2fa/setup - Returns email setup requirement
3. POST /api/admin/2fa/set-email - Sets admin email and enables 2FA
4. POST /api/admin/2fa/send-code - Sends verification code to admin email
5. POST /api/admin/2fa/verify - Verifies email codes instead of TOTP codes
6. POST /api/admin/2fa/disable - Disables email-based 2FA

Focus Areas:
- API endpoint functionality and response format
- Email code generation and verification
- Session token handling
- Error handling for invalid codes/expired codes
- Database integration with admin_users collection
- Email sending functionality (mocked/simulated)
"""

import asyncio
import aiohttp
import json
import time
import os
from datetime import datetime, timedelta
import pytz

# Configuration
BACKEND_URL = "https://258401ff-ff29-421c-8498-4969ee7788f0.preview.emergentagent.com/api"
TEST_PIN = "0224"
TEST_EMAIL = "admin@test420platform.com"

class EmailTwoFactorTester:
    def __init__(self):
        self.session_token = None
        self.test_results = []
        self.admin_user_id = None
        
    async def log_result(self, test_name, success, details, response_time=None):
        """Log test result with details"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "success": success,
            "details": details,
            "response_time": f"{response_time:.3f}s" if response_time else "N/A",
            "timestamp": datetime.now().strftime("%H:%M:%S")
        }
        self.test_results.append(result)
        print(f"{status} {test_name}: {details}")
        if response_time:
            print(f"    Response time: {response_time:.3f}s")
        print()

    async def test_pin_verification_with_2fa_fields(self):
        """Test 1: PIN verification returns 2FA email field"""
        print("🔐 TEST 1: PIN Verification with 2FA Fields")
        print("=" * 60)
        
        try:
            start_time = time.time()
            
            async with aiohttp.ClientSession() as session:
                # Test PIN verification
                pin_data = {"pin": TEST_PIN}
                
                async with session.post(f"{BACKEND_URL}/admin/pin-verify", 
                                       json=pin_data) as response:
                    response_time = time.time() - start_time
                    
                    if response.status == 200:
                        data = await response.json()
                        
                        # Store session token for later tests
                        self.session_token = data.get("session_token")
                        
                        # Verify response structure
                        required_fields = ["pin_valid", "two_fa_enabled", "two_fa_required", "two_fa_email", "session_token"]
                        missing_fields = [field for field in required_fields if field not in data]
                        
                        if missing_fields:
                            await self.log_result(
                                "PIN Verification Response Structure",
                                False,
                                f"Missing fields: {missing_fields}",
                                response_time
                            )
                        else:
                            await self.log_result(
                                "PIN Verification Response Structure",
                                True,
                                f"All required fields present: {list(data.keys())}",
                                response_time
                            )
                            
                            # Check specific field values
                            if data.get("pin_valid") == True:
                                await self.log_result(
                                    "PIN Validation",
                                    True,
                                    f"PIN '{TEST_PIN}' verified successfully",
                                    response_time
                                )
                            else:
                                await self.log_result(
                                    "PIN Validation",
                                    False,
                                    f"PIN validation failed: {data}",
                                    response_time
                                )
                            
                            # Check session token generation
                            if self.session_token and len(self.session_token) > 30:
                                await self.log_result(
                                    "Session Token Generation",
                                    True,
                                    f"Session token generated: {self.session_token[:8]}...{self.session_token[-8:]} (length: {len(self.session_token)})",
                                    response_time
                                )
                            else:
                                await self.log_result(
                                    "Session Token Generation",
                                    False,
                                    f"Invalid session token: {self.session_token}",
                                    response_time
                                )
                    else:
                        error_text = await response.text()
                        await self.log_result(
                            "PIN Verification API",
                            False,
                            f"HTTP {response.status}: {error_text}",
                            response_time
                        )
                        
        except Exception as e:
            await self.log_result(
                "PIN Verification Exception",
                False,
                f"Exception occurred: {str(e)}",
                time.time() - start_time
            )

    async def test_2fa_setup_endpoint(self):
        """Test 2: 2FA Setup endpoint returns email setup requirement"""
        print("📧 TEST 2: 2FA Setup Endpoint")
        print("=" * 60)
        
        try:
            start_time = time.time()
            
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{BACKEND_URL}/admin/2fa/setup") as response:
                    response_time = time.time() - start_time
                    
                    if response.status == 200:
                        data = await response.json()
                        
                        # Check response structure
                        expected_fields = ["setup_required", "email_address", "message"]
                        missing_fields = [field for field in expected_fields if field not in data]
                        
                        if missing_fields:
                            await self.log_result(
                                "2FA Setup Response Structure",
                                False,
                                f"Missing fields: {missing_fields}",
                                response_time
                            )
                        else:
                            await self.log_result(
                                "2FA Setup Response Structure",
                                True,
                                f"All expected fields present: {list(data.keys())}",
                                response_time
                            )
                            
                            # Check setup_required flag
                            if data.get("setup_required") == True:
                                await self.log_result(
                                    "2FA Setup Required Flag",
                                    True,
                                    "Setup required flag correctly set to True",
                                    response_time
                                )
                            else:
                                await self.log_result(
                                    "2FA Setup Required Flag",
                                    False,
                                    f"Setup required flag incorrect: {data.get('setup_required')}",
                                    response_time
                                )
                            
                            # Check message content
                            message = data.get("message", "")
                            if "email" in message.lower() and "authentication" in message.lower():
                                await self.log_result(
                                    "2FA Setup Message Content",
                                    True,
                                    f"Message contains expected content: '{message}'",
                                    response_time
                                )
                            else:
                                await self.log_result(
                                    "2FA Setup Message Content",
                                    False,
                                    f"Message content unexpected: '{message}'",
                                    response_time
                                )
                    else:
                        error_text = await response.text()
                        await self.log_result(
                            "2FA Setup API",
                            False,
                            f"HTTP {response.status}: {error_text}",
                            response_time
                        )
                        
        except Exception as e:
            await self.log_result(
                "2FA Setup Exception",
                False,
                f"Exception occurred: {str(e)}",
                time.time() - start_time
            )

    async def test_set_2fa_email(self):
        """Test 3: Set 2FA email and enable email-based 2FA"""
        print("📮 TEST 3: Set 2FA Email")
        print("=" * 60)
        
        try:
            start_time = time.time()
            
            async with aiohttp.ClientSession() as session:
                # Test setting 2FA email
                email_data = {"email": TEST_EMAIL}
                
                async with session.post(f"{BACKEND_URL}/admin/2fa/set-email", 
                                       json=email_data) as response:
                    response_time = time.time() - start_time
                    
                    if response.status == 200:
                        data = await response.json()
                        
                        # Check success response
                        if data.get("success") == True:
                            await self.log_result(
                                "Set 2FA Email Success",
                                True,
                                f"Email 2FA enabled successfully for {TEST_EMAIL}",
                                response_time
                            )
                            
                            # Check message content
                            message = data.get("message", "")
                            if "enabled" in message.lower() and "successfully" in message.lower():
                                await self.log_result(
                                    "Set 2FA Email Message",
                                    True,
                                    f"Success message: '{message}'",
                                    response_time
                                )
                            else:
                                await self.log_result(
                                    "Set 2FA Email Message",
                                    False,
                                    f"Unexpected message: '{message}'",
                                    response_time
                                )
                        else:
                            await self.log_result(
                                "Set 2FA Email Success",
                                False,
                                f"Success flag not True: {data}",
                                response_time
                            )
                    else:
                        error_text = await response.text()
                        await self.log_result(
                            "Set 2FA Email API",
                            False,
                            f"HTTP {response.status}: {error_text}",
                            response_time
                        )
                        
                # Test invalid email handling
                start_time = time.time()
                invalid_email_data = {"email": "invalid-email"}
                
                async with session.post(f"{BACKEND_URL}/admin/2fa/set-email", 
                                       json=invalid_email_data) as response:
                    response_time = time.time() - start_time
                    
                    if response.status == 400:
                        await self.log_result(
                            "Invalid Email Handling",
                            True,
                            "Invalid email correctly rejected with 400 status",
                            response_time
                        )
                    else:
                        await self.log_result(
                            "Invalid Email Handling",
                            False,
                            f"Invalid email not properly rejected: HTTP {response.status}",
                            response_time
                        )
                        
        except Exception as e:
            await self.log_result(
                "Set 2FA Email Exception",
                False,
                f"Exception occurred: {str(e)}",
                time.time() - start_time
            )

    async def test_send_verification_code(self):
        """Test 4: Send verification code to admin email"""
        print("📤 TEST 4: Send Verification Code")
        print("=" * 60)
        
        if not self.session_token:
            await self.log_result(
                "Send Code Prerequisites",
                False,
                "No session token available - cannot test send code",
                0
            )
            return
        
        try:
            start_time = time.time()
            
            async with aiohttp.ClientSession() as session:
                # Test sending verification code
                send_data = {"session_token": self.session_token}
                
                async with session.post(f"{BACKEND_URL}/admin/2fa/send-code", 
                                       json=send_data) as response:
                    response_time = time.time() - start_time
                    
                    if response.status == 200:
                        data = await response.json()
                        
                        # Check success response
                        if data.get("success") == True:
                            await self.log_result(
                                "Send Verification Code Success",
                                True,
                                f"Verification code sent successfully",
                                response_time
                            )
                            
                            # Check message content
                            message = data.get("message", "")
                            if TEST_EMAIL in message and "sent" in message.lower():
                                await self.log_result(
                                    "Send Code Message Content",
                                    True,
                                    f"Message contains email address: '{message}'",
                                    response_time
                                )
                            else:
                                await self.log_result(
                                    "Send Code Message Content",
                                    False,
                                    f"Message doesn't contain expected content: '{message}'",
                                    response_time
                                )
                            
                            # Check expiration time
                            expires_in = data.get("expires_in_minutes")
                            if expires_in == 10:
                                await self.log_result(
                                    "Code Expiration Time",
                                    True,
                                    f"Code expires in {expires_in} minutes as expected",
                                    response_time
                                )
                            else:
                                await self.log_result(
                                    "Code Expiration Time",
                                    False,
                                    f"Unexpected expiration time: {expires_in} minutes",
                                    response_time
                                )
                        else:
                            await self.log_result(
                                "Send Verification Code Success",
                                False,
                                f"Success flag not True: {data}",
                                response_time
                            )
                    else:
                        error_text = await response.text()
                        await self.log_result(
                            "Send Verification Code API",
                            False,
                            f"HTTP {response.status}: {error_text}",
                            response_time
                        )
                        
                # Test invalid session token handling
                start_time = time.time()
                invalid_session_data = {"session_token": "invalid-token"}
                
                async with session.post(f"{BACKEND_URL}/admin/2fa/send-code", 
                                       json=invalid_session_data) as response:
                    response_time = time.time() - start_time
                    
                    if response.status == 401:
                        await self.log_result(
                            "Invalid Session Token Handling",
                            True,
                            "Invalid session token correctly rejected with 401 status",
                            response_time
                        )
                    else:
                        await self.log_result(
                            "Invalid Session Token Handling",
                            False,
                            f"Invalid session token not properly rejected: HTTP {response.status}",
                            response_time
                        )
                        
        except Exception as e:
            await self.log_result(
                "Send Verification Code Exception",
                False,
                f"Exception occurred: {str(e)}",
                time.time() - start_time
            )

    async def test_email_code_verification(self):
        """Test 5: Verify email codes (simulated since we can't access real email)"""
        print("🔍 TEST 5: Email Code Verification")
        print("=" * 60)
        
        if not self.session_token:
            await self.log_result(
                "Code Verification Prerequisites",
                False,
                "No session token available - cannot test code verification",
                0
            )
            return
        
        try:
            # Test invalid code handling
            start_time = time.time()
            
            async with aiohttp.ClientSession() as session:
                # Test with invalid code
                invalid_code_data = {
                    "email_code": "000000",
                    "session_token": self.session_token
                }
                
                async with session.post(f"{BACKEND_URL}/admin/2fa/verify", 
                                       json=invalid_code_data) as response:
                    response_time = time.time() - start_time
                    
                    if response.status == 401:
                        await self.log_result(
                            "Invalid Code Rejection",
                            True,
                            "Invalid verification code correctly rejected with 401 status",
                            response_time
                        )
                    elif response.status == 400:
                        error_data = await response.json()
                        error_detail = error_data.get("detail", "")
                        if "code" in error_detail.lower():
                            await self.log_result(
                                "Invalid Code Rejection",
                                True,
                                f"Invalid code properly handled: {error_detail}",
                                response_time
                            )
                        else:
                            await self.log_result(
                                "Invalid Code Rejection",
                                False,
                                f"Unexpected error message: {error_detail}",
                                response_time
                            )
                    else:
                        await self.log_result(
                            "Invalid Code Rejection",
                            False,
                            f"Invalid code not properly rejected: HTTP {response.status}",
                            response_time
                        )
                
                # Test missing session token
                start_time = time.time()
                missing_session_data = {"email_code": "123456"}
                
                async with session.post(f"{BACKEND_URL}/admin/2fa/verify", 
                                       json=missing_session_data) as response:
                    response_time = time.time() - start_time
                    
                    if response.status == 422:  # Pydantic validation error
                        await self.log_result(
                            "Missing Session Token Handling",
                            True,
                            "Missing session token correctly rejected with 422 status",
                            response_time
                        )
                    else:
                        await self.log_result(
                            "Missing Session Token Handling",
                            False,
                            f"Missing session token not properly handled: HTTP {response.status}",
                            response_time
                        )
                
                # Test invalid session token
                start_time = time.time()
                invalid_session_data = {
                    "email_code": "123456",
                    "session_token": "invalid-token"
                }
                
                async with session.post(f"{BACKEND_URL}/admin/2fa/verify", 
                                       json=invalid_session_data) as response:
                    response_time = time.time() - start_time
                    
                    if response.status == 401:
                        await self.log_result(
                            "Invalid Session in Verification",
                            True,
                            "Invalid session token in verification correctly rejected",
                            response_time
                        )
                    else:
                        await self.log_result(
                            "Invalid Session in Verification",
                            False,
                            f"Invalid session token not properly rejected: HTTP {response.status}",
                            response_time
                        )
                        
        except Exception as e:
            await self.log_result(
                "Email Code Verification Exception",
                False,
                f"Exception occurred: {str(e)}",
                time.time() - start_time
            )

    async def test_2fa_disable(self):
        """Test 6: Disable email-based 2FA"""
        print("🔒 TEST 6: Disable Email-Based 2FA")
        print("=" * 60)
        
        try:
            start_time = time.time()
            
            async with aiohttp.ClientSession() as session:
                # Test disable without email code
                async with session.post(f"{BACKEND_URL}/admin/2fa/disable", 
                                       json={}) as response:
                    response_time = time.time() - start_time
                    
                    if response.status == 400:
                        error_data = await response.json()
                        error_detail = error_data.get("detail", "")
                        if "code" in error_detail.lower() and "required" in error_detail.lower():
                            await self.log_result(
                                "Disable 2FA Security Check",
                                True,
                                f"Disable properly requires verification code: {error_detail}",
                                response_time
                            )
                        else:
                            await self.log_result(
                                "Disable 2FA Security Check",
                                False,
                                f"Unexpected error message: {error_detail}",
                                response_time
                            )
                    else:
                        await self.log_result(
                            "Disable 2FA Security Check",
                            False,
                            f"Disable without code not properly rejected: HTTP {response.status}",
                            response_time
                        )
                
                # Test disable with invalid code
                start_time = time.time()
                invalid_disable_data = {"email_code": "000000"}
                
                async with session.post(f"{BACKEND_URL}/admin/2fa/disable", 
                                       json=invalid_disable_data) as response:
                    response_time = time.time() - start_time
                    
                    if response.status in [400, 401]:
                        await self.log_result(
                            "Disable 2FA Invalid Code",
                            True,
                            f"Invalid code for disable properly rejected: HTTP {response.status}",
                            response_time
                        )
                    else:
                        await self.log_result(
                            "Disable 2FA Invalid Code",
                            False,
                            f"Invalid code for disable not properly rejected: HTTP {response.status}",
                            response_time
                        )
                        
        except Exception as e:
            await self.log_result(
                "Disable 2FA Exception",
                False,
                f"Exception occurred: {str(e)}",
                time.time() - start_time
            )

    async def test_database_integration(self):
        """Test 7: Database integration and data persistence"""
        print("🗄️ TEST 7: Database Integration")
        print("=" * 60)
        
        try:
            # Test that PIN verification still works after 2FA setup
            start_time = time.time()
            
            async with aiohttp.ClientSession() as session:
                pin_data = {"pin": TEST_PIN}
                
                async with session.post(f"{BACKEND_URL}/admin/pin-verify", 
                                       json=pin_data) as response:
                    response_time = time.time() - start_time
                    
                    if response.status == 200:
                        data = await response.json()
                        
                        # Check that 2FA is now enabled
                        if data.get("two_fa_enabled") == True:
                            await self.log_result(
                                "Database 2FA State Persistence",
                                True,
                                "2FA enabled state correctly persisted in database",
                                response_time
                            )
                        else:
                            await self.log_result(
                                "Database 2FA State Persistence",
                                False,
                                f"2FA enabled state not persisted: {data.get('two_fa_enabled')}",
                                response_time
                            )
                        
                        # Check that email is persisted
                        if data.get("two_fa_email") == TEST_EMAIL:
                            await self.log_result(
                                "Database Email Persistence",
                                True,
                                f"2FA email correctly persisted: {data.get('two_fa_email')}",
                                response_time
                            )
                        else:
                            await self.log_result(
                                "Database Email Persistence",
                                False,
                                f"2FA email not correctly persisted: {data.get('two_fa_email')}",
                                response_time
                            )
                    else:
                        error_text = await response.text()
                        await self.log_result(
                            "Database Integration Test",
                            False,
                            f"PIN verification failed: HTTP {response.status}: {error_text}",
                            response_time
                        )
                        
        except Exception as e:
            await self.log_result(
                "Database Integration Exception",
                False,
                f"Exception occurred: {str(e)}",
                time.time() - start_time
            )

    async def test_error_handling(self):
        """Test 8: Comprehensive error handling"""
        print("⚠️ TEST 8: Error Handling")
        print("=" * 60)
        
        try:
            async with aiohttp.ClientSession() as session:
                # Test 1: Missing PIN
                start_time = time.time()
                async with session.post(f"{BACKEND_URL}/admin/pin-verify", 
                                       json={}) as response:
                    response_time = time.time() - start_time
                    
                    if response.status == 400:
                        await self.log_result(
                            "Missing PIN Error Handling",
                            True,
                            "Missing PIN correctly handled with 400 status",
                            response_time
                        )
                    else:
                        await self.log_result(
                            "Missing PIN Error Handling",
                            False,
                            f"Missing PIN not properly handled: HTTP {response.status}",
                            response_time
                        )
                
                # Test 2: Wrong PIN
                start_time = time.time()
                async with session.post(f"{BACKEND_URL}/admin/pin-verify", 
                                       json={"pin": "9999"}) as response:
                    response_time = time.time() - start_time
                    
                    if response.status == 401:
                        await self.log_result(
                            "Wrong PIN Error Handling",
                            True,
                            "Wrong PIN correctly rejected with 401 status",
                            response_time
                        )
                    else:
                        await self.log_result(
                            "Wrong PIN Error Handling",
                            False,
                            f"Wrong PIN not properly rejected: HTTP {response.status}",
                            response_time
                        )
                
                # Test 3: Send code without session
                start_time = time.time()
                async with session.post(f"{BACKEND_URL}/admin/2fa/send-code", 
                                       json={}) as response:
                    response_time = time.time() - start_time
                    
                    if response.status == 400:
                        await self.log_result(
                            "Send Code Without Session Error",
                            True,
                            "Send code without session correctly handled with 400 status",
                            response_time
                        )
                    else:
                        await self.log_result(
                            "Send Code Without Session Error",
                            False,
                            f"Send code without session not properly handled: HTTP {response.status}",
                            response_time
                        )
                        
        except Exception as e:
            await self.log_result(
                "Error Handling Exception",
                False,
                f"Exception occurred: {str(e)}",
                time.time() - start_time
            )

    async def run_comprehensive_test(self):
        """Run all email-based 2FA tests"""
        print("🔐 EMAIL-BASED 2FA BACKEND TESTING SUITE")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Email: {TEST_EMAIL}")
        print(f"Test PIN: {TEST_PIN}")
        print(f"Test Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        print()
        
        # Run all tests in sequence
        await self.test_pin_verification_with_2fa_fields()
        await self.test_2fa_setup_endpoint()
        await self.test_set_2fa_email()
        await self.test_send_verification_code()
        await self.test_email_code_verification()
        await self.test_2fa_disable()
        await self.test_database_integration()
        await self.test_error_handling()
        
        # Generate summary
        print("📊 EMAIL-BASED 2FA TESTING SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        # Show failed tests
        if failed_tests > 0:
            print("❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  • {result['test']}: {result['details']}")
            print()
        
        # Show passed tests
        print("✅ PASSED TESTS:")
        for result in self.test_results:
            if result["success"]:
                print(f"  • {result['test']}: {result['details']}")
        print()
        
        # Overall assessment
        if success_rate >= 90:
            print("🎉 OVERALL ASSESSMENT: EXCELLENT - Email-based 2FA system is working very well")
        elif success_rate >= 75:
            print("✅ OVERALL ASSESSMENT: GOOD - Email-based 2FA system is mostly functional")
        elif success_rate >= 50:
            print("⚠️ OVERALL ASSESSMENT: NEEDS IMPROVEMENT - Email-based 2FA system has significant issues")
        else:
            print("❌ OVERALL ASSESSMENT: CRITICAL ISSUES - Email-based 2FA system requires major fixes")
        
        print("=" * 80)
        print(f"Test Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return success_rate >= 75

async def main():
    """Main test execution"""
    tester = EmailTwoFactorTester()
    success = await tester.run_comprehensive_test()
    return success

if __name__ == "__main__":
    asyncio.run(main())