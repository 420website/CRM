#!/usr/bin/env python3
"""
Debug Clinical Template Model Validation
"""

import requests
import json

BACKEND_URL = "https://cd556dd9-d36b-422e-8110-4b1830397661.preview.emergentagent.com/api"

def debug_template_structure():
    """Debug the actual template structure returned by the API"""
    print("🔍 DEBUGGING TEMPLATE STRUCTURE")
    print("=" * 50)
    
    try:
        # Get all templates
        response = requests.get(f"{BACKEND_URL}/clinical-templates", timeout=10)
        
        if response.status_code == 200:
            templates = response.json()
            print(f"Found {len(templates)} templates")
            
            if templates:
                template = templates[0]
                print(f"\nFirst template structure:")
                print(json.dumps(template, indent=2))
                
                print(f"\nActual fields in template:")
                for field in template.keys():
                    print(f"  - {field}: {type(template[field])}")
                
                required_fields = ['id', 'name', 'content', 'is_default', 'created_at', 'updated_at']
                print(f"\nRequired fields check:")
                for field in required_fields:
                    if field in template:
                        print(f"  ✅ {field}: Present")
                    else:
                        print(f"  ❌ {field}: Missing")
                
                missing_fields = [field for field in required_fields if field not in template]
                if missing_fields:
                    print(f"\nMissing fields: {missing_fields}")
                else:
                    print(f"\n✅ All required fields are present!")
            else:
                print("No templates found to analyze")
        else:
            print(f"Failed to get templates: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    debug_template_structure()