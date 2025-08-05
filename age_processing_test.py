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

class AgeProcessingTester:
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

    def test_claude_chat_with_age_query(self):
        """Test the Claude chat endpoint with the Age button query"""
        # Generate a random session ID
        self.session_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
        
        # Use the exact query from the Age button
        query = "Show clients by age range?"
        
        success, response = self.run_test(
            "Claude Chat - Age Button Query",
            "POST",
            "api/claude-chat",
            200,
            data={
                "message": query,
                "session_id": self.session_id
            }
        )
        
        if success:
            # Check if the response contains age range information
            response_text = response.get('response', '')
            
            # Check for age range patterns
            age_ranges = ['0-19', '20-29', '30-39', '40-49', '50-59', '60-69', '70-79', '80-89', '90+']
            contains_age_ranges = any(age_range in response_text for age_range in age_ranges)
            
            if contains_age_ranges:
                print("✅ Response contains age range information")
                print("\nResponse excerpt:")
                print(response_text[:500] + "..." if len(response_text) > 500 else response_text)
                
                # Extract and verify age range percentages
                try:
                    # Check if percentages add up to approximately 100%
                    percentage_sum = 0
                    for line in response_text.split('\n'):
                        if '%' in line:
                            # Try to extract percentage values
                            parts = line.split('%')
                            for i in range(len(parts)-1):
                                # Look for the number before the % sign
                                number_part = parts[i].strip().split(' ')[-1].replace('(', '')
                                try:
                                    percentage = float(number_part)
                                    percentage_sum += percentage
                                except ValueError:
                                    continue
                    
                    # Check if percentages sum to approximately 100%
                    if 99.0 <= percentage_sum <= 101.0:
                        print(f"✅ Age range percentages sum to approximately 100% ({percentage_sum:.1f}%)")
                        self.tests_passed += 1
                    else:
                        print(f"❌ Age range percentages do not sum to 100% (got {percentage_sum:.1f}%)")
                except Exception as e:
                    print(f"❌ Error analyzing percentages: {str(e)}")
            else:
                print("❌ Response does not contain age range information")
                print("\nResponse excerpt:")
                print(response_text[:500] + "..." if len(response_text) > 500 else response_text)
                
        return success, response

    def test_age_calculation_accuracy(self):
        """Test the accuracy of age calculation from DOB"""
        if not self.session_id:
            self.session_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
        
        # Ask a specific question about age calculation
        query = "If someone was born on January 1, 1990, what age range would they be in?"
        
        success, response = self.run_test(
            "Claude Chat - Age Calculation Accuracy",
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
            birth_year = 1990
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
                print(f"✅ Response correctly identifies the age range ({expected_range}) for someone born in 1990")
                print("\nResponse excerpt:")
                print(response_text[:500] + "..." if len(response_text) > 500 else response_text)
                self.tests_passed += 1
            else:
                print(f"❌ Response does not correctly identify the age range ({expected_range}) for someone born in 1990")
                print("\nResponse excerpt:")
                print(response_text[:500] + "..." if len(response_text) > 500 else response_text)
                
        return success, response

    def test_dob_format_handling(self):
        """Test that the system can handle different DOB formats"""
        if not self.session_id:
            self.session_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
        
        # Ask about DOB format handling
        query = "How does the system handle different date of birth formats?"
        
        success, response = self.run_test(
            "Claude Chat - DOB Format Handling",
            "POST",
            "api/claude-chat",
            200,
            data={
                "message": query,
                "session_id": self.session_id
            }
        )
        
        if success:
            # Check if the response mentions different date formats
            response_text = response.get('response', '')
            
            # Look for keywords related to date format handling
            format_keywords = ['format', 'ISO', 'yyyy-mm-dd', 'mm/dd/yyyy', 'parse', 'datetime']
            contains_format_info = any(keyword.lower() in response_text.lower() for keyword in format_keywords)
            
            if contains_format_info:
                print("✅ Response explains DOB format handling")
                print("\nResponse excerpt:")
                print(response_text[:500] + "..." if len(response_text) > 500 else response_text)
                self.tests_passed += 1
            else:
                print("❌ Response does not explain DOB format handling")
                print("\nResponse excerpt:")
                print(response_text[:500] + "..." if len(response_text) > 500 else response_text)
                
        return success, response

    def test_age_range_grouping(self):
        """Test the 10-year age range categorization logic"""
        if not self.session_id:
            self.session_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
        
        # Ask about age range grouping
        query = "What are all the age range groups used in the system?"
        
        success, response = self.run_test(
            "Claude Chat - Age Range Grouping",
            "POST",
            "api/claude-chat",
            200,
            data={
                "message": query,
                "session_id": self.session_id
            }
        )
        
        if success:
            # Check if the response lists all age ranges
            response_text = response.get('response', '')
            
            # Define the expected age ranges
            expected_ranges = ['0-19', '20-29', '30-39', '40-49', '50-59', '60-69', '70-79', '80-89', '90+']
            
            # Check if all expected ranges are mentioned
            missing_ranges = [r for r in expected_ranges if r not in response_text]
            
            if not missing_ranges:
                print("✅ Response lists all expected age ranges")
                print("\nResponse excerpt:")
                print(response_text[:500] + "..." if len(response_text) > 500 else response_text)
                self.tests_passed += 1
            else:
                print(f"❌ Response is missing some age ranges: {', '.join(missing_ranges)}")
                print("\nResponse excerpt:")
                print(response_text[:500] + "..." if len(response_text) > 500 else response_text)
                
        return success, response

    def test_age_statistics_in_context(self):
        """Test that age statistics are included in the AI context"""
        if not self.session_id:
            self.session_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
        
        # Ask a specific question that would require age statistics in the context
        query = "What is the most common age range among clients?"
        
        success, response = self.run_test(
            "Claude Chat - Age Statistics in Context",
            "POST",
            "api/claude-chat",
            200,
            data={
                "message": query,
                "session_id": self.session_id
            }
        )
        
        if success:
            # Check if the response identifies a most common age range
            response_text = response.get('response', '')
            
            # Look for patterns indicating a most common age range
            contains_most_common = any(f"{r}" in response_text and "most common" in response_text.lower() for r in ['0-19', '20-29', '30-39', '40-49', '50-59', '60-69', '70-79', '80-89', '90+'])
            
            if contains_most_common:
                print("✅ Response identifies a most common age range")
                print("\nResponse excerpt:")
                print(response_text[:500] + "..." if len(response_text) > 500 else response_text)
                self.tests_passed += 1
            else:
                print("❌ Response does not identify a most common age range")
                print("\nResponse excerpt:")
                print(response_text[:500] + "..." if len(response_text) > 500 else response_text)
                
        return success, response

    def run_all_tests(self):
        """Run all age processing tests"""
        print("🚀 Starting Age Processing Tests")
        print(f"🔗 Base URL: {self.base_url}")
        print("=" * 50)
        
        # Basic API health check
        self.test_api_health()
        
        # Age processing tests
        self.test_claude_chat_with_age_query()
        time.sleep(1)  # Add a small delay between requests
        self.test_age_calculation_accuracy()
        time.sleep(1)
        self.test_dob_format_handling()
        time.sleep(1)
        self.test_age_range_grouping()
        time.sleep(1)
        self.test_age_statistics_in_context()
        
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
    tester = AgeProcessingTester(backend_url)
    success = tester.run_all_tests()
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())