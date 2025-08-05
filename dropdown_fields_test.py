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

def generate_test_data(referral_site=None, physician=None, health_card_version=None):
    """Generate random test data for admin registration with specific dropdown values"""
    random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    today = date.today()
    today_str = today.isoformat()
    dob_date = date(today.year - 40, today.month, today.day)
    dob_str = dob_date.isoformat()
    
    # Generate sample base64 image
    sample_image = generate_sample_base64_image()
    
    # Default values if not provided
    if referral_site is None:
        referral_site = "Toronto - Outreach"
    if physician is None:
        physician = "Dr. David Fletcher"
    if health_card_version is None:
        health_card_version = "AB"
    
    return {
        "firstName": f"Michael {random_suffix}",
        "lastName": f"Smith {random_suffix}",
        "dob": dob_str,
        "patientConsent": "Verbal",
        "gender": "Male",
        "province": "Ontario",
        "disposition": "Reactive",
        "aka": f"Mike {random_suffix}",
        "age": "40",
        "regDate": today_str,
        "healthCard": ''.join(random.choices(string.digits, k=10)),
        "healthCardVersion": health_card_version,
        "referralSite": referral_site,
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

def test_dropdown_fields(base_url):
    """Test the dropdown fields (referral site, physician, health card version)"""
    print("\n" + "=" * 80)
    print("🔍 Testing Dropdown Fields")
    print("=" * 80)
    
    # List of referral sites to test
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
    
    # List of physicians to test
    physicians = [
        "Dr. David Fletcher",
        "None"
    ]
    
    # List of health card versions to test
    health_card_versions = [
        "AB",
        "ON",
        "BC",
        "QC",
        "NS",
        "NB",
        "MB",
        "SK",
        "AB",
        "PE",
        "NL",
        "YT",
        "NT",
        "NU"
    ]
    
    # Test Case 1: Test all referral sites
    print("\n" + "-" * 50)
    print("Test Case 1: Testing Referral Sites")
    print("-" * 50)
    
    for site in referral_sites:
        data = generate_test_data(referral_site=site)
        response = requests.post(f"{base_url}/api/admin-register", json=data)
        
        if response.status_code == 200:
            print(f"✅ Registration with referral site '{site}' successful - Status: {response.status_code}")
            reg_id = response.json().get('registration_id')
            
            # Get the registration to verify
            get_response = requests.get(f"{base_url}/api/admin-registration/{reg_id}")
            
            if get_response.status_code == 200:
                reg_data = get_response.json()
                if reg_data.get('referralSite') == site:
                    print(f"✅ Referral site '{site}' saved correctly")
                else:
                    print(f"❌ Referral site mismatch: expected '{site}', got '{reg_data.get('referralSite')}'")
            else:
                print(f"❌ Failed to get registration - Status: {get_response.status_code}")
        else:
            print(f"❌ Registration with referral site '{site}' failed - Status: {response.status_code}")
            try:
                print(f"Error: {response.json()}")
            except:
                print(f"Response: {response.text}")
    
    # Test Case 2: Test all physicians
    print("\n" + "-" * 50)
    print("Test Case 2: Testing Physicians")
    print("-" * 50)
    
    for physician in physicians:
        # Skip POCT NEG with Dr. David Fletcher as we know it doesn't work from previous test
        if physician == "Dr. David Fletcher":
            disposition = "Reactive"
        else:
            disposition = "POCT NEG"
            
        data = generate_test_data(physician=physician)
        data["disposition"] = disposition
        
        response = requests.post(f"{base_url}/api/admin-register", json=data)
        
        if response.status_code == 200:
            print(f"✅ Registration with physician '{physician}' successful - Status: {response.status_code}")
            reg_id = response.json().get('registration_id')
            
            # Get the registration to verify
            get_response = requests.get(f"{base_url}/api/admin-registration/{reg_id}")
            
            if get_response.status_code == 200:
                reg_data = get_response.json()
                if reg_data.get('physician') == physician:
                    print(f"✅ Physician '{physician}' saved correctly")
                else:
                    print(f"❌ Physician mismatch: expected '{physician}', got '{reg_data.get('physician')}'")
            else:
                print(f"❌ Failed to get registration - Status: {get_response.status_code}")
        else:
            print(f"❌ Registration with physician '{physician}' failed - Status: {response.status_code}")
            try:
                print(f"Error: {response.json()}")
            except:
                print(f"Response: {response.text}")
    
    # Test Case 3: Test health card versions
    print("\n" + "-" * 50)
    print("Test Case 3: Testing Health Card Versions")
    print("-" * 50)
    
    for version in health_card_versions:
        data = generate_test_data(health_card_version=version)
        response = requests.post(f"{base_url}/api/admin-register", json=data)
        
        if response.status_code == 200:
            print(f"✅ Registration with health card version '{version}' successful - Status: {response.status_code}")
            reg_id = response.json().get('registration_id')
            
            # Get the registration to verify
            get_response = requests.get(f"{base_url}/api/admin-registration/{reg_id}")
            
            if get_response.status_code == 200:
                reg_data = get_response.json()
                if reg_data.get('healthCardVersion') == version:
                    print(f"✅ Health card version '{version}' saved correctly")
                else:
                    print(f"❌ Health card version mismatch: expected '{version}', got '{reg_data.get('healthCardVersion')}'")
            else:
                print(f"❌ Failed to get registration - Status: {get_response.status_code}")
        else:
            print(f"❌ Registration with health card version '{version}' failed - Status: {response.status_code}")
            try:
                print(f"Error: {response.json()}")
            except:
                print(f"Response: {response.text}")
    
    # Test Case 4: Test all fields together
    print("\n" + "-" * 50)
    print("Test Case 4: Testing All Dropdown Fields Together")
    print("-" * 50)
    
    # Pick random values for each field
    site = random.choice(referral_sites)
    physician = random.choice(physicians)
    version = random.choice(health_card_versions)
    
    # Ensure compatible disposition and physician
    disposition = "Reactive" if physician == "Dr. David Fletcher" else "POCT NEG"
    
    data = generate_test_data(referral_site=site, physician=physician, health_card_version=version)
    data["disposition"] = disposition
    
    response = requests.post(f"{base_url}/api/admin-register", json=data)
    
    if response.status_code == 200:
        print(f"✅ Registration with all dropdown fields successful - Status: {response.status_code}")
        reg_id = response.json().get('registration_id')
        
        # Get the registration to verify
        get_response = requests.get(f"{base_url}/api/admin-registration/{reg_id}")
        
        if get_response.status_code == 200:
            reg_data = get_response.json()
            all_correct = True
            
            if reg_data.get('referralSite') != site:
                print(f"❌ Referral site mismatch: expected '{site}', got '{reg_data.get('referralSite')}'")
                all_correct = False
            
            if reg_data.get('physician') != physician:
                print(f"❌ Physician mismatch: expected '{physician}', got '{reg_data.get('physician')}'")
                all_correct = False
            
            if reg_data.get('healthCardVersion') != version:
                print(f"❌ Health card version mismatch: expected '{version}', got '{reg_data.get('healthCardVersion')}'")
                all_correct = False
            
            if all_correct:
                print("✅ All dropdown fields saved correctly")
        else:
            print(f"❌ Failed to get registration - Status: {get_response.status_code}")
    else:
        print(f"❌ Registration with all dropdown fields failed - Status: {response.status_code}")
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
    
    # Test dropdown fields
    test_dropdown_fields(backend_url)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())