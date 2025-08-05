import requests
import json
import sys
import os
from dotenv import load_dotenv
import random
import string
from datetime import date

def generate_sample_base64_image():
    """Generate a simple base64 encoded image for testing"""
    # This is a tiny 1x1 pixel transparent PNG image encoded as base64
    return "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="

def generate_test_data(disposition="POCT NEG", physician="None"):
    """Generate random test data for admin registration with specific disposition and physician"""
    random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    today = date.today()
    today_str = today.isoformat()
    dob_date = date(today.year - 40, today.month, today.day)
    dob_str = dob_date.isoformat()
    
    # Generate sample base64 image
    sample_image = generate_sample_base64_image()
    
    # List of referral sites
    referral_sites = [
        "Toronto - Outreach",
        "Barrie - City Centre Pharmacy",
        "Hamilton - Community Health",
        "Kingston - University Hospital",
        "London - Downtown Clinic",
        "Niagara - Regional Health",
        "Orillia - Memorial Hospital",
        "Ottawa - Community Center",
        "Windsor - Downtown Mission"
    ]
    
    return {
        "firstName": f"Michael {random_suffix}",
        "lastName": f"Smith {random_suffix}",
        "dob": dob_str,
        "patientConsent": "Verbal",
        "gender": "Male",
        "province": "Ontario",
        "disposition": disposition,
        "aka": f"Mike {random_suffix}",
        "age": "40",
        "regDate": today_str,
        "healthCard": ''.join(random.choices(string.digits, k=10)),
        "healthCardVersion": "AB",
        "referralSite": random.choice(referral_sites),
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
        "email": f"michael.smith.{random_suffix}@example.com",
        "language": "English",
        "specialAttention": "Patient requires interpreter assistance",
        "photo": sample_image,
        "physician": physician
    }

def test_disposition_logic(base_url):
    """Test the disposition logic (POCT NEG → physician = None)"""
    print("\n" + "=" * 80)
    print("🔍 Testing Disposition Logic")
    print("=" * 80)
    
    # Test Case 1: POCT NEG with physician = None (should work)
    print("\n" + "-" * 50)
    print("Test Case 1: POCT NEG with physician = None")
    print("-" * 50)
    
    data = generate_test_data(disposition="POCT NEG", physician="None")
    response = requests.post(f"{base_url}/api/admin-register", json=data)
    
    if response.status_code == 200:
        print(f"✅ Registration successful - Status: {response.status_code}")
        reg_id = response.json().get('registration_id')
        print(f"Registration ID: {reg_id}")
        
        # Get the registration to verify
        get_response = requests.get(f"{base_url}/api/admin-registration/{reg_id}")
        
        if get_response.status_code == 200:
            reg_data = get_response.json()
            if reg_data.get('disposition') == "POCT NEG" and reg_data.get('physician') == "None":
                print("✅ Disposition logic correct: POCT NEG → physician = None")
            else:
                print(f"❌ Disposition logic incorrect: disposition={reg_data.get('disposition')}, physician={reg_data.get('physician')}")
        else:
            print(f"❌ Failed to get registration - Status: {get_response.status_code}")
    else:
        print(f"❌ Registration failed - Status: {response.status_code}")
        try:
            print(f"Error: {response.json()}")
        except:
            print(f"Response: {response.text}")
    
    # Test Case 2: POCT NEG with physician = Dr. David Fletcher (should be changed to None)
    print("\n" + "-" * 50)
    print("Test Case 2: POCT NEG with physician = Dr. David Fletcher")
    print("-" * 50)
    
    data = generate_test_data(disposition="POCT NEG", physician="Dr. David Fletcher")
    response = requests.post(f"{base_url}/api/admin-register", json=data)
    
    if response.status_code == 200:
        print(f"✅ Registration successful - Status: {response.status_code}")
        reg_id = response.json().get('registration_id')
        print(f"Registration ID: {reg_id}")
        
        # Get the registration to verify
        get_response = requests.get(f"{base_url}/api/admin-registration/{reg_id}")
        
        if get_response.status_code == 200:
            reg_data = get_response.json()
            if reg_data.get('disposition') == "POCT NEG":
                if reg_data.get('physician') == "None":
                    print("✅ Disposition logic correct: POCT NEG automatically changed physician to None")
                else:
                    print(f"❌ Disposition logic incorrect: disposition=POCT NEG but physician={reg_data.get('physician')}")
            else:
                print(f"❌ Unexpected disposition: {reg_data.get('disposition')}")
        else:
            print(f"❌ Failed to get registration - Status: {get_response.status_code}")
    else:
        print(f"❌ Registration failed - Status: {response.status_code}")
        try:
            print(f"Error: {response.json()}")
        except:
            print(f"Response: {response.text}")
    
    # Test Case 3: Reactive with physician = Dr. David Fletcher (should work)
    print("\n" + "-" * 50)
    print("Test Case 3: Reactive with physician = Dr. David Fletcher")
    print("-" * 50)
    
    data = generate_test_data(disposition="Reactive", physician="Dr. David Fletcher")
    response = requests.post(f"{base_url}/api/admin-register", json=data)
    
    if response.status_code == 200:
        print(f"✅ Registration successful - Status: {response.status_code}")
        reg_id = response.json().get('registration_id')
        print(f"Registration ID: {reg_id}")
        
        # Get the registration to verify
        get_response = requests.get(f"{base_url}/api/admin-registration/{reg_id}")
        
        if get_response.status_code == 200:
            reg_data = get_response.json()
            if reg_data.get('disposition') == "Reactive" and reg_data.get('physician') == "Dr. David Fletcher":
                print("✅ Disposition logic correct: Reactive → physician = Dr. David Fletcher")
            else:
                print(f"❌ Disposition logic incorrect: disposition={reg_data.get('disposition')}, physician={reg_data.get('physician')}")
        else:
            print(f"❌ Failed to get registration - Status: {get_response.status_code}")
    else:
        print(f"❌ Registration failed - Status: {response.status_code}")
        try:
            print(f"Error: {response.json()}")
        except:
            print(f"Response: {response.text}")
    
    # Test Case 4: Reactive with physician = None (should work)
    print("\n" + "-" * 50)
    print("Test Case 4: Reactive with physician = None")
    print("-" * 50)
    
    data = generate_test_data(disposition="Reactive", physician="None")
    response = requests.post(f"{base_url}/api/admin-register", json=data)
    
    if response.status_code == 200:
        print(f"✅ Registration successful - Status: {response.status_code}")
        reg_id = response.json().get('registration_id')
        print(f"Registration ID: {reg_id}")
        
        # Get the registration to verify
        get_response = requests.get(f"{base_url}/api/admin-registration/{reg_id}")
        
        if get_response.status_code == 200:
            reg_data = get_response.json()
            if reg_data.get('disposition') == "Reactive" and reg_data.get('physician') == "None":
                print("✅ Disposition logic correct: Reactive → physician = None (allowed)")
            else:
                print(f"❌ Disposition logic incorrect: disposition={reg_data.get('disposition')}, physician={reg_data.get('physician')}")
        else:
            print(f"❌ Failed to get registration - Status: {get_response.status_code}")
    else:
        print(f"❌ Registration failed - Status: {response.status_code}")
        try:
            print(f"Error: {response.json()}")
        except:
            print(f"Response: {response.text}")
    
    # Test Case 5: Update from POCT NEG to Reactive
    print("\n" + "-" * 50)
    print("Test Case 5: Update from POCT NEG to Reactive")
    print("-" * 50)
    
    # First create a POCT NEG registration
    data = generate_test_data(disposition="POCT NEG", physician="None")
    response = requests.post(f"{base_url}/api/admin-register", json=data)
    
    if response.status_code == 200:
        print(f"✅ Initial registration successful - Status: {response.status_code}")
        reg_id = response.json().get('registration_id')
        print(f"Registration ID: {reg_id}")
        
        # Now update to Reactive
        data['disposition'] = "Reactive"
        data['physician'] = "Dr. David Fletcher"
        
        update_response = requests.put(f"{base_url}/api/admin-registration/{reg_id}", json=data)
        
        if update_response.status_code == 200:
            print(f"✅ Update successful - Status: {update_response.status_code}")
            
            # Get the registration to verify
            get_response = requests.get(f"{base_url}/api/admin-registration/{reg_id}")
            
            if get_response.status_code == 200:
                reg_data = get_response.json()
                if reg_data.get('disposition') == "Reactive" and reg_data.get('physician') == "Dr. David Fletcher":
                    print("✅ Disposition logic correct: Updated from POCT NEG to Reactive with physician = Dr. David Fletcher")
                else:
                    print(f"❌ Disposition logic incorrect: disposition={reg_data.get('disposition')}, physician={reg_data.get('physician')}")
            else:
                print(f"❌ Failed to get registration - Status: {get_response.status_code}")
        else:
            print(f"❌ Update failed - Status: {update_response.status_code}")
            try:
                print(f"Error: {update_response.json()}")
            except:
                print(f"Response: {update_response.text}")
    else:
        print(f"❌ Initial registration failed - Status: {response.status_code}")
        try:
            print(f"Error: {response.json()}")
        except:
            print(f"Response: {response.text}")
    
    # Test Case 6: Update from Reactive to POCT NEG
    print("\n" + "-" * 50)
    print("Test Case 6: Update from Reactive to POCT NEG")
    print("-" * 50)
    
    # First create a Reactive registration
    data = generate_test_data(disposition="Reactive", physician="Dr. David Fletcher")
    response = requests.post(f"{base_url}/api/admin-register", json=data)
    
    if response.status_code == 200:
        print(f"✅ Initial registration successful - Status: {response.status_code}")
        reg_id = response.json().get('registration_id')
        print(f"Registration ID: {reg_id}")
        
        # Now update to POCT NEG
        data['disposition'] = "POCT NEG"
        data['physician'] = "None"
        
        update_response = requests.put(f"{base_url}/api/admin-registration/{reg_id}", json=data)
        
        if update_response.status_code == 200:
            print(f"✅ Update successful - Status: {update_response.status_code}")
            
            # Get the registration to verify
            get_response = requests.get(f"{base_url}/api/admin-registration/{reg_id}")
            
            if get_response.status_code == 200:
                reg_data = get_response.json()
                if reg_data.get('disposition') == "POCT NEG" and reg_data.get('physician') == "None":
                    print("✅ Disposition logic correct: Updated from Reactive to POCT NEG with physician = None")
                else:
                    print(f"❌ Disposition logic incorrect: disposition={reg_data.get('disposition')}, physician={reg_data.get('physician')}")
            else:
                print(f"❌ Failed to get registration - Status: {get_response.status_code}")
        else:
            print(f"❌ Update failed - Status: {update_response.status_code}")
            try:
                print(f"Error: {update_response.json()}")
            except:
                print(f"Response: {update_response.text}")
    else:
        print(f"❌ Initial registration failed - Status: {response.status_code}")
        try:
            print(f"Error: {response.json()}")
        except:
            print(f"Response: {response.text}")

def main():
    # Get the backend URL from the frontend .env file
    load_dotenv('/app/frontend/.env')
    
    # Get the backend URL from the environment variable
    backend_url = os.environ.get('REACT_APP_BACKEND_URL')
    if not backend_url:
        print("❌ Error: REACT_APP_BACKEND_URL not found in frontend .env file")
        return 1
    
    print(f"🔗 Using backend URL from .env: {backend_url}")
    
    # Test disposition logic
    test_disposition_logic(backend_url)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())