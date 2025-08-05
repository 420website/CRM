import json
import os
import subprocess
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
    
    # Use curl to make the request
    curl_command = [
        'curl', '-s', '-X', 'POST', 
        '-H', 'Content-Type: application/json', 
        '-d', '{"attachment_data": {"type": "Image", "filename": "test.png", "url": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="}, "expires_in_minutes": 30}', 
        'http://localhost:8001/api/share-attachment'
    ]
    
    try:
        # Run the curl command
        result = subprocess.run(curl_command, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"❌ Curl command failed: {result.stderr}")
            return 1
        
        # Parse the JSON response
        try:
            data = json.loads(result.stdout)
        except json.JSONDecodeError:
            print(f"❌ Failed to parse JSON response: {result.stdout}")
            return 1
        
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
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(test_backend_url_generation())