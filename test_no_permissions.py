#!/usr/bin/env python3
"""
Test without permissions field
"""

import requests
import json
import random

BACKEND_URL = "https://dfe9a1e1-7f3d-45aa-ad71-43a254e568c5.preview.emergentagent.com/api"

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