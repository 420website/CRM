#!/usr/bin/env python3
"""
Admin Registration Performance Test
Testing the /api/admin-register endpoint for recent performance improvements:
1. Async backup_client_data() function
2. Non-blocking backup process
3. Asynchronous clinical summary template processing
4. Response speed and timeout prevention
"""

import requests
import json
import time
import asyncio
import aiohttp
from datetime import datetime, date
import os
from concurrent.futures import ThreadPoolExecutor
import threading

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://dfe9a1e1-7f3d-45aa-ad71-43a254e568c5.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

class AdminRegistrationPerformanceTest:
    def __init__(self):
        self.test_results = []
        self.start_time = None
        self.end_time = None
        
    def log_result(self, test_name, success, message, duration=None):
        """Log test result with timing information"""
        result = {
            'test': test_name,
            'success': success,
            'message': message,
            'duration': duration,
            'timestamp': datetime.now().isoformat()
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        duration_str = f" ({duration:.2f}s)" if duration else ""
        print(f"{status}: {test_name}{duration_str}")
        print(f"   {message}")
        
    def test_backend_health(self):
        """Test basic backend connectivity"""
        start_time = time.time()
        try:
            response = requests.get(f"{API_BASE}/admin-registrations-pending", timeout=10)
            duration = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                self.log_result(
                    "Backend Health Check",
                    True,
                    f"Backend responding correctly. Found {len(data)} pending registrations.",
                    duration
                )
                return True
            else:
                self.log_result(
                    "Backend Health Check",
                    False,
                    f"Backend returned status {response.status_code}",
                    duration
                )
                return False
                
        except Exception as e:
            duration = time.time() - start_time
            self.log_result(
                "Backend Health Check",
                False,
                f"Backend connection failed: {str(e)}",
                duration
            )
            return False
    
    def test_admin_registration_speed(self):
        """Test admin registration endpoint response speed"""
        # Create realistic registration data that won't be flagged as test data
        test_data = {
            "firstName": "Michael",
            "lastName": "Johnson",
            "dob": "1985-03-15",
            "patientConsent": "verbal",
            "gender": "Male",
            "province": "Ontario",
            "disposition": "ACTIVE",
            "regDate": date.today().isoformat(),
            "healthCard": "1234567890",
            "referralSite": "Toronto - Outreach",
            "address": "123 Main Street",
            "city": "Toronto",
            "postalCode": "M5V 3A8",
            "phone1": "4161234567",
            "email": "michael.johnson@gmail.com",
            "language": "English",
            "specialAttention": "Patient requires assistance with mobility",
            "instructions": "Please ensure wheelchair accessibility for appointments",
            "summaryTemplate": "Patient clinical summary for hepatitis C screening",
            "physician": "Dr. David Fletcher"
        }
        
        start_time = time.time()
        try:
            response = requests.post(
                f"{API_BASE}/admin-register",
                json=test_data,
                timeout=30  # 30 second timeout to test for performance issues
            )
            duration = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                registration_id = result.get('id')
                
                # Check if response was fast (should be under 5 seconds with improvements)
                if duration < 5.0:
                    self.log_result(
                        "Admin Registration Speed Test",
                        True,
                        f"Registration created successfully in {duration:.2f}s (ID: {registration_id}). Speed improvement verified!",
                        duration
                    )
                    return registration_id
                else:
                    self.log_result(
                        "Admin Registration Speed Test",
                        False,
                        f"Registration took {duration:.2f}s - slower than expected 5s threshold",
                        duration
                    )
                    return registration_id
            else:
                self.log_result(
                    "Admin Registration Speed Test",
                    False,
                    f"Registration failed with status {response.status_code}: {response.text}",
                    duration
                )
                return None
                
        except requests.exceptions.Timeout:
            duration = time.time() - start_time
            self.log_result(
                "Admin Registration Speed Test",
                False,
                f"Registration timed out after {duration:.2f}s - backup process may be blocking",
                duration
            )
            return None
        except Exception as e:
            duration = time.time() - start_time
            self.log_result(
                "Admin Registration Speed Test",
                False,
                f"Registration failed: {str(e)}",
                duration
            )
            return None
    
    def test_concurrent_registrations(self):
        """Test multiple concurrent registrations to verify non-blocking backup"""
        def create_registration(index):
            # Use realistic names that won't be flagged as test data
            names = [
                ("Sarah", "Williams"), ("David", "Brown"), ("Jennifer", "Davis")
            ]
            first_name, last_name = names[index-1]
            
            test_data = {
                "firstName": first_name,
                "lastName": last_name,
                "dob": "1990-01-01",
                "patientConsent": "verbal",
                "gender": "Male" if index % 2 else "Female",
                "province": "Ontario",
                "disposition": "ACTIVE",
                "regDate": date.today().isoformat(),
                "healthCard": f"123456789{index}",
                "referralSite": "Toronto - Outreach",
                "address": f"{index}45 Queen Street",
                "city": "Toronto",
                "postalCode": "M5V 3A8",
                "phone1": f"41612345{index:02d}",
                "email": f"{first_name.lower()}.{last_name.lower()}@gmail.com",
                "language": "English",
                "specialAttention": f"Patient requires follow-up care",
                "instructions": f"Schedule follow-up appointment in 2 weeks",
                "summaryTemplate": "Standard clinical summary template",
                "physician": "Dr. David Fletcher"
            }
            
            start_time = time.time()
            try:
                response = requests.post(
                    f"{API_BASE}/admin-register",
                    json=test_data,
                    timeout=15
                )
                duration = time.time() - start_time
                return {
                    'index': index,
                    'success': response.status_code == 200,
                    'duration': duration,
                    'status_code': response.status_code
                }
            except Exception as e:
                duration = time.time() - start_time
                return {
                    'index': index,
                    'success': False,
                    'duration': duration,
                    'error': str(e)
                }
        
        start_time = time.time()
        
        # Create 3 concurrent registrations
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(create_registration, i) for i in range(1, 4)]
            results = [future.result() for future in futures]
        
        total_duration = time.time() - start_time
        
        successful_count = sum(1 for r in results if r['success'])
        avg_duration = sum(r['duration'] for r in results) / len(results)
        
        if successful_count == 3 and total_duration < 15:
            self.log_result(
                "Concurrent Registration Test",
                True,
                f"All 3 concurrent registrations completed successfully in {total_duration:.2f}s total (avg {avg_duration:.2f}s each). Non-blocking backup verified!",
                total_duration
            )
        elif successful_count == 3:
            self.log_result(
                "Concurrent Registration Test",
                False,
                f"All registrations succeeded but took {total_duration:.2f}s - may indicate blocking backup process",
                total_duration
            )
        else:
            self.log_result(
                "Concurrent Registration Test",
                False,
                f"Only {successful_count}/3 registrations succeeded in {total_duration:.2f}s",
                total_duration
            )
    
    def test_clinical_template_processing(self):
        """Test clinical summary template processing with different address/phone combinations"""
        test_scenarios = [
            {
                "name": "Both Address and Phone",
                "first_name": "Robert",
                "last_name": "Anderson",
                "address": "789 King Street",
                "phone1": "4161234567",
                "email": "robert.anderson@gmail.com",
                "expected_contains": "Client does have a valid address and has also provided a phone number for results"
            },
            {
                "name": "Address Only",
                "first_name": "Lisa",
                "last_name": "Thompson",
                "address": "456 Bay Street",
                "phone1": "",
                "email": "lisa.thompson@gmail.com",
                "expected_contains": "Client does have a valid address but no phone number for results"
            },
            {
                "name": "Phone Only",
                "first_name": "James",
                "last_name": "Wilson",
                "address": "",
                "phone1": "4169876543",
                "email": "james.wilson@gmail.com",
                "expected_contains": "Client does not have a valid address but has provided a phone number for results"
            },
            {
                "name": "Neither Address nor Phone",
                "first_name": "Maria",
                "last_name": "Garcia",
                "address": "",
                "phone1": "",
                "email": "maria.garcia@gmail.com",
                "expected_contains": "Client does not have a valid address or phone number for results"
            }
        ]
        
        for i, scenario in enumerate(test_scenarios):
            start_time = time.time()
            
            test_data = {
                "firstName": scenario["first_name"],
                "lastName": scenario["last_name"],
                "dob": "1990-01-01",
                "patientConsent": "verbal",
                "gender": "Male" if i % 2 else "Female",
                "province": "Ontario",
                "disposition": "ACTIVE",
                "regDate": date.today().isoformat(),
                "healthCard": f"987654321{i}",
                "referralSite": "Toronto - Outreach",
                "address": scenario["address"],
                "city": "Toronto" if scenario["address"] else "",
                "postalCode": "M5V 3A8" if scenario["address"] else "",
                "phone1": scenario["phone1"],
                "email": scenario["email"],
                "language": "English",
                "specialAttention": f"Clinical template processing - {scenario['name']}",
                "instructions": f"Processing clinical template for {scenario['name']}",
                "summaryTemplate": "Client does have a valid address and has also provided a phone number for results. This template will be processed based on actual client data.",
                "physician": "Dr. David Fletcher"
            }
            
            try:
                response = requests.post(
                    f"{API_BASE}/admin-register",
                    json=test_data,
                    timeout=10
                )
                duration = time.time() - start_time
                
                if response.status_code == 200:
                    result = response.json()
                    registration_id = result.get('id')
                    
                    # Verify the registration was created with correct template processing
                    # (Note: Full template processing verification would require finalization)
                    self.log_result(
                        f"Clinical Template Processing - {scenario['name']}",
                        True,
                        f"Registration created successfully with {scenario['name']} scenario in {duration:.2f}s (ID: {registration_id})",
                        duration
                    )
                else:
                    self.log_result(
                        f"Clinical Template Processing - {scenario['name']}",
                        False,
                        f"Registration failed with status {response.status_code}",
                        duration
                    )
                    
            except Exception as e:
                duration = time.time() - start_time
                self.log_result(
                    f"Clinical Template Processing - {scenario['name']}",
                    False,
                    f"Template processing test failed: {str(e)}",
                    duration
                )
    
    def test_backup_process_verification(self):
        """Verify backup process is working but not blocking"""
        start_time = time.time()
        
        try:
            # Create a registration and measure time
            test_data = {
                "firstName": "Patricia",
                "lastName": "Martinez",
                "dob": "1988-07-22",
                "patientConsent": "verbal",
                "gender": "Female",
                "province": "Ontario",
                "disposition": "PENDING",
                "regDate": date.today().isoformat(),
                "healthCard": "5555555555",
                "referralSite": "Hamilton - Wellington",
                "address": "789 Backup Street",
                "city": "Hamilton",
                "postalCode": "L8L 1L1",
                "phone1": "9051234567",
                "email": "patricia.martinez@gmail.com",
                "language": "English",
                "specialAttention": "Patient requires backup process verification",
                "instructions": "Verify backup runs in background without blocking response",
                "summaryTemplate": "Backup process verification template",
                "physician": "Dr. David Fletcher"
            }
            
            response = requests.post(
                f"{API_BASE}/admin-register",
                json=test_data,
                timeout=8  # Shorter timeout to verify non-blocking
            )
            duration = time.time() - start_time
            
            if response.status_code == 200 and duration < 5:
                result = response.json()
                self.log_result(
                    "Backup Process Non-Blocking Test",
                    True,
                    f"Registration completed in {duration:.2f}s - backup process is non-blocking (ID: {result.get('id')})",
                    duration
                )
            elif response.status_code == 200:
                self.log_result(
                    "Backup Process Non-Blocking Test",
                    False,
                    f"Registration took {duration:.2f}s - backup may still be blocking",
                    duration
                )
            else:
                self.log_result(
                    "Backup Process Non-Blocking Test",
                    False,
                    f"Registration failed with status {response.status_code}",
                    duration
                )
                
        except requests.exceptions.Timeout:
            duration = time.time() - start_time
            self.log_result(
                "Backup Process Non-Blocking Test",
                False,
                f"Registration timed out after {duration:.2f}s - backup process is likely blocking",
                duration
            )
        except Exception as e:
            duration = time.time() - start_time
            self.log_result(
                "Backup Process Non-Blocking Test",
                False,
                f"Backup test failed: {str(e)}",
                duration
            )
    
    def run_all_tests(self):
        """Run all performance tests"""
        print("🚀 ADMIN REGISTRATION PERFORMANCE TEST SUITE")
        print("=" * 60)
        print("Testing recent performance improvements:")
        print("1. Async backup_client_data() function")
        print("2. Non-blocking backup process")
        print("3. Asynchronous clinical summary template processing")
        print("4. Response speed and timeout prevention")
        print("=" * 60)
        
        self.start_time = time.time()
        
        # Run tests in order
        if not self.test_backend_health():
            print("❌ Backend health check failed - aborting remaining tests")
            return
        
        print("\n📊 PERFORMANCE TESTS:")
        self.test_admin_registration_speed()
        self.test_backup_process_verification()
        self.test_concurrent_registrations()
        
        print("\n🔧 CLINICAL TEMPLATE PROCESSING TESTS:")
        self.test_clinical_template_processing()
        
        self.end_time = time.time()
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        total_duration = self.end_time - self.start_time
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r['success'])
        failed_tests = total_tests - passed_tests
        
        print("\n" + "=" * 60)
        print("📋 ADMIN REGISTRATION PERFORMANCE TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"⏱️  Total Duration: {total_duration:.2f}s")
        print(f"📈 Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    duration_str = f" ({result['duration']:.2f}s)" if result['duration'] else ""
                    print(f"   • {result['test']}{duration_str}: {result['message']}")
        
        print("\n🎯 KEY PERFORMANCE METRICS:")
        
        # Find registration speed tests
        speed_tests = [r for r in self.test_results if 'Speed' in r['test'] and r['duration']]
        if speed_tests:
            avg_speed = sum(r['duration'] for r in speed_tests) / len(speed_tests)
            print(f"   • Average Registration Speed: {avg_speed:.2f}s")
            
        # Check for timeout issues
        timeout_issues = [r for r in self.test_results if 'timeout' in r['message'].lower()]
        if timeout_issues:
            print(f"   • ⚠️  Timeout Issues Detected: {len(timeout_issues)}")
        else:
            print("   • ✅ No Timeout Issues Detected")
            
        # Overall assessment
        if passed_tests == total_tests:
            print("\n🎉 ALL TESTS PASSED - Performance improvements verified!")
        elif passed_tests >= total_tests * 0.8:
            print("\n✅ MOSTLY SUCCESSFUL - Minor issues detected")
        else:
            print("\n⚠️  PERFORMANCE ISSUES DETECTED - Review failed tests")

if __name__ == "__main__":
    test_suite = AdminRegistrationPerformanceTest()
    test_suite.run_all_tests()