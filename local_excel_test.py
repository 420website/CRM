import requests
import pandas as pd
import io
import sys
import random
import string
from datetime import datetime, date, timedelta

def create_sample_excel(num_records=10):
    """Create a sample Excel file with patient data for testing"""
    print(f"Creating sample Excel file with {num_records} records...")
    
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

def test_upload_excel():
    """Test uploading a valid Excel file"""
    # Create sample Excel file
    excel_buffer, num_records = create_sample_excel(20)
    
    # Create files dictionary for requests
    files = {
        'file': ('test_data.xlsx', excel_buffer, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    }
    
    # Test upload
    url = "http://localhost:8001/api/upload-legacy-data"
    print(f"Testing Excel upload at {url}...")
    try:
        response = requests.post(url, files=files)
        print(f"Status code: {response.status_code}")
        if response.status_code == 200:
            print("Excel upload test passed!")
            try:
                response_data = response.json()
                print(f"Records count: {response_data.get('records_count')}")
                print(f"Upload ID: {response_data.get('upload_id')}")
                print(f"Preview of first few records: {response_data.get('preview')}")
                return True, response_data
            except:
                print(f"Response: {response.text}")
                return True, {}
        else:
            print("Excel upload test failed!")
            try:
                print(f"Response: {response.json()}")
            except:
                print(f"Response: {response.text}")
            return False, {}
    except Exception as e:
        print(f"Error: {str(e)}")
        return False, {}

def test_get_legacy_data_summary(upload_id=None):
    """Test getting summary of uploaded legacy data"""
    url = "http://localhost:8001/api/legacy-data-summary"
    print(f"Testing legacy data summary at {url}...")
    try:
        response = requests.get(url)
        print(f"Status code: {response.status_code}")
        if response.status_code == 200:
            print("Legacy data summary test passed!")
            try:
                response_data = response.json()
                print(f"Total records: {response_data.get('total_records')}")
                print(f"Date range: {response_data.get('date_range')}")
                print(f"Top dispositions: {response_data.get('top_dispositions')}")
                print(f"Upload info: {response_data.get('upload_info')}")
                
                # Verify the upload ID matches if provided
                if upload_id and response_data.get('upload_info', {}).get('upload_id') == upload_id:
                    print("Upload ID matches the one from our upload")
                elif upload_id:
                    print("Upload ID doesn't match - this may be due to another test run")
                
                return True, response_data
            except:
                print(f"Response: {response.text}")
                return True, {}
        else:
            print("Legacy data summary test failed!")
            try:
                print(f"Response: {response.json()}")
            except:
                print(f"Response: {response.text}")
            return False, {}
    except Exception as e:
        print(f"Error: {str(e)}")
        return False, {}

def test_claude_chat_with_legacy_data():
    """Test Claude chat integration with legacy data context"""
    url = "http://localhost:8001/api/claude-chat"
    print(f"Testing Claude chat with legacy data at {url}...")
    try:
        data = {
            "message": "Can you analyze the trends in the legacy patient data?",
            "session_id": "test-session-" + ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        }
        response = requests.post(url, json=data)
        print(f"Status code: {response.status_code}")
        if response.status_code == 200:
            print("Claude chat with legacy data test passed!")
            try:
                response_data = response.json()
                print(f"Claude response: {response_data.get('response')[:100]}...")  # Show first 100 chars
                print(f"Session ID: {response_data.get('session_id')}")
                
                # Check if the response mentions legacy data
                if "legacy data" in response_data.get('response', '').lower():
                    print("Response mentions legacy data, indicating context was included")
                else:
                    print("Response doesn't explicitly mention legacy data")
                
                return True, response_data
            except:
                print(f"Response: {response.text}")
                return True, {}
        else:
            print("Claude chat with legacy data test failed!")
            try:
                print(f"Response: {response.json()}")
            except:
                print(f"Response: {response.text}")
            return False, {}
    except Exception as e:
        print(f"Error: {str(e)}")
        return False, {}

def main():
    print("Starting Excel Upload and Legacy Data Tests")
    print("=" * 50)
    
    # Test Excel upload
    upload_success, upload_response = test_upload_excel()
    upload_id = upload_response.get('upload_id') if upload_success else None
    
    # Test legacy data summary
    summary_success, _ = test_get_legacy_data_summary(upload_id)
    
    # Test Claude chat with legacy data
    claude_success, _ = test_claude_chat_with_legacy_data()
    
    # Print overall results
    print("=" * 50)
    print("Test Results:")
    print(f"Excel Upload: {'✅ Passed' if upload_success else '❌ Failed'}")
    print(f"Legacy Data Summary: {'✅ Passed' if summary_success else '❌ Failed'}")
    print(f"Claude Chat with Legacy Data: {'✅ Passed' if claude_success else '❌ Failed'}")
    
    return 0 if upload_success and summary_success and claude_success else 1

if __name__ == "__main__":
    sys.exit(main())