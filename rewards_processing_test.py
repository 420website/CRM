import requests
import json
import unittest
import sys
import os
from dotenv import load_dotenv
import random
import string
import time

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

    def test_claude_chat_rewards_query(self):
        """Test the Claude AI chat endpoint with a rewards-related query"""
        # Generate a unique session ID
        if not self.session_id:
            self.session_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
        
        # Create a rewards-related query
        data = {
            "message": "Show how much money the program gave clients for testing and compliance by month in 2024 and 2025 as well as comparison year over year.",
            "session_id": self.session_id
        }
        
        success, response = self.run_test(
            "Claude AI Chat - Rewards Query",
            "POST",
            "api/claude-chat",
            200,
            data=data
        )
        
        if success:
            # Check if the response contains rewards information
            response_text = response.get('response', '')
            print(f"\nResponse excerpt (first 500 chars):\n{response_text[:500]}...\n")
            
            # Check for key reward statistics in the response
            reward_indicators = [
                "total amount", "total paid", "payments", "monthly breakdown", 
                "2024", "2025", "year-over-year", "comparison"
            ]
            
            found_indicators = [indicator for indicator in reward_indicators if indicator.lower() in response_text.lower()]
            
            if found_indicators:
                print(f"✅ Found reward statistics indicators in response: {', '.join(found_indicators)}")
                self.tests_passed += 1
            else:
                print("❌ Response does not contain expected reward statistics")
                
            # Check for dollar amounts in the response
            import re
            dollar_amounts = re.findall(r'\$[\d,]+\.\d{2}', response_text)
            
            if dollar_amounts:
                print(f"✅ Found dollar amounts in response: {', '.join(dollar_amounts[:5])}{'...' if len(dollar_amounts) > 5 else ''}")
                
                # Try to extract the total amount
                total_amount_patterns = [
                    r'total amount paid:?\s*\$([\d,]+\.\d{2})',
                    r'total:?\s*\$([\d,]+\.\d{2})',
                    r'total payments:?\s*\$([\d,]+\.\d{2})'
                ]
                
                total_amount = None
                for pattern in total_amount_patterns:
                    matches = re.search(pattern, response_text.lower())
                    if matches:
                        total_amount = matches.group(1)
                        total_amount = float(total_amount.replace(',', ''))
                        break
                
                if total_amount:
                    print(f"✅ Total amount paid: ${total_amount:.2f}")
                    
                    # Check if the amount is significant (arbitrary threshold for testing)
                    if total_amount > 1000:
                        print(f"✅ Total amount is significant (>${total_amount:.2f})")
                        self.tests_passed += 1
                    else:
                        print(f"❌ Total amount may be too low (${total_amount:.2f})")
                else:
                    print("❌ Could not extract total amount from response")
            else:
                print("❌ Response does not contain dollar amounts")
            
            return success, response
        
        return success, {}

    def test_claude_chat_rewards_monthly_breakdown(self):
        """Test the Claude AI chat endpoint for monthly rewards breakdown"""
        # Use the same session ID for continuity
        if not self.session_id:
            self.session_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
        
        # Create a query specifically about monthly breakdown
        data = {
            "message": "Show me the monthly breakdown of rewards paid to clients in 2024 and 2025.",
            "session_id": self.session_id
        }
        
        success, response = self.run_test(
            "Claude AI Chat - Monthly Rewards Breakdown",
            "POST",
            "api/claude-chat",
            200,
            data=data
        )
        
        if success:
            # Check if the response contains monthly breakdown
            response_text = response.get('response', '')
            print(f"\nResponse excerpt (first 500 chars):\n{response_text[:500]}...\n")
            
            # Check for monthly data in the response
            months = ["January", "February", "March", "April", "May", "June", 
                     "July", "August", "September", "October", "November", "December"]
            
            found_months = [month for month in months if month.lower() in response_text.lower()]
            
            if found_months:
                print(f"✅ Found monthly data in response: {', '.join(found_months)}")
                self.tests_passed += 1
            else:
                # Check for YYYY-MM format
                import re
                month_patterns = re.findall(r'(202[45]-\d{2})', response_text)
                
                if month_patterns:
                    print(f"✅ Found monthly data in YYYY-MM format: {', '.join(month_patterns[:5])}{'...' if len(month_patterns) > 5 else ''}")
                    self.tests_passed += 1
                else:
                    print("❌ Response does not contain expected monthly breakdown")
            
            return success, response
        
        return success, {}

    def test_claude_chat_rewards_yearly_comparison(self):
        """Test the Claude AI chat endpoint for yearly rewards comparison"""
        # Use the same session ID for continuity
        if not self.session_id:
            self.session_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
        
        # Create a query specifically about yearly comparison
        data = {
            "message": "Compare the total rewards paid to clients in 2024 versus 2025. What is the percentage change?",
            "session_id": self.session_id
        }
        
        success, response = self.run_test(
            "Claude AI Chat - Yearly Rewards Comparison",
            "POST",
            "api/claude-chat",
            200,
            data=data
        )
        
        if success:
            # Check if the response contains yearly comparison
            response_text = response.get('response', '')
            print(f"\nResponse excerpt (first 500 chars):\n{response_text[:500]}...\n")
            
            # Check for yearly comparison indicators
            comparison_indicators = [
                "2024", "2025", "increase", "decrease", "change", "percent", "%", 
                "year-over-year", "comparison", "difference"
            ]
            
            found_indicators = [indicator for indicator in comparison_indicators if indicator.lower() in response_text.lower()]
            
            if found_indicators:
                print(f"✅ Found yearly comparison indicators in response: {', '.join(found_indicators)}")
                self.tests_passed += 1
            else:
                print("❌ Response does not contain expected yearly comparison")
            
            # Try to extract the percentage change
            import re
            percentage_patterns = [
                r'(increased|decreased) by (\d+\.?\d*)%',
                r'(\d+\.?\d*)% (increase|decrease)',
                r'change of (\d+\.?\d*)%'
            ]
            
            percentage_change = None
            for pattern in percentage_patterns:
                matches = re.search(pattern, response_text.lower())
                if matches:
                    if len(matches.groups()) == 2:
                        if 'decrease' in matches.group(1).lower():
                            percentage_change = -float(matches.group(2))
                        else:
                            percentage_change = float(matches.group(2))
                    else:
                        percentage_change = float(matches.group(1))
                        if 'decrease' in matches.group(2).lower():
                            percentage_change = -percentage_change
                    break
            
            if percentage_change is not None:
                print(f"✅ Year-over-year percentage change: {percentage_change}%")
                self.tests_passed += 1
            else:
                print("❌ Could not extract percentage change from response")
            
            return success, response
        
        return success, {}

    def test_claude_chat_rewards_average_payment(self):
        """Test the Claude AI chat endpoint for average payment calculation"""
        # Use the same session ID for continuity
        if not self.session_id:
            self.session_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
        
        # Create a query specifically about average payment
        data = {
            "message": "What is the average payment amount per client record?",
            "session_id": self.session_id
        }
        
        success, response = self.run_test(
            "Claude AI Chat - Average Payment Calculation",
            "POST",
            "api/claude-chat",
            200,
            data=data
        )
        
        if success:
            # Check if the response contains average payment information
            response_text = response.get('response', '')
            print(f"\nResponse excerpt (first 500 chars):\n{response_text[:500]}...\n")
            
            # Check for average payment indicators
            average_indicators = [
                "average", "mean", "per record", "per client", "payment"
            ]
            
            found_indicators = [indicator for indicator in average_indicators if indicator.lower() in response_text.lower()]
            
            if found_indicators:
                print(f"✅ Found average payment indicators in response: {', '.join(found_indicators)}")
                self.tests_passed += 1
            else:
                print("❌ Response does not contain expected average payment information")
            
            # Try to extract the average payment amount
            import re
            average_patterns = [
                r'average (?:payment|amount)(?:.*?)is \$([\d,]+\.\d{2})',
                r'average (?:payment|amount)(?:.*?)\$([\d,]+\.\d{2})',
                r'average of \$([\d,]+\.\d{2})'
            ]
            
            average_amount = None
            for pattern in average_patterns:
                matches = re.search(pattern, response_text.lower())
                if matches:
                    average_amount = matches.group(1)
                    average_amount = float(average_amount.replace(',', ''))
                    break
            
            if average_amount:
                print(f"✅ Average payment amount: ${average_amount:.2f}")
                self.tests_passed += 1
            else:
                print("❌ Could not extract average payment amount from response")
            
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
        
        # Test rewards query
        self.test_claude_chat_rewards_query()
        
        # Wait a bit between requests to avoid rate limiting
        time.sleep(1)
        
        # Test monthly breakdown
        self.test_claude_chat_rewards_monthly_breakdown()
        
        # Wait a bit between requests
        time.sleep(1)
        
        # Test yearly comparison
        self.test_claude_chat_rewards_yearly_comparison()
        
        # Wait a bit between requests
        time.sleep(1)
        
        # Test average payment calculation
        self.test_claude_chat_rewards_average_payment()
        
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
    tester = RewardsProcessingTester(backend_url)
    success = tester.run_all_tests()
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())