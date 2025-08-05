#!/usr/bin/env python3

import requests
import json
import time
from datetime import datetime

def test_client_registration_email():
    """Test the client registration email (public registration form)"""
    print("🚨 TESTING CLIENT REGISTRATION EMAIL (PUBLIC FORM)")
    print("=" * 60)
    
    # Backend URL
    base_url = 'http://localhost:8001/api'
    
    # Test data for public registration (correct format)
    test_data = {
        "full_name": "TestClient EmailTest",
        "date_of_birth": "1990-01-01",
        "health_card_number": "1234567890",
        "phone_number": "416-555-0123",
        "email": "test@example.com",
        "consent_given": True
    }
    
    print(f"Sending registration to: {base_url}/register")
    print(f"Test data: {json.dumps(test_data, indent=2)}")
    
    try:
        response = requests.post(
            f"{base_url}/register",
            json=test_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"\nResponse Status: {response.status_code}")
        print(f"Response Body: {response.text}")
        
        if response.status_code == 200:
            print("\n✅ CLIENT REGISTRATION SUBMITTED SUCCESSFULLY")
            print("🚨 CHECK LOGS TO SEE WHAT EMAIL ADDRESS WAS USED")
            
            # Wait a moment for email to be sent
            time.sleep(3)
            
            # Check backend logs
            print("\n📋 CHECKING BACKEND LOGS...")
            import subprocess
            try:
                result = subprocess.run(
                    ['tail', '-n', '20', '/var/log/supervisor/backend.out.log'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                print("Backend logs:")
                print(result.stdout)
                
                result2 = subprocess.run(
                    ['tail', '-n', '20', '/var/log/supervisor/backend.err.log'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                print("Backend error logs:")
                print(result2.stdout)
                
            except Exception as e:
                print(f"Could not check logs: {e}")
                
        else:
            print(f"\n❌ REGISTRATION FAILED: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")

if __name__ == "__main__":
    test_client_registration_email()