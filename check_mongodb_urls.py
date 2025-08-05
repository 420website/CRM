from pymongo import MongoClient
import os
from dotenv import load_dotenv

def check_share_urls_in_mongodb():
    """Check the URLs in the temporary_shares collection in MongoDB"""
    # Load MongoDB connection details from backend .env
    load_dotenv('/app/backend/.env')
    mongo_url = os.environ.get('MONGO_URL')
    db_name = os.environ.get('DB_NAME')
    
    if not mongo_url or not db_name:
        print("❌ MongoDB connection details not found in backend .env")
        return
    
    # Connect to MongoDB
    client = MongoClient(mongo_url)
    db = client[db_name]
    collection = db["temporary_shares"]
    
    # Find all temporary shares
    shares = list(collection.find())
    
    if not shares:
        print("No temporary shares found in MongoDB")
        return
    
    print(f"Found {len(shares)} temporary shares in MongoDB")
    
    # Check each share for URL format
    for share in shares:
        print(f"\nShare ID: {share.get('id')}")
        
        # Get attachment data
        attachment_data = share.get('attachment_data', {})
        
        # Check if there are any URLs in the attachment data
        if 'url' in attachment_data:
            print(f"Attachment URL: {attachment_data['url']}")
        
        # Check access count
        print(f"Access count: {share.get('access_count', 0)}")
        
        # Check expiration time
        print(f"Expires at: {share.get('expires_at')}")

if __name__ == "__main__":
    check_share_urls_in_mongodb()