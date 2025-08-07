#!/usr/bin/env python3
"""
URGENT EMAIL TEST - Admin Registration Finalization Email Testing
Testing the email address used when finalizing admin registrations
"""

import requests
import json
import os
from datetime import date

# Get the backend URL from environment
BACKEND_URL = "https://cd556dd9-d36b-422e-8110-4b1830397661.preview.emergentagent.com/api"

def test_urgent_admin_registration_finalization():
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
            "email": "test@example.com"  # Test email to see where notification goes
        }
        
        response = requests.post(f"{BACKEND_URL}/admin-register", json=registration_data)
        
        if response.status_code == 201:
            registration = response.json()
            registration_id = registration.get('registration_id')
            print(f"✅ Registration created successfully!")
            print(f"   Registration ID: {registration_id}")
            print(f"   Name: {registration.get('firstName')} {registration.get('lastName')}")
        else:
            print(f"❌ Failed to create registration: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
        # Step 2: Finalize the registration immediately to trigger email
        print(f"\n2. Finalizing registration {registration_id} to trigger email...")
        
        finalize_response = requests.post(f"{BACKEND_URL}/admin-registration/{registration_id}/finalize")
        
        if finalize_response.status_code == 200:
            finalize_result = finalize_response.json()
            print(f"✅ Registration finalized successfully!")
            print(f"   Status: {finalize_result.get('status')}")
            print(f"   Message: {finalize_result.get('message')}")
            
            # Check if email information is in the response
            if 'email_sent_to' in finalize_result:
                print(f"📧 EMAIL SENT TO: {finalize_result['email_sent_to']}")
            
        else:
            print(f"❌ Failed to finalize registration: {finalize_response.status_code}")
            print(f"   Response: {finalize_response.text}")
            return False
            
        # Step 3: Check backend logs for email information
        print(f"\n3. Checking backend logs for email address information...")
        
        # Try to get supervisor logs
        try:
            import subprocess
            result = subprocess.run(['tail', '-n', '50', '/var/log/supervisor/backend.out.log'], 
                                  capture_output=True, text=True, timeout=10)
            if result.stdout:
                print("📋 Recent backend logs:")
                print("-" * 40)
                for line in result.stdout.split('\n')[-20:]:  # Last 20 lines
                    if line.strip() and ('email' in line.lower() or 'smtp' in line.lower() or 'finalize' in line.lower()):
                        print(f"   {line}")
                print("-" * 40)
        except Exception as e:
            print(f"⚠️  Could not access supervisor logs: {e}")
            
        # Step 4: Verify environment variables
        print(f"\n4. Checking email configuration...")
        
        # Check what email addresses are configured
        try:
            with open('/app/backend/.env', 'r') as f:
                env_content = f.read()
                print("📧 Email configuration from .env:")
                for line in env_content.split('\n'):
                    if 'EMAIL' in line or 'SMTP' in line:
                        print(f"   {line}")
        except Exception as e:
            print(f"⚠️  Could not read .env file: {e}")
            
        print(f"\n5. CRITICAL FINDINGS:")
        print("=" * 40)
        print("✅ Admin registration created and finalized successfully")
        print("📧 Check the logs above for the actual email address being used")
        print("🔍 Look for SMTP or email-related log entries")
        
        return True
        
    except Exception as e:
        print(f"❌ URGENT TEST FAILED: {str(e)}")
        return False

def check_email_configuration():
    """Check the current email configuration"""
    print("\n🔧 EMAIL CONFIGURATION CHECK")
    print("=" * 40)
    
    try:
        # Read backend environment file
        with open('/app/backend/.env', 'r') as f:
            content = f.read()
            
        print("Current email settings:")
        for line in content.split('\n'):
            if any(keyword in line for keyword in ['EMAIL', 'SMTP']):
                print(f"  {line}")
                
        # Check if SUPPORT_EMAIL is set correctly
        if 'SUPPORT_EMAIL="420pharmacyprogram@gmail.com"' in content:
            print("✅ SUPPORT_EMAIL is correctly set to 420pharmacyprogram@gmail.com")
        elif 'support@my420.ca' in content:
            print("❌ FOUND OLD EMAIL: support@my420.ca is still in configuration!")
        else:
            print("⚠️  SUPPORT_EMAIL configuration unclear")
            
    except Exception as e:
        print(f"❌ Could not check email configuration: {e}")

if __name__ == "__main__":
    print("🚨 URGENT: Testing Admin Registration Finalization Email")
    print("User reports emails still going to support@my420.ca instead of 420pharmacyprogram@gmail.com")
    print()
    
    # First check email configuration
    check_email_configuration()
    
    # Then test the actual functionality
    success = test_urgent_admin_registration_finalization()
    
    if success:
        print("\n✅ URGENT TEST COMPLETED")
        print("📧 Check the log output above to see what email address was used")
        print("🔍 Look for any references to support@my420.ca vs 420pharmacyprogram@gmail.com")
    else:
        print("\n❌ URGENT TEST FAILED")
        print("🚨 Unable to complete email testing - check backend status")