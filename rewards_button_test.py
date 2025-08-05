import requests
import unittest
import json
import os
from dotenv import load_dotenv
import sys

class RewardsButtonTester:
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

    def test_claude_chat_rewards_query(self):
        """Test the Claude chat endpoint with a rewards-related query"""
        rewards_query = "Show how much money the program gave clients for testing and compliance by month in 2024 and 2025 as well as comparison year over year."
        
        data = {
            "message": rewards_query,
            "session_id": self.session_id
        }
        
        success, response = self.run_test(
            "Claude Chat - Rewards Query",
            "POST",
            "api/claude-chat",
            200,
            data=data
        )
        
        if success:
            # Save the session ID for future queries
            self.session_id = response.get('session_id')
            
            # Check if the response contains rewards-related information
            response_text = response.get('response', '')
            
            # Check for key terms that should be in the response
            rewards_terms = ['money', 'paid', 'clients', 'testing', 'compliance', 'month', '2024', '2025', 'year over year']
            found_terms = [term for term in rewards_terms if term.lower() in response_text.lower()]
            
            if found_terms:
                print(f"✅ Response contains rewards-related terms: {', '.join(found_terms)}")
                
                # Check if the response contains monthly breakdown
                if 'monthly' in response_text.lower() or 'month' in response_text.lower():
                    print("✅ Response includes monthly breakdown")
                else:
                    print("❌ Response does not include monthly breakdown")
                    success = False
                
                # Check if the response contains yearly totals
                if 'total' in response_text.lower() or 'year' in response_text.lower():
                    print("✅ Response includes yearly totals")
                else:
                    print("❌ Response does not include yearly totals")
                    success = False
                
                # Check if the response contains year-over-year comparison
                if 'comparison' in response_text.lower() or 'change' in response_text.lower() or 'increase' in response_text.lower() or 'decrease' in response_text.lower():
                    print("✅ Response includes year-over-year comparison")
                else:
                    print("❌ Response does not include year-over-year comparison")
                    success = False
                
                # Print a sample of the response for verification
                print("\nSample of response:")
                print(response_text[:500] + "..." if len(response_text) > 500 else response_text)
            else:
                print("❌ Response does not contain rewards-related information")
                print("\nResponse:")
                print(response_text[:500] + "..." if len(response_text) > 500 else response_text)
                success = False
        
        return success, response

    def test_claude_chat_rewards_monthly_breakdown(self):
        """Test the Claude chat endpoint with a specific query about monthly rewards breakdown"""
        monthly_query = "What was the monthly breakdown of client rewards in 2024?"
        
        data = {
            "message": monthly_query,
            "session_id": self.session_id
        }
        
        success, response = self.run_test(
            "Claude Chat - Monthly Rewards Breakdown",
            "POST",
            "api/claude-chat",
            200,
            data=data
        )
        
        if success:
            # Save the session ID for future queries
            self.session_id = response.get('session_id')
            
            # Check if the response contains monthly breakdown information
            response_text = response.get('response', '')
            
            # Check for months in the response
            months = ['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december']
            found_months = [month for month in months if month.lower() in response_text.lower()]
            
            if found_months or ('2024-' in response_text):
                print(f"✅ Response contains monthly breakdown information")
                print("\nSample of response:")
                print(response_text[:500] + "..." if len(response_text) > 500 else response_text)
            else:
                print("❌ Response does not contain monthly breakdown information")
                print("\nResponse:")
                print(response_text[:500] + "..." if len(response_text) > 500 else response_text)
                success = False
        
        return success, response

    def test_claude_chat_rewards_yearly_comparison(self):
        """Test the Claude chat endpoint with a specific query about yearly rewards comparison"""
        yearly_query = "Compare the total client rewards between 2024 and 2025"
        
        data = {
            "message": yearly_query,
            "session_id": self.session_id
        }
        
        success, response = self.run_test(
            "Claude Chat - Yearly Rewards Comparison",
            "POST",
            "api/claude-chat",
            200,
            data=data
        )
        
        if success:
            # Save the session ID for future queries
            self.session_id = response.get('session_id')
            
            # Check if the response contains yearly comparison information
            response_text = response.get('response', '')
            
            # Check for key terms that should be in the response
            comparison_terms = ['2024', '2025', 'total', 'comparison', 'increase', 'decrease', 'change', 'percent']
            found_terms = [term for term in comparison_terms if term.lower() in response_text.lower()]
            
            if found_terms and len(found_terms) >= 3:
                print(f"✅ Response contains yearly comparison information: {', '.join(found_terms)}")
                print("\nSample of response:")
                print(response_text[:500] + "..." if len(response_text) > 500 else response_text)
            else:
                print("❌ Response does not contain sufficient yearly comparison information")
                print("\nResponse:")
                print(response_text[:500] + "..." if len(response_text) > 500 else response_text)
                success = False
        
        return success, response

    def run_all_tests(self):
        """Run all Rewards button functionality tests"""
        print("🚀 Starting Rewards Button Functionality Tests")
        print(f"🔗 Base URL: {self.base_url}")
        print("=" * 50)
        
        # Test API health first
        self.test_api_health()
        
        # Test Claude chat with rewards-related queries
        print("\n" + "=" * 50)
        print("🔍 Testing Rewards Button Functionality")
        print("=" * 50)
        
        self.test_claude_chat_rewards_query()
        self.test_claude_chat_rewards_monthly_breakdown()
        self.test_claude_chat_rewards_yearly_comparison()
        
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
    tester = RewardsButtonTester(backend_url)
    success = tester.run_all_tests()
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())