from pymongo import MongoClient
import os
import requests
import json
from dotenv import load_dotenv
from datetime import datetime, timedelta
import uuid
import base64

def create_share_and_check_urls():
    """Create a share and check the URLs in MongoDB"""
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
    
    # Create a share directly in MongoDB
    share_id = str(uuid.uuid4())
    expires_at = datetime.utcnow() + timedelta(minutes=30)
    
    # Sample base64 image
    sample_image = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
    
    # Create attachment data
    attachment_data = {
        "type": "Image",
        "filename": "test.png",
        "url": sample_image,
        "description": "Test image for sharing"
    }
    
    # Create share data
    share_data = {
        "id": share_id,
        "attachment_data": attachment_data,
        "created_at": datetime.utcnow(),
        "expires_at": expires_at,
        "access_count": 0
    }
    
    # Insert into MongoDB
    collection.insert_one(share_data)
    print(f"Created share with ID: {share_id}")
    
    # Generate URLs using the correct external base URL
    base_url = "https://dfe9a1e1-7f3d-45aa-ad71-43a254e568c5.preview.emergentagent.com"
    share_url = f"{base_url}/api/shared-attachment/{share_id}/download"
    preview_url = f"{base_url}/api/shared-attachment/{share_id}/preview"
    
    print(f"Share URL: {share_url}")
    print(f"Preview URL: {preview_url}")
    
    # Check for localhost references
    if "localhost" in share_url:
        print("❌ Share URL contains localhost reference")
    else:
        print("✅ Share URL does not contain localhost references")
        
    if "localhost" in preview_url:
        print("❌ Preview URL contains localhost reference")
    else:
        print("✅ Preview URL does not contain localhost references")
    
    # Now check all shares in MongoDB
    shares = list(collection.find())
    print(f"\nFound {len(shares)} temporary shares in MongoDB")
    
    # Check each share
    for share in shares:
        print(f"\nShare ID: {share.get('id')}")
        print(f"Created at: {share.get('created_at')}")
        print(f"Expires at: {share.get('expires_at')}")
        print(f"Access count: {share.get('access_count', 0)}")

if __name__ == "__main__":
    create_share_and_check_urls()