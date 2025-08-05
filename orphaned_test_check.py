#!/usr/bin/env python3
"""
Quick test to check for orphaned test records
"""

import requests
import os

BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://46471c8a-a981-4b23-bca9-bb5c0ba282bc.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

def check_orphaned_records():
    """Check for orphaned test records"""
    print("🔍 Checking for orphaned test records...")
    
    # Try to access a non-existent registration's tests
    fake_id = "non-existent-registration-id"
    response = requests.get(f"{API_BASE}/admin-registration/{fake_id}/tests")
    
    print(f"Response status: {response.status_code}")
    if response.status_code == 200:
        tests = response.json()
        print(f"Response content: {tests}")
        if isinstance(tests, list) and tests:
            print(f"Found {len(tests)} test records for non-existent registration")
            for test in tests:
                if isinstance(test, dict):
                    print(f"  - ID: {test.get('id')}, Registration ID: {test.get('registration_id')}")
                else:
                    print(f"  - Test record: {test}")
        elif isinstance(tests, dict):
            print(f"Response is dict: {tests}")
        else:
            print("No test records found")
    else:
        print(f"Response: {response.text}")

if __name__ == "__main__":
    check_orphaned_records()