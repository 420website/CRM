#!/usr/bin/env python3

import requests
import json
import sys
import os
from datetime import datetime, date

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://cd556dd9-d36b-422e-8110-4b1830397661.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

def test_clinical_template_processing():
    """
    Test the clinical summary template processing functionality for the positive template.
    Verify that the process_clinical_template function correctly handles address/phone logic.
    """
    print("🧪 CLINICAL SUMMARY TEMPLATE PROCESSING TEST")
    print("=" * 60)
    
    # Test scenarios for address/phone combinations
    test_scenarios = [
        {
            "name": "Both address and phone provided",
            "address": "123 Main Street",
            "phone1": "4161234567",
            "expected_message": "Client does have a valid address and has also provided a phone number for results."
        },
        {
            "name": "Only address provided (no phone)",
            "address": "456 Oak Avenue",
            "phone1": "",
            "expected_message": "Client does have a valid address but no phone number for results."
        },
        {
            "name": "Only phone provided (no address)",
            "address": "",
            "phone1": "4169876543",
            "expected_message": "Client does not have a valid address but has provided a phone number for results."
        },
        {
            "name": "Neither address nor phone provided",
            "address": "",
            "phone1": "",
            "expected_message": "Client does not have a valid address or phone number for results."
        },
        {
            "name": "Address with whitespace only",
            "address": "   ",
            "phone1": "4161111111",
            "expected_message": "Client does not have a valid address but has provided a phone number for results."
        },
        {
            "name": "Phone with whitespace only",
            "address": "789 Pine Street",
            "phone1": "   ",
            "expected_message": "Client does have a valid address but no phone number for results."
        }
    ]
    
    # Get the positive template content first
    print("📋 Step 1: Getting clinical templates...")
    try:
        response = requests.get(f"{API_BASE}/clinical-templates")
        if response.status_code != 200:
            print(f"❌ Failed to get clinical templates: {response.status_code}")
            return False
            
        templates = response.json()
        positive_template = None
        
        for template in templates:
            if template.get('name') == 'Positive':
                positive_template = template
                break
        
        if not positive_template:
            print("❌ Could not find 'Positive' template")
            return False
            
        print(f"✅ Found positive template with content length: {len(positive_template['content'])}")
        
        # Verify the template contains the expected trigger text
        trigger_text = "Client does have a valid address and has also provided a phone number for results"
        if trigger_text not in positive_template['content']:
            print(f"❌ Positive template does not contain expected trigger text: {trigger_text}")
            return False
            
        print("✅ Positive template contains the expected trigger text")
        
    except Exception as e:
        print(f"❌ Error getting templates: {str(e)}")
        return False
    
    # Test each scenario by creating registrations and checking email generation
    print("\n📋 Step 2: Testing address/phone logic scenarios...")
    
    all_tests_passed = True
    test_results = []
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n🔍 Test {i}: {scenario['name']}")
        
        try:
            # Create a test registration with the scenario data
            registration_data = {
                "firstName": f"TestClient{i}",
                "lastName": "TemplateTest",
                "dob": "1990-01-01",
                "patientConsent": "verbal",
                "gender": "Male",
                "province": "Ontario",
                "disposition": "ACTIVE",
                "regDate": date.today().isoformat(),
                "address": scenario["address"],
                "phone1": scenario["phone1"],
                "summaryTemplate": positive_template['content'],  # Use the positive template
                "selectedTemplate": "Positive"
            }
            
            # Create the registration
            response = requests.post(f"{API_BASE}/admin-register", json=registration_data)
            if response.status_code != 200:
                print(f"❌ Failed to create registration: {response.status_code} - {response.text}")
                all_tests_passed = False
                continue
                
            registration_result = response.json()
            registration_id = registration_result.get('id')
            print(f"✅ Created test registration: {registration_id}")
            
            # Get the full registration to verify the template processing
            response = requests.get(f"{API_BASE}/admin-registration/{registration_id}")
            if response.status_code != 200:
                print(f"❌ Failed to get registration: {response.status_code}")
                all_tests_passed = False
                continue
                
            full_registration = response.json()
            
            # Check if the summaryTemplate field contains the processed content
            processed_template = full_registration.get('summaryTemplate', '')
            
            # The template should now contain the expected message based on address/phone logic
            if scenario["expected_message"] in processed_template:
                print(f"✅ Template correctly processed: Found expected message")
                test_results.append({
                    "scenario": scenario["name"],
                    "passed": True,
                    "expected": scenario["expected_message"],
                    "found": True
                })
            else:
                print(f"❌ Template processing failed:")
                print(f"   Expected: {scenario['expected_message']}")
                print(f"   Template content: {processed_template[:200]}...")
                all_tests_passed = False
                test_results.append({
                    "scenario": scenario["name"],
                    "passed": False,
                    "expected": scenario["expected_message"],
                    "found": False
                })
            
            # Test the finalize endpoint to see if email generation works correctly
            print("📧 Testing email generation with finalize endpoint...")
            finalize_response = requests.post(f"{API_BASE}/finalize/{registration_id}")
            
            if finalize_response.status_code == 200:
                finalize_result = finalize_response.json()
                if finalize_result.get('email_sent'):
                    print("✅ Email generation successful")
                else:
                    print("⚠️  Email generation completed but email_sent is False")
            else:
                print(f"⚠️  Finalize endpoint returned: {finalize_response.status_code}")
                # This might be expected if email configuration is not set up
                
        except Exception as e:
            print(f"❌ Error in test scenario: {str(e)}")
            all_tests_passed = False
            test_results.append({
                "scenario": scenario["name"],
                "passed": False,
                "expected": scenario["expected_message"],
                "error": str(e)
            })
    
    # Test the process_clinical_template function directly by examining backend behavior
    print("\n📋 Step 3: Testing template processing logic...")
    
    # Create a registration with the positive template and both address and phone
    test_registration = {
        "firstName": "DirectTest",
        "lastName": "ProcessingTest", 
        "dob": "1985-05-15",
        "patientConsent": "written",
        "address": "123 Test Street",
        "phone1": "4165551234",
        "summaryTemplate": positive_template['content'],
        "selectedTemplate": "Positive"
    }
    
    try:
        response = requests.post(f"{API_BASE}/admin-register", json=test_registration)
        if response.status_code == 200:
            reg_result = response.json()
            reg_id = reg_result.get('id')
            
            # Get the registration back to see processed template
            get_response = requests.get(f"{API_BASE}/admin-registration/{reg_id}")
            if get_response.status_code == 200:
                reg_data = get_response.json()
                template_content = reg_data.get('summaryTemplate', '')
                
                # Check if the original trigger text is still there or replaced
                original_text = "Client does have a valid address and has also provided a phone number for results."
                if original_text in template_content:
                    print("✅ Template processing preserved original text for both address and phone case")
                else:
                    print("⚠️  Template processing may have modified the content")
                    
            print("✅ Direct template processing test completed")
        else:
            print(f"❌ Failed to create direct test registration: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error in direct template processing test: {str(e)}")
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed_tests = sum(1 for result in test_results if result.get('passed', False))
    total_tests = len(test_results)
    
    print(f"Tests passed: {passed_tests}/{total_tests}")
    
    for result in test_results:
        status = "✅ PASS" if result.get('passed', False) else "❌ FAIL"
        print(f"{status} - {result['scenario']}")
        if not result.get('passed', False) and 'error' in result:
            print(f"      Error: {result['error']}")
    
    if all_tests_passed:
        print("\n🎉 ALL CLINICAL TEMPLATE PROCESSING TESTS PASSED!")
        print("✅ The process_clinical_template function correctly handles address/phone logic")
        return True
    else:
        print("\n❌ SOME TESTS FAILED")
        print("❌ Clinical template processing may have issues")
        return False

if __name__ == "__main__":
    success = test_clinical_template_processing()
    sys.exit(0 if success else 1)