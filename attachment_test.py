import requests
import unittest
import json
import os
import sys
import random
import string
import base64
from datetime import datetime
from dotenv import load_dotenv

class AttachmentTester:
    def __init__(self, base_url):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.test_data = {}
        self.registration_id = None
        self.attachment_ids = []

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None, files=None):
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
                if files:
                    # For multipart/form-data
                    response = requests.post(url, files=files)
                else:
                    response = requests.post(url, json=data, headers=headers)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers)

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

    def generate_random_string(self, length=10):
        """Generate a random string of fixed length"""
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

    def generate_sample_base64_image(self):
        """Generate a simple base64 encoded image for testing"""
        # This is a tiny 1x1 pixel transparent PNG image encoded as base64
        return "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
    
    def generate_raw_base64_image(self):
        """Generate a raw base64 encoded image without data URI prefix"""
        return "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
    
    def generate_sample_base64_pdf(self):
        """Generate a simple base64 encoded PDF for testing"""
        # This is a minimal valid PDF encoded as base64
        return "data:application/pdf;base64,JVBERi0xLjAKMSAwIG9iago8PC9UeXBlL0NhdGFsb2cvUGFnZXMgMiAwIFI+PgplbmRvYmoKMiAwIG9iago8PC9UeXBlL1BhZ2VzL0tpZHNbMyAwIFJdL0NvdW50IDE+PgplbmRvYmoKMyAwIG9iago8PC9UeXBlL1BhZ2UvTWVkaWFCb3ggWzAgMCAzIDNdPj4KZW5kb2JqCnhyZWYKMCA0CjAwMDAwMDAwMDAgNjU1MzUgZgowMDAwMDAwMDEwIDAwMDAwIG4KMDAwMDAwMDA1MyAwMDAwMCBuCjAwMDAwMDAxMDIgMDAwMDAgbgp0cmFpbGVyCjw8L1Jvb3QgMSAwIFI+PgolJUVPRgo="
    
    def generate_raw_base64_pdf(self):
        """Generate a raw base64 encoded PDF without data URI prefix"""
        return "JVBERi0xLjAKMSAwIG9iago8PC9UeXBlL0NhdGFsb2cvUGFnZXMgMiAwIFI+PgplbmRvYmoKMiAwIG9iago8PC9UeXBlL1BhZ2VzL0tpZHNbMyAwIFJdL0NvdW50IDE+PgplbmRvYmoKMyAwIG9iago8PC9UeXBlL1BhZ2UvTWVkaWFCb3ggWzAgMCAzIDNdPj4KZW5kb2JqCnhyZWYKMCA0CjAwMDAwMDAwMDAgNjU1MzUgZgowMDAwMDAwMDEwIDAwMDAwIG4KMDAwMDAwMDA1MyAwMDAwMCBuCjAwMDAwMDAxMDIgMDAwMDAgbgp0cmFpbGVyCjw8L1Jvb3QgMSAwIFI+PgolJUVPRgo="

    def create_test_registration(self):
        """Create a test registration to use for attachment tests"""
        random_suffix = self.generate_random_string()
        
        registration_data = {
            "firstName": f"Attachment Test {random_suffix}",
            "lastName": f"User {random_suffix}",
            "patientConsent": "Verbal"
        }
        
        success, response = self.run_test(
            "Create Test Registration",
            "POST",
            "api/admin-register",
            200,
            data=registration_data
        )
        
        if success:
            self.registration_id = response.get('registration_id')
            print(f"✅ Created test registration with ID: {self.registration_id}")
            return True
        else:
            print("❌ Failed to create test registration")
            return False

    def test_save_attachment_with_image(self):
        """Test saving an attachment with image data"""
        if not self.registration_id:
            if not self.create_test_registration():
                return False, {}
        
        # Create attachment data with image
        attachment_data = {
            "type": "Image",
            "name": f"Test Image {self.generate_random_string()}",
            "documentType": "Consultation Report",
            "url": self.generate_sample_base64_image()
        }
        
        success, response = self.run_test(
            "Save Attachment with Image",
            "POST",
            f"api/admin-registration/{self.registration_id}/attachment",
            200,
            data=attachment_data
        )
        
        if success:
            attachment_id = response.get('attachment_id')
            self.attachment_ids.append(attachment_id)
            print(f"✅ Saved image attachment with ID: {attachment_id}")
        
        return success, response

    def test_save_attachment_with_raw_base64_image(self):
        """Test saving an attachment with raw base64 image data (no data URI prefix)"""
        if not self.registration_id:
            if not self.create_test_registration():
                return False, {}
        
        # Create attachment data with raw base64 image
        attachment_data = {
            "type": "Image",
            "name": f"Raw Base64 Image {self.generate_random_string()}",
            "documentType": "Treatment Consent",
            "url": self.generate_raw_base64_image()
        }
        
        success, response = self.run_test(
            "Save Attachment with Raw Base64 Image",
            "POST",
            f"api/admin-registration/{self.registration_id}/attachment",
            200,
            data=attachment_data
        )
        
        if success:
            attachment_id = response.get('attachment_id')
            self.attachment_ids.append(attachment_id)
            print(f"✅ Saved raw base64 image attachment with ID: {attachment_id}")
        
        return success, response

    def test_save_attachment_with_pdf(self):
        """Test saving an attachment with PDF data"""
        if not self.registration_id:
            if not self.create_test_registration():
                return False, {}
        
        # Create attachment data with PDF
        attachment_data = {
            "type": "PDF",
            "name": f"Test PDF {self.generate_random_string()}",
            "documentType": "HCV Prescription",
            "url": self.generate_sample_base64_pdf()
        }
        
        success, response = self.run_test(
            "Save Attachment with PDF",
            "POST",
            f"api/admin-registration/{self.registration_id}/attachment",
            200,
            data=attachment_data
        )
        
        if success:
            attachment_id = response.get('attachment_id')
            self.attachment_ids.append(attachment_id)
            print(f"✅ Saved PDF attachment with ID: {attachment_id}")
        
        return success, response

    def test_save_attachment_with_raw_base64_pdf(self):
        """Test saving an attachment with raw base64 PDF data (no data URI prefix)"""
        if not self.registration_id:
            if not self.create_test_registration():
                return False, {}
        
        # Create attachment data with raw base64 PDF
        attachment_data = {
            "type": "PDF",
            "name": f"Raw Base64 PDF {self.generate_random_string()}",
            "documentType": "HCV Prescription",
            "url": self.generate_raw_base64_pdf()
        }
        
        success, response = self.run_test(
            "Save Attachment with Raw Base64 PDF",
            "POST",
            f"api/admin-registration/{self.registration_id}/attachment",
            200,
            data=attachment_data
        )
        
        if success:
            attachment_id = response.get('attachment_id')
            self.attachment_ids.append(attachment_id)
            print(f"✅ Saved raw base64 PDF attachment with ID: {attachment_id}")
        
        return success, response

    def test_get_attachments(self):
        """Test retrieving all attachments for a registration"""
        if not self.registration_id:
            if not self.create_test_registration():
                return False, {}
        
        # First, make sure we have at least one attachment
        if not self.attachment_ids:
            self.test_save_attachment_with_image()
        
        success, response = self.run_test(
            "Get Attachments",
            "GET",
            f"api/admin-registration/{self.registration_id}/attachments",
            200
        )
        
        if success:
            attachments = response.get('attachments', [])
            print(f"✅ Retrieved {len(attachments)} attachments")
            
            # Verify attachment data integrity
            if attachments:
                for attachment in attachments:
                    # Check required fields
                    required_fields = ['id', 'type', 'name', 'documentType', 'url', 'savedAt']
                    missing_fields = [field for field in required_fields if field not in attachment]
                    
                    if missing_fields:
                        print(f"❌ Attachment missing required fields: {', '.join(missing_fields)}")
                        success = False
                    else:
                        print(f"✅ Attachment has all required fields: {attachment['name']}")
                    
                    # Check URL field format for images
                    if attachment.get('type') == 'Image':
                        url = attachment.get('url', '')
                        if url.startswith('data:image/'):
                            print(f"✅ Image URL has correct data URI format: {url[:30]}...")
                        else:
                            print(f"❌ Image URL missing data URI format: {url[:30]}...")
                            success = False
                    
                    # Check URL field format for PDFs
                    if attachment.get('type') == 'PDF':
                        url = attachment.get('url', '')
                        if url.startswith('data:application/pdf;base64,'):
                            print(f"✅ PDF URL has correct data URI format: {url[:40]}...")
                        else:
                            print(f"❌ PDF URL missing data URI format: {url[:40]}...")
                            success = False
            else:
                print("❌ No attachments found")
                success = False
        
        return success, response

    def test_delete_attachment(self):
        """Test deleting an attachment"""
        if not self.registration_id:
            if not self.create_test_registration():
                return False, {}
        
        # First, make sure we have at least one attachment
        if not self.attachment_ids:
            success, response = self.test_save_attachment_with_image()
            if not success:
                return False, {}
        
        # Get the first attachment ID
        attachment_id = self.attachment_ids[0]
        
        success, response = self.run_test(
            "Delete Attachment",
            "DELETE",
            f"api/admin-registration/{self.registration_id}/attachment/{attachment_id}",
            200
        )
        
        if success:
            print(f"✅ Deleted attachment with ID: {attachment_id}")
            
            # Verify the attachment was actually deleted by trying to get all attachments
            get_success, get_response = self.run_test(
                "Verify Attachment Deletion",
                "GET",
                f"api/admin-registration/{self.registration_id}/attachments",
                200
            )
            
            if get_success:
                attachments = get_response.get('attachments', [])
                deleted = True
                
                for attachment in attachments:
                    if attachment.get('id') == attachment_id:
                        print(f"❌ Attachment still exists after deletion: {attachment_id}")
                        deleted = False
                        break
                
                if deleted:
                    print(f"✅ Verified attachment no longer exists: {attachment_id}")
                    # Remove from our tracking list
                    self.attachment_ids.remove(attachment_id)
                else:
                    success = False
        
        return success, response

    def test_delete_nonexistent_attachment(self):
        """Test deleting a non-existent attachment"""
        if not self.registration_id:
            if not self.create_test_registration():
                return False, {}
        
        # Generate a random attachment ID that doesn't exist
        fake_attachment_id = str(random.randint(10000, 99999))
        
        success, response = self.run_test(
            "Delete Non-existent Attachment",
            "DELETE",
            f"api/admin-registration/{self.registration_id}/attachment/{fake_attachment_id}",
            404  # Expect 404 Not Found
        )
        
        if success:
            print(f"✅ Correctly received 404 for non-existent attachment ID: {fake_attachment_id}")
        
        return success, response

    def test_get_attachments_nonexistent_registration(self):
        """Test getting attachments for a non-existent registration"""
        # Generate a random registration ID that doesn't exist
        fake_registration_id = str(random.randint(10000, 99999))
        
        success, response = self.run_test(
            "Get Attachments for Non-existent Registration",
            "GET",
            f"api/admin-registration/{fake_registration_id}/attachments",
            404  # Expect 404 Not Found
        )
        
        if success:
            print(f"✅ Correctly received 404 for non-existent registration ID: {fake_registration_id}")
        
        return success, response

    def test_save_attachment_nonexistent_registration(self):
        """Test saving an attachment to a non-existent registration"""
        # Generate a random registration ID that doesn't exist
        fake_registration_id = str(random.randint(10000, 99999))
        
        # Create attachment data
        attachment_data = {
            "type": "Image",
            "name": f"Test Image {self.generate_random_string()}",
            "documentType": "Consultation Report",
            "url": self.generate_sample_base64_image()
        }
        
        success, response = self.run_test(
            "Save Attachment to Non-existent Registration",
            "POST",
            f"api/admin-registration/{fake_registration_id}/attachment",
            404,  # Expect 404 Not Found
            data=attachment_data
        )
        
        if success:
            print(f"✅ Correctly received 404 for non-existent registration ID: {fake_registration_id}")
        
        return success, response

    def test_data_format_verification(self):
        """Test data format verification for image attachments"""
        if not self.registration_id:
            if not self.create_test_registration():
                return False, {}
        
        # First, save attachments with different formats
        print("\n🔍 Testing Data Format Verification...")
        
        # 1. Save with data URI format
        attachment_data_uri = {
            "type": "Image",
            "name": f"Data URI Image {self.generate_random_string()}",
            "documentType": "Consultation Report",
            "url": self.generate_sample_base64_image()
        }
        
        uri_success, uri_response = self.run_test(
            "Save Image with Data URI Format",
            "POST",
            f"api/admin-registration/{self.registration_id}/attachment",
            200,
            data=attachment_data_uri
        )
        
        if uri_success:
            uri_attachment_id = uri_response.get('attachment_id')
            self.attachment_ids.append(uri_attachment_id)
        
        # 2. Save with raw base64 format
        attachment_raw = {
            "type": "Image",
            "name": f"Raw Base64 Image {self.generate_random_string()}",
            "documentType": "Consultation Report",
            "url": self.generate_raw_base64_image()
        }
        
        raw_success, raw_response = self.run_test(
            "Save Image with Raw Base64 Format",
            "POST",
            f"api/admin-registration/{self.registration_id}/attachment",
            200,
            data=attachment_raw
        )
        
        if raw_success:
            raw_attachment_id = raw_response.get('attachment_id')
            self.attachment_ids.append(raw_attachment_id)
        
        # Now retrieve all attachments and verify the format
        get_success, get_response = self.run_test(
            "Get Attachments for Format Verification",
            "GET",
            f"api/admin-registration/{self.registration_id}/attachments",
            200
        )
        
        if get_success:
            attachments = get_response.get('attachments', [])
            format_correct = True
            
            for attachment in attachments:
                if attachment.get('type') == 'Image':
                    url = attachment.get('url', '')
                    if not url.startswith('data:image/'):
                        print(f"❌ Image URL missing data URI format: {url[:30]}...")
                        format_correct = False
                    else:
                        print(f"✅ Image URL has correct data URI format: {url[:30]}...")
            
            if format_correct:
                print("✅ All image attachments have correct data URI format")
                return True, get_response
            else:
                print("❌ Some image attachments have incorrect format")
                return False, get_response
        
        return get_success, get_response

    def run_all_tests(self):
        """Run all attachment tests"""
        print("🚀 Starting Attachment API Tests")
        print(f"🔗 Base URL: {self.base_url}")
        print("=" * 50)
        
        # Create a test registration
        if not self.create_test_registration():
            print("❌ Failed to create test registration, cannot proceed with attachment tests")
            return False
        
        # Test saving attachments
        self.test_save_attachment_with_image()
        self.test_save_attachment_with_raw_base64_image()
        self.test_save_attachment_with_pdf()
        self.test_save_attachment_with_raw_base64_pdf()
        
        # Test retrieving attachments
        self.test_get_attachments()
        
        # Test data format verification
        self.test_data_format_verification()
        
        # Test deleting attachments
        self.test_delete_attachment()
        
        # Test error cases
        self.test_delete_nonexistent_attachment()
        self.test_get_attachments_nonexistent_registration()
        self.test_save_attachment_nonexistent_registration()
        
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
    tester = AttachmentTester(backend_url)
    success = tester.run_all_tests()
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())