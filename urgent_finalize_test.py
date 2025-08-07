#!/usr/bin/env python3
"""
URGENT EMAIL TEST - Direct Backend Testing
Testing admin registration finalization email functionality
"""

import requests
import json
import os
from datetime import date
import time

# Get the backend URL from environment
BACKEND_URL = "https://cd556dd9-d36b-422e-8110-4b1830397661.preview.emergentagent.com/api"

def test_admin_registration_finalization_email():
    """Test admin registration creation and finalization to check email address"""
    
    print("🚨 URGENT EMAIL TEST - Admin Registration Finalization")
    print("=" * 60)
    
    try:
        # Step 1: Create a new admin registration with name "URGENT TEST"
        print("\n1. Creating new admin registration with name 'URGENT TEST'...")
        
        registration_data = {
            "firstName": "URGENT",
            "lastName": "TEST",
            "patientConsent": "verbal",
            "regDate": str(date.today()),
            "province": "Ontario",
            "email": "test@example.com"
        }
        
        # Try with proper headers
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        response = requests.post(f"{BACKEND_URL}/admin-register", 
                               json=registration_data, 
                               headers=headers,
                               timeout=30)
        
        print(f"Response status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        if response.status_code == 201:
            registration = response.json()
            registration_id = registration.get('registration_id')
            print(f"✅ Registration created successfully!")
            print(f"   Registration ID: {registration_id}")
            print(f"   Name: {registration.get('firstName')} {registration.get('lastName')}")
            
            # Step 2: Finalize the registration immediately to trigger email
            print(f"\n2. Finalizing registration {registration_id} to trigger email...")
            
            finalize_response = requests.post(f"{BACKEND_URL}/admin-registration/{registration_id}/finalize",
                                            headers=headers,
                                            timeout=30)
            
            print(f"Finalize response status: {finalize_response.status_code}")
            
            if finalize_response.status_code == 200:
                finalize_result = finalize_response.json()
                print(f"✅ Registration finalized successfully!")
                print(f"   Status: {finalize_result.get('status')}")
                print(f"   Message: {finalize_result.get('message')}")
                print(f"   Email sent: {finalize_result.get('email_sent')}")
                
                if finalize_result.get('email_error'):
                    print(f"   Email error: {finalize_result.get('email_error')}")
                
                # Wait a moment for logs to be written
                time.sleep(2)
                
                # Step 3: Check backend logs for email information
                print(f"\n3. Checking backend logs for email address information...")
                
                try:
                    import subprocess
                    result = subprocess.run(['tail', '-n', '100', '/var/log/supervisor/backend.err.log'], 
                                          capture_output=True, text=True, timeout=10)
                    if result.stdout:
                        print("📋 Recent backend error logs (looking for email info):")
                        print("-" * 50)
                        lines = result.stdout.split('\n')
                        for line in lines[-30:]:  # Last 30 lines
                            if line.strip() and ('email' in line.lower() or 'finalize' in line.lower() or '🚨' in line):
                                print(f"   {line}")
                        print("-" * 50)
                except Exception as e:
                    print(f"⚠️  Could not access supervisor error logs: {e}")
                
                return True
                
            else:
                print(f"❌ Failed to finalize registration: {finalize_response.status_code}")
                print(f"   Response: {finalize_response.text}")
                return False
                
        else:
            print(f"❌ Failed to create registration: {response.status_code}")
            print(f"   Response: {response.text}")
            
            # Check if it's a network issue
            if response.status_code == 502:
                print("🔍 502 Bad Gateway - checking backend service...")
                try:
                    health_response = requests.get(f"{BACKEND_URL}/health", timeout=10)
                    print(f"Health check status: {health_response.status_code}")
                except Exception as e:
                    print(f"Health check failed: {e}")
            
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ URGENT TEST FAILED: {str(e)}")
        return False

def check_backend_service():
    """Check if backend service is running properly"""
    print("\n🔧 BACKEND SERVICE CHECK")
    print("=" * 40)
    
    try:
        # Check supervisor status
        import subprocess
        result = subprocess.run(['sudo', 'supervisorctl', 'status', 'backend'], 
                              capture_output=True, text=True, timeout=10)
        print(f"Backend service status: {result.stdout.strip()}")
        
        # Check if backend is responding locally
        try:
            local_response = requests.get("http://localhost:8001/api/health", timeout=5)
            print(f"Local backend health: {local_response.status_code}")
        except Exception as e:
            print(f"Local backend not responding: {e}")
            
        # Check external URL
        try:
            external_response = requests.get(f"{BACKEND_URL}/health", timeout=10)
            print(f"External backend health: {external_response.status_code}")
        except Exception as e:
            print(f"External backend not responding: {e}")
            
    except Exception as e:
        print(f"Service check failed: {e}")

if __name__ == "__main__":
    print("🚨 URGENT: Testing Admin Registration Finalization Email")
    print("User reports emails still going to support@my420.ca instead of 420pharmacyprogram@gmail.com")
    print()
    
    # Check backend service first
    check_backend_service()
    
    # Test the functionality
    success = test_admin_registration_finalization_email()
    
    if success:
        print("\n✅ URGENT TEST COMPLETED")
        print("📧 Check the log output above to see what email address was used")
        print("🔍 Look for any references to support@my420.ca vs 420pharmacyprogram@gmail.com")
    else:
        print("\n❌ URGENT TEST FAILED")
        print("🚨 Unable to complete email testing - check backend status")
        
    print("\n📋 SUMMARY:")
    print("- Environment SUPPORT_EMAIL is set to: 420pharmacyprogram@gmail.com")
    print("- Check the logs above for actual email sending behavior")
    print("- If logs show 420pharmacyprogram@gmail.com, the fix is working")
    print("- If logs show support@my420.ca, there's still an issue")