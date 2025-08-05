import requests
import unittest
import json
import pandas as pd
import io
import os
import sys
import random
import string
from datetime import datetime, date, timedelta
from dotenv import load_dotenv

class ExcelUploadTester:
    def __init__(self, base_url):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.upload_id = None
        self.records_count = 0

    def run_test(self, name, method, endpoint, expected_status, data=None, files=None, headers=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        if not headers and not files:
            headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers)
            elif method == 'POST':
                if files:
                    response = requests.post(url, files=files)
                else:
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

    def create_sample_excel(self, num_records=10):
        """Create a sample Excel file with patient data for testing"""
        print(f"\n📊 Creating sample Excel file with {num_records} records...")
        
        # Generate random patient data
        data = []
        for i in range(num_records):
            # Generate random dates within the last 5 years
            reg_date = (date.today() - timedelta(days=random.randint(0, 1825))).strftime('%Y-%m-%d')
            
            # Generate random patient record
            record = {
                'firstName': f"Patient{i}",
                'lastName': f"Test{i}",
                'regDate': reg_date,
                'disposition': random.choice(['POCT NEG', 'POCT POS', 'RNA POS', 'RNA NEG', 'DECLINED']),
                'healthCard': ''.join(random.choices(string.digits, k=10)),
                'age': random.randint(18, 80),
                'gender': random.choice(['Male', 'Female']),
                'province': random.choice(['Ontario', 'Quebec', 'British Columbia']),
                'city': random.choice(['Toronto', 'Ottawa', 'Hamilton', 'London', 'Windsor']),
                'referralSite': random.choice(['Community Clinic', 'Hospital', 'Outreach', 'Self-Referral']),
                'phone': ''.join(random.choices(string.digits, k=10)),
                'email': f"patient{i}@example.com",
                'notes': f"Test patient record {i}"
            }
            data.append(record)
        
        # Create DataFrame
        df = pd.DataFrame(data)
        
        # Create Excel file in memory
        excel_buffer = io.BytesIO()
        df.to_excel(excel_buffer, index=False)
        excel_buffer.seek(0)
        
        return excel_buffer, len(data)

    def create_sample_csv(self, num_records=10):
        """Create a sample CSV file with patient data for testing"""
        print(f"\n📊 Creating sample CSV file with {num_records} records...")
        
        # Generate random patient data
        data = []
        for i in range(num_records):
            # Generate random dates within the last 5 years
            reg_date = (date.today() - timedelta(days=random.randint(0, 1825))).strftime('%Y-%m-%d')
            
            # Generate random patient record
            record = {
                'firstName': f"Patient{i}",
                'lastName': f"Test{i}",
                'regDate': reg_date,
                'disposition': random.choice(['POCT NEG', 'POCT POS', 'RNA POS', 'RNA NEG', 'DECLINED']),
                'healthCard': ''.join(random.choices(string.digits, k=10)),
                'age': random.randint(18, 80),
                'gender': random.choice(['Male', 'Female']),
                'province': random.choice(['Ontario', 'Quebec', 'British Columbia']),
                'city': random.choice(['Toronto', 'Ottawa', 'Hamilton', 'London', 'Windsor']),
                'referralSite': random.choice(['Community Clinic', 'Hospital', 'Outreach', 'Self-Referral']),
                'phone': ''.join(random.choices(string.digits, k=10)),
                'email': f"patient{i}@example.com",
                'notes': f"Test patient record {i}"
            }
            data.append(record)
        
        # Create DataFrame
        df = pd.DataFrame(data)
        
        # Create CSV file in memory
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)
        csv_buffer.seek(0)
        
        return csv_buffer.getvalue(), len(data)

    def create_invalid_file(self):
        """Create an invalid file (not Excel/CSV) for testing"""
        print("\n📊 Creating invalid file for testing...")
        
        # Create a text file
        text_buffer = io.StringIO()
        text_buffer.write("This is not a valid Excel or CSV file.")
        text_buffer.seek(0)
        
        return text_buffer.getvalue()

    def test_upload_excel(self):
        """Test uploading a valid Excel file"""
        # Create sample Excel file
        excel_buffer, num_records = self.create_sample_excel(20)
        
        # Create files dictionary for requests
        files = {
            'file': ('test_data.xlsx', excel_buffer, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        }
        
        # Test upload
        success, response = self.run_test(
            "Upload Excel File",
            "POST",
            "api/upload-legacy-data",
            200,
            files=files
        )
        
        if success:
            print(f"✅ Successfully uploaded {response.get('records_count')} records")
            print(f"✅ Upload ID: {response.get('upload_id')}")
            print(f"✅ Preview of first few records: {response.get('preview')}")
            
            # Save upload ID for later tests
            self.upload_id = response.get('upload_id')
            self.records_count = response.get('records_count')
            
        return success, response

    def test_upload_csv(self):
        """Test uploading a valid CSV file"""
        # Create sample CSV file
        csv_data, num_records = self.create_sample_csv(15)
        
        # Create files dictionary for requests
        files = {
            'file': ('test_data.csv', csv_data, 'text/csv')
        }
        
        # Test upload
        success, response = self.run_test(
            "Upload CSV File",
            "POST",
            "api/upload-legacy-data",
            200,
            files=files
        )
        
        if success:
            print(f"✅ Successfully uploaded {response.get('records_count')} records")
            print(f"✅ Upload ID: {response.get('upload_id')}")
            print(f"✅ Preview of first few records: {response.get('preview')}")
            
            # Save upload ID for later tests
            self.upload_id = response.get('upload_id')
            self.records_count = response.get('records_count')
            
        return success, response

    def test_upload_invalid_file(self):
        """Test uploading an invalid file (not Excel/CSV)"""
        # Create invalid file
        invalid_data = self.create_invalid_file()
        
        # Create files dictionary for requests
        files = {
            'file': ('invalid_file.txt', invalid_data, 'text/plain')
        }
        
        # Test upload - should fail with 400 Bad Request
        success, response = self.run_test(
            "Upload Invalid File",
            "POST",
            "api/upload-legacy-data",
            400,  # Expecting 400 Bad Request
            files=files
        )
        
        if success:
            print("✅ Server correctly rejected invalid file type")
            
        return success, response

    def test_upload_empty_file(self):
        """Test uploading an empty Excel file"""
        # Create empty Excel file
        empty_df = pd.DataFrame()
        excel_buffer = io.BytesIO()
        empty_df.to_excel(excel_buffer, index=False)
        excel_buffer.seek(0)
        
        # Create files dictionary for requests
        files = {
            'file': ('empty.xlsx', excel_buffer, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        }
        
        # Test upload - should succeed but with 0 records
        success, response = self.run_test(
            "Upload Empty Excel File",
            "POST",
            "api/upload-legacy-data",
            200,
            files=files
        )
        
        if success:
            if response.get('records_count') == 0:
                print("✅ Server correctly processed empty file with 0 records")
            else:
                print(f"❌ Expected 0 records, got {response.get('records_count')}")
                success = False
            
        return success, response

    def test_get_legacy_data_summary(self):
        """Test getting summary of uploaded legacy data"""
        # First ensure we have data uploaded
        if not self.upload_id:
            self.test_upload_excel()
        
        # Test getting summary
        success, response = self.run_test(
            "Get Legacy Data Summary",
            "GET",
            "api/legacy-data-summary",
            200
        )
        
        if success:
            print(f"✅ Total records: {response.get('total_records')}")
            print(f"✅ Date range: {response.get('date_range')}")
            print(f"✅ Top dispositions: {response.get('top_dispositions')}")
            print(f"✅ Upload info: {response.get('upload_info')}")
            
            # Verify the upload ID matches
            if response.get('upload_info', {}).get('upload_id') == self.upload_id:
                print("✅ Upload ID matches the one from our upload")
            else:
                print("⚠️ Upload ID doesn't match - this may be due to another test run")
                
            # Verify record count matches
            if response.get('total_records') == self.records_count:
                print("✅ Record count matches our upload")
            else:
                print(f"⚠️ Record count doesn't match - expected {self.records_count}, got {response.get('total_records')}")
            
        return success, response

    def test_get_legacy_data_summary_no_data(self):
        """Test getting summary when no data has been uploaded"""
        # This test assumes we can clear the database or that no data has been uploaded yet
        # Since we can't easily clear the database in this test, we'll just check the response format
        
        success, response = self.run_test(
            "Get Legacy Data Summary (No Data)",
            "GET",
            "api/legacy-data-summary",
            200  # Should still return 200 with empty data, or 404 if properly implemented
        )
        
        # If we get a 404, that's also acceptable
        if not success and response.get('detail') == "No legacy data found. Please upload an Excel file first.":
            print("✅ Server correctly reported no legacy data found")
            self.tests_passed += 1  # Manually increment since we're accepting a different status code
            return True, response
            
        if success:
            print("⚠️ Got a successful response - this means data exists from previous uploads")
            
        return success, response

    def test_claude_chat_with_legacy_data(self):
        """Test Claude chat integration with legacy data context"""
        # First ensure we have data uploaded
        if not self.upload_id:
            self.test_upload_excel()
        
        # Test Claude chat with a query about the legacy data
        data = {
            "message": "Can you analyze the trends in the legacy patient data?",
            "session_id": "test-session-" + ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        }
        
        success, response = self.run_test(
            "Claude Chat with Legacy Data Context",
            "POST",
            "api/claude-chat",
            200,
            data=data
        )
        
        if success:
            print(f"✅ Claude response: {response.get('response')[:100]}...")  # Show first 100 chars
            print(f"✅ Session ID: {response.get('session_id')}")
            
            # Check if the response mentions legacy data
            if "legacy data" in response.get('response', '').lower():
                print("✅ Response mentions legacy data, indicating context was included")
            else:
                print("⚠️ Response doesn't explicitly mention legacy data")
            
        return success, response

    def test_claude_chat_follow_up(self):
        """Test Claude chat session continuity with follow-up question"""
        # First ensure we have a session from previous test
        first_test_success, first_response = self.test_claude_chat_with_legacy_data()
        
        if not first_test_success:
            print("❌ Could not establish initial Claude chat session")
            return False, {}
        
        # Get session ID from first response
        session_id = first_response.get('session_id')
        
        # Test follow-up question using same session ID
        data = {
            "message": "What are the most common dispositions in the data?",
            "session_id": session_id
        }
        
        success, response = self.run_test(
            "Claude Chat Follow-up Question",
            "POST",
            "api/claude-chat",
            200,
            data=data
        )
        
        if success:
            print(f"✅ Claude response to follow-up: {response.get('response')[:100]}...")  # Show first 100 chars
            print(f"✅ Session ID maintained: {response.get('session_id')}")
            
            # Check if the response mentions dispositions
            if "disposition" in response.get('response', '').lower():
                print("✅ Response mentions dispositions, indicating context was maintained")
            else:
                print("⚠️ Response doesn't explicitly mention dispositions")
            
        return success, response

    def run_all_tests(self):
        """Run all Excel upload and legacy data tests"""
        print("🚀 Starting Excel Upload and Legacy Data Tests")
        print(f"🔗 Base URL: {self.base_url}")
        print("=" * 50)
        
        # Test file uploads
        print("\n" + "=" * 50)
        print("🔍 Testing Excel/CSV Upload Functionality")
        print("=" * 50)
        self.test_upload_excel()
        self.test_upload_csv()
        self.test_upload_invalid_file()
        self.test_upload_empty_file()
        
        # Test data summary
        print("\n" + "=" * 50)
        print("🔍 Testing Legacy Data Summary")
        print("=" * 50)
        self.test_get_legacy_data_summary()
        
        # Test Claude integration
        print("\n" + "=" * 50)
        print("🔍 Testing Claude AI Integration with Legacy Data")
        print("=" * 50)
        self.test_claude_chat_with_legacy_data()
        self.test_claude_chat_follow_up()
        
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
    tester = ExcelUploadTester(backend_url)
    success = tester.run_all_tests()
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())