import requests
import unittest
import json
from datetime import datetime, date, timedelta
import random
import string
import sys
import base64
import os
from dotenv import load_dotenv

class AttachmentSharingURLTester:
    def __init__(self, base_url):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.test_data = {}

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        if not headers:
            headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    # Check for proper error format if this is an error response
                    if expected_status >= 400 and 'detail' in response_data:
                        print(f"✅ Error message format correct: {response_data['detail']}")
                    return success, response_data
                except:
                    return success, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    response_data = response.json()
                    print(f"Response: {response_data}")
                    # Check if error response has proper format
                    if response.status_code >= 400 and 'detail' in response_data:
                        print(f"✅ Error message format correct: {response_data['detail']}")
                    elif response.status_code >= 400:
                        print("❌ Error response missing 'detail' field")
                    return False, response_data
                except:
                    print(f"Response: {response.text}")
                    return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def generate_sample_base64_image(self):
        """Generate a simple base64 encoded image for testing"""
        # This is a tiny 1x1 pixel transparent PNG image encoded as base64
        return "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="

    def test_share_attachment_url_format(self):
        """Test that the share attachment URLs use the correct external domain"""
        # Create attachment data
        attachment_data = {
            "attachment_data": {
                "type": "Image",
                "filename": "test_image.png",
                "url": self.generate_sample_base64_image(),
                "description": "Test image for sharing"
            },
            "expires_in_minutes": 30
        }
        
        success, response = self.run_test(
            "Create Share Link",
            "POST",
            "api/share-attachment",
            200,
            data=attachment_data
        )
        
        if success:
            print(f"Share ID: {response.get('share_id')}")
            print(f"Share URL: {response.get('share_url')}")
            print(f"Preview URL: {response.get('preview_url')}")
            
            # Verify URLs use the correct external domain
            expected_domain = "https://258401ff-ff29-421c-8498-4969ee7788f0.preview.emergentagent.com"
            
            if response.get('share_url').startswith(expected_domain):
                print(f"✅ Share URL uses correct external domain: {expected_domain}")
                self.tests_passed += 1
            else:
                print(f"❌ Share URL does not use correct external domain. Found: {response.get('share_url')}")
                
            if response.get('preview_url').startswith(expected_domain):
                print(f"✅ Preview URL uses correct external domain: {expected_domain}")
                self.tests_passed += 1
            else:
                print(f"❌ Preview URL does not use correct external domain. Found: {response.get('preview_url')}")
            
            # Verify no localhost references
            if "localhost" in response.get('share_url'):
                print(f"❌ Share URL contains localhost reference: {response.get('share_url')}")
            else:
                print("✅ Share URL does not contain localhost references")
                self.tests_passed += 1
                
            if "localhost" in response.get('preview_url'):
                print(f"❌ Preview URL contains localhost reference: {response.get('preview_url')}")
            else:
                print("✅ Preview URL does not contain localhost references")
                self.tests_passed += 1
            
            # Store for later tests
            self.test_data["share_id"] = response.get('share_id')
            self.test_data["share_url"] = response.get('share_url')
            self.test_data["preview_url"] = response.get('preview_url')
            
            # Test accessing the preview URL
            try:
                preview_response = requests.get(response.get('preview_url'))
                if preview_response.status_code == 200:
                    print(f"✅ Successfully accessed preview URL: {response.get('preview_url')}")
                    print(f"✅ Content-Type: {preview_response.headers.get('Content-Type')}")
                    self.tests_passed += 1
                else:
                    print(f"❌ Failed to access preview URL. Status: {preview_response.status_code}")
            except Exception as e:
                print(f"❌ Error accessing preview URL: {str(e)}")
            
            # Test accessing the download URL
            try:
                download_response = requests.get(response.get('share_url'))
                if download_response.status_code == 200:
                    print(f"✅ Successfully accessed download URL: {response.get('share_url')}")
                    print(f"✅ Content-Type: {download_response.headers.get('Content-Type')}")
                    print(f"✅ Content-Disposition: {download_response.headers.get('Content-Disposition')}")
                    self.tests_passed += 1
                else:
                    print(f"❌ Failed to access download URL. Status: {download_response.status_code}")
            except Exception as e:
                print(f"❌ Error accessing download URL: {str(e)}")
            
        return success, response

    def run_all_tests(self):
        """Run all URL format tests"""
        print("🚀 Starting Attachment Sharing URL Format Tests")
        print(f"🔗 Base URL: {self.base_url}")
        print("=" * 50)
        
        # Test URL format
        self.test_share_attachment_url_format()
        
        print("\n" + "=" * 50)
        print(f"📊 Tests passed: {self.tests_passed}/{self.tests_run}")
        
        return self.tests_passed == self.tests_run

def main():
    # Get the backend URL from the frontend .env file
    import os
    from dotenv import load_dotenv
    
    # Load the frontend .env file
    load_dotenv('/app/frontend/.env')
    
    # Get the backend URL from the environment variable
    backend_url = os.environ.get('REACT_APP_BACKEND_URL')
    if not backend_url:
        print("❌ Error: REACT_APP_BACKEND_URL not found in frontend .env file")
        return 1
    
    print(f"🔗 Using backend URL from .env: {backend_url}")
    
    # Run the tests
    tester = AttachmentSharingURLTester(backend_url)
    success = tester.run_all_tests()
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())