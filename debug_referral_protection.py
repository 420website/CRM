#!/usr/bin/env python3

import requests
import json

# Configuration
BACKEND_URL = "https://46471c8a-a981-4b23-bca9-bb5c0ba282bc.preview.emergentagent.com/api"

def debug_default_protection():
    """Debug the default referral site protection issue"""
    
    print("🔍 DEBUGGING DEFAULT REFERRAL SITE PROTECTION")
    print("=" * 50)
    
    try:
        # Get all referral sites
        response = requests.get(f"{BACKEND_URL}/referral-sites")
        if response.status_code == 200:
            referral_sites = response.json()
            default_site = next((site for site in referral_sites if site.get('is_default', False)), None)
            
            if default_site:
                print(f"🎯 Testing deletion of default site: {default_site['name']}")
                print(f"   ID: {default_site['id']}")
                print(f"   is_default: {default_site.get('is_default')}")
                
                # Try to delete the default referral site
                response = requests.delete(f"{BACKEND_URL}/referral-sites/{default_site['id']}")
                
                print(f"📊 Response Status: {response.status_code}")
                print(f"📄 Response Body: {response.text}")
                
                if response.status_code == 400:
                    print("✅ Protection working correctly")
                elif response.status_code == 500:
                    print("❌ Server error - protection logic may have an issue")
                else:
                    print(f"⚠️ Unexpected status code: {response.status_code}")
            else:
                print("❌ No default referral sites found")
        else:
            print(f"❌ Failed to get referral sites: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    debug_default_protection()