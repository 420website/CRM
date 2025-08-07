#!/usr/bin/env python3
"""
Test User Management API with unique PIN
"""

import requests
import json
import random

BACKEND_URL = "https://cd556dd9-d36b-422e-8110-4b1830397661.preview.emergentagent.com/api"

def test_with_unique_pin():
    """Test user creation with unique PIN"""
    unique_pin = str(random.randint(5000, 9999))
    print(f"🔍 Testing with unique PIN: {unique_pin}")
    
    user_data = {
        "firstName": "Test",
        "lastName": "User", 
        "email": "test@example.com",
        "phone": "1234567890",
        "pin": unique_pin,
        "permissions": {}
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/users", json=user_data, timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ User creation successful!")
            result = response.json()
            return result['user']['id']
        else:
            print("❌ User creation failed")
            return None
        
    except Exception as e:
        print(f"❌ Request failed: {str(e)}")
        return None

def test_get_users():
    """Test get all users"""
    print("\n🔍 Testing GET /api/users")
    
    try:
        response = requests.get(f"{BACKEND_URL}/users", timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Response length: {len(response.text)}")
        
        if response.status_code == 200:
            users = response.json()
            print(f"✅ Retrieved {len(users)} users")
            return True
        else:
            print("❌ Get users failed")
            return False
        
    except Exception as e:
        print(f"❌ Request failed: {str(e)}")
        return False

if __name__ == "__main__":
    user_id = test_with_unique_pin()
    test_get_users()