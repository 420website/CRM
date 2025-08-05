#!/usr/bin/env python3
import os
import sys
import json
import requests
from pymongo import MongoClient
from dotenv import load_dotenv
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def connect_to_mongodb():
    """Connect to MongoDB using environment variables"""
    try:
        # Load environment variables from backend/.env
        load_dotenv('/app/backend/.env')
        
        # Get MongoDB connection details
        mongo_url = os.environ.get('MONGO_URL')
        db_name = os.environ.get('DB_NAME', 'my420_ca_db')
        
        if not mongo_url:
            logger.error("MongoDB URL not found in environment variables")
            return None, None
        
        logger.info(f"Connecting to MongoDB at {mongo_url}, database: {db_name}")
        client = MongoClient(mongo_url)
        db = client[db_name]
        
        # Test connection
        client.admin.command('ping')
        logger.info("Successfully connected to MongoDB")
        
        return client, db
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {str(e)}")
        return None, None

def verify_empty_collections(db):
    """Verify that all patient-related collections are empty"""
    if db is None:
        logger.error("Database connection not available")
        return False
    
    collections_to_check = [
        "admin_registrations",
        "test_records",
        "attachments",
        "shared_attachments",
        "temporary_shares"
    ]
    
    all_empty = True
    collection_counts = {}
    
    for collection_name in collections_to_check:
        try:
            # Check if collection exists
            if collection_name in db.list_collection_names():
                # Count documents
                count = db[collection_name].count_documents({})
                collection_counts[collection_name] = count
                
                if count > 0:
                    logger.warning(f"Collection {collection_name} has {count} records")
                    all_empty = False
                else:
                    logger.info(f"Collection {collection_name} is empty ✅")
            else:
                logger.info(f"Collection {collection_name} does not exist (considered empty) ✅")
                collection_counts[collection_name] = 0
        except Exception as e:
            logger.error(f"Error checking collection {collection_name}: {str(e)}")
            all_empty = False
    
    return all_empty, collection_counts

def test_api_health(base_url):
    """Test the API health endpoint"""
    try:
        import subprocess
        
        url = f"{base_url}/api/"  # Note the trailing slash
        logger.info(f"Testing API health at {url}")
        
        # Use wget instead of requests
        result = subprocess.run(['wget', '-O', '-', url], 
                               stdout=subprocess.PIPE, 
                               stderr=subprocess.PIPE,
                               text=True)
        
        if result.returncode == 0:
            logger.info(f"API health check successful ✅")
            logger.info(f"Response: {result.stdout.strip()}")
            return True
        else:
            logger.error(f"API health check failed ❌ - Return code: {result.returncode}")
            logger.error(f"Error: {result.stderr.strip()}")
            return False
    except Exception as e:
        logger.error(f"API health check failed ❌ - Error: {str(e)}")
        return False

def create_test_registration(base_url):
    """Create a test registration to verify system is working"""
    try:
        import subprocess
        import json
        import tempfile
        
        url = f"{base_url}/api/admin-register"
        logger.info(f"Creating test registration at {url}")
        
        # Create test data
        test_data = {
            "firstName": f"Test User",
            "lastName": f"Fresh System",
            "patientConsent": "Verbal",
            "gender": "Male",
            "province": "Ontario",
            "disposition": "POCT NEG",
            "regDate": datetime.now().strftime("%Y-%m-%d")
        }
        
        # Save test data to a temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp:
            json.dump(test_data, temp)
            temp_filename = temp.name
        
        # Use wget to post the data
        result = subprocess.run([
            'wget', '--header=Content-Type: application/json', 
            '--post-file', temp_filename, 
            '-O', '-', url
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Clean up the temporary file
        os.unlink(temp_filename)
        
        if result.returncode == 0:
            try:
                response_data = json.loads(result.stdout)
                registration_id = response_data.get("registration_id")
                logger.info(f"Test registration created successfully ✅ - ID: {registration_id}")
                return True, registration_id
            except json.JSONDecodeError:
                logger.error(f"Failed to parse response: {result.stdout}")
                return False, None
        else:
            logger.error(f"Test registration failed ❌ - Return code: {result.returncode}")
            logger.error(f"Error: {result.stderr}")
            return False, None
    except Exception as e:
        logger.error(f"Test registration failed ❌ - Error: {str(e)}")
        return False, None

def delete_test_registration(base_url, registration_id):
    """Delete the test registration"""
    if not registration_id:
        return False
    
    try:
        import subprocess
        
        url = f"{base_url}/api/admin-registration/{registration_id}"
        logger.info(f"Deleting test registration at {url}")
        
        # Use wget to send a DELETE request
        result = subprocess.run([
            'wget', '--method=DELETE', 
            '-O', '-', url
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        if result.returncode == 0:
            logger.info(f"Test registration deleted successfully ✅")
            return True
        else:
            logger.error(f"Test registration deletion failed ❌ - Return code: {result.returncode}")
            logger.error(f"Error: {result.stderr}")
            return False
    except Exception as e:
        logger.error(f"Test registration deletion failed ❌ - Error: {str(e)}")
        return False

def main():
    """Main function to verify system is ready for testing"""
    logger.info("Starting system verification")
    
    # Load the frontend .env file to get the backend URL
    load_dotenv('/app/frontend/.env')
    backend_url = os.environ.get('REACT_APP_BACKEND_URL')
    if not backend_url:
        logger.error("Backend URL not found in frontend .env file")
        return 1
    
    # For local testing, use the local backend URL
    local_backend_url = "http://localhost:8001"
    logger.info(f"Using local backend URL: {local_backend_url} (external URL: {backend_url})")
    
    # Connect to MongoDB
    client, db = connect_to_mongodb()
    if client is None or db is None:
        logger.error("Failed to connect to MongoDB, aborting")
        return 1
    
    try:
        # Verify collections are empty
        all_empty, collection_counts = verify_empty_collections(db)
        
        # Test API health
        api_healthy = test_api_health(local_backend_url)
        
        # Create and delete a test registration
        if api_healthy:
            registration_success, registration_id = create_test_registration(local_backend_url)
            if registration_success and registration_id:
                delete_success = delete_test_registration(local_backend_url, registration_id)
            else:
                delete_success = False
        else:
            registration_success = False
            delete_success = False
        
        # Print summary
        logger.info("\n" + "=" * 50)
        logger.info("SYSTEM VERIFICATION SUMMARY")
        logger.info("=" * 50)
        
        for collection, count in collection_counts.items():
            status = "✅ EMPTY" if count == 0 else f"❌ NOT EMPTY ({count} records)"
            logger.info(f"{collection}: {status}")
        
        logger.info(f"API Health: {'✅ HEALTHY' if api_healthy else '❌ UNHEALTHY'}")
        logger.info(f"Registration Test: {'✅ PASSED' if registration_success else '❌ FAILED'}")
        logger.info(f"Deletion Test: {'✅ PASSED' if delete_success else '❌ FAILED'}")
        
        if all_empty and api_healthy and registration_success and delete_success:
            logger.info("\n✅ SUCCESS: System is ready for fresh testing")
            return 0
        else:
            logger.error("\n❌ ERROR: System verification failed")
            return 1
    
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        return 1
    finally:
        # Close MongoDB connection
        if client:
            client.close()
            logger.info("MongoDB connection closed")

if __name__ == "__main__":
    sys.exit(main())