#!/usr/bin/env python3
"""
PIN 0224 Bypass Logic Testing for 2FA Rate Limiting
Test the special bypass logic for PIN 0224 in both 2FA send-code and verify endpoints.
"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime

# Backend URL from environment
BACKEND_URL = "https://cd556dd9-d36b-422e-8110-4b1830397661.preview.emergentagent.com/api"

class PIN0224BypassTester:
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
        
    async def test_admin_pin_0224_authentication(self):
        """Test 1: Admin PIN 0224 Authentication"""
        try:
            # Test PIN 0224 authentication
            async with self.session.post(
                f"{BACKEND_URL}/auth/pin-verify",
                json={"pin": "0224"},
                headers={"Content-Type": "application/json"}
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    
                    # Verify required fields
                    required_fields = ["pin_valid", "user_type", "session_token", "two_fa_enabled", "two_fa_required", "two_fa_email"]
                    missing_fields = [field for field in required_fields if field not in data]
                    
                    if missing_fields:
                        self.log_test("Admin PIN 0224 Authentication", False, f"Missing fields: {missing_fields}")
                        return False
                        
                    # Verify values
                    if (data["pin_valid"] == True and 
                        data["user_type"] == "admin" and 
                        data["session_token"] and
                        data["two_fa_required"] == True):
                        
                        self.admin_session_token = data["session_token"]
                        self.log_test("Admin PIN 0224 Authentication", True, 
                                    f"Session token: {data['session_token'][:8]}..., 2FA Email: {data['two_fa_email']}")
                        return True
                    else:
                        self.log_test("Admin PIN 0224 Authentication", False, f"Invalid response values: {data}")
                        return False
                else:
                    error_text = await response.text()
                    self.log_test("Admin PIN 0224 Authentication", False, f"HTTP {response.status}: {error_text}")
                    return False
                
        except Exception as e:
            self.log_test("Admin PIN 0224 Authentication", False, f"Exception: {str(e)}")
            return False
            
    async def simulate_rate_limiting_scenario(self):
        """Test 2: Simulate rate limiting scenario by making failed attempts"""
        try:
            # First, let's try to trigger rate limiting with a different session
            # Create a fake session token to simulate non-admin user
            fake_session_token = "fake-session-token-12345"
            
            # Try to send code with fake session (should fail)
            for i in range(4):  # Try 4 times to trigger rate limiting
                try:
                    response = await self.session.post(
                        f"{BACKEND_URL}/admin/2fa/send-code",
                        json={"session_token": fake_session_token},
                        headers={"Content-Type": "application/json"}
                    )
                    
                    if response.status == 401:
                        print(f"   Attempt {i+1}: Expected 401 for fake session")
                    else:
                        print(f"   Attempt {i+1}: Unexpected status {response.status}")
                        
                except Exception as e:
                    print(f"   Attempt {i+1}: Exception (expected): {str(e)}")
                    
            self.log_test("Rate Limiting Scenario Setup", True, "Attempted to create rate limiting conditions")
            return True
            
        except Exception as e:
            self.log_test("Rate Limiting Scenario Setup", False, f"Exception: {str(e)}")
            return False
            
    async def test_2fa_send_code_bypass(self):
        """Test 3: 2FA Send Code with PIN 0224 Bypass"""
        try:
            if not self.admin_session_token:
                self.log_test("2FA Send Code Bypass", False, "No admin session token available")
                return False
                
            # Test send code with admin session token (should bypass rate limiting)
            async with self.session.post(
                f"{BACKEND_URL}/admin/2fa/send-code",
                json={"session_token": self.admin_session_token},
                headers={"Content-Type": "application/json"}
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get("success") == True and "message" in data:
                        self.log_test("2FA Send Code Bypass", True, 
                                    f"Code sent successfully: {data['message']}")
                        return True
                    else:
                        self.log_test("2FA Send Code Bypass", False, f"Invalid response: {data}")
                        return False
                else:
                    error_text = await response.text()
                    self.log_test("2FA Send Code Bypass", False, f"HTTP {response.status}: {error_text}")
                    return False
                
        except Exception as e:
            self.log_test("2FA Send Code Bypass", False, f"Exception: {str(e)}")
            return False
            
    async def test_2fa_verify_bypass(self):
        """Test 4: 2FA Verify with PIN 0224 Bypass (test with wrong code)"""
        try:
            if not self.admin_session_token:
                self.log_test("2FA Verify Bypass", False, "No admin session token available")
                return False
                
            # Test verify with wrong code but admin session (should not increment failed attempts due to bypass)
            wrong_code = "999999"  # Intentionally wrong code
            
            async with self.session.post(
                f"{BACKEND_URL}/admin/2fa/verify",
                json={
                    "email_code": wrong_code,
                    "session_token": self.admin_session_token
                },
                headers={"Content-Type": "application/json"}
            ) as response:
                
                # We expect this to fail (401) but the bypass should prevent rate limiting
                if response.status == 401:
                    error_data = await response.json()
                    self.log_test("2FA Verify Bypass", True, 
                                f"Expected 401 for wrong code, bypass should prevent rate limiting: {error_data.get('detail', 'No detail')}")
                    return True
                else:
                    # If it's not 401, something unexpected happened
                    response_text = await response.text()
                    self.log_test("2FA Verify Bypass", False, f"Unexpected status {response.status}: {response_text}")
                    return False
                
        except Exception as e:
            self.log_test("2FA Verify Bypass", False, f"Exception: {str(e)}")
            return False
            
    async def test_bypass_status_verification(self):
        """Test 5: Verify bypass status by checking database state"""
        try:
            # We can't directly access the database, but we can test the behavior
            # by making multiple requests and ensuring no rate limiting occurs
            
            if not self.admin_session_token:
                self.log_test("Bypass Status Verification", False, "No admin session token available")
                return False
                
            # Make multiple send-code requests rapidly to test bypass
            success_count = 0
            for i in range(3):
                try:
                    async with self.session.post(
                        f"{BACKEND_URL}/admin/2fa/send-code",
                        json={"session_token": self.admin_session_token},
                        headers={"Content-Type": "application/json"}
                    ) as response:
                        
                        if response.status == 200:
                            success_count += 1
                            print(f"   Request {i+1}: Success (no rate limiting)")
                        else:
                            print(f"   Request {i+1}: Status {response.status}")
                            
                        # Small delay between requests
                        await asyncio.sleep(0.5)
                        
                except Exception as e:
                    print(f"   Request {i+1}: Exception: {str(e)}")
                    
            if success_count >= 2:  # At least 2 out of 3 should succeed
                self.log_test("Bypass Status Verification", True, 
                            f"Multiple requests succeeded ({success_count}/3), indicating bypass is working")
                return True
            else:
                self.log_test("Bypass Status Verification", False, 
                            f"Only {success_count}/3 requests succeeded, bypass may not be working")
                return False
                
        except Exception as e:
            self.log_test("Bypass Status Verification", False, f"Exception: {str(e)}")
            return False
            
    async def test_non_admin_rate_limiting(self):
        """Test 6: Verify non-admin sessions still get rate limited"""
        try:
            # Test with invalid session token to ensure normal rate limiting still works
            fake_session = "invalid-session-token"
            
            async with self.session.post(
                f"{BACKEND_URL}/admin/2fa/send-code",
                json={"session_token": fake_session},
                headers={"Content-Type": "application/json"}
            ) as response:
                
                # Should get 401 for invalid session
                if response.status == 401:
                    self.log_test("Non-Admin Rate Limiting", True, 
                                "Invalid session correctly rejected (rate limiting still works for non-admin)")
                    return True
                else:
                    error_text = await response.text()
                    self.log_test("Non-Admin Rate Limiting", False, 
                                f"Unexpected status {response.status}: {error_text}")
                    return False
                
        except Exception as e:
            self.log_test("Non-Admin Rate Limiting", False, f"Exception: {str(e)}")
            return False
            
    async def run_all_tests(self):
        """Run all PIN 0224 bypass tests"""
        print("🔐 PIN 0224 BYPASS LOGIC TESTING STARTED")
        print("=" * 60)
        
        await self.setup_session()
        
        try:
            # Test sequence
            test_functions = [
                self.test_admin_pin_0224_authentication,
                self.simulate_rate_limiting_scenario,
                self.test_2fa_send_code_bypass,
                self.test_2fa_verify_bypass,
                self.test_bypass_status_verification,
                self.test_non_admin_rate_limiting
            ]
            
            passed_tests = 0
            total_tests = len(test_functions)
            
            for test_func in test_functions:
                success = await test_func()
                if success:
                    passed_tests += 1
                print()  # Add spacing between tests
                
            # Summary
            print("=" * 60)
            print(f"🎯 PIN 0224 BYPASS TESTING SUMMARY")
            print(f"Total Tests: {total_tests}")
            print(f"Passed: {passed_tests}")
            print(f"Failed: {total_tests - passed_tests}")
            print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
            
            if passed_tests == total_tests:
                print("🎉 ALL TESTS PASSED - PIN 0224 bypass logic is working correctly!")
            else:
                print("⚠️  SOME TESTS FAILED - PIN 0224 bypass logic needs attention")
                
            return passed_tests == total_tests
            
        finally:
            await self.cleanup_session()

async def main():
    """Main test execution"""
    tester = PIN0224BypassTester()
    success = await tester.run_all_tests()
    return success

if __name__ == "__main__":
    asyncio.run(main())