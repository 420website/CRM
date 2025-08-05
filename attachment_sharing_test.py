import requests
import unittest
import json
from datetime import datetime, date, timedelta
import random
import string
import sys
import time
import base64
from dotenv import load_dotenv
import os

class AttachmentSharingTester:
    def __init__(self, base_url):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.test_data = {}

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None, binary=False):
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
                if binary:
                    response = requests.post(url, data=data, headers=headers)
                else:
                    response = requests.post(url, json=data, headers=headers)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    if 'application/json' in response.headers.get('Content-Type', ''):
                        response_data = response.json()
                        # Check for proper error format if this is an error response
                        if expected_status >= 400 and 'detail' in response_data:
                            print(f"✅ Error message format correct: {response_data['detail']}")
                        return success, response_data
                    else:
                        # For binary responses or other content types
                        return success, response
                except:
                    return success, response
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    if 'application/json' in response.headers.get('Content-Type', ''):
                        response_data = response.json()
                        print(f"Response: {response_data}")
                        # Check if error response has proper format
                        if response.status_code >= 400 and 'detail' in response_data:
                            print(f"✅ Error message format correct: {response_data['detail']}")
                        elif response.status_code >= 400:
                            print("❌ Error response missing 'detail' field")
                        return False, response_data
                    else:
                        print(f"Response: {response.text[:200]}...")
                        return False, response
                except:
                    print(f"Response: {response.text[:200]}...")
                    return False, response

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def generate_sample_base64_image(self):
        """Generate a simple base64 encoded image for testing"""
        # This is a tiny 1x1 pixel transparent PNG image encoded as base64
        return "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
        
    def generate_sample_base64_pdf(self):
        """Generate a simple base64 encoded PDF for testing"""
        # This is a minimal valid PDF encoded as base64
        return "data:application/pdf;base64,JVBERi0xLjAKMSAwIG9iago8PC9UeXBlL0NhdGFsb2cvUGFnZXMgMiAwIFI+PgplbmRvYmoKMiAwIG9iago8PC9UeXBlL1BhZ2VzL0tpZHNbMyAwIFJdL0NvdW50IDE+PgplbmRvYmoKMyAwIG9iago8PC9UeXBlL1BhZ2UvTWVkaWFCb3ggWzAgMCAzIDNdPj4KZW5kb2JqCnhyZWYKMCA0CjAwMDAwMDAwMDAgNjU1MzUgZiAKMDAwMDAwMDAxMCAwMDAwMCBuIAowMDAwMDAwMDUzIDAwMDAwIG4gCjAwMDAwMDAxMDIgMDAwMDAgbiAKdHJhaWxlcgo8PC9TaXplIDQvUm9vdCAxIDAgUj4+CnN0YXJ0eHJlZgoxNDkKJSVFT0YK"

    def generate_test_data(self):
        """Generate random test data for attachment sharing"""
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
        
        # Generate sample base64 image and PDF
        sample_image = self.generate_sample_base64_image()
        sample_pdf = self.generate_sample_base64_pdf()
        
        self.test_data = {
            "image_attachment": {
                "attachment_data": {
                    "id": f"img_{random_suffix}",
                    "name": f"test_image_{random_suffix}.png",
                    "type": "Image",
                    "url": sample_image,
                    "size": len(sample_image)
                },
                "expires_in_minutes": 30
            },
            "pdf_attachment": {
                "attachment_data": {
                    "id": f"pdf_{random_suffix}",
                    "name": f"test_document_{random_suffix}.pdf",
                    "type": "PDF",
                    "url": sample_pdf,
                    "size": len(sample_pdf)
                },
                "expires_in_minutes": 30
            },
            "custom_expiration": {
                "attachment_data": {
                    "id": f"custom_{random_suffix}",
                    "name": f"custom_expiration_{random_suffix}.png",
                    "type": "Image",
                    "url": sample_image,
                    "size": len(sample_image)
                },
                "expires_in_minutes": 5  # Custom expiration time (5 minutes)
            }
        }
        
        return self.test_data

    def test_share_image_attachment(self):
        """Test creating a shareable link for an image attachment"""
        if not self.test_data:
            self.generate_test_data()
            
        success, response = self.run_test(
            "Share Image Attachment",
            "POST",
            "api/share-attachment",
            200,
            data=self.test_data["image_attachment"]
        )
        
        if success:
            print(f"Share ID: {response.get('share_id')}")
            print(f"Share URL: {response.get('share_url')}")
            print(f"Preview URL: {response.get('preview_url')}")
            print(f"Expires at: {response.get('expires_at')}")
            print(f"Expires in: {response.get('expires_in_minutes')} minutes")
            
            # Store the response data for later tests
            self.test_data["image_share_response"] = response
            
        return success, response

    def test_share_pdf_attachment(self):
        """Test creating a shareable link for a PDF attachment"""
        if not self.test_data:
            self.generate_test_data()
            
        success, response = self.run_test(
            "Share PDF Attachment",
            "POST",
            "api/share-attachment",
            200,
            data=self.test_data["pdf_attachment"]
        )
        
        if success:
            print(f"Share ID: {response.get('share_id')}")
            print(f"Share URL: {response.get('share_url')}")
            print(f"Preview URL: {response.get('preview_url')}")
            print(f"Expires at: {response.get('expires_at')}")
            print(f"Expires in: {response.get('expires_in_minutes')} minutes")
            
            # Store the response data for later tests
            self.test_data["pdf_share_response"] = response
            
        return success, response

    def test_share_with_custom_expiration(self):
        """Test creating a shareable link with custom expiration time"""
        if not self.test_data:
            self.generate_test_data()
            
        success, response = self.run_test(
            "Share Attachment with Custom Expiration",
            "POST",
            "api/share-attachment",
            200,
            data=self.test_data["custom_expiration"]
        )
        
        if success:
            print(f"Share ID: {response.get('share_id')}")
            print(f"Share URL: {response.get('share_url')}")
            print(f"Preview URL: {response.get('preview_url')}")
            print(f"Expires at: {response.get('expires_at')}")
            print(f"Expires in: {response.get('expires_in_minutes')} minutes")
            
            # Verify custom expiration time
            if response.get('expires_in_minutes') == 5:
                print("✅ Custom expiration time (5 minutes) verified")
                self.tests_passed += 1
            else:
                print(f"❌ Custom expiration time not set correctly. Expected 5 minutes, got {response.get('expires_in_minutes')}")
            
            # Store the response data for later tests
            self.test_data["custom_expiration_response"] = response
            
        return success, response

    def test_preview_shared_image(self):
        """Test previewing a shared image"""
        if not self.test_data or "image_share_response" not in self.test_data:
            print("❌ No shared image data available. Run test_share_image_attachment first.")
            return False, {}
            
        share_id = self.test_data["image_share_response"]["share_id"]
        
        # Test with Accept header for image
        headers = {'Accept': 'image/png'}
        success, response = self.run_test(
            "Preview Shared Image",
            "GET",
            f"api/shared-attachment/{share_id}/preview",
            200,
            headers=headers
        )
        
        if success:
            # Verify content type
            content_type = response.headers.get('Content-Type', '')
            if 'image/png' in content_type:
                print(f"✅ Content-Type verified: {content_type}")
                self.tests_passed += 1
            else:
                print(f"❌ Unexpected Content-Type: {content_type}")
                
            # Verify content length
            content_length = int(response.headers.get('Content-Length', 0))
            if content_length > 0:
                print(f"✅ Content-Length verified: {content_length} bytes")
                self.tests_passed += 1
            else:
                print("❌ Content-Length is zero or missing")
                
        return success, response

    def test_preview_shared_pdf(self):
        """Test previewing a shared PDF"""
        if not self.test_data or "pdf_share_response" not in self.test_data:
            print("❌ No shared PDF data available. Run test_share_pdf_attachment first.")
            return False, {}
            
        share_id = self.test_data["pdf_share_response"]["share_id"]
        
        # Test with Accept header for PDF
        headers = {'Accept': 'application/pdf'}
        success, response = self.run_test(
            "Preview Shared PDF",
            "GET",
            f"api/shared-attachment/{share_id}/preview",
            200,
            headers=headers
        )
        
        if success:
            # Verify content type
            content_type = response.headers.get('Content-Type', '')
            if 'application/pdf' in content_type:
                print(f"✅ Content-Type verified: {content_type}")
                self.tests_passed += 1
            else:
                print(f"❌ Unexpected Content-Type: {content_type}")
                
            # Verify content length
            content_length = int(response.headers.get('Content-Length', 0))
            if content_length > 0:
                print(f"✅ Content-Length verified: {content_length} bytes")
                self.tests_passed += 1
            else:
                print("❌ Content-Length is zero or missing")
                
        return success, response

    def test_download_shared_image(self):
        """Test downloading a shared image"""
        if not self.test_data or "image_share_response" not in self.test_data:
            print("❌ No shared image data available. Run test_share_image_attachment first.")
            return False, {}
            
        share_id = self.test_data["image_share_response"]["share_id"]
        
        success, response = self.run_test(
            "Download Shared Image",
            "GET",
            f"api/shared-attachment/{share_id}/download",
            200
        )
        
        if success:
            # Verify content type
            content_type = response.headers.get('Content-Type', '')
            if 'image/png' in content_type:
                print(f"✅ Content-Type verified: {content_type}")
                self.tests_passed += 1
            else:
                print(f"❌ Unexpected Content-Type: {content_type}")
                
            # Verify content disposition
            content_disposition = response.headers.get('Content-Disposition', '')
            if 'attachment' in content_disposition:
                print(f"✅ Content-Disposition verified: {content_disposition}")
                self.tests_passed += 1
            else:
                print(f"❌ Content-Disposition missing or incorrect: {content_disposition}")
                
            # Verify content length
            content_length = int(response.headers.get('Content-Length', 0))
            if content_length > 0:
                print(f"✅ Content-Length verified: {content_length} bytes")
                self.tests_passed += 1
            else:
                print("❌ Content-Length is zero or missing")
                
        return success, response

    def test_download_shared_pdf(self):
        """Test downloading a shared PDF"""
        if not self.test_data or "pdf_share_response" not in self.test_data:
            print("❌ No shared PDF data available. Run test_share_pdf_attachment first.")
            return False, {}
            
        share_id = self.test_data["pdf_share_response"]["share_id"]
        
        success, response = self.run_test(
            "Download Shared PDF",
            "GET",
            f"api/shared-attachment/{share_id}/download",
            200
        )
        
        if success:
            # Verify content type
            content_type = response.headers.get('Content-Type', '')
            if 'application/pdf' in content_type:
                print(f"✅ Content-Type verified: {content_type}")
                self.tests_passed += 1
            else:
                print(f"❌ Unexpected Content-Type: {content_type}")
                
            # Verify content disposition
            content_disposition = response.headers.get('Content-Disposition', '')
            if 'attachment' in content_disposition:
                print(f"✅ Content-Disposition verified: {content_disposition}")
                self.tests_passed += 1
            else:
                print(f"❌ Content-Disposition missing or incorrect: {content_disposition}")
                
            # Verify content length
            content_length = int(response.headers.get('Content-Length', 0))
            if content_length > 0:
                print(f"✅ Content-Length verified: {content_length} bytes")
                self.tests_passed += 1
            else:
                print("❌ Content-Length is zero or missing")
                
        return success, response

    def test_invalid_share_id(self):
        """Test accessing a shared attachment with an invalid share ID"""
        invalid_share_id = "invalid_" + ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
        
        # Test preview with invalid share ID
        success, response = self.run_test(
            "Preview with Invalid Share ID",
            "GET",
            f"api/shared-attachment/{invalid_share_id}/preview",
            404
        )
        
        # Test download with invalid share ID
        success, response = self.run_test(
            "Download with Invalid Share ID",
            "GET",
            f"api/shared-attachment/{invalid_share_id}/download",
            404
        )
        
        return success, response

    def test_expired_share(self):
        """Test accessing an expired shared attachment"""
        if not self.test_data or "custom_expiration_response" not in self.test_data:
            print("❌ No custom expiration data available. Run test_share_with_custom_expiration first.")
            return False, {}
            
        share_id = self.test_data["custom_expiration_response"]["share_id"]
        
        # Wait for the share to expire (5 minutes + buffer)
        # Note: This is a long wait, so we'll simulate expiration by directly checking MongoDB
        print("⏳ Testing expiration handling (simulating expired share)...")
        
        # Connect to MongoDB to check if TTL index is working
        try:
            from pymongo import MongoClient
            import os
            from dotenv import load_dotenv
            
            # Load MongoDB connection details from backend .env
            load_dotenv('/app/backend/.env')
            mongo_url = os.environ.get('MONGO_URL')
            db_name = os.environ.get('DB_NAME')
            
            if not mongo_url or not db_name:
                print("❌ MongoDB connection details not found in backend .env")
                return False, {}
                
            # Connect to MongoDB
            client = MongoClient(mongo_url)
            db = client[db_name]
            collection = db["temporary_shares"]
            
            # Verify TTL index exists
            indexes = collection.index_information()
            ttl_index_exists = False
            for index_name, index_info in indexes.items():
                if 'expireAfterSeconds' in index_info:
                    ttl_index_exists = True
                    print(f"✅ TTL index verified: {index_name} with expireAfterSeconds={index_info['expireAfterSeconds']}")
                    self.tests_passed += 1
                    break
                    
            if not ttl_index_exists:
                print("❌ TTL index not found on temporary_shares collection")
            
            # Find the share we created
            share = collection.find_one({"id": share_id})
            if share:
                print(f"✅ Found share in MongoDB: {share['id']}")
                print(f"✅ Expires at: {share['expires_at']}")
                
                # Manually delete the share to simulate expiration
                collection.delete_one({"id": share_id})
                print("✅ Manually deleted share to simulate expiration")
                
                # Now test accessing the expired share
                success, response = self.run_test(
                    "Preview Expired Share",
                    "GET",
                    f"api/shared-attachment/{share_id}/preview",
                    404
                )
                
                success, response = self.run_test(
                    "Download Expired Share",
                    "GET",
                    f"api/shared-attachment/{share_id}/download",
                    404
                )
                
                return success, response
            else:
                print(f"❌ Share not found in MongoDB: {share_id}")
                return False, {}
                
        except Exception as e:
            print(f"❌ Error checking MongoDB for TTL index: {str(e)}")
            return False, {"error": str(e)}

    def test_access_count_increment(self):
        """Test that access count is incremented when accessing a shared attachment"""
        if not self.test_data or "image_share_response" not in self.test_data:
            print("❌ No shared image data available. Run test_share_image_attachment first.")
            return False, {}
            
        share_id = self.test_data["image_share_response"]["share_id"]
        
        # Connect to MongoDB to check access count
        try:
            from pymongo import MongoClient
            import os
            from dotenv import load_dotenv
            
            # Load MongoDB connection details from backend .env
            load_dotenv('/app/backend/.env')
            mongo_url = os.environ.get('MONGO_URL')
            db_name = os.environ.get('DB_NAME')
            
            if not mongo_url or not db_name:
                print("❌ MongoDB connection details not found in backend .env")
                return False, {}
                
            # Connect to MongoDB
            client = MongoClient(mongo_url)
            db = client[db_name]
            collection = db["temporary_shares"]
            
            # Get initial access count
            share = collection.find_one({"id": share_id})
            if not share:
                print(f"❌ Share not found in MongoDB: {share_id}")
                return False, {}
                
            initial_count = share.get("access_count", 0)
            print(f"Initial access count: {initial_count}")
            
            # Access the shared attachment
            self.run_test(
                "Access Shared Attachment for Count Test",
                "GET",
                f"api/shared-attachment/{share_id}/preview",
                200
            )
            
            # Check updated access count
            share = collection.find_one({"id": share_id})
            if not share:
                print(f"❌ Share not found in MongoDB after access: {share_id}")
                return False, {}
                
            updated_count = share.get("access_count", 0)
            print(f"Updated access count: {updated_count}")
            
            if updated_count > initial_count:
                print(f"✅ Access count incremented: {initial_count} → {updated_count}")
                self.tests_passed += 1
                return True, {"initial_count": initial_count, "updated_count": updated_count}
            else:
                print(f"❌ Access count not incremented: {initial_count} → {updated_count}")
                return False, {"initial_count": initial_count, "updated_count": updated_count}
                
        except Exception as e:
            print(f"❌ Error checking access count in MongoDB: {str(e)}")
            return False, {"error": str(e)}

    def run_all_tests(self):
        """Run all attachment sharing tests"""
        print("🚀 Starting Attachment Sharing Tests")
        print(f"🔗 Base URL: {self.base_url}")
        print("=" * 50)
        
        # Generate test data
        self.generate_test_data()
        
        # Test creating shareable links
        self.test_share_image_attachment()
        self.test_share_pdf_attachment()
        self.test_share_with_custom_expiration()
        
        # Test accessing shared attachments
        self.test_preview_shared_image()
        self.test_preview_shared_pdf()
        self.test_download_shared_image()
        self.test_download_shared_pdf()
        
        # Test error handling
        self.test_invalid_share_id()
        self.test_expired_share()
        
        # Test access count tracking
        self.test_access_count_increment()
        
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
    tester = AttachmentSharingTester(backend_url)
    success = tester.run_all_tests()
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())