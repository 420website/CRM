#!/usr/bin/env python3
"""
Email Template Changes Testing Script
=====================================

This script tests the email template changes to ensure:
1. Changed "FINAL SUBMISSION -" to "New Registration"
2. Deleted "FINAL ADMIN REGISTRATION - COMPLETED" line
3. Moved Province to Contact information after city
4. Renamed "Medical Information" title to "Other Information"
5. Removed entire "PROCESSING DETAILS:" section

Focus on testing:
- Backend email functionality is working correctly
- Email template generation includes the correct structure
- No broken functionality after template changes
- Email generation process is successful
- Template structure matches the requested changes
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

class EmailTemplateTest:
    def __init__(self):
        self.test_results = []
        self.backend_url = os.environ.get('REACT_APP_BACKEND_URL', 'https://258401ff-ff29-421c-8498-4969ee7788f0.preview.emergentagent.com')
        
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

    def test_backend_connectivity(self):
        """Test backend API connectivity"""
        try:
            # Test basic API connectivity
            response = requests.get(f"{self.backend_url}/api/admin-registrations-pending", timeout=10)
            
            if response.status_code == 200:
                registrations = response.json()
                self.log_result(
                    "Backend Connectivity",
                    True,
                    f"Successfully connected to backend API",
                    f"Found {len(registrations)} pending registrations"
                )
                return True
            else:
                self.log_result(
                    "Backend Connectivity",
                    False,
                    f"Backend API returned status {response.status_code}"
                )
                return False
                
        except Exception as e:
            self.log_result(
                "Backend Connectivity",
                False,
                f"Failed to connect to backend: {str(e)}"
            )
            return False

    def test_email_template_structure_from_code(self):
        """Test the email template structure by examining the backend code"""
        try:
            # Read the backend server.py file to examine email template
            with open('/app/backend/server.py', 'r') as f:
                server_code = f.read()
            
            # Look for the email template in send_finalization_email_async function
            template_start = server_code.find('email_body = f"""')
            template_end = server_code.find('"""', template_start + 15)
            
            if template_start == -1 or template_end == -1:
                self.log_result(
                    "Email Template Structure from Code",
                    False,
                    "Could not find email template in server code"
                )
                return False
            
            email_template = server_code[template_start:template_end + 3]
            
            # Test 1: Check if "New Registration" is used instead of "FINAL SUBMISSION -"
            change_1_success = "New Registration" in email_template and "FINAL SUBMISSION -" not in email_template
            
            # Test 2: Check if "FINAL ADMIN REGISTRATION - COMPLETED" line is deleted
            change_2_success = "FINAL ADMIN REGISTRATION - COMPLETED" not in email_template
            
            # Test 3: Check if Province is in Contact Information section after city
            contact_section_start = email_template.find("CONTACT INFORMATION:")
            other_info_start = email_template.find("OTHER INFORMATION:")
            province_position = email_template.find("• Province:")
            city_position = email_template.find("• City:")
            
            change_3_success = (contact_section_start != -1 and other_info_start != -1 and 
                              province_position != -1 and city_position != -1 and
                              contact_section_start < province_position < other_info_start and 
                              city_position < province_position)
            
            # Test 4: Check if "Medical Information" is renamed to "Other Information"
            change_4_success = "OTHER INFORMATION:" in email_template and "MEDICAL INFORMATION:" not in email_template
            
            # Test 5: Check if "PROCESSING DETAILS:" section is removed
            change_5_success = ("PROCESSING DETAILS:" not in email_template and 
                              "Registration ID" not in email_template and
                              "*** THIS REGISTRATION HAS BEEN REVIEWED AND FINALIZED ***" not in email_template)
            
            # Overall success
            all_changes_success = all([change_1_success, change_2_success, change_3_success, 
                                     change_4_success, change_5_success])
            
            details = {
                'template_found': True,
                'template_length': len(email_template),
                'changes_verification': {
                    'change_1_new_registration_title': change_1_success,
                    'change_2_removed_final_admin_line': change_2_success,
                    'change_3_province_in_contact_info': change_3_success,
                    'change_4_other_information_title': change_4_success,
                    'change_5_removed_processing_details': change_5_success
                },
                'template_preview': email_template[:500] + "..." if len(email_template) > 500 else email_template
            }
            
            self.log_result(
                "Email Template Structure from Code",
                all_changes_success,
                f"Email template structure verification: {'All changes implemented correctly' if all_changes_success else 'Some changes missing'}",
                details
            )
            
            return all_changes_success
            
        except Exception as e:
            self.log_result(
                "Email Template Structure from Code",
                False,
                f"Failed to examine email template in code: {str(e)}"
            )
            return False

    def test_finalization_endpoint_availability(self):
        """Test that the finalization endpoint is available and working"""
        try:
            # First, get a pending registration to test with
            response = requests.get(f"{self.backend_url}/api/admin-registrations-pending", timeout=10)
            
            if response.status_code != 200:
                self.log_result(
                    "Finalization Endpoint Availability",
                    False,
                    f"Could not get pending registrations: {response.status_code}"
                )
                return False
            
            registrations = response.json()
            
            if not registrations:
                self.log_result(
                    "Finalization Endpoint Availability",
                    True,
                    "No pending registrations to test finalization with, but endpoint is accessible",
                    "This is expected if no registrations are pending"
                )
                return True
            
            # Test the finalization endpoint structure (without actually finalizing)
            test_registration_id = registrations[0].get('id')
            
            # We won't actually call the finalize endpoint to avoid side effects,
            # but we can verify the endpoint structure exists in the code
            with open('/app/backend/server.py', 'r') as f:
                server_code = f.read()
            
            finalize_endpoint_exists = 'finalize_admin_registration' in server_code
            finalize_route_exists = '/finalize' in server_code
            
            self.log_result(
                "Finalization Endpoint Availability",
                finalize_endpoint_exists and finalize_route_exists,
                f"Finalization endpoint {'exists and is properly configured' if finalize_endpoint_exists and finalize_route_exists else 'has issues'}",
                {
                    'finalize_function_exists': finalize_endpoint_exists,
                    'finalize_route_exists': finalize_route_exists,
                    'test_registration_available': test_registration_id is not None,
                    'pending_registrations_count': len(registrations)
                }
            )
            
            return finalize_endpoint_exists and finalize_route_exists
            
        except Exception as e:
            self.log_result(
                "Finalization Endpoint Availability",
                False,
                f"Failed to test finalization endpoint: {str(e)}"
            )
            return False

    def test_email_sending_function_structure(self):
        """Test that the email sending functions are properly structured"""
        try:
            with open('/app/backend/server.py', 'r') as f:
                server_code = f.read()
            
            # Check for key email functions
            send_email_exists = 'async def send_email' in server_code
            send_finalization_email_exists = 'send_finalization_email_async' in server_code
            smtp_config_exists = 'SMTP_SERVER' in server_code
            
            # Check for proper error handling
            error_handling_exists = 'except Exception as' in server_code and 'logging.error' in server_code
            
            # Check for photo attachment support
            photo_attachment_exists = 'photo_base64' in server_code and 'MIMEBase' in server_code
            
            all_functions_exist = all([
                send_email_exists,
                send_finalization_email_exists,
                smtp_config_exists,
                error_handling_exists,
                photo_attachment_exists
            ])
            
            self.log_result(
                "Email Sending Function Structure",
                all_functions_exist,
                f"Email sending functions {'are properly structured' if all_functions_exist else 'have structural issues'}",
                {
                    'send_email_function_exists': send_email_exists,
                    'send_finalization_email_function_exists': send_finalization_email_exists,
                    'smtp_configuration_exists': smtp_config_exists,
                    'error_handling_exists': error_handling_exists,
                    'photo_attachment_support_exists': photo_attachment_exists
                }
            )
            
            return all_functions_exist
            
        except Exception as e:
            self.log_result(
                "Email Sending Function Structure",
                False,
                f"Failed to examine email sending functions: {str(e)}"
            )
            return False

    def test_email_template_content_completeness(self):
        """Test that the email template includes all required sections and fields"""
        try:
            with open('/app/backend/server.py', 'r') as f:
                server_code = f.read()
            
            # Find the email template
            template_start = server_code.find('email_body = f"""')
            template_end = server_code.find('"""', template_start + 15)
            
            if template_start == -1 or template_end == -1:
                self.log_result(
                    "Email Template Content Completeness",
                    False,
                    "Could not find email template in server code"
                )
                return False
            
            email_template = server_code[template_start:template_end + 3]
            
            # Check for required sections
            required_sections = [
                "PATIENT INFORMATION:",
                "CONTACT INFORMATION:",
                "OTHER INFORMATION:",
                "CLINICAL SUMMARY TEMPLATE:"
            ]
            
            # Check for required patient fields
            required_patient_fields = [
                "• First Name:",
                "• Last Name:",
                "• Date of Birth:",
                "• Patient Consent:",
                "• Gender:",
                "• Health Card:"
            ]
            
            # Check for required contact fields
            required_contact_fields = [
                "• Phone 1:",
                "• Email:",
                "• Address:",
                "• City:",
                "• Province:",
                "• Postal Code:"
            ]
            
            # Check for required other information fields
            required_other_fields = [
                "• Special Attention/Notes:",
                "• Photo Attached:",
                "• Physician:",
                "• Disposition:"
            ]
            
            sections_present = all(section in email_template for section in required_sections)
            patient_fields_present = all(field in email_template for field in required_patient_fields)
            contact_fields_present = all(field in email_template for field in required_contact_fields)
            other_fields_present = all(field in email_template for field in required_other_fields)
            
            all_content_complete = all([
                sections_present,
                patient_fields_present,
                contact_fields_present,
                other_fields_present
            ])
            
            self.log_result(
                "Email Template Content Completeness",
                all_content_complete,
                f"Email template content {'is complete with all required sections and fields' if all_content_complete else 'is missing some required sections or fields'}",
                {
                    'sections_present': sections_present,
                    'patient_fields_present': patient_fields_present,
                    'contact_fields_present': contact_fields_present,
                    'other_fields_present': other_fields_present,
                    'missing_sections': [s for s in required_sections if s not in email_template],
                    'missing_patient_fields': [f for f in required_patient_fields if f not in email_template],
                    'missing_contact_fields': [f for f in required_contact_fields if f not in email_template],
                    'missing_other_fields': [f for f in required_other_fields if f not in email_template]
                }
            )
            
            return all_content_complete
            
        except Exception as e:
            self.log_result(
                "Email Template Content Completeness",
                False,
                f"Failed to test email template content completeness: {str(e)}"
            )
            return False

    def run_all_tests(self):
        """Run all email template tests"""
        logger.info("🚀 Starting Email Template Changes Testing")
        logger.info("=" * 60)
        
        # Test 1: Backend Connectivity
        connectivity_success = self.test_backend_connectivity()
        
        # Test 2: Email Template Structure from Code
        template_success = self.test_email_template_structure_from_code()
        
        # Test 3: Finalization Endpoint Availability
        finalization_success = self.test_finalization_endpoint_availability()
        
        # Test 4: Email Sending Function Structure
        function_success = self.test_email_sending_function_structure()
        
        # Test 5: Email Template Content Completeness
        content_success = self.test_email_template_content_completeness()
        
        # Summary
        total_tests = 5
        passed_tests = sum([connectivity_success, template_success, finalization_success, function_success, content_success])
        
        logger.info("=" * 60)
        logger.info(f"📊 EMAIL TEMPLATE TESTING SUMMARY")
        logger.info(f"Total Tests: {total_tests}")
        logger.info(f"Passed: {passed_tests}")
        logger.info(f"Failed: {total_tests - passed_tests}")
        logger.info(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if passed_tests == total_tests:
            logger.info("🎉 ALL EMAIL TEMPLATE TESTS PASSED!")
        else:
            logger.info("⚠️  Some email template tests failed - see details above")
        
        return {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'success_rate': (passed_tests/total_tests)*100,
            'all_passed': passed_tests == total_tests,
            'test_results': self.test_results
        }

def main():
    """Main test execution function"""
    tester = EmailTemplateTest()
    results = tester.run_all_tests()
    
    # Return exit code based on results
    return 0 if results['all_passed'] else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)