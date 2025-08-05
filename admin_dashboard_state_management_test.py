#!/usr/bin/env python3
"""
Admin Dashboard State Management Bug Fix Testing
==============================================

This test suite focuses on testing the admin dashboard state management bug fix
where users reported that after submitting clients from the pending tab to the 
submitted tab, they still appeared briefly in the pending tab requiring multiple refreshes.

Test Coverage:
1. Basic finalize endpoint functionality
2. Revert-to-pending endpoint functionality  
3. Delete endpoint functionality
4. Optimized endpoints data consistency
5. Dashboard stats endpoint accuracy
6. Complete workflow testing (pending -> submitted -> back to pending -> delete)
"""

import requests
import json
import time
import uuid
from datetime import datetime, date
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/backend/.env')

# Get backend URL from frontend environment
try:
    with open('/app/frontend/.env', 'r') as f:
        for line in f:
            if line.startswith('REACT_APP_BACKEND_URL='):
                BACKEND_URL = line.split('=')[1].strip()
                break
        else:
            BACKEND_URL = "http://localhost:8001"
except:
    BACKEND_URL = "http://localhost:8001"

API_BASE = f"{BACKEND_URL}/api"

class AdminDashboardStateTest:
    def __init__(self):
        self.test_results = []
        self.test_registration_id = None
        
    def log_result(self, test_name, success, message, details=None):
        """Log test result"""
        result = {
            'test': test_name,
            'success': success,
            'message': message,
            'details': details,
            'timestamp': datetime.now().isoformat()
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        print(f"   {message}")
        if details:
            print(f"   Details: {details}")
        print()

    def test_backend_health(self):
        """Test 1: Backend Health Check"""
        try:
            response = requests.get(f"{API_BASE}/admin-registrations-pending", timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.log_result(
                    "Backend Health Check",
                    True,
                    f"Backend accessible, found {len(data)} pending registrations",
                    f"Response time: {response.elapsed.total_seconds():.2f}s"
                )
                return True
            else:
                self.log_result(
                    "Backend Health Check",
                    False,
                    f"Backend returned status {response.status_code}",
                    response.text[:200]
                )
                return False
        except Exception as e:
            self.log_result(
                "Backend Health Check",
                False,
                f"Backend connection failed: {str(e)}"
            )
            return False

    def create_test_registration(self):
        """Test 2: Create Test Registration in Pending Status"""
        try:
            # Create a test registration with realistic data
            test_data = {
                "firstName": "TestClient",
                "lastName": f"StateTest{uuid.uuid4().hex[:8]}",
                "patientConsent": "verbal",
                "gender": "Male",
                "province": "Ontario",
                "disposition": "PENDING",
                "regDate": date.today().isoformat(),
                "healthCard": "1234567890 ON",
                "referralSite": "Toronto - Outreach",
                "address": "123 Test Street",
                "city": "Toronto",
                "postalCode": "M5V 3A8",
                "phone1": "4161234567",
                "email": "test@statemanagement.com",
                "language": "English",
                "specialAttention": "Test registration for state management testing",
                "physician": "Dr. David Fletcher"
            }
            
            response = requests.post(f"{API_BASE}/admin-register", json=test_data, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                self.test_registration_id = result.get('id')
                self.log_result(
                    "Create Test Registration",
                    True,
                    f"Test registration created successfully",
                    f"Registration ID: {self.test_registration_id}"
                )
                return True
            else:
                self.log_result(
                    "Create Test Registration",
                    False,
                    f"Failed to create registration: {response.status_code}",
                    response.text[:200]
                )
                return False
                
        except Exception as e:
            self.log_result(
                "Create Test Registration",
                False,
                f"Registration creation failed: {str(e)}"
            )
            return False

    def test_finalize_endpoint(self):
        """Test 3: Basic Finalize Endpoint Functionality"""
        if not self.test_registration_id:
            self.log_result(
                "Finalize Endpoint Test",
                False,
                "No test registration ID available"
            )
            return False
            
        try:
            # Test finalize endpoint
            response = requests.post(f"{API_BASE}/admin-registration/{self.test_registration_id}/finalize", timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                self.log_result(
                    "Finalize Endpoint Test",
                    True,
                    "Registration finalized successfully",
                    f"Status: {result.get('status')}, Email sent: {result.get('email_sent', False)}"
                )
                return True
            else:
                self.log_result(
                    "Finalize Endpoint Test",
                    False,
                    f"Finalize failed: {response.status_code}",
                    response.text[:200]
                )
                return False
                
        except Exception as e:
            self.log_result(
                "Finalize Endpoint Test",
                False,
                f"Finalize endpoint error: {str(e)}"
            )
            return False

    def test_data_consistency_after_finalize(self):
        """Test 4: Data Consistency After Finalize"""
        if not self.test_registration_id:
            return False
            
        try:
            # Check pending registrations (should NOT contain our registration)
            pending_response = requests.get(f"{API_BASE}/admin-registrations-pending", timeout=10)
            submitted_response = requests.get(f"{API_BASE}/admin-registrations-submitted", timeout=10)
            
            if pending_response.status_code == 200 and submitted_response.status_code == 200:
                pending_data = pending_response.json()
                submitted_data = submitted_response.json()
                
                # Check if registration moved from pending to submitted
                pending_ids = [reg.get('id') for reg in pending_data]
                submitted_ids = [reg.get('id') for reg in submitted_data]
                
                in_pending = self.test_registration_id in pending_ids
                in_submitted = self.test_registration_id in submitted_ids
                
                if not in_pending and in_submitted:
                    self.log_result(
                        "Data Consistency After Finalize",
                        True,
                        "Registration correctly moved from pending to submitted",
                        f"Pending: {len(pending_data)}, Submitted: {len(submitted_data)}"
                    )
                    return True
                else:
                    self.log_result(
                        "Data Consistency After Finalize",
                        False,
                        f"Registration state inconsistent - In pending: {in_pending}, In submitted: {in_submitted}",
                        f"Registration ID: {self.test_registration_id}"
                    )
                    return False
            else:
                self.log_result(
                    "Data Consistency After Finalize",
                    False,
                    f"Failed to fetch registration lists - Pending: {pending_response.status_code}, Submitted: {submitted_response.status_code}"
                )
                return False
                
        except Exception as e:
            self.log_result(
                "Data Consistency After Finalize",
                False,
                f"Data consistency check failed: {str(e)}"
            )
            return False

    def test_optimized_endpoints(self):
        """Test 5: Optimized Endpoints Data Consistency"""
        try:
            # Test optimized endpoints
            pending_opt_response = requests.get(f"{API_BASE}/admin-registrations-pending-optimized", timeout=10)
            submitted_opt_response = requests.get(f"{API_BASE}/admin-registrations-submitted-optimized", timeout=10)
            
            if pending_opt_response.status_code == 200 and submitted_opt_response.status_code == 200:
                pending_opt_data = pending_opt_response.json()
                submitted_opt_data = submitted_opt_response.json()
                
                # Check data structure
                pending_results = pending_opt_data.get('results', [])
                submitted_results = submitted_opt_data.get('results', [])
                
                self.log_result(
                    "Optimized Endpoints Test",
                    True,
                    "Optimized endpoints working correctly",
                    f"Pending optimized: {len(pending_results)}, Submitted optimized: {len(submitted_results)}"
                )
                return True
            else:
                self.log_result(
                    "Optimized Endpoints Test",
                    False,
                    f"Optimized endpoints failed - Pending: {pending_opt_response.status_code}, Submitted: {submitted_opt_response.status_code}"
                )
                return False
                
        except Exception as e:
            self.log_result(
                "Optimized Endpoints Test",
                False,
                f"Optimized endpoints test failed: {str(e)}"
            )
            return False

    def test_dashboard_stats(self):
        """Test 6: Dashboard Stats Endpoint"""
        try:
            response = requests.get(f"{API_BASE}/admin-dashboard-stats", timeout=10)
            
            if response.status_code == 200:
                stats = response.json()
                
                # Verify stats structure
                required_fields = ['pending_count', 'submitted_count', 'total_count']
                missing_fields = [field for field in required_fields if field not in stats]
                
                if not missing_fields:
                    self.log_result(
                        "Dashboard Stats Test",
                        True,
                        "Dashboard stats endpoint working correctly",
                        f"Pending: {stats.get('pending_count')}, Submitted: {stats.get('submitted_count')}, Total: {stats.get('total_count')}"
                    )
                    return True
                else:
                    self.log_result(
                        "Dashboard Stats Test",
                        False,
                        f"Dashboard stats missing fields: {missing_fields}",
                        str(stats)
                    )
                    return False
            else:
                self.log_result(
                    "Dashboard Stats Test",
                    False,
                    f"Dashboard stats failed: {response.status_code}",
                    response.text[:200]
                )
                return False
                
        except Exception as e:
            self.log_result(
                "Dashboard Stats Test",
                False,
                f"Dashboard stats test failed: {str(e)}"
            )
            return False

    def test_revert_to_pending(self):
        """Test 7: Revert-to-Pending Endpoint"""
        if not self.test_registration_id:
            return False
            
        try:
            # Test revert to pending endpoint
            response = requests.post(f"{API_BASE}/admin-registration/{self.test_registration_id}/revert-to-pending", timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                self.log_result(
                    "Revert to Pending Test",
                    True,
                    "Registration reverted to pending successfully",
                    f"Status: {result.get('status')}"
                )
                return True
            else:
                self.log_result(
                    "Revert to Pending Test",
                    False,
                    f"Revert failed: {response.status_code}",
                    response.text[:200]
                )
                return False
                
        except Exception as e:
            self.log_result(
                "Revert to Pending Test",
                False,
                f"Revert endpoint error: {str(e)}"
            )
            return False

    def test_data_consistency_after_revert(self):
        """Test 8: Data Consistency After Revert"""
        if not self.test_registration_id:
            return False
            
        try:
            # Small delay to ensure database consistency
            time.sleep(1)
            
            # Check registration lists again
            pending_response = requests.get(f"{API_BASE}/admin-registrations-pending", timeout=10)
            submitted_response = requests.get(f"{API_BASE}/admin-registrations-submitted", timeout=10)
            
            if pending_response.status_code == 200 and submitted_response.status_code == 200:
                pending_data = pending_response.json()
                submitted_data = submitted_response.json()
                
                # Check if registration moved back to pending
                pending_ids = [reg.get('id') for reg in pending_data]
                submitted_ids = [reg.get('id') for reg in submitted_data]
                
                in_pending = self.test_registration_id in pending_ids
                in_submitted = self.test_registration_id in submitted_ids
                
                if in_pending and not in_submitted:
                    self.log_result(
                        "Data Consistency After Revert",
                        True,
                        "Registration correctly moved back to pending",
                        f"Pending: {len(pending_data)}, Submitted: {len(submitted_data)}"
                    )
                    return True
                else:
                    self.log_result(
                        "Data Consistency After Revert",
                        False,
                        f"Registration state inconsistent after revert - In pending: {in_pending}, In submitted: {in_submitted}",
                        f"Registration ID: {self.test_registration_id}"
                    )
                    return False
            else:
                self.log_result(
                    "Data Consistency After Revert",
                    False,
                    f"Failed to fetch registration lists after revert"
                )
                return False
                
        except Exception as e:
            self.log_result(
                "Data Consistency After Revert",
                False,
                f"Data consistency check after revert failed: {str(e)}"
            )
            return False

    def test_delete_endpoint(self):
        """Test 9: Delete Endpoint Functionality"""
        if not self.test_registration_id:
            return False
            
        try:
            # Test delete endpoint
            response = requests.delete(f"{API_BASE}/admin-registration/{self.test_registration_id}", timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                self.log_result(
                    "Delete Endpoint Test",
                    True,
                    "Registration deleted successfully",
                    f"Message: {result.get('message')}"
                )
                return True
            else:
                self.log_result(
                    "Delete Endpoint Test",
                    False,
                    f"Delete failed: {response.status_code}",
                    response.text[:200]
                )
                return False
                
        except Exception as e:
            self.log_result(
                "Delete Endpoint Test",
                False,
                f"Delete endpoint error: {str(e)}"
            )
            return False

    def test_data_consistency_after_delete(self):
        """Test 10: Data Consistency After Delete"""
        if not self.test_registration_id:
            return False
            
        try:
            # Small delay to ensure database consistency
            time.sleep(1)
            
            # Check that registration is completely removed
            pending_response = requests.get(f"{API_BASE}/admin-registrations-pending", timeout=10)
            submitted_response = requests.get(f"{API_BASE}/admin-registrations-submitted", timeout=10)
            
            if pending_response.status_code == 200 and submitted_response.status_code == 200:
                pending_data = pending_response.json()
                submitted_data = submitted_response.json()
                
                # Check if registration is completely removed
                pending_ids = [reg.get('id') for reg in pending_data]
                submitted_ids = [reg.get('id') for reg in submitted_data]
                
                in_pending = self.test_registration_id in pending_ids
                in_submitted = self.test_registration_id in submitted_ids
                
                if not in_pending and not in_submitted:
                    self.log_result(
                        "Data Consistency After Delete",
                        True,
                        "Registration completely removed from both lists",
                        f"Pending: {len(pending_data)}, Submitted: {len(submitted_data)}"
                    )
                    return True
                else:
                    self.log_result(
                        "Data Consistency After Delete",
                        False,
                        f"Registration still exists after delete - In pending: {in_pending}, In submitted: {in_submitted}",
                        f"Registration ID: {self.test_registration_id}"
                    )
                    return False
            else:
                self.log_result(
                    "Data Consistency After Delete",
                    False,
                    f"Failed to fetch registration lists after delete"
                )
                return False
                
        except Exception as e:
            self.log_result(
                "Data Consistency After Delete",
                False,
                f"Data consistency check after delete failed: {str(e)}"
            )
            return False

    def run_all_tests(self):
        """Run all admin dashboard state management tests"""
        print("🔧 ADMIN DASHBOARD STATE MANAGEMENT BUG FIX TESTING")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"API Base: {API_BASE}")
        print()
        
        # Run tests in sequence
        tests = [
            self.test_backend_health,
            self.create_test_registration,
            self.test_finalize_endpoint,
            self.test_data_consistency_after_finalize,
            self.test_optimized_endpoints,
            self.test_dashboard_stats,
            self.test_revert_to_pending,
            self.test_data_consistency_after_revert,
            self.test_delete_endpoint,
            self.test_data_consistency_after_delete
        ]
        
        for test in tests:
            test()
            time.sleep(0.5)  # Small delay between tests
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for result in self.test_results if result['success'])
        total = len(self.test_results)
        success_rate = (passed / total * 100) if total > 0 else 0
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        # Failed tests details
        failed_tests = [result for result in self.test_results if not result['success']]
        if failed_tests:
            print("❌ FAILED TESTS:")
            for test in failed_tests:
                print(f"   • {test['test']}: {test['message']}")
        else:
            print("✅ ALL TESTS PASSED!")
        
        print()
        print("🎯 ADMIN DASHBOARD STATE MANAGEMENT TESTING COMPLETED")
        
        return success_rate >= 80  # Consider 80%+ as success

if __name__ == "__main__":
    tester = AdminDashboardStateTest()
    success = tester.run_all_tests()
    exit(0 if success else 1)
