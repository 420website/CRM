#!/usr/bin/env python3
"""
Corrected Selected Template Field Testing Suite
Tests the newly added selectedTemplate field functionality with proper API understanding.
"""

import requests
import json
import uuid
from datetime import datetime, date
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

class CorrectedSelectedTemplateFieldTester:
    def __init__(self):
        self.base_url = os.getenv('REACT_APP_BACKEND_URL', 'https://dfe9a1e1-7f3d-45aa-ad71-43a254e568c5.preview.emergentagent.com')
        self.api_url = f"{self.base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.created_registrations = []
        
    def log_test(self, test_name, success, details=""):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {test_name}: PASSED {details}")
        else:
            print(f"❌ {test_name}: FAILED {details}")
        return success
    
    def create_test_registration(self, selected_template="Select", summary_template=None):
        """Create a test registration with specific selectedTemplate value"""
        unique_id = str(uuid.uuid4())[:8]
        
        registration_data = {
            "firstName": f"TestUser{unique_id}",
            "lastName": f"Template{unique_id}",
            "patientConsent": "verbal",
            "selectedTemplate": selected_template
        }
        
        if summary_template:
            registration_data["summaryTemplate"] = summary_template
            
        try:
            response = requests.post(
                f"{self.api_url}/admin-register",
                json=registration_data,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                result = response.json()
                registration_id = result.get('registration_id')
                if registration_id:
                    self.created_registrations.append(registration_id)
                    return True, registration_id, result
                else:
                    return False, None, f"No registration_id in response: {result}"
            else:
                return False, None, f"HTTP {response.status_code}: {response.text}"
                
        except Exception as e:
            return False, None, f"Exception: {str(e)}"
    
    def get_registration(self, registration_id):
        """Retrieve a registration by ID"""
        try:
            response = requests.get(
                f"{self.api_url}/admin-registration/{registration_id}",
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                return True, response.json()
            else:
                return False, f"HTTP {response.status_code}: {response.text}"
                
        except Exception as e:
            return False, f"Exception: {str(e)}"
    
    def update_registration_full(self, registration_id, update_data):
        """Update a registration with full data (as required by the API)"""
        try:
            # First get the existing registration
            success, existing_data = self.get_registration(registration_id)
            if not success:
                return False, f"Failed to get existing data: {existing_data}"
            
            # Merge the update data with existing data
            full_update_data = {
                "firstName": existing_data.get("firstName"),
                "lastName": existing_data.get("lastName"),
                "patientConsent": existing_data.get("patientConsent"),
                "selectedTemplate": existing_data.get("selectedTemplate", "Select"),
                "summaryTemplate": existing_data.get("summaryTemplate"),
                "province": existing_data.get("province", "Ontario"),
                "language": existing_data.get("language", "English"),
                "physician": existing_data.get("physician", "Dr. David Fletcher"),
                "rnaAvailable": existing_data.get("rnaAvailable", "No"),
                "rnaResult": existing_data.get("rnaResult", "Positive"),
                "coverageType": existing_data.get("coverageType", "Select"),
                "testType": existing_data.get("testType", "Tests"),
                "hivTester": existing_data.get("hivTester", "CM")
            }
            
            # Apply the updates
            full_update_data.update(update_data)
            
            # Remove None values and fields that shouldn't be updated
            clean_data = {}
            for key, value in full_update_data.items():
                if value is not None and key not in ['id', 'timestamp', 'status', 'attachments']:
                    clean_data[key] = value
            
            response = requests.put(
                f"{self.api_url}/admin-registration/{registration_id}",
                json=clean_data,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                return True, response.json()
            else:
                return False, f"HTTP {response.status_code}: {response.text}"
                
        except Exception as e:
            return False, f"Exception: {str(e)}"
    
    def test_1_create_with_default_selected_template(self):
        """Test 1: Create registration with default selectedTemplate"""
        print("\n🧪 TEST 1: Create registration with default selectedTemplate")
        
        success, reg_id, result = self.create_test_registration()
        
        if not success:
            return self.log_test("Create with default selectedTemplate", False, f"Failed to create: {result}")
        
        # Retrieve the registration to check the selectedTemplate field
        success, retrieved_data = self.get_registration(reg_id)
        if not success:
            return self.log_test("Create with default selectedTemplate", False, f"Failed to retrieve: {retrieved_data}")
        
        if retrieved_data.get('selectedTemplate') != 'Select':
            return self.log_test("Create with default selectedTemplate", False, 
                               f"Expected 'Select', got '{retrieved_data.get('selectedTemplate')}'")
        
        return self.log_test("Create with default selectedTemplate", True, 
                           f"Registration ID: {reg_id}, selectedTemplate: '{retrieved_data.get('selectedTemplate')}'")
    
    def test_2_create_with_specific_selected_template(self):
        """Test 2: Create registration with specific selectedTemplate values"""
        print("\n🧪 TEST 2: Create registration with specific selectedTemplate values")
        
        template_values = ["Positive", "Negative - Pipes", "Custom Template", "Another Template"]
        all_passed = True
        
        for template_value in template_values:
            success, reg_id, result = self.create_test_registration(selected_template=template_value)
            
            if not success:
                self.log_test(f"Create with selectedTemplate '{template_value}'", False, f"Failed to create: {result}")
                all_passed = False
                continue
            
            # Retrieve to verify
            success, retrieved_data = self.get_registration(reg_id)
            if not success:
                self.log_test(f"Create with selectedTemplate '{template_value}'", False, f"Failed to retrieve: {retrieved_data}")
                all_passed = False
                continue
            
            if retrieved_data.get('selectedTemplate') != template_value:
                self.log_test(f"Create with selectedTemplate '{template_value}'", False, 
                            f"Expected '{template_value}', got '{retrieved_data.get('selectedTemplate')}'")
                all_passed = False
                continue
            
            self.log_test(f"Create with selectedTemplate '{template_value}'", True, 
                        f"Registration ID: {reg_id}")
        
        return all_passed
    
    def test_3_create_with_both_templates(self):
        """Test 3: Create registration with both summaryTemplate content AND selectedTemplate"""
        print("\n🧪 TEST 3: Create registration with both summaryTemplate content AND selectedTemplate")
        
        summary_content = "This is a test clinical summary template content."
        selected_template = "Positive"
        
        success, reg_id, result = self.create_test_registration(
            selected_template=selected_template,
            summary_template=summary_content
        )
        
        if not success:
            return self.log_test("Create with both templates", False, f"Failed to create: {result}")
        
        # Retrieve to verify both fields
        success, retrieved_data = self.get_registration(reg_id)
        if not success:
            return self.log_test("Create with both templates", False, f"Failed to retrieve: {retrieved_data}")
        
        if retrieved_data.get('selectedTemplate') != selected_template:
            return self.log_test("Create with both templates", False, 
                               f"selectedTemplate: Expected '{selected_template}', got '{retrieved_data.get('selectedTemplate')}'")
        
        if retrieved_data.get('summaryTemplate') != summary_content:
            return self.log_test("Create with both templates", False, 
                               f"summaryTemplate: Expected content not found. Got: '{retrieved_data.get('summaryTemplate')}'")
        
        return self.log_test("Create with both templates", True, 
                           f"Both fields saved correctly. Registration ID: {reg_id}")
    
    def test_4_retrieve_and_verify_persistence(self):
        """Test 4: Retrieve registration and confirm selectedTemplate field is returned correctly"""
        print("\n🧪 TEST 4: Retrieve registration and verify selectedTemplate persistence")
        
        # Create a registration with specific selectedTemplate
        template_value = "Negative - Pipes"
        success, reg_id, create_result = self.create_test_registration(selected_template=template_value)
        
        if not success:
            return self.log_test("Retrieve and verify persistence", False, f"Failed to create: {create_result}")
        
        # Retrieve the registration
        success, get_result = self.get_registration(reg_id)
        
        if not success:
            return self.log_test("Retrieve and verify persistence", False, f"Failed to retrieve: {get_result}")
        
        # Verify selectedTemplate is persisted correctly
        if get_result.get('selectedTemplate') != template_value:
            return self.log_test("Retrieve and verify persistence", False, 
                               f"Expected '{template_value}', got '{get_result.get('selectedTemplate')}'")
        
        return self.log_test("Retrieve and verify persistence", True, 
                           f"selectedTemplate correctly persisted as '{template_value}'")
    
    def test_5_update_selected_template(self):
        """Test 5: Test updating a registration with different selectedTemplate values"""
        print("\n🧪 TEST 5: Update registration with different selectedTemplate values")
        
        # Create initial registration
        initial_template = "Select"
        success, reg_id, create_result = self.create_test_registration(selected_template=initial_template)
        
        if not success:
            return self.log_test("Update selectedTemplate", False, f"Failed to create: {create_result}")
        
        # Update with different selectedTemplate values
        update_templates = ["Positive", "Negative - Pipes", "Custom Update"]
        all_passed = True
        
        for new_template in update_templates:
            update_data = {"selectedTemplate": new_template}
            success, update_result = self.update_registration_full(reg_id, update_data)
            
            if not success:
                self.log_test(f"Update to '{new_template}'", False, f"Failed to update: {update_result}")
                all_passed = False
                continue
            
            # Verify the update
            success, get_result = self.get_registration(reg_id)
            if not success:
                self.log_test(f"Update to '{new_template}'", False, f"Failed to retrieve after update: {get_result}")
                all_passed = False
                continue
            
            if get_result.get('selectedTemplate') != new_template:
                self.log_test(f"Update to '{new_template}'", False, 
                            f"Expected '{new_template}', got '{get_result.get('selectedTemplate')}'")
                all_passed = False
                continue
            
            self.log_test(f"Update to '{new_template}'", True, "Successfully updated and verified")
        
        return all_passed
    
    def test_6_valid_template_names(self):
        """Test 6: Confirm the field accepts valid template names"""
        print("\n🧪 TEST 6: Test valid template names acceptance")
        
        valid_templates = [
            "Select",
            "Positive", 
            "Negative - Pipes",
            "Custom Template Name",
            "Template with Numbers 123",
            "Template-with-dashes",
            "Template_with_underscores"
        ]
        
        all_passed = True
        
        for template_name in valid_templates:
            success, reg_id, result = self.create_test_registration(selected_template=template_name)
            
            if not success:
                self.log_test(f"Valid template '{template_name}'", False, f"Failed to create: {result}")
                all_passed = False
                continue
            
            # Retrieve to verify
            success, retrieved_data = self.get_registration(reg_id)
            if not success:
                self.log_test(f"Valid template '{template_name}'", False, f"Failed to retrieve: {retrieved_data}")
                all_passed = False
                continue
            
            if retrieved_data.get('selectedTemplate') != template_name:
                self.log_test(f"Valid template '{template_name}'", False, 
                            f"Expected '{template_name}', got '{retrieved_data.get('selectedTemplate')}'")
                all_passed = False
                continue
            
            self.log_test(f"Valid template '{template_name}'", True, "Accepted and saved correctly")
        
        return all_passed
    
    def test_7_backwards_compatibility(self):
        """Test 7: Verify backwards compatibility - older records without selectedTemplate still work"""
        print("\n🧪 TEST 7: Test backwards compatibility")
        
        # Create registration without selectedTemplate field (simulating old record)
        unique_id = str(uuid.uuid4())[:8]
        
        registration_data = {
            "firstName": f"OldRecord{unique_id}",
            "lastName": f"BackwardsCompat{unique_id}",
            "patientConsent": "verbal"
            # Note: No selectedTemplate field included
        }
        
        try:
            response = requests.post(
                f"{self.api_url}/admin-register",
                json=registration_data,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code != 200:
                return self.log_test("Backwards compatibility", False, f"HTTP {response.status_code}: {response.text}")
            
            result = response.json()
            reg_id = result.get('registration_id')
            
            if not reg_id:
                return self.log_test("Backwards compatibility", False, "No registration_id in response")
            
            self.created_registrations.append(reg_id)
            
            # Retrieve the record to check selectedTemplate default
            success, get_result = self.get_registration(reg_id)
            if not success:
                return self.log_test("Backwards compatibility", False, f"Failed to retrieve: {get_result}")
            
            expected_default = "Select"
            if get_result.get('selectedTemplate') != expected_default:
                return self.log_test("Backwards compatibility", False, 
                                   f"Expected default '{expected_default}', got '{get_result.get('selectedTemplate')}'")
            
            return self.log_test("Backwards compatibility", True, 
                               f"Old records work correctly with default selectedTemplate: '{expected_default}'")
            
        except Exception as e:
            return self.log_test("Backwards compatibility", False, f"Exception: {str(e)}")
    
    def test_8_comprehensive_workflow(self):
        """Test 8: Comprehensive workflow test"""
        print("\n🧪 TEST 8: Comprehensive workflow test")
        
        # Step 1: Create with specific template
        template1 = "Positive"
        summary1 = "Initial positive template content"
        
        success, reg_id, result = self.create_test_registration(
            selected_template=template1,
            summary_template=summary1
        )
        
        if not success:
            return self.log_test("Comprehensive workflow - Create", False, f"Failed to create: {result}")
        
        # Step 2: Verify creation by retrieving
        success, initial_data = self.get_registration(reg_id)
        if not success:
            return self.log_test("Comprehensive workflow - Verify creation", False, f"Failed to retrieve: {initial_data}")
        
        if initial_data.get('selectedTemplate') != template1 or initial_data.get('summaryTemplate') != summary1:
            return self.log_test("Comprehensive workflow - Verify creation", False, 
                               f"Initial values not correct. selectedTemplate: '{initial_data.get('selectedTemplate')}', summaryTemplate: '{initial_data.get('summaryTemplate')}'")
        
        # Step 3: Update selectedTemplate only
        template2 = "Negative - Pipes"
        update_data = {"selectedTemplate": template2}
        success, update_result = self.update_registration_full(reg_id, update_data)
        
        if not success:
            return self.log_test("Comprehensive workflow - Update selectedTemplate", False, f"Failed to update: {update_result}")
        
        # Step 4: Verify update preserved summaryTemplate but changed selectedTemplate
        success, get_result = self.get_registration(reg_id)
        if not success:
            return self.log_test("Comprehensive workflow - Verify update", False, f"Failed to retrieve: {get_result}")
        
        if get_result.get('selectedTemplate') != template2:
            return self.log_test("Comprehensive workflow - Verify selectedTemplate update", False, 
                               f"Expected '{template2}', got '{get_result.get('selectedTemplate')}'")
        
        if get_result.get('summaryTemplate') != summary1:
            return self.log_test("Comprehensive workflow - Verify summaryTemplate preserved", False, 
                               f"summaryTemplate was not preserved during selectedTemplate update. Expected: '{summary1}', Got: '{get_result.get('summaryTemplate')}'")
        
        # Step 5: Update both fields
        template3 = "Custom Final"
        summary3 = "Updated summary content"
        update_data = {"selectedTemplate": template3, "summaryTemplate": summary3}
        success, update_result = self.update_registration_full(reg_id, update_data)
        
        if not success:
            return self.log_test("Comprehensive workflow - Update both fields", False, f"Failed to update: {update_result}")
        
        # Step 6: Final verification
        success, final_result = self.get_registration(reg_id)
        if not success:
            return self.log_test("Comprehensive workflow - Final verification", False, f"Failed to retrieve: {final_result}")
        
        if final_result.get('selectedTemplate') != template3 or final_result.get('summaryTemplate') != summary3:
            return self.log_test("Comprehensive workflow - Final verification", False, 
                               f"Final values incorrect. selectedTemplate: '{final_result.get('selectedTemplate')}', summaryTemplate: '{final_result.get('summaryTemplate')}'")
        
        return self.log_test("Comprehensive workflow", True, 
                           "Complete workflow successful: Create → Update selectedTemplate → Update both fields")
    
    def cleanup(self):
        """Clean up created test registrations"""
        print(f"\n🧹 Cleaning up {len(self.created_registrations)} test registrations...")
        cleaned = 0
        
        for reg_id in self.created_registrations:
            try:
                response = requests.delete(
                    f"{self.api_url}/admin-registration/{reg_id}",
                    headers={'Content-Type': 'application/json'}
                )
                if response.status_code in [200, 204, 404]:  # 404 is OK if already deleted
                    cleaned += 1
            except:
                pass  # Ignore cleanup errors
        
        print(f"✅ Cleaned up {cleaned}/{len(self.created_registrations)} test registrations")
    
    def run_all_tests(self):
        """Run all selectedTemplate field tests"""
        print("🚀 STARTING CORRECTED SELECTED TEMPLATE FIELD TESTING SUITE")
        print("=" * 70)
        print(f"Testing against: {self.api_url}")
        print("=" * 70)
        
        try:
            # Run all tests
            self.test_1_create_with_default_selected_template()
            self.test_2_create_with_specific_selected_template()
            self.test_3_create_with_both_templates()
            self.test_4_retrieve_and_verify_persistence()
            self.test_5_update_selected_template()
            self.test_6_valid_template_names()
            self.test_7_backwards_compatibility()
            self.test_8_comprehensive_workflow()
            
        finally:
            # Always cleanup
            self.cleanup()
        
        # Print summary
        print("\n" + "=" * 70)
        print("📊 SELECTED TEMPLATE FIELD TEST SUMMARY")
        print("=" * 70)
        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Tests Failed: {self.tests_run - self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%" if self.tests_run > 0 else "No tests run")
        
        if self.tests_passed == self.tests_run:
            print("🎉 ALL TESTS PASSED! selectedTemplate field functionality is working correctly.")
            return True
        else:
            print("⚠️  SOME TESTS FAILED! selectedTemplate field functionality needs attention.")
            return False

if __name__ == "__main__":
    tester = CorrectedSelectedTemplateFieldTester()
    success = tester.run_all_tests()
    exit(0 if success else 1)