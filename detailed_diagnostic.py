#!/usr/bin/env python3
"""
Detailed diagnostic test for TOTP login verification issue
"""

import requests
import json
import time
import pyotp
from datetime import datetime
import pytz

# Configuration
BACKEND_URL = "https://46471c8a-a981-4b23-bca9-bb5c0ba282bc.preview.emergentagent.com/api"
DEFAULT_PIN = "0224"

def detailed_diagnostic():
    print("🔍 DETAILED DIAGNOSTIC FOR TOTP LOGIN VERIFICATION")
    print("=" * 60)
    
    # Step 1: Fresh setup
    print("Step 1: Fresh 2FA setup...")
    
    # Get session token
    pin_response = requests.post(f"{BACKEND_URL}/admin/pin-verify", 
                               json={"pin": DEFAULT_PIN}, timeout=30)
    
    if pin_response.status_code != 200:
        print(f"❌ PIN verification failed: {pin_response.status_code}")
        return
    
    pin_data = pin_response.json()
    session_token = pin_data.get('session_token')
    print(f"✅ Session token: {session_token}")
    print(f"   2FA enabled: {pin_data.get('two_fa_enabled')}")
    print(f"   2FA required: {pin_data.get('two_fa_required')}")
    
    # Setup 2FA
    setup_response = requests.post(f"{BACKEND_URL}/admin/2fa/setup", timeout=30)
    
    if setup_response.status_code != 200:
        print(f"❌ 2FA setup failed: {setup_response.status_code}")
        return
    
    setup_data = setup_response.json()
    totp_secret = setup_data.get('totp_secret')
    backup_codes = setup_data.get('backup_codes', [])
    print(f"✅ TOTP secret: {totp_secret}")
    print(f"✅ Backup codes count: {len(backup_codes)}")
    
    # Step 2: Verify setup
    print("\nStep 2: Verifying 2FA setup...")
    
    totp = pyotp.TOTP(totp_secret)
    setup_code = totp.now()
    print(f"Setup TOTP code: {setup_code}")
    
    verify_setup_response = requests.post(f"{BACKEND_URL}/admin/2fa/verify-setup", 
                                        json={"totp_code": setup_code}, timeout=30)
    
    if verify_setup_response.status_code != 200:
        print(f"❌ Setup verification failed: {verify_setup_response.status_code}")
        return
    
    print(f"✅ 2FA setup verified")
    
    # Step 3: Check PIN verification again (should show 2FA enabled now)
    print("\nStep 3: Checking PIN verification after 2FA enabled...")
    
    pin_response2 = requests.post(f"{BACKEND_URL}/admin/pin-verify", 
                                json={"pin": DEFAULT_PIN}, timeout=30)
    
    if pin_response2.status_code == 200:
        pin_data2 = pin_response2.json()
        new_session_token = pin_data2.get('session_token')
        print(f"✅ New session token: {new_session_token}")
        print(f"   2FA enabled: {pin_data2.get('two_fa_enabled')}")
        print(f"   2FA required: {pin_data2.get('two_fa_required')}")
        
        # Use the new session token
        session_token = new_session_token
    else:
        print(f"❌ PIN verification failed: {pin_response2.status_code}")
    
    # Step 4: Wait and test TOTP login verification
    print("\nStep 4: Testing TOTP login verification...")
    
    # Wait for fresh TOTP window
    current_time = int(time.time())
    next_window = ((current_time // 30) + 1) * 30
    wait_time = next_window - current_time + 2
    print(f"Waiting {wait_time} seconds for fresh TOTP window...")
    time.sleep(wait_time)
    
    login_code = totp.now()
    print(f"Login TOTP code: {login_code}")
    
    # Test with current session token
    login_response = requests.post(f"{BACKEND_URL}/admin/2fa/verify", 
                                 json={
                                     "totp_code": login_code,
                                     "session_token": session_token
                                 }, timeout=30)
    
    print(f"Login verification result: {login_response.status_code}")
    print(f"Response: {login_response.text}")
    
    # Step 5: Try backup code as alternative
    print("\nStep 5: Testing backup code as alternative...")
    
    if backup_codes:
        backup_code = backup_codes[0]
        print(f"Testing backup code: {backup_code}")
        
        backup_response = requests.post(f"{BACKEND_URL}/admin/2fa/verify", 
                                      json={
                                          "backup_code": backup_code,
                                          "session_token": session_token
                                      }, timeout=30)
        
        print(f"Backup code result: {backup_response.status_code}")
        print(f"Response: {backup_response.text}")
    
    # Step 6: Clean up
    print("\nStep 6: Cleaning up...")
    
    # Wait for fresh code for cleanup
    time.sleep(35)
    cleanup_code = totp.now()
    
    disable_response = requests.post(f"{BACKEND_URL}/admin/2fa/disable", 
                                   json={"totp_code": cleanup_code}, timeout=30)
    
    print(f"Cleanup result: {disable_response.status_code}")

if __name__ == "__main__":
    detailed_diagnostic()