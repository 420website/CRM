import requests
import unittest
import json
import os
import sys
from dotenv import load_dotenv
import uuid

class ClaudeChatTester:
    def __init__(self, base_url):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.session_id = str(uuid.uuid4())  # Generate a session ID for testing

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

    def test_claude_chat_basic(self):
        """Test basic Claude chat functionality with a simple greeting"""
        data = {
            "message": "Hello, what can you help me with?",
            "session_id": self.session_id
        }
        
        success, response = self.run_test(
            "Claude Chat - Basic Greeting",
            "POST",
            "api/claude-chat",
            200,
            data=data
        )
        
        if success:
            # Verify response structure
            if 'response' in response and 'session_id' in response:
                print(f"✅ Response structure correct")
                print(f"✅ Session ID: {response['session_id']}")
                print(f"✅ Response preview: {response['response'][:100]}...")
                
                # Verify response content is meaningful (not empty or error message)
                if len(response['response']) > 50:
                    print(f"✅ Response length good: {len(response['response'])} characters")
                else:
                    print(f"⚠️ Response seems short: {len(response['response'])} characters")
                    
                # Verify session ID is preserved
                if response['session_id'] == self.session_id:
                    print(f"✅ Session ID preserved correctly")
                else:
                    print(f"❌ Session ID changed: {self.session_id} -> {response['session_id']}")
                    success = False
            else:
                print(f"❌ Response missing required fields")
                success = False
                
        return success, response

    def test_claude_chat_medical(self):
        """Test Claude chat with a medical/analytics query about Hepatitis C"""
        data = {
            "message": "Can you explain Hepatitis C testing trends?",
            "session_id": self.session_id
        }
        
        success, response = self.run_test(
            "Claude Chat - Medical Query",
            "POST",
            "api/claude-chat",
            200,
            data=data
        )
        
        if success:
            # Verify response contains medical terminology related to Hepatitis C
            medical_terms = ['hepatitis', 'hcv', 'testing', 'screening', 'antibody', 'virus', 'treatment']
            found_terms = []
            
            response_lower = response['response'].lower()
            for term in medical_terms:
                if term in response_lower:
                    found_terms.append(term)
            
            if found_terms:
                print(f"✅ Response contains medical terminology: {', '.join(found_terms)}")
            else:
                print(f"⚠️ Response doesn't contain expected medical terminology")
                
            # Check for analytics-related content
            analytics_terms = ['trend', 'data', 'increase', 'decrease', 'statistics', 'rate', 'percentage']
            found_analytics = []
            
            for term in analytics_terms:
                if term in response_lower:
                    found_analytics.append(term)
            
            if found_analytics:
                print(f"✅ Response contains analytics terminology: {', '.join(found_analytics)}")
            else:
                print(f"⚠️ Response doesn't contain expected analytics terminology")
                
        return success, response

    def test_claude_chat_analytics(self):
        """Test Claude chat with a data analytics query"""
        data = {
            "message": "How can I analyze registration data?",
            "session_id": self.session_id
        }
        
        success, response = self.run_test(
            "Claude Chat - Analytics Query",
            "POST",
            "api/claude-chat",
            200,
            data=data
        )
        
        if success:
            # Verify response contains analytics terminology
            analytics_terms = ['data', 'analysis', 'trend', 'pattern', 'visualization', 'dashboard', 'report', 'metric']
            found_terms = []
            
            response_lower = response['response'].lower()
            for term in analytics_terms:
                if term in response_lower:
                    found_terms.append(term)
            
            if found_terms:
                print(f"✅ Response contains analytics terminology: {', '.join(found_terms)}")
            else:
                print(f"⚠️ Response doesn't contain expected analytics terminology")
                
        return success, response

    def test_claude_chat_session_continuity(self):
        """Test that Claude chat maintains context across multiple messages in a session"""
        # First message to establish context
        data1 = {
            "message": "Tell me about Hepatitis C testing.",
            "session_id": self.session_id
        }
        
        success1, response1 = self.run_test(
            "Claude Chat - Session Message 1",
            "POST",
            "api/claude-chat",
            200,
            data=data1
        )
        
        if not success1:
            return False, {}
            
        # Follow-up message that relies on previous context
        data2 = {
            "message": "What are the latest trends in this area?",
            "session_id": self.session_id
        }
        
        success2, response2 = self.run_test(
            "Claude Chat - Session Message 2 (Follow-up)",
            "POST",
            "api/claude-chat",
            200,
            data=data2
        )
        
        if success2:
            # Check if the response references Hepatitis C without it being mentioned in the second message
            hep_c_terms = ['hepatitis c', 'hcv', 'hepatitis', 'liver disease']
            found_terms = []
            
            response_lower = response2['response'].lower()
            for term in hep_c_terms:
                if term in response_lower:
                    found_terms.append(term)
            
            if found_terms:
                print(f"✅ Session continuity verified - response references: {', '.join(found_terms)}")
            else:
                print(f"⚠️ Session continuity unclear - response doesn't explicitly reference Hepatitis C")
                
        return success2, response2

    def test_claude_chat_error_handling(self):
        """Test Claude chat error handling with invalid requests"""
        # Test with empty message
        data = {
            "message": "",
            "session_id": self.session_id
        }
        
        success, response = self.run_test(
            "Claude Chat - Empty Message",
            "POST",
            "api/claude-chat",
            422,  # Expecting validation error
            data=data
        )
        
        # Test with missing message field
        data = {
            "session_id": self.session_id
        }
        
        success, response = self.run_test(
            "Claude Chat - Missing Message Field",
            "POST",
            "api/claude-chat",
            422,  # Expecting validation error
            data=data
        )
        
        return success, response

    def run_all_tests(self):
        """Run all Claude chat API tests"""
        print("🚀 Starting Claude Chat API Tests")
        print(f"🔗 Base URL: {self.base_url}")
        print("=" * 50)
        
        # First verify API health
        self.test_api_health()
        
        # Run Claude chat tests
        print("\n" + "=" * 50)
        print("🔍 Testing Claude Chat Functionality")
        print("=" * 50)
        
        self.test_claude_chat_basic()
        self.test_claude_chat_medical()
        self.test_claude_chat_analytics()
        self.test_claude_chat_session_continuity()
        self.test_claude_chat_error_handling()
        
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
    tester = ClaudeChatTester(backend_url)
    success = tester.run_all_tests()
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())