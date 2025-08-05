#!/usr/bin/env python3
"""
Debug User Management API - Check MongoDB ObjectId issue
"""

import requests
import json

BACKEND_URL = "https://46471c8a-a981-4b23-bca9-bb5c0ba282bc.preview.emergentagent.com/api"

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