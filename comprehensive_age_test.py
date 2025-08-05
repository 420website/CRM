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

class ComprehensiveAgeTester:
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

    def test_age_button_query(self):
        """Test the exact query used by the Age button"""
        # Generate a random session ID
        self.session_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
        
        # Use the exact query from the Age button
        query = "Show clients by age range?"
        
        success, response = self.run_test(
            "Age Button Query",
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
                self.tests_passed += 1
            else:
                print("❌ Response does not contain age range information")
                print("\nResponse excerpt:")
                print(response_text[:500] + "..." if len(response_text) > 500 else response_text)
                
        return success, response

    def test_age_range_counts(self):
        """Test that the age range counts are provided"""
        if not self.session_id:
            self.session_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
        
        # Ask for specific counts
        query = "How many clients are in each age range?"
        
        success, response = self.run_test(
            "Age Range Counts",
            "POST",
            "api/claude-chat",
            200,
            data={
                "message": query,
                "session_id": self.session_id
            }
        )
        
        if success:
            # Check if the response contains counts for each age range
            response_text = response.get('response', '')
            
            # Define the expected age ranges
            age_ranges = ['0-19', '20-29', '30-39', '40-49', '50-59', '60-69', '70-79', '80-89', '90+']
            
            # Check if counts are provided for each age range
            contains_counts = all(age_range in response_text and any(char.isdigit() for char in response_text.split(age_range)[1].split('\n')[0]) for age_range in age_ranges if age_range in response_text)
            
            if contains_counts:
                print("✅ Response contains counts for age ranges")
                print("\nResponse excerpt:")
                print(response_text[:500] + "..." if len(response_text) > 500 else response_text)
                self.tests_passed += 1
            else:
                print("❌ Response does not contain counts for all age ranges")
                print("\nResponse excerpt:")
                print(response_text[:500] + "..." if len(response_text) > 500 else response_text)
                
        return success, response

    def test_age_range_percentages(self):
        """Test that the age range percentages are provided"""
        if not self.session_id:
            self.session_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
        
        # Ask for percentages
        query = "What percentage of clients are in each age range?"
        
        success, response = self.run_test(
            "Age Range Percentages",
            "POST",
            "api/claude-chat",
            200,
            data={
                "message": query,
                "session_id": self.session_id
            }
        )
        
        if success:
            # Check if the response contains percentages for age ranges
            response_text = response.get('response', '')
            
            # Check if percentages are provided
            contains_percentages = '%' in response_text
            
            if contains_percentages:
                print("✅ Response contains percentages for age ranges")
                print("\nResponse excerpt:")
                print(response_text[:500] + "..." if len(response_text) > 500 else response_text)
                self.tests_passed += 1
            else:
                print("❌ Response does not contain percentages for age ranges")
                print("\nResponse excerpt:")
                print(response_text[:500] + "..." if len(response_text) > 500 else response_text)
                
        return success, response

    def test_total_records_with_age(self):
        """Test that the total number of records with age data is provided"""
        if not self.session_id:
            self.session_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
        
        # Ask for the total number of records with age data
        query = "How many total records have age data?"
        
        success, response = self.run_test(
            "Total Records with Age Data",
            "POST",
            "api/claude-chat",
            200,
            data={
                "message": query,
                "session_id": self.session_id
            }
        )
        
        if success:
            # Check if the response contains the total number of records with age data
            response_text = response.get('response', '')
            
            # Look for patterns indicating the total number of records
            contains_total = any(keyword in response_text.lower() for keyword in ['total', 'records', 'clients']) and any(char.isdigit() for char in response_text)
            
            if contains_total:
                print("✅ Response contains the total number of records with age data")
                print("\nResponse excerpt:")
                print(response_text[:500] + "..." if len(response_text) > 500 else response_text)
                self.tests_passed += 1
            else:
                print("❌ Response does not contain the total number of records with age data")
                print("\nResponse excerpt:")
                print(response_text[:500] + "..." if len(response_text) > 500 else response_text)
                
        return success, response

    def test_most_common_age_range(self):
        """Test that the most common age range is identified"""
        if not self.session_id:
            self.session_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
        
        # Ask for the most common age range
        query = "What is the most common age range among clients?"
        
        success, response = self.run_test(
            "Most Common Age Range",
            "POST",
            "api/claude-chat",
            200,
            data={
                "message": query,
                "session_id": self.session_id
            }
        )
        
        if success:
            # Check if the response identifies the most common age range
            response_text = response.get('response', '')
            
            # Look for patterns indicating the most common age range
            contains_most_common = any(f"{r}" in response_text and "most common" in response_text.lower() for r in ['0-19', '20-29', '30-39', '40-49', '50-59', '60-69', '70-79', '80-89', '90+'])
            
            if contains_most_common:
                print("✅ Response identifies the most common age range")
                print("\nResponse excerpt:")
                print(response_text[:500] + "..." if len(response_text) > 500 else response_text)
                self.tests_passed += 1
            else:
                print("❌ Response does not identify the most common age range")
                print("\nResponse excerpt:")
                print(response_text[:500] + "..." if len(response_text) > 500 else response_text)
                
        return success, response

    def run_all_tests(self):
        """Run all comprehensive age tests"""
        print("🚀 Starting Comprehensive Age Tests")
        print(f"🔗 Base URL: {self.base_url}")
        print("=" * 50)
        
        # Basic API health check
        self.test_api_health()
        
        # Comprehensive age tests
        self.test_age_button_query()
        time.sleep(1)  # Add a small delay between requests
        self.test_age_range_counts()
        time.sleep(1)
        self.test_age_range_percentages()
        time.sleep(1)
        self.test_total_records_with_age()
        time.sleep(1)
        self.test_most_common_age_range()
        
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
    tester = ComprehensiveAgeTester(backend_url)
    success = tester.run_all_tests()
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())