import requests
import unittest
import json
from datetime import datetime, date
import random
import string
import sys
from dotenv import load_dotenv
import os
import pandas as pd
import time

# Load the frontend .env file to get the backend URL
load_dotenv('/app/frontend/.env')
backend_url = os.environ.get('REACT_APP_BACKEND_URL')

class DOBProcessingTester:
    def __init__(self, base_url):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.session_id = None

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
                    return success, response_data
                except:
                    return success, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    response_data = response.json()
                    print(f"Response: {response_data}")
                    return False, response_data
                except:
                    print(f"Response: {response.text}")
                    return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_api_health(self):
        """Test the API health endpoint"""
        return self.run_test(
            "API Health Check",
            "GET",
            "api",
            200
        )

    def test_dob_iso_format(self):
        """Test DOB processing with ISO format (YYYY-MM-DD)"""
        # Generate a random session ID
        self.session_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
        
        # Ask about a specific DOB in ISO format
        query = "If a client's DOB is 1985-06-15, what age range would they be in?"
        
        success, response = self.run_test(
            "DOB Processing - ISO Format (YYYY-MM-DD)",
            "POST",
            "api/claude-chat",
            200,
            data={
                "message": query,
                "session_id": self.session_id
            }
        )
        
        if success:
            # Check if the response contains the correct age range
            response_text = response.get('response', '')
            
            # Calculate the expected age range
            birth_year = 1985
            current_year = datetime.now().year
            age = current_year - birth_year
            expected_range = None
            
            if age < 20:
                expected_range = '0-19'
            elif age < 30:
                expected_range = '20-29'
            elif age < 40:
                expected_range = '30-39'
            elif age < 50:
                expected_range = '40-49'
            elif age < 60:
                expected_range = '50-59'
            elif age < 70:
                expected_range = '60-69'
            elif age < 80:
                expected_range = '70-79'
            elif age < 90:
                expected_range = '80-89'
            else:
                expected_range = '90+'
            
            # Check if the response contains the expected age range
            contains_expected_range = expected_range in response_text
            
            if contains_expected_range:
                print(f"✅ Response correctly identifies the age range ({expected_range}) for DOB 1985-06-15")
                print("\nResponse excerpt:")
                print(response_text[:500] + "..." if len(response_text) > 500 else response_text)
                self.tests_passed += 1
            else:
                print(f"❌ Response does not correctly identify the age range ({expected_range}) for DOB 1985-06-15")
                print("\nResponse excerpt:")
                print(response_text[:500] + "..." if len(response_text) > 500 else response_text)
                
        return success, response

    def test_dob_us_format(self):
        """Test DOB processing with US format (MM/DD/YYYY)"""
        if not self.session_id:
            self.session_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
        
        # Ask about a specific DOB in US format
        query = "If a client's DOB is 12/25/1975, what age range would they be in?"
        
        success, response = self.run_test(
            "DOB Processing - US Format (MM/DD/YYYY)",
            "POST",
            "api/claude-chat",
            200,
            data={
                "message": query,
                "session_id": self.session_id
            }
        )
        
        if success:
            # Check if the response contains the correct age range
            response_text = response.get('response', '')
            
            # Calculate the expected age range
            birth_year = 1975
            current_year = datetime.now().year
            age = current_year - birth_year
            expected_range = None
            
            if age < 20:
                expected_range = '0-19'
            elif age < 30:
                expected_range = '20-29'
            elif age < 40:
                expected_range = '30-39'
            elif age < 50:
                expected_range = '40-49'
            elif age < 60:
                expected_range = '50-59'
            elif age < 70:
                expected_range = '60-69'
            elif age < 80:
                expected_range = '70-79'
            elif age < 90:
                expected_range = '80-89'
            else:
                expected_range = '90+'
            
            # Check if the response contains the expected age range
            contains_expected_range = expected_range in response_text
            
            if contains_expected_range:
                print(f"✅ Response correctly identifies the age range ({expected_range}) for DOB 12/25/1975")
                print("\nResponse excerpt:")
                print(response_text[:500] + "..." if len(response_text) > 500 else response_text)
                self.tests_passed += 1
            else:
                print(f"❌ Response does not correctly identify the age range ({expected_range}) for DOB 12/25/1975")
                print("\nResponse excerpt:")
                print(response_text[:500] + "..." if len(response_text) > 500 else response_text)
                
        return success, response

    def test_dob_iso_with_time(self):
        """Test DOB processing with ISO format including time (YYYY-MM-DDThh:mm:ss)"""
        if not self.session_id:
            self.session_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
        
        # Ask about a specific DOB in ISO format with time
        query = "If a client's DOB is 2000-01-01T00:00:00, what age range would they be in?"
        
        success, response = self.run_test(
            "DOB Processing - ISO Format with Time",
            "POST",
            "api/claude-chat",
            200,
            data={
                "message": query,
                "session_id": self.session_id
            }
        )
        
        if success:
            # Check if the response contains the correct age range
            response_text = response.get('response', '')
            
            # Calculate the expected age range
            birth_year = 2000
            current_year = datetime.now().year
            age = current_year - birth_year
            expected_range = None
            
            if age < 20:
                expected_range = '0-19'
            elif age < 30:
                expected_range = '20-29'
            elif age < 40:
                expected_range = '30-39'
            elif age < 50:
                expected_range = '40-49'
            elif age < 60:
                expected_range = '50-59'
            elif age < 70:
                expected_range = '60-69'
            elif age < 80:
                expected_range = '70-79'
            elif age < 90:
                expected_range = '80-89'
            else:
                expected_range = '90+'
            
            # Check if the response contains the expected age range
            contains_expected_range = expected_range in response_text
            
            if contains_expected_range:
                print(f"✅ Response correctly identifies the age range ({expected_range}) for DOB 2000-01-01T00:00:00")
                print("\nResponse excerpt:")
                print(response_text[:500] + "..." if len(response_text) > 500 else response_text)
                self.tests_passed += 1
            else:
                print(f"❌ Response does not correctly identify the age range ({expected_range}) for DOB 2000-01-01T00:00:00")
                print("\nResponse excerpt:")
                print(response_text[:500] + "..." if len(response_text) > 500 else response_text)
                
        return success, response

    def test_edge_case_current_year(self):
        """Test age calculation for someone born in the current year"""
        if not self.session_id:
            self.session_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
        
        # Get the current year
        current_year = datetime.now().year
        
        # Ask about a DOB in the current year
        query = f"If a client's DOB is {current_year}-01-01, what age range would they be in?"
        
        success, response = self.run_test(
            "Age Calculation - Born in Current Year",
            "POST",
            "api/claude-chat",
            200,
            data={
                "message": query,
                "session_id": self.session_id
            }
        )
        
        if success:
            # Check if the response contains the correct age range (should be 0-19)
            response_text = response.get('response', '')
            expected_range = '0-19'
            
            # Check if the response contains the expected age range
            contains_expected_range = expected_range in response_text
            
            if contains_expected_range:
                print(f"✅ Response correctly identifies the age range ({expected_range}) for someone born in the current year")
                print("\nResponse excerpt:")
                print(response_text[:500] + "..." if len(response_text) > 500 else response_text)
                self.tests_passed += 1
            else:
                print(f"❌ Response does not correctly identify the age range ({expected_range}) for someone born in the current year")
                print("\nResponse excerpt:")
                print(response_text[:500] + "..." if len(response_text) > 500 else response_text)
                
        return success, response

    def test_edge_case_very_old(self):
        """Test age calculation for someone very old (100+ years)"""
        if not self.session_id:
            self.session_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
        
        # Get the current year
        current_year = datetime.now().year
        
        # Ask about a DOB 100 years ago
        query = f"If a client's DOB is {current_year - 100}-01-01, what age range would they be in?"
        
        success, response = self.run_test(
            "Age Calculation - 100 Years Old",
            "POST",
            "api/claude-chat",
            200,
            data={
                "message": query,
                "session_id": self.session_id
            }
        )
        
        if success:
            # Check if the response contains the correct age range (should be 90+)
            response_text = response.get('response', '')
            expected_range = '90+'
            
            # Check if the response contains the expected age range
            contains_expected_range = expected_range in response_text
            
            if contains_expected_range:
                print(f"✅ Response correctly identifies the age range ({expected_range}) for someone 100 years old")
                print("\nResponse excerpt:")
                print(response_text[:500] + "..." if len(response_text) > 500 else response_text)
                self.tests_passed += 1
            else:
                print(f"❌ Response does not correctly identify the age range ({expected_range}) for someone 100 years old")
                print("\nResponse excerpt:")
                print(response_text[:500] + "..." if len(response_text) > 500 else response_text)
                
        return success, response

    def run_all_tests(self):
        """Run all DOB processing tests"""
        print("🚀 Starting DOB Processing Tests")
        print(f"🔗 Base URL: {self.base_url}")
        print("=" * 50)
        
        # Basic API health check
        self.test_api_health()
        
        # DOB processing tests
        self.test_dob_iso_format()
        time.sleep(1)  # Add a small delay between requests
        self.test_dob_us_format()
        time.sleep(1)
        self.test_dob_iso_with_time()
        time.sleep(1)
        self.test_edge_case_current_year()
        time.sleep(1)
        self.test_edge_case_very_old()
        
        print("\n" + "=" * 50)
        print(f"📊 Tests passed: {self.tests_passed}/{self.tests_run}")
        
        return self.tests_passed == self.tests_run


def main():
    # Get the backend URL from the frontend .env file
    if not backend_url:
        print("❌ Error: REACT_APP_BACKEND_URL not found in frontend .env file")
        return 1
    
    print(f"🔗 Using backend URL from .env: {backend_url}")
    
    # Run the tests
    tester = DOBProcessingTester(backend_url)
    success = tester.run_all_tests()
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())