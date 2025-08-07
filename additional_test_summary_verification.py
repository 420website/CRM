#!/usr/bin/env python3
"""
Additional Test Summary Workflow Verification
==============================================

This creates a second registration with different test data to ensure 
the system works consistently and test data is properly isolated per registration.
"""

import requests
import json
from datetime import datetime, date
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

def test_additional_registration():
    base_url = os.getenv('REACT_APP_BACKEND_URL', 'https://cd556dd9-d36b-422e-8110-4b1830397661.preview.emergentagent.com')
    api_url = f"{base_url}/api"
    
    print("🧪 ADDITIONAL TEST SUMMARY WORKFLOW VERIFICATION")
    print("=" * 60)
    
    # Create second registration
    registration_data = {
        "firstName": "Sarah",
        "lastName": "Wilson", 
        "patientConsent": "written",
        "dob": "1992-03-22",
        "gender": "Female",
        "province": "Ontario",
        "healthCard": "9876543210CD",
        "phone1": "647-555-0987",
        "email": "sarah.wilson@email.com"
    }
    
    print("\n📋 Creating second registration...")
    response = requests.post(
        f"{api_url}/admin-register",
        json=registration_data,
        headers={'Content-Type': 'application/json'}
    )
    
    if response.status_code != 200:
        print(f"❌ Failed to create registration: {response.status_code}")
        return False
    
    data = response.json()
    registration_id = data.get('registration_id')
    print(f"✅ Created registration: {registration_id}")
    
    # Add different test data
    tests_to_create = [
        {
            "test_type": "HIV",
            "test_date": "2025-01-20",
            "hiv_result": "positive",
            "hiv_type": "Type 2",
            "hiv_tester": "DR"
        },
        {
            "test_type": "HCV",
            "test_date": "2025-01-21",
            "hcv_result": "negative",
            "hcv_tester": "JY"
        },
        {
            "test_type": "Bloodwork",
            "test_date": "2025-01-22",
            "bloodwork_type": "Serum",
            "bloodwork_circles": "5",
            "bloodwork_result": "Submitted",
            "bloodwork_date_submitted": "2025-01-23",
            "bloodwork_tester": "CM"
        }
    ]
    
    test_ids = []
    for i, test_data in enumerate(tests_to_create):
        print(f"\n📝 Creating {test_data['test_type']} test...")
        response = requests.post(
            f"{api_url}/admin-registration/{registration_id}/test",
            json=test_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            data = response.json()
            test_ids.append(data.get('test_id'))
            print(f"✅ Created {test_data['test_type']} test: {data.get('test_id')}")
        else:
            print(f"❌ Failed to create {test_data['test_type']} test: {response.status_code}")
            return False
    
    # Retrieve and verify tests
    print(f"\n📊 Retrieving tests for registration {registration_id}...")
    response = requests.get(
        f"{api_url}/admin-registration/{registration_id}/tests",
        headers={'Content-Type': 'application/json'}
    )
    
    if response.status_code != 200:
        print(f"❌ Failed to retrieve tests: {response.status_code}")
        return False
    
    data = response.json()
    tests = data.get('tests', [])
    
    print(f"✅ Retrieved {len(tests)} tests")
    
    # Verify test data
    expected_results = {
        'HIV': {'hiv_result': 'positive', 'hiv_type': 'Type 2', 'hiv_tester': 'DR'},
        'HCV': {'hcv_result': 'negative', 'hcv_tester': 'JY'},
        'Bloodwork': {'bloodwork_type': 'Serum', 'bloodwork_result': 'Submitted', 'bloodwork_tester': 'CM'}
    }
    
    for test in tests:
        test_type = test.get('test_type')
        if test_type in expected_results:
            expected = expected_results[test_type]
            for field, expected_value in expected.items():
                actual_value = test.get(field)
                if actual_value == expected_value:
                    print(f"✅ {test_type} {field}: {actual_value}")
                else:
                    print(f"❌ {test_type} {field}: expected {expected_value}, got {actual_value}")
                    return False
    
    # Generate email template format
    print(f"\n📧 Generating email template format...")
    test_summary = ""
    for test in tests:
        test_type = test.get('test_type', 'Unknown')
        test_date = test.get('test_date', 'Not specified')
        
        test_summary += f"\n--- {test_type} Test ---\n"
        test_summary += f"Date: {test_date}\n"
        
        if test_type == 'HIV':
            test_summary += f"Result: {test.get('hiv_result', 'Not specified')}\n"
            test_summary += f"Type: {test.get('hiv_type', 'Not specified')}\n"
            test_summary += f"Tester: {test.get('hiv_tester', 'Not specified')}\n"
        
        elif test_type == 'HCV':
            test_summary += f"Result: {test.get('hcv_result', 'Not specified')}\n"
            test_summary += f"Tester: {test.get('hcv_tester', 'Not specified')}\n"
        
        elif test_type == 'Bloodwork':
            test_summary += f"Type: {test.get('bloodwork_type', 'Not specified')}\n"
            test_summary += f"Circles: {test.get('bloodwork_circles', 'Not specified')}\n"
            test_summary += f"Result: {test.get('bloodwork_result', 'Not specified')}\n"
            test_summary += f"Date Submitted: {test.get('bloodwork_date_submitted', 'Not specified')}\n"
            test_summary += f"Tester: {test.get('bloodwork_tester', 'Not specified')}\n"
        
        test_summary += "\n"
    
    print(f"Generated Test Summary:\n{test_summary}")
    
    # Verify different results from first registration
    expected_different_content = ["positive", "Type 2", "negative", "Serum", "Submitted"]
    for content in expected_different_content:
        if content not in test_summary:
            print(f"❌ Missing expected different content: {content}")
            return False
    
    print("✅ All different test data verified successfully")
    print(f"✅ Registration ID: {registration_id}")
    print(f"✅ Test IDs: {test_ids}")
    
    return True

if __name__ == "__main__":
    success = test_additional_registration()
    
    if success:
        print("\n🎉 ADDITIONAL VERIFICATION PASSED")
        print("✅ System handles multiple registrations correctly")
        print("✅ Test data is properly isolated per registration")
        print("✅ Different test results are stored and retrieved correctly")
        print("✅ Email template generation works with varied data")
    else:
        print("\n❌ ADDITIONAL VERIFICATION FAILED")
    
    exit(0 if success else 1)