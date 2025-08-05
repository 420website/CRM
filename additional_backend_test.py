#!/usr/bin/env python3
"""
Test Additional Backend Endpoints for my420.ca
"""

import requests
import json
import sys
import os
from dotenv import load_dotenv

def test_additional_endpoints():
    """Test additional backend endpoints"""
    # Load environment variables
    load_dotenv('/app/frontend/.env')
    backend_url = os.environ.get('REACT_APP_BACKEND_URL')
    
    if not backend_url:
        print("❌ Error: REACT_APP_BACKEND_URL not found in frontend .env file")
        return False
    
    print("🚀 Testing Additional Backend Endpoints")
    print(f"🔗 Base URL: {backend_url}")
    print("=" * 50)
    
    tests_passed = 0
    tests_total = 0
    
    # Test 1: Health check endpoint
    print("\n🔍 Testing Health Check Endpoint...")
    tests_total += 1
    try:
        response = requests.get(f"{backend_url}/api")
        if response.status_code == 200:
            print("✅ Health check endpoint working")
            tests_passed += 1
        else:
            print(f"❌ Health check failed - Status: {response.status_code}")
    except Exception as e:
        print(f"❌ Health check error: {str(e)}")
    
    # Test 2: User registration endpoint
    print("\n🔍 Testing User Registration Endpoint...")
    tests_total += 1
    user_data = {
        "full_name": "Test User",
        "date_of_birth": "1990-01-01",
        "phone_number": "4161234567",
        "email": "test@example.com",
        "consent_given": True
    }
    try:
        response = requests.post(f"{backend_url}/api/register", json=user_data)
        if response.status_code == 200:
            print("✅ User registration endpoint working")
            tests_passed += 1
        else:
            print(f"❌ User registration failed - Status: {response.status_code}")
    except Exception as e:
        print(f"❌ User registration error: {str(e)}")
    
    # Test 3: Contact form endpoint
    print("\n🔍 Testing Contact Form Endpoint...")
    tests_total += 1
    contact_data = {
        "name": "Test Contact",
        "email": "contact@example.com",
        "subject": "Test Subject",
        "message": "This is a test message for the contact form."
    }
    try:
        response = requests.post(f"{backend_url}/api/contact", json=contact_data)
        if response.status_code == 200:
            print("✅ Contact form endpoint working")
            tests_passed += 1
        else:
            print(f"❌ Contact form failed - Status: {response.status_code}")
    except Exception as e:
        print(f"❌ Contact form error: {str(e)}")
    
    # Test 4: Get registrations endpoint
    print("\n🔍 Testing Get Registrations Endpoint...")
    tests_total += 1
    try:
        response = requests.get(f"{backend_url}/api/registrations")
        if response.status_code == 200:
            print("✅ Get registrations endpoint working")
            data = response.json()
            print(f"   Found {len(data)} registrations")
            tests_passed += 1
        else:
            print(f"❌ Get registrations failed - Status: {response.status_code}")
    except Exception as e:
        print(f"❌ Get registrations error: {str(e)}")
    
    # Test 5: Get contact messages endpoint
    print("\n🔍 Testing Get Contact Messages Endpoint...")
    tests_total += 1
    try:
        response = requests.get(f"{backend_url}/api/contact-messages")
        if response.status_code == 200:
            print("✅ Get contact messages endpoint working")
            data = response.json()
            print(f"   Found {len(data)} contact messages")
            tests_passed += 1
        else:
            print(f"❌ Get contact messages failed - Status: {response.status_code}")
    except Exception as e:
        print(f"❌ Get contact messages error: {str(e)}")
    
    # Test 6: Admin registration endpoint
    print("\n🔍 Testing Admin Registration Endpoint...")
    tests_total += 1
    admin_data = {
        "firstName": "Admin",
        "lastName": "Test",
        "patientConsent": "Verbal",
        "email": "admin@example.com"
    }
    try:
        response = requests.post(f"{backend_url}/api/admin-register", json=admin_data)
        if response.status_code == 200:
            print("✅ Admin registration endpoint working")
            data = response.json()
            registration_id = data.get('registration_id')
            print(f"   Registration ID: {registration_id}")
            tests_passed += 1
            
            # Test getting pending registrations
            print("\n🔍 Testing Get Pending Admin Registrations...")
            tests_total += 1
            try:
                response = requests.get(f"{backend_url}/api/admin-registrations/pending")
                if response.status_code == 200:
                    print("✅ Get pending admin registrations working")
                    data = response.json()
                    print(f"   Found {len(data.get('registrations', []))} pending registrations")
                    tests_passed += 1
                else:
                    print(f"❌ Get pending admin registrations failed - Status: {response.status_code}")
            except Exception as e:
                print(f"❌ Get pending admin registrations error: {str(e)}")
            
            # Test getting specific registration
            if registration_id:
                print("\n🔍 Testing Get Specific Admin Registration...")
                tests_total += 1
                try:
                    response = requests.get(f"{backend_url}/api/admin-registration/{registration_id}")
                    if response.status_code == 200:
                        print("✅ Get specific admin registration working")
                        tests_passed += 1
                    else:
                        print(f"❌ Get specific admin registration failed - Status: {response.status_code}")
                except Exception as e:
                    print(f"❌ Get specific admin registration error: {str(e)}")
        else:
            print(f"❌ Admin registration failed - Status: {response.status_code}")
    except Exception as e:
        print(f"❌ Admin registration error: {str(e)}")
    
    # Test 7: MongoDB connection test
    print("\n🔍 Testing MongoDB Connection...")
    tests_total += 1
    try:
        from pymongo import MongoClient
        load_dotenv('/app/backend/.env')
        mongo_url = os.environ.get('MONGO_URL')
        db_name = os.environ.get('DB_NAME')
        
        if mongo_url and db_name:
            client = MongoClient(mongo_url)
            db = client[db_name]
            # Try to get collection stats
            collections = db.list_collection_names()
            print(f"✅ MongoDB connection working")
            print(f"   Database: {db_name}")
            print(f"   Collections: {len(collections)}")
            print(f"   Collection names: {', '.join(collections[:5])}{'...' if len(collections) > 5 else ''}")
            tests_passed += 1
        else:
            print("❌ MongoDB connection details not found")
    except Exception as e:
        print(f"❌ MongoDB connection error: {str(e)}")
    
    # Print summary
    print("\n" + "=" * 50)
    print(f"📊 Test Summary: {tests_passed}/{tests_total} tests passed")
    
    if tests_passed == tests_total:
        print("🎉 All additional endpoint tests passed!")
        return True
    else:
        failed_tests = tests_total - tests_passed
        print(f"⚠️  {failed_tests} tests failed")
        return False

def main():
    """Main test function"""
    success = test_additional_endpoints()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())