#!/usr/bin/env python3
"""
Server Restart Persistence Test
===============================

This test verifies that clinical templates persist across server restarts.
"""

import requests
import subprocess
import time
import sys

BACKEND_URL = "https://46471c8a-a981-4b23-bca9-bb5c0ba282bc.preview.emergentagent.com/api"

def test_server_restart_persistence():
    """Test template persistence across server restart"""
    print("🔄 TESTING SERVER RESTART PERSISTENCE")
    print("=" * 50)
    
    try:
        # 1. Get templates before restart
        print("1️⃣ Getting templates before restart...")
        response = requests.get(f"{BACKEND_URL}/clinical-templates", timeout=30)
        
        if response.status_code == 200:
            templates_before = response.json()
            template_count_before = len(templates_before)
            template_names_before = [t['name'] for t in templates_before]
            print(f"✅ Found {template_count_before} templates before restart")
            print(f"   Template names: {template_names_before[:5]}...")  # Show first 5
        else:
            print(f"❌ Failed to get templates before restart: {response.status_code}")
            return False
        
        # 2. Restart backend service
        print("\n2️⃣ Restarting backend service...")
        try:
            result = subprocess.run(['sudo', 'supervisorctl', 'restart', 'backend'], 
                                  capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                print("✅ Backend service restarted successfully")
            else:
                print(f"❌ Failed to restart backend: {result.stderr}")
                return False
        except subprocess.TimeoutExpired:
            print("❌ Backend restart timed out")
            return False
        
        # 3. Wait for service to be ready
        print("\n3️⃣ Waiting for backend to be ready...")
        max_attempts = 10
        for attempt in range(max_attempts):
            try:
                response = requests.get(f"{BACKEND_URL}/", timeout=10)
                if response.status_code == 200:
                    print(f"✅ Backend ready after {attempt + 1} attempts")
                    break
            except:
                pass
            
            if attempt < max_attempts - 1:
                print(f"   Attempt {attempt + 1}/{max_attempts} - waiting...")
                time.sleep(3)
        else:
            print("❌ Backend not ready after restart")
            return False
        
        # 4. Get templates after restart
        print("\n4️⃣ Getting templates after restart...")
        response = requests.get(f"{BACKEND_URL}/clinical-templates", timeout=30)
        
        if response.status_code == 200:
            templates_after = response.json()
            template_count_after = len(templates_after)
            template_names_after = [t['name'] for t in templates_after]
            print(f"✅ Found {template_count_after} templates after restart")
        else:
            print(f"❌ Failed to get templates after restart: {response.status_code}")
            return False
        
        # 5. Compare templates
        print("\n5️⃣ Comparing templates before and after restart...")
        
        if template_count_before == template_count_after:
            print(f"✅ Template count matches: {template_count_before} templates")
        else:
            print(f"❌ Template count mismatch: {template_count_before} → {template_count_after}")
            return False
        
        # Check if all template names are preserved
        missing_templates = set(template_names_before) - set(template_names_after)
        new_templates = set(template_names_after) - set(template_names_before)
        
        if not missing_templates and not new_templates:
            print("✅ All template names preserved across restart")
        else:
            if missing_templates:
                print(f"❌ Missing templates after restart: {missing_templates}")
            if new_templates:
                print(f"⚠️  New templates after restart: {new_templates}")
            return False
        
        # 6. Verify template content integrity
        print("\n6️⃣ Verifying template content integrity...")
        content_matches = 0
        
        for template_before in templates_before:
            template_after = next((t for t in templates_after if t['name'] == template_before['name']), None)
            if template_after and template_before['content'] == template_after['content']:
                content_matches += 1
        
        if content_matches == len(templates_before):
            print(f"✅ All {content_matches} template contents preserved")
        else:
            print(f"❌ Only {content_matches}/{len(templates_before)} template contents preserved")
            return False
        
        print("\n🎉 SERVER RESTART PERSISTENCE TEST PASSED!")
        print("✅ All templates survived server restart")
        print("✅ Template count preserved")
        print("✅ Template names preserved")
        print("✅ Template content preserved")
        print("✅ Database persistence confirmed")
        
        return True
        
    except Exception as e:
        print(f"❌ Unexpected error during restart test: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_server_restart_persistence()
    sys.exit(0 if success else 1)