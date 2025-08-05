import requests
import json
import os
from dotenv import load_dotenv
import sys

def test_backend_url_generation():
    """Test that the backend is generating the correct URLs for shared attachments"""
    # Load environment variables
    load_dotenv('/app/frontend/.env')
    
    # Get the backend URL from the environment variable
    expected_domain = os.environ.get('REACT_APP_BACKEND_URL')
    if not expected_domain:
        print("❌ Error: REACT_APP_BACKEND_URL not found in frontend .env file")
        return 1
    
    print(f"Expected domain from .env: {expected_domain}")
    
    # Create a simple test attachment
    attachment_data = {
        "attachment_data": {
            "type": "Image",
            "filename": "test.png",
            "url": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
        },
        "expires_in_minutes": 30
    }
    
    # Make the request directly to the backend
    try:
        # Use the local backend URL for the request
        response = requests.post(
            "http://localhost:8001/api/share-attachment",
            json=attachment_data,
            timeout=10
        )
        
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Share ID: {data.get('share_id')}")
            print(f"Share URL: {data.get('share_url')}")
            print(f"Preview URL: {data.get('preview_url')}")
            
            # Check for localhost references
            if "localhost" in data.get('share_url', ''):
                print("❌ Share URL contains localhost reference")
                return 1
            else:
                print("✅ Share URL does not contain localhost references")
                
            if "localhost" in data.get('preview_url', ''):
                print("❌ Preview URL contains localhost reference")
                return 1
            else:
                print("✅ Preview URL does not contain localhost references")
                
            # Check for correct domain
            if data.get('share_url', '').startswith(expected_domain):
                print(f"✅ Share URL uses correct external domain: {expected_domain}")
            else:
                print(f"❌ Share URL does not use correct external domain: {data.get('share_url')}")
                return 1
                
            if data.get('preview_url', '').startswith(expected_domain):
                print(f"✅ Preview URL uses correct external domain: {expected_domain}")
            else:
                print(f"❌ Preview URL does not use correct external domain: {data.get('preview_url')}")
                return 1
                
            return 0
        else:
            print(f"Error response: {response.text}")
            return 1
            
    except requests.exceptions.RequestException as e:
        print(f"Request error: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(test_backend_url_generation())