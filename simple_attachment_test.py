import requests
import json
import sys
from dotenv import load_dotenv
import os

def main():
    # Get the backend URL from the frontend .env file
    load_dotenv('/app/frontend/.env')
    backend_url = os.environ.get('REACT_APP_BACKEND_URL')
    
    if not backend_url:
        print("❌ Error: REACT_APP_BACKEND_URL not found in frontend .env file")
        return 1
    
    print(f"🔗 Using backend URL: {backend_url}")
    
    # Test 1: Create a shareable link for an image attachment
    print("\n🔍 Test 1: Creating shareable link for image attachment...")
    
    # Sample base64 image
    sample_image = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
    
    # Prepare request data
    data = {
        "attachment_data": {
            "id": "test_image_123",
            "name": "test_image.png",
            "type": "Image",
            "url": sample_image,
            "size": len(sample_image)
        },
        "expires_in_minutes": 30
    }
    
    # Send request
    response = requests.post(
        f"{backend_url}/api/share-attachment",
        json=data,
        headers={'Content-Type': 'application/json'}
    )
    
    # Check response
    if response.status_code == 200:
        print(f"✅ Success - Status: {response.status_code}")
        response_data = response.json()
        print(f"Share ID: {response_data.get('share_id')}")
        print(f"Share URL: {response_data.get('share_url')}")
        print(f"Preview URL: {response_data.get('preview_url')}")
        print(f"Expires at: {response_data.get('expires_at')}")
        print(f"Expires in: {response_data.get('expires_in_minutes')} minutes")
        
        # Store share ID for next tests
        share_id = response_data.get('share_id')
        
        # Test 2: Preview shared attachment
        print("\n🔍 Test 2: Previewing shared attachment...")
        preview_response = requests.get(
            f"{backend_url}/api/shared-attachment/{share_id}/preview",
            headers={'Accept': 'image/png'}
        )
        
        if preview_response.status_code == 200:
            print(f"✅ Success - Status: {preview_response.status_code}")
            print(f"Content-Type: {preview_response.headers.get('Content-Type')}")
            print(f"Content-Length: {preview_response.headers.get('Content-Length')} bytes")
        else:
            print(f"❌ Failed - Status: {preview_response.status_code}")
            try:
                print(f"Response: {preview_response.json()}")
            except:
                print(f"Response: {preview_response.text[:200]}...")
        
        # Test 3: Download shared attachment
        print("\n🔍 Test 3: Downloading shared attachment...")
        download_response = requests.get(
            f"{backend_url}/api/shared-attachment/{share_id}/download"
        )
        
        if download_response.status_code == 200:
            print(f"✅ Success - Status: {download_response.status_code}")
            print(f"Content-Type: {download_response.headers.get('Content-Type')}")
            print(f"Content-Disposition: {download_response.headers.get('Content-Disposition')}")
            print(f"Content-Length: {download_response.headers.get('Content-Length')} bytes")
        else:
            print(f"❌ Failed - Status: {download_response.status_code}")
            try:
                print(f"Response: {download_response.json()}")
            except:
                print(f"Response: {download_response.text[:200]}...")
        
        # Test 4: Invalid share ID
        print("\n🔍 Test 4: Testing invalid share ID...")
        invalid_response = requests.get(
            f"{backend_url}/api/shared-attachment/invalid_share_id/preview"
        )
        
        if invalid_response.status_code == 404:
            print(f"✅ Success - Status: {invalid_response.status_code} (Expected 404)")
            try:
                print(f"Error message: {invalid_response.json().get('detail')}")
            except:
                print(f"Response: {invalid_response.text[:200]}...")
        else:
            print(f"❌ Failed - Expected 404, got {invalid_response.status_code}")
            try:
                print(f"Response: {invalid_response.json()}")
            except:
                print(f"Response: {invalid_response.text[:200]}...")
        
        print("\n✅ All tests completed!")
        return 0
    else:
        print(f"❌ Failed - Status: {response.status_code}")
        try:
            print(f"Response: {response.json()}")
        except:
            print(f"Response: {response.text[:200]}...")
        return 1

if __name__ == "__main__":
    sys.exit(main())