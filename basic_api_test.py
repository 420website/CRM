import requests
import sys
from dotenv import load_dotenv
import os

def test_api_health(base_url):
    """Test the API health endpoint"""
    url = f"{base_url}/api"
    print(f"Testing API health at {url}...")
    try:
        response = requests.get(url)
        print(f"Status code: {response.status_code}")
        if response.status_code == 200:
            print("API health check passed!")
            try:
                print(f"Response: {response.json()}")
            except:
                print(f"Response: {response.text}")
            return True
        else:
            print("API health check failed!")
            try:
                print(f"Response: {response.json()}")
            except:
                print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

def test_claude_chat(base_url):
    """Test the Claude chat endpoint"""
    url = f"{base_url}/api/claude-chat"
    print(f"Testing Claude chat at {url}...")
    try:
        data = {
            "message": "Hello, how are you?",
            "session_id": "test-session-123"
        }
        response = requests.post(url, json=data)
        print(f"Status code: {response.status_code}")
        if response.status_code == 200:
            print("Claude chat test passed!")
            try:
                print(f"Response: {response.json()}")
            except:
                print(f"Response: {response.text}")
            return True
        else:
            print("Claude chat test failed!")
            try:
                print(f"Response: {response.json()}")
            except:
                print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

def main():
    # Get the backend URL from the frontend .env file
    load_dotenv('/app/frontend/.env')
    backend_url = os.environ.get('REACT_APP_BACKEND_URL')
    if not backend_url:
        print("Error: REACT_APP_BACKEND_URL not found in frontend .env file")
        return 1
    
    print(f"Using backend URL from .env: {backend_url}")
    
    # Test API health
    health_result = test_api_health(backend_url)
    
    # Test Claude chat
    claude_result = test_claude_chat(backend_url)
    
    return 0 if health_result and claude_result else 1

if __name__ == "__main__":
    sys.exit(main())