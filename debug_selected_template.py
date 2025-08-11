#!/usr/bin/env python3
"""
Debug selectedTemplate field API response
"""

import requests
import json
import uuid
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

def debug_api_response():
    base_url = os.getenv('REACT_APP_BACKEND_URL', 'https://258401ff-ff29-421c-8498-4969ee7788f0.preview.emergentagent.com')
    api_url = f"{base_url}/api"
    
    print(f"Testing API: {api_url}")
    
    # Create test registration with selectedTemplate
    unique_id = str(uuid.uuid4())[:8]
    registration_data = {
        "firstName": f"DebugUser{unique_id}",
        "lastName": f"Template{unique_id}",
        "patientConsent": "verbal",
        "selectedTemplate": "Positive"
    }
    
    print(f"\n📤 Sending registration data:")
    print(json.dumps(registration_data, indent=2))
    
    try:
        response = requests.post(
            f"{api_url}/admin-register",
            json=registration_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"\n📥 Response Status: {response.status_code}")
        print(f"📥 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"📥 Response Body:")
            print(json.dumps(result, indent=2, default=str))
            
            # Check if selectedTemplate is in the response
            if 'selectedTemplate' in result:
                print(f"\n✅ selectedTemplate found in response: '{result['selectedTemplate']}'")
            else:
                print(f"\n❌ selectedTemplate NOT found in response")
                print(f"Available fields: {list(result.keys())}")
            
            # Try to retrieve the registration
            reg_id = result.get('registration_id')
            if reg_id:
                print(f"\n🔍 Retrieving registration {reg_id}...")
                get_response = requests.get(
                    f"{api_url}/admin-registration/{reg_id}",
                    headers={'Content-Type': 'application/json'}
                )
                
                if get_response.status_code == 200:
                    get_result = get_response.json()
                    print(f"📥 Retrieved registration:")
                    print(json.dumps(get_result, indent=2, default=str))
                    
                    if 'selectedTemplate' in get_result:
                        print(f"\n✅ selectedTemplate found in retrieved data: '{get_result['selectedTemplate']}'")
                    else:
                        print(f"\n❌ selectedTemplate NOT found in retrieved data")
                        print(f"Available fields: {list(get_result.keys())}")
                else:
                    print(f"❌ Failed to retrieve registration: {get_response.status_code} - {get_response.text}")
                
                # Cleanup
                try:
                    requests.delete(f"{api_url}/admin-registration/{reg_id}")
                    print(f"\n🧹 Cleaned up test registration {reg_id}")
                except:
                    pass
        else:
            print(f"❌ Failed to create registration: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception occurred: {str(e)}")

if __name__ == "__main__":
    debug_api_response()