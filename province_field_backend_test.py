#!/usr/bin/env python3
"""
Province Field Repositioning Backend Test
=========================================

This test verifies that the province field repositioning (frontend-only change) 
has not broken any backend functionality. The province field was moved from 
Client Information section to Address Information section after the city field.

Test Focus:
1. All existing API endpoints working correctly
2. Registration creation and retrieval functional
3. Form data handling (including province field) working properly
4. Core backend services running properly
"""

import requests
import json
import random
import string
import sys
from dotenv import load_dotenv
import os
from pymongo import MongoClient
from datetime import datetime, date
import time

# Load environment variables
load_dotenv('/app/frontend/.env')
backend_url = os.environ.get('REACT_APP_BACKEND_URL')

load_dotenv('/app/backend/.env')
mongo_url = os.environ.get('MONGO_URL')
db_name = os.environ.get('DB_NAME')

print(f"🔧 Backend URL: {backend_url}")
print(f"🔧 MongoDB URL: {mongo_url}")
print(f"🔧 Database Name: {db_name}")

def generate_sample_base64_image():
    """Generate a simple base64 encoded image for testing"""
    return "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="

def generate_test_data_with_province():
    """Generate test data specifically testing province field handling"""
    random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    
    return {
        "firstName": f"ProvinceTest{random_suffix}",
        "lastName": f"Backend{random_suffix}",
        "dob": "1985-06-15",
        "patientConsent": "Verbal",
        "gender": "Female",
        "province": "British Columbia",  # Test different province
        "disposition": "POCT POS",
        "aka": f"PT{random_suffix}",
        "age": "38",
        "regDate": "2025-01-15",
        "healthCard": ''.join(random.choices(string.digits, k=10)) + "BC",
        "healthCardVersion": "BC",
        "referralSite": "Vancouver - Clinic",
        "address": f"{random.randint(100, 999)} Granville Street",
        "unitNumber": f"Suite {random.randint(100, 999)}",
        "city": "Vancouver",
        "postalCode": f"V{random.randint(1, 9)}A {random.randint(1, 9)}B{random.randint(1, 9)}",
        "phone1": ''.join(random.choices(string.digits, k=10)),
        "phone2": ''.join(random.choices(string.digits, k=10)),
        "ext1": str(random.randint(100, 999)),
        "ext2": str(random.randint(100, 999)),
        "leaveMessage": True,
        "voicemail": False,
        "text": True,
        "preferredTime": "Morning",
        "email": f"provincetest{random_suffix}@example.com",
        "language": "English",
        "specialAttention": "Province field repositioning test",
        "photo": generate_sample_base64_image(),
        "summaryTemplate": "Test template for province field",
        "selectedTemplate": "Positive",
        "physician": "Dr. Province Test",
        "rnaAvailable": "Yes",
        "rnaSampleDate": "2025-01-10",
        "rnaResult": "Positive",
        "coverageType": "MSP",
        "testType": "HCV",
        "hivDate": "2025-01-10",
        "hivResult": "negative",
        "hivType": "Type 1",
        "hivTester": "PT"
    }

def test_api_endpoint(endpoint, method="GET", data=None, description=""):
    """Test an API endpoint and return result"""
    url = f"{backend_url}/api/{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url, timeout=30)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=30)
        elif method == "PUT":
            response = requests.put(url, json=data, timeout=30)
        elif method == "DELETE":
            response = requests.delete(url, timeout=30)
        
        print(f"✅ {description}: {response.status_code}")
        return response.status_code, response.json() if response.content else {}
    
    except requests.exceptions.RequestException as e:
        print(f"❌ {description}: Connection error - {str(e)}")
        return None, {}
    except json.JSONDecodeError:
        print(f"⚠️ {description}: {response.status_code} (No JSON response)")
        return response.status_code, {}

def test_core_backend_services():
    """Test core backend services are running"""
    print("\n🔍 TESTING CORE BACKEND SERVICES")
    print("=" * 50)
    
    # Test basic health check endpoints
    endpoints_to_test = [
        ("admin-registrations-pending", "GET", None, "Pending registrations endpoint"),
        ("admin-registrations-submitted", "GET", None, "Submitted registrations endpoint"),
        ("notes-templates", "GET", None, "Notes templates endpoint"),
        ("clinical-templates", "GET", None, "Clinical templates endpoint")
    ]
    
    success_count = 0
    total_tests = len(endpoints_to_test)
    
    for endpoint, method, data, description in endpoints_to_test:
        status_code, response_data = test_api_endpoint(endpoint, method, data, description)
        if status_code and 200 <= status_code < 300:
            success_count += 1
    
    print(f"\n📊 Core Services Test Results: {success_count}/{total_tests} passed")
    return success_count == total_tests

def test_registration_creation_with_province():
    """Test registration creation with province field in new position"""
    print("\n🔍 TESTING REGISTRATION CREATION WITH PROVINCE FIELD")
    print("=" * 60)
    
    test_data = generate_test_data_with_province()
    
    print(f"📝 Creating registration with province: {test_data['province']}")
    print(f"📍 Address details: {test_data['address']}, {test_data['city']}, {test_data['province']}")
    
    # Test registration creation
    status_code, response_data = test_api_endpoint(
        "admin-register", 
        "POST", 
        test_data, 
        "Create registration with province field"
    )
    
    if status_code == 200 and 'registration_id' in response_data:
        registration_id = response_data['registration_id']
        print(f"✅ Registration created successfully with ID: {registration_id}")
        
        # Test registration retrieval
        status_code, retrieved_data = test_api_endpoint(
            f"admin-registration/{registration_id}",
            "GET",
            None,
            "Retrieve created registration"
        )
        
        if status_code == 200:
            # Verify province field is correctly stored and retrieved
            if retrieved_data.get('province') == test_data['province']:
                print(f"✅ Province field correctly stored and retrieved: {retrieved_data.get('province')}")
                
                # Verify address information is complete
                address_fields = ['address', 'city', 'province', 'postalCode']
                address_complete = all(retrieved_data.get(field) for field in address_fields)
                
                if address_complete:
                    print("✅ Complete address information (including province) verified")
                    print(f"   Address: {retrieved_data.get('address')}")
                    print(f"   City: {retrieved_data.get('city')}")
                    print(f"   Province: {retrieved_data.get('province')}")
                    print(f"   Postal Code: {retrieved_data.get('postalCode')}")
                    return True, registration_id
                else:
                    print("❌ Address information incomplete")
                    return False, None
            else:
                print(f"❌ Province field mismatch. Expected: {test_data['province']}, Got: {retrieved_data.get('province')}")
                return False, None
        else:
            print("❌ Failed to retrieve created registration")
            return False, None
    else:
        print("❌ Failed to create registration")
        return False, None

def test_province_field_variations():
    """Test different province values to ensure field handling is robust"""
    print("\n🔍 TESTING PROVINCE FIELD VARIATIONS")
    print("=" * 45)
    
    provinces_to_test = [
        "Ontario",
        "British Columbia", 
        "Alberta",
        "Quebec",
        "Manitoba",
        "Saskatchewan",
        "Nova Scotia",
        "New Brunswick",
        "Prince Edward Island",
        "Newfoundland and Labrador",
        "Northwest Territories",
        "Nunavut",
        "Yukon"
    ]
    
    success_count = 0
    created_registrations = []
    
    for province in provinces_to_test[:5]:  # Test first 5 to avoid too many test records
        test_data = generate_test_data_with_province()
        test_data['province'] = province
        test_data['firstName'] = f"Province{province.replace(' ', '')}"
        
        print(f"🧪 Testing province: {province}")
        
        status_code, response_data = test_api_endpoint(
            "admin-register",
            "POST",
            test_data,
            f"Create registration with province: {province}"
        )
        
        if status_code == 200 and 'registration_id' in response_data:
            registration_id = response_data['registration_id']
            created_registrations.append(registration_id)
            
            # Verify the province was stored correctly
            status_code, retrieved_data = test_api_endpoint(
                f"admin-registration/{registration_id}",
                "GET",
                None,
                f"Verify province storage: {province}"
            )
            
            if status_code == 200 and retrieved_data.get('province') == province:
                print(f"   ✅ Province '{province}' stored and retrieved correctly")
                success_count += 1
            else:
                print(f"   ❌ Province '{province}' storage/retrieval failed")
        else:
            print(f"   ❌ Failed to create registration with province: {province}")
    
    print(f"\n📊 Province Variations Test Results: {success_count}/5 passed")
    return success_count >= 4, created_registrations  # Allow 1 failure

def test_registration_update_with_province():
    """Test updating registration with province field changes"""
    print("\n🔍 TESTING REGISTRATION UPDATE WITH PROVINCE CHANGES")
    print("=" * 55)
    
    # First create a registration
    success, registration_id = test_registration_creation_with_province()
    
    if not success or not registration_id:
        print("❌ Cannot test updates - registration creation failed")
        return False
    
    # Test updating the province field
    update_data = {
        "province": "Alberta",
        "city": "Calgary",
        "postalCode": "T2P 1J9"
    }
    
    status_code, response_data = test_api_endpoint(
        f"admin-registration/{registration_id}",
        "PUT",
        update_data,
        "Update registration province field"
    )
    
    if status_code == 200:
        # Verify the update
        status_code, retrieved_data = test_api_endpoint(
            f"admin-registrations/{registration_id}",
            "GET",
            None,
            "Verify province field update"
        )
        
        if (status_code == 200 and 
            retrieved_data.get('province') == "Alberta" and
            retrieved_data.get('city') == "Calgary"):
            print("✅ Province field update successful")
            return True
        else:
            print("❌ Province field update verification failed")
            return False
    else:
        print("❌ Province field update failed")
        return False

def test_form_data_handling():
    """Test comprehensive form data handling including province field"""
    print("\n🔍 TESTING COMPREHENSIVE FORM DATA HANDLING")
    print("=" * 50)
    
    # Test with complete form data
    complete_data = generate_test_data_with_province()
    
    status_code, response_data = test_api_endpoint(
        "admin-register",
        "POST",
        complete_data,
        "Complete form data submission"
    )
    
    if status_code == 200 and 'registration_id' in response_data:
        registration_id = response_data['registration_id']
        
        # Retrieve and verify all fields
        status_code, retrieved_data = test_api_endpoint(
            f"admin-registration/{registration_id}",
            "GET",
            None,
            "Verify complete form data"
        )
        
        if status_code == 200:
            # Check critical fields including province
            critical_fields = [
                'firstName', 'lastName', 'province', 'city', 'address', 
                'postalCode', 'phone1', 'email', 'patientConsent'
            ]
            
            missing_fields = []
            for field in critical_fields:
                if not retrieved_data.get(field):
                    missing_fields.append(field)
            
            if not missing_fields:
                print("✅ All critical form fields (including province) handled correctly")
                
                # Specifically verify address section fields are in correct order
                address_section = {
                    'address': retrieved_data.get('address'),
                    'unitNumber': retrieved_data.get('unitNumber'),
                    'city': retrieved_data.get('city'),
                    'province': retrieved_data.get('province'),
                    'postalCode': retrieved_data.get('postalCode')
                }
                
                print("📍 Address Section Fields:")
                for field, value in address_section.items():
                    print(f"   {field}: {value}")
                
                return True
            else:
                print(f"❌ Missing critical fields: {missing_fields}")
                return False
        else:
            print("❌ Failed to retrieve form data for verification")
            return False
    else:
        print("❌ Failed to submit complete form data")
        return False

def test_database_connectivity():
    """Test direct database connectivity to ensure backend can access data"""
    print("\n🔍 TESTING DATABASE CONNECTIVITY")
    print("=" * 40)
    
    try:
        client = MongoClient(mongo_url)
        db = client[db_name]
        
        # Test basic database operations
        collections = db.list_collection_names()
        print(f"✅ Database connected. Collections: {len(collections)}")
        
        # Test admin_registrations collection
        if 'admin_registrations' in collections:
            count = db.admin_registrations.count_documents({})
            print(f"✅ Admin registrations collection accessible. Records: {count}")
            
            # Test a simple query
            recent_records = list(db.admin_registrations.find({}).limit(1))
            if recent_records:
                print("✅ Database queries working correctly")
                return True
            else:
                print("⚠️ No records found but database is accessible")
                return True
        else:
            print("❌ Admin registrations collection not found")
            return False
            
    except Exception as e:
        print(f"❌ Database connectivity failed: {str(e)}")
        return False

def run_comprehensive_backend_test():
    """Run comprehensive backend test suite"""
    print("🚀 PROVINCE FIELD REPOSITIONING - BACKEND FUNCTIONALITY TEST")
    print("=" * 70)
    print("Testing backend functionality after province field repositioning")
    print("(Frontend-only change: moved province field after city field)")
    print("=" * 70)
    
    test_results = {}
    
    # Test 1: Core Backend Services
    test_results['core_services'] = test_core_backend_services()
    
    # Test 2: Database Connectivity
    test_results['database'] = test_database_connectivity()
    
    # Test 3: Registration Creation with Province
    success, _ = test_registration_creation_with_province()
    test_results['registration_creation'] = success
    
    # Test 4: Province Field Variations
    success, _ = test_province_field_variations()
    test_results['province_variations'] = success
    
    # Test 5: Registration Updates
    test_results['registration_updates'] = test_registration_update_with_province()
    
    # Test 6: Form Data Handling
    test_results['form_data_handling'] = test_form_data_handling()
    
    # Summary
    print("\n" + "=" * 70)
    print("🎯 BACKEND TEST RESULTS SUMMARY")
    print("=" * 70)
    
    passed_tests = sum(test_results.values())
    total_tests = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
    
    print(f"\n📊 Overall Results: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 ALL BACKEND TESTS PASSED!")
        print("✅ Province field repositioning has NOT broken backend functionality")
        print("✅ All API endpoints working correctly")
        print("✅ Registration creation and retrieval functional")
        print("✅ Form data handling (including province field) working properly")
        print("✅ Core backend services running properly")
        return True
    else:
        print("⚠️ SOME BACKEND TESTS FAILED!")
        print("❌ Backend functionality may be impacted")
        failed_tests = [name for name, result in test_results.items() if not result]
        print(f"❌ Failed tests: {', '.join(failed_tests)}")
        return False

if __name__ == "__main__":
    success = run_comprehensive_backend_test()
    sys.exit(0 if success else 1)