#!/usr/bin/env python3
"""
Minimal test to isolate the ObjectId issue
"""

import requests
import json
import random

BACKEND_URL = "https://dfe9a1e1-7f3d-45aa-ad71-43a254e568c5.preview.emergentagent.com/api"

def test_minimal_user():
    """Test with absolutely minimal user data"""
    unique_pin = str(random.randint(7000, 9999))
    print(f"🔍 Testing minimal user with PIN: {unique_pin}")
    
    # Minimal required data only
    user_data = {
        "firstName": "A",
        "lastName": "B", 
        "email": "a@b.com",
        "phone": "1111111111",
        "pin": unique_pin
    }
    
    try:
        print("Sending request...")
        response = requests.post(f"{BACKEND_URL}/users", json=user_data, timeout=15)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ SUCCESS!")
            result = response.json()
            print(f"User ID: {result.get('user', {}).get('id', 'N/A')}")
        else:
            print(f"❌ FAILED: {response.text}")
        
    except Exception as e:
        print(f"❌ Exception: {str(e)}")

if __name__ == "__main__":
    test_minimal_user()