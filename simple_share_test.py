import requests
import json

def test_share_attachment():
    """Test the share attachment endpoint directly"""
    # Base URL from frontend .env
    base_url = "https://258401ff-ff29-421c-8498-4969ee7788f0.preview.emergentagent.com"
    
    # Create a simple test attachment
    attachment_data = {
        "attachment_data": {
            "type": "Image",
            "filename": "test.png",
            "url": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
        },
        "expires_in_minutes": 30
    }
    
    # Make the request
    try:
        response = requests.post(
            f"{base_url}/api/share-attachment",
            json=attachment_data,
            timeout=10  # Set a timeout to avoid hanging
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
    test_share_attachment()