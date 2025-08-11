#!/usr/bin/env python3
"""
Test a simple endpoint to isolate the issue
"""

import requests
import json

BACKEND_URL = "https://258401ff-ff29-421c-8498-4969ee7788f0.preview.emergentagent.com/api"

def test_simple_endpoint():
    """Test a simple endpoint that should work"""
    try:
        # Test a known working endpoint
        response = requests.get(f"{BACKEND_URL}/dispositions", timeout=10)
        print(f"Dispositions endpoint status: {response.status_code}")
        
        # Test another endpoint
        response = requests.get(f"{BACKEND_URL}/clinical-templates", timeout=10)
        print(f"Clinical templates endpoint status: {response.status_code}")
        
        # Test the users GET endpoint again
        response = requests.get(f"{BACKEND_URL}/users", timeout=10)
        print(f"Users GET endpoint status: {response.status_code}")
        
    except Exception as e:
        print(f"❌ Exception: {str(e)}")

if __name__ == "__main__":
    test_simple_endpoint()