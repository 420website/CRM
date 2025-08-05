#!/usr/bin/env python3
"""
Brother P-touch Label Printing Backend Test
Testing medical platform backend functionality for label data requirements

Focus Areas:
1. Backend Health Check - Verify service is running and API endpoints accessible
2. Core API Testing - Test main endpoints for registration data
3. Registration Creation - Create test registration with medical data for labels
4. Data Persistence - Verify registration data persists correctly
5. Template Management - Test clinical and notes templates loading
6. Label Data Validation - Ensure all fields needed for labels are working

This test ensures the backend can provide all necessary data for Brother P-touch labels:
- Patient info (name, DOB, health card)
- Contact info (address, phone, email)
- Medical data (disposition, physician, etc.)
"""

import requests
import json
import sys
from datetime import datetime, date
import uuid
import time

# Backend URL - use internal URL for testing from within container
BACKEND_URL = "http://localhost:8001"
API_BASE = f"{BACKEND_URL}/api"

def test_backend_health():
    """Test basic backend connectivity and health"""
    print("🔍 1. Testing Backend Health and Connectivity...")
    
    try:
        # Test basic backend response
        response = requests.get(BACKEND_URL, timeout=10)
        print(f"   ✅ Backend base URL accessible: {response.status_code}")
        
        # Test API root
        api_response = requests.get(API_BASE, timeout=10)
        print(f"   ✅ API base accessible: {api_response.status_code}")
        
        return True
    except Exception as e:
        print(f"   ❌ Backend health check failed: {str(e)}")
        return False

def test_core_api_endpoints():
    """Test main API endpoints needed for label data"""
    print("\n🔍 2. Testing Core API Endpoints...")
    
    endpoints = {
        "admin-registrations-pending": "Pending registrations",
        "admin-registrations-submitted": "Submitted registrations", 
        "clinical-templates": "Clinical templates",
        "notes-templates": "Notes templates",
        "dispositions": "Dispositions",
        "referral-sites": "Referral sites"
    }
    
    results = {}
    
    for endpoint, description in endpoints.items():
        try:
            response = requests.get(f"{API_BASE}/{endpoint}", timeout=10)
            if response.status_code == 200:
                data = response.json()
                count = len(data) if isinstance(data, list) else "N/A"
                print(f"   ✅ {description}: {response.status_code} ({count} items)")
                results[endpoint] = True
            else:
                print(f"   ❌ {description}: {response.status_code}")
                results[endpoint] = False
        except Exception as e:
            print(f"   ❌ {description}: Error - {str(e)}")
            results[endpoint] = False
    
    success_rate = sum(results.values()) / len(results)
    print(f"   📊 Core API Success Rate: {sum(results.values())}/{len(results)} ({success_rate*100:.1f}%)")
    
    return success_rate >= 0.8  # 80% success rate required

def create_test_registration_for_labels():
    """Create a comprehensive test registration with all label data fields"""
    print("\n🔍 3. Creating Test Registration with Label Data...")
    
    # Generate unique test data to avoid duplicates
    test_id = str(uuid.uuid4())[:8]
    
    # Comprehensive registration data with all fields needed for Brother P-touch labels
    registration_data = {
        # Patient Identity (Critical for labels)
        "firstName": f"Michael",
        "lastName": f"Johnson{test_id}",
        "dob": "1985-06-15",
        "healthCard": "1234567890",
        "healthCardVersion": "AB",
        "patientConsent": "written",
        "gender": "Male",
        
        # Contact Information (Critical for labels)
        "address": "456 Oak Avenue",
        "unitNumber": "Unit 12",
        "city": "Toronto", 
        "province": "Ontario",
        "postalCode": "M5V 3A8",
        "phone1": "4161234567",
        "phone2": "6471234567",
        "ext1": "123",
        "email": "michael.johnson@gmail.com",
        "language": "English",
        
        # Medical Information (Important for labels)
        "disposition": "ACTIVE",
        "physician": "Dr. David Fletcher",
        "referralSite": "Toronto - Outreach",
        "specialAttention": "Patient has mobility issues - wheelchair accessible entrance required",
        "instructions": "Patient is on blood thinners. Please apply pressure for extended time after blood draw. Schedule morning appointments only.",
        
        # Registration Details
        "regDate": date.today().strftime("%Y-%m-%d"),
        "aka": "Johnny",
        "age": "38",
        
        # Contact Preferences
        "leaveMessage": True,
        "voicemail": True,
        "text": False,
        "preferredTime": "Morning (9-12)",
        
        # Test Information
        "rnaAvailable": "Yes",
        "rnaSampleDate": "2024-01-15",
        "rnaResult": "Positive",
        "coverageType": "OHIP",
        "testType": "HCV",
        
        # HIV Test Data
        "hivDate": "2024-01-15",
        "hivResult": "negative",
        "hivType": "Type 1",
        "hivTester": "CM"
    }
    
    try:
        print(f"   📝 Creating registration for: {registration_data['firstName']} {registration_data['lastName']}")
        print(f"   📍 Address: {registration_data['address']}, {registration_data['city']}, {registration_data['province']}")
        print(f"   🏥 Health Card: {registration_data['healthCard']}")
        print(f"   📞 Phone: {registration_data['phone1']}")
        
        response = requests.post(f"{API_BASE}/admin-register", 
                               json=registration_data, 
                               timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            registration_id = result.get('registration_id')  # Changed from 'id' to 'registration_id'
            print(f"   ✅ Registration created successfully: {registration_id}")
            print(f"   📊 Response time: {response.elapsed.total_seconds():.2f}s")
            
            return registration_id, registration_data
        else:
            print(f"   ❌ Registration creation failed: {response.status_code}")
            print(f"   📄 Response: {response.text}")
            return None, None
            
    except Exception as e:
        print(f"   ❌ Registration creation error: {str(e)}")
        return None, None

def test_data_persistence(registration_id, original_data):
    """Test that registration data persists correctly and all label fields are retrievable"""
    print("\n🔍 4. Testing Data Persistence and Label Field Retrieval...")
    
    if not registration_id:
        print("   ❌ No registration ID provided - skipping persistence test")
        return False
    
    try:
        # Retrieve the registration
        response = requests.get(f"{API_BASE}/admin-registration/{registration_id}", timeout=10)
        
        if response.status_code == 200:
            retrieved_data = response.json()
            print(f"   ✅ Registration retrieved successfully")
            
            # Check critical label fields
            label_fields = {
                "firstName": "First Name",
                "lastName": "Last Name", 
                "dob": "Date of Birth",
                "healthCard": "Health Card",
                "address": "Address",
                "city": "City",
                "province": "Province",
                "postalCode": "Postal Code",
                "phone1": "Primary Phone",
                "email": "Email",
                "disposition": "Disposition",
                "physician": "Physician",
                "specialAttention": "Special Attention",
                "instructions": "Instructions"
            }
            
            missing_fields = []
            field_matches = []
            
            for field, description in label_fields.items():
                if field in retrieved_data:
                    original_value = original_data.get(field)
                    retrieved_value = retrieved_data.get(field)
                    
                    if original_value == retrieved_value:
                        field_matches.append(field)
                        print(f"   ✅ {description}: '{retrieved_value}'")
                    else:
                        print(f"   ⚠️  {description}: Original='{original_value}' vs Retrieved='{retrieved_value}'")
                else:
                    missing_fields.append(field)
                    print(f"   ❌ {description}: Missing from retrieved data")
            
            # Summary
            total_fields = len(label_fields)
            matched_fields = len(field_matches)
            
            print(f"   📊 Label Field Persistence: {matched_fields}/{total_fields} ({(matched_fields/total_fields)*100:.1f}%)")
            
            if missing_fields:
                print(f"   ⚠️  Missing critical label fields: {', '.join(missing_fields)}")
            
            # Test additional data integrity
            if retrieved_data.get('id') == registration_id:
                print(f"   ✅ Registration ID matches: {registration_id}")
            else:
                print(f"   ❌ Registration ID mismatch")
            
            return len(missing_fields) == 0 and matched_fields >= (total_fields * 0.9)  # 90% match required
            
        else:
            print(f"   ❌ Failed to retrieve registration: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Data persistence test error: {str(e)}")
        return False

def test_template_management():
    """Test that clinical and notes templates are loading correctly for label context"""
    print("\n🔍 5. Testing Template Management for Label Context...")
    
    template_tests = {
        "clinical-templates": "Clinical Summary Templates",
        "notes-templates": "Notes Templates"
    }
    
    results = {}
    
    for endpoint, description in template_tests.items():
        try:
            response = requests.get(f"{API_BASE}/{endpoint}", timeout=10)
            
            if response.status_code == 200:
                templates = response.json()
                
                if isinstance(templates, list) and len(templates) > 0:
                    print(f"   ✅ {description}: {len(templates)} templates loaded")
                    
                    # Check template structure
                    sample_template = templates[0]
                    required_fields = ['id', 'name', 'content']
                    
                    if all(field in sample_template for field in required_fields):
                        print(f"   ✅ Template structure valid - Sample: '{sample_template.get('name')}'")
                        
                        # Check for default templates
                        default_count = len([t for t in templates if t.get('is_default', False)])
                        print(f"   ✅ Default templates: {default_count}")
                        
                        results[endpoint] = True
                    else:
                        print(f"   ❌ {description}: Invalid template structure")
                        results[endpoint] = False
                else:
                    print(f"   ❌ {description}: No templates found")
                    results[endpoint] = False
            else:
                print(f"   ❌ {description}: API failed ({response.status_code})")
                results[endpoint] = False
                
        except Exception as e:
            print(f"   ❌ {description}: Error - {str(e)}")
            results[endpoint] = False
    
    success_rate = sum(results.values()) / len(results)
    print(f"   📊 Template Management Success: {sum(results.values())}/{len(results)} ({success_rate*100:.1f}%)")
    
    return success_rate == 1.0  # 100% required for templates

def test_label_data_validation(registration_id):
    """Validate that all data needed for Brother P-touch labels is properly formatted"""
    print("\n🔍 6. Testing Label Data Validation and Formatting...")
    
    if not registration_id:
        print("   ❌ No registration ID provided - skipping label validation")
        return False
    
    try:
        # Get registration data
        response = requests.get(f"{API_BASE}/admin-registration/{registration_id}", timeout=10)
        
        if response.status_code != 200:
            print(f"   ❌ Could not retrieve registration for label validation: {response.status_code}")
            return False
        
        data = response.json()
        
        # Define label format requirements
        label_validations = {
            "Patient Name": {
                "fields": ["firstName", "lastName"],
                "format": lambda d: f"{d.get('firstName', '')} {d.get('lastName', '')}".strip(),
                "required": True
            },
            "Health Card": {
                "fields": ["healthCard", "healthCardVersion"],
                "format": lambda d: f"{d.get('healthCard', '')} {d.get('healthCardVersion', '')}".strip(),
                "required": True
            },
            "Date of Birth": {
                "fields": ["dob"],
                "format": lambda d: d.get('dob', ''),
                "required": True
            },
            "Address": {
                "fields": ["address", "unitNumber", "city", "province", "postalCode"],
                "format": lambda d: f"{d.get('unitNumber', '')} {d.get('address', '')}, {d.get('city', '')}, {d.get('province', '')} {d.get('postalCode', '')}".strip(),
                "required": False
            },
            "Phone": {
                "fields": ["phone1"],
                "format": lambda d: d.get('phone1', ''),
                "required": False
            },
            "Email": {
                "fields": ["email"],
                "format": lambda d: d.get('email', ''),
                "required": False
            },
            "Disposition": {
                "fields": ["disposition"],
                "format": lambda d: d.get('disposition', ''),
                "required": False
            },
            "Physician": {
                "fields": ["physician"],
                "format": lambda d: d.get('physician', ''),
                "required": False
            }
        }
        
        validation_results = {}
        
        for label_type, validation in label_validations.items():
            try:
                formatted_value = validation["format"](data)
                
                if validation["required"] and not formatted_value:
                    print(f"   ❌ {label_type}: Required field is empty")
                    validation_results[label_type] = False
                elif formatted_value:
                    print(f"   ✅ {label_type}: '{formatted_value}'")
                    validation_results[label_type] = True
                else:
                    print(f"   ⚠️  {label_type}: Optional field is empty")
                    validation_results[label_type] = True  # Optional fields can be empty
                    
            except Exception as e:
                print(f"   ❌ {label_type}: Formatting error - {str(e)}")
                validation_results[label_type] = False
        
        # Summary
        passed_validations = sum(validation_results.values())
        total_validations = len(validation_results)
        
        print(f"   📊 Label Data Validation: {passed_validations}/{total_validations} ({(passed_validations/total_validations)*100:.1f}%)")
        
        # Check critical fields
        critical_fields = ["Patient Name", "Health Card", "Date of Birth"]
        critical_passed = sum(validation_results.get(field, False) for field in critical_fields)
        
        if critical_passed == len(critical_fields):
            print(f"   ✅ All critical label fields are valid")
        else:
            print(f"   ❌ Critical label fields missing: {len(critical_fields) - critical_passed}")
        
        return critical_passed == len(critical_fields)
        
    except Exception as e:
        print(f"   ❌ Label data validation error: {str(e)}")
        return False

def cleanup_test_registration(registration_id):
    """Clean up test registration"""
    if not registration_id:
        return
    
    try:
        response = requests.delete(f"{API_BASE}/admin-registration/{registration_id}", timeout=10)
        if response.status_code == 200:
            print(f"   🧹 Test registration cleaned up: {registration_id}")
        else:
            print(f"   ⚠️  Could not clean up test registration: {response.status_code}")
    except Exception as e:
        print(f"   ⚠️  Cleanup error: {str(e)}")

def run_brother_ptouch_backend_test():
    """Run comprehensive backend test for Brother P-touch label printing functionality"""
    print("=" * 80)
    print("🏷️  BROTHER P-TOUCH LABEL PRINTING - BACKEND FUNCTIONALITY TEST")
    print("=" * 80)
    print(f"Backend URL: {BACKEND_URL}")
    print(f"API Base: {API_BASE}")
    print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Purpose: Verify backend can provide all data needed for Brother P-touch labels")
    print("=" * 80)
    
    test_results = {}
    registration_id = None
    registration_data = None
    
    # Run all tests in sequence
    test_results['backend_health'] = test_backend_health()
    test_results['core_api_endpoints'] = test_core_api_endpoints()
    
    # Create test registration
    if test_results['core_api_endpoints']:
        registration_id, registration_data = create_test_registration_for_labels()
        test_results['registration_creation'] = registration_id is not None
    else:
        test_results['registration_creation'] = False
    
    # Test data persistence
    test_results['data_persistence'] = test_data_persistence(registration_id, registration_data)
    
    # Test template management
    test_results['template_management'] = test_template_management()
    
    # Test label data validation
    test_results['label_data_validation'] = test_label_data_validation(registration_id)
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 BROTHER P-TOUCH BACKEND TEST RESULTS")
    print("=" * 80)
    
    passed_tests = sum(test_results.values())
    total_tests = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
    
    print(f"\nOverall Success Rate: {passed_tests}/{total_tests} ({(passed_tests/total_tests)*100:.1f}%)")
    
    # Analysis for Brother P-touch functionality
    print("\n🏷️  BROTHER P-TOUCH LABEL READINESS ANALYSIS:")
    
    if test_results['backend_health'] and test_results['core_api_endpoints']:
        print("   ✅ Backend service is operational and accessible")
    else:
        print("   ❌ Backend service issues - labels cannot be generated")
    
    if test_results['registration_creation'] and test_results['data_persistence']:
        print("   ✅ Patient registration data is properly stored and retrievable")
    else:
        print("   ❌ Registration data issues - patient info may be incomplete for labels")
    
    if test_results['template_management']:
        print("   ✅ Clinical and notes templates are loading correctly")
    else:
        print("   ❌ Template loading issues - medical context may be missing from labels")
    
    if test_results['label_data_validation']:
        print("   ✅ All critical label data fields are properly formatted and available")
    else:
        print("   ❌ Label data formatting issues - some fields may be missing from labels")
    
    # Overall assessment
    critical_tests = ['backend_health', 'registration_creation', 'data_persistence', 'label_data_validation']
    critical_passed = sum(test_results.get(test, False) for test in critical_tests)
    
    print(f"\n🎯 BROTHER P-TOUCH INTEGRATION READINESS:")
    if critical_passed == len(critical_tests):
        print("   🎉 READY FOR BROTHER P-TOUCH INTEGRATION!")
        print("   ✅ All critical backend functionality is working")
        print("   ✅ Patient data (name, health card, DOB, address, phone) is available")
        print("   ✅ Medical data (disposition, physician, instructions) is accessible")
        print("   ✅ Data persistence ensures reliable label generation")
    else:
        print("   ⚠️  BROTHER P-TOUCH INTEGRATION ISSUES DETECTED")
        print(f"   ❌ {len(critical_tests) - critical_passed} critical issues need resolution")
        print("   🔧 Fix backend issues before implementing label printing")
    
    # Cleanup
    if registration_id:
        cleanup_test_registration(registration_id)
    
    print("=" * 80)
    
    return critical_passed == len(critical_tests)

if __name__ == "__main__":
    success = run_brother_ptouch_backend_test()
    sys.exit(0 if success else 1)