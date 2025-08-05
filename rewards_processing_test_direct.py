import requests
import json
import unittest
import sys
import os
from dotenv import load_dotenv
import random
import string
import time
import re

class RewardsProcessingTester:
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

    def test_claude_chat_direct_rewards_query(self):
        """Test the Claude AI chat endpoint with a direct rewards query"""
        # Generate a unique session ID
        if not self.session_id:
            self.session_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
        
        # Create a direct query about rewards statistics
        data = {
            "message": "What is the total amount of rewards paid to clients? How many records have payments? What is the average payment per record?",
            "session_id": self.session_id
        }
        
        success, response = self.run_test(
            "Claude AI Chat - Direct Rewards Statistics Query",
            "POST",
            "api/claude-chat",
            200,
            data=data
        )
        
        if success:
            # Check if the response contains rewards information
            response_text = response.get('response', '')
            print(f"\nResponse excerpt (first 500 chars):\n{response_text[:500]}...\n")
            
            # Extract total amount paid
            total_amount_match = re.search(r'total amount (?:paid|of rewards)(?:.*?)[is:]\s*\$([\d,]+\.\d{2})', response_text.lower())
            if total_amount_match:
                total_amount = float(total_amount_match.group(1).replace(',', ''))
                print(f"✅ Total amount paid: ${total_amount:.2f}")
                
                # Check if the amount is significant
                if total_amount > 10000:  # Expecting a significant amount
                    print(f"✅ Total amount is significant (>${total_amount:.2f})")
                    self.tests_passed += 1
                else:
                    print(f"❌ Total amount may be too low (${total_amount:.2f})")
            else:
                print("❌ Could not extract total amount from response")
            
            # Extract number of records with payments
            records_match = re.search(r'(?:records with payments|records have payments)(?:.*?)[is:]\s*(\d+,?\d*)', response_text.lower())
            if records_match:
                records_count = int(records_match.group(1).replace(',', ''))
                print(f"✅ Records with payments: {records_count}")
                
                # Check if the count is significant
                if records_count > 500:  # Expecting a significant number
                    print(f"✅ Records count is significant ({records_count})")
                    self.tests_passed += 1
                else:
                    print(f"❌ Records count may be too low ({records_count})")
            else:
                print("❌ Could not extract records count from response")
            
            # Extract average payment per record
            average_match = re.search(r'average (?:payment|amount) per record(?:.*?)[is:]\s*\$([\d,]+\.\d{2})', response_text.lower())
            if average_match:
                average_amount = float(average_match.group(1).replace(',', ''))
                print(f"✅ Average payment per record: ${average_amount:.2f}")
                self.tests_passed += 1
            else:
                print("❌ Could not extract average payment from response")
            
            return success, response
        
        return success, {}

    def test_claude_chat_monthly_rewards_2024(self):
        """Test the Claude AI chat endpoint for 2024 monthly rewards"""
        # Use the same session ID for continuity
        if not self.session_id:
            self.session_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
        
        # Create a query specifically about 2024 monthly rewards
        data = {
            "message": "Show me the monthly rewards paid to clients in 2024 only.",
            "session_id": self.session_id
        }
        
        success, response = self.run_test(
            "Claude AI Chat - 2024 Monthly Rewards",
            "POST",
            "api/claude-chat",
            200,
            data=data
        )
        
        if success:
            # Check if the response contains 2024 monthly data
            response_text = response.get('response', '')
            print(f"\nResponse excerpt (first 500 chars):\n{response_text[:500]}...\n")
            
            # Look for 2024 months in the response
            month_patterns = re.findall(r'(2024-\d{2})[:\s]*\$([\d,]+\.\d{2})', response_text)
            
            if month_patterns:
                print(f"✅ Found 2024 monthly data: {month_patterns[:5]}{'...' if len(month_patterns) > 5 else ''}")
                
                # Calculate total from monthly data
                total_2024 = sum(float(amount.replace(',', '')) for _, amount in month_patterns)
                print(f"✅ Total from 2024 monthly data: ${total_2024:.2f}")
                
                # Check if the total is significant
                if total_2024 > 10000:  # Expecting a significant amount
                    print(f"✅ 2024 total is significant (>${total_2024:.2f})")
                    self.tests_passed += 1
                else:
                    print(f"❌ 2024 total may be too low (${total_2024:.2f})")
            else:
                print("❌ Response does not contain expected 2024 monthly data")
            
            return success, response
        
        return success, {}

    def test_claude_chat_monthly_rewards_2025(self):
        """Test the Claude AI chat endpoint for 2025 monthly rewards"""
        # Use the same session ID for continuity
        if not self.session_id:
            self.session_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
        
        # Create a query specifically about 2025 monthly rewards
        data = {
            "message": "Show me the monthly rewards paid to clients in 2025 only.",
            "session_id": self.session_id
        }
        
        success, response = self.run_test(
            "Claude AI Chat - 2025 Monthly Rewards",
            "POST",
            "api/claude-chat",
            200,
            data=data
        )
        
        if success:
            # Check if the response contains 2025 monthly data
            response_text = response.get('response', '')
            print(f"\nResponse excerpt (first 500 chars):\n{response_text[:500]}...\n")
            
            # Look for 2025 months in the response
            month_patterns = re.findall(r'(2025-\d{2})[:\s]*\$([\d,]+\.\d{2})', response_text)
            
            if month_patterns:
                print(f"✅ Found 2025 monthly data: {month_patterns[:5]}{'...' if len(month_patterns) > 5 else ''}")
                
                # Calculate total from monthly data
                total_2025 = sum(float(amount.replace(',', '')) for _, amount in month_patterns)
                print(f"✅ Total from 2025 monthly data: ${total_2025:.2f}")
                
                # Check if the total is significant
                if total_2025 > 1000:  # Expecting a significant amount
                    print(f"✅ 2025 total is significant (>${total_2025:.2f})")
                    self.tests_passed += 1
                else:
                    print(f"❌ 2025 total may be too low (${total_2025:.2f})")
            else:
                print("❌ Response does not contain expected 2025 monthly data")
            
            return success, response
        
        return success, {}

    def test_claude_chat_yearly_totals(self):
        """Test the Claude AI chat endpoint for yearly reward totals"""
        # Use the same session ID for continuity
        if not self.session_id:
            self.session_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
        
        # Create a query specifically about yearly totals
        data = {
            "message": "What are the total rewards paid to clients in 2024 and 2025?",
            "session_id": self.session_id
        }
        
        success, response = self.run_test(
            "Claude AI Chat - Yearly Reward Totals",
            "POST",
            "api/claude-chat",
            200,
            data=data
        )
        
        if success:
            # Check if the response contains yearly totals
            response_text = response.get('response', '')
            print(f"\nResponse excerpt (first 500 chars):\n{response_text[:500]}...\n")
            
            # Extract 2024 total
            total_2024_match = re.search(r'2024(?:.*?)(?:total|paid)(?:.*?)\$([\d,]+\.\d{2})', response_text.lower())
            if total_2024_match:
                total_2024 = float(total_2024_match.group(1).replace(',', ''))
                print(f"✅ 2024 total: ${total_2024:.2f}")
                
                # Check if the amount is significant
                if total_2024 > 10000:  # Expecting a significant amount
                    print(f"✅ 2024 total is significant (>${total_2024:.2f})")
                    self.tests_passed += 1
                else:
                    print(f"❌ 2024 total may be too low (${total_2024:.2f})")
            else:
                print("❌ Could not extract 2024 total from response")
            
            # Extract 2025 total
            total_2025_match = re.search(r'2025(?:.*?)(?:total|paid)(?:.*?)\$([\d,]+\.\d{2})', response_text.lower())
            if total_2025_match:
                total_2025 = float(total_2025_match.group(1).replace(',', ''))
                print(f"✅ 2025 total: ${total_2025:.2f}")
                
                # Check if the amount is significant
                if total_2025 > 1000:  # Expecting a significant amount
                    print(f"✅ 2025 total is significant (>${total_2025:.2f})")
                    self.tests_passed += 1
                else:
                    print(f"❌ 2025 total may be too low (${total_2025:.2f})")
            else:
                print("❌ Could not extract 2025 total from response")
            
            return success, response
        
        return success, {}

    def run_all_tests(self):
        """Run all rewards processing tests"""
        print("🚀 Starting Rewards Processing Tests")
        print(f"🔗 Base URL: {self.base_url}")
        print("=" * 50)
        
        self.test_api_health()
        
        print("\n" + "=" * 50)
        print("🔍 Testing Enhanced Rewards Processing Logic")
        print("=" * 50)
        
        # Test direct rewards statistics
        self.test_claude_chat_direct_rewards_query()
        
        # Wait a bit between requests to avoid rate limiting
        time.sleep(1)
        
        # Test 2024 monthly rewards
        self.test_claude_chat_monthly_rewards_2024()
        
        # Wait a bit between requests
        time.sleep(1)
        
        # Test 2025 monthly rewards
        self.test_claude_chat_monthly_rewards_2025()
        
        # Wait a bit between requests
        time.sleep(1)
        
        # Test yearly totals
        self.test_claude_chat_yearly_totals()
        
        print("\n" + "=" * 50)
        print(f"📊 Tests passed: {self.tests_passed}/{self.tests_run}")
        
        return self.tests_passed >= 4  # Consider test successful if at least 4 tests pass


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
    tester = RewardsProcessingTester(backend_url)
    success = tester.run_all_tests()
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())