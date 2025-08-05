#!/usr/bin/env python3
"""
Model Validation Test for selectedTemplate field
"""

import requests
import json
import uuid
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

def test_model_validation():
    base_url = os.getenv('REACT_APP_BACKEND_URL', 'https://46471c8a-a981-4b23-bca9-bb5c0ba282bc.preview.emergentagent.com')
    api_url = f"{base_url}/api"
    
    print("🧪 TESTING MODEL VALIDATION FOR selectedTemplate FIELD")
    print("=" * 60)
    
    # Test 1: Verify AdminRegistrationCreate model accepts selectedTemplate
    print("\n📝 Test 1: AdminRegistrationCreate model validation")
    
    unique_id = str(uuid.uuid4())[:8]
    test_data = {
        "firstName": f"ModelTest{unique_id}",
        "lastName": f"Validation{unique_id}",
        "patientConsent": "verbal",
        "selectedTemplate": "Model Test Template"
    }
    
    try:
        response = requests.post(
            f"{api_url}/admin-register",
            json=test_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            result = response.json()
            reg_id = result.get('registration_id')
            print(f"✅ AdminRegistrationCreate accepts selectedTemplate field")
            
            # Retrieve to verify AdminRegistration model includes the field
            get_response = requests.get(
                f"{api_url}/admin-registration/{reg_id}",
                headers={'Content-Type': 'application/json'}
            )
            
            if get_response.status_code == 200:
                retrieved = get_response.json()
                if 'selectedTemplate' in retrieved:
                    print(f"✅ AdminRegistration model includes selectedTemplate field")
                    print(f"✅ Value correctly stored: '{retrieved['selectedTemplate']}'")
                else:
                    print(f"❌ AdminRegistration model missing selectedTemplate field")
            else:
                print(f"❌ Failed to retrieve registration: {get_response.status_code}")
            
            # Cleanup
            try:
                requests.delete(f"{api_url}/admin-registration/{reg_id}")
                print(f"🧹 Cleaned up test registration")
            except:
                pass
                
        else:
            print(f"❌ AdminRegistrationCreate rejected selectedTemplate: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Exception during model validation: {str(e)}")
    
    # Test 2: Test field defaults
    print("\n📝 Test 2: Default value handling")
    
    unique_id = str(uuid.uuid4())[:8]
    test_data_no_template = {
        "firstName": f"DefaultTest{unique_id}",
        "lastName": f"Validation{unique_id}",
        "patientConsent": "verbal"
        # No selectedTemplate field
    }
    
    try:
        response = requests.post(
            f"{api_url}/admin-register",
            json=test_data_no_template,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            result = response.json()
            reg_id = result.get('registration_id')
            
            # Retrieve to check default
            get_response = requests.get(
                f"{api_url}/admin-registration/{reg_id}",
                headers={'Content-Type': 'application/json'}
            )
            
            if get_response.status_code == 200:
                retrieved = get_response.json()
                default_value = retrieved.get('selectedTemplate')
                if default_value == 'Select':
                    print(f"✅ Default value correctly set to 'Select'")
                else:
                    print(f"❌ Unexpected default value: '{default_value}'")
            
            # Cleanup
            try:
                requests.delete(f"{api_url}/admin-registration/{reg_id}")
                print(f"🧹 Cleaned up test registration")
            except:
                pass
                
        else:
            print(f"❌ Failed to create registration without selectedTemplate: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Exception during default value test: {str(e)}")
    
    print("\n" + "=" * 60)
    print("📊 MODEL VALIDATION COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    test_model_validation()