import requests
from pymongo import MongoClient
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv('/app/backend/.env')

# MongoDB connection
mongo_url = os.environ.get('MONGO_URL')
db_name = os.environ.get('DB_NAME')
client = MongoClient(mongo_url)
db = client[db_name]

# Get all share IDs from MongoDB
shares = list(db.temporary_shares.find())
print(f"Found {len(shares)} shares in MongoDB")

# Test accessing each share
for share in shares:
    share_id = share.get('id')
    created_at = share.get('created_at')
    expires_at = share.get('expires_at')
    
    print(f"\nTesting share ID: {share_id}")
    print(f"Created at: {created_at}")
    print(f"Expires at: {expires_at}")
    
    # Calculate time until expiration
    if isinstance(expires_at, datetime):
        now = datetime.utcnow()
        if expires_at > now:
            time_left = expires_at - now
            print(f"Time until expiration: {time_left.total_seconds()/60:.1f} minutes")
        else:
            print(f"EXPIRED: {expires_at} < {now}")
    
    # Test preview URL
    preview_url = f"https://258401ff-ff29-421c-8498-4969ee7788f0.preview.emergentagent.com/api/shared-attachment/{share_id}/preview"
    print(f"Testing preview URL: {preview_url}")
    
    try:
        preview_response = requests.get(preview_url, timeout=10)
        print(f"Preview response status code: {preview_response.status_code}")
        
        if preview_response.status_code == 200:
            content_type = preview_response.headers.get("Content-Type", "Unknown")
            content_length = len(preview_response.content)
            print(f"Content-Type: {content_type}")
            print(f"Content-Length: {content_length} bytes")
        else:
            try:
                error_data = preview_response.json()
                print(f"Error: {error_data}")
            except:
                print(f"Response: {preview_response.text}")
    except Exception as e:
        print(f"Error accessing preview URL: {str(e)}")
    
    # Test download URL
    download_url = f"https://258401ff-ff29-421c-8498-4969ee7788f0.preview.emergentagent.com/api/shared-attachment/{share_id}/download"
    print(f"Testing download URL: {download_url}")
    
    try:
        download_response = requests.get(download_url, timeout=10)
        print(f"Download response status code: {download_response.status_code}")
        
        if download_response.status_code == 200:
            content_type = download_response.headers.get("Content-Type", "Unknown")
            content_length = len(download_response.content)
            print(f"Content-Type: {content_type}")
            print(f"Content-Length: {content_length} bytes")
        else:
            try:
                error_data = download_response.json()
                print(f"Error: {error_data}")
            except:
                print(f"Response: {download_response.text}")
    except Exception as e:
        print(f"Error accessing download URL: {str(e)}")
    
    print("-" * 50)