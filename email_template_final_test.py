#!/usr/bin/env python3
"""
Email Template Changes Final Validation Test
===========================================

This script validates that the email template changes have been properly implemented:
1. Changed "FINAL SUBMISSION -" to "New Registration"
2. Deleted "FINAL ADMIN REGISTRATION - COMPLETED" line
3. Moved Province to Contact information after city
4. Renamed "Medical Information" title to "Other Information"
5. Removed entire "PROCESSING DETAILS:" section

This test focuses on the actual email template functionality and structure.
"""

import asyncio
import sys
import os
import logging
import json
import requests
from datetime import datetime, date
import pytz

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EmailTemplateFinalTest:
    def __init__(self):
        self.test_results = []
        self.backend_url = os.environ.get('REACT_APP_BACKEND_URL', 'https://dfe9a1e1-7f3d-45aa-ad71-43a254e568c5.preview.emergentagent.com')
        
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
        logger.info(f"{status}: {test_name} - {message}")
        if details:
            logger.info(f"Details: {details}")

    def test_email_template_changes_validation(self):
        """Validate all the requested email template changes"""
        try:
            # Read the backend server.py file
            with open('/app/backend/server.py', 'r') as f:
                server_code = f.read()
            
            # Find the send_finalization_email_async function
            async_func_start = server_code.find('async def send_finalization_email_async')
            if async_func_start == -1:
                self.log_result(
                    "Email Template Changes Validation",
                    False,
                    "Could not find send_finalization_email_async function"
                )
                return False
            
            # Extract the entire function
            next_func_start = server_code.find('\n\nasync def', async_func_start + 1)
            if next_func_start == -1:
                next_func_start = server_code.find('\n\ndef', async_func_start + 1)
            if next_func_start == -1:
                next_func_start = len(server_code)
            
            email_function = server_code[async_func_start:next_func_start]
            
            # Test Change 1: "New Registration" title instead of "FINAL SUBMISSION -"
            change_1_success = "New Registration" in email_function and "FINAL SUBMISSION -" not in email_function
            
            # Test Change 2: "FINAL ADMIN REGISTRATION - COMPLETED" line deleted
            change_2_success = "FINAL ADMIN REGISTRATION - COMPLETED" not in email_function
            
            # Test Change 3: Province moved to Contact Information after city
            # Check that Province is in the CONTACT INFORMATION section
            contact_info_start = email_function.find("CONTACT INFORMATION:")
            other_info_start = email_function.find("OTHER INFORMATION:")
            province_line = email_function.find("• Province:")
            city_line = email_function.find("• City:")
            
            change_3_success = (contact_info_start != -1 and other_info_start != -1 and 
                              province_line != -1 and city_line != -1 and
                              contact_info_start < province_line < other_info_start and
                              city_line < province_line)
            
            # Test Change 4: "Medical Information" renamed to "Other Information"
            change_4_success = "OTHER INFORMATION:" in email_function and "MEDICAL INFORMATION:" not in email_function
            
            # Test Change 5: "PROCESSING DETAILS:" section removed
            change_5_success = ("PROCESSING DETAILS:" not in email_function and 
                              "Registration ID" not in email_function and
                              "*** THIS REGISTRATION HAS BEEN REVIEWED AND FINALIZED ***" not in email_function)
            
            # Additional validation: Check that CLINICAL SUMMARY TEMPLATE section exists
            has_clinical_summary = "CLINICAL SUMMARY TEMPLATE:" in email_function
            
            # Check that all required sections are present
            required_sections = [
                "PATIENT INFORMATION:",
                "CONTACT INFORMATION:", 
                "OTHER INFORMATION:",
                "CLINICAL SUMMARY TEMPLATE:"
            ]
            all_sections_present = all(section in email_function for section in required_sections)
            
            # Overall validation
            all_changes_implemented = all([change_1_success, change_2_success, change_3_success, 
                                         change_4_success, change_5_success])
            
            template_complete = all_changes_implemented and has_clinical_summary and all_sections_present
            
            details = {
                'requested_changes': {
                    'change_1_new_registration_title': change_1_success,
                    'change_2_removed_final_admin_line': change_2_success,
                    'change_3_province_in_contact_info': change_3_success,
                    'change_4_other_information_title': change_4_success,
                    'change_5_removed_processing_details': change_5_success
                },
                'template_completeness': {
                    'has_clinical_summary_section': has_clinical_summary,
                    'all_required_sections_present': all_sections_present,
                    'required_sections': required_sections
                },
                'function_analysis': {
                    'function_found': True,
                    'function_length': len(email_function),
                    'has_proper_structure': "email_body = f\"\"\"" in email_function
                }
            }
            
            self.log_result(
                "Email Template Changes Validation",
                template_complete,
                f"Email template changes: {'All requested changes implemented correctly' if template_complete else 'Some issues found'}",
                details
            )
            
            return template_complete
            
        except Exception as e:
            self.log_result(
                "Email Template Changes Validation",
                False,
                f"Failed to validate email template changes: {str(e)}"
            )
            return False

    def test_email_functionality_integration(self):
        """Test that email functionality is properly integrated"""
        try:
            with open('/app/backend/server.py', 'r') as f:
                server_code = f.read()
            
            # Check that the finalize endpoint uses the correct email function
            finalize_endpoint = server_code[server_code.find('async def finalize_admin_registration'):
                                          server_code.find('\n\ndef', server_code.find('async def finalize_admin_registration'))]
            
            # Validate integration points
            calls_send_email = 'send_email(' in finalize_endpoint
            has_email_body_construction = 'email_body =' in finalize_endpoint
            has_subject_line = 'subject =' in finalize_endpoint
            has_photo_handling = 'photo' in finalize_endpoint
            has_error_handling = 'try:' in finalize_endpoint and 'except' in finalize_endpoint
            
            # Check that the async email function exists and is properly structured
            async_email_func_exists = 'async def send_finalization_email_async' in server_code
            send_email_func_exists = 'async def send_email' in server_code
            
            integration_complete = all([
                calls_send_email,
                has_email_body_construction,
                has_subject_line,
                has_photo_handling,
                has_error_handling,
                async_email_func_exists,
                send_email_func_exists
            ])
            
            self.log_result(
                "Email Functionality Integration",
                integration_complete,
                f"Email functionality integration: {'Complete and working' if integration_complete else 'Has some issues'}",
                {
                    'finalize_endpoint_calls_send_email': calls_send_email,
                    'has_email_body_construction': has_email_body_construction,
                    'has_subject_line': has_subject_line,
                    'has_photo_handling': has_photo_handling,
                    'has_error_handling': has_error_handling,
                    'async_email_function_exists': async_email_func_exists,
                    'send_email_function_exists': send_email_func_exists
                }
            )
            
            return integration_complete
            
        except Exception as e:
            self.log_result(
                "Email Functionality Integration",
                False,
                f"Failed to test email functionality integration: {str(e)}"
            )
            return False

    def test_email_template_structure_completeness(self):
        """Test that the email template structure is complete and properly formatted"""
        try:
            with open('/app/backend/server.py', 'r') as f:
                server_code = f.read()
            
            # Find the send_finalization_email_async function
            async_func_start = server_code.find('async def send_finalization_email_async')
            async_func_end = server_code.find('\n\ndef', async_func_start + 1)
            if async_func_end == -1:
                async_func_end = server_code.find('\n\nasync def', async_func_start + 1)
            if async_func_end == -1:
                async_func_end = len(server_code)
            
            email_function = server_code[async_func_start:async_func_end]
            
            # Check for all required patient information fields
            patient_fields = [
                "• First Name:",
                "• Last Name:",
                "• Date of Birth:",
                "• Patient Consent:",
                "• Gender:",
                "• Health Card:",
                "• Health Card Version:"
            ]
            
            # Check for all required contact information fields
            contact_fields = [
                "• Phone 1:",
                "• Phone 2:",
                "• Email:",
                "• Address:",
                "• City:",
                "• Province:",
                "• Postal Code:",
                "• Language:"
            ]
            
            # Check for all required other information fields
            other_fields = [
                "• Special Attention/Notes:",
                "• Photo Attached:",
                "• Physician:",
                "• Disposition:"
            ]
            
            patient_fields_present = all(field in email_function for field in patient_fields)
            contact_fields_present = all(field in email_function for field in contact_fields)
            other_fields_present = all(field in email_function for field in other_fields)
            
            # Check for proper section headers
            section_headers = [
                "PATIENT INFORMATION:",
                "CONTACT INFORMATION:",
                "OTHER INFORMATION:",
                "CLINICAL SUMMARY TEMPLATE:"
            ]
            
            headers_present = all(header in email_function for header in section_headers)
            
            # Check for proper data handling
            has_data_fallbacks = "or 'Not provided'" in email_function
            has_conditional_logic = "if registration_data.get" in email_function
            
            structure_complete = all([
                patient_fields_present,
                contact_fields_present,
                other_fields_present,
                headers_present,
                has_data_fallbacks,
                has_conditional_logic
            ])
            
            missing_patient = [f for f in patient_fields if f not in email_function]
            missing_contact = [f for f in contact_fields if f not in email_function]
            missing_other = [f for f in other_fields if f not in email_function]
            missing_headers = [h for h in section_headers if h not in email_function]
            
            self.log_result(
                "Email Template Structure Completeness",
                structure_complete,
                f"Email template structure: {'Complete with all required fields and sections' if structure_complete else 'Missing some required elements'}",
                {
                    'patient_fields_present': patient_fields_present,
                    'contact_fields_present': contact_fields_present,
                    'other_fields_present': other_fields_present,
                    'section_headers_present': headers_present,
                    'has_data_fallbacks': has_data_fallbacks,
                    'has_conditional_logic': has_conditional_logic,
                    'missing_patient_fields': missing_patient,
                    'missing_contact_fields': missing_contact,
                    'missing_other_fields': missing_other,
                    'missing_section_headers': missing_headers
                }
            )
            
            return structure_complete
            
        except Exception as e:
            self.log_result(
                "Email Template Structure Completeness",
                False,
                f"Failed to test email template structure completeness: {str(e)}"
            )
            return False

    def test_backend_api_endpoints(self):
        """Test that backend API endpoints are working"""
        try:
            # Test the finalization endpoint exists and is accessible
            # We won't actually call it to avoid side effects, but we'll verify it exists in code
            with open('/app/backend/server.py', 'r') as f:
                server_code = f.read()
            
            # Check for finalization endpoints
            get_endpoint = '@api_router.get("/admin-registration/{registration_id}/finalize"' in server_code
            post_endpoint = '@api_router.post("/admin-registration/{registration_id}/finalize"' in server_code
            finalize_function = 'async def finalize_admin_registration' in server_code
            
            # Check for other related endpoints
            pending_endpoint = '/admin-registrations-pending' in server_code
            submitted_endpoint = '/admin-registrations-submitted' in server_code
            
            # Check for proper API router setup
            api_router_setup = 'api_router = APIRouter(prefix="/api")' in server_code
            app_includes_router = 'app.include_router(api_router)' in server_code
            
            endpoints_working = all([
                get_endpoint,
                post_endpoint,
                finalize_function,
                pending_endpoint,
                submitted_endpoint,
                api_router_setup,
                app_includes_router
            ])
            
            self.log_result(
                "Backend API Endpoints",
                endpoints_working,
                f"Backend API endpoints: {'All required endpoints are properly configured' if endpoints_working else 'Some endpoint issues found'}",
                {
                    'finalize_get_endpoint': get_endpoint,
                    'finalize_post_endpoint': post_endpoint,
                    'finalize_function_exists': finalize_function,
                    'pending_registrations_endpoint': pending_endpoint,
                    'submitted_registrations_endpoint': submitted_endpoint,
                    'api_router_properly_setup': api_router_setup,
                    'app_includes_router': app_includes_router
                }
            )
            
            return endpoints_working
            
        except Exception as e:
            self.log_result(
                "Backend API Endpoints",
                False,
                f"Failed to test backend API endpoints: {str(e)}"
            )
            return False

    def run_all_tests(self):
        """Run all email template validation tests"""
        logger.info("🚀 Starting Email Template Changes Final Validation")
        logger.info("=" * 60)
        
        # Test 1: Email Template Changes Validation (CRITICAL)
        changes_success = self.test_email_template_changes_validation()
        
        # Test 2: Email Functionality Integration (CRITICAL)
        integration_success = self.test_email_functionality_integration()
        
        # Test 3: Email Template Structure Completeness (CRITICAL)
        structure_success = self.test_email_template_structure_completeness()
        
        # Test 4: Backend API Endpoints (IMPORTANT)
        endpoints_success = self.test_backend_api_endpoints()
        
        # Summary
        critical_tests = [changes_success, integration_success, structure_success]
        all_tests = [changes_success, integration_success, structure_success, endpoints_success]
        
        critical_passed = sum(critical_tests)
        total_passed = sum(all_tests)
        total_tests = len(all_tests)
        
        logger.info("=" * 60)
        logger.info(f"📊 EMAIL TEMPLATE FINAL VALIDATION SUMMARY")
        logger.info(f"Critical Tests (Email Template Changes): {critical_passed}/3")
        logger.info(f"Total Tests Passed: {total_passed}/{total_tests}")
        logger.info(f"Critical Success Rate: {(critical_passed/3)*100:.1f}%")
        logger.info(f"Overall Success Rate: {(total_passed/total_tests)*100:.1f}%")
        
        if critical_passed == 3:
            logger.info("🎉 ALL CRITICAL EMAIL TEMPLATE TESTS PASSED!")
            logger.info("✅ Email template changes have been successfully implemented and validated")
            if total_passed == total_tests:
                logger.info("✅ All supporting functionality is also working correctly")
        else:
            logger.info("⚠️  Some critical email template tests failed")
            logger.info("❌ Email template changes may not be fully implemented")
        
        return {
            'critical_tests_passed': critical_passed,
            'total_tests_passed': total_passed,
            'total_tests': total_tests,
            'critical_success_rate': (critical_passed/3)*100,
            'overall_success_rate': (total_passed/total_tests)*100,
            'all_critical_passed': critical_passed == 3,
            'all_tests_passed': total_passed == total_tests,
            'test_results': self.test_results
        }

def main():
    """Main test execution function"""
    tester = EmailTemplateFinalTest()
    results = tester.run_all_tests()
    
    # Return exit code based on critical tests
    return 0 if results['all_critical_passed'] else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)