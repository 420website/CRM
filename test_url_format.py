import requests
import json
import os
from dotenv import load_dotenv

def test_share_attachment_url_format():
    """Test that the share attachment URLs use the correct external domain"""
    # Load environment variables
    load_dotenv('/app/frontend/.env')
    
    # Get the backend URL from the environment variable
    backend_url = os.environ.get('REACT_APP_BACKEND_URL')
    if not backend_url:
        print("❌ Error: REACT_APP_BACKEND_URL not found in frontend .env file")
        return
    
    print(f"Using backend URL from .env: {backend_url}")
    
    # Create a simple test attachment
    attachment_data = {
        "attachment_data": {
            "type": "Image",
            "filename": "test.png",
            "url": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
        },
        "expires_in_minutes": 30
    }
    
    # Make the request to the local backend directly
    try:
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
            else:
                print("✅ Share URL does not contain localhost references")
                
            if "localhost" in data.get('preview_url', ''):
                print("❌ Preview URL contains localhost reference")
            else:
                print("✅ Preview URL does not contain localhost references")
                
            # Check for correct domain
            expected_domain = "https://258401ff-ff29-421c-8498-4969ee7788f0.preview.emergentagent.com"
            if data.get('share_url', '').startswith(expected_domain):
                print(f"✅ Share URL uses correct external domain: {expected_domain}")
            else:
                print(f"❌ Share URL does not use correct external domain: {data.get('share_url')}")
                
            if data.get('preview_url', '').startswith(expected_domain):
                print(f"✅ Preview URL uses correct external domain: {expected_domain}")
            else:
                print(f"❌ Preview URL does not use correct external domain: {data.get('preview_url')}")
        else:
            print(f"Error response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"Request error: {str(e)}")

if __name__ == "__main__":
    test_share_attachment_url_format()