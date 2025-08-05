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

class AgeButtonTester:
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

    def test_api_health(self):
        """Test the API health endpoint"""
        return self.run_test(
            "API Health Check",
            "GET",
            "api",
            200
        )

    def test_claude_chat_age_query(self):
        """Test the Claude chat endpoint with an age-related query"""
        # Generate a random session ID
        self.session_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
        
        # Test with the exact query used by the Age button
        query = "Show clients by age range?"
        
        success, response = self.run_test(
            "Claude Chat - Age Query",
            "POST",
            "api/claude-chat",
            200,
            data={
                "message": query,
                "session_id": self.session_id
            }
        )
        
        if success:
            # Check if the response contains age-related information
            response_text = response.get('response', '')
            
            # Check for age range keywords in the response
            age_keywords = ['age', 'range', '0-19', '20-29', '30-39', '40-49', '50-59', '60-69', '70-79', '80-89', '90+', 'distribution']
            contains_age_info = any(keyword.lower() in response_text.lower() for keyword in age_keywords)
            
            if contains_age_info:
                print("✅ Response contains age-related information")
                print("\nResponse excerpt:")
                print(response_text[:500] + "..." if len(response_text) > 500 else response_text)
                self.tests_passed += 1
            else:
                print("❌ Response does not contain age-related information")
                print("\nResponse excerpt:")
                print(response_text[:500] + "..." if len(response_text) > 500 else response_text)
                
        return success, response

    def test_claude_chat_age_context(self):
        """Test that the Claude chat endpoint includes age statistics in the context"""
        # We can't directly test the context sent to Claude, but we can infer it from the response
        # by asking a specific question about age statistics
        
        if not self.session_id:
            self.session_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
        
        # Ask a specific question about age statistics
        query = "What percentage of clients are in the 30-39 age range?"
        
        success, response = self.run_test(
            "Claude Chat - Age Statistics Context",
            "POST",
            "api/claude-chat",
            200,
            data={
                "message": query,
                "session_id": self.session_id
            }
        )
        
        if success:
            # Check if the response contains specific age range percentages
            response_text = response.get('response', '')
            
            # Look for percentage patterns like "X%" or "X.X%" related to the 30-39 age range
            contains_percentage = '30-39' in response_text and ('%' in response_text)
            
            if contains_percentage:
                print("✅ Response contains specific age range percentages")
                print("\nResponse excerpt:")
                print(response_text[:500] + "..." if len(response_text) > 500 else response_text)
                self.tests_passed += 1
            else:
                print("❌ Response does not contain specific age range percentages")
                print("\nResponse excerpt:")
                print(response_text[:500] + "..." if len(response_text) > 500 else response_text)
                
        return success, response

    def test_claude_chat_age_calculation(self):
        """Test that the age calculation logic works correctly"""
        # We can't directly test the backend calculation, but we can infer it from the response
        # by asking a specific question about age calculation
        
        if not self.session_id:
            self.session_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
        
        # Ask a specific question about how ages are calculated
        query = "How do you calculate the age ranges from DOB?"
        
        success, response = self.run_test(
            "Claude Chat - Age Calculation Logic",
            "POST",
            "api/claude-chat",
            200,
            data={
                "message": query,
                "session_id": self.session_id
            }
        )
        
        if success:
            # Check if the response mentions the calculation logic
            response_text = response.get('response', '')
            
            # Look for keywords related to age calculation
            calculation_keywords = ['calculate', 'dob', 'date of birth', 'today', 'year', 'subtract', 'difference']
            contains_calculation_info = any(keyword.lower() in response_text.lower() for keyword in calculation_keywords)
            
            if contains_calculation_info:
                print("✅ Response explains age calculation logic")
                print("\nResponse excerpt:")
                print(response_text[:500] + "..." if len(response_text) > 500 else response_text)
                self.tests_passed += 1
            else:
                print("❌ Response does not explain age calculation logic")
                print("\nResponse excerpt:")
                print(response_text[:500] + "..." if len(response_text) > 500 else response_text)
                
        return success, response

    def test_claude_chat_age_distribution(self):
        """Test that the Claude chat endpoint can provide age distribution information"""
        
        if not self.session_id:
            self.session_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
        
        # Ask for the age distribution
        query = "What is the age distribution of clients?"
        
        success, response = self.run_test(
            "Claude Chat - Age Distribution",
            "POST",
            "api/claude-chat",
            200,
            data={
                "message": query,
                "session_id": self.session_id
            }
        )
        
        if success:
            # Check if the response contains age distribution information
            response_text = response.get('response', '')
            
            # Look for age range patterns
            age_ranges = ['0-19', '20-29', '30-39', '40-49', '50-59', '60-69', '70-79', '80-89', '90+']
            contains_distribution = any(age_range in response_text for age_range in age_ranges)
            
            if contains_distribution:
                print("✅ Response contains age distribution information")
                print("\nResponse excerpt:")
                print(response_text[:500] + "..." if len(response_text) > 500 else response_text)
                self.tests_passed += 1
            else:
                print("❌ Response does not contain age distribution information")
                print("\nResponse excerpt:")
                print(response_text[:500] + "..." if len(response_text) > 500 else response_text)
                
        return success, response

    def test_claude_chat_empty_message(self):
        """Test the Claude chat endpoint with an empty message (error handling)"""
        
        if not self.session_id:
            self.session_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
        
        # Test with an empty message
        success, response = self.run_test(
            "Claude Chat - Empty Message",
            "POST",
            "api/claude-chat",
            422,  # Expecting validation error
            data={
                "message": "",
                "session_id": self.session_id
            }
        )
        
        return success, response

    def run_all_tests(self):
        """Run all Age button tests"""
        print("🚀 Starting Age Button Tests")
        print(f"🔗 Base URL: {self.base_url}")
        print("=" * 50)
        
        # Basic API health check
        self.test_api_health()
        
        # Age-related tests
        self.test_claude_chat_age_query()
        time.sleep(1)  # Add a small delay between requests
        self.test_claude_chat_age_context()
        time.sleep(1)
        self.test_claude_chat_age_calculation()
        time.sleep(1)
        self.test_claude_chat_age_distribution()
        time.sleep(1)
        self.test_claude_chat_empty_message()
        
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
    tester = AgeButtonTester(backend_url)
    success = tester.run_all_tests()
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())