import requests
import sys

def test_api_health():
    """Test the API health endpoint"""
    url = "http://localhost:8001/api"
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

def test_claude_chat():
    """Test the Claude chat endpoint"""
    url = "http://localhost:8001/api/claude-chat"
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
    # Test API health
    health_result = test_api_health()
    
    # Test Claude chat
    claude_result = test_claude_chat()
    
    return 0 if health_result and claude_result else 1

if __name__ == "__main__":
    sys.exit(main())