import requests
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

def test_get_tests(registration_id):
    """Test retrieving tests for a specific registration"""
    logging.info(f"Testing retrieval of tests for registration {registration_id}...")
    
    url = f"{BACKEND_URL}/api/admin-registration/{registration_id}/tests"
    headers = {'Content-Type': 'application/json'}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            response_data = response.json()
            tests = response_data.get("tests", [])
            
            logging.info(f"✅ Tests retrieved successfully")
            logging.info(f"Number of tests: {len(tests)}")
            
            for i, test in enumerate(tests):
                logging.info(f"Test {i+1}:")
                logging.info(f"  ID: {test.get('id')}")
                logging.info(f"  Type: {test.get('test_type')}")
                logging.info(f"  Registration ID: {test.get('registration_id')}")
                
            return True
        else:
            logging.error(f"❌ Failed to retrieve tests: {response.status_code}")
            try:
                logging.error(f"Response: {response.json()}")
            except:
                logging.error(f"Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        logging.error("❌ Request timed out after 10 seconds")
        return False
    except Exception as e:
        logging.error(f"❌ Exception during tests retrieval: {str(e)}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        logging.error("Please provide a registration ID as an argument")
        sys.exit(1)
    
    registration_id = sys.argv[1]
    success = test_get_tests(registration_id)
    
    sys.exit(0 if success else 1)