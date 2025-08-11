#!/usr/bin/env python3
"""
Quick test to verify the timezone issue in TOTP verification
"""

import requests
import json
import time
import pyotp
from datetime import datetime
import pytz

# Configuration
BACKEND_URL = "https://258401ff-ff29-421c-8498-4969ee7788f0.preview.emergentagent.com/api"
DEFAULT_PIN = "0224"

def test_timezone_issue():
    print("🕐 TESTING TIMEZONE ISSUE IN TOTP VERIFICATION")
    print("=" * 50)
    
    # Show current time in different timezones
    utc_now = datetime.now()
    toronto_now = datetime.now(pytz.timezone('America/Toronto'))
    
    print(f"UTC time: {utc_now}")
    print(f"Toronto time: {toronto_now}")
    print(f"Time difference: {(toronto_now.replace(tzinfo=None) - utc_now).total_seconds()} seconds")
    
    # Test a simple 2FA flow
    print("\n1. Setting up 2FA...")
    
    # Get session
    pin_response = requests.post(f"{BACKEND_URL}/admin/pin-verify", 
                               json={"pin": DEFAULT_PIN}, timeout=30)
    session_token = pin_response.json().get('session_token')
    
    # Setup 2FA
    setup_response = requests.post(f"{BACKEND_URL}/admin/2fa/setup", timeout=30)
    totp_secret = setup_response.json().get('totp_secret')
    
    # Verify setup
    totp = pyotp.TOTP(totp_secret)
    setup_code = totp.now()
    
    verify_response = requests.post(f"{BACKEND_URL}/admin/2fa/verify-setup", 
                                  json={"totp_code": setup_code}, timeout=30)
    
    print(f"Setup result: {verify_response.status_code}")
    
    # Now test login verification with a fresh code after waiting
    print("\n2. Testing login verification...")
    
    # Wait for next TOTP window
    time.sleep(35)  # Wait more than 30 seconds
    
    fresh_code = totp.now()
    print(f"Fresh TOTP code: {fresh_code}")
    
    login_response = requests.post(f"{BACKEND_URL}/admin/2fa/verify", 
                                 json={
                                     "totp_code": fresh_code,
                                     "session_token": session_token
                                 }, timeout=30)
    
    print(f"Login verification result: {login_response.status_code}")
    print(f"Response: {login_response.text}")
    
    # Clean up
    cleanup_code = totp.now()
    if cleanup_code == fresh_code:
        time.sleep(30)
        cleanup_code = totp.now()
    
    requests.post(f"{BACKEND_URL}/admin/2fa/disable", 
                 json={"totp_code": cleanup_code}, timeout=30)

if __name__ == "__main__":
    test_timezone_issue()