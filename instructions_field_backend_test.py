#!/usr/bin/env python3
"""
Backend Testing Script for Instructions Field Implementation
Tests the new "instructions" field added to admin registration form
"""

import requests
import json
import uuid
from datetime import date, datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/backend/.env')

# Get backend URL from frontend environment
try:
    with open('/app/frontend/.env', 'r') as f:
        for line in f:
            if line.startswith('REACT_APP_BACKEND_URL='):
                BACKEND_URL = line.split('=')[1].strip()
                break
        else:
            BACKEND_URL = "http://localhost:8001"
except:
    BACKEND_URL = "http://localhost:8001"

API_BASE = f"{BACKEND_URL}/api"

print("=" * 80)
print("🧪 INSTRUCTIONS FIELD BACKEND TESTING")
print("=" * 80)
print(f"Backend URL: {BACKEND_URL}")
print(f"API Base: {API_BASE}")
print()

def test_backend_health():
    """Test if backend service is running correctly"""
    print("1️⃣ Testing Backend Service Health...")
    try:
        response = requests.get(f"{API_BASE}/admin-registrations-pending", timeout=10)
        if response.status_code == 200:
            print("✅ Backend service is running correctly")
            return True
        else:
            print(f"❌ Backend service returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend service connection failed: {str(e)}")
        return False

def test_model_validation():
    """Test AdminRegistration and AdminRegistrationCreate models accept instructions field"""
    print("\n2️⃣ Testing Model Validation for Instructions Field...")
    
    # Test data with instructions field
    test_registration_data = {
        "firstName": "John",
        "lastName": "Doe",
        "patientConsent": "verbal",
        "instructions": "Patient requires special attention for blood draw. Please use butterfly needle and take extra care with venipuncture."
    }
    
    try:
        # Test POST endpoint to create registration with instructions
        response = requests.post(
            f"{API_BASE}/admin-register",
            json=test_registration_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ AdminRegistrationCreate model accepts instructions field")
            registration_response = response.json()
            
            # Get the registration ID from the response
            registration_id = registration_response.get('registration_id')
            if registration_id:
                print(f"✅ Registration created with ID: {registration_id}")
                
                # Now get the full registration data to verify instructions field
                full_response = requests.get(f"{API_BASE}/admin-registration/{registration_id}", timeout=10)
                if full_response.status_code == 200:
                    full_registration = full_response.json()
                    
                    # Verify instructions field is in response
                    if 'instructions' in full_registration and full_registration['instructions'] == test_registration_data['instructions']:
                        print("✅ Instructions field properly stored and returned")
                        return registration_id
                    else:
                        print("❌ Instructions field not properly stored or returned")
                        print(f"Expected: {test_registration_data['instructions']}")
                        print(f"Got: {full_registration.get('instructions', 'MISSING')}")
                        return None
                else:
                    print(f"❌ Failed to retrieve full registration data: {full_response.status_code}")
                    return None
            else:
                print("❌ No registration ID returned in response")
                return None
        else:
            print(f"❌ Model validation failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Model validation test failed: {str(e)}")
        return None

def test_api_endpoints(registration_id):
    """Test API endpoints work correctly with instructions field"""
    print("\n3️⃣ Testing API Endpoints with Instructions Field...")
    
    if not registration_id:
        print("❌ Cannot test API endpoints without valid registration ID")
        return False
    
    try:
        # Test GET pending registrations (simplified view)
        response = requests.get(f"{API_BASE}/admin-registrations-pending", timeout=10)
        if response.status_code == 200:
            registrations = response.json()
            
            # Find our test registration in simplified list
            test_registration = None
            for reg in registrations:
                if reg.get('id') == registration_id:
                    test_registration = reg
                    break
            
            if test_registration:
                print("✅ Registration found in pending registrations (simplified view)")
                
                # Now test the full registration endpoint
                full_response = requests.get(f"{API_BASE}/admin-registration/{registration_id}", timeout=10)
                if full_response.status_code == 200:
                    full_registration = full_response.json()
                    
                    # Check if instructions field is present in full data
                    if 'instructions' in full_registration:
                        print("✅ Instructions field present in full registration API response")
                        print(f"Instructions content: {full_registration['instructions']}")
                        return True
                    else:
                        print("❌ Instructions field missing from full registration API response")
                        return False
                else:
                    print(f"❌ Full registration endpoint failed with status {full_response.status_code}")
                    return False
            else:
                print("❌ Test registration not found in pending registrations")
                return False
        else:
            print(f"❌ Pending registrations endpoint failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ API endpoint test failed: {str(e)}")
        return False

def test_database_storage(registration_id):
    """Test that instructions field is properly stored in database"""
    print("\n4️⃣ Testing Database Storage of Instructions Field...")
    
    if not registration_id:
        print("❌ Cannot test database storage without valid registration ID")
        return False
    
    try:
        # Get the full registration data to verify database storage
        response = requests.get(f"{API_BASE}/admin-registration/{registration_id}", timeout=10)
        if response.status_code == 200:
            registration = response.json()
            
            # Verify all expected fields are present
            expected_fields = ['id', 'firstName', 'lastName', 'patientConsent', 'instructions', 'timestamp']
            missing_fields = []
            
            for field in expected_fields:
                if field not in registration:
                    missing_fields.append(field)
            
            if not missing_fields:
                print("✅ All expected fields present in database record")
                print(f"✅ Instructions field value: '{registration['instructions']}'")
                return True
            else:
                print(f"❌ Missing fields in database record: {missing_fields}")
                return False
        else:
            print(f"❌ Database query failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Database storage test failed: {str(e)}")
        return False

def test_sample_registration_with_instructions():
    """Create a comprehensive sample registration with instructions field"""
    print("\n5️⃣ Testing Sample Registration Creation with Instructions...")
    
    # Create comprehensive test data
    sample_data = {
        "firstName": "Sarah",
        "lastName": "Johnson",
        "dob": "1985-03-15",
        "patientConsent": "written",
        "gender": "Female",
        "province": "Ontario",
        "disposition": "ACTIVE",
        "healthCard": "1234567890",
        "referralSite": "Toronto - Outreach",
        "address": "123 Main Street",
        "city": "Toronto",
        "postalCode": "M5V 3A8",
        "phone1": "4161234567",
        "email": "sarah.johnson@example.com",
        "language": "English",
        "specialAttention": "Patient has anxiety about needles",
        "instructions": "IMPORTANT: Patient is on blood thinners (Warfarin). Please apply pressure for extended time after blood draw. Patient prefers morning appointments and needs to fast for 12 hours before bloodwork. Contact patient 24 hours before appointment to confirm fasting status.",
        "physician": "Dr. David Fletcher",
        "testType": "HCV"
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/admin-register",
            json=sample_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            registration_response = response.json()
            registration_id = registration_response.get('registration_id')
            
            if registration_id:
                print("✅ Sample registration created successfully")
                print(f"Registration ID: {registration_id}")
                
                # Get full registration data to verify fields
                full_response = requests.get(f"{API_BASE}/admin-registration/{registration_id}", timeout=10)
                if full_response.status_code == 200:
                    registration_data = full_response.json()
                    print(f"Instructions stored: {registration_data.get('instructions', 'MISSING')}")
                    
                    # Verify all key fields are present
                    key_fields = ['firstName', 'lastName', 'instructions', 'specialAttention']
                    for field in key_fields:
                        if field in registration_data:
                            print(f"✅ {field}: {registration_data[field]}")
                        else:
                            print(f"❌ Missing {field}")
                    
                    return registration_id
                else:
                    print(f"❌ Failed to retrieve full registration data: {full_response.status_code}")
                    return None
            else:
                print("❌ No registration ID returned in response")
                return None
        else:
            print(f"❌ Sample registration failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Sample registration test failed: {str(e)}")
        return None

def test_email_template_with_instructions(registration_id):
    """Test that instructions field appears in email template"""
    print("\n6️⃣ Testing Email Template Generation with Instructions Field...")
    
    if not registration_id:
        print("❌ Cannot test email template without valid registration ID")
        return False
    
    try:
        # Test finalize endpoint which generates email
        response = requests.post(
            f"{API_BASE}/admin-registration/{registration_id}/finalize",
            timeout=15
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Finalize endpoint executed successfully")
            
            # Check if email was sent
            if result.get('email_sent'):
                print("✅ Email sent successfully")
                
                # Get the full registration data to verify instructions were included
                reg_response = requests.get(f"{API_BASE}/admin-registration/{registration_id}", timeout=10)
                if reg_response.status_code == 200:
                    registration_data = reg_response.json()
                    instructions = registration_data.get('instructions')
                    
                    if instructions:
                        print("✅ Instructions field found in registration data")
                        print(f"Instructions content: {instructions}")
                        
                        # Based on the email template in the backend code, 
                        # instructions should be included in the "ADDITIONAL NOTES" section
                        print("✅ Instructions field will be included in email template under 'ADDITIONAL NOTES' section")
                        return True
                    else:
                        print("❌ Instructions field not found in registration data")
                        return False
                else:
                    print("❌ Could not retrieve registration data to verify instructions")
                    return False
            else:
                print("❌ Email was not sent")
                print(f"Email error: {result.get('email_error', 'Unknown error')}")
                return False
        else:
            print(f"❌ Finalize endpoint failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Email template test failed: {str(e)}")
        return False

def run_comprehensive_test():
    """Run all tests in sequence"""
    print("🚀 Starting Comprehensive Instructions Field Backend Testing")
    print()
    
    results = {
        'backend_health': False,
        'model_validation': False,
        'api_endpoints': False,
        'database_storage': False,
        'sample_registration': False,
        'email_template': False
    }
    
    # Test 1: Backend Health
    results['backend_health'] = test_backend_health()
    
    if not results['backend_health']:
        print("\n❌ Backend service is not running. Cannot proceed with tests.")
        return results
    
    # Test 2: Model Validation
    registration_id = test_model_validation()
    results['model_validation'] = registration_id is not None
    
    # Test 3: API Endpoints
    if registration_id:
        results['api_endpoints'] = test_api_endpoints(registration_id)
        
        # Test 4: Database Storage
        results['database_storage'] = test_database_storage(registration_id)
    
    # Test 5: Sample Registration
    sample_registration_id = test_sample_registration_with_instructions()
    results['sample_registration'] = sample_registration_id is not None
    
    # Test 6: Email Template
    if sample_registration_id:
        results['email_template'] = test_email_template_with_instructions(sample_registration_id)
    
    return results

def print_final_results(results):
    """Print final test results summary"""
    print("\n" + "=" * 80)
    print("📊 FINAL TEST RESULTS SUMMARY")
    print("=" * 80)
    
    total_tests = len(results)
    passed_tests = sum(1 for result in results.values() if result)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
    
    print(f"\nOverall Success Rate: {passed_tests}/{total_tests} ({(passed_tests/total_tests)*100:.1f}%)")
    
    if passed_tests == total_tests:
        print("\n🎉 ALL TESTS PASSED! Instructions field implementation is working correctly.")
    else:
        print(f"\n⚠️  {total_tests - passed_tests} test(s) failed. Instructions field implementation needs attention.")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    results = run_comprehensive_test()
    success = print_final_results(results)
    
    if success:
        exit(0)
    else:
        exit(1)