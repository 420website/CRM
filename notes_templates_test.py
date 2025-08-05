#!/usr/bin/env python3

"""
Comprehensive Notes Template API Testing
Tests the newly implemented Notes Template functionality to ensure it works identically to Clinical Summary Templates.

Test Requirements:
1. Notes Template API Testing (5 endpoints)
2. Default Templates Verification (Consultation, Lab, Prescription)
3. Identical Functionality to Clinical Templates
4. Integration Testing and Database Persistence
"""

import requests
import json
import sys
import os
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://46471c8a-a981-4b23-bca9-bb5c0ba282bc.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

class NotesTemplatesTester:
    def __init__(self):
        self.test_results = []
        self.failed_tests = []
        
    def log_test(self, test_name, success, details=""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = f"{status}: {test_name}"
        if details:
            result += f" - {details}"
        
        print(result)
        self.test_results.append({
            'test': test_name,
            'success': success,
            'details': details,
            'timestamp': datetime.now().isoformat()
        })
        
        if not success:
            self.failed_tests.append(test_name)
    
    def test_health_check(self):
        """Test basic API connectivity"""
        try:
            response = requests.get(f"{API_BASE}/health", timeout=10)
            success = response.status_code == 200
            self.log_test("API Health Check", success, f"Status: {response.status_code}")
            return success
        except Exception as e:
            self.log_test("API Health Check", False, f"Error: {str(e)}")
            return False
    
    def test_get_all_notes_templates(self):
        """Test GET /api/notes-templates - retrieve all Notes templates"""
        try:
            response = requests.get(f"{API_BASE}/notes-templates", timeout=10)
            
            if response.status_code == 200:
                templates = response.json()
                
                # Verify response structure
                if isinstance(templates, list):
                    # Check for default templates
                    template_names = [t.get('name', '') for t in templates]
                    expected_defaults = ['Consultation', 'Lab', 'Prescription']
                    
                    defaults_found = []
                    for default in expected_defaults:
                        if default in template_names:
                            defaults_found.append(default)
                    
                    success = len(defaults_found) >= 3
                    details = f"Found {len(templates)} templates, defaults: {defaults_found}"
                    self.log_test("GET /api/notes-templates", success, details)
                    return templates if success else []
                else:
                    self.log_test("GET /api/notes-templates", False, "Response is not a list")
                    return []
            else:
                self.log_test("GET /api/notes-templates", False, f"Status: {response.status_code}")
                return []
                
        except Exception as e:
            self.log_test("GET /api/notes-templates", False, f"Error: {str(e)}")
            return []
    
    def test_create_notes_template(self):
        """Test POST /api/notes-templates - create single Notes template"""
        try:
            test_template = {
                "name": "Test Template",
                "content": "This is a test template for Notes functionality",
                "is_default": False
            }
            
            response = requests.post(
                f"{API_BASE}/notes-templates",
                json=test_template,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                created_template = response.json()
                
                # Verify response structure
                required_fields = ['id', 'name', 'content', 'is_default', 'created_at', 'updated_at']
                has_all_fields = all(field in created_template for field in required_fields)
                
                # Verify content matches
                content_matches = (
                    created_template.get('name') == test_template['name'] and
                    created_template.get('content') == test_template['content'] and
                    created_template.get('is_default') == test_template['is_default']
                )
                
                success = has_all_fields and content_matches
                details = f"Created template ID: {created_template.get('id', 'N/A')}"
                self.log_test("POST /api/notes-templates", success, details)
                return created_template if success else None
            else:
                self.log_test("POST /api/notes-templates", False, f"Status: {response.status_code}")
                return None
                
        except Exception as e:
            self.log_test("POST /api/notes-templates", False, f"Error: {str(e)}")
            return None
    
    def test_update_notes_template(self, template_id):
        """Test PUT /api/notes-templates/{id} - update Notes template"""
        if not template_id:
            self.log_test("PUT /api/notes-templates/{id}", False, "No template ID provided")
            return False
            
        try:
            update_data = {
                "name": "Updated Test Template",
                "content": "This template has been updated successfully"
            }
            
            response = requests.put(
                f"{API_BASE}/notes-templates/{template_id}",
                json=update_data,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                updated_template = response.json()
                
                # Verify updates were applied
                name_updated = updated_template.get('name') == update_data['name']
                content_updated = updated_template.get('content') == update_data['content']
                has_updated_timestamp = 'updated_at' in updated_template
                
                success = name_updated and content_updated and has_updated_timestamp
                details = f"Updated template: {updated_template.get('name', 'N/A')}"
                self.log_test("PUT /api/notes-templates/{id}", success, details)
                return success
            else:
                self.log_test("PUT /api/notes-templates/{id}", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("PUT /api/notes-templates/{id}", False, f"Error: {str(e)}")
            return False
    
    def test_delete_notes_template(self, template_id):
        """Test DELETE /api/notes-templates/{id} - delete Notes template"""
        if not template_id:
            self.log_test("DELETE /api/notes-templates/{id}", False, "No template ID provided")
            return False
            
        try:
            response = requests.delete(f"{API_BASE}/notes-templates/{template_id}", timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                success = 'message' in result and 'deleted' in result['message'].lower()
                details = result.get('message', 'Template deleted')
                self.log_test("DELETE /api/notes-templates/{id}", success, details)
                return success
            else:
                self.log_test("DELETE /api/notes-templates/{id}", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("DELETE /api/notes-templates/{id}", False, f"Error: {str(e)}")
            return False
    
    def test_bulk_save_notes_templates(self):
        """Test POST /api/notes-templates/save-all - bulk save Notes templates"""
        try:
            bulk_templates = {
                "Bulk Test 1": "Content for bulk test template 1",
                "Bulk Test 2": "Content for bulk test template 2",
                "Bulk Test 3": "Content for bulk test template 3"
            }
            
            response = requests.post(
                f"{API_BASE}/notes-templates/save-all",
                json=bulk_templates,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Verify response structure
                has_message = 'message' in result
                has_count = 'count' in result
                correct_count = result.get('count', 0) == len(bulk_templates)
                
                success = has_message and has_count and correct_count
                details = f"Saved {result.get('count', 0)} templates"
                self.log_test("POST /api/notes-templates/save-all", success, details)
                return success
            else:
                self.log_test("POST /api/notes-templates/save-all", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("POST /api/notes-templates/save-all", False, f"Error: {str(e)}")
            return False
    
    def test_default_templates_verification(self):
        """Verify default Notes templates exist with correct structure"""
        try:
            response = requests.get(f"{API_BASE}/notes-templates", timeout=10)
            
            if response.status_code == 200:
                templates = response.json()
                expected_defaults = ['Consultation', 'Lab', 'Prescription']
                
                found_defaults = {}
                for template in templates:
                    if template.get('name') in expected_defaults:
                        found_defaults[template['name']] = template
                
                # Verify all defaults exist
                all_defaults_exist = len(found_defaults) == len(expected_defaults)
                
                # Verify structure of default templates
                structure_valid = True
                for name, template in found_defaults.items():
                    required_fields = ['id', 'name', 'content', 'is_default', 'created_at', 'updated_at']
                    if not all(field in template for field in required_fields):
                        structure_valid = False
                        break
                
                success = all_defaults_exist and structure_valid
                details = f"Found defaults: {list(found_defaults.keys())}"
                self.log_test("Default Templates Verification", success, details)
                return success
            else:
                self.log_test("Default Templates Verification", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Default Templates Verification", False, f"Error: {str(e)}")
            return False
    
    def test_clinical_vs_notes_comparison(self):
        """Compare Clinical Templates and Notes Templates API structure"""
        try:
            # Get Clinical Templates
            clinical_response = requests.get(f"{API_BASE}/clinical-templates", timeout=10)
            notes_response = requests.get(f"{API_BASE}/notes-templates", timeout=10)
            
            if clinical_response.status_code == 200 and notes_response.status_code == 200:
                clinical_templates = clinical_response.json()
                notes_templates = notes_response.json()
                
                # Compare structure
                if clinical_templates and notes_templates:
                    clinical_fields = set(clinical_templates[0].keys()) if clinical_templates else set()
                    notes_fields = set(notes_templates[0].keys()) if notes_templates else set()
                    
                    # Should have identical structure
                    identical_structure = clinical_fields == notes_fields
                    
                    success = identical_structure
                    details = f"Clinical fields: {len(clinical_fields)}, Notes fields: {len(notes_fields)}"
                    self.log_test("Clinical vs Notes API Comparison", success, details)
                    return success
                else:
                    self.log_test("Clinical vs Notes API Comparison", False, "Empty template lists")
                    return False
            else:
                self.log_test("Clinical vs Notes API Comparison", False, "Failed to fetch templates")
                return False
                
        except Exception as e:
            self.log_test("Clinical vs Notes API Comparison", False, f"Error: {str(e)}")
            return False
    
    def test_database_persistence(self):
        """Test that Notes templates persist in database"""
        try:
            # Create a persistence test template
            test_template = {
                "name": "Persistence Test",
                "content": "This template tests database persistence",
                "is_default": False
            }
            
            # Create template
            create_response = requests.post(
                f"{API_BASE}/notes-templates",
                json=test_template,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if create_response.status_code == 200:
                created_template = create_response.json()
                template_id = created_template.get('id')
                
                # Retrieve all templates to verify persistence
                get_response = requests.get(f"{API_BASE}/notes-templates", timeout=10)
                
                if get_response.status_code == 200:
                    all_templates = get_response.json()
                    
                    # Check if our template exists
                    template_exists = any(
                        t.get('id') == template_id and t.get('name') == test_template['name']
                        for t in all_templates
                    )
                    
                    # Clean up - delete the test template
                    if template_id:
                        requests.delete(f"{API_BASE}/notes-templates/{template_id}", timeout=10)
                    
                    success = template_exists
                    details = f"Template persisted with ID: {template_id}"
                    self.log_test("Database Persistence Test", success, details)
                    return success
                else:
                    self.log_test("Database Persistence Test", False, "Failed to retrieve templates")
                    return False
            else:
                self.log_test("Database Persistence Test", False, "Failed to create test template")
                return False
                
        except Exception as e:
            self.log_test("Database Persistence Test", False, f"Error: {str(e)}")
            return False
    
    def run_comprehensive_test(self):
        """Run all Notes Template tests"""
        print("🧪 NOTES TEMPLATE FUNCTIONALITY TESTING")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"API Base: {API_BASE}")
        print("=" * 60)
        
        # Test 1: Get all Notes templates (includes default verification)
        templates = self.test_get_all_notes_templates()
        
        # Test 2: Default templates verification
        self.test_default_templates_verification()
        
        # Test 3: Create Notes template
        created_template = self.test_create_notes_template()
        template_id = created_template.get('id') if created_template else None
        
        # Test 4: Update Notes template
        if template_id:
            self.test_update_notes_template(template_id)
        
        # Test 5: Bulk save Notes templates
        self.test_bulk_save_notes_templates()
        
        # Test 6: Clinical vs Notes comparison
        self.test_clinical_vs_notes_comparison()
        
        # Test 7: Database persistence
        self.test_database_persistence()
        
        # Test 8: Delete Notes template (cleanup)
        if template_id:
            self.test_delete_notes_template(template_id)
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if self.failed_tests:
            print(f"\n❌ Failed Tests:")
            for test in self.failed_tests:
                print(f"  - {test}")
        
        # Overall result
        overall_success = failed_tests == 0
        status = "✅ ALL TESTS PASSED" if overall_success else "❌ SOME TESTS FAILED"
        print(f"\n{status}")
        
        return overall_success

def main():
    """Main test execution"""
    tester = NotesTemplatesTester()
    success = tester.run_comprehensive_test()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()