import requests
import json
import os
import sys
from dotenv import load_dotenv

def test_claude_chat_housing_query():
    """Test the Claude chat endpoint with housing query"""
    # Load the frontend .env file to get the backend URL
    load_dotenv('/app/frontend/.env')
    backend_url = os.environ.get('REACT_APP_BACKEND_URL')
    
    if not backend_url:
        print("❌ Error: REACT_APP_BACKEND_URL not found in frontend .env file")
        return False
    
    print(f"🔗 Using backend URL from .env: {backend_url}")
    
    # Housing query
    housing_query = "What percentage of clients have an address listed?"
    
    # Prepare request data
    data = {
        "message": housing_query,
        "session_id": None  # No session ID for first request
    }
    
    # Make request to Claude chat endpoint
    try:
        print(f"🔍 Testing Claude Chat - Housing Query...")
        response = requests.post(
            f"{backend_url}/api/claude-chat",
            json=data,
            headers={'Content-Type': 'application/json'}
        )
        
        # Check response status code
        if response.status_code == 200:
            print(f"✅ Passed - Status: {response.status_code}")
            
            # Parse response JSON
            response_data = response.json()
            
            # Store session ID for future queries
            session_id = response_data.get('session_id')
            
            # Check if the response contains address/housing information
            response_text = response_data.get('response', '')
            
            # Print response excerpt
            print(f"✅ Response excerpt: {response_text[:200]}...")
            
            # Check for key terms related to housing/address statistics
            housing_terms = ['address', 'housing', 'percentage', 'clients', 'listed']
            found_terms = [term for term in housing_terms if term.lower() in response_text.lower()]
            
            if found_terms:
                print(f"✅ Response contains housing/address information. Found terms: {', '.join(found_terms)}")
                
                # Check if the response contains a percentage
                import re
                percentage_pattern = r'\d+(\.\d+)?%'
                percentages = re.findall(percentage_pattern, response_text)
                
                if percentages:
                    print(f"✅ Response contains percentage values: {percentages}")
                    return True
                else:
                    print("❌ Response does not contain any percentage values")
                    return False
            else:
                print("❌ Response does not contain housing/address information")
                return False
        else:
            print(f"❌ Failed - Status: {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error: {error_data}")
            except:
                print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Failed - Error: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_claude_chat_housing_query()
    sys.exit(0 if success else 1)