#!/usr/bin/env python3
"""
Notes Template Save/Load Functionality Test
Specifically testing the template saving functionality as requested in the review.
"""

import requests
import json
import sys
from datetime import datetime

class NotesTemplateTester:
    def __init__(self, base_url):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def log_test(self, test_name, success, details=""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            status = "✅ PASS"
        else:
            status = "❌ FAIL"
        
        result = f"{status} - {test_name}"
        if details:
            result += f" | {details}"
        
        print(result)
        self.test_results.append(result)
        return success

    def test_get_notes_templates(self):
        """Test 1: GET /api/notes-templates - verify templates load correctly"""
        try:
            response = requests.get(f"{self.base_url}/api/notes-templates")
            
            if response.status_code == 200:
                templates = response.json()
                
                # Verify response is a list
                if not isinstance(templates, list):
                    return self.log_test("GET notes-templates returns list", False, f"Expected list, got {type(templates)}")
                
                # Check for default templates
                template_names = [t.get('name') for t in templates]
                expected_defaults = ['Consultation', 'Lab', 'Prescription']
                
                defaults_found = []
                for expected in expected_defaults:
                    if expected in template_names:
                        defaults_found.append(expected)
                
                details = f"Found {len(templates)} templates: {template_names}. Defaults found: {defaults_found}"
                
                # Verify template structure
                if templates:
                    first_template = templates[0]
                    required_fields = ['id', 'name', 'content', 'is_default', 'created_at', 'updated_at']
                    missing_fields = [field for field in required_fields if field not in first_template]
                    
                    if missing_fields:
                        return self.log_test("GET notes-templates structure", False, f"Missing fields: {missing_fields}")
                
                return self.log_test("GET notes-templates", True, details)
            else:
                return self.log_test("GET notes-templates", False, f"Status {response.status_code}: {response.text}")
                
        except Exception as e:
            return self.log_test("GET notes-templates", False, f"Exception: {str(e)}")

    def test_save_all_notes_templates(self):
        """Test 2: POST /api/notes-templates/save-all - test template saving"""
        try:
            # Test payload as specified in the review request
            test_payload = {
                "Consultation": "Test consultation template content"
            }
            
            response = requests.post(
                f"{self.base_url}/api/notes-templates/save-all",
                json=test_payload,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Verify response structure
                if 'message' in result and 'count' in result:
                    templates_saved = result.get('count', 0)
                    details = f"Message: {result['message']}, Templates saved: {templates_saved}"
                    return self.log_test("POST save-all templates", True, details)
                else:
                    return self.log_test("POST save-all templates", False, f"Invalid response structure: {result}")
            else:
                return self.log_test("POST save-all templates", False, f"Status {response.status_code}: {response.text}")
                
        except Exception as e:
            return self.log_test("POST save-all templates", False, f"Exception: {str(e)}")

    def test_verify_template_saved(self):
        """Test 3: Verify the template is actually saved and can be retrieved"""
        try:
            # Get all templates again to verify our save worked
            response = requests.get(f"{self.base_url}/api/notes-templates")
            
            if response.status_code == 200:
                templates = response.json()
                
                # Look for our test template
                consultation_template = None
                for template in templates:
                    if template.get('name') == 'Consultation':
                        consultation_template = template
                        break
                
                if consultation_template:
                    # Check if content was updated
                    content = consultation_template.get('content', '')
                    expected_content = "Test consultation template content"
                    
                    if content == expected_content:
                        details = f"Template found with correct content: '{content}'"
                        return self.log_test("Verify template saved", True, details)
                    else:
                        details = f"Template found but content mismatch. Expected: '{expected_content}', Got: '{content}'"
                        return self.log_test("Verify template saved", False, details)
                else:
                    available_names = [t.get('name') for t in templates]
                    return self.log_test("Verify template saved", False, f"Consultation template not found. Available: {available_names}")
            else:
                return self.log_test("Verify template saved", False, f"Status {response.status_code}: {response.text}")
                
        except Exception as e:
            return self.log_test("Verify template saved", False, f"Exception: {str(e)}")

    def test_template_persistence(self):
        """Test 4: Test template persistence with multiple saves"""
        try:
            # Save multiple templates
            test_payload = {
                "Consultation": "Updated consultation content",
                "Lab": "Updated lab content", 
                "Prescription": "Updated prescription content"
            }
            
            response = requests.post(
                f"{self.base_url}/api/notes-templates/save-all",
                json=test_payload,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code != 200:
                return self.log_test("Template persistence save", False, f"Save failed: {response.status_code}")
            
            # Verify all templates were saved
            response = requests.get(f"{self.base_url}/api/notes-templates")
            if response.status_code == 200:
                templates = response.json()
                template_dict = {t['name']: t['content'] for t in templates}
                
                success_count = 0
                for name, expected_content in test_payload.items():
                    if name in template_dict and template_dict[name] == expected_content:
                        success_count += 1
                
                if success_count == len(test_payload):
                    details = f"All {success_count} templates saved correctly"
                    return self.log_test("Template persistence", True, details)
                else:
                    details = f"Only {success_count}/{len(test_payload)} templates saved correctly"
                    return self.log_test("Template persistence", False, details)
            else:
                return self.log_test("Template persistence", False, f"Verification failed: {response.status_code}")
                
        except Exception as e:
            return self.log_test("Template persistence", False, f"Exception: {str(e)}")

    def test_template_save_load_cycle(self):
        """Test 5: Complete save/load cycle with edge cases"""
        try:
            # Test with special characters and longer content
            test_payload = {
                "Consultation": "Patient consultation notes:\\n- Symptoms: fever, cough\\n- Diagnosis: viral infection\\n- Treatment: rest & fluids\\n\\nSpecial chars: @#$%^&*()",
                "Lab": "Lab results template with unicode: Normal Abnormal Follow-up required",
                "Custom Template": "This is a custom template with mixed content"
            }
            
            # Save templates
            save_response = requests.post(
                f"{self.base_url}/api/notes-templates/save-all",
                json=test_payload,
                headers={'Content-Type': 'application/json'}
            )
            
            if save_response.status_code != 200:
                return self.log_test("Save/Load cycle - Save", False, f"Save failed: {save_response.status_code}")
            
            # Load and verify
            load_response = requests.get(f"{self.base_url}/api/notes-templates")
            if load_response.status_code == 200:
                templates = load_response.json()
                template_dict = {t['name']: t['content'] for t in templates}
                
                verification_results = []
                for name, expected_content in test_payload.items():
                    if name in template_dict:
                        if template_dict[name] == expected_content:
                            verification_results.append(f"✓ {name}")
                        else:
                            verification_results.append(f"✗ {name} (content mismatch)")
                    else:
                        verification_results.append(f"✗ {name} (not found)")
                
                all_passed = all("✓" in result for result in verification_results)
                details = f"Results: {', '.join(verification_results)}"
                
                return self.log_test("Save/Load cycle", all_passed, details)
            else:
                return self.log_test("Save/Load cycle - Load", False, f"Load failed: {load_response.status_code}")
                
        except Exception as e:
            return self.log_test("Save/Load cycle", False, f"Exception: {str(e)}")

    def run_all_tests(self):
        """Run all Notes Template tests"""
        print("🧪 NOTES TEMPLATE SAVE/LOAD FUNCTIONALITY TEST")
        print("=" * 60)
        print(f"Testing against: {self.base_url}")
        print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()

        # Run tests in sequence
        self.test_get_notes_templates()
        self.test_save_all_notes_templates()
        self.test_verify_template_saved()
        self.test_template_persistence()
        self.test_template_save_load_cycle()

        # Summary
        print("\\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        for result in self.test_results:
            print(result)
        
        print(f"\\nTotal Tests: {self.tests_run}")
        print(f"Passed: {self.tests_passed}")
        print(f"Failed: {self.tests_run - self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        if self.tests_passed == self.tests_run:
            print("\\n🎉 ALL TESTS PASSED - Notes Template functionality is working correctly!")
            return True
        else:
            print(f"\\n⚠️  {self.tests_run - self.tests_passed} TEST(S) FAILED - Notes Template functionality has issues")
            return False

def main():
    # Get backend URL from environment
    try:
        with open('/app/frontend/.env', 'r') as f:
            for line in f:
                if line.startswith('REACT_APP_BACKEND_URL='):
                    base_url = line.split('=')[1].strip()
                    break
            else:
                base_url = "https://cd556dd9-d36b-422e-8110-4b1830397661.preview.emergentagent.com"
    except:
        base_url = "https://cd556dd9-d36b-422e-8110-4b1830397661.preview.emergentagent.com"
    
    print(f"Using backend URL: {base_url}")
    
    # Run tests
    tester = NotesTemplateTester(base_url)
    success = tester.run_all_tests()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()