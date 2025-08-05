#!/usr/bin/env python3
"""
Comprehensive PIN 0224 Rate Limiting Bypass Test
This test specifically verifies that PIN 0224 bypasses rate limiting that would normally occur.
"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime

# Backend URL from environment
BACKEND_URL = "https://dfe9a1e1-7f3d-45aa-ad71-43a254e568c5.preview.emergentagent.com/api"

class ComprehensiveBypassTester:
    def __init__(self):
        self.session = None
        self.admin_session_token = None
        self.test_results = []
        
    async def setup_session(self):
        """Setup HTTP session"""
        self.session = aiohttp.ClientSession()
        
    async def cleanup_session(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()
            
    def log_test(self, test_name, success, details):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details
        })
        
    async def get_admin_session_token(self):
        """Get admin session token using PIN 0224"""
        try:
            async with self.session.post(
                f"{BACKEND_URL}/auth/pin-verify",
                json={"pin": "0224"},
                headers={"Content-Type": "application/json"}
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    self.admin_session_token = data["session_token"]
                    return True
                return False
        except:
            return False
            
    async def test_rate_limiting_bypass_with_multiple_failed_verifications(self):
        """Test that PIN 0224 bypasses rate limiting even after multiple failed verification attempts"""
        try:
            if not await self.get_admin_session_token():
                self.log_test("Rate Limiting Bypass - Multiple Failed Verifications", False, "Could not get admin session token")
                return False
                
            # First, send a verification code
            async with self.session.post(
                f"{BACKEND_URL}/admin/2fa/send-code",
                json={"session_token": self.admin_session_token},
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status != 200:
                    self.log_test("Rate Limiting Bypass - Multiple Failed Verifications", False, "Could not send initial verification code")
                    return False
                    
            # Now make multiple failed verification attempts (normally this would trigger rate limiting)
            failed_attempts = 0
            for i in range(5):  # Try 5 failed attempts
                async with self.session.post(
                    f"{BACKEND_URL}/admin/2fa/verify",
                    json={
                        "email_code": "999999",  # Wrong code
                        "session_token": self.admin_session_token
                    },
                    headers={"Content-Type": "application/json"}
                ) as response:
                    if response.status == 401:
                        failed_attempts += 1
                        print(f"   Failed attempt {i+1}: Expected 401 (wrong code)")
                    else:
                        print(f"   Failed attempt {i+1}: Unexpected status {response.status}")
                        
            # After multiple failed attempts, try to send another code (should still work due to bypass)
            async with self.session.post(
                f"{BACKEND_URL}/admin/2fa/send-code",
                json={"session_token": self.admin_session_token},
                headers={"Content-Type": "application/json"}
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    self.log_test("Rate Limiting Bypass - Multiple Failed Verifications", True, 
                                f"After {failed_attempts} failed attempts, send-code still works: {data.get('message', 'Success')}")
                    return True
                elif response.status == 429:
                    self.log_test("Rate Limiting Bypass - Multiple Failed Verifications", False, 
                                f"Rate limiting triggered despite PIN 0224 bypass (HTTP 429)")
                    return False
                else:
                    error_text = await response.text()
                    self.log_test("Rate Limiting Bypass - Multiple Failed Verifications", False, 
                                f"Unexpected status {response.status}: {error_text}")
                    return False
                    
        except Exception as e:
            self.log_test("Rate Limiting Bypass - Multiple Failed Verifications", False, f"Exception: {str(e)}")
            return False
            
    async def test_rapid_send_code_requests_bypass(self):
        """Test that PIN 0224 allows rapid send-code requests without rate limiting"""
        try:
            if not await self.get_admin_session_token():
                self.log_test("Rapid Send Code Requests Bypass", False, "Could not get admin session token")
                return False
                
            # Make rapid send-code requests (normally this would trigger rate limiting)
            success_count = 0
            rate_limited_count = 0
            
            for i in range(6):  # Try 6 rapid requests
                async with self.session.post(
                    f"{BACKEND_URL}/admin/2fa/send-code",
                    json={"session_token": self.admin_session_token},
                    headers={"Content-Type": "application/json"}
                ) as response:
                    
                    if response.status == 200:
                        success_count += 1
                        print(f"   Request {i+1}: Success (200)")
                    elif response.status == 429:
                        rate_limited_count += 1
                        print(f"   Request {i+1}: Rate limited (429)")
                    else:
                        print(f"   Request {i+1}: Status {response.status}")
                        
                # Very small delay to simulate rapid requests
                await asyncio.sleep(0.1)
                
            # With PIN 0224 bypass, we should have mostly successful requests
            if success_count >= 4 and rate_limited_count == 0:
                self.log_test("Rapid Send Code Requests Bypass", True, 
                            f"Rapid requests successful: {success_count}/6 succeeded, {rate_limited_count} rate limited")
                return True
            else:
                self.log_test("Rapid Send Code Requests Bypass", False, 
                            f"Rate limiting may not be bypassed: {success_count}/6 succeeded, {rate_limited_count} rate limited")
                return False
                
        except Exception as e:
            self.log_test("Rapid Send Code Requests Bypass", False, f"Exception: {str(e)}")
            return False
            
    async def test_lockout_clearing_on_pin_0224_login(self):
        """Test that PIN 0224 login clears any existing lockouts"""
        try:
            # First, authenticate with PIN 0224 (this should clear any lockouts)
            async with self.session.post(
                f"{BACKEND_URL}/auth/pin-verify",
                json={"pin": "0224"},
                headers={"Content-Type": "application/json"}
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    session_token = data["session_token"]
                    
                    # Immediately try to send a code (should work if lockouts were cleared)
                    async with self.session.post(
                        f"{BACKEND_URL}/admin/2fa/send-code",
                        json={"session_token": session_token},
                        headers={"Content-Type": "application/json"}
                    ) as send_response:
                        
                        if send_response.status == 200:
                            send_data = await send_response.json()
                            self.log_test("Lockout Clearing on PIN 0224 Login", True, 
                                        f"PIN 0224 login cleared lockouts, send-code works: {send_data.get('message', 'Success')}")
                            return True
                        else:
                            error_text = await send_response.text()
                            self.log_test("Lockout Clearing on PIN 0224 Login", False, 
                                        f"Send-code failed after PIN 0224 login: {send_response.status} - {error_text}")
                            return False
                else:
                    error_text = await response.text()
                    self.log_test("Lockout Clearing on PIN 0224 Login", False, 
                                f"PIN 0224 authentication failed: {response.status} - {error_text}")
                    return False
                    
        except Exception as e:
            self.log_test("Lockout Clearing on PIN 0224 Login", False, f"Exception: {str(e)}")
            return False
            
    async def test_bypass_persistence_across_sessions(self):
        """Test that bypass works consistently across multiple PIN 0224 authentications"""
        try:
            success_count = 0
            
            # Test multiple PIN 0224 authentications and immediate 2FA operations
            for i in range(3):
                # Get new session token
                async with self.session.post(
                    f"{BACKEND_URL}/auth/pin-verify",
                    json={"pin": "0224"},
                    headers={"Content-Type": "application/json"}
                ) as auth_response:
                    
                    if auth_response.status == 200:
                        auth_data = await auth_response.json()
                        session_token = auth_data["session_token"]
                        
                        # Immediately test send-code with this session
                        async with self.session.post(
                            f"{BACKEND_URL}/admin/2fa/send-code",
                            json={"session_token": session_token},
                            headers={"Content-Type": "application/json"}
                        ) as send_response:
                            
                            if send_response.status == 200:
                                success_count += 1
                                print(f"   Session {i+1}: PIN 0224 auth + send-code successful")
                            else:
                                print(f"   Session {i+1}: Send-code failed with status {send_response.status}")
                    else:
                        print(f"   Session {i+1}: PIN 0224 auth failed with status {auth_response.status}")
                        
                await asyncio.sleep(0.5)  # Small delay between sessions
                
            if success_count == 3:
                self.log_test("Bypass Persistence Across Sessions", True, 
                            f"All {success_count}/3 PIN 0224 sessions worked with immediate 2FA operations")
                return True
            else:
                self.log_test("Bypass Persistence Across Sessions", False, 
                            f"Only {success_count}/3 PIN 0224 sessions worked properly")
                return False
                
        except Exception as e:
            self.log_test("Bypass Persistence Across Sessions", False, f"Exception: {str(e)}")
            return False
            
    async def run_comprehensive_tests(self):
        """Run all comprehensive bypass tests"""
        print("🔐 COMPREHENSIVE PIN 0224 BYPASS TESTING STARTED")
        print("=" * 70)
        
        await self.setup_session()
        
        try:
            # Test sequence
            test_functions = [
                self.test_rate_limiting_bypass_with_multiple_failed_verifications,
                self.test_rapid_send_code_requests_bypass,
                self.test_lockout_clearing_on_pin_0224_login,
                self.test_bypass_persistence_across_sessions
            ]
            
            passed_tests = 0
            total_tests = len(test_functions)
            
            for test_func in test_functions:
                success = await test_func()
                if success:
                    passed_tests += 1
                print()  # Add spacing between tests
                
            # Summary
            print("=" * 70)
            print(f"🎯 COMPREHENSIVE PIN 0224 BYPASS TESTING SUMMARY")
            print(f"Total Tests: {total_tests}")
            print(f"Passed: {passed_tests}")
            print(f"Failed: {total_tests - passed_tests}")
            print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
            
            if passed_tests == total_tests:
                print("🎉 ALL COMPREHENSIVE TESTS PASSED - PIN 0224 bypass logic is robust!")
            else:
                print("⚠️  SOME COMPREHENSIVE TESTS FAILED - PIN 0224 bypass needs attention")
                
            return passed_tests == total_tests
            
        finally:
            await self.cleanup_session()

async def main():
    """Main test execution"""
    tester = ComprehensiveBypassTester()
    success = await tester.run_comprehensive_tests()
    return success

if __name__ == "__main__":
    asyncio.run(main())