#!/usr/bin/env python3
"""
TOTP Replay Attack Investigation
Testing the timing issue with TOTP verification
"""

import requests
import json
import time
import pyotp
from datetime import datetime

# Configuration
BACKEND_URL = "https://46471c8a-a981-4b23-bca9-bb5c0ba282bc.preview.emergentagent.com/api"
DEFAULT_PIN = "0224"

def investigate_totp_timing():
    print("🔍 INVESTIGATING TOTP TIMING ISSUE")
    print("=" * 50)
    
    # Step 1: Get fresh session and setup 2FA
    print("Step 1: Setting up fresh 2FA...")
    
    # Get session token
    pin_response = requests.post(f"{BACKEND_URL}/admin/pin-verify", 
                               json={"pin": DEFAULT_PIN},
                               timeout=30)
    
    if pin_response.status_code != 200:
        print(f"❌ PIN verification failed: {pin_response.status_code}")
        return
    
    session_token = pin_response.json().get('session_token')
    print(f"✅ Session token obtained: {session_token[:20]}...")
    
    # Setup 2FA
    setup_response = requests.post(f"{BACKEND_URL}/admin/2fa/setup", timeout=30)
    
    if setup_response.status_code != 200:
        print(f"❌ 2FA setup failed: {setup_response.status_code}")
        return
    
    setup_data = setup_response.json()
    totp_secret = setup_data.get('totp_secret')
    print(f"✅ TOTP secret obtained: {totp_secret}")
    
    # Step 2: Verify setup with first TOTP code
    print("\nStep 2: Verifying 2FA setup...")
    
    totp = pyotp.TOTP(totp_secret)
    first_code = totp.now()
    print(f"Generated first TOTP code: {first_code}")
    
    verify_setup_response = requests.post(f"{BACKEND_URL}/admin/2fa/verify-setup", 
                                        json={"totp_code": first_code},
                                        timeout=30)
    
    if verify_setup_response.status_code != 200:
        print(f"❌ Setup verification failed: {verify_setup_response.status_code} - {verify_setup_response.text}")
        return
    
    print(f"✅ 2FA setup verified successfully")
    
    # Step 3: Test immediate reuse (should fail due to replay protection)
    print("\nStep 3: Testing immediate TOTP reuse...")
    
    immediate_verify_response = requests.post(f"{BACKEND_URL}/admin/2fa/verify", 
                                            json={
                                                "totp_code": first_code,
                                                "session_token": session_token
                                            },
                                            timeout=30)
    
    print(f"Immediate reuse result: {immediate_verify_response.status_code}")
    if immediate_verify_response.status_code != 200:
        print(f"✅ Replay protection working - code reuse blocked: {immediate_verify_response.text}")
    else:
        print(f"❌ Replay protection failed - code reuse allowed")
    
    # Step 4: Wait for new TOTP window and test
    print("\nStep 4: Waiting for new TOTP window...")
    
    # Wait for next 30-second window
    current_time = int(time.time())
    next_window = ((current_time // 30) + 1) * 30
    wait_time = next_window - current_time + 1  # Add 1 second buffer
    
    print(f"Current time: {current_time}")
    print(f"Next TOTP window: {next_window}")
    print(f"Waiting {wait_time} seconds...")
    
    time.sleep(wait_time)
    
    # Generate new code
    second_code = totp.now()
    print(f"Generated second TOTP code: {second_code}")
    
    if second_code == first_code:
        print("⚠️ Same code generated - waiting longer...")
        time.sleep(30)
        second_code = totp.now()
        print(f"Generated third TOTP code: {second_code}")
    
    # Test new code
    new_verify_response = requests.post(f"{BACKEND_URL}/admin/2fa/verify", 
                                      json={
                                          "totp_code": second_code,
                                          "session_token": session_token
                                      },
                                      timeout=30)
    
    print(f"New code verification result: {new_verify_response.status_code}")
    if new_verify_response.status_code == 200:
        print(f"✅ New TOTP code accepted: {new_verify_response.json()}")
    else:
        print(f"❌ New TOTP code rejected: {new_verify_response.text}")
    
    # Step 5: Clean up - disable 2FA
    print("\nStep 5: Cleaning up...")
    
    cleanup_code = totp.now()
    time.sleep(1)  # Small delay
    if cleanup_code == second_code:
        time.sleep(30)
        cleanup_code = totp.now()
    
    disable_response = requests.post(f"{BACKEND_URL}/admin/2fa/disable", 
                                   json={"totp_code": cleanup_code},
                                   timeout=30)
    
    if disable_response.status_code == 200:
        print(f"✅ 2FA disabled for cleanup")
    else:
        print(f"⚠️ 2FA disable failed: {disable_response.status_code}")

if __name__ == "__main__":
    investigate_totp_timing()