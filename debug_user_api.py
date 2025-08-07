#!/usr/bin/env python3
"""
Debug User Management API - Check MongoDB ObjectId issue
"""

import requests
import json

BACKEND_URL = "https://cd556dd9-d36b-422e-8110-4b1830397661.preview.emergentagent.com/api"

def debug_user_creation():
    """Debug user creation with minimal data"""
    print("🔍 DEBUG: User Creation with minimal data")
    
    user_data = {
        "firstName": "Test",
        "lastName": "User", 
        "email": "test@example.com",
        "phone": "1234567890",
        "pin": "1111",
        "permissions": {}
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/users", json=user_data, timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 500:
            print("❌ 500 Internal Server Error - likely MongoDB ObjectId serialization issue")
        
    except Exception as e:
        print(f"❌ Request failed: {str(e)}")

if __name__ == "__main__":
    debug_user_creation()