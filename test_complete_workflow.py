import requests
import unittest
import json
from datetime import datetime, date
import random
import string
import sys
import os
from dotenv import load_dotenv
import logging
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables
load_dotenv('/app/frontend/.env')
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL')

if not BACKEND_URL:
    logging.error("REACT_APP_BACKEND_URL not found in environment variables")
    sys.exit(1)

logging.info(f"Using backend URL: {BACKEND_URL}")

def test_complete_workflow():
    """Test the complete workflow: create registration -> add tests -> get tests"""
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
    
    # HCV test data
    hcv_test_data = {
        "test_type": "HCV",
        "test_date": date.today().isoformat(),
        "hcv_result": "positive",
        "hcv_tester": "JY"
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
        
        # Wait a moment before proceeding
        time.sleep(1)
        
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
        
        # Wait a moment before proceeding
        time.sleep(1)
        
        # Step 3: Add HCV test
        logging.info("\nStep 3: Adding HCV test...")
        
        url = f"{BACKEND_URL}/api/admin-registration/{registration_id}/test"
        
        response = requests.post(url, json=hcv_test_data, headers=headers, timeout=10)
        
        if response.status_code != 200:
            logging.error(f"❌ Failed to add HCV test: {response.status_code}")
            try:
                logging.error(f"Response: {response.json()}")
            except:
                logging.error(f"Response: {response.text}")
            return False
        
        response_data = response.json()
        hcv_test_id = response_data.get("test_id")
        
        if not hcv_test_id:
            logging.error("❌ HCV test ID not returned in response")
            return False
        
        logging.info(f"✅ HCV test added successfully")
        logging.info(f"HCV Test ID: {hcv_test_id}")
        
        # Wait a moment before proceeding
        time.sleep(2)
        
        # Step 4: Get tests
        logging.info("\nStep 4: Getting tests...")
        
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
        
        if len(tests) != 2:
            logging.error(f"❌ Expected 2 tests, got {len(tests)}")
            return False
        
        logging.info(f"✅ Retrieved {len(tests)} tests successfully")
        
        # Verify test data
        hiv_test = None
        hcv_test = None
        
        for test in tests:
            if test.get("test_type") == "HIV":
                hiv_test = test
            elif test.get("test_type") == "HCV":
                hcv_test = test
        
        if not hiv_test:
            logging.error("❌ HIV test not found in retrieved tests")
            return False
        
        if not hcv_test:
            logging.error("❌ HCV test not found in retrieved tests")
            return False
        
        # Verify registration_id is correctly set
        if hiv_test.get("registration_id") != registration_id:
            logging.error(f"❌ HIV test registration_id mismatch: {hiv_test.get('registration_id')} != {registration_id}")
            return False
        
        if hcv_test.get("registration_id") != registration_id:
            logging.error(f"❌ HCV test registration_id mismatch: {hcv_test.get('registration_id')} != {registration_id}")
            return False
        
        logging.info(f"✅ Test data verified")
        logging.info(f"✅ HIV test registration_id: {hiv_test.get('registration_id')}")
        logging.info(f"✅ HCV test registration_id: {hcv_test.get('registration_id')}")
        
        # Step 5: Update HIV test
        logging.info("\nStep 5: Updating HIV test...")
        
        url = f"{BACKEND_URL}/api/admin-registration/{registration_id}/test/{hiv_test_id}"
        
        update_data = {
            "hiv_result": "positive",
            "hiv_type": "Type 1",
            "hiv_tester": "JD"
        }
        
        response = requests.put(url, json=update_data, headers=headers, timeout=10)
        
        if response.status_code != 200:
            logging.error(f"❌ Failed to update HIV test: {response.status_code}")
            try:
                logging.error(f"Response: {response.json()}")
            except:
                logging.error(f"Response: {response.text}")
            return False
        
        logging.info(f"✅ HIV test updated successfully")
        
        # Wait a moment before proceeding
        time.sleep(1)
        
        # Step 6: Verify update
        logging.info("\nStep 6: Verifying update...")
        
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
        
        # Find the updated test
        updated_test = None
        for test in tests:
            if test.get("id") == hiv_test_id:
                updated_test = test
                break
        
        if not updated_test:
            logging.error(f"❌ Updated test not found in retrieved tests")
            return False
        
        # Verify updated fields
        if updated_test.get("hiv_result") != update_data["hiv_result"]:
            logging.error(f"❌ Updated HIV result mismatch: {updated_test.get('hiv_result')} != {update_data['hiv_result']}")
            return False
        
        if updated_test.get("hiv_type") != update_data["hiv_type"]:
            logging.error(f"❌ Updated HIV type mismatch: {updated_test.get('hiv_type')} != {update_data['hiv_type']}")
            return False
        
        if updated_test.get("hiv_tester") != update_data["hiv_tester"]:
            logging.error(f"❌ Updated HIV tester mismatch: {updated_test.get('hiv_tester')} != {update_data['hiv_tester']}")
            return False
        
        logging.info(f"✅ Update verified")
        
        # Step 7: Delete HIV test
        logging.info("\nStep 7: Deleting HIV test...")
        
        url = f"{BACKEND_URL}/api/admin-registration/{registration_id}/test/{hiv_test_id}"
        
        response = requests.delete(url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            logging.error(f"❌ Failed to delete HIV test: {response.status_code}")
            try:
                logging.error(f"Response: {response.json()}")
            except:
                logging.error(f"Response: {response.text}")
            return False
        
        logging.info(f"✅ HIV test deleted successfully")
        
        # Wait a moment before proceeding
        time.sleep(1)
        
        # Step 8: Verify deletion
        logging.info("\nStep 8: Verifying deletion...")
        
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
        
        # Check that the deleted test is not in the list
        for test in tests:
            if test.get("id") == hiv_test_id:
                logging.error(f"❌ Deleted test still found in retrieved tests")
                return False
        
        logging.info(f"✅ Deletion verified")
        
        # All steps completed successfully
        logging.info("\n✅ Complete workflow test passed")
        return True
        
    except requests.exceptions.Timeout:
        logging.error("❌ Request timed out")
        return False
    except Exception as e:
        logging.error(f"❌ Exception during test: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_complete_workflow()
    
    if success:
        logging.info("\n✅ ALL TESTS PASSED")
        sys.exit(0)
    else:
        logging.error("\n❌ SOME TESTS FAILED")
        sys.exit(1)