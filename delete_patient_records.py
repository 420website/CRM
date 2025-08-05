#!/usr/bin/env python3
import os
import sys
from pymongo import MongoClient
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def delete_all_patient_records():
    """
    Delete all patient records from the MongoDB database.
    This includes admin_registrations and any related test records.
    """
    # Load MongoDB connection details from backend .env
    load_dotenv('/app/backend/.env')
    mongo_url = os.environ.get('MONGO_URL')
    db_name = os.environ.get('DB_NAME')
    
    if not mongo_url or not db_name:
        logging.error("MongoDB connection details not found in backend .env")
        return False
    
    try:
        # Connect to MongoDB
        logging.info(f"Connecting to MongoDB at {mongo_url}")
        client = MongoClient(mongo_url)
        db = client[db_name]
        
        # Get list of all collections
        collections = db.list_collection_names()
        logging.info(f"Found collections: {collections}")
        
        # Collections to clean
        patient_collections = [
            "admin_registrations",  # Main patient records
            "tests",                # Test records
            "test_records",         # Test records (actual collection name)
            "attachments",          # Attachment records
            "shared_attachments",   # Shared attachment records
            "temporary_shares"      # Temporary shared links
        ]
        
        # Delete records from each collection
        for collection_name in patient_collections:
            if collection_name in collections:
                # Count records before deletion
                count_before = db[collection_name].count_documents({})
                
                # Delete all records
                result = db[collection_name].delete_many({})
                
                # Log results
                logging.info(f"Deleted {result.deleted_count} records from {collection_name} collection")
                
                # Verify deletion
                count_after = db[collection_name].count_documents({})
                logging.info(f"Verification: {collection_name} now has {count_after} records")
                
                if count_after > 0:
                    logging.warning(f"Warning: {count_after} records still remain in {collection_name}")
            else:
                logging.info(f"Collection {collection_name} not found, skipping")
        
        # Final verification
        all_empty = True
        for collection_name in patient_collections:
            if collection_name in collections:
                count = db[collection_name].count_documents({})
                if count > 0:
                    all_empty = False
                    logging.error(f"Collection {collection_name} still has {count} records")
        
        if all_empty:
            logging.info("SUCCESS: All patient collections are now empty")
            return True
        else:
            logging.error("FAILURE: Some collections still have records")
            return False
            
    except Exception as e:
        logging.error(f"Error deleting patient records: {str(e)}")
        return False

if __name__ == "__main__":
    success = delete_all_patient_records()
    sys.exit(0 if success else 1)