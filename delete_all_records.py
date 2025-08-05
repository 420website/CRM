#!/usr/bin/env python3
import os
import sys
from pymongo import MongoClient
from dotenv import load_dotenv
import logging

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

def delete_all_records(db):
    """Delete all patient records from all relevant collections"""
    if db is None:
        logger.error("Database connection not available")
        return False
    
    collections_to_clear = [
        "admin_registrations",
        "test_records",
        "attachments",
        "shared_attachments",
        "temporary_shares"
    ]
    
    success = True
    deletion_counts = {}
    
    for collection_name in collections_to_clear:
        try:
            # Check if collection exists
            if collection_name in db.list_collection_names():
                # Count documents before deletion
                count_before = db[collection_name].count_documents({})
                
                # Delete all documents
                result = db[collection_name].delete_many({})
                
                # Store deletion count
                deletion_counts[collection_name] = result.deleted_count
                
                logger.info(f"Deleted {result.deleted_count} records from {collection_name}")
                
                # Verify deletion
                count_after = db[collection_name].count_documents({})
                if count_after > 0:
                    logger.warning(f"Collection {collection_name} still has {count_after} records after deletion")
                    success = False
                else:
                    logger.info(f"Collection {collection_name} is now empty")
            else:
                logger.info(f"Collection {collection_name} does not exist, skipping")
                deletion_counts[collection_name] = 0
        except Exception as e:
            logger.error(f"Error deleting records from {collection_name}: {str(e)}")
            success = False
    
    return success, deletion_counts

def verify_empty_collections(db):
    """Verify that all collections are empty"""
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
                    logger.warning(f"Collection {collection_name} still has {count} records")
                    all_empty = False
                else:
                    logger.info(f"Collection {collection_name} is empty")
            else:
                logger.info(f"Collection {collection_name} does not exist")
                collection_counts[collection_name] = 0
        except Exception as e:
            logger.error(f"Error checking collection {collection_name}: {str(e)}")
            all_empty = False
    
    return all_empty, collection_counts

def main():
    """Main function to delete all patient records"""
    logger.info("Starting deletion of all patient records")
    
    # Connect to MongoDB
    client, db = connect_to_mongodb()
    if client is None or db is None:
        logger.error("Failed to connect to MongoDB, aborting")
        return 1
    
    try:
        # Delete all records
        success, deletion_counts = delete_all_records(db)
        
        # Verify collections are empty
        all_empty, collection_counts = verify_empty_collections(db)
        
        # Print summary
        logger.info("\n" + "=" * 50)
        logger.info("DELETION SUMMARY")
        logger.info("=" * 50)
        
        for collection, count in deletion_counts.items():
            logger.info(f"Deleted {count} records from {collection}")
        
        logger.info("\n" + "=" * 50)
        logger.info("VERIFICATION SUMMARY")
        logger.info("=" * 50)
        
        for collection, count in collection_counts.items():
            status = "✅ EMPTY" if count == 0 else f"❌ NOT EMPTY ({count} records)"
            logger.info(f"{collection}: {status}")
        
        if success and all_empty:
            logger.info("\n✅ SUCCESS: All patient records have been deleted")
            logger.info("✅ The system is ready for fresh testing")
            return 0
        else:
            logger.error("\n❌ ERROR: Some collections could not be fully cleared")
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