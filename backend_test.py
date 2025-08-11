#!/usr/bin/env python3
"""
PIN Lockout Duration Fix Testing
Testing that the PIN lockout duration fix is working correctly and shows "4 hours and 20 minutes" 
lockout message when locked out, with actual lockout duration of 260 minutes (4 hours 20 minutes).
"""

import asyncio
import aiohttp
import json
import logging
from datetime import datetime, timedelta
import pytz
import time
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://258401ff-ff29-421c-8498-4969ee7788f0.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

class PINLockoutTester:
    def __init__(self):
        self.session = None
        self.test_results = []
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def log_test_result(self, test_name: str, success: bool, message: str, details: dict = None):
        """Log test result"""
        result = {
            'test': test_name,
            'success': success,
            'message': message,
            'details': details or {},
            'timestamp': datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        logger.info(f"{status}: {test_name} - {message}")
        if details:
            logger.info(f"   Details: {details}")
    
    async def test_backend_health(self):
        """Test 1: Backend Health Check"""
        try:
            async with self.session.get(f"{API_BASE}/admin-registrations-pending") as response:
                if response.status == 200:
                    data = await response.json()
                    count = len(data)
                    self.log_test_result(
                        "Backend Health Check",
                        True,
                        f"Backend accessible and responding correctly ({count} pending registrations)",
                        {"status_code": response.status, "pending_count": count}
                    )
                    return True
                else:
                    self.log_test_result(
                        "Backend Health Check",
                        False,
                        f"Backend returned status {response.status}",
                        {"status_code": response.status}
                    )
                    return False
        except Exception as e:
            self.log_test_result(
                "Backend Health Check",
                False,
                f"Backend connection failed: {str(e)}",
                {"error": str(e)}
            )
            return False
    
    async def clear_existing_lockouts(self):
        """Clear any existing lockouts using admin PIN bypass"""
        try:
            # Use admin PIN 0224 to clear lockouts
            payload = {"pin": "0224"}
            async with self.session.post(f"{API_BASE}/auth/pin-verify", json=payload) as response:
                if response.status == 200:
                    logger.info("🔑 Admin PIN used to clear existing lockouts")
                    return True
                else:
                    logger.warning(f"Admin PIN verification returned status {response.status}")
                    return False
        except Exception as e:
            logger.error(f"Error clearing lockouts: {str(e)}")
            return False
    
    async def test_pin_verification_working(self):
        """Test 2: PIN Verification System Working"""
        try:
            # Test with admin PIN 0224 (should work)
            payload = {"pin": "0224"}
            async with self.session.post(f"{API_BASE}/auth/pin-verify", json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    expected_fields = ['pin_valid', 'user_type', 'session_token', 'two_fa_enabled', 'two_fa_required', 'two_fa_email']
                    missing_fields = [field for field in expected_fields if field not in data]
                    
                    if not missing_fields and data.get('pin_valid') == True:
                        self.log_test_result(
                            "PIN Verification System Working",
                            True,
                            f"Admin PIN verification successful with all required fields",
                            {"response_fields": list(data.keys()), "user_type": data.get('user_type')}
                        )
                        return True
                    else:
                        self.log_test_result(
                            "PIN Verification System Working",
                            False,
                            f"PIN verification response missing fields or invalid",
                            {"missing_fields": missing_fields, "pin_valid": data.get('pin_valid')}
                        )
                        return False
                else:
                    self.log_test_result(
                        "PIN Verification System Working",
                        False,
                        f"PIN verification failed with status {response.status}",
                        {"status_code": response.status}
                    )
                    return False
        except Exception as e:
            self.log_test_result(
                "PIN Verification System Working",
                False,
                f"PIN verification test failed: {str(e)}",
                {"error": str(e)}
            )
            return False
    
    async def test_lockout_trigger_and_duration(self):
        """Test 3: Lockout Trigger and Duration Message"""
        try:
            # Clear any existing lockouts first
            await self.clear_existing_lockouts()
            
            # Make 3 failed PIN attempts to trigger lockout
            failed_attempts = 0
            for attempt in range(1, 4):
                payload = {"pin": "9999"}  # Invalid PIN
                async with self.session.post(f"{API_BASE}/auth/pin-verify", json=payload) as response:
                    if response.status == 401:
                        failed_attempts += 1
                        logger.info(f"Failed attempt #{attempt} recorded (status: 401)")
                    elif response.status == 423:
                        # Lockout triggered
                        error_data = await response.json()
                        error_message = error_data.get('detail', '')
                        
                        # Check if message contains "4 hours and 20 minutes"
                        if "4 hours and 20 minutes" in error_message:
                            self.log_test_result(
                                "Lockout Trigger and Duration Message",
                                True,
                                f"Lockout triggered after {failed_attempts} attempts with correct '4 hours and 20 minutes' message",
                                {"lockout_message": error_message, "failed_attempts": failed_attempts}
                            )
                            return True
                        else:
                            self.log_test_result(
                                "Lockout Trigger and Duration Message",
                                False,
                                f"Lockout triggered but message incorrect: '{error_message}'",
                                {"lockout_message": error_message, "expected": "4 hours and 20 minutes"}
                            )
                            return False
                    else:
                        logger.warning(f"Unexpected response status {response.status} on attempt {attempt}")
                
                # Small delay between attempts
                await asyncio.sleep(0.1)
            
            # If we get here, lockout wasn't triggered after 3 attempts
            self.log_test_result(
                "Lockout Trigger and Duration Message",
                False,
                f"Lockout not triggered after 3 failed attempts",
                {"failed_attempts": failed_attempts}
            )
            return False
            
        except Exception as e:
            self.log_test_result(
                "Lockout Trigger and Duration Message",
                False,
                f"Lockout trigger test failed: {str(e)}",
                {"error": str(e)}
            )
            return False
    
    async def test_lockout_duration_calculation(self):
        """Test 4: Actual Lockout Duration is 260 Minutes"""
        try:
            # Clear existing lockouts and trigger a new one
            await self.clear_existing_lockouts()
            
            # Trigger lockout with 3 failed attempts
            for attempt in range(3):
                payload = {"pin": "9999"}
                async with self.session.post(f"{API_BASE}/auth/pin-verify", json=payload) as response:
                    if response.status == 423:
                        break
                await asyncio.sleep(0.1)
            
            # Now test that we're locked out and get the remaining time
            payload = {"pin": "9999"}
            async with self.session.post(f"{API_BASE}/auth/pin-verify", json=payload) as response:
                if response.status == 423:
                    error_data = await response.json()
                    error_message = error_data.get('detail', '')
                    
                    # Extract hours and minutes from message
                    import re
                    time_match = re.search(r'(\d+) hours and (\d+) minutes', error_message)
                    if time_match:
                        hours = int(time_match.group(1))
                        minutes = int(time_match.group(2))
                        total_minutes = hours * 60 + minutes
                        
                        # Should be close to 260 minutes (allowing for small timing differences)
                        if 258 <= total_minutes <= 260:
                            self.log_test_result(
                                "Lockout Duration Calculation",
                                True,
                                f"Lockout duration is correct: {total_minutes} minutes (expected ~260)",
                                {"calculated_minutes": total_minutes, "hours": hours, "minutes": minutes, "message": error_message}
                            )
                            return True
                        else:
                            self.log_test_result(
                                "Lockout Duration Calculation",
                                False,
                                f"Lockout duration incorrect: {total_minutes} minutes (expected ~260)",
                                {"calculated_minutes": total_minutes, "expected": 260, "message": error_message}
                            )
                            return False
                    else:
                        self.log_test_result(
                            "Lockout Duration Calculation",
                            False,
                            f"Could not parse time from lockout message: '{error_message}'",
                            {"message": error_message}
                        )
                        return False
                else:
                    self.log_test_result(
                        "Lockout Duration Calculation",
                        False,
                        f"Expected lockout (423) but got status {response.status}",
                        {"status_code": response.status}
                    )
                    return False
                    
        except Exception as e:
            self.log_test_result(
                "Lockout Duration Calculation",
                False,
                f"Lockout duration test failed: {str(e)}",
                {"error": str(e)}
            )
            return False
    
    async def test_timezone_fix_working(self):
        """Test 5: Timezone Fix for Lockout Calculations"""
        try:
            # Clear existing lockouts and trigger a new one
            await self.clear_existing_lockouts()
            
            # Trigger lockout
            for attempt in range(3):
                payload = {"pin": "9999"}
                async with self.session.post(f"{API_BASE}/auth/pin-verify", json=payload) as response:
                    if response.status == 423:
                        break
                await asyncio.sleep(0.1)
            
            # Test multiple PIN attempts to ensure timezone comparison works consistently
            consistent_responses = 0
            for test_attempt in range(3):
                payload = {"pin": "9999"}
                async with self.session.post(f"{API_BASE}/auth/pin-verify", json=payload) as response:
                    if response.status == 423:
                        error_data = await response.json()
                        error_message = error_data.get('detail', '')
                        if "hours and" in error_message and "minutes" in error_message:
                            consistent_responses += 1
                await asyncio.sleep(0.1)
            
            if consistent_responses == 3:
                self.log_test_result(
                    "Timezone Fix Working",
                    True,
                    f"Timezone handling working correctly - all {consistent_responses} lockout responses consistent",
                    {"consistent_responses": consistent_responses, "total_tests": 3}
                )
                return True
            else:
                self.log_test_result(
                    "Timezone Fix Working",
                    False,
                    f"Timezone handling inconsistent - only {consistent_responses}/3 responses consistent",
                    {"consistent_responses": consistent_responses, "total_tests": 3}
                )
                return False
                
        except Exception as e:
            self.log_test_result(
                "Timezone Fix Working",
                False,
                f"Timezone fix test failed: {str(e)}",
                {"error": str(e)}
            )
            return False
    
    async def test_admin_bypass_functionality(self):
        """Test 6: Admin PIN Bypass Functionality"""
        try:
            # Ensure system is locked out first
            await self.clear_existing_lockouts()
            
            # Trigger lockout
            for attempt in range(3):
                payload = {"pin": "9999"}
                await self.session.post(f"{API_BASE}/auth/pin-verify", json=payload)
                await asyncio.sleep(0.1)
            
            # Verify lockout is active
            payload = {"pin": "9999"}
            async with self.session.post(f"{API_BASE}/auth/pin-verify", json=payload) as response:
                if response.status != 423:
                    self.log_test_result(
                        "Admin PIN Bypass Functionality",
                        False,
                        f"Could not establish lockout for bypass test (status: {response.status})",
                        {"status_code": response.status}
                    )
                    return False
            
            # Now test admin PIN bypass
            payload = {"pin": "0224"}
            async with self.session.post(f"{API_BASE}/auth/pin-verify", json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('pin_valid') == True and data.get('user_type') == 'admin':
                        # Verify lockout was cleared by testing with invalid PIN again
                        payload = {"pin": "9999"}
                        async with self.session.post(f"{API_BASE}/auth/pin-verify", json=payload) as response:
                            if response.status == 401:  # Should be 401 (invalid) not 423 (locked)
                                self.log_test_result(
                                    "Admin PIN Bypass Functionality",
                                    True,
                                    "Admin PIN 0224 successfully bypassed lockout and cleared system",
                                    {"admin_response": data, "post_bypass_status": response.status}
                                )
                                return True
                            else:
                                self.log_test_result(
                                    "Admin PIN Bypass Functionality",
                                    False,
                                    f"Admin PIN worked but lockout not cleared (status: {response.status})",
                                    {"post_bypass_status": response.status}
                                )
                                return False
                    else:
                        self.log_test_result(
                            "Admin PIN Bypass Functionality",
                            False,
                            f"Admin PIN response invalid",
                            {"response_data": data}
                        )
                        return False
                else:
                    self.log_test_result(
                        "Admin PIN Bypass Functionality",
                        False,
                        f"Admin PIN failed with status {response.status}",
                        {"status_code": response.status}
                    )
                    return False
                    
        except Exception as e:
            self.log_test_result(
                "Admin PIN Bypass Functionality",
                False,
                f"Admin bypass test failed: {str(e)}",
                {"error": str(e)}
            )
            return False
    
    async def test_no_regression_in_authentication(self):
        """Test 7: No Regressions in Authentication System"""
        try:
            # Clear any lockouts first
            await self.clear_existing_lockouts()
            
            # Test admin PIN authentication
            payload = {"pin": "0224"}
            async with self.session.post(f"{API_BASE}/auth/pin-verify", json=payload) as response:
                admin_working = response.status == 200
                admin_data = await response.json() if admin_working else {}
            
            # Test invalid PIN handling
            payload = {"pin": "9999"}
            async with self.session.post(f"{API_BASE}/auth/pin-verify", json=payload) as response:
                invalid_handled = response.status == 401
            
            # Test session token generation
            session_token_valid = bool(admin_data.get('session_token')) if admin_working else False
            
            # Test 2FA fields present
            twofa_fields = ['two_fa_enabled', 'two_fa_required', 'two_fa_email']
            twofa_present = all(field in admin_data for field in twofa_fields) if admin_working else False
            
            all_tests_passed = admin_working and invalid_handled and session_token_valid and twofa_present
            
            self.log_test_result(
                "No Regressions in Authentication System",
                all_tests_passed,
                f"Authentication system regression test: Admin PIN: {admin_working}, Invalid PIN handling: {invalid_handled}, Session tokens: {session_token_valid}, 2FA fields: {twofa_present}",
                {
                    "admin_pin_working": admin_working,
                    "invalid_pin_handled": invalid_handled,
                    "session_token_valid": session_token_valid,
                    "twofa_fields_present": twofa_present,
                    "admin_response": admin_data
                }
            )
            return all_tests_passed
            
        except Exception as e:
            self.log_test_result(
                "No Regressions in Authentication System",
                False,
                f"Authentication regression test failed: {str(e)}",
                {"error": str(e)}
            )
            return False
    
    async def run_all_tests(self):
        """Run all PIN lockout tests"""
        logger.info("🔐 Starting PIN Lockout Duration Fix Testing")
        logger.info(f"Backend URL: {BACKEND_URL}")
        
        test_functions = [
            self.test_backend_health,
            self.test_pin_verification_working,
            self.test_lockout_trigger_and_duration,
            self.test_lockout_duration_calculation,
            self.test_timezone_fix_working,
            self.test_admin_bypass_functionality,
            self.test_no_regression_in_authentication
        ]
        
        passed_tests = 0
        total_tests = len(test_functions)
        
        for test_func in test_functions:
            try:
                result = await test_func()
                if result:
                    passed_tests += 1
            except Exception as e:
                logger.error(f"Test {test_func.__name__} failed with exception: {str(e)}")
        
        # Final summary
        success_rate = (passed_tests / total_tests) * 100
        logger.info(f"\n{'='*80}")
        logger.info(f"🎯 PIN LOCKOUT DURATION FIX TESTING COMPLETED")
        logger.info(f"{'='*80}")
        logger.info(f"📊 RESULTS: {passed_tests}/{total_tests} tests passed ({success_rate:.1f}% success rate)")
        
        if passed_tests == total_tests:
            logger.info("🎉 ALL TESTS PASSED - PIN lockout duration fix working correctly!")
            logger.info("✅ System shows '4 hours and 20 minutes' lockout message")
            logger.info("✅ Lockout duration is actually 260 minutes (4 hours 20 minutes)")
            logger.info("✅ PIN verification system working correctly")
            logger.info("✅ Timezone fix for lockout calculations working properly")
            logger.info("✅ No regressions in authentication system")
            logger.info("✅ Admin PIN bypass functionality working")
        else:
            logger.error(f"❌ {total_tests - passed_tests} tests failed - issues detected")
        
        return self.test_results

async def main():
    """Main test execution"""
    async with PINLockoutTester() as tester:
        results = await tester.run_all_tests()
        
        # Save detailed results
        with open('/app/pin_lockout_test_results.json', 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        return results

if __name__ == "__main__":
    asyncio.run(main())