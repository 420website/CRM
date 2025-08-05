import requests
import json
import random
import string
import sys
from dotenv import load_dotenv
import os
from pymongo import MongoClient

# Load environment variables
load_dotenv('/app/frontend/.env')
backend_url = os.environ.get('REACT_APP_BACKEND_URL')

load_dotenv('/app/backend/.env')
mongo_url = os.environ.get('MONGO_URL')
db_name = os.environ.get('DB_NAME')

def generate_sample_base64_image():
    """Generate a simple base64 encoded image for testing"""
    return "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="

def generate_test_data():
    """Generate random test data for admin registration"""
    random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    
    return {
        "firstName": f"RNA{random_suffix}",
        "lastName": f"Test{random_suffix}",
        "dob": None,
        "patientConsent": "Verbal",
        "gender": "Male",
        "province": "Ontario",
        "disposition": "POCT NEG",
        "aka": f"RNA{random_suffix}",
        "age": "40",
        "regDate": None,
        "healthCard": ''.join(random.choices(string.digits, k=10)),
        "healthCardVersion": "AB",
        "referralSite": "Toronto - Outreach",
        "address": f"{random.randint(100, 999)} Main Street",
        "unitNumber": str(random.randint(1, 100)),
        "city": "Toronto",
        "postalCode": f"M{random.randint(1, 9)}A {random.randint(1, 9)}B{random.randint(1, 9)}",
        "phone1": ''.join(random.choices(string.digits, k=10)),
        "phone2": ''.join(random.choices(string.digits, k=10)),
        "ext1": str(random.randint(100, 999)),
        "ext2": str(random.randint(100, 999)),
        "leaveMessage": True,
        "voicemail": True,
        "text": False,
        "preferredTime": "Afternoon",
        "email": f"rna.test.{random_suffix}@example.com",
        "language": "English",
        "specialAttention": "RNA test patient",
        "photo": generate_sample_base64_image(),
        "physician": "Dr. David Fletcher",
        "rnaAvailable": "Yes",
        "rnaSampleDate": "2025-07-15",
        "rnaResult": "Negative"
    }

def test_admin_registration_with_rna_fields():
    """Test admin registration with RNA fields"""
    print("\n" + "=" * 50)
    print("🔍 Testing Admin Registration with RNA Fields")
    print("=" * 50)
    
    # Create test data with RNA fields
    test_data = generate_test_data()
    
    # Step 1: Create admin registration
    print("\n🔍 Step 1: Creating admin registration with RNA fields...")
    response = requests.post(
        f"{backend_url}/api/admin-register",
        json=test_data,
        headers={'Content-Type': 'application/json'}
    )
    
    if response.status_code != 200:
        print(f"❌ Failed to create admin registration - Status: {response.status_code}")
        try:
            print(f"Response: {response.json()}")
        except:
            print(f"Response: {response.text}")
        return False
    
    print(f"✅ Admin registration created - Status: {response.status_code}")
    response_data = response.json()
    registration_id = response_data.get('registration_id')
    print(f"Registration ID: {registration_id}")
    
    # Connect to MongoDB to verify RNA fields
    client = MongoClient(mongo_url)
    db = client[db_name]
    collection = db["admin_registrations"]
    
    # Find the registration in MongoDB
    registration = collection.find_one({"id": registration_id})
    
    if not registration:
        print(f"❌ Could not find registration with ID {registration_id} in MongoDB")
        return False
    
    # Check RNA fields in MongoDB
    print("\n🔍 Checking RNA fields in MongoDB...")
    rna_available = registration.get("rnaAvailable")
    rna_sample_date = registration.get("rnaSampleDate")
    rna_result = registration.get("rnaResult")
    
    print(f"MongoDB rnaAvailable: {rna_available}")
    print(f"MongoDB rnaSampleDate: {rna_sample_date}")
    print(f"MongoDB rnaResult: {rna_result}")
    
    if rna_available != "Yes":
        print(f"❌ rnaAvailable in MongoDB does not match expected 'Yes'")
        return False
    
    if rna_sample_date != "2025-07-15":
        print(f"❌ rnaSampleDate in MongoDB does not match expected '2025-07-15'")
        return False
    
    if rna_result != "Negative":
        print(f"❌ rnaResult in MongoDB does not match expected 'Negative'")
        return False
    
    print("✅ RNA fields verified in MongoDB")
    
    # Step 2: Get admin registration by ID
    print("\n🔍 Step 2: Getting admin registration by ID...")
    response = requests.get(
        f"{backend_url}/api/admin-registration/{registration_id}",
        headers={'Content-Type': 'application/json'}
    )
    
    if response.status_code != 200:
        print(f"❌ Failed to get admin registration - Status: {response.status_code}")
        try:
            print(f"Response: {response.json()}")
        except:
            print(f"Response: {response.text}")
        return False
    
    print(f"✅ Admin registration retrieved - Status: {response.status_code}")
    registration_data = response.json()
    
    # Check RNA fields in API response
    print("\n🔍 Checking RNA fields in API response...")
    api_rna_available = registration_data.get("rnaAvailable")
    api_rna_sample_date = registration_data.get("rnaSampleDate")
    api_rna_result = registration_data.get("rnaResult")
    
    print(f"API rnaAvailable: {api_rna_available}")
    print(f"API rnaSampleDate: {api_rna_sample_date}")
    print(f"API rnaResult: {api_rna_result}")
    
    if api_rna_available != "Yes":
        print(f"❌ rnaAvailable in API response does not match expected 'Yes'")
        return False
    
    if api_rna_sample_date != "2025-07-15":
        print(f"❌ rnaSampleDate in API response does not match expected '2025-07-15'")
        return False
    
    if api_rna_result != "Negative":
        print(f"❌ rnaResult in API response does not match expected 'Negative'")
        return False
    
    print("✅ RNA fields verified in API response")
    
    # Step 3: Update admin registration with new RNA values
    print("\n🔍 Step 3: Updating admin registration with new RNA values...")
    update_data = registration_data.copy()
    update_data["rnaAvailable"] = "Yes"
    update_data["rnaSampleDate"] = "2025-07-20"  # Updated date
    update_data["rnaResult"] = "Positive"  # Changed result
    
    # Remove fields that shouldn't be in the update request
    if "_id" in update_data:
        update_data.pop("_id")
    if "id" in update_data:
        update_data.pop("id")
    if "timestamp" in update_data:
        update_data.pop("timestamp")
    if "status" in update_data:
        update_data.pop("status")
    
    response = requests.put(
        f"{backend_url}/api/admin-registration/{registration_id}",
        json=update_data,
        headers={'Content-Type': 'application/json'}
    )
    
    if response.status_code != 200:
        print(f"❌ Failed to update admin registration - Status: {response.status_code}")
        try:
            print(f"Response: {response.json()}")
        except:
            print(f"Response: {response.text}")
        return False
    
    print(f"✅ Admin registration updated - Status: {response.status_code}")
    
    # Step 4: Get updated admin registration
    print("\n🔍 Step 4: Getting updated admin registration...")
    response = requests.get(
        f"{backend_url}/api/admin-registration/{registration_id}",
        headers={'Content-Type': 'application/json'}
    )
    
    if response.status_code != 200:
        print(f"❌ Failed to get updated admin registration - Status: {response.status_code}")
        try:
            print(f"Response: {response.json()}")
        except:
            print(f"Response: {response.text}")
        return False
    
    print(f"✅ Updated admin registration retrieved - Status: {response.status_code}")
    updated_data = response.json()
    
    # Check updated RNA fields in API response
    print("\n🔍 Checking updated RNA fields in API response...")
    updated_rna_available = updated_data.get("rnaAvailable")
    updated_rna_sample_date = updated_data.get("rnaSampleDate")
    updated_rna_result = updated_data.get("rnaResult")
    
    print(f"Updated API rnaAvailable: {updated_rna_available}")
    print(f"Updated API rnaSampleDate: {updated_rna_sample_date}")
    print(f"Updated API rnaResult: {updated_rna_result}")
    
    if updated_rna_available != "Yes":
        print(f"❌ Updated rnaAvailable in API response does not match expected 'Yes'")
        return False
    
    if updated_rna_sample_date != "2025-07-20":
        print(f"❌ Updated rnaSampleDate in API response does not match expected '2025-07-20'")
        return False
    
    if updated_rna_result != "Positive":
        print(f"❌ Updated rnaResult in API response does not match expected 'Positive'")
        return False
    
    print("✅ Updated RNA fields verified in API response")
    
    # Step 5: Finalize admin registration
    print("\n🔍 Step 5: Finalizing admin registration...")
    response = requests.post(
        f"{backend_url}/api/admin-registration/{registration_id}/finalize",
        headers={'Content-Type': 'application/json'}
    )
    
    if response.status_code != 200:
        print(f"❌ Failed to finalize admin registration - Status: {response.status_code}")
        try:
            print(f"Response: {response.json()}")
        except:
            print(f"Response: {response.text}")
        return False
    
    print(f"✅ Admin registration finalized - Status: {response.status_code}")
    finalize_data = response.json()
    
    if finalize_data.get("status") != "completed":
        print(f"❌ Registration status not updated to 'completed'")
        return False
    
    print(f"✅ Registration status verified: {finalize_data.get('status')}")
    
    # Step 6: Verify registration is not in pending list
    print("\n🔍 Step 6: Verifying registration is not in pending list...")
    response = requests.get(
        f"{backend_url}/api/admin-registrations-pending",
        headers={'Content-Type': 'application/json'}
    )
    
    if response.status_code != 200:
        print(f"❌ Failed to get pending registrations - Status: {response.status_code}")
        try:
            print(f"Response: {response.json()}")
        except:
            print(f"Response: {response.text}")
        return False
    
    print(f"✅ Pending registrations retrieved - Status: {response.status_code}")
    pending_data = response.json()
    
    for reg in pending_data:
        if reg.get('id') == registration_id:
            print("❌ Registration still found in pending list after finalization")
            return False
    
    print("✅ Registration successfully removed from pending list after finalization")
    
    print("\n" + "=" * 50)
    print("✅ Admin Registration with RNA Fields Test Completed Successfully")
    print("=" * 50)
    
    return True

def test_duplicate_prevention():
    """Test duplicate prevention with unique index on firstName + lastName"""
    print("\n" + "=" * 50)
    print("🔍 Testing Duplicate Prevention")
    print("=" * 50)
    
    # Create test data
    test_data = generate_test_data()
    
    # Step 1: Create first registration
    print("\n🔍 Step 1: Creating first registration...")
    response = requests.post(
        f"{backend_url}/api/admin-register",
        json=test_data,
        headers={'Content-Type': 'application/json'}
    )
    
    if response.status_code != 200:
        print(f"❌ Failed to create first registration - Status: {response.status_code}")
        try:
            print(f"Response: {response.json()}")
        except:
            print(f"Response: {response.text}")
        return False
    
    print(f"✅ First registration created - Status: {response.status_code}")
    response_data = response.json()
    registration_id = response_data.get('registration_id')
    print(f"First Registration ID: {registration_id}")
    
    # Step 2: Create duplicate registration
    print("\n🔍 Step 2: Creating duplicate registration...")
    duplicate_data = test_data.copy()
    duplicate_data["email"] = f"duplicate.{test_data['email']}"
    duplicate_data["phone1"] = ''.join(random.choices(string.digits, k=10))
    
    response = requests.post(
        f"{backend_url}/api/admin-register",
        json=duplicate_data,
        headers={'Content-Type': 'application/json'}
    )
    
    if response.status_code != 200:
        print(f"❌ Failed to create duplicate registration - Status: {response.status_code}")
        try:
            print(f"Response: {response.json()}")
        except:
            print(f"Response: {response.text}")
        return False
    
    print(f"✅ Duplicate registration attempt processed - Status: {response.status_code}")
    duplicate_response = response.json()
    
    # Check if duplicate was detected
    if "duplicate_prevented" in duplicate_response and duplicate_response["duplicate_prevented"] == True:
        print("✅ Duplicate prevention working correctly")
        print(f"✅ Response message: {duplicate_response.get('message')}")
        
        # Verify the returned registration ID matches the original
        if duplicate_response.get('registration_id') == registration_id:
            print("✅ Duplicate returns original registration ID")
        else:
            print("❌ Duplicate returns different registration ID")
            return False
    else:
        print("❌ Duplicate prevention not working - created new registration instead of detecting duplicate")
        return False
    
    print("\n" + "=" * 50)
    print("✅ Duplicate Prevention Test Completed Successfully")
    print("=" * 50)
    
    return True

def main():
    print("🚀 Starting Comprehensive Backend Tests for my420.ca")
    print(f"🔗 Base URL: {backend_url}")
    print("=" * 50)
    
    # Test admin registration with RNA fields
    rna_test_success = test_admin_registration_with_rna_fields()
    
    # Test duplicate prevention
    duplicate_test_success = test_duplicate_prevention()
    
    # Print overall results
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"RNA Fields Test: {'✅ Passed' if rna_test_success else '❌ Failed'}")
    print(f"Duplicate Prevention Test: {'✅ Passed' if duplicate_test_success else '❌ Failed'}")
    print("=" * 50)
    
    return 0 if rna_test_success and duplicate_test_success else 1

if __name__ == "__main__":
    sys.exit(main())