#!/usr/bin/env python3
"""
Test without permissions field
"""

import requests
import json
import random

BACKEND_URL = "https://cd556dd9-d36b-422e-8110-4b1830397661.preview.emergentagent.com/api"

def test_without_permissions():
    """Test without permissions field"""
    unique_pin = str(random.randint(8000, 9999))
    print(f"🔍 Testing without permissions field, PIN: {unique_pin}")
    
    # No permissions field
    user_data = {
        "firstName": "Test",
        "lastName": "User", 
        "email": "test@example.com",
        "phone": "1234567890",
        "pin": unique_pin
    }
    
    try:
        print("Sending request...")
        response = requests.post(f"{BACKEND_URL}/users", json=user_data, timeout=15)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
    except Exception as e:
        print(f"❌ Exception: {str(e)}")

if __name__ == "__main__":
    test_without_permissions()