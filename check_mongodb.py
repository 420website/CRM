from pymongo import MongoClient
import os
from dotenv import load_dotenv
from datetime import datetime
import json
from bson import json_util

# Load environment variables
load_dotenv('/app/backend/.env')

# MongoDB connection
mongo_url = os.environ.get('MONGO_URL')
db_name = os.environ.get('DB_NAME')
client = MongoClient(mongo_url)
db = client[db_name]

# Check TTL index
print("Checking TTL index on temporary_shares collection...")
indexes = list(db.temporary_shares.list_indexes())
for index in indexes:
    print(f"Index: {index}")

# Check collection contents
print("\nChecking contents of temporary_shares collection...")
count = db.temporary_shares.count_documents({})
print(f"Found {count} documents in temporary_shares collection")

if count > 0:
    # Get all documents
    shares = list(db.temporary_shares.find())
    print(f"Documents in collection:")
    
    for share in shares:
        # Convert ObjectId to string for printing
        share_json = json.loads(json_util.dumps(share))
        
        # Print basic info
        print(f"ID: {share.get('id', 'Unknown')}")
        print(f"Created at: {share.get('created_at', 'Unknown')}")
        print(f"Expires at: {share.get('expires_at', 'Unknown')}")
        
        # Calculate time until expiration
        expires_at = share.get('expires_at')
        if isinstance(expires_at, datetime):
            now = datetime.utcnow()
            if expires_at > now:
                time_left = expires_at - now
                print(f"Time until expiration: {time_left.total_seconds()/60:.1f} minutes")
            else:
                print(f"EXPIRED: {expires_at} < {now}")
        
        # Check attachment data
        attachment_data = share.get('attachment_data')
        if attachment_data:
            print(f"Attachment type: {attachment_data.get('type', 'Unknown')}")
            print(f"Attachment filename: {attachment_data.get('filename', 'Unknown')}")
            url = attachment_data.get('url', '')
            if url:
                print(f"URL starts with: {url[:30]}...")
        
        print("-" * 50)