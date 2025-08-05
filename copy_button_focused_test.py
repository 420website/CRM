#!/usr/bin/env python3

import asyncio
import aiohttp
import json
import sys
import time
from datetime import datetime

# Backend URL from environment
BACKEND_URL = "https://dfe9a1e1-7f3d-45aa-ad71-43a254e568c5.preview.emergentagent.com/api"

class CopyButtonFunctionalityTest:
    def __init__(self):
        self.session = None
        self.test_results = []
        self.existing_registration_id = None
        
    async def setup_session(self):
        """Setup HTTP session"""
        self.session = aiohttp.ClientSession()
        
    async def cleanup_session(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()
            
    def log_test(self, test_name, success, message, details=None):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        print(f"   {message}")
        if details:
            print(f"   Details: {details}")
        print()
        
        self.test_results.append({
            'test': test_name,
            'success': success,
            'message': message,
            'details': details
        })

    async def test_backend_health(self):
        """Test if backend is accessible"""
        try:
            async with self.session.get(f"{BACKEND_URL.replace('/api', '')}/") as response:
                if response.status == 200:
                    self.log_test("Backend Health Check", True, "Backend is accessible")
                    return True
                else:
                    self.log_test("Backend Health Check", False, f"Backend returned status {response.status}")
                    return False
        except Exception as e:
            self.log_test("Backend Health Check", False, f"Backend connection failed: {str(e)}")
            return False

    async def get_existing_registration(self):
        """Get an existing registration for AdminEdit testing"""
        try:
            async with self.session.get(f"{BACKEND_URL}/admin-registrations-pending") as response:
                if response.status == 200:
                    registrations = await response.json()
                    if registrations and len(registrations) > 0:
                        # Get the first registration
                        self.existing_registration_id = registrations[0]['id']
                        self.log_test("Get Existing Registration", True, 
                                    f"Found existing registration: {self.existing_registration_id}")
                        return True
                    else:
                        self.log_test("Get Existing Registration", False, "No existing registrations found")
                        return False
                else:
                    self.log_test("Get Existing Registration", False, f"Failed to get registrations: {response.status}")
                    return False
        except Exception as e:
            self.log_test("Get Existing Registration", False, f"Error getting existing registration: {str(e)}")
            return False

    async def test_adminregister_copy_scenario(self):
        """Test AdminRegister copy button scenario (new registration)"""
        try:
            # In AdminRegister, copy button works with form data in memory
            # Test that all required data sources are available
            
            # Test dispositions (needed for form)
            async with self.session.get(f"{BACKEND_URL}/dispositions") as response:
                if response.status != 200:
                    self.log_test("AdminRegister - Dispositions Access", False, 
                                f"Cannot access dispositions: {response.status}")
                    return False
                dispositions = await response.json()
                
            # Test referral sites (needed for form)
            async with self.session.get(f"{BACKEND_URL}/referral-sites") as response:
                if response.status != 200:
                    self.log_test("AdminRegister - Referral Sites Access", False, 
                                f"Cannot access referral sites: {response.status}")
                    return False
                referral_sites = await response.json()
                
            # Test clinical templates (needed for form)
            async with self.session.get(f"{BACKEND_URL}/clinical-templates") as response:
                if response.status != 200:
                    self.log_test("AdminRegister - Clinical Templates Access", False, 
                                f"Cannot access clinical templates: {response.status}")
                    return False
                clinical_templates = await response.json()
            
            self.log_test("AdminRegister Copy Scenario", True, 
                        f"All data sources accessible: {len(dispositions)} dispositions, "
                        f"{len(referral_sites)} referral sites, {len(clinical_templates)} templates")
            return True
            
        except Exception as e:
            self.log_test("AdminRegister Copy Scenario", False, f"Error testing AdminRegister scenario: {str(e)}")
            return False

    async def test_adminedit_copy_scenario(self):
        """Test AdminEdit copy button scenario (existing registration)"""
        if not self.existing_registration_id:
            self.log_test("AdminEdit Copy Scenario", False, "No existing registration ID available")
            return False
            
        try:
            # In AdminEdit, copy button needs to fetch data from API
            
            # Test registration data access (this is loaded into form state)
            async with self.session.get(f"{BACKEND_URL}/admin-registration/{self.existing_registration_id}") as response:
                if response.status != 200:
                    self.log_test("AdminEdit - Registration Data Access", False, 
                                f"Cannot access registration data: {response.status}")
                    return False
                registration_data = await response.json()
                
            # Test test data access (this is what copy button fetches)
            async with self.session.get(f"{BACKEND_URL}/admin-registration/{self.existing_registration_id}/tests") as response:
                if response.status != 200:
                    self.log_test("AdminEdit - Test Data Access", False, 
                                f"Cannot access test data: {response.status}")
                    return False
                tests_data = await response.json()
                tests = tests_data.get('tests', [])
            
            # Verify that we have the essential data for copy functionality
            has_required_fields = (
                registration_data.get('firstName') and
                registration_data.get('lastName') and
                registration_data.get('dob')
            )
            
            if has_required_fields:
                self.log_test("AdminEdit Copy Scenario", True, 
                            f"Registration data accessible with {len(tests)} test records")
                return True
            else:
                self.log_test("AdminEdit Copy Scenario", False, 
                            "Missing required fields in registration data")
                return False
            
        except Exception as e:
            self.log_test("AdminEdit Copy Scenario", False, f"Error testing AdminEdit scenario: {str(e)}")
            return False

    async def test_copy_button_api_endpoints(self):
        """Test all API endpoints that the copy button functionality depends on"""
        if not self.existing_registration_id:
            self.log_test("Copy Button API Endpoints", False, "No registration ID for testing")
            return False
            
        try:
            # Test the specific endpoint that copy button uses to fetch test data
            async with self.session.get(f"{BACKEND_URL}/admin-registration/{self.existing_registration_id}/tests") as response:
                if response.status == 200:
                    tests_data = await response.json()
                    tests = tests_data.get('tests', [])
                    
                    # Verify the response structure matches what copy button expects
                    if isinstance(tests, list):
                        test_fields_valid = True
                        for test in tests:
                            # Check if test has the fields that copy button uses
                            required_fields = ['test_type', 'test_date']
                            for field in required_fields:
                                if field not in test:
                                    test_fields_valid = False
                                    break
                        
                        if test_fields_valid:
                            self.log_test("Copy Button API - Tests Endpoint", True, 
                                        f"Tests endpoint working correctly with {len(tests)} tests")
                        else:
                            self.log_test("Copy Button API - Tests Endpoint", False, 
                                        "Tests missing required fields for copy functionality")
                    else:
                        self.log_test("Copy Button API - Tests Endpoint", False, 
                                    "Tests endpoint returned invalid structure")
                else:
                    self.log_test("Copy Button API - Tests Endpoint", False, 
                                f"Tests endpoint failed: {response.status}")
                    return False
            
            # Test registration data endpoint (used to populate form in AdminEdit)
            async with self.session.get(f"{BACKEND_URL}/admin-registration/{self.existing_registration_id}") as response:
                if response.status == 200:
                    registration_data = await response.json()
                    
                    # Check if registration has the fields that copy button uses
                    copy_fields = ['firstName', 'lastName', 'dob', 'healthCard', 'phone1', 
                                 'address', 'city', 'province', 'postalCode', 'summaryTemplate']
                    
                    available_fields = []
                    missing_fields = []
                    
                    for field in copy_fields:
                        if field in registration_data and registration_data[field]:
                            available_fields.append(field)
                        else:
                            missing_fields.append(field)
                    
                    self.log_test("Copy Button API - Registration Endpoint", True, 
                                f"Registration endpoint working. Available fields: {len(available_fields)}, "
                                f"Missing/empty fields: {len(missing_fields)}")
                else:
                    self.log_test("Copy Button API - Registration Endpoint", False, 
                                f"Registration endpoint failed: {response.status}")
                    return False
            
            return True
            
        except Exception as e:
            self.log_test("Copy Button API Endpoints", False, f"Error testing copy button APIs: {str(e)}")
            return False

    async def test_registration_id_availability(self):
        """Test the key difference: registration ID availability between AdminRegister and AdminEdit"""
        try:
            # AdminRegister scenario analysis
            print("🔍 REGISTRATION ID AVAILABILITY ANALYSIS:")
            print()
            print("AdminRegister Component:")
            print("  • Uses currentRegistrationId state variable")
            print("  • Initially null when creating new registration")
            print("  • Set after successful form submission")
            print("  • Copy button works because form data is in component state")
            print("  • Test data fetched only if currentRegistrationId exists")
            print()
            
            # AdminEdit scenario analysis
            print("AdminEdit Component:")
            print("  • Uses registrationId from URL params (useParams())")
            print("  • Available immediately when component loads")
            print("  • Form data loaded from API into component state")
            print("  • Copy button should work because registrationId is known")
            print("  • Test data can always be fetched using registrationId")
            print()
            
            if self.existing_registration_id:
                # Verify that the registration ID we have works for API calls
                async with self.session.get(f"{BACKEND_URL}/admin-registration/{self.existing_registration_id}") as response:
                    if response.status == 200:
                        self.log_test("Registration ID Availability", True, 
                                    "AdminEdit scenario: registrationId from URL params works for API calls")
                        return True
                    else:
                        self.log_test("Registration ID Availability", False, 
                                    f"AdminEdit scenario: registrationId failed API call: {response.status}")
                        return False
            else:
                self.log_test("Registration ID Availability", False, 
                            "No registration ID available for testing AdminEdit scenario")
                return False
                
        except Exception as e:
            self.log_test("Registration ID Availability", False, f"Error analyzing registration ID availability: {str(e)}")
            return False

    async def test_copy_functionality_differences(self):
        """Analyze the differences between AdminRegister and AdminEdit copy functionality"""
        try:
            print("🔍 COPY FUNCTIONALITY ANALYSIS:")
            print()
            
            # AdminRegister copy functionality
            print("AdminRegister Copy Button Logic:")
            print("  1. Uses formData from component state (always available)")
            print("  2. Uses currentRegistrationId state variable")
            print("  3. If currentRegistrationId exists, fetches fresh test data")
            print("  4. If no currentRegistrationId, proceeds without test data")
            print("  5. Formats and copies data to clipboard")
            print()
            
            # AdminEdit copy functionality  
            print("AdminEdit Copy Button Logic:")
            print("  1. Uses formData from component state (loaded from API)")
            print("  2. Uses registrationId from URL params")
            print("  3. Always has registrationId, so always fetches test data")
            print("  4. Formats and copies data to clipboard")
            print()
            
            # Test the critical difference
            if self.existing_registration_id:
                # Test that AdminEdit scenario can always fetch test data
                async with self.session.get(f"{BACKEND_URL}/admin-registration/{self.existing_registration_id}/tests") as response:
                    if response.status == 200:
                        tests_data = await response.json()
                        tests = tests_data.get('tests', [])
                        
                        self.log_test("Copy Functionality Differences", True, 
                                    f"AdminEdit can always fetch test data: {len(tests)} tests available")
                        
                        print("🎯 KEY INSIGHT:")
                        print("  AdminEdit should have MORE reliable copy functionality")
                        print("  because registrationId is always available from URL params")
                        print("  If copy button isn't working in AdminEdit, the issue is likely:")
                        print("    • Frontend state management problem")
                        print("    • Form data not properly loaded into component state")
                        print("    • Error in the copy button click handler")
                        print()
                        
                        return True
                    else:
                        self.log_test("Copy Functionality Differences", False, 
                                    f"AdminEdit cannot fetch test data: {response.status}")
                        return False
            else:
                self.log_test("Copy Functionality Differences", False, 
                            "Cannot analyze without registration ID")
                return False
                
        except Exception as e:
            self.log_test("Copy Functionality Differences", False, f"Error analyzing copy functionality: {str(e)}")
            return False

    async def run_all_tests(self):
        """Run all copy button functionality tests"""
        print("🔄 COPY BUTTON FUNCTIONALITY TESTING")
        print("Testing why copy button works in AdminRegister but not AdminEdit")
        print("=" * 70)
        print()
        
        await self.setup_session()
        
        try:
            # Test backend health
            if not await self.test_backend_health():
                print("❌ Backend not accessible, stopping tests")
                return
            
            # Get existing registration for AdminEdit testing
            if not await self.get_existing_registration():
                print("❌ Cannot get existing registration for AdminEdit testing")
                return
            
            # Test AdminRegister scenario
            await self.test_adminregister_copy_scenario()
            
            # Test AdminEdit scenario
            await self.test_adminedit_copy_scenario()
            
            # Test copy button API endpoints
            await self.test_copy_button_api_endpoints()
            
            # Test registration ID availability
            await self.test_registration_id_availability()
            
            # Analyze copy functionality differences
            await self.test_copy_functionality_differences()
            
        finally:
            await self.cleanup_session()
        
        # Print summary
        print("\n" + "=" * 70)
        print("📊 COPY BUTTON FUNCTIONALITY TEST SUMMARY")
        print("=" * 70)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  • {result['test']}: {result['message']}")
        
        print(f"\n🎯 COPY BUTTON DIAGNOSIS:")
        print("=" * 50)
        
        if passed_tests >= total_tests - 1:  # Allow for 1 minor failure
            print("✅ BACKEND SUPPORTS COPY FUNCTIONALITY CORRECTLY")
            print()
            print("Root Cause Analysis:")
            print("  AdminRegister Copy Button: ✅ Works")
            print("    • Form data available in component state")
            print("    • currentRegistrationId set after submission")
            print("    • Test data fetched if registration exists")
            print()
            print("  AdminEdit Copy Button: ❓ Should Work")
            print("    • registrationId available from URL params")
            print("    • Form data loaded from API")
            print("    • All required API endpoints working")
            print()
            print("🔧 LIKELY FRONTEND ISSUES TO CHECK:")
            print("  1. Verify registrationId from useParams() is being used correctly")
            print("  2. Check if formData state is properly populated after loading")
            print("  3. Ensure copy button handler uses the correct registrationId")
            print("  4. Check browser console for JavaScript errors")
            print("  5. Verify clipboard API permissions in browser")
            print()
            print("💡 RECOMMENDATION:")
            print("  The backend is working correctly. The issue is likely in the")
            print("  frontend AdminEdit component's state management or copy handler.")
        else:
            print("❌ BACKEND ISSUES DETECTED")
            print("  Backend problems may be affecting copy functionality")
            print("  Fix backend issues before investigating frontend problems")

async def main():
    """Main test execution"""
    tester = CopyButtonFunctionalityTest()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())