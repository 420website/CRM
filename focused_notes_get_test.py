#!/usr/bin/env python3
"""
Focused Notes Template GET API Test
Tests the GET endpoint specifically with longer timeout and retry logic
"""

import requests
import json
import time

# Backend URL from environment
BACKEND_URL = "https://46471c8a-a981-4b23-bca9-bb5c0ba282bc.preview.emergentagent.com/api"

def test_get_notes_templates_with_retry():
    """Test GET /api/notes-templates with retry logic"""
    print("🧪 Testing GET /api/notes-templates with retry logic...")
    
    max_retries = 3
    timeout = 30
    
    for attempt in range(max_retries):
        try:
            print(f"Attempt {attempt + 1}/{max_retries}...")
            response = requests.get(f"{BACKEND_URL}/notes-templates", timeout=timeout)
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                templates = response.json()
                print(f"✅ SUCCESS: Retrieved {len(templates)} templates")
                
                # Check for default templates
                template_names = [t.get('name') for t in templates]
                expected_defaults = ['Consultation', 'Lab', 'Prescription']
                
                print(f"Template names found: {template_names}")
                
                defaults_found = 0
                for default_name in expected_defaults:
                    if default_name in template_names:
                        print(f"✅ Default template '{default_name}' found")
                        defaults_found += 1
                    else:
                        print(f"⚠️  Default template '{default_name}' missing")
                
                # Show template details
                for template in templates:
                    print(f"Template: {template.get('name')} (Default: {template.get('is_default')})")
                    print(f"  ID: {template.get('id')}")
                    print(f"  Content length: {len(template.get('content', ''))}")
                    print(f"  Created: {template.get('created_at')}")
                
                return {
                    'success': True,
                    'templates': templates,
                    'defaults_found': defaults_found,
                    'total_templates': len(templates)
                }
            else:
                print(f"❌ HTTP Error: {response.status_code} - {response.text}")
                if attempt < max_retries - 1:
                    print("Retrying in 2 seconds...")
                    time.sleep(2)
                    continue
                else:
                    return {'success': False, 'error': f"HTTP {response.status_code}"}
                    
        except requests.exceptions.Timeout:
            print(f"❌ Timeout error (>{timeout}s)")
            if attempt < max_retries - 1:
                print("Retrying with longer timeout...")
                timeout += 10
                time.sleep(2)
                continue
            else:
                return {'success': False, 'error': 'Timeout'}
                
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
            if attempt < max_retries - 1:
                print("Retrying in 2 seconds...")
                time.sleep(2)
                continue
            else:
                return {'success': False, 'error': str(e)}
    
    return {'success': False, 'error': 'Max retries exceeded'}

def test_health_check():
    """Test basic health check first"""
    print("🏥 Testing basic health check...")
    
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=10)
        print(f"Health check status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Backend is healthy")
            return True
        else:
            print(f"⚠️  Backend health check failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Health check error: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Focused Notes Template GET API Testing")
    print("=" * 50)
    
    # First test health
    health_ok = test_health_check()
    
    # Then test GET endpoint
    result = test_get_notes_templates_with_retry()
    
    print("\n" + "=" * 50)
    print("📊 RESULTS")
    print("=" * 50)
    
    if result['success']:
        print("✅ GET /api/notes-templates is working correctly!")
        print(f"Total templates: {result['total_templates']}")
        print(f"Default templates found: {result['defaults_found']}/3")
        
        if result['defaults_found'] == 3:
            print("🎉 All default templates (Consultation, Lab, Prescription) are present!")
        else:
            print("⚠️  Some default templates may be missing")
    else:
        print(f"❌ GET endpoint failed: {result['error']}")
        print("This could be due to:")
        print("- Network connectivity issues")
        print("- Backend service temporarily unavailable")
        print("- Database connection problems")
        print("- High server load causing timeouts")