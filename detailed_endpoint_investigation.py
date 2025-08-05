#!/usr/bin/env python3
"""
DETAILED ENDPOINT INVESTIGATION
===============================
Investigating the specific issue with optimized endpoints returning wrong data structure.
"""

import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/backend/.env')

# Get backend URL from frontend env
with open('/app/frontend/.env', 'r') as f:
    for line in f:
        if line.startswith('REACT_APP_BACKEND_URL='):
            BACKEND_URL = line.split('=')[1].strip()
            break

API_BASE = f"{BACKEND_URL}/api"

print("🔍 DETAILED ENDPOINT INVESTIGATION")
print("=" * 50)

def test_endpoint_detailed(endpoint_name, url):
    """Test an endpoint and show detailed response structure"""
    print(f"\n📋 Testing {endpoint_name}:")
    print(f"URL: {url}")
    
    try:
        response = requests.get(url, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response Type: {type(data)}")
            
            if isinstance(data, dict):
                print("Response Keys:", list(data.keys()))
                
                # Check for different possible data fields
                for key in ['data', 'results', 'registrations']:
                    if key in data:
                        items = data[key]
                        print(f"  {key}: {len(items)} items")
                        if items and len(items) > 0:
                            print(f"  Sample item keys: {list(items[0].keys())}")
                            print(f"  Sample item: {items[0].get('firstName', 'N/A')} {items[0].get('lastName', 'N/A')} - {items[0].get('status', 'N/A')}")
                
                # Check pagination info
                if 'pagination' in data:
                    pagination = data['pagination']
                    print(f"  Pagination: {pagination}")
                
                # Check total count
                for key in ['total', 'total_records', 'total_count']:
                    if key in data:
                        print(f"  {key}: {data[key]}")
                        
            elif isinstance(data, list):
                print(f"Response is a list with {len(data)} items")
                if data:
                    print(f"Sample item: {data[0].get('firstName', 'N/A')} {data[0].get('lastName', 'N/A')} - {data[0].get('status', 'N/A')}")
        else:
            print(f"Error Response: {response.text}")
            
    except Exception as e:
        print(f"Request failed: {str(e)}")

# Test all relevant endpoints
test_endpoint_detailed("Optimized Submitted", f"{API_BASE}/admin-registrations-submitted-optimized")
test_endpoint_detailed("Regular Submitted", f"{API_BASE}/admin-registrations-submitted")
test_endpoint_detailed("Optimized Pending", f"{API_BASE}/admin-registrations-pending-optimized")
test_endpoint_detailed("Regular Pending", f"{API_BASE}/admin-registrations-pending")
test_endpoint_detailed("Dashboard Stats", f"{API_BASE}/admin-dashboard-stats")

# Test with different page sizes to see if that affects results
print(f"\n🔍 Testing optimized submitted with different parameters:")
test_params = [
    "?page=1&page_size=10",
    "?page=1&page_size=50", 
    "?page=1&page_size=100"
]

for params in test_params:
    url = f"{API_BASE}/admin-registrations-submitted-optimized{params}"
    print(f"\n📋 Testing with params {params}:")
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if 'data' in data:
                print(f"  Found {len(data['data'])} items")
                if 'pagination' in data:
                    print(f"  Total records: {data['pagination'].get('total_records', 'N/A')}")
        else:
            print(f"  Error: {response.status_code}")
    except Exception as e:
        print(f"  Failed: {str(e)}")

print("\n" + "=" * 50)
print("🔍 DETAILED ENDPOINT INVESTIGATION COMPLETED")