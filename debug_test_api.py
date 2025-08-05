#!/usr/bin/env python3
"""
Debug script to check the test retrieval API response format
"""

import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

def debug_test_retrieval():
    base_url = os.getenv('REACT_APP_BACKEND_URL', 'https://46471c8a-a981-4b23-bca9-bb5c0ba282bc.preview.emergentagent.com')
    api_url = f"{base_url}/api"
    
    # First create a registration
    registration_data = {
        "firstName": "Debug",
        "lastName": "Test",
        "patientConsent": "verbal"
    }
    
    print("Creating registration...")
    response = requests.post(f"{api_url}/admin-register", 
                           json=registration_data, 
                           headers={'Content-Type': 'application/json'},
                           timeout=30)
    
    print(f"Registration response status: {response.status_code}")
    print(f"Registration response: {response.text}")
    
    if response.status_code in [200, 201]:
        data = response.json()
        registration_id = data.get('registration_id')
        print(f"Registration ID: {registration_id}")
        
        # Add a test
        test_data = {
            "test_type": "HIV",
            "test_date": "2024-01-15",
            "hiv_result": "negative",
            "hiv_tester": "JY"
        }
        
        print("\nAdding test...")
        test_response = requests.post(f"{api_url}/admin-registration/{registration_id}/test",
                                    json=test_data,
                                    headers={'Content-Type': 'application/json'},
                                    timeout=30)
        
        print(f"Test response status: {test_response.status_code}")
        print(f"Test response: {test_response.text}")
        
        # Now retrieve tests
        print("\nRetrieving tests...")
        get_response = requests.get(f"{api_url}/admin-registration/{registration_id}/tests",
                                  headers={'Content-Type': 'application/json'},
                                  timeout=30)
        
        print(f"Get tests response status: {get_response.status_code}")
        print(f"Get tests response headers: {dict(get_response.headers)}")
        print(f"Get tests response text: {get_response.text}")
        print(f"Get tests response type: {type(get_response.text)}")
        
        try:
            json_data = get_response.json()
            print(f"JSON data type: {type(json_data)}")
            print(f"JSON data: {json_data}")
            
            if isinstance(json_data, list):
                print(f"Number of tests: {len(json_data)}")
                for i, test in enumerate(json_data):
                    print(f"Test {i}: {test}")
            else:
                print(f"Unexpected data type: {type(json_data)}")
        except Exception as e:
            print(f"Error parsing JSON: {e}")

if __name__ == "__main__":
    debug_test_retrieval()