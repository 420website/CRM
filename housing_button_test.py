import requests
import unittest
import json
import os
from dotenv import load_dotenv
import sys

class HousingButtonTester:
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

    def test_claude_chat_housing_query(self):
        """Test the Claude chat endpoint with housing query"""
        housing_query = "What percentage of clients have an address listed?"
        
        data = {
            "message": housing_query,
            "session_id": self.session_id
        }
        
        success, response = self.run_test(
            "Claude Chat - Housing Query",
            "POST",
            "api/claude-chat",
            200,
            data=data
        )
        
        if success:
            # Store session ID for future queries
            self.session_id = response.get('session_id')
            
            # Check if the response contains address/housing information
            response_text = response.get('response', '')
            
            # Check for key terms related to housing/address statistics
            housing_terms = ['address', 'housing', 'percentage', 'clients', 'listed']
            found_terms = [term for term in housing_terms if term.lower() in response_text.lower()]
            
            if found_terms:
                print(f"✅ Response contains housing/address information. Found terms: {', '.join(found_terms)}")
                print(f"✅ Response excerpt: {response_text[:200]}...")
                
                # Check if the response contains a percentage
                import re
                percentage_pattern = r'\d+(\.\d+)?%'
                percentages = re.findall(percentage_pattern, response_text)
                
                if percentages:
                    print(f"✅ Response contains percentage values: {percentages}")
                else:
                    print("❌ Response does not contain any percentage values")
                    success = False
            else:
                print("❌ Response does not contain housing/address information")
                print(f"Response: {response_text[:200]}...")
                success = False
        
        return success, response

    def test_address_identification(self):
        """Test that the system correctly identifies clients with no address"""
        # This test sends a follow-up query to check if the system correctly identifies
        # empty values, null, 'no address', 'no fixed address', 'nfa', 'homeless' as no address
        
        if not self.session_id:
            # First run the housing query to get a session ID
            self.test_claude_chat_housing_query()
        
        follow_up_query = "What criteria do you use to determine if a client has no address?"
        
        data = {
            "message": follow_up_query,
            "session_id": self.session_id
        }
        
        success, response = self.run_test(
            "Claude Chat - Address Identification Criteria",
            "POST",
            "api/claude-chat",
            200,
            data=data
        )
        
        if success:
            response_text = response.get('response', '')
            
            # Check for key terms related to address identification criteria
            criteria_terms = ['empty', 'null', 'no address', 'no fixed address', 'nfa', 'homeless']
            found_criteria = [term for term in criteria_terms if term.lower() in response_text.lower()]
            
            if found_criteria:
                print(f"✅ Response mentions address identification criteria: {', '.join(found_criteria)}")
                print(f"✅ Response excerpt: {response_text[:200]}...")
            else:
                print("❌ Response does not mention address identification criteria")
                print(f"Response: {response_text[:200]}...")
                success = False
        
        return success, response

    def test_percentage_calculation(self):
        """Test the accuracy of percentage calculations for clients with addresses"""
        # This test sends a query to check the percentage calculation
        
        if not self.session_id:
            # First run the housing query to get a session ID
            self.test_claude_chat_housing_query()
        
        calculation_query = "Can you explain how the percentage of clients with addresses is calculated?"
        
        data = {
            "message": calculation_query,
            "session_id": self.session_id
        }
        
        success, response = self.run_test(
            "Claude Chat - Percentage Calculation",
            "POST",
            "api/claude-chat",
            200,
            data=data
        )
        
        if success:
            response_text = response.get('response', '')
            
            # Check for key terms related to percentage calculation
            calculation_terms = ['total records', 'valid address', 'percentage', 'calculation', 'divide']
            found_terms = [term for term in calculation_terms if term.lower() in response_text.lower()]
            
            if found_terms:
                print(f"✅ Response explains percentage calculation. Found terms: {', '.join(found_terms)}")
                print(f"✅ Response excerpt: {response_text[:200]}...")
            else:
                print("❌ Response does not explain percentage calculation")
                print(f"Response: {response_text[:200]}...")
                success = False
        
        return success, response

    def test_ai_context_inclusion(self):
        """Test that address statistics are included in the AI context"""
        # This test sends a query to check if address statistics are included in the context
        
        if not self.session_id:
            # First run the housing query to get a session ID
            self.test_claude_chat_housing_query()
        
        context_query = "What address statistics do you have access to in your context?"
        
        data = {
            "message": context_query,
            "session_id": self.session_id
        }
        
        success, response = self.run_test(
            "Claude Chat - AI Context Inclusion",
            "POST",
            "api/claude-chat",
            200,
            data=data
        )
        
        if success:
            response_text = response.get('response', '')
            
            # Check for key terms related to address statistics in context
            context_terms = ['total records', 'no address', 'valid address', 'percentage']
            found_terms = [term for term in context_terms if term.lower() in response_text.lower()]
            
            if found_terms:
                print(f"✅ Response confirms address statistics in context. Found terms: {', '.join(found_terms)}")
                print(f"✅ Response excerpt: {response_text[:200]}...")
            else:
                print("❌ Response does not confirm address statistics in context")
                print(f"Response: {response_text[:200]}...")
                success = False
        
        return success, response

    def run_all_tests(self):
        """Run all Housing button tests"""
        print("🚀 Starting Housing Button Tests for my420.ca")
        print(f"🔗 Base URL: {self.base_url}")
        print("=" * 50)
        
        self.test_api_health()
        
        print("\n" + "=" * 50)
        print("🔍 Testing Housing Button Functionality")
        print("=" * 50)
        
        self.test_claude_chat_housing_query()
        self.test_address_identification()
        self.test_percentage_calculation()
        self.test_ai_context_inclusion()
        
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
    tester = HousingButtonTester(backend_url)
    success = tester.run_all_tests()
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())