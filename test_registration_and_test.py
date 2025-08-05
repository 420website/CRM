import requests
import json
from datetime import datetime, date
import random
import string
import sys
import os
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables
load_dotenv('/app/frontend/.env')
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL')

if not BACKEND_URL:
    logging.error("REACT_APP_BACKEND_URL not found in environment variables")
    sys.exit(1)

logging.info(f"Using backend URL: {BACKEND_URL}")

def test_registration_and_test():
    """Test creating a registration and adding a test to it"""
    # Generate random data
    random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    
    # Registration data
    registration_data = {
        "firstName": f"Test{random_suffix}",
        "lastName": f"User{random_suffix}",
        "patientConsent": "Verbal",
        "gender": "Male",
        "province": "Ontario",
        "disposition": "POCT NEG",
        "healthCard": ''.join(random.choices(string.digits, k=10)),
        "email": f"test.user.{random_suffix}@example.com",
    }
    
    # HIV test data
    hiv_test_data = {
        "test_type": "HIV",
        "test_date": date.today().isoformat(),
        "hiv_result": "negative",
        "hiv_tester": "CM"
    }
    
    headers = {'Content-Type': 'application/json'}
    
    # Step 1: Create admin registration
    logging.info("Step 1: Creating admin registration...")
    
    url = f"{BACKEND_URL}/api/admin-register"
    
    try:
        response = requests.post(url, json=registration_data, headers=headers, timeout=10)
        
        if response.status_code != 200:
            logging.error(f"❌ Failed to create admin registration: {response.status_code}")
            try:
                logging.error(f"Response: {response.json()}")
            except:
                logging.error(f"Response: {response.text}")
            return False
        
        response_data = response.json()
        registration_id = response_data.get("registration_id")
        
        if not registration_id:
            logging.error("❌ Registration ID not returned in response")
            return False
        
        logging.info(f"✅ Admin registration created successfully")
        logging.info(f"Registration ID: {registration_id}")
        
        # Step 2: Add HIV test
        logging.info("\nStep 2: Adding HIV test...")
        
        url = f"{BACKEND_URL}/api/admin-registration/{registration_id}/test"
        
        response = requests.post(url, json=hiv_test_data, headers=headers, timeout=10)
        
        if response.status_code != 200:
            logging.error(f"❌ Failed to add HIV test: {response.status_code}")
            try:
                logging.error(f"Response: {response.json()}")
            except:
                logging.error(f"Response: {response.text}")
            return False
        
        response_data = response.json()
        hiv_test_id = response_data.get("test_id")
        
        if not hiv_test_id:
            logging.error("❌ HIV test ID not returned in response")
            return False
        
        logging.info(f"✅ HIV test added successfully")
        logging.info(f"HIV Test ID: {hiv_test_id}")
        
        # Step 3: Get tests
        logging.info("\nStep 3: Getting tests...")
        
        url = f"{BACKEND_URL}/api/admin-registration/{registration_id}/tests"
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            logging.error(f"❌ Failed to get tests: {response.status_code}")
            try:
                logging.error(f"Response: {response.json()}")
            except:
                logging.error(f"Response: {response.text}")
            return False
        
        response_data = response.json()
        tests = response_data.get("tests", [])
        
        if len(tests) != 1:
            logging.error(f"❌ Expected 1 test, got {len(tests)}")
            return False
        
        logging.info(f"✅ Retrieved {len(tests)} tests successfully")
        
        # Verify test data
        test = tests[0]
        
        if test.get("test_type") != "HIV":
            logging.error(f"❌ Test type mismatch: {test.get('test_type')} != HIV")
            return False
        
        if test.get("registration_id") != registration_id:
            logging.error(f"❌ Test registration_id mismatch: {test.get('registration_id')} != {registration_id}")
            return False
        
        logging.info(f"✅ Test data verified")
        logging.info(f"✅ Test registration_id: {test.get('registration_id')}")
        
        # All steps completed successfully
        logging.info("\n✅ Registration and test workflow passed")
        return True
        
    except requests.exceptions.Timeout:
        logging.error("❌ Request timed out")
        return False
    except Exception as e:
        logging.error(f"❌ Exception during test: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_registration_and_test()
    
    if success:
        logging.info("\n✅ ALL TESTS PASSED")
        sys.exit(0)
    else:
        logging.error("\n❌ SOME TESTS FAILED")
        sys.exit(1)