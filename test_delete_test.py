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

def test_delete_test(registration_id, test_id):
    """Test deleting a test"""
    logging.info(f"Testing deleting test {test_id} for registration {registration_id}...")
    
    url = f"{BACKEND_URL}/api/admin-registration/{registration_id}/test/{test_id}"
    headers = {'Content-Type': 'application/json'}
    
    try:
        response = requests.delete(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            logging.info(f"✅ Test deleted successfully")
            return True
        else:
            logging.error(f"❌ Failed to delete test: {response.status_code}")
            try:
                logging.error(f"Response: {response.json()}")
            except:
                logging.error(f"Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        logging.error("❌ Request timed out after 10 seconds")
        return False
    except Exception as e:
        logging.error(f"❌ Exception during test deletion: {str(e)}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 3:
        logging.error("Please provide a registration ID and test ID as arguments")
        sys.exit(1)
    
    registration_id = sys.argv[1]
    test_id = sys.argv[2]
    success = test_delete_test(registration_id, test_id)
    
    sys.exit(0 if success else 1)